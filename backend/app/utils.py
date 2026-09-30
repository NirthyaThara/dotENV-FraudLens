from datetime import datetime, timezone


def utcnow() -> datetime:
    """Current UTC time without tzinfo (SQLite does not store timezones)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_naive_utc(dt: datetime) -> datetime:
    """Convert any datetime to naive UTC."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def to_z(dt: datetime) -> str:
    """Format as ISO 8601 UTC, e.g. 2026-09-30T06:15:00Z."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
