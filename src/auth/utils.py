from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from src.config import Config

passwd_context = CryptContext(schemes=["bcrypt"])
session_serializer = URLSafeTimedSerializer(Config.JWT_SECRET, salt="session-cookie")
SESSION_EXPIRY = 3600

def generate_passwd_hash(password: str) -> str:
    return passwd_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)

def create_url_safe_token(data: dict):
    return session_serializer.dumps(data)

def decode_url_safe_token(token: str):
    try:
        return session_serializer.loads(token)
    except Exception:
        return None

def create_session_cookie(user_data: dict) -> str:
    return session_serializer.dumps(user_data)

def read_session_cookie(cookie_value: str) -> dict | None:
    try:
        return session_serializer.loads(cookie_value, max_age=SESSION_EXPIRY)
    except Exception:
        return None