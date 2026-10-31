from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SubscriptIQ — The Royal Ledger"
    DATABASE_URL: str = "sqlite:///./subscriptiq.db"
    SECRET_KEY: str = "subscriptiq-royal-ledger-secret-key-super-secure-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
