from notifications import send_alert

test_flag = {
    "id": 12,
    "transaction_id": 101,
    "risk_score": 95,
    "risk_level": "HIGH",
    "reasons": [
        {
            "rule": "velocity",
            "score": 30,
            "message": "6 transactions in 5 minutes"
        },
        {
            "rule": "amount",
            "score": 25,
            "message": "Amount is 8x the user's average"
        },
        {
            "rule": "impossible_location",
            "score": 40,
            "message": "Chennai to London in 20 minutes"
        }
    ],
    "transaction": {
        "id": 101,
        "user_id": "U1001",
        "amount": 48500.0,
        "currency": "INR",
        "merchant": "Electronics Hub"
    }
}

send_alert(test_flag)