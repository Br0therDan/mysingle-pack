from datetime import UTC, datetime
from decimal import Decimal
from typing import Generic, Optional, TypeVar

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class BaseResponseSchema(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id")

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    """Timestamp mixin for created_at and updated_at."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(
        default=100, ge=1, le=1000, description="Number of items to return"
    )


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    skip: int
    limit: int
    has_more: bool

    @classmethod
    def create(
        cls, items: list[T], total: int, skip: int, limit: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total,
        )


class BaseResponse(BaseModel):
    """API 응답 기본 스키마"""

    success: bool = Field(True, description="요청 성공 여부")
    message: Optional[str] = Field(None, description="응답 메시지")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="응답 시간"
    )


class DataQualityInfo(BaseModel):
    """데이터 품질 정보"""

    quality_score: Decimal = Field(..., description="품질 점수 (0-100)")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")
    data_source: str = Field(..., description="데이터 출처")
    confidence_level: Optional[str] = Field(None, description="신뢰도 수준")


class CacheInfo(BaseModel):
    """캐시 정보"""

    cached: bool = Field(..., description="캐시된 데이터 여부")
    cache_hit: bool = Field(..., description="캐시 히트 여부")
    cache_timestamp: Optional[datetime] = Field(None, description="캐시 생성 시간")
    cache_ttl: Optional[int] = Field(None, description="캐시 TTL (초)")


class MetadataInfo(BaseModel):
    """메타데이터 정보"""

    data_quality: DataQualityInfo = Field(..., description="데이터 품질 정보")
    cache_info: CacheInfo = Field(..., description="캐시 정보")
    processing_time_ms: Optional[float] = Field(None, description="처리 시간 (밀리초)")


class DataResponse(BaseResponse, Generic[T]):
    """데이터 응답 스키마 (메타데이터 포함)"""

    data: T = Field(..., description="데이터")
    metadata: MetadataInfo = Field(..., description="메타데이터")
