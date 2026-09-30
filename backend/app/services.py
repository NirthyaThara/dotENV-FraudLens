import logging
from typing import Optional, Tuple

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from . import crud
from .database import SessionLocal
from .integrations import evaluate, send_alert
from .models import FraudFlag, Transaction
from .schemas import FlagOut, TransactionCreate

logger = logging.getLogger("services")


def send_alert_task(flag_id: int) -> None:
    """Runs in the background after the response. Uses its own DB session."""
    db = SessionLocal()
    try:
        flag = db.get(FraudFlag, flag_id)
        if flag is None or flag.notified:  # never alert twice
            return
        payload = FlagOut.model_validate(flag).model_dump()
        try:
            send_alert(payload)
        except Exception:
            logger.exception("Alert failed for flag %s", flag_id)
            return
        flag.notified = True
        db.commit()
    finally:
        db.close()


def process_transaction(
    db: Session, data: TransactionCreate, background: BackgroundTasks
) -> Tuple[Transaction, Optional[FraudFlag]]:
    """
    1. read the user's recent history
    2. save the transaction
    3. ask the engine for a verdict
    4. save a flag if flagged
    5. queue an alert if risk is HIGH
    """
    history = crud.get_recent_history(db, data.user_id, data.timestamp)
    txn = crud.create_transaction(db, data)

    try:
        result = evaluate(crud.txn_to_dict(txn), history)
    except Exception:
        # A broken engine must not lose the transaction or crash the demo
        logger.exception("Engine failed for transaction %s", txn.id)
        result = None

    flag = None
    if result and result.get("flagged"):
        flag = crud.create_flag(db, txn.id, result)
        if flag.risk_level == "HIGH":
            background.add_task(send_alert_task, flag.id)

    return txn, flag
