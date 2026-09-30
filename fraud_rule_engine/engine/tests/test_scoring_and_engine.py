from engine import evaluate
from engine.models import RiskLevel, RuleResult
from engine.scoring import calculate_assessment

def test_scoring_low():
    r = calculate_assessment([RuleResult(rule_name="merchant",triggered=True,score=6,reason="new")])
    assert r.risk_level == RiskLevel.LOW and not r.is_flagged

def test_scoring_high():
    r = calculate_assessment([
        RuleResult(rule_name="amount",triggered=True,score=25,reason="large"),
        RuleResult(rule_name="location",triggered=True,score=30,reason="travel"),
        RuleResult(rule_name="velocity",triggered=True,score=20,reason="fast"),
    ])
    assert r.risk_level == RiskLevel.HIGH and r.is_flagged and r.risk_score <= 100

def test_full_engine(make_tx):
    history = [
        make_tx("E1",amount="500",merchant="Amazon",minutes_ago=10000),
        make_tx("E2",amount="600",merchant="Amazon",minutes_ago=9000),
        make_tx("E3",amount="700",merchant="Amazon",minutes_ago=8000),
    ]
    result = evaluate(make_tx("E4",amount="10000",merchant="Unknown"),history)
    assert 0 <= result.risk_score <= 100
    assert result.risk_level in RiskLevel
    assert result.reasons
