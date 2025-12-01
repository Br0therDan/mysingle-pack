"""
통합 로깅 시스템 (Structured + Traditional Logging)

이 모듈은 기존 logging_config.py와 structured_logging.py를 통합하여
다음 기능을 제공합니다:

1. 구조화된 로깅 (structlog 기반)
   - Correlation ID, User ID, Request ID 컨텍스트 변수
   - JSON 출력 지원
   - 서비스명 자동 태깅
   - 편의 함수들 (log_user_action, log_service_call, log_database_operation)

2. 전통적인 로깅 (logging 기반)
   - 컬러 출력 (colorlog)
   - 파일 로깅 (app.log, error.log)
   - 외부 라이브러리 로그 레벨 조정

3. 통합 설정
   - 환경별 설정 (development, production)
   - 자동 서비스명 감지
   - FastAPI 미들웨어 통합 지원
"""

import logging
import sys
from contextvars import ContextVar
from pathlib import Path
from typing import Optional

import structlog

try:
    import colorlog

    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


# Correlation ID, User ID, Request ID 컨텍스트 변수
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


# =============================================================================
# 구조화된 로깅 시스템 (structlog)
# =============================================================================


class CorrelationIdProcessor:
    """Correlation ID를 로그에 추가하는 프로세서"""

    def __call__(self, logger, method_name, event_dict):
        correlation_id = correlation_id_var.get()
        if correlation_id:
            # 로그 메시지에 correlation ID 프리픽스 추가
            event_dict["event"] = (
                f"[{correlation_id[:8]}] {event_dict.get('event', '')}"
            )
        return event_dict


class ServiceNameProcessor:
    """서비스명을 로그에 추가하는 프로세서"""

    def __init__(self, service_name: str):
        self.service_name = service_name

    def __call__(self, logger, method_name, event_dict):
        event_dict["service"] = self.service_name
        return event_dict


class UserContextProcessor:
    """User ID와 Request ID를 로그에 추가하는 프로세서"""

    def __call__(self, logger, method_name, event_dict):
        user_id = user_id_var.get()
        request_id = request_id_var.get()

        if user_id:
            event_dict["user_id"] = user_id

        if request_id:
            event_dict["request_id"] = request_id

        return event_dict


def configure_structured_logging(
    service_name: str,
    log_level: str = "INFO",
    enable_json: bool = False,
    enable_correlation_id: bool = True,
    enable_user_context: bool = True,
):
    """
    구조화된 로깅 설정

    Args:
        service_name: 서비스명
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: JSON 형식 출력 활성화
        enable_correlation_id: Correlation ID 추가 활성화
        enable_user_context: User/Request ID 컨텍스트 추가 활성화
    """
    processors = [
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        ServiceNameProcessor(service_name),
    ]

    if enable_correlation_id:
        processors.append(CorrelationIdProcessor())

    if enable_user_context:
        processors.append(UserContextProcessor())

    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger = get_structured_logger(__name__)
    logger.info(
        "Structured logging configured",
        extra={
            "json_logging": enable_json,
            "correlation_id_enabled": enable_correlation_id,
        },
    )


def get_structured_logger(name: str):
    """구조화된 로거 인스턴스 획득"""
    return structlog.get_logger(name)


# =============================================================================
# 컨텍스트 변수 관리
# =============================================================================


def set_correlation_id(correlation_id: str):
    """Correlation ID 설정"""
    correlation_id_var.set(correlation_id)


def set_user_id(user_id: str):
    """User ID 설정"""
    user_id_var.set(user_id)


def set_request_id(request_id: str):
    """Request ID 설정"""
    request_id_var.set(request_id)


def get_correlation_id() -> str:
    """현재 Correlation ID 획득"""
    return correlation_id_var.get()


def get_user_id() -> str:
    """현재 User ID 획득"""
    return user_id_var.get()


def get_request_id() -> str:
    """현재 Request ID 획득"""
    return request_id_var.get()


def clear_logging_context():
    """로깅 컨텍스트 초기화"""
    correlation_id_var.set("")
    user_id_var.set("")
    request_id_var.set("")


# =============================================================================
# 편의 함수들 (구조화된 로깅)
# =============================================================================


def log_user_action(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    success: bool = True,
    error: Optional[str] = None,
):
    """사용자 액션 로깅"""
    logger = get_structured_logger(__name__)

    log_data = {
        "action": action,
        "resource_type": resource_type,
        "success": success,
    }

    if resource_id:
        log_data["resource_id"] = resource_id

    if details:
        log_data["details"] = details

    if error:
        log_data["error"] = error
        logger.error("User action failed", extra=log_data)
    else:
        logger.info("User action completed", extra=log_data)


