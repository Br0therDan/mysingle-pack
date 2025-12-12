"""
Tests for BaseGrpcServer and GrpcCache

gRPC 서버 및 캐시 기능 테스트
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mysingle.grpc import BaseGrpcServer, GrpcCache, GrpcServerConfig, grpc_cached


class TestGrpcServerConfig:
    """GrpcServerConfig 테스트"""

    def test_config_defaults(self):
        """기본 설정 테스트"""
        config = GrpcServerConfig(service_name="test-service", port=50051)

        assert config.service_name == "test-service"
        assert config.port == 50051
        assert config.max_workers == 10
        assert config.enable_auth is True
        assert config.enable_rate_limiting is True
        assert config.enable_metrics is True
        assert config.keepalive_time_ms == 30000

    def test_config_custom(self):
        """커스텀 설정 테스트"""
        config = GrpcServerConfig(
            service_name="test-service",
            port=50052,
            max_workers=20,
            enable_auth=False,
            rate_limit_max_requests=2000,
            auth_exempt_methods=["/health/Check"],
        )

        assert config.max_workers == 20
        assert config.enable_auth is False
        assert config.rate_limit_max_requests == 2000
        assert "/health/Check" in config.auth_exempt_methods


class TestGrpcServer:
    """BaseGrpcServer 테스트"""

    class MockGrpcServer(BaseGrpcServer):
        """테스트용 Mock 서버"""

        def __init__(self, config: GrpcServerConfig):
            super().__init__(config)
            self.servicer_registered = False

        def register_servicers(self, server):
            self.servicer_registered = True

    def test_server_initialization(self):
        """서버 초기화 테스트"""
        config = GrpcServerConfig(service_name="test-service", port=50051)
        server = self.MockGrpcServer(config)

        assert server.config.service_name == "test-service"
        assert server.config.port == 50051
        assert server.server is None
        assert server._running is False

    def test_interceptor_chain_build(self):
        """Interceptor 체인 구성 테스트"""
        config = GrpcServerConfig(
            service_name="test-service",
            port=50051,
            enable_auth=True,
            enable_metrics=True,
            enable_rate_limiting=True,
            enable_error_handling=True,
        )
        server = self.MockGrpcServer(config)
        interceptors = server._build_interceptor_chain()

        # 6개 interceptor 확인 (Metrics, Auth, RateLimit, Metadata, Logging, Error)
        assert len(interceptors) == 6

        # 타입 확인
        from mysingle.grpc.interceptors import (
            AuthInterceptor,
            ErrorHandlingInterceptor,
            LoggingInterceptor,
            MetadataInterceptor,
            MetricsInterceptor,
            RateLimiterInterceptor,
        )

        assert isinstance(interceptors[0], MetricsInterceptor)
        assert isinstance(interceptors[1], AuthInterceptor)
        assert isinstance(interceptors[2], RateLimiterInterceptor)
        assert isinstance(interceptors[3], MetadataInterceptor)
        assert isinstance(interceptors[4], LoggingInterceptor)
        assert isinstance(interceptors[5], ErrorHandlingInterceptor)

    def test_server_options_build(self):
        """서버 옵션 구성 테스트"""
        config = GrpcServerConfig(
            service_name="test-service",
            port=50051,
            keepalive_time_ms=60000,
            max_message_length=20 * 1024 * 1024,
        )
        server = self.MockGrpcServer(config)
        options = server._build_server_options()

        # dict로 변환하여 검증
        options_dict = dict(options)
        assert options_dict["grpc.keepalive_time_ms"] == 60000
        assert options_dict["grpc.max_send_message_length"] == 20 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_lifecycle_hooks(self):
        """Lifecycle hook 실행 테스트"""
        config = GrpcServerConfig(service_name="test-service", port=50051)
        server = self.MockGrpcServer(config)

        # Mock hook 추가
        before_start_called = False
        after_start_called = False

        async def mock_before_start():
            nonlocal before_start_called
            before_start_called = True
            await asyncio.sleep(0)  # coroutine이어야 함

        async def mock_after_start():
            nonlocal after_start_called
            after_start_called = True
            await asyncio.sleep(0)

        server.before_start = mock_before_start
        server.after_start = mock_after_start

        # grpc.aio.server Mock
        mock_grpc_server = AsyncMock()
        mock_grpc_server.start = AsyncMock()
        mock_grpc_server.add_insecure_port = MagicMock()

        with patch("grpc.aio.server", return_value=mock_grpc_server):
            await server.start()

        assert before_start_called
        assert after_start_called
        assert server.servicer_registered


class TestGrpcCache:
    """GrpcCache 테스트"""

    @pytest.mark.asyncio
    async def test_cache_initialization(self):
        """캐시 초기화 테스트 (redis_db는 자동으로 settings.REDIS_DB_GRPC 사용)"""
        cache = GrpcCache(service_name="test-service")

        assert cache.service_name == "test-service"
        assert cache.key_prefix == "grpc:test-service"
        assert cache.memory_ttl == 300
        assert cache.memory_max_size == 100
        assert len(cache._memory_cache) == 0

    def test_cache_key_generation(self):
        """캐시 키 생성 테스트"""
        from google.protobuf.wrappers_pb2 import StringValue

        cache = GrpcCache(service_name="test-service")
        request = StringValue(value="test")

        cache_key = cache.make_cache_key(
            method="GetStrategyVersion",
            request=request,
            user_id="user123",
            correlation_id="corr123",
        )

        # 키 형식: "GetStrategyVersion:해시"
        assert cache_key.startswith("GetStrategyVersion:")
        assert len(cache_key.split(":")) == 2
        assert len(cache_key.split(":")[1]) == 12  # MD5 hash 12자

    @pytest.mark.asyncio
    async def test_l1_cache_hit(self):
        """L1 캐시 히트 테스트"""
        cache = GrpcCache(service_name="test-service")

        # L1에 직접 추가
        cache._add_to_memory("test_key", "test_value")

        # L1에서 조회 (Redis 호출 없음)
        result = await cache.get_with_l1("test_key")

        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_l1_lru_eviction(self):
        """L1 LRU 캐시 제거 테스트"""
        cache = GrpcCache(service_name="test-service", memory_max_size=3)

        # 3개 추가
        cache._add_to_memory("key1", "value1")
        cache._add_to_memory("key2", "value2")
        cache._add_to_memory("key3", "value3")

        assert len(cache._memory_cache) == 3

        # 4번째 추가 시 가장 오래된 key1 제거
        cache._add_to_memory("key4", "value4")

        assert len(cache._memory_cache) == 3
        assert "key1" not in cache._memory_cache
        assert "key4" in cache._memory_cache

    @pytest.mark.asyncio
    async def test_grpc_cached_decorator(self):
        """@grpc_cached 데코레이터 테스트"""
        from google.protobuf.wrappers_pb2 import StringValue

        class MockServicer:
            def __init__(self):
                self.cache = GrpcCache(service_name="test-service")
                self.call_count = 0

            @grpc_cached(ttl=300, use_metadata=False)
            async def GetData(self, request, context):
                self.call_count += 1
                return StringValue(value=f"result_{self.call_count}")

        servicer = MockServicer()
        mock_context = MagicMock()
        mock_context.invocation_metadata.return_value = []

        request = StringValue(value="test")

        # 첫 호출 (캐시 미스)
        result1 = await servicer.GetData(request, mock_context)
        assert servicer.call_count == 1
        assert result1.value == "result_1"

        # 두 번째 호출 (캐시 히트)
        result2 = await servicer.GetData(request, mock_context)
        assert servicer.call_count == 1  # 호출 증가 없음
        assert result2.value == "result_1"  # 캐시된 값 반환

    def test_clear_l1_cache(self):
        """L1 캐시 전체 삭제 테스트"""
        cache = GrpcCache(service_name="test-service")

        # 여러 항목 추가
        cache._add_to_memory("key1", "value1")
        cache._add_to_memory("key2", "value2")
        cache._add_to_memory("key3", "value3")

        assert len(cache._memory_cache) == 3

        # L1 삭제
        cache.clear_l1()

        assert len(cache._memory_cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
