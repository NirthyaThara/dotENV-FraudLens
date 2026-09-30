import logging
import os

from dotenv import load_dotenv

load_dotenv()  # must run before the app modules read environment variables

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.middleware.trustedhost import TrustedHostMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from slowapi import _rate_limit_exceeded_handler  # noqa: E402
from slowapi.errors import RateLimitExceeded  # noqa: E402
from slowapi.middleware import SlowAPIMiddleware  # noqa: E402
from starlette.middleware.base import BaseHTTPMiddleware  # noqa: E402

from . import models  # noqa: E402,F401  (registers tables)
from .database import Base, engine  # noqa: E402
from .routers import flags, simulate, stats, transactions  # noqa: E402
from .security import limiter  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fraud Rule Engine API",
    version="1.0.0",
    description="Stores transactions, runs the fraud engine, serves flags to the reviewer console.",
)

# ── Rate limiter ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── Trusted hosts ────────────────────────────────────────────────────────────
# Rejects requests whose Host header is not in this list (prevents host-injection).
# Set ALLOWED_HOSTS=yourdomain.com in production. Defaults to wildcard (*) in dev.
_raw_allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
_ALLOWED_HOSTS = (
    [h.strip() for h in _raw_allowed_hosts.split(",") if h.strip()]
    if _raw_allowed_hosts.strip()
    else ["*"]  # dev/test mode -- unrestricted
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=_ALLOWED_HOSTS)

# ── Security response headers ────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard browser security headers and strips the Server header."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        # Remove server version fingerprint
        if "server" in response.headers:
            del response.headers["server"]
        return response

app.add_middleware(SecurityHeadersMiddleware)

# ── Request body size limit (64 KB) ─────────────────────────────────────────
_MAX_BODY = int(os.getenv("MAX_BODY_BYTES", str(64 * 1024)))  # 64 KB default

class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Rejects requests whose body exceeds MAX_BODY_BYTES."""

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > _MAX_BODY:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request body too large (max {_MAX_BODY} bytes)."},
            )
        return await call_next(request)

app.add_middleware(BodySizeLimitMiddleware)

origins = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],  # no wildcard
    allow_headers=["Content-Type", "X-API-Key"],        # only what's needed
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
)


# Errors always look like {"detail": "message"}
@app.exception_handler(RequestValidationError)
async def validation_handler(_request: Request, exc: RequestValidationError):
    parts = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err["loc"] if p not in ("body", "query"))
        parts.append(f"{loc}: {err['msg']}" if loc else err["msg"])
    return JSONResponse(status_code=422, content={"detail": "; ".join(parts)})


@app.exception_handler(Exception)
async def unhandled_handler(_request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(transactions.router)
app.include_router(flags.router)
app.include_router(stats.router)
app.include_router(simulate.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}
