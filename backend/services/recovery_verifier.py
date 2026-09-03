from datetime import datetime


def verify_recovery(payment):

    verified_at = datetime.utcnow().isoformat()

    # ========================================================
    # PAYMENT RECOVERED
    # ========================================================

    if payment.status == "success":

        return {
            "recovered": True,
            "amount_recovered": float(payment.amount),
            "status": "RECOVERED",
            "transaction_id": payment.transaction_id,
            "verification_source": "payment_status",
            "verified_at": verified_at
        }

    # ========================================================
    # PAYMENT NOT RECOVERED
    # ========================================================

    return {
        "recovered": False,
        "amount_recovered": 0,
        "status": "NOT_RECOVERED",
        "transaction_id": payment.transaction_id,
        "verification_source": "payment_status",
        "verified_at": verified_at
    }