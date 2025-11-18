from typing import Optional, TypedDict

from fastapi import Request

from mysingle.constants import (
    HEADER_CORRELATION_ID,
    HEADER_KONG_CONSUMER_ID,
    HEADER_KONG_REQUEST_ID,
    HEADER_KONG_USER_ID,
    HEADER_USER_ID,
)


def _get_header(request: Request, key: str) -> Optional[str]:
    """Case-insensitive, trimmed header getter.

    Starlette's Headers mapping is case-insensitive, so we can use a single
    canonical lowercase key. Returns None for missing or empty values.
    """
    val = request.headers.get(key)
    if val is None:
        return None
    val = val.strip()
    return val or None


def get_kong_user_id(request: Request) -> Optional[str]:
    """
    애플리케이션 최종 사용자 ID.

    Kong Gateway에서 JWT 플러그인을 통해 주입하는 헤더:
    - X-Consumer-Custom-ID: JWT의 sub 클레임 값 (원본)
    - X-User-Id: 다운스트림 서비스로 전파되는 표준 헤더

    우선순위:
    1. X-User-Id (서비스 간 전파 표준)
    2. X-Consumer-Custom-ID (Kong JWT 플러그인 원본)
    """
    # 우선순위 1: 서비스 간 전파 표준 헤더
    user_id = _get_header(request, HEADER_USER_ID.lower())
    if user_id:
        return user_id

    # 우선순위 2: Kong JWT 플러그인 원본 헤더
    return _get_header(request, HEADER_KONG_USER_ID.lower())


def get_kong_consumer_id(request: Request) -> Optional[str]:
    """Kong Consumer 내부 ID"""
    return _get_header(request, HEADER_KONG_CONSUMER_ID.lower())


def get_kong_consumer_username(request: Request) -> Optional[str]:
    """Kong Consumer username"""
    return _get_header(request, "x-consumer-username")


def get_kong_forwarded_service(request: Request) -> Optional[str]:
    """Kong Request Transformer가 추가한 서비스명"""
    return _get_header(request, "x-forwarded-service")


def is_kong_authenticated(request: Request) -> bool:
    """Kong 헤더가 존재하면 인증된 것으로 판단"""
    return bool(get_kong_user_id(request))


class KongHeaders(TypedDict, total=False):
    user_id: Optional[str]
    consumer_id: Optional[str]
    consumer_username: Optional[str]
    forwarded_service: Optional[str]
    is_authenticated: bool


def get_kong_headers_dict(request: Request) -> KongHeaders:
    """표준 Kong 인증 헤더를 dict로 반환"""
    return {
        "user_id": get_kong_user_id(request),
        "consumer_id": get_kong_consumer_id(request),
        "consumer_username": get_kong_consumer_username(request),
        "forwarded_service": get_kong_forwarded_service(request),
        "is_authenticated": is_kong_authenticated(request),
    }


def get_kong_correlation_id(request: Request) -> Optional[str]:
    """
    Correlation ID 추출

    X-Correlation-Id 헤더를 우선 사용하며, 없으면 대체 헤더 확인
    """
    return _get_header(request, HEADER_CORRELATION_ID.lower()) or _get_header(
        request, "correlation-id"
    )


def get_kong_request_id(request: Request) -> Optional[str]:
    """
    Kong Request ID 추출

    X-Kong-Request-Id 헤더를 우선 사용하며, 없으면 대체 헤더 확인
    """
    return _get_header(request, HEADER_KONG_REQUEST_ID.lower()) or _get_header(
        request, "x-request-id"
    )


def get_kong_upstream_latency(request: Request) -> Optional[str]:
    """업스트림 지연시간(ms)"""
    return _get_header(request, "x-kong-upstream-latency")


def get_kong_proxy_latency(request: Request) -> Optional[str]:
    """프록시 지연시간(ms)"""
    return _get_header(request, "x-kong-proxy-latency")


class KongExtendedHeaders(KongHeaders, total=False):
    correlation_id: Optional[str]
    request_id: Optional[str]
    upstream_latency: Optional[str]
    proxy_latency: Optional[str]


def get_extended_kong_headers_dict(request: Request) -> KongExtendedHeaders:
    """기본 인증 헤더 + 운영 헤더 전체 반환"""
    base_headers = get_kong_headers_dict(request)
    extended_headers: KongExtendedHeaders = {
        **base_headers,
        "correlation_id": get_kong_correlation_id(request),
        "request_id": get_kong_request_id(request),
        "upstream_latency": get_kong_upstream_latency(request),
        "proxy_latency": get_kong_proxy_latency(request),
    }
    return extended_headers
