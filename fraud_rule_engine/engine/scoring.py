from collections.abc import Iterable
from .config import DEFAULT_CONFIG, ScoringConfig
from .models import FraudAssessment, RiskLevel, RuleResult

def calculate_assessment(results: Iterable[RuleResult], config: ScoringConfig = DEFAULT_CONFIG):
    triggered = [r for r in results if r.triggered and r.score > 0]
    score = sum(r.score for r in triggered)
    if len(triggered) >= 3:
        score += config.corroboration_bonus_3
    elif len(triggered) >= 2:
        score += config.corroboration_bonus_2
    score = min(config.max_score, max(0, score))
    level = RiskLevel.HIGH if score >= config.high_threshold else (
        RiskLevel.MEDIUM if score >= config.medium_threshold else RiskLevel.LOW
    )
    return FraudAssessment(
        risk_score=int(round(score)),
        risk_level=level,
        is_flagged=score >= config.flag_threshold,
        reasons=[r.reason for r in triggered if r.reason],
        triggered_rules=triggered,
    )
