from engine.models import EvaluationContext
from engine.rules.amount_rule import AmountAnomalyRule
from engine.rules.velocity_rule import VelocityRule
from engine.rules.burst_rule import BurstRule
from engine.rules.location_rule import LocationRule
from engine.rules.merchant_rule import MerchantRule
from engine.rules.behavioral_rule import BehavioralRule
from engine.rules.transaction_pattern_rule import TransactionPatternRule

def test_amount_rule(make_tx):
    history = [make_tx("A1",amount="500",minutes_ago=10000),make_tx("A2",amount="600",minutes_ago=9000),make_tx("A3",amount="700",minutes_ago=8000)]
    result = AmountAnomalyRule().evaluate(EvaluationContext(current=make_tx("A4",amount="10000"),history=history))
    assert result.triggered

def test_velocity_rule(make_tx):
    history = [make_tx(f"V{i}",minutes_ago=i*5+1) for i in range(6)]
    assert VelocityRule().evaluate(EvaluationContext(current=make_tx("V"),history=history)).triggered

def test_burst_rule(make_tx):
    history = [make_tx(f"B{i}",minutes_ago=i*0.5+0.1) for i in range(3)]
    assert BurstRule().evaluate(EvaluationContext(current=make_tx("B"),history=history)).triggered

def test_location_rule(make_tx):
    previous = make_tx("L1",lat=13.0827,lon=80.2707,minutes_ago=30)
    current = make_tx("L2",lat=19.0760,lon=72.8777,city="Mumbai")
    result = LocationRule().evaluate(EvaluationContext(current=current,history=[previous]))
    assert result.triggered and result.score >= 20

def test_merchant_rule(make_tx):
    history = [make_tx("M1",merchant="Amazon",minutes_ago=1000)]
    result = MerchantRule().evaluate(EvaluationContext(current=make_tx("M2",merchant="Unknown"),history=history))
    assert result.triggered and result.score < 10

def test_behavioral_rule(make_tx):
    history = [make_tx(f"BH{i}",amount="500",merchant="Amazon",minutes_ago=1000+i*100) for i in range(6)]
    current = make_tx("BH7",amount="5000",merchant="Unknown")
    result = BehavioralRule().evaluate(EvaluationContext(current=current,history=history))
    assert result.triggered

def test_transaction_pattern_rule(make_tx):
    history = [make_tx("P1",amount="1000",minutes_ago=2),make_tx("P2",amount="1000",minutes_ago=5)]
    current = make_tx("P3",amount="1000")
    assert TransactionPatternRule().evaluate(EvaluationContext(current=current,history=history)).triggered
