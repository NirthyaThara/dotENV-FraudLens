import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "key")

HEADERS = {
    "X-API-Key": API_KEY
}


def run_scenario(scenario):
    url = f"{BASE_URL}/simulate/{scenario}"

    try:
        response = requests.post(
            url,
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()
        result = response.json()

        print(
            f"[OK] {scenario}: "
            f"{result['created']} transactions created, "
            f"{result['flags']} flags generated"
        )

    except Exception as e:
        print(f"[ERROR] {scenario}: {e}")

def reset_demo():
    try:
        response = requests.delete(
            f"{BASE_URL}/demo/reset",
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()
        print("[OK] Demo database reset")

    except Exception as e:
        print(f"[ERROR] Reset failed: {e}")

if __name__ == "__main__":
    print("\n=== FraudLens Demo Data Generator ===\n")

    reset_demo()

    run_scenario("normal")
    run_scenario("velocity")
    run_scenario("impossible_travel")

    print("\nDemo data generation complete.")