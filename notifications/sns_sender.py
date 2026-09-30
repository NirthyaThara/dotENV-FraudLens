import os
import boto3
from dotenv import load_dotenv
load_dotenv(override=True)

def send_sns_alert(flag: dict):
    region = os.getenv("AWS_REGION", "").strip()
    topic_arn = os.getenv("SNS_TOPIC_ARN", "").strip()

    # print("Region:", repr(region))
    # print("Topic ARN:", repr(topic_arn))
    # print("ARN parts:", topic_arn.split(":"))

    transaction = flag.get("transaction", {})

    reasons_text = "\n".join(
        [
            f"- {reason.get('rule')}: {reason.get('message')} (+{reason.get('score')})"
            for reason in flag.get("reasons", [])
        ]
    )

    message = f"""
HIGH RISK FRAUD ALERT

Flag ID: {flag.get('id')}
Transaction ID: {flag.get('transaction_id')}

User ID: {transaction.get('user_id')}
Amount: {transaction.get('amount')} {transaction.get('currency')}
Merchant: {transaction.get('merchant')}

Risk Score: {flag.get('risk_score')}
Risk Level: {flag.get('risk_level')}

Triggered Rules:
{reasons_text}
"""

    sns = boto3.client(
        "sns",
        region_name=region
    )

    response = sns.publish(
        TopicArn=topic_arn,
        Subject="High Risk Fraud Alert",
        Message=message
    )

    print("SNS alert sent successfully")
    return response