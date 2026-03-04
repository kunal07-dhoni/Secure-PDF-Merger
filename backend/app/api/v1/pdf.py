import json
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limiter import limiter
from app.models.user import User
from app.services.pdf_service import PDFService
from app.services.history_service import HistoryService
from app.schemas.pdf import (
    UploadResponse, MergeResponse, PageRange, FileInfo,
)
from app.config import settings

router = APIRouter()
pdf_service = PDFService()


@router.post("/upload", response_model=UploadResponse)
@limiter.limit("20/minute")
async def upload_pdfs(
    request: Request,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    session_id, file_infos = await pdf_service.process_uploads(
        files, current_user.id
    )

    total_size = sum(fi.size_bytes for fi in file_infos if fi.is_valid)

    return UploadResponse(
        session_id=session_id,
        files=file_infos,
        total_files=len([fi for fi in file_infos if fi.is_valid]),
        total_size_bytes=total_size,
    )


@router.post("/merge", response_model=MergeResponse)
@limiter.limit(f"{settings.RATE_LIMIT_MERGE_PER_HOUR}/hour")
async def merge_pdfs(
    request: Request,
    session_id: str = Form(...),
    file_order: str = Form(...),  # JSON array of indices
    output_filename: str = Form(default="merged_output.pdf"),
    page_ranges: Optional[str] = Form(default=None),  # JSON array
    watermark_text: Optional[str] = Form(default=None),
    compress: bool = Form(default=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Parse file order
    order = json.loads(file_order)

    # Parse page ranges
    ranges = None
    if page_ranges:
        ranges_data = json.loads(page_ranges)
        ranges = [PageRange(**r) for r in ranges_data]

    # Perform merge
    output_path, total_pages, output_size = await pdf_service.merge_pdfs(
        session_id=session_id,
        file_order=order,
        output_filename=output_filename,
        page_ranges=ranges,
        watermark_text=watermark_text,
        compress=compress,
        user_id=current_user.id,
    )

    # Create history record
    history_service = HistoryService(db)
    record = await history_service.create_record(
        user=current_user,
        output_filename=output_filename,
        original_filenames=[],
        file_count=len(order),
        total_pages=total_pages,
        output_size_bytes=output_size,
        output_path=output_path,
        page_ranges=page_ranges,
        watermark_text=watermark_text,
        compressed=compress,
    )

    # Clean up upload session
    pdf_service.cleanup_session(session_id)

    return MergeResponse(
        success=True,
        download_token=record.download_token,
        filename=output_filename,
        total_pages=total_pages,
        file_size_bytes=output_size,
        message=f"Successfully merged {len(order)} files into {total_pages} pages",
    )


@router.get("/preview/{session_id}/{file_index}")
async def preview_file(
    session_id: str,
    file_index: int,
    current_user: User = Depends(get_current_user),
):
    # Ensure user owns this session
    if not session_id.startswith(current_user.id):
        from app.exceptions import AuthorizationError
        raise AuthorizationError("Access denied")

    info = pdf_service.get_file_preview_info(session_id, file_index)
    return info


@router.delete("/session/{session_id}")
async def cleanup_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    if not session_id.startswith(current_user.id):
        from app.exceptions import AuthorizationError
        raise AuthorizationError("Access denied")

    pdf_service.cleanup_session(session_id)
    return {"message": "Session cleaned up"}