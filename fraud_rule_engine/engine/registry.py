from typing import TypeVar
from .base import FraudRule

RuleType = TypeVar("RuleType", bound=type[FraudRule])
_RULES: dict[str, type[FraudRule]] = {}

def register_rule(rule_cls: RuleType) -> RuleType:
    if not rule_cls.name or rule_cls.name == "unnamed_rule":
        raise ValueError("Every fraud rule must define a unique name")
    if rule_cls.name in _RULES:
        raise ValueError(f"Duplicate fraud rule: {rule_cls.name}")
    _RULES[rule_cls.name] = rule_cls
    return rule_cls

def get_rule_classes() -> tuple[type[FraudRule], ...]:
    return tuple(_RULES.values())

def build_rules() -> list[FraudRule]:
    return [rule_cls() for rule_cls in get_rule_classes()]
