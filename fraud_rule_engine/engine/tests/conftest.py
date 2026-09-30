from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from engine.models import Transaction

@pytest.fixture
def make_tx():
    def _make(ref="TX", user="U1", amount="500", merchant="Amazon",
              city="Chennai", country="India", lat=13.0827, lon=80.2707, minutes_ago=0):
        return Transaction(
            transaction_ref=ref, user_id=user, amount=Decimal(amount), currency="INR",
            merchant=merchant, city=city, country=country, lat=lat, lon=lon,
            transaction_time=datetime(2026,1,1,12,0) - timedelta(minutes=minutes_ago),
        )
    return _make
