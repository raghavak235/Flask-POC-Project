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

    # --- Application ---
    # Public domain of the app, used in email links and CORS (e.g. https://myapp.com)
    DOMAIN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # Silently discard any env vars not declared above
    )


# Instantiate once at startup — a missing or invalid .env will raise immediately
Config = Settings()