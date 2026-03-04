"""
Health check and system status endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.config import settings
import os

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with database connectivity."""
    checks = {
        "api": "healthy",
        "database": "unknown",
        "upload_dir": "unknown",
        "merged_dir": "unknown",
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)[:100]}"

    # Check directories
    checks["upload_dir"] = (
        "healthy" if os.path.isdir(settings.UPLOAD_DIR) and os.access(settings.UPLOAD_DIR, os.W_OK)
        else "unhealthy: not writable"
    )
    checks["merged_dir"] = (
        "healthy" if os.path.isdir(settings.MERGED_DIR) and os.access(settings.MERGED_DIR, os.W_OK)
        else "unhealthy: not writable"
    )

    overall = "healthy" if all(v == "healthy" for v in checks.values()) else "degraded"

    return {
        "status": overall,
        "checks": checks,
        "config": {
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "max_files_per_merge": settings.MAX_FILES_PER_MERGE,
            "file_retention_minutes": settings.FILE_RETENTION_MINUTES,
        },
    }