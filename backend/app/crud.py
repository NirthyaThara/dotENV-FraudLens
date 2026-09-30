from datetime import datetime, timedelta
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, joinedload

from .models import FraudFlag, Transaction
from .schemas import TransactionCreate
from .utils import utcnow

# Allowed review moves. Anything else returns 409.
ALLOWED_TRANSITIONS = {
    ("PENDING", "REVIEWED"),
    ("PENDING", "CLEARED"),
    ("REVIEWED", "CLEARED"),
}


# ---------- Transactions ----------
def txn_to_dict(t: Transaction) -> dict:
    return {
        "id": t.id,
        "user_id": t.user_id,
        "amount": t.amount,
        "currency": t.currency,
        "merchant": t.merchant,
        "lat": t.lat,
        "lon": t.lon,
        "city": t.city,
        "country": t.country,
        "timestamp": t.timestamp,
    }


def create_transaction(db: Session, data: TransactionCreate) -> Transaction:
    txn = Transaction(**data.model_dump())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def get_recent_history(
    db: Session, user_id: str, before: datetime, hours: int = 24
) -> List[dict]:
    """The user's earlier transactions (last 24h), newest first, as plain dicts."""
    stmt = (
        select(Transaction)
        .where(
            Transaction.user_id == user_id,
            Transaction.timestamp <= before,
            Transaction.timestamp >= before - timedelta(hours=hours),
        )
        .order_by(Transaction.timestamp.desc())
        .limit(200)
    )
    return [txn_to_dict(t) for t in db.scalars(stmt).all()]


def list_transactions(
    db: Session, user_id: Optional[str], limit: int, offset: int
) -> Tuple[Sequence[Transaction], int]:
    filters = []
    if user_id:
        filters.append(Transaction.user_id == user_id)
    total = db.scalar(select(func.count(Transaction.id)).where(*filters)) or 0
    items = db.scalars(
        select(Transaction)
        .where(*filters)
        .order_by(Transaction.timestamp.desc(), Transaction.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return items, total


# ---------- Flags ----------
def create_flag(db: Session, transaction_id: int, result: dict) -> FraudFlag:
    flag = FraudFlag(
        transaction_id=transaction_id,
        risk_score=max(0, min(100, int(result["risk_score"]))),
        risk_level=result["risk_level"],
        reasons=result.get("reasons", []),
    )
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return flag


def get_flag(db: Session, flag_id: int) -> Optional[FraudFlag]:
    return db.get(FraudFlag, flag_id)


def list_flags(
    db: Session,
    status: Optional[str],
    level: Optional[str],
    user_id: Optional[str],
    limit: int,
    offset: int,
) -> Tuple[Sequence[FraudFlag], int]:
    filters = []
    if status:
        filters.append(FraudFlag.review_status == status)
    if level:
        filters.append(FraudFlag.risk_level == level)
    if user_id:
        filters.append(Transaction.user_id == user_id)

    total = (
        db.scalar(
            select(func.count(FraudFlag.id)).join(Transaction).where(*filters)
        )
        or 0
    )
    items = db.scalars(
        select(FraudFlag)
        .join(Transaction)
        .options(joinedload(FraudFlag.transaction))
        .where(*filters)
        .order_by(FraudFlag.created_at.desc(), FraudFlag.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return items, total


def set_review_status(
    db: Session, flag: FraudFlag, new_status: str, comment: Optional[str]
) -> FraudFlag:
    if (flag.review_status, new_status) not in ALLOWED_TRANSITIONS:
        raise ValueError(
            f"Flag is already {flag.review_status}; cannot change it to {new_status}"
        )
    flag.review_status = new_status
    flag.reviewed_at = utcnow()
    if comment:
        flag.review_comment = comment
    db.commit()
    db.refresh(flag)
    return flag


# ---------- Stats ----------
def compute_stats(db: Session) -> dict:
    total_txn = db.scalar(select(func.count(Transaction.id))) or 0
    total_flags = db.scalar(select(func.count(FraudFlag.id))) or 0

    by_level = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for level, n in db.execute(
        select(FraudFlag.risk_level, func.count(FraudFlag.id)).group_by(
            FraudFlag.risk_level
        )
    ):
        by_level[level] = n

    by_status = {"PENDING": 0, "REVIEWED": 0, "CLEARED": 0}
    for st, n in db.execute(
        select(FraudFlag.review_status, func.count(FraudFlag.id)).group_by(
            FraudFlag.review_status
        )
    ):
        by_status[st] = n

    by_rule: dict = {}
    for (reasons,) in db.execute(select(FraudFlag.reasons)):
        for r in reasons or []:
            name = r.get("rule", "unknown")
            by_rule[name] = by_rule.get(name, 0) + 1

    decided = by_status["REVIEWED"] + by_status["CLEARED"]
    return {
        "total_transactions": total_txn,
        "total_flags": total_flags,
        "flag_rate": round(total_flags / total_txn * 100, 1) if total_txn else 0.0,
        "by_level": by_level,
        "by_status": by_status,
        "by_rule": by_rule,
        "false_positive_rate": (
            round(by_status["CLEARED"] / decided * 100, 1) if decided else 0.0
        ),
    }


# ---------- Demo ----------
def reset_all(db: Session) -> None:
    db.execute(delete(FraudFlag))
    db.execute(delete(Transaction))
    db.commit()
