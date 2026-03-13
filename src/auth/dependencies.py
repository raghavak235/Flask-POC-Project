from typing import Any, List

from fastapi import Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from .service import UserService
from .utils import read_session_cookie
from src.errors import InvalidToken, InsufficientPermission

user_service = UserService()

async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User:
    cookie_value = request.cookies.get("session")
    if not cookie_value:
        raise InvalidToken()

    session_data = read_session_cookie(cookie_value)
    if not session_data:
        raise InvalidToken()

    user = await user_service.get_user_by_email(session_data["email"], session)
    if not user:
        raise InvalidToken()

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()