from backend.models.payment import Payment


def calculate_revenue_risk(payment: Payment):

    if payment.status == "success":
        return {
            "at_risk": False,
            "risk_score": 0,
            "reason": "Payment successful"
        }

    risk_score = 0

    # Failed payment
    if payment.status == "failed":
        risk_score += 40

    # Customer has payment history
    if payment.previous_successful_payments >= 5:
        risk_score += 20

    # Multiple retries indicate higher risk
    if payment.retry_count >= 2:
        risk_score += 20

    # High-value transaction
    if payment.amount >= 10000:
        risk_score += 10

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        level = "HIGH"
    elif risk_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "at_risk": True,
        "risk_score": risk_score,
        "risk_level": level,
        "amount_at_risk": payment.amount,
        "failure_reason": payment.failure_reason
    }