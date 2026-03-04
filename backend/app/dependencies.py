"""
Shared dependencies for dependency injection across the application.
"""
from typing import Optional
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.pdf_service import PDFService
from app.services.history_service import HistoryService
from app.services.cleanup_service import CleanupService


# Singleton PDF service
_pdf_service: Optional[PDFService] = None


def get_pdf_service() -> PDFService:
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFService()
    return _pdf_service


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_history_service(db: AsyncSession = Depends(get_db)) -> HistoryService:
    return HistoryService(db)


def get_cleanup_service() -> CleanupService:
    return CleanupService()


class PaginationParams:
    """Common pagination parameters."""
    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number"),
        page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


async def get_authenticated_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Alias for get_current_user with additional checks if needed."""
    return current_user