from ..base import FraudRule
from ..models import EvaluationContext, RuleResult
from ..registry import register_rule
from ..utils import haversine_km

@register_rule
class LocationRule(FraudRule):
    name = "location_anomaly"
    def evaluate(self, context):
        current, previous = context.current, context.previous_transaction()
        if previous is None:
            return RuleResult(rule_name=self.name)
        if (current.country and previous.country and
            current.country.lower() != previous.country.lower() and
            None in (current.lat, current.lon, previous.lat, previous.lon)):
            return RuleResult(rule_name=self.name, triggered=True, score=6,
                              severity="LOW",
                              reason="Transaction occurred in a new country for this user")
        if None in (current.lat, current.lon, previous.lat, previous.lon):
            return RuleResult(rule_name=self.name)
        distance = haversine_km(previous.lat, previous.lon, current.lat, current.lon)
        hours = (current.transaction_time - previous.transaction_time).total_seconds()/3600
        if hours <= 0 or distance < 500:
            return RuleResult(rule_name=self.name)
        speed = distance / hours
        if speed >= 1200 and hours <= 2:
            return RuleResult(rule_name=self.name, triggered=True, score=30, severity="HIGH",
                              reason="Location change implies an implausibly high travel speed",
                              metadata={"distance_km": round(distance,2),
                                        "elapsed_hours": round(hours,3),
                                        "required_speed_kmh": round(speed,2)})
        if speed >= 900 and hours <= 1:
            return RuleResult(rule_name=self.name, triggered=True, score=22, severity="HIGH",
                              reason="Rapid location change is inconsistent with normal travel time",
                              metadata={"distance_km": round(distance,2),
                                        "elapsed_hours": round(hours,3),
                                        "required_speed_kmh": round(speed,2)})
        return RuleResult(rule_name=self.name)
