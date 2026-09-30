from datetime import datetime, timedelta
from decimal import Decimal
from engine import evaluate
from engine.models import Transaction

BASE = datetime(2026,1,1,12,0)

def tx(ref, amount, merchant, city, lat, lon, minutes_ago):
    return Transaction(
        transaction_ref=ref,user_id="U001",amount=Decimal(amount),currency="INR",
        merchant=merchant,city=city,country="India",lat=lat,lon=lon,
        transaction_time=BASE-timedelta(minutes=minutes_ago),
    )

history = [
    tx("H1","500","Amazon","Chennai",13.0827,80.2707,10000),
    tx("H2","600","Amazon","Chennai",13.0827,80.2707,9000),
    tx("H3","700","Amazon","Chennai",13.0827,80.2707,8000),
    tx("H4","550","Amazon","Chennai",13.0827,80.2707,7000),
    tx("H5","650","Amazon","Chennai",13.0827,80.2707,6000),
]

def show(title, transaction):
    result = evaluate(transaction, history)
    print("\n"+"="*60)
    print(title)
    print("="*60)
    print(f"Risk score : {result.risk_score}/100")
    print(f"Risk level : {result.risk_level.value}")
    print(f"Flagged    : {result.is_flagged}")
    print("\nTriggered rules:")
    for r in result.triggered_rules:
        print(f"  - {r.rule_name}: +{r.score:g}")
    if not result.triggered_rules:
        print("  None")
    print("\nReasons:")
    for reason in result.reasons:
        print(f"  - {reason}")
    if not result.reasons:
        print("  None")

show("NORMAL TRANSACTION", tx("DEMO-NORMAL","600","Amazon","Chennai",13.0827,80.2707,0))
show("SUSPICIOUS TRANSACTION", tx("DEMO-SUSPICIOUS","10000","Unknown Merchant","Mumbai",19.0760,72.8777,0))
print("\nDemo complete.")
