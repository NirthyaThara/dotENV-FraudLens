from ..base import FraudRule
from ..models import EvaluationContext, RuleResult
from ..registry import register_rule
from ..utils import circular_hour_distance

@register_rule
class OddHoursRule(FraudRule):
    name = "odd_hours"
    def evaluate(self, context):
        prior = context.prior
        if len(prior) < 5:
            return RuleResult(rule_name=self.name)
        current_hour = context.current.transaction_time.hour + context.current.transaction_time.minute/60
        hours = [tx.transaction_time.hour + tx.transaction_time.minute/60 for tx in prior]
        nearest = min(circular_hour_distance(current_hour, h) for h in hours)
        if nearest >= 5:
            return RuleResult(rule_name=self.name, triggered=True, score=6, severity="LOW",
                              reason="Transaction time is unusual for this user's historical activity",
                              metadata={"minimum_hour_distance": round(nearest,2)})
        return RuleResult(rule_name=self.name)
