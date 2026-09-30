# Backend (FastAPI + SQLite)

## Run
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   |  source venv/bin/activate  (Mac/Linux)
pip install -r requirements.txt
copy .env.example .env         # Windows   |  cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Swagger docs (share with Member 3): http://localhost:8000/docs
- Tests: `python -m pytest -q`

## Quick check
```bash
curl -X POST http://localhost:8000/simulate/velocity
curl "http://localhost:8000/flags?status=PENDING"
curl http://localhost:8000/stats
curl -X PATCH http://localhost:8000/flags/1/review -H "Content-Type: application/json" -d '{"comment":"checked"}'
curl -X PATCH http://localhost:8000/flags/1/clear
curl -X DELETE http://localhost:8000/demo/reset
```

## Plugging in teammates
- Member 1: put the engine in `repo/engine/` and expose `evaluate(transaction: dict, history: list[dict])`.
  `timestamp` inside those dicts is a Python `datetime` (naive UTC).
- Member 4: put the notifier in `repo/notifications/` and expose `send_alert(flag: dict)`.
- Until they exist, `app/integrations.py` uses a stub engine and a mock alert.

## Review rules
PENDING -> REVIEWED or CLEARED, REVIEWED -> CLEARED. Anything else returns 409.
