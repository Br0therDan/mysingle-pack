"""
표준 HTTP 클라이언트 (연결 풀링 지원)
Standard HTTP Client with Connection Pooling
"""

from contextlib import asynccontextmanager
from typing import Dict, Optional

import httpx

from mysingle.core.config import settings
from mysingle.core.logging import get_logger

logger = get_logger(__name__)


class ServiceHttpClient:
    """표준 HTTP 클라이언트 (연결 풀링 지원)"""

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        headers: Optional[Dict[str, str]] = None,
        service_name: Optional[str] = None,
        propagate_auth_headers: bool = True,
    ):
        """
        HTTP 클라이언트 초기화

        Args:
            base_url: 기본 URL
            timeout: 요청 타임아웃 (초)
            max_connections: 최대 연결 수
            max_keepalive_connections: 최대 Keep-Alive 연결 수
            headers: 기본 헤더
            service_name: 서비스 이름 (로깅용)
            propagate_auth_headers: Kong Gateway 인증 헤더 자동 전파 여부
        """
        self.base_url = base_url
        self.service_name = service_name or "unknown"
        self.propagate_auth_headers = propagate_auth_headers

        # 기본 헤더 설정
        default_headers = {
            "User-Agent": f"mysingle-quant/{settings.PROJECT_NAME}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if headers:
            default_headers.update(headers)

        # HTTP 클라이언트 생성
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout),
            headers=default_headers,
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
            ),
            follow_redirects=True,
        )

        logger.debug(
            "HTTP client created",
            service=self.service_name,
            base_url=base_url,
            timeout_seconds=timeout,
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            propagate_auth=propagate_auth_headers,
        )

    async def close(self):
        """클라이언트 연결 정리"""
        if hasattr(self, "client") and self.client:
            await self.client.aclose()
            logger.debug(
                "HTTP client closed",
                service=self.service_name,
            )

    # 컨텍스트 매니저 지원
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    # HTTP 메서드 래퍼들
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET 요청"""
        logger.debug(
            "HTTP GET request",
            service=self.service_name,
            url=url,
        )
        return await self.client.get(url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST 요청"""
        logger.debug(
            "HTTP POST request",
            service=self.service_name,
            url=url,
        )
        return await self.client.post(url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        """PUT 요청"""
        logger.debug(
            "HTTP PUT request",
            service=self.service_name,
            url=url,
        )
        return await self.client.put(url, **kwargs)

    async def patch(self, url: str, **kwargs) -> httpx.Response:
        """PATCH 요청"""
        logger.debug(
            "HTTP PATCH request",
            service=self.service_name,
            url=url,
        )
        return await self.client.patch(url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """DELETE 요청"""
        logger.debug(
            "HTTP DELETE request",
            service=self.service_name,
            url=url,
        )
        return await self.client.delete(url, **kwargs)

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """일반 요청 메서드"""
        logger.debug(
            "HTTP request",
            service=self.service_name,
            method=method,
            url=url,
        )
        return await self.client.request(method, url, **kwargs)

    def _prepare_headers_with_propagation(
        self,
        request: Optional["httpx.Request"] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Kong Gateway 헤더 전파를 포함한 요청 헤더 준비

        Args:
            request: FastAPI Request 객체 (헤더 추출용)
            additional_headers: 추가 헤더

        Returns:
            병합된 헤더 딕셔너리
        """
        from mysingle.constants import (
            HEADER_AUTHORIZATION,
            HEADER_CORRELATION_ID,
            HEADER_USER_ID,
        )

        headers = dict(self.client.headers)

        # Kong Gateway 헤더 전파 (활성화된 경우)
        if self.propagate_auth_headers and request:
            # Authorization 헤더
            auth_header = request.headers.get(HEADER_AUTHORIZATION)
            if auth_header:
                headers[HEADER_AUTHORIZATION] = auth_header

            # X-User-Id 헤더
            user_id = request.headers.get(HEADER_USER_ID)
            if user_id:
                headers[HEADER_USER_ID] = user_id

            # X-Correlation-Id 헤더
            correlation_id = request.headers.get(HEADER_CORRELATION_ID)
            if correlation_id:
                headers[HEADER_CORRELATION_ID] = correlation_id

            logger.debug(
                "Kong Gateway headers propagated",
                service=self.service_name,
                has_authorization=bool(auth_header),
                has_user_id=bool(user_id),
                has_correlation_id=bool(correlation_id),
            )

        # 추가 헤더 병합
        if additional_headers:
            headers.update(additional_headers)

        return headers

    async def request_with_auth_propagation(
        self,
        method: str,
        url: str,
        request: Optional["httpx.Request"] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Kong Gateway 인증 헤더 전파를 포함한 요청

        Args:
            method: HTTP 메서드
            url: 요청 URL
            request: FastAPI Request 객체 (헤더 추출용)
            headers: 추가 헤더
            **kwargs: 기타 요청 파라미터

        Returns:
            HTTP 응답
        """
        prepared_headers = self._prepare_headers_with_propagation(request, headers)
        return await self.client.request(
            method, url, headers=prepared_headers, **kwargs
        )


class ServiceHttpClientManager:
    """HTTP 클라이언트 매니저 (싱글톤 패턴)"""

    _instances: Dict[str, ServiceHttpClient] = {}

    @classmethod
    def get_client(
        cls, service_name: str, base_url: Optional[str] = None, **kwargs
    ) -> ServiceHttpClient:
        """서비스별 HTTP 클라이언트 획득 (재사용)"""

        if service_name in cls._instances:
            return cls._instances[service_name]

        # base_url 자동 구성
        if not base_url:
            base_url = cls._build_service_url(service_name)

        # 클라이언트 생성 및 캐시
        client = ServiceHttpClient(
            base_url=base_url, service_name=service_name, **kwargs
        )

        cls._instances[service_name] = client
        logger.info(
            "HTTP client created and cached",
            service=service_name,
            base_url=base_url,
        )

        return client

    @classmethod
    def _build_service_url(cls, service_name: str) -> str:
        """서비스명으로부터 URL 자동 구성"""
        # 서비스명 정규화 (언더스코어 → 하이픈)
        normalized_name = service_name.replace("_", "-").replace("-service", "")

        if settings.USE_API_GATEWAY:
            # API Gateway 경로
            return f"{settings.API_GATEWAY_URL}/{normalized_name}"
        else:
            # 직접 연결 (개발 환경)
            port_mapping = {
                "iam": 8001,
                "journey": 8002,
                "strategy": 8003,
                "backtest": 8004,
                "optimization": 8005,
                "dashboard": 8006,
                "notification": 8007,
                "market-data": 8008,
                "gen-ai": 8009,
                "ml": 8010,
            }
            port = port_mapping.get(normalized_name, 8000)
            return f"http://localhost:{port}"

    @classmethod
    async def close_all(cls):
        """모든 클라이언트 연결 정리"""
        for service_name, client in cls._instances.items():
            try:
                await client.close()
                logger.debug(
                    "HTTP client closed",
                    service=service_name,
                )
            except Exception as e:
                logger.error(
                    "Error closing HTTP client",
                    service=service_name,
                    error=str(e),
                )

        cls._instances.clear()
        logger.info(
            "All HTTP clients closed",
            count=len(cls._instances),
        )


# Factory 함수들
def create_service_http_client(
    service_name: str,
    base_url: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
    max_connections: int = 100,
    max_keepalive_connections: int = 20,
) -> ServiceHttpClient:
    """서비스별 HTTP 클라이언트 생성 (일회성)"""

    if not base_url:
        base_url = ServiceHttpClientManager._build_service_url(service_name)

    # X-Service-Name 헤더 자동 추가
    default_headers = {"X-Service-Name": service_name}
    if headers:
        default_headers.update(headers)

    return ServiceHttpClient(
        base_url=base_url,
        headers=default_headers,
        service_name=service_name,
        timeout=timeout,
        max_connections=max_connections,
        max_keepalive_connections=max_keepalive_connections,
    )


def get_service_http_client(
    service_name: str, base_url: Optional[str] = None, **kwargs
) -> ServiceHttpClient:
    """서비스별 HTTP 클라이언트 획득 (재사용/싱글톤)"""
    return ServiceHttpClientManager.get_client(
        service_name=service_name, base_url=base_url, **kwargs
    )


@asynccontextmanager
async def http_client_lifespan():
    """HTTP 클라이언트 생명주기 관리"""
    try:
        logger.info(
            "HTTP client manager initialized",
            manager="ServiceHttpClientManager",
        )
        yield ServiceHttpClientManager
    finally:
        await ServiceHttpClientManager.close_all()
        logger.info(
            "HTTP client manager shutdown completed",
            manager="ServiceHttpClientManager",
        )


# 환경 설정 기반 기본값들
class HttpClientConfig:
    """HTTP 클라이언트 설정"""

    # 환경 변수로 오버라이드 가능한 기본값들
    DEFAULT_TIMEOUT: float = float(getattr(settings, "HTTP_CLIENT_TIMEOUT", 30.0))
    DEFAULT_MAX_CONNECTIONS: int = int(
        getattr(settings, "HTTP_CLIENT_MAX_CONNECTIONS", 100)
    )
    DEFAULT_MAX_KEEPALIVE: int = int(getattr(settings, "HTTP_CLIENT_MAX_KEEPALIVE", 20))

    # 재시도 설정
    DEFAULT_MAX_RETRIES: int = int(getattr(settings, "HTTP_CLIENT_MAX_RETRIES", 3))
    DEFAULT_RETRY_DELAY: float = float(
        getattr(settings, "HTTP_CLIENT_RETRY_DELAY", 1.0)
    )


# 편의 함수들
async def make_service_request(
    service_name: str,
    method: str,
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    **kwargs,
) -> httpx.Response:
    """서비스 요청 편의 함수"""
    client = get_service_http_client(service_name)

    # 추가 헤더 병합
    if headers:
        request_headers = {**client.client.headers, **headers}
        kwargs["headers"] = request_headers

    return await client.request(method, endpoint, **kwargs)
