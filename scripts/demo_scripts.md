# FraudLens Demo

## 1. Start Backend

Run:

uvicorn app.main:app --reload

from the backend directory.

## 2. Generate Demo Data

Run:

python scripts/generate_transactions.py

## 3. Open Reviewer Console

Show:
- Total transactions
- Fraud flags
- Risk levels
- Triggered rules

## 4. Demonstrate Fraud Detection

Show the impossible-travel scenario:

Chennai → London within 20 minutes.

Explain that the rule engine calculates the geographical distance and determines that the required travel speed is impossible.

## 5. Show HIGH Risk Flag

Show:
- Risk score
- Risk level
- Triggered rule
- Transaction information
- Review status

## 6. Show AWS Notification

Open the received SNS email and show the High Risk Fraud Alert.

## 7. Review Transaction

Click "Reviewed".

Show the status changing:

PENDING → REVIEWED

## 8. Clear Transaction

Demonstrate that the reviewer can also mark a transaction as CLEARED.

## 9. Extensibility

Explain:

"Each fraud rule is an independent module. New rules can be added without modifying the core rule engine."