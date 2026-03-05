from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.api.v1.router import api_router
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.utils.logging_config import setup_logging, get_logger

try:
    setup_logging()
except Exception as e:
    print(f"Logging warning: {e}")

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting", env=settings.APP_ENV)

    try:
        await init_db()
        logger.info("database_ready")
    except Exception as e:
        logger.error("db_error", error=str(e))
        raise

    try:
        from app.tasks.scheduled import setup_scheduled_tasks
        setup_scheduled_tasks()
    except Exception as e:
        logger.warning("scheduler_warning", error=str(e))

    yield

    try:
        from app.tasks.scheduled import shutdown_scheduled_tasks
        shutdown_scheduled_tasks()
    except Exception:
        pass

    logger.info("shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    description="Secure PDF Merger API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Middleware order matters: last added = first executed

# 1. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Content-Disposition",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
    ],
)

# 2. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. Global Rate Limiter
app.add_middleware(
    RateLimitMiddleware,
    default_limit=f"{settings.RATE_LIMIT_PER_MINUTE}/minute",
)


# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    messages = []
    for err in exc.errors():
        loc = " → ".join(str(x) for x in err.get("loc", []) if x != "body")
        msg = err.get("msg", "Invalid")
        messages.append(f"{loc}: {msg}" if loc else msg)

    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(messages)},
    )


@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    logger.error("unhandled", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc) if settings.DEBUG else "Internal server error"
        },
    )


# Routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health():
    return {"status": "healthy", "app": settings.APP_NAME, "version": "1.0.0"}


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/api/docs"}