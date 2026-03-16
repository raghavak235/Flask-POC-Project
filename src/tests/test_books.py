import uuid
from datetime import date, datetime

import pytest

from src.books.schemas import Book, BookCreateModel, BookUpdateModel

# NOTE: make_book, book_service, and mock_book_repository fixtures all come from conftest.py


def make_book(**kwargs):
    return Book(
        uid=kwargs.get("uid", uuid.uuid4()),
        title=kwargs.get("title", "Test Book"),
        author=kwargs.get("author", "Test Author"),
        publisher=kwargs.get("publisher", "Test Publisher"),
        published_date=kwargs.get("published_date", date(2024, 1, 1)),
        page_count=kwargs.get("page_count", 300),
        language=kwargs.get("language", "English"),
        created_at=kwargs.get("created_at", datetime.now()),
        update_at=kwargs.get("update_at", datetime.now()),
    )

# ─────────────────────────────────────────────
# get_all_books
# ─────────────────────────────────────────────

@pytest.mark.anyio
async def test_get_all_books_returns_list(book_service, mock_book_repository):
    books = [make_book(title="Book A"), make_book(title="Book B")]
    mock_book_repository.get_all.return_value = books

    response = await book_service.get_all_books()

    assert response == books
    assert len(response) == 2
    mock_book_repository.get_all.assert_awaited_once()


@pytest.mark.anyio
async def test_get_all_books_returns_empty_list(book_service, mock_book_repository):
    mock_book_repository.get_all.return_value = []

    response = await book_service.get_all_books()

    assert response == []


# ─────────────────────────────────────────────
# get_user_books
# ─────────────────────────────────────────────

@pytest.mark.anyio
async def test_get_user_books_returns_books_for_user(book_service, mock_book_repository):
    user_uid = "user-123"
    books = [make_book(title="Book A"), make_book(title="Book B")]
    mock_book_repository.get_by_user.return_value = books

    response = await book_service.get_user_books(user_uid)

    assert len(response) == 2
    mock_book_repository.get_by_user.assert_awaited_once_with(user_uid)


@pytest.mark.anyio
async def test_get_user_books_returns_empty_for_unknown_user(book_service, mock_book_repository):
    unknown_user_uid = str(uuid.uuid4())
    mock_book_repository.get_by_user.return_value = []

    response = await book_service.get_user_books(unknown_user_uid)

    assert response == []


# ─────────────────────────────────────────────
# get_book
# ─────────────────────────────────────────────

@pytest.mark.anyio
async def test_get_book_returns_book_when_found(book_service, mock_book_repository):
    book = make_book()
    mock_book_repository.get_by_id.return_value = book

    response = await book_service.get_book(str(book.uid))

    assert response == book


@pytest.mark.anyio
async def test_get_book_returns_none_when_not_found(book_service, mock_book_repository):
    mock_book_repository.get_by_id.return_value = None

    response = await book_service.get_book(str(uuid.uuid4()))

    assert response is None


# ─────────────────────────────────────────────
# create_book
# ─────────────────────────────────────────────

@pytest.mark.anyio
async def test_create_book_success(book_service, mock_book_repository):
    user_uid = str(uuid.uuid4())

    book_data = BookCreateModel(
        title="New Book",
        author="Author",
        publisher="Publisher",
        published_date="2024-06-15",
        page_count=250,
        language="English",
    )
    created_book = make_book(
        title="New Book",
        author="Author",
        publisher="Publisher",
        published_date=date(2024, 6, 15),
        page_count=250,
        language="English",
    )
    mock_book_repository.create.return_value = created_book

    result = await book_service.create_book(book_data, user_uid)

    assert result.title == "New Book"
    assert result.author == "Author"
    assert result.published_date == date(2024, 6, 15)
    mock_book_repository.create.assert_awaited_once_with(book_data, user_uid)


@pytest.mark.anyio
async def test_create_book_delegates_to_repository(book_service, mock_book_repository):
    book_data = BookCreateModel(
        title="Date Test",
        author="Author",
        publisher="Publisher",
        published_date="2023-12-31",
        page_count=100,
        language="English",
    )
    user_uid = str(uuid.uuid4())
    mock_book_repository.create.return_value = make_book(
        title="Date Test",
        author="Author",
        publisher="Publisher",
        published_date=date(2023, 12, 31),
        page_count=100,
        language="English",
    )

    result = await book_service.create_book(book_data, user_uid)

    assert result.published_date == date(2023, 12, 31)
    mock_book_repository.create.assert_awaited_once_with(book_data, user_uid)


# ─────────────────────────────────────────────
# update_book
# ─────────────────────────────────────────────

@pytest.mark.anyio
async def test_update_book_success(book_service, mock_book_repository):
    book = make_book(title="Updated Title", page_count=400, language="French")
    mock_book_repository.update.return_value = book

    update_data = BookUpdateModel(
        title="Updated Title",
        author="Updated Author",
        publisher="Updated Publisher",
        page_count=400,
        language="French",
    )

    response = await book_service.update_book(str(book.uid), update_data)

    assert response.title == "Updated Title"
    assert response.page_count == 400
    assert response.language == "French"
    mock_book_repository.update.assert_awaited_once_with(str(book.uid), update_data)


@pytest.mark.anyio
async def test_update_book_returns_none_when_not_found(book_service, mock_book_repository):
    mock_book_repository.update.return_value = None

    update_data = BookUpdateModel(
        title="Title",
        author="Author",
        publisher="Publisher",
        page_count=100,
        language="English",
    )
    missing_book_uid = str(uuid.uuid4())

    response = await book_service.update_book(missing_book_uid, update_data)

    assert response is None
    mock_book_repository.update.assert_awaited_once_with(missing_book_uid, update_data)


# ─────────────────────────────────────────────
# delete_book
# ─────────────────────────────────────────────

@pytest.mark.anyio
async def test_delete_book_success(book_service, mock_book_repository):
    book_uid = str(uuid.uuid4())
    mock_book_repository.delete.return_value = True

    response = await book_service.delete_book(book_uid)

    assert response is True
    mock_book_repository.delete.assert_awaited_once_with(book_uid)


@pytest.mark.anyio
async def test_delete_book_returns_false_when_not_found(book_service, mock_book_repository):
    book_uid = str(uuid.uuid4())
    mock_book_repository.delete.return_value = False

    response = await book_service.delete_book(book_uid)

    assert response is False
    mock_book_repository.delete.assert_awaited_once_with(book_uid)


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