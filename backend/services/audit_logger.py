from datetime import datetime


def create_audit_log(
    payment,
    risk,
    root_cause,
    strategy,
    guardrail,
    execution,
    verification
):
    return {
        "transaction_id": payment.transaction_id,
        "timestamp": datetime.utcnow().isoformat(),

        "amount": payment.amount,

        "risk": {
            "score": risk.get("risk_score"),
            "level": risk.get("risk_level"),
            "at_risk": risk.get("at_risk")
        },

        "root_cause": {
            "cause": root_cause.get("root_cause"),
            "category": root_cause.get("category"),
            "confidence": root_cause.get("confidence")
        },

        "decision": {
            "recommended_action": strategy.get("action"),
            "reason": strategy.get("reason")
        },

        "guardrail": {
            "allowed": guardrail.get("allowed"),
            "final_action": guardrail.get("final_action"),
            "reason": guardrail.get("reason")
        },

        "execution": {
            "executed": execution.get("executed"),
            "status": execution.get("status")
        },

        "recovery": {
            "recovered": verification.get("recovered"),
            "amount_recovered": verification.get("amount_recovered"),
            "status": verification.get("status")
        }
    }