from engine.base import FraudRule
from engine.models import EvaluationContext, RuleResult
from engine.registry import register_rule, get_rule_classes

def test_new_rule_registration():
    class DemoRule(FraudRule):
        name = "demo_extension_rule"
        def evaluate(self, context: EvaluationContext) -> RuleResult:
            return RuleResult(rule_name=self.name,triggered=True,score=7,reason="demo")
    register_rule(DemoRule)
    assert "demo_extension_rule" in {r.name for r in get_rule_classes()}
