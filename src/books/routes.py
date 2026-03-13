# src/books/routes.py
from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, get_current_user
from src.books.service import BookService
from src.db.main import get_session
from src.db.models import Book as BookModel, User

from .schemas import Book, BookCreateModel, BookDetailModel, BookUpdateModel
from src.errors import BookNotFound

book_service = BookService()

# Router-level dependency: all routes require authenticated user with role
book_router = APIRouter(
    dependencies=[Depends(RoleChecker(["admin", "user"]))]
)


async def get_book_or_404(
    book_uid: str, session: AsyncSession = Depends(get_session)
) -> BookModel:
    """Reusable dependency: fetch a book by UID or raise BookNotFound."""
    book = await book_service.get_book(book_uid, session)
    if book is None:
        raise BookNotFound()
    return book


@book_router.get("/", response_model=List[Book])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session)
    return books


@book_router.get("/user/{user_uid}", response_model=List[Book])
async def get_user_book_submissions(
    user_uid: str, session: AsyncSession = Depends(get_session),
):
    books = await book_service.get_user_books(user_uid, session)
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    new_book = await book_service.create_book(book_data, str(current_user.uid), session)
    return new_book


@book_router.get("/{book_uid}", response_model=BookDetailModel)
async def get_book(book: BookModel = Depends(get_book_or_404)) -> dict:
    return book


@book_router.patch("/{book_uid}", response_model=Book)
async def update_book(
    book_update_data: BookUpdateModel,
    book: BookModel = Depends(get_book_or_404),
    session: AsyncSession = Depends(get_session),
) -> dict:
    updated_book = await book_service.update_book(str(book.uid), book_update_data, session)
    return updated_book


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book: BookModel = Depends(get_book_or_404),
    session: AsyncSession = Depends(get_session),
):
    await book_service.delete_book(str(book.uid), session)
    return {}