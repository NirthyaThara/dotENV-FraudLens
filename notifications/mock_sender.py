def send_mock_alert(flag: dict):
    transaction = flag.get("transaction", {})

    print("\n" + "=" * 50)
    print("FRAUD ALERT")
    print("=" * 50)

    print(f"Flag ID       : {flag.get('id')}")
    print(f"Transaction ID: {flag.get('transaction_id')}")
    print(f"User ID       : {transaction.get('user_id')}")
    print(f"Amount        : {transaction.get('amount')} {transaction.get('currency')}")
    print(f"Merchant      : {transaction.get('merchant')}")
    print(f"Risk Score    : {flag.get('risk_score')}")
    print(f"Risk Level    : {flag.get('risk_level')}")

    print("\nTriggered Rules:")

    for reason in flag.get("reasons", []):
        print(
            f"- {reason.get('rule')}: "
            f"{reason.get('message')} "
            f"(+{reason.get('score')})"
        )

    print("=" * 50 + "\n")

    return True