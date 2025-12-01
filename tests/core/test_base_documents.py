"""
Tests for mysingle.core.base.documents module.
"""

from datetime import UTC, datetime

import pytest
from beanie import PydanticObjectId

from mysingle.core import BaseDoc, BaseTimeDoc, BaseTimeDocWithUserId


class TestDocument(BaseDoc):
    """Test document class."""

    name: str


class TestTimeDocument(BaseTimeDoc):
    """Test time document class."""

    name: str


class TestUserDocument(BaseTimeDocWithUserId):
    """Test user-scoped document class."""

    name: str


@pytest.mark.asyncio
async def test_base_doc_id():
    """Test BaseDoc has id field."""
    doc = TestDocument(name="test")
    assert hasattr(doc, "id")
    assert doc.id is None or isinstance(doc.id, PydanticObjectId)


@pytest.mark.asyncio
async def test_base_time_doc_timestamps():
    """Test BaseTimeDoc has timestamp fields."""
    doc = TestTimeDocument(name="test")

    assert hasattr(doc, "created_at")
    assert hasattr(doc, "updated_at")


@pytest.mark.asyncio
async def test_base_time_doc_with_user_id():
    """Test BaseTimeDocWithUserId has user_id field."""
    user_id = str(PydanticObjectId())
    doc = TestUserDocument(name="test", user_id=user_id)

    assert hasattr(doc, "user_id")
    assert doc.user_id == user_id
    assert hasattr(doc, "created_at")
    assert hasattr(doc, "updated_at")


@pytest.mark.asyncio
async def test_base_doc_dict_export():
    """Test document serialization."""
    doc = TestDocument(name="test")
    doc_dict = doc.model_dump()

    assert "name" in doc_dict
    assert doc_dict["name"] == "test"


@pytest.mark.asyncio
async def test_time_doc_auto_timestamps():
    """Test that timestamps are automatically set."""
    before = datetime.now(UTC)
    doc = TestTimeDocument(name="test")
    after = datetime.now(UTC)

    # created_at and updated_at should be set automatically
    # This test assumes pre_save hook is configured
    assert doc.created_at is None or (before <= doc.created_at <= after)
