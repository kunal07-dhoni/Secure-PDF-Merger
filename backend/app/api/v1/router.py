"""
API v1 router aggregating all sub-routers.
"""
from fastapi import APIRouter
from app.api.v1 import auth, pdf, history, health

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)
api_router.include_router(
    pdf.router,
    prefix="/pdf",
    tags=["PDF Operations"],
)
api_router.include_router(
    history.router,
    prefix="/history",
    tags=["Merge History"],
)
api_router.include_router(
    health.router,
    prefix="",
    tags=["System"],
)