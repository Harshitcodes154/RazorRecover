from backend.models.payment import Payment


def choose_recovery_strategy(payment: Payment, risk_score: int):

    # Payment already successful
    if payment.status == "success":
        return {
            "action": "STOP",
            "reason": "Payment already successful"
        }

    # Too many retries
    if payment.retry_count >= 3:
        return {
            "action": "ESCALATE",
            "reason": "Maximum retry limit reached"
        }

    # High-value payment
    if payment.amount >= 10000 and risk_score >= 60:
        return {
            "action": "GENERATE_PAYMENT_LINK",
            "reason": "High-value transaction with reasonable recovery probability"
        }

    # High recovery potential
    if risk_score >= 60:
        return {
            "action": "SCHEDULE_RETRY",
            "delay_hours": 6,
            "reason": "High recovery potential; delayed retry recommended"
        }

    # Medium risk
    if risk_score >= 40:
        return {
            "action": "SEND_REMINDER",
            "reason": "Customer reminder recommended before another retry"
        }

    # Low probability
    return {
        "action": "ESCALATE",
        "reason": "Low recovery probability"
    }