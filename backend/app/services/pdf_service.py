import os
import uuid
import json
import shutil
import io
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from app.config import settings
from app.schemas.pdf import PageRange, FileInfo, MergeResponse
from app.utils.file_validator import (
    validate_file_size,
    validate_pdf_magic_bytes,
    validate_pdf_integrity,
    sanitize_filename,
)
from app.utils.security import create_download_token
from app.exceptions import FileProcessingError, ValidationError
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class PDFService:
    def __init__(self):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.MERGED_DIR, exist_ok=True)

    def _get_session_dir(self, session_id: str) -> str:
        # Prevent path traversal
        safe_id = session_id.replace("/", "").replace("\\", "").replace("..", "")
        path = os.path.join(settings.UPLOAD_DIR, safe_id)
        os.makedirs(path, exist_ok=True)
        return path

    async def process_uploads(
        self, files: list, user_id: str
    ) -> Tuple[str, List[FileInfo]]:
        if len(files) < 2:
            raise ValidationError("At least 2 PDF files are required for merging")

        if len(files) > settings.MAX_FILES_PER_MERGE:
            raise ValidationError(
                f"Maximum {settings.MAX_FILES_PER_MERGE} files allowed per merge"
            )

        session_id = f"{user_id}_{uuid.uuid4().hex[:12]}"
        session_dir = self._get_session_dir(session_id)
        file_infos = []

        try:
            for idx, file in enumerate(files):
                content = await file.read()
                await file.seek(0)

                # Validate file size
                valid, msg = validate_file_size(len(content))
                if not valid:
                    file_infos.append(
                        FileInfo(
                            index=idx,
                            filename=sanitize_filename(file.filename),
                            size_bytes=len(content),
                            page_count=0,
                            is_valid=False,
                            error=msg,
                        )
                    )
                    continue

                # Validate magic bytes
                valid, msg = validate_pdf_magic_bytes(content)
                if not valid:
                    file_infos.append(
                        FileInfo(
                            index=idx,
                            filename=sanitize_filename(file.filename),
                            size_bytes=len(content),
                            page_count=0,
                            is_valid=False,
                            error=msg,
                        )
                    )
                    continue

                # Save file temporarily
                safe_name = f"{idx:04d}_{uuid.uuid4().hex[:8]}.pdf"
                file_path = os.path.join(session_dir, safe_name)

                with open(file_path, "wb") as f:
                    f.write(content)

                # Validate PDF integrity
                valid, page_count, msg = validate_pdf_integrity(file_path)
                if not valid:
                    os.remove(file_path)
                    file_infos.append(
                        FileInfo(
                            index=idx,
                            filename=sanitize_filename(file.filename),
                            size_bytes=len(content),
                            page_count=0,
                            is_valid=False,
                            error=msg,
                        )
                    )
                    continue

                file_infos.append(
                    FileInfo(
                        index=idx,
                        filename=sanitize_filename(file.filename),
                        size_bytes=len(content),
                        page_count=page_count,
                        is_valid=True,
                    )
                )

                # Store mapping
                mapping_file = os.path.join(session_dir, "mapping.json")
                mapping = {}
                if os.path.exists(mapping_file):
                    with open(mapping_file, "r") as f:
                        mapping = json.load(f)

                mapping[str(idx)] = {
                    "stored_name": safe_name,
                    "original_name": sanitize_filename(file.filename),
                    "page_count": page_count,
                    "size": len(content),
                }

                with open(mapping_file, "w") as f:
                    json.dump(mapping, f)

        except Exception as e:
            # Clean up on error
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.error("upload_processing_error", error=str(e))
            raise FileProcessingError(f"Error processing uploads: {str(e)}")

        # Check if we have at least 2 valid files
        valid_count = sum(1 for fi in file_infos if fi.is_valid)
        if valid_count < 2:
            shutil.rmtree(session_dir, ignore_errors=True)
            raise ValidationError(
                "At least 2 valid PDF files are required. Check individual file errors."
            )

        logger.info(
            "files_uploaded",
            session_id=session_id,
            total_files=len(files),
            valid_files=valid_count,
        )

        return session_id, file_infos

    async def merge_pdfs(
        self,
        session_id: str,
        file_order: List[int],
        output_filename: str,
        page_ranges: Optional[List[PageRange]] = None,
        watermark_text: Optional[str] = None,
        compress: bool = False,
        user_id: str = None,
    ) -> Tuple[str, int, int]:
        session_dir = self._get_session_dir(session_id)
        mapping_file = os.path.join(session_dir, "mapping.json")

        if not os.path.exists(mapping_file):
            raise FileProcessingError("Upload session not found or expired")

        with open(mapping_file, "r") as f:
            mapping = json.load(f)

        writer = PdfWriter()
        total_pages = 0
        original_names = []

        # Build page range lookup
        range_map = {}
        if page_ranges:
            for pr in page_ranges:
                range_map[pr.file_index] = (pr.start_page, pr.end_page)

        try:
            for order_idx in file_order:
                str_idx = str(order_idx)
                if str_idx not in mapping:
                    logger.warning("file_index_not_found", index=order_idx)
                    continue

                file_info = mapping[str_idx]
                file_path = os.path.join(session_dir, file_info["stored_name"])

                if not os.path.exists(file_path):
                    logger.warning("file_not_found", path=file_path)
                    continue

                reader = PdfReader(file_path)
                num_pages = len(reader.pages)
                original_names.append(file_info["original_name"])

                # Determine page range
                start_page = 1
                end_page = num_pages

                if order_idx in range_map:
                    s, e = range_map[order_idx]
                    if s is not None:
                        start_page = max(1, min(s, num_pages))
                    if e is not None:
                        end_page = max(start_page, min(e, num_pages))

                for page_num in range(start_page - 1, end_page):
                    writer.add_page(reader.pages[page_num])
                    total_pages += 1

            if total_pages == 0:
                raise FileProcessingError("No pages to merge")

            # Apply watermark if requested
            if watermark_text:
                writer = self._apply_watermark(writer, watermark_text)

            # Generate output
            safe_output = sanitize_filename(output_filename)
            output_id = uuid.uuid4().hex[:12]
            output_path = os.path.join(settings.MERGED_DIR, f"{output_id}_{safe_output}")

            with open(output_path, "wb") as f:
                writer.write(f)

            # Compress if requested
            if compress:
                output_path = self._compress_pdf(output_path)

            output_size = os.path.getsize(output_path)

            logger.info(
                "pdf_merged",
                session_id=session_id,
                total_pages=total_pages,
                output_size=output_size,
                user_id=user_id,
            )

            return output_path, total_pages, output_size

        except FileProcessingError:
            raise
        except Exception as e:
            logger.error("merge_error", error=str(e), session_id=session_id)
            raise FileProcessingError(f"Error during merge: {str(e)}")

    def _apply_watermark(self, writer: PdfWriter, text: str) -> PdfWriter:
        try:
            watermarked_writer = PdfWriter()

            for page in writer.pages:
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)

                # Create watermark
                packet = io.BytesIO()
                c = canvas.Canvas(packet, pagesize=(page_width, page_height))

                c.saveState()
                c.setFillColor(
                    Color(0.5, 0.5, 0.5, alpha=settings.WATERMARK_OPACITY)
                )
                c.setFont("Helvetica", settings.WATERMARK_FONT_SIZE)
                c.translate(page_width / 2, page_height / 2)
                c.rotate(45)
                c.drawCentredString(0, 0, text)
                c.restoreState()
                c.save()

                packet.seek(0)
                watermark_reader = PdfReader(packet)
                watermark_page = watermark_reader.pages[0]

                page.merge_page(watermark_page)
                watermarked_writer.add_page(page)

            return watermarked_writer

        except Exception as e:
            logger.warning("watermark_error", error=str(e))
            return writer

    def _compress_pdf(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()

            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)

            writer.add_metadata(reader.metadata or {})

            compressed_path = file_path.replace(".pdf", "_compressed.pdf")
            with open(compressed_path, "wb") as f:
                writer.write(f)

            # If compressed is smaller, use it
            if os.path.getsize(compressed_path) < os.path.getsize(file_path):
                os.remove(file_path)
                os.rename(compressed_path, file_path)
            else:
                os.remove(compressed_path)

            return file_path

        except Exception as e:
            logger.warning("compression_error", error=str(e))
            return file_path

    def cleanup_session(self, session_id: str):
        session_dir = self._get_session_dir(session_id)
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.info("session_cleaned", session_id=session_id)

    def get_file_preview_info(self, session_id: str, file_index: int) -> dict:
        session_dir = self._get_session_dir(session_id)
        mapping_file = os.path.join(session_dir, "mapping.json")

        if not os.path.exists(mapping_file):
            raise FileProcessingError("Session not found")

        with open(mapping_file, "r") as f:
            mapping = json.load(f)

        str_idx = str(file_index)
        if str_idx not in mapping:
            raise FileProcessingError("File not found in session")

        file_info = mapping[str_idx]
        file_path = os.path.join(session_dir, file_info["stored_name"])

        reader = PdfReader(file_path)

        # Extract text from first page for preview
        first_page_text = ""
        try:
            first_page_text = reader.pages[0].extract_text()[:500]
        except Exception:
            pass

        return {
            "filename": file_info["original_name"],
            "page_count": len(reader.pages),
            "file_size": file_info["size"],
            "first_page_preview": first_page_text,
            "metadata": {
                k: str(v)
                for k, v in (reader.metadata or {}).items()
                if v
            },
        }