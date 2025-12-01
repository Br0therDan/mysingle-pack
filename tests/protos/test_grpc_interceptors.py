"""
gRPC Interceptor 테스트

서버 및 클라이언트 인터셉터 기본 동작 검증
"""

from __future__ import annotations

import pytest

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


@pytest.mark.skip(reason="Requires running gRPC server")
class TestInterceptorIntegration:
    """인터셉터 통합 테스트 (실제 서버 필요)"""

    async def test_server_auth_interceptor(self):
        """서버 인증 인터셉터 통합 테스트"""
        # TODO: 실제 gRPC 서버를 띄우고 테스트
        pass

    async def test_client_auth_interceptor(self):
        """클라이언트 인증 인터셉터 통합 테스트"""
        # TODO: 실제 gRPC 클라이언트로 테스트
        pass
