"""
Common/shared schemas used across the application.
"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class MessageResponse(BaseModel):
    """Standard message response."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = None

    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)


class PaginatedResponse(BaseModel):
    """Base paginated response."""
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app: str
    version: str
    environment: Optional[str] = None