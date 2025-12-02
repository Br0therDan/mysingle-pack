from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Callable

from fastapi import Request

from mysingle.auth.exceptions import AuthorizationFailed
from mysingle.core.logging import get_structured_logger

from .core import (
    get_current_active_superuser,
    get_current_active_verified_user,
    get_current_user,
)
from .permissions import require_user_role

logger = get_structured_logger(__name__)


def _extract_request(*args: Any, **kwargs: Any) -> Request:
    """전달된 args/kwargs에서 FastAPI Request를 추출.
    엔드포인트 첫 인자 또는 키워드 인자에 존재한다고 가정한다.
    """
    for arg in args:
        if isinstance(arg, Request):
            return arg
    for value in kwargs.values():
        if isinstance(value, Request):
            return value
    raise RuntimeError("Request object not found in endpoint parameters")


def _ensure_async(func: Callable[..., Any]) -> Callable[..., Any]:
    """func가 sync면 스레드 풀로 감싸고, async면 그대로 반환."""
    if asyncio.iscoroutinefunction(func):
        return func

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return wrapper


def authenticated(func: Callable[..., Any]) -> Callable[..., Any]:
    """인증 필수 데코레이터 (기본 사용자 보장)"""

    async_func = _ensure_async(func)

    @wraps(func)
    async def inner(*args: Any, **kwargs: Any):
        request = _extract_request(*args, **kwargs)
        # 검증: 미들웨어가 주입한 사용자 보장
        _ = get_current_user(request)
        return await async_func(*args, **kwargs)

    return inner


def verified_only(func: Callable[..., Any]) -> Callable[..., Any]:
    """이메일 검증 사용자만 허용"""

    async_func = _ensure_async(func)

    @wraps(func)
    async def inner(*args: Any, **kwargs: Any):
        request = _extract_request(*args, **kwargs)
        _ = get_current_active_verified_user(request)
        return await async_func(*args, **kwargs)

    return inner


def admin_only(func: Callable[..., Any]) -> Callable[..., Any]:
    """관리자(슈퍼유저) 전용"""

    async_func = _ensure_async(func)

    @wraps(func)
    async def inner(*args: Any, **kwargs: Any):
        request = _extract_request(*args, **kwargs)
        _ = get_current_active_superuser(request)
        return await async_func(*args, **kwargs)

    return inner


def roles_required(*roles: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """특정 역할 요구 데코레이터"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async_func = _ensure_async(func)

        @wraps(func)
        async def inner(*args: Any, **kwargs: Any):
            request = _extract_request(*args, **kwargs)
            _ = require_user_role(request, list(roles))
            return await async_func(*args, **kwargs)

        return inner

    return decorator


def resource_owner_required(
    param_name: str | None = None,
    *,
    extractor: Callable[[Request, dict[str, Any]], Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    리소스 소유자 요구 데코레이터.

    - 엔드포인트의 경로/쿼리 인자 중 `param_name`으로 전달된 사용자 ID와
      현재 인증된 사용자 ID가 동일해야 접근을 허용합니다.
    - param_name 값은 함수의 키워드 인자(kwargs), Request.path_params, Request.query_params에서 찾습니다.
    - extractor 콜백을 제공하면 Request와 kwargs를 받아 소유자 ID를 직접 추출할 수 있습니다.
    - 비교는 문자열로 수행합니다.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async_func = _ensure_async(func)

        @wraps(func)
        async def inner(*args: Any, **kwargs: Any):
            request = _extract_request(*args, **kwargs)
            current_user = get_current_user(request)

            owner_val: Any | None = None
            # 0) 커스텀 extractor가 제공되면 우선 사용
            if extractor is not None:
                try:
                    owner_val = extractor(request, kwargs)
                except Exception:
                    owner_val = None
            # 1) extractor 결과가 없고 param_name이 제공된 경우 자동 탐색
            if owner_val is None:
                if not param_name:
                    raise AuthorizationFailed(
                        required_permission="resource_owner",
                        user_id=str(current_user.id),
                    )
                # 1-1) 함수 키워드 인자에서 찾기
                owner_val = kwargs.get(param_name)
                # 1-2) 없으면 path_params에서 찾기
                if owner_val is None and hasattr(request, "path_params"):
                    owner_val = request.path_params.get(param_name)
                # 1-3) 없으면 query_params에서 찾기
                if owner_val is None and hasattr(request, "query_params"):
                    try:
                        owner_val = request.query_params.get(param_name)
                    except Exception:
                        pass

            if owner_val is None:
                raise AuthorizationFailed(
                    required_permission=f"resource_owner:{param_name or 'custom'}",
                    user_id=str(current_user.id),
                )

            # 문자열 비교로 통일
            if str(owner_val) != str(current_user.id):
                raise AuthorizationFailed(
                    required_permission=f"resource_owner:{param_name or 'custom'}",
                    user_id=str(current_user.id),
                )

            return await async_func(*args, **kwargs)

        return inner

    return decorator
