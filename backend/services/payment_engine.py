import uuid

from backend.models.payment import Payment


payments_db = {}


def create_test_payment(
    customer_id: str,
    amount: float,
    failure_reason: str | None,
    payment_type: str
):

    transaction_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"

    status = "failed" if failure_reason else "success"

    payment = Payment(
        transaction_id=transaction_id,
        customer_id=customer_id,
        amount=amount,
        status=status,
        failure_reason=failure_reason,
        previous_successful_payments=5,
        retry_count=0,
        payment_type=payment_type
    )

    payments_db[transaction_id] = payment

    return payment


def get_payment(transaction_id: str):

    return payments_db.get(transaction_id)


def retry_payment(transaction_id: str):

    payment = payments_db.get(transaction_id)

    if payment is None:
        return None

    payment.retry_count += 1

    # Demo recovery simulation
    # First retry succeeds for recoverable failures
    if payment.failure_reason in [
        "insufficient_funds",
        "network_timeout"
    ]:
        payment.status = "success"
        payment.failure_reason = None

    elif payment.failure_reason == "expired_card":
        payment.status = "failed"

    elif payment.failure_reason == "payment_declined":
        payment.status = "failed"

    return payment