from ..base import FraudRule
from ..models import EvaluationContext, RuleResult
from ..registry import register_rule

@register_rule
class TransactionPatternRule(FraudRule):
    name = "transaction_pattern"
    def evaluate(self, context):
        recent = context.within_minutes(10)
        matching = [tx for tx in recent if tx.amount == context.current.amount]
        if len(matching) >= 2:
            return RuleResult(rule_name=self.name, triggered=True, score=10, severity="MEDIUM",
                              reason="Repeated transactions with the same amount were detected in a short period",
                              metadata={"matching_recent_transactions": len(matching)})
        return RuleResult(rule_name=self.name)
