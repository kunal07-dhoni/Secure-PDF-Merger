import os
import json
import math
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.models.merge_history import MergeHistory
from app.models.user import User
from app.schemas.history import HistoryItem, HistoryListResponse
from app.utils.security import create_download_token, verify_download_token
from app.config import settings
from app.exceptions import NotFoundError, AuthorizationError
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class HistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_record(
        self,
        user: User,
        output_filename: str,
        original_filenames: list,
        file_count: int,
        total_pages: int,
        output_size_bytes: int,
        output_path: str,
        page_ranges: Optional[str] = None,
        watermark_text: Optional[str] = None,
        compressed: bool = False,
    ) -> MergeHistory:
        download_token = create_download_token(output_path)
        expires_at = datetime.utcnow() + timedelta(minutes=settings.FILE_RETENTION_MINUTES)

        record = MergeHistory(
            user_id=user.id,
            output_filename=output_filename,
            original_filenames=json.dumps(original_filenames),
            file_count=file_count,
            total_pages=total_pages,
            output_size_bytes=output_size_bytes,
            page_ranges=page_ranges,
            watermark_applied=watermark_text,
            compressed=1 if compressed else 0,
            download_token=download_token,
            download_expires_at=expires_at,
            status="completed",
        )

        self.db.add(record)

        # Update user merge count
        user.merge_count += 1

        await self.db.flush()
        await self.db.refresh(record)

        # Store the file path mapping
        path_mapping_file = os.path.join(settings.MERGED_DIR, f"{record.id}.path")
        with open(path_mapping_file, "w") as f:
            f.write(output_path)

        logger.info("history_created", record_id=record.id, user_id=user.id)

        return record

    async def get_user_history(
        self, user_id: str, page: int = 1, page_size: int = 20
    ) -> HistoryListResponse:
        # Count total
        count_query = select(func.count(MergeHistory.id)).where(
            MergeHistory.user_id == user_id
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get items
        offset = (page - 1) * page_size
        query = (
            select(MergeHistory)
            .where(MergeHistory.user_id == user_id)
            .order_by(MergeHistory.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        items = result.scalars().all()

        # Check and update expired downloads
        now = datetime.utcnow()
        for item in items:
            if (
                item.status == "completed"
                and item.download_expires_at
                and item.download_expires_at < now
            ):
                item.status = "expired"
                item.download_token = None

        await self.db.flush()

        return HistoryListResponse(
            items=[HistoryItem.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        )

    async def get_download_path(self, record_id: str, user_id: str) -> str:
        result = await self.db.execute(
            select(MergeHistory).where(MergeHistory.id == record_id)
        )
        record = result.scalar_one_or_none()

        if not record:
            raise NotFoundError("Record not found")

        if record.user_id != user_id:
            raise AuthorizationError("Access denied")

        if record.status != "completed":
            raise NotFoundError("Download is no longer available")

        if record.download_expires_at and record.download_expires_at < datetime.utcnow():
            record.status = "expired"
            await self.db.flush()
            raise NotFoundError("Download link has expired")

        # Get file path
        path_mapping_file = os.path.join(settings.MERGED_DIR, f"{record.id}.path")
        if not os.path.exists(path_mapping_file):
            raise NotFoundError("File not found")

        with open(path_mapping_file, "r") as f:
            file_path = f.read().strip()

        if not os.path.exists(file_path):
            record.status = "expired"
            await self.db.flush()
            raise NotFoundError("File has been cleaned up")

        record.download_count += 1
        await self.db.flush()

        return file_path

    async def delete_record(self, record_id: str, user_id: str) -> bool:
        result = await self.db.execute(
            select(MergeHistory).where(MergeHistory.id == record_id)
        )
        record = result.scalar_one_or_none()

        if not record:
            raise NotFoundError("Record not found")

        if record.user_id != user_id:
            raise AuthorizationError("Access denied")

        # Clean up files
        path_mapping_file = os.path.join(settings.MERGED_DIR, f"{record.id}.path")
        if os.path.exists(path_mapping_file):
            with open(path_mapping_file, "r") as f:
                file_path = f.read().strip()
            if os.path.exists(file_path):
                os.remove(file_path)
            os.remove(path_mapping_file)

        await self.db.delete(record)
        await self.db.flush()

        logger.info("history_deleted", record_id=record_id, user_id=user_id)
        return True

    async def regenerate_download(self, record_id: str, user_id: str) -> MergeHistory:
        result = await self.db.execute(
            select(MergeHistory).where(MergeHistory.id == record_id)
        )
        record = result.scalar_one_or_none()

        if not record:
            raise NotFoundError("Record not found")

        if record.user_id != user_id:
            raise AuthorizationError("Access denied")

        # Check if file still exists
        path_mapping_file = os.path.join(settings.MERGED_DIR, f"{record.id}.path")
        if not os.path.exists(path_mapping_file):
            raise NotFoundError("File no longer available")

        with open(path_mapping_file, "r") as f:
            file_path = f.read().strip()

        if not os.path.exists(file_path):
            raise NotFoundError("File has been cleaned up")

        # Regenerate token
        record.download_token = create_download_token(record.id)
        record.download_expires_at = datetime.utcnow() + timedelta(
            minutes=settings.FILE_RETENTION_MINUTES
        )
        record.status = "completed"

        await self.db.flush()
        await self.db.refresh(record)

        return record