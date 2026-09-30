from datetime import datetime
from typing import Annotated, Dict, List, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    field_validator,
    model_validator,
)

from .utils import to_naive_utc, to_z, utcnow

RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
ReviewStatus = Literal["PENDING", "REVIEWED", "CLEARED"]

# Every datetime leaves the API as "2026-09-30T06:15:00Z"
UTCDatetime = Annotated[datetime, PlainSerializer(to_z, return_type=str)]


# ---------- Transactions ----------
class TransactionCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    amount: float = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    merchant: str = Field(min_length=1, max_length=120)
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    city: Optional[str] = Field(default=None, max_length=80)
    country: Optional[str] = Field(default=None, max_length=80)
    timestamp: datetime = Field(default_factory=utcnow)

    @field_validator("timestamp")
    @classmethod
    def _timestamp_to_utc(cls, v: datetime) -> datetime:
        return to_naive_utc(v)

    @field_validator("currency")
    @classmethod
    def _currency_upper(cls, v: str) -> str:
        return v.upper()

    @model_validator(mode="after")
    def _lat_lon_together(self):
        if (self.lat is None) != (self.lon is None):
            raise ValueError("lat and lon must be provided together")
        return self


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    amount: float
    currency: str
    merchant: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None
    timestamp: UTCDatetime


# ---------- Flags ----------
class ReasonOut(BaseModel):
    rule: str
    score: float
    message: str


class FlagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: int
    risk_score: int
    risk_level: RiskLevel
    reasons: List[ReasonOut]
    review_status: ReviewStatus
    reviewed_at: Optional[UTCDatetime] = None
    review_comment: Optional[str] = None
    created_at: UTCDatetime
    transaction: TransactionOut


class ReviewRequest(BaseModel):
    comment: Optional[str] = Field(default=None, max_length=500)


# ---------- Responses ----------
class TransactionWithFlag(BaseModel):
    transaction: TransactionOut
    flag: Optional[FlagOut] = None


class PagedTransactions(BaseModel):
    items: List[TransactionOut]
    total: int
    limit: int
    offset: int


class PagedFlags(BaseModel):
    items: List[FlagOut]
    total: int
    limit: int
    offset: int


class StatsOut(BaseModel):
    total_transactions: int
    total_flags: int
    flag_rate: float
    by_level: Dict[str, int]
    by_status: Dict[str, int]
    by_rule: Dict[str, int]
    false_positive_rate: float


class SimulateOut(BaseModel):
    created: int
    flags: int
