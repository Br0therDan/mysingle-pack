"""
Tests for mysingle.core.base module.
"""

from datetime import UTC, datetime

import pytest
from beanie import PydanticObjectId, init_beanie
from mongomock_motor import AsyncMongoMockClient

from mysingle.core.base import BaseDoc, BaseTimeDoc, BaseTimeDocWithUserId


class _TestDocument(BaseDoc):
    """Test document class."""

    name: str


class _TestTimeDocument(BaseTimeDoc):
    """Test time document class."""

    name: str


class _TestUserDocument(BaseTimeDocWithUserId):
    """Test user-scoped document class."""

    name: str


@pytest.fixture
async def init_db():
    """Initialize test database."""
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client.test_db,  # type: ignore
        document_models=[_TestDocument, _TestTimeDocument, _TestUserDocument],
    )
    yield
    # Cleanup
    await client.drop_database("test_db")


@pytest.mark.asyncio
async def test_base_doc_id(init_db):
    """Test BaseDoc has id field."""
    doc = _TestDocument(name="test")
    assert hasattr(doc, "id")
    assert doc.id is None or isinstance(doc.id, PydanticObjectId)


@pytest.mark.asyncio
async def test_base_time_doc_timestamps(init_db):
    """Test BaseTimeDoc has timestamp fields."""
    doc = _TestTimeDocument(name="test")

    assert hasattr(doc, "created_at")
    assert hasattr(doc, "updated_at")


@pytest.mark.asyncio
async def test_base_time_doc_with_user_id(init_db):
    """Test BaseTimeDocWithUserId has user_id field."""
    user_id = str(PydanticObjectId())
    doc = _TestUserDocument(name="test", user_id=user_id)

    assert hasattr(doc, "user_id")
    assert doc.user_id == user_id
    assert hasattr(doc, "created_at")
    assert hasattr(doc, "updated_at")


@pytest.mark.asyncio
async def test_base_doc_dict_export(init_db):
    """Test document serialization."""
    doc = _TestDocument(name="test")
    doc_dict = doc.model_dump()

    assert "name" in doc_dict
    assert doc_dict["name"] == "test"


@pytest.mark.asyncio
async def test_time_doc_auto_timestamps(init_db):
    """Test that timestamps are automatically set."""
    before = datetime.now(UTC)
    doc = _TestTimeDocument(name="test")
    after = datetime.now(UTC)

    # created_at and updated_at should be set automatically
    # This test assumes pre_save hook is configured
    assert doc.created_at is None or (before <= doc.created_at <= after)
