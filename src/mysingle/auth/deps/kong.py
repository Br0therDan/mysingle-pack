from typing import Optional

from fastapi import Request


def get_kong_user_id(request: Request) -> Optional[str]:
    """Kong JWT Plugin이 전달한 사용자 ID (X-Consumer-Custom-ID | X-User-Id)"""
    return (
        request.headers.get("x-consumer-custom-id")
        or request.headers.get("X-Consumer-Custom-ID")
        or request.headers.get("x-user-id")
        or request.headers.get("X-User-Id")
    )


def get_kong_consumer_id(request: Request) -> Optional[str]:
    """Kong Consumer 내부 ID"""
    return request.headers.get("x-consumer-id") or request.headers.get("X-Consumer-ID")


def get_kong_consumer_username(request: Request) -> Optional[str]:
    """Kong Consumer username"""
    return request.headers.get("x-consumer-username") or request.headers.get(
        "X-Consumer-Username"
    )


def get_kong_forwarded_service(request: Request) -> Optional[str]:
    """Kong Request Transformer가 추가한 서비스명"""
    return request.headers.get("x-forwarded-service") or request.headers.get(
        "X-Forwarded-Service"
    )


def is_kong_authenticated(request: Request) -> bool:
    """Kong 헤더가 존재하면 인증된 것으로 판단"""
    return get_kong_user_id(request) is not None


def get_kong_headers_dict(request: Request) -> dict:
    """표준 Kong 인증 헤더를 dict로 반환"""
    return {
        "user_id": get_kong_user_id(request),
        "consumer_id": get_kong_consumer_id(request),
        "consumer_username": get_kong_consumer_username(request),
        "forwarded_service": get_kong_forwarded_service(request),
        "is_authenticated": is_kong_authenticated(request),
    }


def get_kong_correlation_id(request: Request) -> Optional[str]:
    """Correlation ID 추출"""
    return (
        request.headers.get("x-correlation-id")
        or request.headers.get("X-Correlation-Id")
        or request.headers.get("correlation-id")
        or request.headers.get("Correlation-Id")
    )


def get_kong_request_id(request: Request) -> Optional[str]:
    """Kong Request ID 추출"""
    return (
        request.headers.get("x-kong-request-id")
        or request.headers.get("X-Kong-Request-Id")
        or request.headers.get("x-request-id")
        or request.headers.get("X-Request-Id")
    )


def get_kong_upstream_latency(request: Request) -> Optional[str]:
    """업스트림 지연시간(ms)"""
    return request.headers.get("x-kong-upstream-latency") or request.headers.get(
        "X-Kong-Upstream-Latency"
    )


def get_kong_proxy_latency(request: Request) -> Optional[str]:
    """프록시 지연시간(ms)"""
    return request.headers.get("x-kong-proxy-latency") or request.headers.get(
        "X-Kong-Proxy-Latency"
    )


def get_extended_kong_headers_dict(request: Request) -> dict:
    """기본 인증 헤더 + 운영 헤더 전체 반환"""
    base_headers = get_kong_headers_dict(request)
    extended_headers = {
        **base_headers,
        "correlation_id": get_kong_correlation_id(request),
        "request_id": get_kong_request_id(request),
        "upstream_latency": get_kong_upstream_latency(request),
        "proxy_latency": get_kong_proxy_latency(request),
    }
    return extended_headers
