"""Enhanced metrics middleware with performance optimizations."""

import time
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from mysingle.core.logging import get_structured_logger

from .collector import MetricsCollector, MetricsConfig

logger = get_structured_logger(__name__)

# Global metrics collector
_metrics_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        raise RuntimeError("Metrics collector not initialized.")
    return _metrics_collector


class MetricsMiddleware(BaseHTTPMiddleware):
    """Enhanced middleware to collect HTTP request metrics with performance optimizations."""

    def __init__(
        self,
        app: Any,
        collector: MetricsCollector,
        exclude_paths: set[str] | None = None,
        include_response_headers: bool = True,
        track_user_agents: bool = False,
    ) -> None:
        super().__init__(app)
        self.collector = collector
        # 성능을 위해 메트릭에서 제외할 경로들 (health check 등)
        self.exclude_paths = exclude_paths or {
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        }
        self.include_response_headers = include_response_headers
        self.track_user_agents = track_user_agents

    def _should_track_request(self, request: Request) -> bool:
        """Determine if request should be tracked."""
        path = request.url.path

        # 제외 경로 확인
        if path in self.exclude_paths:
            return False

        # 정적 파일 제외 (성능 최적화)
        return not path.startswith(("/static/", "/assets/", "/favicon"))

    def _extract_route_pattern(self, request: Request) -> str:
        """Extract normalized route pattern from request."""
        try:
            # FastAPI route pattern 추출
            if hasattr(request, "scope") and "route" in request.scope:
                route = request.scope["route"]
                if hasattr(route, "path"):
                    return str(route.path)

            # 경로에서 ID 패턴 정규화 (성능 최적화)
            path = request.url.path

            # UUID 패턴 정규화
            import re

            uuid_pattern = (
                r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            )
            path = re.sub(uuid_pattern, "/{uuid}", path, flags=re.IGNORECASE)

            # 숫자 ID 패턴 정규화
            numeric_pattern = r"/\d+"
            path = re.sub(numeric_pattern, "/{id}", path)

            return path

        except Exception as e:
            logger.debug(f"Error extracting route pattern: {e}")
            return request.url.path

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Process request and collect metrics with enhanced performance."""
        # 성능 최적화: 추적하지 않을 요청은 빠르게 처리
        if not self._should_track_request(request):
            early_response: Response = await call_next(request)
            return early_response

        start_time = time.time()

        # 경로 패턴 추출
        route_path = self._extract_route_pattern(request)

        try:
            # 요청 처리
            response: Response = await call_next(request)
        except Exception as e:
            # 예외 발생 시에도 메트릭 기록
            duration = time.time() - start_time
            self.collector.record_request_sync(
                method=request.method,
                path=route_path,
                status_code=500,
                duration=duration,
            )
            logger.error(f"Error processing request {request.method} {route_path}: {e}")
            raise

        # 지속 시간 계산
        duration = time.time() - start_time

        # 메트릭 기록 (비동기로 처리하여 응답 지연 최소화)
        try:
            self.collector.record_request_sync(
                method=request.method,
                path=route_path,
                status_code=response.status_code,
                duration=duration,
            )
        except Exception as e:
            logger.warning(f"Error recording metrics: {e}")

        # 응답 헤더 추가 (선택적)
        if self.include_response_headers:
            response.headers["X-Response-Time"] = f"{duration:.4f}s"
            response.headers["X-Service-Name"] = self.collector.service_name

        return response


def create_metrics_middleware(
    service_name: str,
    config: MetricsConfig | None = None,
    exclude_paths: set[str] | None = None,
) -> None:
    """Create and configure metrics middleware for the given service.

    Args:
        service_name: Name of the service
        config: Metrics configuration
        exclude_paths: Paths to exclude from metrics collection

    Returns:
        None (sets up global collector)
    """
    global _metrics_collector

    try:
        # 설정 기본값
        metrics_config = config or MetricsConfig()

        # 메트릭 컬렉터 초기화
        _metrics_collector = MetricsCollector(service_name, metrics_config)

        logger.info(f"✅ Metrics collector initialized for {service_name}")
        logger.debug(f"Metrics config: {metrics_config}")

    except Exception as e:
        logger.error(f"❌ Failed to create metrics middleware for {service_name}: {e}")
        raise
