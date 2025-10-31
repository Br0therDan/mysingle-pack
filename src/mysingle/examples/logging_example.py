#!/usr/bin/env python3
"""
Structured Logging 시스템 테스트 예제

이 파일은 quant-pack의 structured logging 시스템이 올바르게 동작하는지 테스트합니다.
"""

import asyncio
from mysingle.logging import (
    configure_structured_logging,
    get_structured_logger,
    set_correlation_id,
    set_user_id,
    set_request_id,
    get_correlation_id,
    get_user_id,
    get_request_id,
    clear_logging_context,
    log_user_action,
    log_service_call,
    log_database_operation,
)


async def test_structured_logging():
    """Structured logging 시스템 테스트"""

    # 로깅 시스템 설정
    configure_structured_logging(service_name="logging-test", log_level="INFO")

    logger = get_structured_logger(__name__)

    print("=== Structured Logging 테스트 시작 ===")

    # 1. 기본 로깅 테스트
    logger.info("기본 로깅 테스트", extra={"test_type": "basic"})

    # 2. 컨텍스트 설정 테스트
    set_correlation_id("test-correlation-123")
    set_user_id("user-456")
    set_request_id("req-789")

    logger.info("컨텍스트 설정 후 로깅", extra={"context_test": True})

    # 3. 컨텍스트 조회 테스트
    print(f"Correlation ID: {get_correlation_id()}")
    print(f"User ID: {get_user_id()}")
    print(f"Request ID: {get_request_id()}")

    # 4. 편의 함수 테스트
    log_user_action(
        action="create_strategy",
        resource_type="strategy",
        resource_id="strategy-123",
        details={"name": "My Test Strategy", "version": "1.0"},
        success=True,
    )

    log_service_call(
        service_name="strategy-service",
        method="POST",
        endpoint="/strategies",
        duration=0.123,
        status_code=201,
    )

    log_database_operation(
        operation="insert", collection="strategies", duration=0.045, document_count=1
    )

    # 5. 에러 로깅 테스트
    log_user_action(
        action="delete_strategy",
        resource_type="strategy",
        resource_id="strategy-404",
        success=False,
        error="Strategy not found",
    )

    log_service_call(
        service_name="backtest-service",
        method="GET",
        endpoint="/backtests/invalid",
        duration=0.025,
        status_code=404,
        error="Not found",
    )

    log_database_operation(
        operation="find",
        collection="backtests",
        duration=0.123,
        error="Connection timeout",
    )

    # 6. 컨텍스트 초기화 테스트
    clear_logging_context()
    logger.info("컨텍스트 초기화 후 로깅")

    print(f"초기화 후 Correlation ID: {get_correlation_id()}")
    print(f"초기화 후 User ID: {get_user_id()}")
    print(f"초기화 후 Request ID: {get_request_id()}")

    print("=== Structured Logging 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_structured_logging())
