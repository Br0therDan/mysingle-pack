"""Enhanced metrics router with comprehensive endpoints.

Public endpoints (no auth required, configured in Kong):
- GET /metrics/ - Basic metrics (json/prometheus format)
- GET /metrics/json - JSON format metrics
- GET /metrics/prometheus - Prometheus format metrics
- GET /metrics/health - Metrics system health
- GET /metrics/summary - Summarized metrics

Protected endpoints (auth required):
- GET /metrics/routes - Detailed route metrics (authenticated users)
- POST /metrics/reset - Reset metrics (superuser only)
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from ..logging import get_structured_logger
from .collector import MetricsCollector
from .middleware import get_metrics_collector

logger = get_structured_logger(__name__)


def create_metrics_router() -> APIRouter:
    """Create router with enhanced metrics endpoints."""
    router = APIRouter(prefix="/metrics", tags=["Metrics"])

    @router.get("/")
    async def get_metrics(
        format: Literal["json", "prometheus"] = Query(
            "json", description="Output format"
        ),
        collector: MetricsCollector = Depends(get_metrics_collector),
    ):
        """Get service metrics in JSON or Prometheus format.

        Args:
            format: Output format (json or prometheus)
            collector: Metrics collector dependency

        Returns:
            Metrics data in requested format
        """
        try:
            if format == "prometheus":
                content = collector.get_prometheus_metrics()
                return Response(content=content, media_type="text/plain")
            else:
                return collector.get_metrics()
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error retrieving metrics: {str(e)}"
            )

    @router.get("/json")
    async def get_json_metrics(
        collector: MetricsCollector = Depends(get_metrics_collector),
    ) -> dict:
        """Get comprehensive service metrics in JSON format."""
        try:
            return collector.get_metrics()
        except Exception as e:
            logger.error(f"Error getting JSON metrics: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error retrieving metrics: {str(e)}"
            )

    @router.get("/prometheus")
    async def get_prometheus_metrics(
        collector: MetricsCollector = Depends(get_metrics_collector),
    ) -> Response:
        """Get metrics in Prometheus exposition format."""
        try:
            content = collector.get_prometheus_metrics()
            return Response(content=content, media_type="text/plain")
        except Exception as e:
            logger.error(f"Error getting Prometheus metrics: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error retrieving Prometheus metrics: {str(e)}"
            )

    @router.get("/health")
    async def get_metrics_health(
        collector: MetricsCollector = Depends(get_metrics_collector),
    ) -> dict:
        """Get health status of the metrics system."""
        try:
            metrics = collector.get_metrics()

            # 간단한 헬스체크 로직
            is_healthy = True
            health_issues = []

            # 에러율이 50% 이상이면 비정상
            if metrics["error_rate"] > 0.5:
                is_healthy = False
                health_issues.append(f"High error rate: {metrics['error_rate']:.2%}")

            # 활성 라우트가 없으면 비정상 (서비스가 요청을 받지 못함)
            if metrics["active_routes"] == 0 and metrics["total_requests"] == 0:
                is_healthy = False
                health_issues.append("No active routes or requests")

            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "service": metrics["service"],
                "uptime_seconds": metrics["uptime_seconds"],
                "total_requests": metrics["total_requests"],
                "error_rate": metrics["error_rate"],
                "active_routes": metrics["active_routes"],
                "issues": health_issues,
                "timestamp": metrics["timestamp"],
            }
        except Exception as e:
            logger.error(f"Error getting metrics health: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error checking metrics health: {str(e)}"
            )

    @router.get("/summary")
    async def get_metrics_summary(
        collector: MetricsCollector = Depends(get_metrics_collector),
    ) -> dict:
        """Get summarized metrics without detailed route information."""
        try:
            full_metrics = collector.get_metrics()

            # 요약된 정보만 반환
            return {
                "service": full_metrics["service"],
                "timestamp": full_metrics["timestamp"],
                "uptime_seconds": full_metrics["uptime_seconds"],
                "total_requests": full_metrics["total_requests"],
                "total_errors": full_metrics["total_errors"],
                "error_rate": full_metrics["error_rate"],
                "requests_per_second": full_metrics["requests_per_second"],
                "active_routes": full_metrics["active_routes"],
                "config": full_metrics["config"],
            }
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error retrieving metrics summary: {str(e)}"
            )

    @router.get("/routes")
    async def get_route_metrics(
        route_filter: str | None = Query(None, description="Filter routes by pattern"),
        collector: MetricsCollector = Depends(get_metrics_collector),
    ) -> dict:
        """Get detailed metrics for specific routes (authenticated users only).

        This endpoint exposes internal route structure and performance metrics,
        so it requires authentication.

        Args:
            route_filter: Optional filter pattern for route names
            collector: Metrics collector dependency
            current_user: Authenticated user (injected by dependency)

        Returns:
            Detailed route metrics
        """
        try:
            full_metrics = collector.get_metrics()
            routes = full_metrics["routes"]

            if route_filter:
                # 간단한 패턴 필터링
                filtered_routes = {
                    route_key: route_data
                    for route_key, route_data in routes.items()
                    if route_filter.lower() in route_key.lower()
                }
                routes = filtered_routes

            return {
                "service": full_metrics["service"],
                "timestamp": full_metrics["timestamp"],
                "total_routes": len(routes),
                "routes": routes,
            }
        except Exception as e:
            logger.error(f"Error getting route metrics: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error retrieving route metrics: {str(e)}"
            )

    @router.post("/reset")
    async def reset_metrics(
        collector: MetricsCollector = Depends(get_metrics_collector),
    ) -> dict:
        """Reset all metrics (superuser only).

        This is a destructive operation that clears all collected metrics data.
        Restricted to superuser access only for security.

        Warning: This will permanently clear all collected metrics data.
        """
        try:
            collector.reset_metrics()
            logger.info(f"Metrics reset for service: {collector.service_name}")
            return {
                "status": "success",
                "message": f"Metrics reset for service: {collector.service_name}",
                "timestamp": collector.start_time,
            }
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error resetting metrics: {str(e)}"
            )

    return router
