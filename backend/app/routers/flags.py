from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..security import WRITE_LIMIT, limiter, require_api_key

from .. import crud
from ..database import get_db
from ..models import AuditLog
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
    flag_id: int, new_status: str, body: Optional[ReviewRequest], db: Session,
    request: Optional[Request] = None,
) -> FlagOut:
    flag = crud.get_flag(db, flag_id)
    if flag is None:
        raise HTTPException(status_code=404, detail="Flag not found")
    previous_status = flag.review_status
    try:
        flag = crud.set_review_status(
            db, flag, new_status, body.comment if body else None
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    # Write immutable audit trail
    client_ip = request.client.host if request and request.client else None
    db.add(AuditLog(
        flag_id=flag.id,
        action=new_status,
        previous_status=previous_status,
        new_status=new_status,
        comment=body.comment if body else None,
        client_ip=client_ip,
    ))
    db.commit()

    return FlagOut.model_validate(flag)


@router.patch("/{flag_id}/review", response_model=FlagOut,
              dependencies=[Depends(require_api_key)])
@limiter.limit(WRITE_LIMIT)
def review_flag(
    request: Request,
    flag_id: int,
    body: Optional[ReviewRequest] = None,
    db: Session = Depends(get_db),
):
    return _change_status(flag_id, "REVIEWED", body, db, request)


@router.patch("/{flag_id}/clear", response_model=FlagOut,
              dependencies=[Depends(require_api_key)])
@limiter.limit(WRITE_LIMIT)
def clear_flag(
    request: Request,
    flag_id: int,
    body: Optional[ReviewRequest] = None,
    db: Session = Depends(get_db),
):
    return _change_status(flag_id, "CLEARED", body, db, request)
