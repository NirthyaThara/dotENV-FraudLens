from collections.abc import Iterable
from .base import FraudRule
from .context import build_context
from .models import FraudAssessment, Transaction
from .registry import build_rules
from .scoring import calculate_assessment

class FraudEngine:
    def __init__(self, rules: Iterable[FraudRule] | None = None):
        self.rules = list(rules) if rules is not None else build_rules()

    def evaluate(self, transaction: Transaction, history: list[Transaction]) -> FraudAssessment:
        context = build_context(transaction, history)
        return calculate_assessment(rule.evaluate(context) for rule in self.rules)
