"""
Glue between your backend and your teammates' modules.

Repo layout expected:
    repo/
      engine/          <- Member 1: must expose  evaluate(transaction, history)
      notifications/   <- Member 4: must expose  send_alert(flag)
      backend/         <- you

Until they deliver, the fallbacks below keep everything working.
"""
import logging
import sys
from pathlib import Path

logger = logging.getLogger("integrations")

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------- Fraud engine (Member 1) ----------
def stub_evaluate(transaction: dict, history: list) -> dict:
    """Simple stand-in so you are never blocked. Replaced automatically."""
    reasons = []

    if transaction["amount"] > 50000:
        reasons.append(
            {
                "rule": "amount",
                "score": 40,
                "message": f"Amount {transaction['amount']:.0f} is above 50000",
            }
        )

    ts = transaction["timestamp"]
    recent = [h for h in history if (ts - h["timestamp"]).total_seconds() <= 300]
    if len(recent) >= 4:
        reasons.append(
            {
                "rule": "velocity",
                "score": 30,
                "message": f"{len(recent) + 1} transactions in 5 minutes",
            }
        )

    score = min(sum(int(r["score"]) for r in reasons), 100)  # type: ignore
    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return {
        "risk_score": score,
        "risk_level": level,
        "flagged": score >= 40,
        "reasons": reasons,
    }


try:
    from engine import evaluate  # type: ignore

    logger.info("Using Member 1's fraud engine")
except ImportError as exc:
    logger.warning("Real engine not found (%s). Using stub engine.", exc)
    evaluate = stub_evaluate


# ---------- Notifications (Member 4) ----------
def stub_send_alert(flag: dict) -> None:
    logger.warning(
        "[MOCK ALERT] HIGH risk flag #%s for transaction #%s (score %s)",
        flag["id"],
        flag["transaction_id"],
        flag["risk_score"],
    )


try:
    from notifications import send_alert  # type: ignore

    logger.info("Using Member 4's notification module")
except ImportError as exc:
    logger.warning("Real notifier not found (%s). Using mock alerts.", exc)
    send_alert = stub_send_alert
