from backend.services.payment_engine import get_payment


def get_customer_payment_context(customer_id: str):

    from backend.services.payment_engine import payments_db

    customer_payments = [
        payment
        for payment in payments_db.values()
        if payment.customer_id == customer_id
    ]

    if not customer_payments:
        return {
            "customer_id": customer_id,
            "payments_found": 0,
            "payments": []
        }

    payments = []

    for payment in customer_payments:
        payments.append({
            "transaction_id": payment.transaction_id,
            "amount": payment.amount,
            "status": payment.status,
            "failure_reason": payment.failure_reason,
            "retry_count": payment.retry_count,
            "payment_type": payment.payment_type
        })

    return {
        "customer_id": customer_id,
        "payments_found": len(payments),
        "payments": payments
    }