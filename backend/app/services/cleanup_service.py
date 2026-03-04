import os
import shutil
import time
from datetime import datetime, timedelta
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class CleanupService:
    @staticmethod
    def cleanup_expired_files():
        """Remove files older than retention period."""
        cutoff_time = time.time() - (settings.FILE_RETENTION_MINUTES * 60)
        cleaned_count = 0

        # Clean upload sessions
        if os.path.exists(settings.UPLOAD_DIR):
            for item in os.listdir(settings.UPLOAD_DIR):
                item_path = os.path.join(settings.UPLOAD_DIR, item)
                try:
                    if os.path.isdir(item_path):
                        mod_time = os.path.getmtime(item_path)
                        if mod_time < cutoff_time:
                            shutil.rmtree(item_path, ignore_errors=True)
                            cleaned_count += 1
                except Exception as e:
                    logger.warning("cleanup_error", path=item_path, error=str(e))

        # Clean merged files
        if os.path.exists(settings.MERGED_DIR):
            for item in os.listdir(settings.MERGED_DIR):
                item_path = os.path.join(settings.MERGED_DIR, item)
                try:
                    if os.path.isfile(item_path):
                        mod_time = os.path.getmtime(item_path)
                        if mod_time < cutoff_time:
                            os.remove(item_path)
                            cleaned_count += 1
                except Exception as e:
                    logger.warning("cleanup_error", path=item_path, error=str(e))

        if cleaned_count > 0:
            logger.info("cleanup_completed", files_removed=cleaned_count)

        return cleaned_count