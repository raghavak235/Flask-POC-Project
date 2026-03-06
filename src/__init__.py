from fastapi import FastAPI
from src.auth.routes import auth_router
from src.books.routes import book_router
from src.reviews.routes import review_router
from .errors import register_all_errors
from .middleware import register_middleware


version = "v1"
description = """
### Book Review API 📚
A specialized REST service for managing a digital library and user feedback.

#### Key Features:
* **Books**: Full lifecycle management (CRUD).
* **Reviews**: Post and retrieve community reviews.
"""

version_prefix =f"/api/{version}"

app = FastAPI(
    title="Book Review API",
    description=description,
    version=version,
    
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

register_all_errors(app)

register_middleware(app)


app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"{version_prefix}/reviews", tags=["reviews"])