from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Book as BookModel

from .schemas import Book, BookCreateModel, BookDetailModel, BookUpdateModel


class BookRepository(ABC):
    @abstractmethod
    async def get_all(self) -> list[Book]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user(self, user_uid: str) -> list[Book]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, book_uid: str) -> BookDetailModel | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, book_data: BookCreateModel, user_uid: str) -> Book:
        raise NotImplementedError

    @abstractmethod
    async def update(self, book_uid: str, update_data: BookUpdateModel) -> Book | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, book_uid: str) -> bool:
        raise NotImplementedError


class SqlModelBookRepository(BookRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[Book]:
        statement = select(BookModel).order_by(desc(BookModel.created_at))
        result = await self.session.execute(statement)
        books = result.scalars().all()
        return [Book.model_validate(book) for book in books]

    async def get_by_user(self, user_uid: str) -> list[Book]:
        statement = (
            select(BookModel)
            .where(BookModel.user_uid == user_uid)
            .order_by(desc(BookModel.created_at))
        )
        result = await self.session.execute(statement)
        books = result.scalars().all()
        return [Book.model_validate(book) for book in books]

    async def get_by_id(self, book_uid: str) -> BookDetailModel | None:
        statement = select(BookModel).where(BookModel.uid == book_uid)
        result = await self.session.execute(statement)
        book = result.scalars().first()
        if book is None:
            return None
        return BookDetailModel.model_validate(book)

    async def create(self, book_data: BookCreateModel, user_uid: str) -> Book:
        book_data_dict = book_data.model_dump()
        new_book = BookModel(**book_data_dict)
        new_book.published_date = datetime.strptime(
            book_data_dict["published_date"], "%Y-%m-%d"
        ).date()
        new_book.user_uid = user_uid

        self.session.add(new_book)
        await self.session.commit()
        await self.session.refresh(new_book)

        return Book.model_validate(new_book)

    async def update(self, book_uid: str, update_data: BookUpdateModel) -> Book | None:
        statement = select(BookModel).where(BookModel.uid == book_uid)
        result = await self.session.execute(statement)
        book_to_update = result.scalars().first()

        if book_to_update is None:
            return None

        for key, value in update_data.model_dump().items():
            setattr(book_to_update, key, value)

        await self.session.commit()
        await self.session.refresh(book_to_update)

        return Book.model_validate(book_to_update)

    async def delete(self, book_uid: str) -> bool:
        statement = select(BookModel).where(BookModel.uid == book_uid)
        result = await self.session.execute(statement)
        book_to_delete = result.scalars().first()

        if book_to_delete is None:
            return False

        await self.session.delete(book_to_delete)
        await self.session.commit()
        return True