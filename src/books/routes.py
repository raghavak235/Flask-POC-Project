# src/books/routes.py
from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, get_current_user
from src.books.service import BookService
from src.db.main import get_session
from src.db.models import User

from .schemas import Book, BookCreateModel, BookDetailModel, BookUpdateModel
from src.errors import BookNotFound

book_router = APIRouter()
book_service = BookService()
role_checker = Depends(RoleChecker(["admin", "user"]))


@book_router.get("/", response_model=List[Book], dependencies=[role_checker])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session)
    return books


@book_router.get("/user/{user_uid}", response_model=List[Book], dependencies=[role_checker])
async def get_user_book_submissions(
    user_uid: str, session: AsyncSession = Depends(get_session),
):
    books = await book_service.get_user_books(user_uid, session)
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book, dependencies=[role_checker])
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    new_book = await book_service.create_book(book_data, str(current_user.uid), session)
    return new_book


@book_router.get("/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker])
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session)) -> dict:
    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    else:
        raise BookNotFound()


@book_router.patch("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def update_book(
    book_uid: str, book_update_data: BookUpdateModel, session: AsyncSession = Depends(get_session),
) -> dict:
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    if updated_book is None:
        raise BookNotFound()
    else:
        return updated_book


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    book_to_delete = await book_service.delete_book(book_uid, session)
    if book_to_delete is None:
        raise BookNotFound()
    else:
        return {}