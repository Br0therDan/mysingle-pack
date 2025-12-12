"""
Kong Gateway Authentication Module

Simplified authentication based on Kong Gateway headers.
"""

from .decorators import admin_only, authorized, resource_owner_required
from .deps import (
    get_correlation_id,
    get_request_id,
    get_request_security_context,
    get_user_display_name,
    get_user_email,
    get_user_id,
    get_user_id_optional,
)
from .middleware import AuthMiddleware

__all__ = [
    # Core Functions
    "get_user_id",
    "get_user_id_optional",
    "get_user_email",
    "get_correlation_id",
    "get_request_id",
    # Utilities
    "get_user_display_name",
    "get_request_security_context",
    # Decorators
    "authorized",
    "admin_only",
    "resource_owner_required",
    # Middleware
    "AuthMiddleware",
]
