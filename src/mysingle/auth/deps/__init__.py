"""
Auth dependencies public interface (modularized)

Note:
- Backward compatibility wrappers for FastAPI Depends() are intentionally omitted.
- Prefer Request-based helpers and decorators.
"""

from .core import (
    get_current_active_superuser,
    get_current_active_user,
    get_current_active_verified_user,
    get_current_user,
    get_current_user_optional,
    get_request_security_context,
    get_user_display_name,
    get_user_email,
    get_user_id,
    is_user_authenticated,
)
from .decorators import (
    admin_only,
    authenticated,
    resource_owner_required,
    roles_required,
    verified_only,
)
from .kong import (
    get_kong_correlation_id,
    get_kong_proxy_latency,
    get_kong_request_id,
    get_kong_upstream_latency,
    get_kong_user_id,
    is_kong_authenticated,
)
from .permissions import (
    require_admin_access,
    require_user_role,
)

__all__ = [
    # core
    "get_current_user",
    "get_current_active_user",
    "get_current_active_verified_user",
    "get_current_active_superuser",
    "get_current_user_optional",
    "is_user_authenticated",
    "get_user_id",
    "get_user_email",
    "get_user_display_name",
    "get_request_security_context",
    # kong (simplified - only actively used functions)
    "get_kong_user_id",
    "is_kong_authenticated",
    "get_kong_correlation_id",
    "get_kong_request_id",
    "get_kong_upstream_latency",
    "get_kong_proxy_latency",
    # permissions
    "require_user_role",
    "require_admin_access",
    # decorators
    "authenticated",
    "verified_only",
    "admin_only",
    "roles_required",
    "resource_owner_required",
]
