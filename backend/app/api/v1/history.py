from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.history_service import HistoryService
from app.schemas.history import HistoryListResponse, HistoryItem, HistoryDeleteResponse

router = APIRouter()


@router.get("/", response_model=HistoryListResponse)
async def get_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryService(db)
    return await service.get_user_history(current_user.id, page, page_size)


@router.get("/{record_id}/download")
async def download_merged_file(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryService(db)
    file_path = await service.get_download_path(record_id, current_user.id)

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.split("/")[-1] if "/" in file_path else file_path,
    )


@router.delete("/{record_id}", response_model=HistoryDeleteResponse)
async def delete_history_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryService(db)
    await service.delete_record(record_id, current_user.id)
    return HistoryDeleteResponse(success=True, message="Record deleted successfully")


@router.post("/{record_id}/regenerate-download", response_model=HistoryItem)
async def regenerate_download_link(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryService(db)
    record = await service.regenerate_download(record_id, current_user.id)
    return HistoryItem.model_validate(record)