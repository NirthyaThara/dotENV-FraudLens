from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Transaction(BaseModel):
    model_config = ConfigDict(frozen=True)
    transaction_ref: str
    user_id: str
    amount: Decimal = Field(gt=0)
    currency: str
    merchant: str
    lat: float | None = None
    lon: float | None = None
    city: str | None = None
    country: str | None = None
    transaction_time: datetime

class EvaluationContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    current: Transaction
    history: list[Transaction] = Field(default_factory=list)

    @property
    def prior(self) -> list[Transaction]:
        return [tx for tx in self.history if tx.transaction_time < self.current.transaction_time]

    def within_minutes(self, minutes: int) -> list[Transaction]:
        current_ts = self.current.transaction_time.timestamp()
        return [
            tx for tx in self.prior
            if 0 <= current_ts - tx.transaction_time.timestamp() <= minutes * 60
        ]

    def previous_transaction(self) -> Transaction | None:
        return max(self.prior, key=lambda tx: tx.transaction_time, default=None)

    def user_amounts(self) -> list[Decimal]:
        return [tx.amount for tx in self.prior]

    def known_merchants(self) -> set[str]:
        return {tx.merchant.strip().lower() for tx in self.prior if tx.merchant}

class RuleResult(BaseModel):
    rule_name: str
    triggered: bool = False
    score: float = Field(default=0, ge=0)
    severity: str = "NONE"
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class FraudAssessment(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    is_flagged: bool
    reasons: list[str] = Field(default_factory=list)
    triggered_rules: list[RuleResult] = Field(default_factory=list)
