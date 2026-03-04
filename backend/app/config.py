from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SecurePDFMerger"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str = ""

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    MAX_FILES_PER_MERGE: int = 20
    UPLOAD_DIR: str = "./temp_uploads"
    MERGED_DIR: str = "./temp_merged"
    FILE_RETENTION_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    RATE_LIMIT_MERGE_PER_HOUR: int = 10

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    FRONTEND_URL: str = "http://localhost:5173"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Watermark
    DEFAULT_WATERMARK_TEXT: str = "SecurePDFMerger"
    WATERMARK_FONT_SIZE: int = 36
    WATERMARK_OPACITY: float = 0.1

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @field_validator("UPLOAD_DIR", "MERGED_DIR")
    @classmethod
    def create_directories(cls, v: str) -> str:
        os.makedirs(v, exist_ok=True)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
