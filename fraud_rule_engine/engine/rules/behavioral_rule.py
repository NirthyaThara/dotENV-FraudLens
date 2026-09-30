from statistics import median
from ..base import FraudRule
from ..models import EvaluationContext, RuleResult
from ..registry import register_rule
from ..utils import circular_hour_distance

@register_rule
class BehavioralRule(FraudRule):
    name = "behavioral_anomaly"
    def evaluate(self, context):
        prior = context.prior
        if len(prior) < 5:
            return RuleResult(rule_name=self.name)
        signals = []
        amount_median = median(float(tx.amount) for tx in prior)
        if amount_median and float(context.current.amount) >= amount_median * 3:
            signals.append("amount")
        if context.current.merchant.strip().lower() not in context.known_merchants():
            signals.append("merchant")
        hours = [tx.transaction_time.hour + tx.transaction_time.minute/60 for tx in prior]
        current_hour = context.current.transaction_time.hour + context.current.transaction_time.minute/60
        if min(circular_hour_distance(current_hour, h) for h in hours) >= 4:
            signals.append("time")
        if len(signals) >= 3:
            return RuleResult(rule_name=self.name, triggered=True, score=15, severity="MEDIUM",
                              reason="Multiple independent behavioral patterns deviate from the user's history",
                              metadata={"signals": signals})
        if len(signals) == 2:
            return RuleResult(rule_name=self.name, triggered=True, score=10, severity="MEDIUM",
                              reason="Two independent behavioral patterns deviate from the user's history",
                              metadata={"signals": signals})
        return RuleResult(rule_name=self.name)
