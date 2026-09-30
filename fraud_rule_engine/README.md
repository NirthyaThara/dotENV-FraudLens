# Fraud Rule Engine — Final Hackathon Submission

Pure-Python, extensible transaction fraud risk engine.

## Quick start
Python 3.11+ recommended.

```bash
pip install -r requirements.txt
pytest -q
python demo.py
```

The engine is independent of FastAPI, SQLite, AWS, and React.

## Integration

```python
from engine import evaluate
assessment = evaluate(transaction, history)
```

Result fields:
- risk_score: 0-100
- risk_level: LOW / MEDIUM / HIGH
- is_flagged
- reasons
- triggered_rules

## Architecture

The core engine does not contain rule-specific `if/else` logic. Each rule is a
separate class implementing `FraudRule` and returning `RuleResult`. Rules are
registered through `registry.py`; `engine.py` only orchestrates registered rules.
Adding a rule therefore does not require changing the core engine.

This is a risk-scoring system, not a guarantee of fraud detection. Thresholds
should be calibrated with labelled production data.
