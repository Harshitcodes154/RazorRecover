from backend.models.payment import Payment


def analyze_root_cause(payment: Payment):

    reason = (payment.failure_reason or "").lower()

    if "insufficient" in reason:
        return {
            "root_cause": "INSUFFICIENT_FUNDS",
            "category": "CUSTOMER_SIDE",
            "confidence": 0.92,
            "recommended_approach": "Delayed retry after customer balance replenishment"
        }

    if "expired" in reason:
        return {
            "root_cause": "EXPIRED_PAYMENT_METHOD",
            "category": "CUSTOMER_SIDE",
            "confidence": 0.95,
            "recommended_approach": "Request updated payment method"
        }

    if "network" in reason or "timeout" in reason:
        return {
            "root_cause": "TEMPORARY_PROCESSING_FAILURE",
            "category": "SYSTEM_SIDE",
            "confidence": 0.88,
            "recommended_approach": "Retry after short delay"
        }

    if "declined" in reason:
        return {
            "root_cause": "PAYMENT_DECLINED",
            "category": "PAYMENT_METHOD",
            "confidence": 0.85,
            "recommended_approach": "Suggest alternate payment method"
        }

    return {
        "root_cause": "UNKNOWN",
        "category": "UNKNOWN",
        "confidence": 0.50,
        "recommended_approach": "Escalate for further review"
    }