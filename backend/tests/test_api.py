import os

os.environ["DATABASE_URL"] = "sqlite:///./test_fraud.db"  # before importing the app

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import services  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)

FAKE_HIGH = {
    "risk_score": 95,
    "risk_level": "HIGH",
    "flagged": True,
    "reasons": [
        {"rule": "velocity", "score": 30, "message": "6 transactions in 5 minutes"},
        {"rule": "impossible_location", "score": 65, "message": "Chennai to London in 20 min"},
    ],
}
FAKE_CLEAN = {"risk_score": 0, "risk_level": "LOW", "flagged": False, "reasons": []}


def make_txn(**overrides):
    base = {
        "user_id": "U1001",
        "amount": 4500,
        "merchant": "Electronics Hub",
        "lat": 13.0827,
        "lon": 80.2707,
        "city": "Chennai",
        "country": "IN",
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def clean_db():
    client.delete("/demo/reset")
    yield


@pytest.fixture
def force_flag(monkeypatch):
    monkeypatch.setattr(services, "evaluate", lambda t, h: FAKE_HIGH)
    monkeypatch.setattr(services, "send_alert_task", lambda flag_id: None)


@pytest.fixture
def force_clean(monkeypatch):
    monkeypatch.setattr(services, "evaluate", lambda t, h: FAKE_CLEAN)


def test_normal_transaction_not_flagged(force_clean):
    r = client.post("/transactions", json=make_txn())
    assert r.status_code == 201
    body = r.json()
    assert body["flag"] is None
    assert body["transaction"]["id"] > 0
    assert body["transaction"]["timestamp"].endswith("Z")


def test_flagged_transaction_creates_flag(force_flag):
    r = client.post("/transactions", json=make_txn(amount=90000))
    assert r.status_code == 201
    flag = r.json()["flag"]
    assert flag["risk_level"] == "HIGH"
    assert flag["risk_score"] == 95
    assert flag["review_status"] == "PENDING"
    assert len(flag["reasons"]) == 2
    assert flag["transaction"]["amount"] == 90000


def test_list_flags_with_filters(force_flag):
    client.post("/transactions", json=make_txn())
    r = client.get("/flags?status=PENDING&level=HIGH")
    assert r.json()["total"] == 1
    r = client.get("/flags?status=CLEARED")
    assert r.json()["total"] == 0
    r = client.get("/flags?user_id=U1001")
    assert r.json()["total"] == 1


def test_review_then_clear_then_conflict(force_flag):
    flag_id = client.post("/transactions", json=make_txn()).json()["flag"]["id"]

    r = client.patch(f"/flags/{flag_id}/review", json={"comment": "Called customer"})
    assert r.status_code == 200
    assert r.json()["review_status"] == "REVIEWED"
    assert r.json()["reviewed_at"].endswith("Z")
    assert r.json()["review_comment"] == "Called customer"

    r = client.patch(f"/flags/{flag_id}/clear")
    assert r.status_code == 200
    assert r.json()["review_status"] == "CLEARED"

    r = client.patch(f"/flags/{flag_id}/review")
    assert r.status_code == 409
    assert "detail" in r.json()


def test_missing_flag_returns_404():
    r = client.get("/flags/99999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Flag not found"}


def test_validation_errors_are_clean_strings():
    r = client.post("/transactions", json=make_txn(amount=-5))
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], str)

    r = client.post("/transactions", json=make_txn(lat=95))
    assert r.status_code == 422


def test_stats(force_flag):
    client.post("/transactions", json=make_txn())
    s = client.get("/stats").json()
    assert s["total_transactions"] == 1
    assert s["total_flags"] == 1
    assert s["flag_rate"] == 100.0
    assert s["by_level"]["HIGH"] == 1
    assert s["by_rule"]["velocity"] == 1


def test_simulator_runs():
    r = client.post("/simulate/velocity")
    assert r.status_code == 200
    assert r.json()["created"] == 6
    assert client.post("/simulate/nonsense").status_code == 422
