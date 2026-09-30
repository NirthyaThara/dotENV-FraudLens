from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import (
    FlagOut,
    PagedTransactions,
    TransactionCreate,
    TransactionOut,
    TransactionWithFlag,
)
from ..services import process_transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionWithFlag, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    txn, flag = process_transaction(db, payload, background)
    return TransactionWithFlag(
        transaction=TransactionOut.model_validate(txn),
        flag=FlagOut.model_validate(flag) if flag else None,
    )


@router.get("", response_model=PagedTransactions)
def list_transactions(
    user_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = crud.list_transactions(db, user_id, limit, offset)
    return PagedTransactions(
        items=[TransactionOut.model_validate(t) for t in items],
        total=total,
        limit=limit,
        offset=offset,
    )
