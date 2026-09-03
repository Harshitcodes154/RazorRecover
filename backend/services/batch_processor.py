from simulator.generate_payments import generate_payments

from backend.models.payment import Payment
from backend.services.risk_engine import calculate_revenue_risk
from backend.services.root_cause import analyze_root_cause
from backend.services.recovery_strategy import choose_recovery_strategy
from backend.policies.guard_rails import validate_recovery_action
from backend.services.action_executer import execute_recovery_action


def process_batch(count: int = 1000):

    payments = generate_payments(count)

    total_revenue_at_risk = 0
    total_recovered = 0

    transactions_analyzed = 0
    recovery_candidates = 0
    actions_executed = 0
    successful_recoveries = 0
    escalations = 0

    results = []

    for data in payments:

        payment = Payment(**data)

        transactions_analyzed += 1

        risk = calculate_revenue_risk(payment)

        if not risk["at_risk"]:
            continue

        total_revenue_at_risk += payment.amount
        recovery_candidates += 1

        root_cause = analyze_root_cause(payment)

        strategy = choose_recovery_strategy(
            payment,
            risk["risk_score"]
        )

        guardrail = validate_recovery_action(
            payment,
            strategy["action"],
            risk["risk_score"]
        )

        execution = execute_recovery_action(
            payment,
            guardrail
        )

        if execution["executed"]:
            actions_executed += 1

        if execution["status"] == "ESCALATED":
            escalations += 1

        # Demo recovery simulation
        recovered = False

        if guardrail["allowed"]:

            recovery_probability = risk["risk_score"] / 100

            recovered = (
                __import__("random").random()
                < recovery_probability
            )

        if recovered:
            total_recovered += payment.amount
            successful_recoveries += 1

        results.append({
            "transaction_id": payment.transaction_id,
            "amount": payment.amount,
            "risk_score": risk["risk_score"],
            "root_cause": root_cause["root_cause"],
            "action": guardrail["final_action"],
            "recovered": recovered,
            "amount_recovered": payment.amount if recovered else 0
        })

    recovery_rate = 0

    if total_revenue_at_risk > 0:
        recovery_rate = (
            total_recovered / total_revenue_at_risk
        ) * 100

    return {
        "transactions_analyzed": transactions_analyzed,
        "recovery_candidates": recovery_candidates,
        "actions_executed": actions_executed,
        "successful_recoveries": successful_recoveries,
        "escalations": escalations,
        "revenue_at_risk": round(total_revenue_at_risk, 2),
        "revenue_recovered": round(total_recovered, 2),
        "recovery_rate": round(recovery_rate, 2),
        "transactions": results
    }