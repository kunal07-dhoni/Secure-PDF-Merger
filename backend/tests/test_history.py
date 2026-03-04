"""
History endpoint tests.
"""
import io
import pytest
from httpx import AsyncClient
from tests.test_pdf import create_test_pdf


@pytest.mark.asyncio
async def test_empty_history(authenticated_client):
    client, user = authenticated_client

    response = await client.get("/api/v1/history/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_history_after_merge(authenticated_client):
    client, user = authenticated_client

    # Upload and merge
    pdf1 = create_test_pdf(1)
    pdf2 = create_test_pdf(1)
    files = [
        ("files", ("a.pdf", io.BytesIO(pdf1), "application/pdf")),
        ("files", ("b.pdf", io.BytesIO(pdf2), "application/pdf")),
    ]

    upload_resp = await client.post("/api/v1/pdf/upload", files=files)
    session_id = upload_resp.json()["session_id"]
    file_indices = [f["index"] for f in upload_resp.json()["files"]]

    await client.post(
        "/api/v1/pdf/merge",
        data={
            "session_id": session_id,
            "file_order": str(file_indices),
            "output_filename": "history_test.pdf",
        },
    )

    # Check history
    response = await client.get("/api/v1/history/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["output_filename"] == "history_test.pdf"


@pytest.mark.asyncio
async def test_delete_history(authenticated_client):
    client, user = authenticated_client

    # Create a merge first
    pdf1 = create_test_pdf(1)
    pdf2 = create_test_pdf(1)
    files = [
        ("files", ("x.pdf", io.BytesIO(pdf1), "application/pdf")),
        ("files", ("y.pdf", io.BytesIO(pdf2), "application/pdf")),
    ]

    upload_resp = await client.post("/api/v1/pdf/upload", files=files)
    session_id = upload_resp.json()["session_id"]
    file_indices = [f["index"] for f in upload_resp.json()["files"]]

    await client.post(
        "/api/v1/pdf/merge",
        data={
            "session_id": session_id,
            "file_order": str(file_indices),
            "output_filename": "delete_test.pdf",
        },
    )

    # Get history
    history_resp = await client.get("/api/v1/history/")
    record_id = history_resp.json()["items"][0]["id"]

    # Delete
    delete_resp = await client.delete(f"/api/v1/history/{record_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["success"] is True


@pytest.mark.asyncio
async def test_history_pagination(authenticated_client):
    client, user = authenticated_client

    response = await client.get("/api/v1/history/?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data