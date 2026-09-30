"""
Glue between the backend and the fraud_rule_engine module.

Repo layout:
    dotENV-FraudLens/
      fraud_rule_engine/engine/   <- real fraud engine (Member 1)
      backend/                    <- this backend
      notifications/              <- alerts module (Member 4, optional)

The backend always calls:
    evaluate(transaction_dict, history_list_of_dicts) -> dict
    send_alert(flag_dict) -> None

This file translates between the backend's plain-dict format and the
engine's typed Pydantic models, so neither side needs to know about
the other's internals.
"""
import logging
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

logger = logging.getLogger("integrations")

# ── sys.path setup ─────────────────────────────────────────────────────────
# The engine lives in  <repo_root>/fraud_rule_engine/
# The backend lives in <repo_root>/backend/
# __file__ is backend/app/integrations.py  → parents[2] = repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_ROOT = REPO_ROOT / "fraud_rule_engine"

for p in (str(REPO_ROOT), str(ENGINE_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


# ── Adapter helpers ────────────────────────────────────────────────────────

def _to_engine_txn(d: dict) -> Any:
    """Convert a backend transaction dict into engine.models.Transaction."""
    from engine.models import Transaction as EngTxn  # local import after path setup
    return EngTxn(
        transaction_ref=str(d.get("id", "unknown")),
        user_id=d["user_id"],
        amount=Decimal(str(d["amount"])),
        currency=d.get("currency", "INR"),
        merchant=d.get("merchant", ""),
        lat=d.get("lat"),
        lon=d.get("lon"),
        city=d.get("city"),
        country=d.get("country"),
        transaction_time=d["timestamp"],
    )


def _to_backend_result(assessment: Any) -> dict:
    """Convert engine.models.FraudAssessment to the backend dict format.

    Backend expects:
        {
          "risk_score": int,
          "risk_level": "LOW" | "MEDIUM" | "HIGH",
          "flagged": bool,
          "reasons": [{"rule": str, "score": float, "message": str}, ...]
        }
    """
    reasons = []
    for rule_result in assessment.triggered_rules:
        reasons.append({
            "rule": rule_result.rule_name,
            "score": float(rule_result.score),
            "message": rule_result.reason or rule_result.rule_name,
        })

    return {
        "risk_score": assessment.risk_score,
        # RiskLevel is a str-enum so .value gives the plain string
        "risk_level": assessment.risk_level.value
            if hasattr(assessment.risk_level, "value")
            else str(assessment.risk_level),
        "flagged": assessment.is_flagged,
        "reasons": reasons,
    }


# ── Fraud engine ────────────────────────────────────────────────────────────

def stub_evaluate(transaction: dict, history: list) -> dict:
    """Fallback engine — used only when the real engine cannot be imported."""
    reasons = []

    if transaction["amount"] > 50000:
        reasons.append({
            "rule": "amount",
            "score": 40,
            "message": f"Amount {transaction['amount']:.0f} is above 50000",
        })

    ts = transaction["timestamp"]
    recent = [h for h in history if (ts - h["timestamp"]).total_seconds() <= 300]
    if len(recent) >= 4:
        reasons.append({
            "rule": "velocity",
            "score": 30,
            "message": f"{len(recent) + 1} transactions in 5 minutes",
        })

    score = min(sum(int(r["score"]) for r in reasons), 100)  # type: ignore
    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return {
        "risk_score": score,
        "risk_level": level,
        "flagged": score >= 40,
        "reasons": reasons,
    }


def _real_evaluate(transaction: dict, history: list) -> dict:
    """Adapter that calls the real engine and converts types on both sides."""
    from engine import evaluate as _eng_evaluate  # already on sys.path
    eng_txn = _to_engine_txn(transaction)
    eng_history = []
    for h in history:
        try:
            eng_history.append(_to_engine_txn(h))
        except Exception as exc:
            logger.warning("Skipping history entry due to conversion error: %s", exc)
    assessment = _eng_evaluate(eng_txn, eng_history)
    return _to_backend_result(assessment)


try:
    # Verify the import works at startup
    from engine import evaluate as _verify_import  # type: ignore  # noqa: F401
    evaluate = _real_evaluate
    logger.info("Connected to real fraud engine at %s", ENGINE_ROOT)
except ImportError as exc:
    logger.warning("Real engine not found (%s). Using stub engine.", exc)
    evaluate = stub_evaluate


# ── Notifications (Member 4) ────────────────────────────────────────────────

def stub_send_alert(flag: dict) -> None:
    logger.warning(
        "[MOCK ALERT] HIGH risk flag #%s for transaction #%s (score %s)",
        flag["id"],
        flag["transaction_id"],
        flag["risk_score"],
    )


try:
    from notifications import send_alert  # type: ignore
    logger.info("Using Member 4s notification module")
except ImportError as exc:
    logger.warning("Real notifier not found (%s). Using mock alerts.", exc)
    send_alert = stub_send_alert
