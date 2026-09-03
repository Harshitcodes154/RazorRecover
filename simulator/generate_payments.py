import random
from typing import List


FAILURE_REASONS = [
    "insufficient_funds",
    "expired_card",
    "payment_declined",
    "network_timeout",
]


def generate_payments(count: int = 1000) -> List[dict]:
    payments = []

    for i in range(1, count + 1):

        amount = random.choice([
            499, 999, 1499, 2499,
            4999, 9999, 14999, 24999
        ])

        status = random.choices(
            ["success", "failed"],
            weights=[70, 30]
        )[0]

        failure_reason = None

        if status == "failed":
            failure_reason = random.choice(FAILURE_REASONS)

        payment_type = random.choice([
            "payment",
            "subscription",
            "checkout"
        ])

        payments.append({
            "transaction_id": f"TXN_{i:05d}",
            "customer_id": f"CUS_{random.randint(1000, 9999)}",
            "amount": amount,
            "status": status,
            "failure_reason": failure_reason,
            "previous_successful_payments": random.randint(0, 20),
            "retry_count": random.randint(0, 3),
            "payment_type": payment_type
        })

    return payments