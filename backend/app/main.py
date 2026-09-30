import logging
import os

from dotenv import load_dotenv

load_dotenv()  # must run before the app modules read environment variables

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

from . import models  # noqa: E402,F401  (registers tables)
from .database import Base, engine  # noqa: E402
from .routers import flags, simulate, stats, transactions  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fraud Rule Engine API",
    version="1.0.0",
    description="Stores transactions, runs the fraud engine, serves flags to the reviewer console.",
)

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
    allow_methods=["*"],
    allow_headers=["*"],
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
