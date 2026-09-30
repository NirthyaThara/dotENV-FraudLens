"""
security.py -- API key authentication and rate-limiter configuration.

How it works
------------
1. Set  API_KEY=<your-secret>  in your .env file (or environment).
2. Every write request must include the header:  X-API-Key: <your-secret>
3. If the key is wrong or missing you get 401 Unauthorized.
4. After 10 consecutive bad keys from the same IP, that IP is locked out
   for 15 minutes (returns 429).
5. Rate limits:
       - Global:  60 requests / minute  per IP
       - Write:   10 requests / minute  per IP  (POST, PATCH, DELETE)
6. If API_KEY is not set a warning is logged and auth is skipped (dev mode).
   Never leave this in production!
"""

import logging
import os
import secrets
import time
from typing import Dict

from fastapi import Header, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger("security")

# ---------------------------------------------------------------------------
# API Key
# ---------------------------------------------------------------------------
_API_KEY: str | None = os.getenv("API_KEY")

if not _API_KEY:
    logger.warning(
        "API_KEY is not set -- authentication is DISABLED. "
        "Set API_KEY=<secret> in your .env file before going to production."
    )

# Brute-force lockout state (in-memory; use Redis for multi-worker production)
_MAX_FAILURES = 10
_LOCKOUT_SECONDS = 15 * 60  # 15 minutes
_fail_counts: Dict[str, int] = {}
_lockout: Dict[str, float] = {}   # ip -> monotonic unlock timestamp


async def require_api_key(
    request: Request,
    x_api_key: str = Header(default=""),
) -> None:
    """FastAPI dependency -- inject with  Depends(require_api_key).

    - Skips the check when API_KEY is not configured (dev-mode fallback).
    - Uses constant-time comparison to prevent timing attacks.
    - Locks out an IP for 15 min after 10 consecutive bad keys.
    """
    if _API_KEY is None:
        return  # Auth disabled -- dev mode

    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()

    # Check active lockout
    if client_ip in _lockout:
        if now < _lockout[client_ip]:
            remaining = int(_lockout[client_ip] - now)
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed attempts. Try again in {remaining}s.",
            )
        else:
            del _lockout[client_ip]
            _fail_counts.pop(client_ip, None)

    if not secrets.compare_digest(x_api_key, _API_KEY):
        count = _fail_counts.get(client_ip, 0) + 1
        _fail_counts[client_ip] = count
        if count >= _MAX_FAILURES:
            _lockout[client_ip] = now + _LOCKOUT_SECONDS
            _fail_counts.pop(client_ip, None)
            logger.warning(
                "IP %s locked out after %d failed API key attempts", client_ip, _MAX_FAILURES
            )
            raise HTTPException(
                status_code=429,
                detail="Too many failed attempts. Locked out for 15 minutes.",
            )
        logger.warning(
            "Bad API key from %s (attempt %d/%d)", client_ip, count, _MAX_FAILURES
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Pass it as the X-API-Key header.",
        )

    # Successful auth -- reset failure counter
    _fail_counts.pop(client_ip, None)


# ---------------------------------------------------------------------------
# Rate Limiter  (slowapi)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

# Tighter limit string used on write endpoints
WRITE_LIMIT = "10/minute"

