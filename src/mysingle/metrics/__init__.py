"""Enhanced metrics package with performance optimizations."""

from .collector import MetricsCollector, MetricsConfig
from .middleware import (
    MetricsMiddleware,
    create_metrics_middleware,
    get_metrics_collector,
)
from .router import create_metrics_router

__all__ = [
    # Core classes
    "MetricsCollector",
    "MetricsConfig",
    "MetricsMiddleware",
    # Factory functions
    "create_metrics_middleware",
    "create_metrics_router",
    "get_metrics_collector",
]
