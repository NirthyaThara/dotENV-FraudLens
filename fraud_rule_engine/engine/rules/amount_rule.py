from ..base import FraudRule
from ..models import EvaluationContext, RuleResult
from ..registry import register_rule
from ..utils import median_abs_deviation, median_decimal, robust_amount_score

@register_rule
class AmountAnomalyRule(FraudRule):
    name = "amount_anomaly"
    def evaluate(self, context):
        amounts = context.user_amounts()
        baseline = median_decimal(amounts)
        mad = median_abs_deviation(amounts, baseline) if baseline else 0
        score, reason = robust_amount_score(context.current.amount, baseline, mad)
        return RuleResult(
            rule_name=self.name, triggered=score > 0, score=score,
            severity="HIGH" if score >= 20 else "MEDIUM" if score else "NONE",
            reason=reason or None,
            metadata={"historical_transactions": len(amounts),
                      "median_amount": str(baseline) if baseline else None},
        )
