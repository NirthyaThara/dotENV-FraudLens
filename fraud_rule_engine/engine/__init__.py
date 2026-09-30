from .engine import FraudEngine
from .models import EvaluationContext, FraudAssessment, RiskLevel, RuleResult, Transaction
from . import rules as _rules  # noqa: F401

_default_engine = FraudEngine()

def evaluate(transaction: Transaction, history: list[Transaction]) -> FraudAssessment:
    return _default_engine.evaluate(transaction, history)

__all__ = [
    "evaluate", "FraudEngine", "Transaction", "EvaluationContext",
    "RuleResult", "FraudAssessment", "RiskLevel",
]
