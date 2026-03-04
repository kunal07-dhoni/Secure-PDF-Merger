"""
PDF operation endpoint tests.
"""
import io
import pytest
from httpx import AsyncClient
from pypdf import PdfWriter


def create_test_pdf(num_pages: int = 3, text: str = "Test Page") -> bytes:
    """Create a simple test PDF in memory."""
    writer = PdfWriter()

    for i in range(num_pages):
        writer.add_blank_page(width=612, height=792)

    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer.read()


@pytest.mark.asyncio
async def test_upload_pdfs(authenticated_client):
    client, user = authenticated_client

    pdf1 = create_test_pdf(2, "First PDF")
    pdf2 = create_test_pdf(3, "Second PDF")

    files = [
        ("files", ("test1.pdf", io.BytesIO(pdf1), "application/pdf")),
        ("files", ("test2.pdf", io.BytesIO(pdf2), "application/pdf")),
    ]

    response = await client.post("/api/v1/pdf/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["total_files"] == 2


@pytest.mark.asyncio
async def test_upload_single_pdf_fails(authenticated_client):
    client, user = authenticated_client

    pdf = create_test_pdf(1)
    files = [("files", ("single.pdf", io.BytesIO(pdf), "application/pdf"))]

    response = await client.post("/api/v1/pdf/upload", files=files)
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_upload_non_pdf_fails(authenticated_client):
    client, user = authenticated_client

    fake_content = b"This is not a PDF file at all"
    files = [
        ("files", ("test1.pdf", io.BytesIO(create_test_pdf(1)), "application/pdf")),
        ("files", ("fake.pdf", io.BytesIO(fake_content), "application/pdf")),
    ]

    response = await client.post("/api/v1/pdf/upload", files=files)
    data = response.json()

    # Should still succeed if at least 2 valid files exist
    # Or fail if less than 2 valid
    if response.status_code == 200:
        invalid_files = [f for f in data["files"] if not f["is_valid"]]
        assert len(invalid_files) >= 1


@pytest.mark.asyncio
async def test_upload_unauthenticated(client: AsyncClient):
    pdf = create_test_pdf(1)
    files = [("files", ("test.pdf", io.BytesIO(pdf), "application/pdf"))]

    response = await client.post("/api/v1/pdf/upload", files=files)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_full_merge_flow(authenticated_client):
    client, user = authenticated_client

    # Step 1: Upload
    pdf1 = create_test_pdf(2)
    pdf2 = create_test_pdf(3)

    files = [
        ("files", ("doc1.pdf", io.BytesIO(pdf1), "application/pdf")),
        ("files", ("doc2.pdf", io.BytesIO(pdf2), "application/pdf")),
    ]

    upload_response = await client.post("/api/v1/pdf/upload", files=files)
    assert upload_response.status_code == 200
    session_id = upload_response.json()["session_id"]
    uploaded_files = upload_response.json()["files"]

    # Step 2: Merge
    merge_data = {
        "session_id": session_id,
        "file_order": str([f["index"] for f in uploaded_files]),
        "output_filename": "test_merged.pdf",
        "compress": "false",
    }

    merge_response = await client.post("/api/v1/pdf/merge", data=merge_data)
    assert merge_response.status_code == 200
    assert merge_response.json()["success"] is True
    assert merge_response.json()["total_pages"] == 5