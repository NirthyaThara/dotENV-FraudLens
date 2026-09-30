import random
import uuid
from datetime import timedelta
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import SimulateOut, TransactionCreate
from ..services import process_transaction
from ..utils import utcnow

router = APIRouter(tags=["demo"])

Scenario = Literal["normal", "velocity", "impossible_travel"]

CHENNAI = dict(lat=13.0827, lon=80.2707, city="Chennai", country="IN")
LONDON = dict(lat=51.5074, lon=-0.1278, city="London", country="GB")


def _txn(user: str, amount: float, merchant: str, place: dict, ts) -> TransactionCreate:
    return TransactionCreate(
        user_id=user, amount=amount, merchant=merchant, timestamp=ts, **place
    )


@router.post("/simulate/{scenario}", response_model=SimulateOut)
def simulate(
    scenario: Scenario,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Creates a batch of transactions that should trigger a given rule."""
    now = utcnow()
    # Fresh user each click, so old history never mixes into a new demo
    user = f"SIM-{scenario[:3].upper()}-{uuid.uuid4().hex[:4]}"

    if scenario == "normal":
        batch = [
            _txn(user, round(random.uniform(200, 3000), 2), "Local Grocery", CHENNAI, now)
        ]
    elif scenario == "velocity":
        merchants = ["Cafe", "Fuel Station", "Pharmacy", "Bookstore", "Taxi", "Snacks"]
        batch = [
            _txn(
                user,
                round(random.uniform(200, 900), 2),
                merchants[i],
                CHENNAI,
                now - timedelta(seconds=(5 - i) * 40),
            )
            for i in range(6)
        ]
    else:  # impossible_travel
        batch = [
            _txn(user, 1800, "Chennai Cafe", CHENNAI, now - timedelta(minutes=20)),
            _txn(user, 42000, "London Electronics", LONDON, now),
        ]

    flags = 0
    for data in batch:  # oldest first, so history builds up in order
        _, flag = process_transaction(db, data, background)
        if flag:
            flags += 1
    return SimulateOut(created=len(batch), flags=flags)


@router.delete("/demo/reset")
def reset_demo(db: Session = Depends(get_db)):
    crud.reset_all(db)
    return {"status": "ok"}
