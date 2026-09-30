from abc import ABC, abstractmethod
from .models import EvaluationContext, RuleResult

class FraudRule(ABC):
    name: str = "unnamed_rule"

    @abstractmethod
    def evaluate(self, context: EvaluationContext) -> RuleResult:
        raise NotImplementedError
