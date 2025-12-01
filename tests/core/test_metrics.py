"""
Tests for mysingle.core.metrics module.
"""

import pytest

from mysingle.core.metrics import MetricsCollector, get_metrics_collector


def test_metrics_collector_initialization():
    """Test MetricsCollector initialization."""
    collector = MetricsCollector(service_name="test-service")

    assert collector is not None
    assert collector.service_name == "test-service"
    assert hasattr(collector, "routes")
    assert hasattr(collector, "total_requests")


def test_get_metrics_collector():
    """Test get_metrics_collector singleton."""
    # Reset the global collector first
    from mysingle.core.metrics import middleware as middleware_module

    # Initialize the global collector
    middleware_module._metrics_collector = MetricsCollector(service_name="test-service")

    # First call returns the initialized instance
    collector1 = get_metrics_collector()
    assert collector1 is not None
    assert collector1.service_name == "test-service"

    # Second call returns same instance (singleton)
    collector2 = get_metrics_collector()
    assert collector2 is collector1

    # Clean up
    middleware_module._metrics_collector = None


def test_metrics_counter():
    """Test counter metric."""
    collector = MetricsCollector(service_name="test-service")

    # MetricsCollector doesn't have counter() method
    # It tracks metrics via record_request
    assert collector.total_requests == 0
    assert collector.total_errors == 0


async def test_metrics_histogram():
    """Test histogram-like behavior via record_request."""
    collector = MetricsCollector(service_name="test-service")

    # Record multiple requests with different durations (histogram-like data)
    await collector.record_request("GET", "/api/items", 200, 0.5)
    await collector.record_request("GET", "/api/items", 200, 1.0)
    await collector.record_request("GET", "/api/items", 200, 2.5)

    # Verify metrics are recorded
    route_key = "GET:/api/items"
    assert route_key in collector.routes
    metrics = collector.routes[route_key]
    assert metrics.request_count == 3
    assert len(metrics.durations) == 3
    assert 0.5 in metrics.durations
    assert 1.0 in metrics.durations
    assert 2.5 in metrics.durations


async def test_metrics_gauge():
    """Test gauge-like behavior via request and error counts."""
    collector = MetricsCollector(service_name="test-service")

    # Gauge-like metrics: total requests and errors
    initial_requests = collector.total_requests
    initial_errors = collector.total_errors

    # Record successful requests
    await collector.record_request("GET", "/api/health", 200, 0.01)
    await collector.record_request("GET", "/api/health", 200, 0.02)

    # Record error request
    await collector.record_request("GET", "/api/data", 500, 0.5)

    # Verify counts increased (gauge-like behavior)
    assert collector.total_requests == initial_requests + 3
    assert collector.total_errors == initial_errors + 1


async def test_metrics_with_labels():
    """Test metrics with labels (method+path as label)."""
    collector = MetricsCollector(service_name="test-service")

    # Labels are represented by method:path route keys
    await collector.record_request("GET", "/api/users", 200, 0.1)
    await collector.record_request("POST", "/api/users", 201, 0.2)
    await collector.record_request("GET", "/api/items", 200, 0.15)

    # Verify different route keys (labels) are tracked separately
    assert "GET:/api/users" in collector.routes
    assert "POST:/api/users" in collector.routes
    assert "GET:/api/items" in collector.routes

    # Each route has independent metrics
    assert collector.routes["GET:/api/users"].request_count == 1
    assert collector.routes["POST:/api/users"].request_count == 1
    assert collector.routes["GET:/api/items"].request_count == 1
