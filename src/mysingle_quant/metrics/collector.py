"""Enhanced metrics collector with performance optimizations."""

import asyncio
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""

    max_duration_samples: int = 1000
    max_histogram_buckets: int = 20
    enable_percentiles: bool = True
    enable_histogram: bool = True
    retention_period_seconds: int = 3600  # 1 hour
    cleanup_interval_seconds: int = 300  # 5 minutes


@dataclass
class RouteMetrics:
    """Metrics for a specific route."""

    request_count: int = 0
    error_count: int = 0
    durations: deque[float] = field(default_factory=lambda: deque(maxlen=1000))
    last_accessed: float = field(default_factory=time.time)
    status_codes: defaultdict[int, int] = field(
        default_factory=lambda: defaultdict(int)
    )


class MetricsCollector:
    """Enhanced in-memory metrics collector with performance optimizations."""

    def __init__(self, service_name: str, config: MetricsConfig | None = None):
        self.service_name = service_name
        self.config = config or MetricsConfig()
        self.start_time = time.time()

        # 효율적인 데이터 구조 사용
        self.routes: dict[str, RouteMetrics] = {}
        self._lock = asyncio.Lock() if hasattr(asyncio, "current_task") else None

        # 전역 카운터
        self.total_requests = 0
        self.total_errors = 0

        # 백그라운드 정리 작업
        self._cleanup_task: asyncio.Task | None = None
        self._start_cleanup_task()

    def _start_cleanup_task(self) -> None:
        """Start background cleanup task."""
        try:
            if asyncio.get_running_loop():
                self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        except RuntimeError:
            # No event loop running
            pass

    async def _periodic_cleanup(self) -> None:
        """Periodically clean up old metrics data."""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                await self._cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Error in metrics cleanup: {e}")

    async def _cleanup_old_metrics(self) -> None:
        """Remove old metrics data to prevent memory bloat."""
        current_time = time.time()
        cutoff_time = current_time - self.config.retention_period_seconds

        routes_to_remove = []
        for route_key, metrics in self.routes.items():
            if metrics.last_accessed < cutoff_time:
                routes_to_remove.append(route_key)

        for route_key in routes_to_remove:
            del self.routes[route_key]

        if routes_to_remove:
            logger.debug(f"Cleaned up {len(routes_to_remove)} old route metrics")

    async def record_request(
        self, method: str, path: str, status_code: int, duration: float
    ) -> None:
        """Record a request metric asynchronously."""
        route_key = f"{method}:{path}"
        current_time = time.time()

        # 전역 카운터 업데이트
        self.total_requests += 1
        if status_code >= 400:
            self.total_errors += 1

        # 루트별 메트릭 업데이트
        if route_key not in self.routes:
            self.routes[route_key] = RouteMetrics()

        route_metrics = self.routes[route_key]
        route_metrics.request_count += 1
        route_metrics.last_accessed = current_time
        route_metrics.status_codes[status_code] += 1

        if status_code >= 400:
            route_metrics.error_count += 1

        # 지속 시간 추가 (메모리 효율적)
        route_metrics.durations.append(duration)

    def record_request_sync(
        self, method: str, path: str, status_code: int, duration: float
    ) -> None:
        """Synchronous version of record_request for compatibility."""
        try:
            # 항상 동기적으로 처리 (테스트 환경 호환성)
            route_key = f"{method}:{path}"
            current_time = time.time()

            self.total_requests += 1
            if status_code >= 400:
                self.total_errors += 1

            if route_key not in self.routes:
                self.routes[route_key] = RouteMetrics()

            route_metrics = self.routes[route_key]
            route_metrics.request_count += 1
            route_metrics.last_accessed = current_time
            route_metrics.status_codes[status_code] += 1

            if status_code >= 400:
                route_metrics.error_count += 1

            route_metrics.durations.append(duration)
        except Exception as e:
            logger.warning(f"Error recording metrics: {e}")

    def _calculate_percentiles(self, durations: deque[float]) -> dict[str, float]:
        """Calculate percentiles for response times."""
        if not durations or not self.config.enable_percentiles:
            return {}

        sorted_durations = sorted(durations)
        return {
            "p50": statistics.median(sorted_durations),
            "p90": (
                statistics.quantiles(sorted_durations, n=10)[8]
                if len(sorted_durations) >= 10
                else sorted_durations[-1]
            ),
            "p95": (
                statistics.quantiles(sorted_durations, n=20)[18]
                if len(sorted_durations) >= 20
                else sorted_durations[-1]
            ),
            "p99": (
                statistics.quantiles(sorted_durations, n=100)[98]
                if len(sorted_durations) >= 100
                else sorted_durations[-1]
            ),
        }

    def _calculate_histogram(self, durations: deque[float]) -> dict[str, Any]:
        """Calculate histogram for response times."""
        if not durations or not self.config.enable_histogram:
            return {}

        # 히스토그램 버킷 생성
        max_duration = max(durations)
        bucket_size = max_duration / self.config.max_histogram_buckets

        buckets: dict[str, int] = {}
        for duration in durations:
            bucket = int(duration / bucket_size) if bucket_size > 0 else 0
            bucket_key = f"le_{bucket * bucket_size:.3f}"
            buckets[bucket_key] = buckets.get(bucket_key, 0) + 1

        return {
            "buckets": buckets,
            "bucket_size": bucket_size,
            "total_samples": len(durations),
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive metrics summary."""
        uptime = time.time() - self.start_time

        # 루트별 상세 메트릭
        routes_metrics = {}
        for route_key, route_metrics in self.routes.items():
            durations = route_metrics.durations

            route_data = {
                "request_count": route_metrics.request_count,
                "error_count": route_metrics.error_count,
                "error_rate": (
                    route_metrics.error_count / route_metrics.request_count
                    if route_metrics.request_count > 0
                    else 0
                ),
                "status_codes": dict(route_metrics.status_codes),
                "last_accessed": route_metrics.last_accessed,
            }

            # 응답 시간 통계
            if durations:
                route_data.update(
                    {
                        "avg_response_time": sum(durations) / len(durations),
                        "min_response_time": min(durations),
                        "max_response_time": max(durations),
                        "total_samples": len(durations),
                    }
                )

                # 백분위수 추가
                route_data.update(self._calculate_percentiles(durations))

                # 히스토그램 추가
                histogram = self._calculate_histogram(durations)
                if histogram:
                    route_data["histogram"] = histogram  # type: ignore[assignment]

            routes_metrics[route_key] = route_data

        return {
            "service": self.service_name,
            "timestamp": time.time(),
            "uptime_seconds": uptime,
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": (
                self.total_errors / self.total_requests
                if self.total_requests > 0
                else 0
            ),
            "requests_per_second": self.total_requests / uptime if uptime > 0 else 0,
            "active_routes": len(self.routes),
            "config": {
                "max_duration_samples": self.config.max_duration_samples,
                "enable_percentiles": self.config.enable_percentiles,
                "enable_histogram": self.config.enable_histogram,
                "retention_period_seconds": self.config.retention_period_seconds,
            },
            "routes": routes_metrics,
        }

    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus-formatted metrics."""
        metrics = self.get_metrics()
        lines = []

        service_name = self.service_name.replace("-", "_").replace(".", "_")

        # 기본 메트릭
        lines.extend(
            [
                f"# HELP {service_name}_uptime_seconds Service uptime in seconds",
                f"# TYPE {service_name}_uptime_seconds gauge",
                f"{service_name}_uptime_seconds {metrics['uptime_seconds']:.2f}",
                "",
                f"# HELP {service_name}_requests_total Total number of requests",
                f"# TYPE {service_name}_requests_total counter",
                f"{service_name}_requests_total {metrics['total_requests']}",
                "",
                f"# HELP {service_name}_errors_total Total number of errors",
                f"# TYPE {service_name}_errors_total counter",
                f"{service_name}_errors_total {metrics['total_errors']}",
                "",
                f"# HELP {service_name}_requests_per_second Current requests per second",
                f"# TYPE {service_name}_requests_per_second gauge",
                f"{service_name}_requests_per_second {metrics['requests_per_second']:.2f}",
                "",
            ]
        )

        # 루트별 메트릭
        for route, route_data in metrics["routes"].items():
            method, path = route.split(":", 1)
            labels = f'method="{method}",path="{path}"'

            lines.extend(
                [
                    f"# HELP {service_name}_route_requests_total Total requests per route",
                    f"# TYPE {service_name}_route_requests_total counter",
                    f"{service_name}_route_requests_total{{{labels}}} {route_data['request_count']}",
                    "",
                    f"# HELP {service_name}_route_errors_total Total errors per route",
                    f"# TYPE {service_name}_route_errors_total counter",
                    f"{service_name}_route_errors_total{{{labels}}} {route_data['error_count']}",
                    "",
                ]
            )

            if "avg_response_time" in route_data:
                lines.extend(
                    [
                        f"# HELP {service_name}_route_duration_seconds Average response time per route",
                        f"# TYPE {service_name}_route_duration_seconds gauge",
                        f"{service_name}_route_duration_seconds{{{labels}}} {route_data['avg_response_time']:.4f}",
                        "",
                    ]
                )

                # 백분위수 메트릭
                for percentile in ["p50", "p90", "p95", "p99"]:
                    if percentile in route_data:
                        lines.extend(
                            [
                                f"# HELP {service_name}_route_duration_{percentile}_seconds {percentile.upper()} response time per route",
                                f"# TYPE {service_name}_route_duration_{percentile}_seconds gauge",
                                f"{service_name}_route_duration_{percentile}_seconds{{{labels}}} {route_data[percentile]:.4f}",
                                "",
                            ]
                        )

        return "\n".join(lines)

    def reset_metrics(self) -> None:
        """Reset all metrics (useful for testing)."""
        self.routes.clear()
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = time.time()

    def __del__(self) -> None:
        """Cleanup when collector is destroyed."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
