from pydantic import BaseModel, Field

class UserSearchBookModel(BaseModel):
    query: str = Field(min_length=3, max_length=500, 
                       description="If you want to search for a book, you can provide the book title or author. "
                                   "Agent will also provide search results for the book title or author along with a brief description.")
    