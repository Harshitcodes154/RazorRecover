from backend.models.payment import Payment


# ============================================================
# RECOVERY POLICY LIMITS
# ============================================================

MAX_RETRIES = 3
MAX_REMINDERS = 2
MAX_RECOVERY_WINDOW_HOURS = 72

MIN_AUTO_RECOVERY_AMOUNT = 100
MIN_RECOVERY_SCORE = 40


# ============================================================
# RECOVERY GUARDRAIL
# ============================================================

def validate_recovery_action(
    payment: Payment,
    action: str,
    risk_score: int
):

    # --------------------------------------------------------
    # 1. PAYMENT ALREADY RECOVERED
    # --------------------------------------------------------

    if payment.status == "success":

        return {
            "allowed": False,
            "final_action": "STOP",
            "reason": "Payment already successful",
            "policy_status": "STOPPED"
        }

    # --------------------------------------------------------
    # 2. RETRY LIMIT
    # --------------------------------------------------------

    retry_count = int(
        getattr(payment, "retry_count", 0) or 0
    )

    if retry_count >= MAX_RETRIES:

        return {
            "allowed": False,
            "final_action": "ESCALATE",
            "reason": (
                f"Maximum retry limit of "
                f"{MAX_RETRIES} reached"
            ),
            "policy_status": "ESCALATED"
        }

    # --------------------------------------------------------
    # 3. RECOVERY SCORE THRESHOLD
    # --------------------------------------------------------

    if risk_score < MIN_RECOVERY_SCORE:

        return {
            "allowed": False,
            "final_action": "ESCALATE",
            "reason": (
                "Recovery probability below "
                "policy threshold"
            ),
            "policy_status": "ESCALATED"
        }

    # --------------------------------------------------------
    # 4. LOW-VALUE TRANSACTION
    # --------------------------------------------------------

    amount = float(
        getattr(payment, "amount", 0) or 0
    )

    if amount < MIN_AUTO_RECOVERY_AMOUNT:

        return {
            "allowed": False,
            "final_action": "STOP",
            "reason": (
                "Transaction below automated "
                "recovery threshold"
            ),
            "policy_status": "STOPPED"
        }

    # --------------------------------------------------------
    # 5. VALIDATE ACTION
    # --------------------------------------------------------

    allowed_actions = {
        "SCHEDULE_RETRY",
        "REQUEST_PAYMENT_METHOD_UPDATE",
        "ALTERNATIVE_PAYMENT_METHOD",
        "ESCALATE_TO_SUPPORT",
        "NO_ACTION"
    }

    if action not in allowed_actions:

        return {
            "allowed": False,
            "final_action": "ESCALATE",
            "reason": "Invalid recovery action",
            "policy_status": "ESCALATED"
        }

    # --------------------------------------------------------
    # 6. EXPLICIT ESCALATION
    # --------------------------------------------------------

    if action == "ESCALATE_TO_SUPPORT":

        return {
            "allowed": False,
            "final_action": "ESCALATE",
            "reason": "AI requested human support escalation",
            "policy_status": "ESCALATED"
        }

    # --------------------------------------------------------
    # 7. NO ACTION
    # --------------------------------------------------------

    if action == "NO_ACTION":

        return {
            "allowed": False,
            "final_action": "STOP",
            "reason": "No recovery action required",
            "policy_status": "STOPPED"
        }

    # --------------------------------------------------------
    # 8. APPROVED
    # --------------------------------------------------------

    return {
        "allowed": True,
        "final_action": action,
        "reason": (
            "Action complies with merchant "
            "recovery policy"
        ),
        "policy_status": "APPROVED",

        # Policy metadata for auditability
        "limits": {
            "max_retries": MAX_RETRIES,
            "max_reminders": MAX_REMINDERS,
            "max_recovery_window_hours":
                MAX_RECOVERY_WINDOW_HOURS,
            "min_auto_recovery_amount":
                MIN_AUTO_RECOVERY_AMOUNT,
            "min_recovery_score":
                MIN_RECOVERY_SCORE
        }
    }