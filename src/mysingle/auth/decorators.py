"""Simplified Authorization Decorators

Provides two decorators:
- @authorized: For authenticated users (is_active=true, is_verified=true)
- @admin_only: For admin users (is_superuser=true)

Since is_active and is_verified are already validated at IAM login,
all authenticated users are active and verified.
"""

from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, Request, status

from mysingle.core.logging import get_structured_logger

logger = get_structured_logger(__name__)


class AuthorizationFailed(HTTPException):
    """Authorization failed exception"""

    def __init__(self, detail: str = "Authorization failed"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _extract_request(*args: Any, **kwargs: Any) -> Request:
    """Extract FastAPI Request from args/kwargs"""
    for arg in args:
        if isinstance(arg, Request):
            return arg
    for value in kwargs.values():
        if isinstance(value, Request):
            return value
    raise RuntimeError("Request object not found in endpoint parameters")


def _ensure_async(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap sync function to async if needed"""
    if asyncio.iscoroutinefunction(func):
        return func

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return wrapper


def _get_user_id(request: Request) -> str:
    """Internal: Get user_id from request.state (raises 401 if missing)"""
    from typing import Optional

    user_id: Optional[str] = getattr(request.state, "user_id", None)

    if not user_id:
        logger.warning("No user_id in request.state - authentication required")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return user_id


def authorized(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    인증된 사용자 전용 데코레이터

    IAM 로그인에서 is_active=true, is_verified=true 검증이 완료되므로
    이 데코레이터는 단순히 인증 여부만 확인합니다.

    Usage:
        @authorized
        async def endpoint(request: Request):
            ...

    Note:
        is_active=false or is_verified=false 유저는 IAM 로그인에서 이미 차단되므로
        JWT를 받은 유저는 모두 active + verified 상태입니다.
    """
    async_func = _ensure_async(func)

    @wraps(func)
    async def inner(*args: Any, **kwargs: Any):
        request = _extract_request(*args, **kwargs)

        # 기본 인증 확인 (user_id 존재 여부)
        _get_user_id(request)  # Raises 401 if not authenticated

        return await async_func(*args, **kwargs)

    return inner


def admin_only(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    관리자 전용 데코레이터

    인증 + is_superuser=true 검증

    Usage:
        @admin_only
        async def admin_endpoint(request: Request):
            ...
    """
    async_func = _ensure_async(func)

    @wraps(func)
    async def inner(*args: Any, **kwargs: Any):
        request = _extract_request(*args, **kwargs)

        # 1. 기본 인증 확인
        user_id = _get_user_id(request)  # Raises 401 if not authenticated

        # 2. Admin 권한 확인
        is_superuser = getattr(request.state, "is_superuser", False)
        if not is_superuser:
            logger.warning(
                "Non-admin user attempted admin access",
                user_id=user_id,
                endpoint=request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        return await async_func(*args, **kwargs)

    return inner


def resource_owner_required(
    resource_user_id_getter: Callable[[Any], str],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    리소스 소유자 확인 데코레이터

    현재 사용자가 리소스의 소유자인지 확인합니다.
    관리자(is_superuser=true)는 모든 리소스에 접근 가능합니다.

    Args:
        resource_user_id_getter: 리소스에서 user_id를 추출하는 함수
            예: lambda resource: resource.user_id

    Usage:
        @resource_owner_required(lambda strategy: strategy.user_id)
        async def update_strategy(request: Request, strategy: Strategy):
            # strategy.user_id == current_user_id 검증 완료
            ...

    Raises:
        HTTPException(401): 인증되지 않은 경우
        HTTPException(403): 소유자가 아니고 관리자도 아닌 경우
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async_func = _ensure_async(func)

        @wraps(func)
        async def inner(*args: Any, **kwargs: Any):
            request = _extract_request(*args, **kwargs)

            # 1. 기본 인증 확인
            current_user_id = _get_user_id(request)  # Raises 401

            # 2. Admin은 모든 리소스 접근 가능
            is_superuser = getattr(request.state, "is_superuser", False)
            if is_superuser:
                return await async_func(*args, **kwargs)

            # 3. 리소스 소유자 확인
            try:
                # args[0]는 보통 self (클래스 메서드), args[1]은 request
                # 실제 리소스는 kwargs에 있거나 args 뒷부분
                resource = None
                for arg in args:
                    if not isinstance(arg, Request):
                        try:
                            resource_user_id = resource_user_id_getter(arg)
                            if resource_user_id:
                                resource = arg
                                break
                        except (AttributeError, TypeError, KeyError):
                            continue

                if not resource:
                    for value in kwargs.values():
                        if not isinstance(value, Request):
                            try:
                                resource_user_id = resource_user_id_getter(value)
                                if resource_user_id:
                                    resource = value
                                    break
                            except (AttributeError, TypeError, KeyError):
                                continue

                if not resource:
                    raise AuthorizationFailed("Resource not found in parameters")

                resource_user_id = resource_user_id_getter(resource)

                if str(resource_user_id) != str(current_user_id):
                    logger.warning(
                        "User attempted to access resource owned by another user",
                        current_user_id=current_user_id,
                        resource_user_id=resource_user_id,
                        endpoint=request.url.path,
                    )
                    raise AuthorizationFailed("You do not have access to this resource")

            except AuthorizationFailed:
                raise
            except Exception as e:
                logger.error(
                    "Error checking resource ownership",
                    error=str(e),
                    current_user_id=current_user_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error verifying resource ownership",
                )

            return await async_func(*args, **kwargs)

        return inner

    return decorator
