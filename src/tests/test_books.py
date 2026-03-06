import uuid
from datetime import date, datetime
from unittest.mock import AsyncMock

import pytest

from src.books.schemas import Book, BookCreateModel, BookDetailModel, BookUpdateModel

# NOTE: make_book, book_service, mock_session fixtures all come from conftest.py


from unittest.mock import MagicMock

def make_book(**kwargs):
    book = MagicMock()
    book.uid = kwargs.get("uid", uuid.uuid4())
    book.title = kwargs.get("title", "Test Book")
    book.author = kwargs.get("author", "Test Author")
    book.publisher = kwargs.get("publisher", "Test Publisher")
    book.published_date = kwargs.get("published_date", date(2024, 1, 1))
    book.page_count = kwargs.get("page_count", 300)
    book.language = kwargs.get("language", "English")
    book.user_uid = kwargs.get("user_uid", str(uuid.uuid4()))
    book.created_at = kwargs.get("created_at", datetime.now())
    book.update_at = kwargs.get("update_at", datetime.now())
    return book

# ─────────────────────────────────────────────
# get_all_books
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_all_books_returns_list(book_service, mock_session):
    session, result = mock_session
    books = [make_book(title="Book A"), make_book(title="Book B")]
    result.scalars.return_value.all.return_value = books

    response = await book_service.get_all_books(session)

    assert response == books
    assert len(response) == 2
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_books_returns_empty_list(book_service, mock_session):
    session, result = mock_session
    result.scalars.return_value.all.return_value = []

    response = await book_service.get_all_books(session)

    assert response == []


# ─────────────────────────────────────────────
# get_user_books
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_user_books_returns_books_for_user(book_service, mock_session):
    session, result = mock_session
    user_uid = str(uuid.uuid4())
    books = [make_book(user_uid=user_uid), make_book(user_uid=user_uid)]
    result.scalars.return_value.all.return_value = books

    response = await book_service.get_user_books(user_uid, session)

    assert len(response) == 2
    assert all(b.user_uid == user_uid for b in response)


@pytest.mark.asyncio
async def test_get_user_books_returns_empty_for_unknown_user(book_service, mock_session):
    session, result = mock_session
    result.scalars.return_value.all.return_value = []

    response = await book_service.get_user_books(str(uuid.uuid4()), session)

    assert response == []


# ─────────────────────────────────────────────
# get_book
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_book_returns_book_when_found(book_service, mock_session):
    session, result = mock_session
    book = make_book()
    result.scalars.return_value.first.return_value = book

    response = await book_service.get_book(str(book.uid), session)

    assert response == book


@pytest.mark.asyncio
async def test_get_book_returns_none_when_not_found(book_service, mock_session):
    session, result = mock_session
    result.scalars.return_value.first.return_value = None

    response = await book_service.get_book(str(uuid.uuid4()), session)

    assert response is None


# ─────────────────────────────────────────────
# create_book
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_book_success(book_service):
    session = AsyncMock()
    user_uid = str(uuid.uuid4())

    book_data = BookCreateModel(
        title="New Book",
        author="Author",
        publisher="Publisher",
        published_date="2024-06-15",
        page_count=250,
        language="English",
    )

    result = await book_service.create_book(book_data, user_uid, session)

    session.add.assert_called_once()
    session.commit.assert_called_once()
    assert result.title == "New Book"
    assert result.author == "Author"
    assert result.user_uid == user_uid
    assert result.published_date == datetime(2024, 6, 15)


@pytest.mark.asyncio
async def test_create_book_sets_published_date_correctly(book_service):
    session = AsyncMock()
    book_data = BookCreateModel(
        title="Date Test",
        author="Author",
        publisher="Publisher",
        published_date="2023-12-31",
        page_count=100,
        language="English",
    )

    result = await book_service.create_book(book_data, str(uuid.uuid4()), session)

    assert result.published_date == datetime(2023, 12, 31)


# ─────────────────────────────────────────────
# update_book
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_book_success(book_service, mock_session):
    session, result = mock_session
    book = make_book(title="Old Title", page_count=100)
    result.scalars.return_value.first.return_value = book

    update_data = BookUpdateModel(
        title="Updated Title",
        author="Updated Author",
        publisher="Updated Publisher",
        page_count=400,
        language="French",
    )

    response = await book_service.update_book(str(book.uid), update_data, session)

    session.commit.assert_called_once()
    assert response.title == "Updated Title"
    assert response.page_count == 400
    assert response.language == "French"


@pytest.mark.asyncio
async def test_update_book_returns_none_when_not_found(book_service, mock_session):
    session, result = mock_session
    result.scalars.return_value.first.return_value = None

    update_data = BookUpdateModel(
        title="Title",
        author="Author",
        publisher="Publisher",
        page_count=100,
        language="English",
    )

    response = await book_service.update_book(str(uuid.uuid4()), update_data, session)

    assert response is None
    session.commit.assert_not_called()


# ─────────────────────────────────────────────
# delete_book
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_book_success(book_service, mock_session):
    session, result = mock_session
    book = make_book()
    result.scalars.return_value.first.return_value = book

    response = await book_service.delete_book(str(book.uid), session)

    session.delete.assert_called_once_with(book)
    session.commit.assert_called_once()
    assert response == {}


@pytest.mark.asyncio
async def test_delete_book_returns_none_when_not_found(book_service, mock_session):
    session, result = mock_session
    result.scalars.return_value.first.return_value = None

    response = await book_service.delete_book(str(uuid.uuid4()), session)

    assert response is None
    session.delete.assert_not_called()
    session.commit.assert_not_called()


# ─────────────────────────────────────────────
# Schema validation tests
# ─────────────────────────────────────────────

def test_book_schema_valid():
    book = Book(
        uid=uuid.uuid4(),
        title="Test",
        author="Author",
        publisher="Publisher",
        published_date=date(2024, 1, 1),
        page_count=100,
        language="English",
        created_at=datetime.now(),
        update_at=datetime.now(),
    )
    assert book.title == "Test"
    assert book.page_count == 100


def test_book_create_model_valid():
    data = BookCreateModel(
        title="New Book",
        author="Author",
        publisher="Publisher",
        published_date="2024-01-01",
        page_count=200,
        language="English",
    )
    assert data.title == "New Book"
    assert data.published_date == "2024-01-01"


def test_book_update_model_valid():
    data = BookUpdateModel(
        title="Updated",
        author="Author",
        publisher="Publisher",
        page_count=350,
        language="Spanish",
    )
    assert data.language == "Spanish"


def test_book_create_model_missing_field():
    with pytest.raises(Exception):
        BookCreateModel(
            title="Missing fields",
            # author is missing
            publisher="Publisher",
            published_date="2024-01-01",
            page_count=100,
            language="English",
        )