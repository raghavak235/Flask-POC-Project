# src/books/routes.py
from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, get_current_user
from src.books.repository import SqlModelBookRepository
from src.books.service import BookService
from src.db.main import get_session
from src.db.models import User

from .schemas import Book, BookCreateModel, BookDetailModel, BookUpdateModel
from src.errors import BookNotFound

# Router-level dependency: all routes require authenticated user with role
book_router = APIRouter(
    dependencies=[Depends(RoleChecker(["admin", "user"]))]
)


def get_book_service(
    session: AsyncSession = Depends(get_session),
) -> BookService:
    return BookService(SqlModelBookRepository(session))


async def get_book_or_404(
    book_uid: str, book_service: BookService = Depends(get_book_service)
) -> BookDetailModel:
    """Reusable dependency: fetch a book by UID or raise BookNotFound."""
    book = await book_service.get_book(book_uid)
    if book is None:
        raise BookNotFound()
    return book


@book_router.get("/", response_model=List[Book])
async def get_all_books(book_service: BookService = Depends(get_book_service)):
    books = await book_service.get_all_books()
    return books


@book_router.get("/user/{user_uid}", response_model=List[Book])
async def get_user_book_submissions(
    user_uid: str,
    book_service: BookService = Depends(get_book_service),
):
    books = await book_service.get_user_books(user_uid)
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_a_book(
    book_data: BookCreateModel,
    book_service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    new_book = await book_service.create_book(book_data, str(current_user.uid))
    return new_book


@book_router.get("/{book_uid}", response_model=BookDetailModel)
async def get_book(book: BookDetailModel = Depends(get_book_or_404)) -> dict:
    return book


@book_router.patch("/{book_uid}", response_model=Book)
async def update_book(
    book_update_data: BookUpdateModel,
    book: BookDetailModel = Depends(get_book_or_404),
    book_service: BookService = Depends(get_book_service),
) -> dict:
    updated_book = await book_service.update_book(str(book.uid), book_update_data)
    return updated_book


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book: BookDetailModel = Depends(get_book_or_404),
    book_service: BookService = Depends(get_book_service),
):
    await book_service.delete_book(str(book.uid))
    return {}