from .repository import BookRepository
from .schemas import Book, BookCreateModel, BookDetailModel, BookUpdateModel


class BookService:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    async def get_all_books(self) -> list[Book]:
        return await self.repository.get_all()

    async def get_user_books(self, user_uid: str) -> list[Book]:
        return await self.repository.get_by_user(user_uid)

    async def get_book(self, book_uid: str) -> BookDetailModel | None:
        return await self.repository.get_by_id(book_uid)

    async def create_book(self, book_data: BookCreateModel, user_uid: str) -> Book:
        return await self.repository.create(book_data, user_uid)

    async def update_book(self, book_uid: str, update_data: BookUpdateModel) -> Book | None:
        return await self.repository.update(book_uid, update_data)

    async def delete_book(self, book_uid: str) -> bool:
        return await self.repository.delete(book_uid)
