from ..base import FraudRule
from ..models import EvaluationContext, RuleResult
from ..registry import register_rule

@register_rule
class BurstRule(FraudRule):
    name = "burst_pattern"
    def evaluate(self, context):
        count = len(context.within_minutes(2))
        if count >= 5:
            score, reason = 18, "Strong transaction burst detected within two minutes"
        elif count >= 3:
            score, reason = 12, "Rapid transaction burst detected within two minutes"
        else:
            score, reason = 0, None
        return RuleResult(rule_name=self.name, triggered=score > 0, score=score,
                          severity="HIGH" if score >= 18 else "MEDIUM" if score else "NONE",
                          reason=reason, metadata={"transactions_2m": count})
