from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    APP_NAME: str = "SecurePDFMerger"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production-1234567890"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    DATABASE_URL_SYNC: str = "sqlite:///./app.db"

    JWT_SECRET_KEY: str = "dev-jwt-secret-change-in-production-1234567890"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MAX_FILE_SIZE_MB: int = 50
    MAX_FILES_PER_MERGE: int = 20
    UPLOAD_DIR: str = "./temp_uploads"
    MERGED_DIR: str = "./temp_merged"
    FILE_RETENTION_MINUTES: int = 30

    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_MERGE_PER_HOUR: int = 30

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    FRONTEND_URL: str = "http://localhost:5173"

    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "./logs/app.log"

    REDIS_URL: str = "memory://"

    DEFAULT_WATERMARK_TEXT: str = "SecurePDFMerger"
    WATERMARK_FONT_SIZE: int = 36
    WATERMARK_OPACITY: float = 0.1

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


# Create required directories
for d in ["./temp_uploads", "./temp_merged", "./logs"]:
    os.makedirs(d, exist_ok=True)

settings = Settings()