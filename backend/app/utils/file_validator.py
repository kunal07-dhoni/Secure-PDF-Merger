"""
File validation utilities with robust MIME type checking.
Falls back gracefully if python-magic is not available.
"""
import os
from typing import Tuple
from pypdf import PdfReader
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

ALLOWED_MIME_TYPES = {
    "application/pdf",
}

PDF_MAGIC_BYTES = b"%PDF"

# Try to import python-magic, fall back if unavailable
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    logger.warning("python-magic not available, using fallback MIME detection")


def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """Validate that file size is within acceptable limits."""
    if file_size > settings.max_file_size_bytes:
        return False, f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum of {settings.MAX_FILE_SIZE_MB}MB"
    if file_size == 0:
        return False, "File is empty"
    return True, ""


def validate_pdf_magic_bytes(content: bytes) -> Tuple[bool, str]:
    """Check PDF magic bytes at beginning of file."""
    if len(content) < 4:
        return False, "File is too small to be a valid PDF"
    if content[:4] != PDF_MAGIC_BYTES:
        return False, "File does not appear to be a valid PDF (invalid header)"
    return True, ""


def validate_mime_type(content: bytes) -> Tuple[bool, str]:
    """Validate MIME type of uploaded content."""
    if HAS_MAGIC:
        try:
            mime = magic.from_buffer(content[:2048], mime=True)
            if mime not in ALLOWED_MIME_TYPES:
                return False, f"Invalid file type: {mime}. Only PDF files are allowed."
            return True, ""
        except Exception as e:
            logger.warning("magic_mime_detection_failed", error=str(e))

    # Fallback to magic bytes check
    return validate_pdf_magic_bytes(content)


def validate_pdf_integrity(file_path: str) -> Tuple[bool, int, str]:
    """
    Validate PDF file integrity by attempting to parse it.
    Returns: (is_valid, page_count, error_message)
    """
    try:
        if not os.path.exists(file_path):
            return False, 0, "File does not exist"

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, 0, "File is empty"

        reader = PdfReader(file_path)
        page_count = len(reader.pages)

        if page_count == 0:
            return False, 0, "PDF has no pages"

        # Try to access first page to verify integrity
        first_page = reader.pages[0]
        # Try to get the mediabox to ensure page is readable
        _ = first_page.mediabox

        return True, page_count, ""

    except Exception as e:
        error_msg = str(e)
        logger.error("pdf_validation_error", error=error_msg, file=file_path)
        return False, 0, f"Corrupted or invalid PDF: {error_msg[:200]}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and other attacks.
    """
    if not filename:
        return "unnamed.pdf"

    # Remove path components
    filename = os.path.basename(filename)

    # Remove dangerous sequences
    filename = filename.replace("..", "")
    filename = filename.replace("/", "")
    filename = filename.replace("\\", "")
    filename = filename.replace("\x00", "")  # Null byte

    # Keep only safe characters
    safe_chars = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789._- "
    )
    filename = "".join(c if c in safe_chars else "_" for c in filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Ensure non-empty
    if not filename or filename == ".pdf":
        filename = "unnamed.pdf"

    # Ensure .pdf extension
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    # Truncate to reasonable length
    if len(filename) > 255:
        name_part = filename[:-4][:247]
        filename = name_part + ".pdf"

    return filename


def validate_filename_for_output(filename: str) -> str:
    """Validate and sanitize output filename."""
    filename = sanitize_filename(filename)

    # Additional output-specific checks
    reserved_names = {
        "con", "prn", "aux", "nul",
        "com1", "com2", "com3", "com4",
        "lpt1", "lpt2", "lpt3", "lpt4",
    }

    name_without_ext = filename[:-4].lower().strip()
    if name_without_ext in reserved_names:
        filename = f"output_{filename}"

    return filename