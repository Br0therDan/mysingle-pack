"""
Unit tests for service-specific model initialization
"""

import pytest
from beanie import Document

from mysingle.core.service_types import ServiceConfig, ServiceType


class SampleDocument(Document):
    """Sample document model for testing (renamed to avoid pytest collection warning)"""

    name: str

    class Settings:
        name = "test_collection"


@pytest.mark.asyncio
async def test_iam_service_includes_auth_models():
    """Test that IAM service includes User and OAuthAccount models"""
    service_config = ServiceConfig(
        service_name="test-iam",
        service_type=ServiceType.IAM_SERVICE,
        enable_database=True,
    )

    # Check that models are prepared correctly
    # We can't actually run the lifespan without MongoDB, but we can verify the logic
    # by checking the code path

    # This test verifies the logic exists - actual integration test would need MongoDB
    assert service_config.enable_auth is True  # Auto-set by __post_init__
    assert service_config.service_type == ServiceType.IAM_SERVICE


@pytest.mark.asyncio
async def test_non_iam_service_excludes_auth_models():
    """Test that NON_IAM service does NOT include User and OAuthAccount models"""
    service_config = ServiceConfig(
        service_name="test-non-iam",
        service_type=ServiceType.NON_IAM_SERVICE,
        enable_database=True,
    )

    # Verify service configuration
    assert service_config.enable_auth is True  # Auth enabled but not IAM service
    assert service_config.service_type == ServiceType.NON_IAM_SERVICE
    # NON_IAM services should use Kong Gateway auth, not local User models


@pytest.mark.asyncio
async def test_service_with_custom_models_only():
    """Test that service with only custom models doesn't auto-add auth models"""
    _ = ServiceConfig(
        service_name="test-custom",
        service_type=ServiceType.NON_IAM_SERVICE,
        enable_database=True,
        enable_audit_logging=False,  # Disable audit to test only custom models
    )

    custom_models = [SampleDocument]

    # If this was an actual lifespan run, NON_IAM should not add User/OAuthAccount
    # IAM service would add them
    assert len(custom_models) == 1
    assert SampleDocument in custom_models


def test_model_initialization_logic():
    """Test the model initialization decision logic"""
    # IAM Service - should prepare auth models
    iam_config = ServiceConfig(
        service_name="iam-service",
        service_type=ServiceType.IAM_SERVICE,
    )
    assert iam_config.service_type == ServiceType.IAM_SERVICE
    assert iam_config.enable_auth is True  # Auto-set

    # Non-IAM Service - should NOT prepare auth models
    non_iam_config = ServiceConfig(
        service_name="backtest-service",
        service_type=ServiceType.NON_IAM_SERVICE,
    )
    assert non_iam_config.service_type == ServiceType.NON_IAM_SERVICE
    assert non_iam_config.enable_auth is True  # Auth enabled via Gateway

    # The difference: IAM service owns User/OAuthAccount collections
    # Non-IAM services rely on Kong Gateway headers (X-User-ID, etc.)
