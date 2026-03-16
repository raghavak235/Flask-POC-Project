import uuid
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src import app
from src.auth.dependencies import get_current_user
from src.books.repository import BookRepository
from src.books.service import BookService
from src.db.main import get_session
from src.books.schemas import Book


app.dependency_overrides[get_session] = lambda: MagicMock()
app.dependency_overrides[get_current_user] = lambda: MagicMock(
    uid=uuid.uuid4(), role="admin", email="test@example.com"
)



# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def book_service():
    repository = MagicMock(spec=BookRepository)
    return BookService(repository)


@pytest.fixture
def mock_book_repository(book_service):
    return book_service.repository


@pytest.fixture
def fake_session():
    """Sync mock session used by route-level tests via dependency override."""
    session = MagicMock()
    return session


@pytest.fixture
def fake_book_service():
    return MagicMock()


@pytest.fixture
def fake_user_service():
    return MagicMock()


@pytest.fixture
def test_book():
    return Book(
        uid=uuid.uuid4(),
        title="sample title",
        author="sample author",
        publisher="sample publisher",
        page_count=200,
        language="English",
        published_date=date.today(),
        created_at=datetime.now(),
        update_at=datetime.now(),
    )