from collections.abc import Iterable, Sequence
from decimal import Decimal
from statistics import median
import math

def median_decimal(values: Iterable[Decimal]) -> Decimal | None:
    values = list(values)
    return Decimal(str(median([float(v) for v in values]))) if values else None

def median_abs_deviation(values: Sequence[Decimal], center: Decimal) -> Decimal:
    if not values:
        return Decimal("0")
    return Decimal(str(median([abs(float(v - center)) for v in values])))

def robust_amount_score(amount: Decimal, baseline: Decimal | None, mad: Decimal):
    if baseline is None or baseline <= 0:
        return 0.0, ""
    ratio = float(amount / baseline)
    if ratio < 2.5:
        return 0.0, ""
    robust_z = abs(float(amount - baseline)) / float(mad) if mad > 0 else 0
    if ratio >= 10 or robust_z >= 10:
        return 25.0, "Amount is exceptionally high compared with the user's history"
    if ratio >= 5 or robust_z >= 6:
        return 20.0, "Amount is substantially above the user's normal range"
    return 12.0, "Amount is noticeably above the user's normal range"

def haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * radius_km * math.asin(math.sqrt(min(1, a)))

def circular_hour_distance(a: float, b: float) -> float:
    d = abs(a-b) % 24
    return min(d, 24-d)
