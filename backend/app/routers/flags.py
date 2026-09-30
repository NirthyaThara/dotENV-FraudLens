from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import (
    FlagOut,
    PagedFlags,
    ReviewRequest,
    ReviewStatus,
    RiskLevel,
)

router = APIRouter(prefix="/flags", tags=["flags"])


@router.get("", response_model=PagedFlags)
def list_flags(
    status: Optional[ReviewStatus] = None,
    level: Optional[RiskLevel] = None,
    user_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = crud.list_flags(db, status, level, user_id, limit, offset)
    return PagedFlags(
        items=[FlagOut.model_validate(f) for f in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{flag_id}", response_model=FlagOut)
def get_flag(flag_id: int, db: Session = Depends(get_db)):
    flag = crud.get_flag(db, flag_id)
    if flag is None:
        raise HTTPException(status_code=404, detail="Flag not found")
    return FlagOut.model_validate(flag)


def _change_status(
    flag_id: int, new_status: str, body: Optional[ReviewRequest], db: Session
) -> FlagOut:
    flag = crud.get_flag(db, flag_id)
    if flag is None:
        raise HTTPException(status_code=404, detail="Flag not found")
    try:
        flag = crud.set_review_status(
            db, flag, new_status, body.comment if body else None
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return FlagOut.model_validate(flag)


@router.patch("/{flag_id}/review", response_model=FlagOut)
def review_flag(
    flag_id: int,
    body: Optional[ReviewRequest] = None,
    db: Session = Depends(get_db),
):
    return _change_status(flag_id, "REVIEWED", body, db)


@router.patch("/{flag_id}/clear", response_model=FlagOut)
def clear_flag(
    flag_id: int,
    body: Optional[ReviewRequest] = None,
    db: Session = Depends(get_db),
):
    return _change_status(flag_id, "CLEARED", body, db)
