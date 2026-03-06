import uuid
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src import app
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker
from src.books.service import BookService
from src.db.main import get_session
from src.db.models import Book


# ─────────────────────────────────────────────
# Dependency Overrides
# ─────────────────────────────────────────────

access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(["admin"])

# Override FastAPI dependencies with mocks
app.dependency_overrides[get_session] = lambda: MagicMock()
app.dependency_overrides[access_token_bearer] = Mock()
app.dependency_overrides[refresh_token_bearer] = Mock()
app.dependency_overrides[role_checker] = Mock()



# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def book_service():
    return BookService()


@pytest.fixture
def mock_session():
    """Async session fixture used by service-level tests."""
    session = AsyncMock()
    result = MagicMock()
    session.execute = AsyncMock(return_value=result)
    return session, result


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
        user_uid=uuid.uuid4(),
        title="sample title",
        author="sample author",
        publisher="sample publisher",
        page_count=200,
        language="English",
        published_date=datetime.now(),
        created_at=datetime.now(),
        update_at=datetime.now(),
    )