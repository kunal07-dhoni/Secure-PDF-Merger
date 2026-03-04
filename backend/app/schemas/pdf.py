from pydantic import BaseModel, field_validator
from typing import Optional, List


class PageRange(BaseModel):
    file_index: int
    start_page: Optional[int] = None
    end_page: Optional[int] = None

    @field_validator("start_page", "end_page")
    @classmethod
    def validate_page(cls, v):
        if v is not None and v < 1:
            raise ValueError("Page numbers must be >= 1")
        return v


class MergeRequest(BaseModel):
    file_order: List[int]  # Indices representing desired order
    output_filename: Optional[str] = "merged_output.pdf"
    page_ranges: Optional[List[PageRange]] = None
    watermark_text: Optional[str] = None
    compress: bool = False

    @field_validator("output_filename")
    @classmethod
    def validate_filename(cls, v):
        if v:
            # Sanitize filename
            v = v.strip()
            if not v.endswith(".pdf"):
                v += ".pdf"
            # Remove path traversal characters
            v = v.replace("/", "").replace("\\", "").replace("..", "")
            if len(v) > 200:
                v = v[:196] + ".pdf"
        return v


class FileInfo(BaseModel):
    index: int
    filename: str
    size_bytes: int
    page_count: int
    is_valid: bool
    error: Optional[str] = None


class UploadResponse(BaseModel):
    session_id: str
    files: List[FileInfo]
    total_files: int
    total_size_bytes: int


class MergeResponse(BaseModel):
    success: bool
    download_token: str
    filename: str
    total_pages: int
    file_size_bytes: int
    message: str