"""
Tests for mysingle.core.metrics module.
"""


from mysingle.core.metrics import MetricsCollector, get_metrics_collector


def test_metrics_collector_initialization():
    """Test MetricsCollector initialization."""
    collector = MetricsCollector(service_name="test-service")

    assert collector is not None
    assert hasattr(collector, "counter")
    assert hasattr(collector, "histogram")
    assert hasattr(collector, "gauge")


def test_get_metrics_collector():
    """Test get_metrics_collector singleton."""
    collector1 = get_metrics_collector()
    collector2 = get_metrics_collector()

    assert collector1 is collector2  # Should be the same instance


def test_metrics_counter():
    """Test counter metric."""
    collector = MetricsCollector(service_name="test-service")

    # Create counter
    counter = collector.counter(
        name="test_counter",
        description="Test counter",
    )

    assert counter is not None

    # Increment counter
    counter.inc()
    counter.inc(2)


def test_metrics_histogram():
    """Test histogram metric."""
    collector = MetricsCollector(service_name="test-service")

    # Create histogram
    histogram = collector.histogram(
        name="test_histogram",
        description="Test histogram",
    )

    assert histogram is not None

    # Observe values
    histogram.observe(0.5)
    histogram.observe(1.0)
    histogram.observe(2.5)


def test_metrics_gauge():
    """Test gauge metric."""
    collector = MetricsCollector(service_name="test-service")

    # Create gauge
    gauge = collector.gauge(
        name="test_gauge",
        description="Test gauge",
    )

    assert gauge is not None

    # Set gauge values
    gauge.set(10)
    gauge.inc()
    gauge.dec()
    gauge.set(5)


def test_metrics_with_labels():
    """Test metrics with labels."""
    collector = MetricsCollector(service_name="test-service")

    # Create counter with labels
    counter = collector.counter(
        name="test_labeled_counter",
        description="Test counter with labels",
        labels=["method", "endpoint"],
    )

    assert counter is not None

    # Increment with labels
    counter.labels(method="GET", endpoint="/api/test").inc()
    counter.labels(method="POST", endpoint="/api/test").inc(2)