def log_service_call(
    service_name: str,
    method: str,
    endpoint: str,
    duration: float,
    status_code: Optional[int] = None,
    error: Optional[str] = None,
):
    """서비스 호출 로깅"""
    logger = get_structured_logger(__name__)

    log_data = {
        "target_service": service_name,
        "http_method": method,
        "endpoint": endpoint,
        "duration_ms": round(duration * 1000, 2),
    }

    if status_code:
        log_data["status_code"] = status_code

    if error:
        log_data["error"] = error
        logger.error("Service call failed", extra=log_data)
    else:
        logger.info("Service call completed", extra=log_data)


def log_database_operation(
    operation: str,
    collection: str,
    duration: float,
    document_count: Optional[int] = None,
    error: Optional[str] = None,
):
    """데이터베이스 작업 로깅"""
    logger = get_structured_logger(__name__)

    log_data = {
        "operation": operation,
        "collection": collection,
        "duration_ms": round(duration * 1000, 2),
    }

    if document_count is not None:
        log_data["document_count"] = document_count

    if error:
        log_data["error"] = error
        logger.error("Database operation failed", extra=log_data)
    else:
        logger.info("Database operation completed", extra=log_data)


# =============================================================================
# 전통적인 로깅 시스템 (기존 logging_config.py 통합)
# =============================================================================


def setup_traditional_logging():
    """전통적인 파일/콘솔 로깅 설정"""

    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 컬러 로그 포맷 (colorlog 사용)
    if HAS_COLORLOG:
        color_format = (
            "%(log_color)s%(asctime)s%(reset)s | "
            "%(log_color)s%(levelname)-8s%(reset)s | "
            "%(cyan)s%(name)-30s%(reset)s | "
            "%(message_log_color)s%(message)s%(reset)s"
        )
        date_format = "%H:%M:%S"

        console_formatter = colorlog.ColoredFormatter(
            color_format,
            datefmt=date_format,
            log_colors={
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={
                "message": {
                    "DEBUG": "white",
                    "INFO": "white",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                }
            },
        )
    else:
        # colorlog 없을 때 기본 포맷
        log_format = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
        date_format = "%H:%M:%S"
        console_formatter = logging.Formatter(log_format, datefmt=date_format)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 파일 핸들러 (일반 로그) - 컬러 없이
    file_format = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    file_date_format = "%Y-%m-%d %H:%M:%S"

    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(file_format, datefmt=file_date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # 에러 로그 파일 핸들러
    error_handler = logging.FileHandler(log_dir / "error.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(file_format, datefmt=file_date_format)
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)

    # 외부 라이브러리 로그 레벨 조정
    _configure_external_loggers()


def _configure_external_loggers():
    """외부 라이브러리 로거 설정"""
    external_loggers = {
        "uvicorn.access": logging.WARNING,
        "uvicorn.error": logging.INFO,
        "httpx": logging.WARNING,
        "watchfiles": logging.WARNING,
        "watchfiles.main": logging.WARNING,
        "pymongo": logging.WARNING,
        "pymongo.serverSelection": logging.WARNING,
        "pymongo.connection": logging.WARNING,
        "pymongo.command": logging.WARNING,
        "pymongo.topology": logging.WARNING,
        # Email 및 User 관리 로거 (서비스별)
        "app.utils.email": logging.INFO,
        "app.services.user_manager": logging.INFO,
    }

    for logger_name, level in external_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


# =============================================================================
# 통합 로깅 설정 (권장)
# =============================================================================


def setup_logging(
    service_name: str = "unknown-service",
    log_level: str = "INFO",
    environment: str = "development",
    enable_structured: bool = True,
    enable_traditional: bool = True,
    enable_json: bool = False,
):
    """
    통합 로깅 시스템 설정 (구조화된 + 전통적인 로깅)

    Args:
        service_name: 서비스명
        log_level: 로그 레벨
        environment: 환경 (development, production)
        enable_structured: 구조화된 로깅 활성화
        enable_traditional: 전통적인 로깅 활성화
        enable_json: JSON 출력 활성화 (production 권장)
    """
    # 환경별 기본 설정
    if environment == "production":
        enable_json = True
        log_level = "INFO"
    elif environment == "development":
        enable_json = False
        log_level = "DEBUG"

    # 전통적인 로깅 설정 (파일, 콘솔)
    if enable_traditional:
        setup_traditional_logging()

    # 구조화된 로깅 설정
    if enable_structured:
        configure_structured_logging(
            service_name=service_name,
            log_level=log_level,
            enable_json=enable_json,
        )

    # 설정 완료 로그
    logger = get_structured_logger(__name__)
    logger.info(f"✅ Integrated logging configured for {service_name}")
    logger.info(f"Environment: {environment}, Level: {log_level}, JSON: {enable_json}")


# =============================================================================
# 레거시 호환성 함수
# =============================================================================


def setup_logging_legacy():
    """기존 setup_logging 함수 (호환성 유지)"""
    setup_traditional_logging()


# 기본 설정 함수 (서비스명 없이 호출하는 경우)
def configure_logging_for_service(service_name: str):
    """서비스별 로깅 설정 (간단한 인터페이스)"""
    setup_logging(service_name=service_name)
