# src/auth/routes.py
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session

from .dependencies import (
    RoleChecker,
    get_current_user,
)
from .schemas import (
    UserBooksModel,
    UserLoginModel,
)
from .service import UserService
from .utils import (
    verify_password,
    create_session_cookie,
    SESSION_EXPIRY,
)
from src.errors import InvalidCredentials

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel,
    session: AsyncSession = Depends(get_session),
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            # Sign user data into a cookie
            cookie_value = create_session_cookie(
                {
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )

            response = JSONResponse(
                content={
                    "message": "Login successful",
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )
            response.set_cookie(
                key="session",
                value=cookie_value,
                httponly=True,
                samesite="lax",
                max_age=SESSION_EXPIRY,
            )
            return response

    raise InvalidCredentials()


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user_route(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user


@auth_router.get("/logout")
async def logout():
    response = JSONResponse(
        content={"message": "Logged Out Successfully"},
        status_code=status.HTTP_200_OK,
    )
    response.delete_cookie(key="session")
    return response