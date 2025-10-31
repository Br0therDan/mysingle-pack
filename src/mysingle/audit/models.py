from datetime import UTC, datetime

from beanie import PydanticObjectId
from pydantic import Field

from ..base.models import BaseTimeDoc


class AuditLog(BaseTimeDoc):
    """HTTP 요청/응답 감사 로그 문서.

    Week 14 잔여 과제: 필드 확장(요청 페이로드 크기, 처리 소요시간, 응답 크기).
    기타 기본 컨텍스트 필드 포함.
    """

    # Who/Context
    user_id: PydanticObjectId | None = None
    service: str
    request_id: str | None = None
    trace_id: str | None = None

    # Request
    method: str
    path: str
    ip: str | None = None
    user_agent: str | None = None
    req_bytes: int = 0

    # Response
    status_code: int
    resp_bytes: int = 0

    # Timing
    latency_ms: int = 0
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


__all__ = ["AuditLog"]
