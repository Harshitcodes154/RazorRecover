from datetime import datetime


def execute_recovery_action(payment, guardrail):

    timestamp = datetime.utcnow().isoformat()

    # ========================================================
    # POLICY BLOCK
    # ========================================================

    if not guardrail["allowed"]:

        return {
            "executed": False,
            "action": guardrail["final_action"],
            "status": (
                guardrail.get(
                    "policy_status",
                    "BLOCKED"
                )
            ),
            "message": guardrail["reason"],
            "timestamp": timestamp
        }

    action = guardrail["final_action"]

    # ========================================================
    # SCHEDULE RETRY
    # ========================================================

    if action == "SCHEDULE_RETRY":

        return {
            "executed": True,
            "action": action,
            "status": "SCHEDULED",
            "delay_hours": 6,
            "message": (
                "Payment retry scheduled for "
                "6 hours later."
            ),
            "timestamp": timestamp
        }

    # ========================================================
    # PAYMENT METHOD UPDATE
    # ========================================================

    if action == "REQUEST_PAYMENT_METHOD_UPDATE":

        return {
            "executed": True,
            "action": action,
            "status": "CUSTOMER_ACTION_REQUIRED",
            "message": (
                "Customer must update the payment "
                "method before recovery can continue."
            ),
            "customer_action_required": True,
            "timestamp": timestamp
        }

    # ========================================================
    # ALTERNATIVE PAYMENT METHOD
    # ========================================================

    if action == "ALTERNATIVE_PAYMENT_METHOD":

        return {
            "executed": True,
            "action": action,
            "status": "ALTERNATIVE_METHOD_REQUESTED",
            "message": (
                "Customer should use an alternative "
                "payment method."
            ),
            "customer_action_required": True,
            "timestamp": timestamp
        }

    # ========================================================
    # ESCALATE TO SUPPORT
    # ========================================================

    if action == "ESCALATE_TO_SUPPORT":

        return {
            "executed": True,
            "action": action,
            "status": "ESCALATED",
            "message": (
                "Recovery case escalated to merchant "
                "support."
            ),
            "escalation_required": True,
            "timestamp": timestamp
        }

    # ========================================================
    # NO ACTION
    # ========================================================

    if action == "NO_ACTION":

        return {
            "executed": False,
            "action": action,
            "status": "STOPPED",
            "message": (
                "No recovery action required."
            ),
            "timestamp": timestamp
        }

    # ========================================================
    # SAFETY FALLBACK
    # ========================================================

    return {
        "executed": False,
        "action": action,
        "status": "UNKNOWN_ACTION",
        "message": (
            "Unsupported recovery action. "
            "Execution blocked for safety."
        ),
        "timestamp": timestamp
    }