import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from src.reviews.schemas import ReviewModel
# from src.tags.schemas import TagModel


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    description: Optional[str] = None
    created_at: datetime
    update_at: datetime


class BookDetailModel(Book):
    reviews: List[ReviewModel]
    # tags:List[TagModel]


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    description: Optional[str] = None


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    description: Optional[str] = None
