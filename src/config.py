from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database ---
    # Full connection string for the primary database (e.g. postgresql+asyncpg://user:pass@host/db)
    DATABASE_URL: str

    # --- Authentication ---
    # Secret key used to sign and verify JWT tokens — keep this long, random, and private
    JWT_SECRET: str
    # Hashing algorithm for JWTs (e.g. HS256, RS256)
    JWT_ALGORITHM: str

    # --- Redis ---
    # Connection URL for Redis, used as Celery broker and result backend
    # Override in .env if Redis is on a different host/port/db (e.g. redis://myhost:6379/1)
    REDIS_URL: str

    # --- Email (FastMail / SMTP) ---
    # SMTP login credentials
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    # Sender address that appears in the "From" field
    MAIL_FROM: str
    # Human-readable sender name (e.g. "MyApp Notifications")
    MAIL_FROM_NAME: str
    # SMTP server hostname (e.g. smtp.gmail.com)
    MAIL_SERVER: str
    # SMTP port (587 for STARTTLS, 465 for SSL, 25 for plain)
    MAIL_PORT: int
    # Use STARTTLS to upgrade the connection to TLS after connecting (default: True)
    MAIL_STARTTLS: bool = True
    # Use implicit SSL/TLS from the start (mutually exclusive with STARTTLS; default: False)
    MAIL_SSL_TLS: bool = False
    # Whether to send SMTP login credentials (default: True)
    USE_CREDENTIALS: bool = True
    # Whether to validate the SMTP server's SSL certificate (default: True)
    VALIDATE_CERTS: bool = True

    # --- Application ---
    # Public domain of the app, used in email links and CORS (e.g. https://myapp.com)
    DOMAIN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # Silently discard any env vars not declared above
    )


# Instantiate once at startup — a missing or invalid .env will raise immediately
Config = Settings()

# --- Celery configuration ---
# Expose Redis settings in the format Celery expects when this module is used as its config
broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True  # Suppress deprecation warning in Celery 6+