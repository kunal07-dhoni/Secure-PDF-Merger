"""
Custom in-memory rate limiter.
Zero external dependencies. Production ready.
Supports per-IP, per-user, and per-endpoint limiting.
"""
import time
from collections import defaultdict
from functools import wraps
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger("rate_limiter")


# ============================================
# CORE: Token Bucket Algorithm
# ============================================

class TokenBucket:
    """
    Token bucket rate limiting algorithm.
    Tokens refill gradually over time.
    Each request consumes one token.
    """

    def __init__(self, rate: int, period: int = 60):
        self.rate = rate          # max tokens
        self.period = period      # refill period in seconds
        self.tokens = float(rate) # current tokens
        self.last_refill = time.time()

    def consume(self) -> bool:
        """Try to consume one token. Returns True if allowed."""
        now = time.time()
        elapsed = now - self.last_refill

        # Refill tokens based on elapsed time
        self.tokens = min(
            self.rate,
            self.tokens + (elapsed * self.rate / self.period)
        )
        self.last_refill = now

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True

        return False

    @property
    def remaining(self) -> int:
        """Tokens remaining."""
        return max(0, int(self.tokens))

    @property
    def retry_after(self) -> int:
        """Seconds until next token available."""
        if self.tokens >= 1.0:
            return 0
        tokens_needed = 1.0 - self.tokens
        return int((tokens_needed * self.period / self.rate)) + 1


# ============================================
# STORE: Manages all rate limit buckets
# ============================================

class RateLimiterStore:
    """Thread-safe in-memory store with automatic cleanup."""

    def __init__(self):
        self._buckets: dict[str, TokenBucket] = {}
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # every 5 minutes

    def get_bucket(self, key: str, rate: int, period: int) -> TokenBucket:
        """Get or create a token bucket."""
        self._maybe_cleanup()

        if key not in self._buckets:
            self._buckets[key] = TokenBucket(rate, period)

        return self._buckets[key]

    def _maybe_cleanup(self):
        """Remove inactive buckets to prevent memory leak."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = now
        stale = [
            key for key, bucket in self._buckets.items()
            if now - bucket.last_refill > 600  # inactive 10 min
        ]

        for key in stale:
            del self._buckets[key]

        if stale:
            logger.debug("rate_limiter_cleanup", removed=len(stale))

    @property
    def bucket_count(self) -> int:
        return len(self._buckets)


# Global store instance
_store = RateLimiterStore()


# ============================================
# HELPERS
# ============================================

def _get_client_ip(request: Request) -> str:
    """Extract real client IP from request."""
    # Check proxy headers
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    if request.client:
        return request.client.host

    return "unknown"


def _get_client_identifier(request: Request) -> str:
    """Get unique identifier: user ID if authenticated, else IP."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from app.utils.security import decode_token
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if payload and payload.get("sub"):
                return f"user:{payload['sub']}"
        except Exception:
            pass

    return f"ip:{_get_client_ip(request)}"


def _parse_rate_string(rate_string: str) -> tuple:
    """
    Parse rate limit string.
    Examples: '10/minute', '100/hour', '5/second', '1000/day'
    Returns: (count, period_seconds)
    """
    parts = rate_string.strip().split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid rate format: {rate_string}. Use format: '10/minute'")

    count = int(parts[0].strip())

    period_map = {
        "second": 1, "sec": 1, "s": 1,
        "minute": 60, "min": 60, "m": 60,
        "hour": 3600, "hr": 3600, "h": 3600,
        "day": 86400, "d": 86400,
    }

    period_key = parts[1].strip().lower()
    period = period_map.get(period_key)

    if period is None:
        raise ValueError(f"Unknown period: {period_key}. Use: second/minute/hour/day")

    return count, period


# ============================================
# MIDDLEWARE: Global Rate Limiting
# ============================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Global rate limiting applied to ALL requests.
    Add to FastAPI app via app.add_middleware()
    """

    SKIP_PATHS = {
        "/health",
        "/",
        "/api/docs",
        "/api/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/favicon.svg",
    }

    def __init__(self, app, default_limit: str = None):
        super().__init__(app)
        limit_str = default_limit or f"{settings.RATE_LIMIT_PER_MINUTE}/minute"
        self.rate, self.period = _parse_rate_string(limit_str)
        logger.info(
            "rate_limiter_initialized",
            default_limit=limit_str,
            rate=self.rate,
            period_seconds=self.period,
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Skip certain paths
        if path in self.SKIP_PATHS:
            return await call_next(request)

        # Skip CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # Get client identifier
        client_id = _get_client_identifier(request)
        bucket_key = f"global:{client_id}"

        # Check rate limit
        bucket = _store.get_bucket(bucket_key, self.rate, self.period)

        if not bucket.consume():
            retry_after = bucket.retry_after

            logger.warning(
                "global_rate_limit_exceeded",
                client=client_id,
                path=path,
                retry_after=retry_after,
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please slow down and try again.",
                    "retry_after_seconds": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.rate),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit info to response headers
        response.headers["X-RateLimit-Limit"] = str(self.rate)
        response.headers["X-RateLimit-Remaining"] = str(bucket.remaining)

        return response


# ============================================
# DECORATOR: Per-Endpoint Rate Limiting
# ============================================

class _Limiter:
    """
    Decorator-based rate limiter for individual endpoints.

    Usage in route files:
        from app.middleware.rate_limiter import limiter

        @router.post("/register")
        @limiter.limit("5/minute")
        async def register(request: Request, ...):
            ...
    """

    def limit(self, limit_string: str):
        """
        Rate limit decorator.

        Args:
            limit_string: Rate limit like "5/minute", "10/hour"
        """
        rate, period = _parse_rate_string(limit_string)

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Find Request object
                request = kwargs.get("request")
                if request is None:
                    for arg in args:
                        if isinstance(arg, Request):
                            request = arg
                            break

                # If no request found, skip rate limiting
                if request is None:
                    logger.debug(
                        "rate_limit_skip_no_request",
                        endpoint=func.__name__,
                    )
                    return await func(*args, **kwargs)

                # Build unique key for this client + endpoint
                client_id = _get_client_identifier(request)
                bucket_key = f"endpoint:{func.__name__}:{client_id}"

                # Check limit
                bucket = _store.get_bucket(bucket_key, rate, period)

                if not bucket.consume():
                    retry_after = bucket.retry_after

                    logger.warning(
                        "endpoint_rate_limit_exceeded",
                        client=client_id,
                        endpoint=func.__name__,
                        limit=limit_string,
                        retry_after=retry_after,
                    )

                    raise HTTPException(
                        status_code=429,
                        detail=(
                            f"Rate limit exceeded for this action "
                            f"({limit_string}). "
                            f"Please wait {retry_after} seconds."
                        ),
                    )

                return await func(*args, **kwargs)

            return wrapper
        return decorator


# Global limiter instance - import this in route files
limiter = _Limiter()