from ..base import FraudRule
from ..models import EvaluationContext, RuleResult
from ..registry import register_rule

@register_rule
class MerchantRule(FraudRule):
    name = "merchant_anomaly"
    def evaluate(self, context):
        known = context.known_merchants()
        merchant = context.current.merchant.strip().lower()
        if known and merchant not in known:
            return RuleResult(rule_name=self.name, triggered=True, score=6, severity="LOW",
                              reason="Merchant is new or unusual for this user",
                              metadata={"known_merchant_count": len(known)})
        return RuleResult(rule_name=self.name)
