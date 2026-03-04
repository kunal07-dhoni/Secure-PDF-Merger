from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class HistoryItem(BaseModel):
    id: str
    output_filename: str
    original_filenames: str
    file_count: int
    total_pages: int
    output_size_bytes: int
    watermark_applied: Optional[str]
    compressed: int
    download_token: Optional[str]
    download_expires_at: Optional[datetime]
    download_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class HistoryDeleteResponse(BaseModel):
    success: bool
    message: str