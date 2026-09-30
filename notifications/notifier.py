import os
from dotenv import load_dotenv

from .mock_sender import send_mock_alert
from .sns_sender import send_sns_alert

load_dotenv()


def send_alert(flag: dict):
    provider = os.getenv("NOTIFICATION_PROVIDER", "mock").lower()

    if provider == "mock":
        return send_mock_alert(flag)

    if provider == "sns":
        return send_sns_alert(flag)

    raise ValueError(
        f"Unsupported notification provider: {provider}"
    )