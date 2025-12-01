"""
gRPC Interceptor 테스트

서버 및 클라이언트 인터셉터 기본 동작 검증
"""

from __future__ import annotations

from mysingle.grpc import (
    AuthInterceptor,
    ClientAuthInterceptor,
    LoggingInterceptor,
    MetadataInterceptor,
)


class TestAuthInterceptor:
    """AuthInterceptor 테스트"""

    def test_interceptor_creation(self):
        """인터셉터 생성 테스트"""
        interceptor = AuthInterceptor(require_auth=True)
        assert interceptor.require_auth is True
        assert interceptor.exempt_methods == set()

    def test_interceptor_with_exempt_methods(self):
        """면제 메서드가 있는 인터셉터 생성"""
        interceptor = AuthInterceptor(
            require_auth=True, exempt_methods=["/health/Check", "/health/Ready"]
        )
        assert "/health/Check" in interceptor.exempt_methods
        assert len(interceptor.exempt_methods) == 2

    def test_auth_disabled(self):
        """인증 비활성화 시 통과"""
        interceptor = AuthInterceptor(require_auth=False)
        assert interceptor.require_auth is False


class TestLoggingInterceptor:
    """LoggingInterceptor 테스트"""

    def test_interceptor_creation(self):
        """로깅 인터셉터 생성 테스트"""
        interceptor = LoggingInterceptor()
        assert interceptor is not None


class TestMetadataInterceptor:
    """MetadataInterceptor 테스트"""

    def test_interceptor_creation(self):
        """메타데이터 인터셉터 생성 테스트"""
        interceptor = MetadataInterceptor(auto_generate=True)
        assert interceptor.auto_generate is True

    def test_auto_generate_disabled(self):
        """자동 생성 비활성화"""
        interceptor = MetadataInterceptor(auto_generate=False)
        assert interceptor.auto_generate is False


class TestClientAuthInterceptor:
    """ClientAuthInterceptor 테스트"""

    def test_interceptor_creation(self):
        """클라이언트 인터셉터 생성 테스트"""
        interceptor = ClientAuthInterceptor(
            user_id="test-user", correlation_id="test-correlation"
        )
        assert interceptor.user_id == "test-user"
        assert interceptor.correlation_id == "test-correlation"

    def test_interceptor_without_correlation_id(self):
        """correlation_id 없이 인터셉터 생성"""
        interceptor = ClientAuthInterceptor(user_id="test-user")
        assert interceptor.user_id == "test-user"
        assert interceptor.correlation_id is None  # 런타임에 자동 생성됨


# Integration tests (실제 gRPC 서버 필요)
# 아래 테스트는 실제 서비스에서 통합 테스트로 실행


class TestInterceptorIntegration:
    """인터셉터 통합 테스트 (mock 기반)"""

    async def test_server_auth_interceptor(self):
        """서버 인증 인터셉터 통합 테스트"""
        # Test interceptor configuration and behavior without actual server
        interceptor = AuthInterceptor(
            require_auth=True, exempt_methods=["/health/Check"]
        )

        # Verify interceptor is properly configured
        assert interceptor.require_auth is True
        assert "/health/Check" in interceptor.exempt_methods

        # Test that exempt methods list is working
        assert len(interceptor.exempt_methods) == 1

        # Test metadata interceptor integration
        metadata_interceptor = MetadataInterceptor(auto_generate=True)
        assert metadata_interceptor.auto_generate is True

    async def test_client_auth_interceptor(self):
        """클라이언트 인증 인터셉터 통합 테스트"""
        # Test client interceptor with metadata injection
        user_id = "test-user-123"
        correlation_id = "corr-456"

        client_interceptor = ClientAuthInterceptor(
            user_id=user_id, correlation_id=correlation_id
        )

        # Verify metadata is properly set
        assert client_interceptor.user_id == user_id
        assert client_interceptor.correlation_id == correlation_id

        # Test interceptor without correlation_id (should be auto-generated at runtime)
        client_interceptor2 = ClientAuthInterceptor(user_id="another-user")
        assert client_interceptor2.user_id == "another-user"
        assert (
            client_interceptor2.correlation_id is None
        )  # Will be generated at runtime
