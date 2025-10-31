from enum import Enum


class SeverityLevel(str, Enum):
    """심각도 수준"""

    NORMAL = "normal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Celery 태스크 상태"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


class LogLevel(str, Enum):
    """로그 레벨"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
