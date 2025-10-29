"""
Base Service Client

모든 마이크로서비스 HTTP 클라이언트의 베이스 클래스
공통 기능: 인증, 로깅, 에러 핸들링, 컨텍스트 매니저
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict

import httpx

from mysingle_quant.logging import get_logger

if TYPE_CHECKING:
    from fastapi import Request

logger = get_logger(__name__)


class BaseServiceClient:
    """
    마이크로서비스 HTTP 클라이언트 베이스 클래스

    Features:
        - JWT 토큰 인증 자동 처리
        - 비동기 컨텍스트 매니저 지원
        - 공통 에러 핸들링
        - 로깅 표준화
        - 환경별 URL 설정 (Docker 내부 vs 외부)

    Usage:
        ```python
        from fastapi import Request

        class MyServiceClient(BaseServiceClient):
            def __init__(
                self,
                auth_token: str | None = None,
                request: Request | None = None
            ):
                super().__init__(
                    service_name="my-service",
                    default_port=8001,
                    auth_token=auth_token,
                    request=request,
                )

            async def get_data(self) -> dict:
                return await self._request("GET", "/api/v1/data")

        # 사용 1: 명시적 토큰
        async with MyServiceClient(auth_token="jwt_token") as client:
            data = await client.get_data()

        # 사용 2: Request에서 자동 추출 (권장 - Kong Gateway 환경)
        @router.get("/some-endpoint")
        async def endpoint(request: Request):
            async with MyServiceClient(request=request) as client:
                data = await client.get_data()
            return data
        ```
    """

    def __init__(
        self,
        service_name: str,
        default_port: int,
        base_url: str | None = None,
        auth_token: str | None = None,
        request: "Request | None" = None,
        timeout: float = 60.0,
        follow_redirects: bool = True,
        **kwargs: Any,
    ):
        """
        Args:
            service_name: 서비스 이름 (예: "strategy-service", "market-data-service")
            default_port: 기본 포트 (예: 8001, 8002)
            base_url: 명시적 base URL (없으면 자동 결정)
            auth_token: JWT 인증 토큰 (optional, request가 주어지면 자동 추출)
            request: FastAPI Request 객체 (optional, Authorization 헤더 자동 추출)
            timeout: 요청 타임아웃 (초)
            follow_redirects: 리다이렉트 자동 처리 여부
            **kwargs: httpx.AsyncClient 추가 인자

        Note:
            - request 객체가 제공되면 Authorization 헤더에서 JWT 토큰을 자동 추출합니다.
            - auth_token과 request 둘 다 제공되면 auth_token이 우선순위를 가집니다.
            - Kong Gateway를 통한 서비스 간 통신에서 User Context를 유지하려면
              반드시 request 객체를 전달해야 합니다.
        """
        self.service_name = service_name
        self.default_port = default_port

        # JWT 토큰 결정: auth_token > request.headers["Authorization"]
        if auth_token:
            self.auth_token: str = auth_token
        elif request:
            extracted_token = self._extract_token_from_request(request)
            self.auth_token = extracted_token if extracted_token else ""
        else:
            self.auth_token = ""

        # Base URL 결정
        if base_url is None:
            base_url = self._determine_base_url()

        self.base_url = base_url

        # HTTP 헤더 설정
        headers = kwargs.pop("headers", {})
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        # httpx AsyncClient 초기화
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            follow_redirects=follow_redirects,
            headers=headers,
            **kwargs,
        )

        logger.info(
            f"{self.__class__.__name__} initialized: {self.base_url} "
            f"(auth={'enabled' if self.auth_token else 'disabled'})"
        )

    @staticmethod
    def _extract_token_from_request(request: "Request") -> str | None:
        """
        FastAPI Request 객체에서 JWT 토큰 추출

        Args:
            request: FastAPI Request 객체

        Returns:
            추출된 JWT 토큰 (없으면 None)

        Note:
            Authorization 헤더 형식: "Bearer <token>"
        """
        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            logger.debug("JWT token extracted from request")
            return token
        logger.debug("No valid Authorization header found in request")
        return None

    def _determine_base_url(self) -> str:
        """
        실행 환경에 따라 적절한 base URL 결정

        Returns:
            base URL (API Gateway 경유 또는 직접 접근)

        Priority:
            1. 명시적 환경변수 (SERVICE_NAME_URL)
            2. API Gateway 경유 (권장)
            3. 직접 접근 (개발/테스트용)

        Kong Gateway Routes:
            - strategy-service: /strategy/*
            - market-data-service: /market-data/*
            - ml-service: /ml/*
            - genai-service: /gen-ai/*
        """
        # 1. 환경 변수로 명시적 URL 제공 가능
        env_var = f"{self.service_name.upper().replace('-', '_')}_URL"
        if url := os.getenv(env_var):
            logger.debug(f"Using explicit URL from {env_var}: {url}")
            return url

        # 2. API Gateway 사용 여부 확인
        use_gateway = os.getenv("USE_API_GATEWAY", "true").lower() == "true"
        api_gateway_url = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

        if use_gateway:
            # Kong Gateway 라우트 매핑
            route_map = {
                "strategy-service": "/strategy",
                "market-data-service": "/market-data",
                "ml-service": "/ml",
                "genai-service": "/gen-ai",
            }
            route = route_map.get(self.service_name, f"/{self.service_name}")
            gateway_url = f"{api_gateway_url}{route}"
            logger.info(f"Using API Gateway: {gateway_url}")
            return gateway_url

        # 3. 직접 접근 (Gateway 우회 - 개발/테스트용)
        # Docker 내부 여부 확인
        is_docker = os.path.exists("/.dockerenv") or os.getenv("DOCKER_ENV") == "true"

        if is_docker:
            # Docker 내부: 서비스 이름으로 직접 접근
            direct_url = f"http://{self.service_name}:8000"
            logger.warning(f"Bypassing API Gateway (Docker): {direct_url}")
            return direct_url
        else:
            # 외부/개발: localhost + 서비스별 포트로 직접 접근
            direct_url = f"http://localhost:{self.default_port}"
            logger.warning(f"Bypassing API Gateway (localhost): {direct_url}")
            return direct_url

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        HTTP 요청 수행 (공통 에러 핸들링 포함)

        Args:
            method: HTTP 메서드 (GET, POST, PUT, DELETE 등)
            path: API 경로 (예: "/api/v1/data")
            **kwargs: httpx request 인자 (json, params, headers 등)

        Returns:
            응답 JSON 데이터

        Raises:
            httpx.HTTPError: HTTP 오류 발생 시
        """
        try:
            response = await self.client.request(method, path, **kwargs)
            response.raise_for_status()
            json_data: dict[str, Any] = response.json()
            return json_data
        except httpx.HTTPStatusError as e:
            logger.error(
                f"{self.service_name} HTTP {e.response.status_code} error: "
                f"{method} {path} - {e.response.text[:200]}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"{self.service_name} request failed: {method} {path} - {e}")
            raise
        except Exception as e:
            logger.error(f"{self.service_name} unexpected error: {method} {path} - {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        서비스 Health Check (모든 서비스 공통)

        Returns:
            Health check 응답
        """
        try:
            response = await self._request("GET", "/health")
            logger.info(f"{self.service_name} health check passed")
            return response
        except Exception as e:
            logger.error(f"{self.service_name} health check failed: {e}")
            return {"status": "error", "message": str(e)}

    async def close(self):
        """클라이언트 종료"""
        await self.client.aclose()
        logger.info(f"{self.__class__.__name__} closed")

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.close()

    def set_auth_token(self, token: str):
        """
        인증 토큰 동적 설정/변경

        Args:
            token: 새로운 JWT 토큰
        """
        self.auth_token = token
        self.client.headers["Authorization"] = f"Bearer {token}"
        logger.debug(f"{self.__class__.__name__} auth token updated")

    def remove_auth_token(self):
        """인증 토큰 제거"""
        self.auth_token = ""
        self.client.headers.pop("Authorization", None)
        logger.debug(f"{self.__class__.__name__} auth token removed")
