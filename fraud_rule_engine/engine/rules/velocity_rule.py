from ..base import FraudRule
from ..models import EvaluationContext, RuleResult
from ..registry import register_rule

@register_rule
class VelocityRule(FraudRule):
    name = "velocity"
    def evaluate(self, context):
        c30, c60 = len(context.within_minutes(30)), len(context.within_minutes(60))
        if c30 >= 6:
            score, reason = 20, "Unusually high transaction velocity in the last 30 minutes"
        elif c30 >= 4:
            score, reason = 14, "High transaction velocity in the last 30 minutes"
        elif c60 >= 6:
            score, reason = 10, "Multiple transactions detected in the last hour"
        else:
            score, reason = 0, None
        return RuleResult(rule_name=self.name, triggered=score > 0, score=score,
                          severity="HIGH" if score >= 20 else "MEDIUM" if score else "NONE",
                          reason=reason, metadata={"transactions_30m": c30, "transactions_60m": c60})
