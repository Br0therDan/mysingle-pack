from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class BaseResponseSchema(BaseModel):
    """Base response schema with MongoDB ObjectId support."""

    id: PydanticObjectId = Field(..., alias="_id")

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
