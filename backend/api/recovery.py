from fastapi import APIRouter, HTTPException

from backend.models.payment import (
    Payment,
    CreatePaymentRequest
)

from backend.models.chat import ChatRequest

from backend.services.root_cause import (
    analyze_root_cause
)

from backend.services.risk_engine import (
    calculate_revenue_risk
)

from backend.services.ai_agent import (
    get_ai_recovery_decision
)

from backend.policies.guard_rails import (
    validate_recovery_action
)

from backend.services.action_executer import (
    execute_recovery_action
)

from backend.services.recovery_verifier import (
    verify_recovery
)

from backend.services.audit_logger import (
    create_audit_log
)

from backend.services.batch_processor import (
    process_batch
)

from backend.services.payment_engine import (
    create_test_payment,
    get_payment,
    retry_payment
)

from backend.services.recovery_scheduler import (
    create_recovery_plan
)

from backend.services.recovery_store import (
    save_recovery_plan,
    get_recovery_plan
)

from backend.services.customer_context import (
    get_customer_payment_context
)

from backend.services.customer_chat import (
    customer_chat
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/recovery",
    tags=["Revenue Recovery"]
)


# =========================================================
# ANALYZE PAYMENT
# =========================================================

@router.post("/analyze")
def analyze_payment(payment: Payment):

    # 1. Revenue risk
    risk = calculate_revenue_risk(payment)

    # 2. Root cause
    root_cause = analyze_root_cause(payment)

    # 3. AI recovery decision
    try:

        strategy = get_ai_recovery_decision(
            payment,
            risk,
            root_cause
        )

    except Exception as e:

        print(
            f"[RazorRecover] AI decision failed: {e}"
        )

        strategy = {
            "action": "SCHEDULE_RETRY",
            "reason": "AI unavailable. Safe fallback selected.",
            "retry_after_hours": 24,
            "max_attempts": 2,
            "recovery_window_hours": 72,
            "customer_message": (
                "Your payment could not be completed. "
                "We will retry it automatically."
            ),
            "decision_source": "emergency_fallback"
        }

    # 4. Guardrail
    guardrail = validate_recovery_action(
        payment,
        strategy.get("action", "NO_ACTION"),
        risk.get("risk_score", 0)
    )

    # 5. Execute
    execution = execute_recovery_action(
        payment,
        guardrail
    )

    # 6. Verification
    # Do NOT fake a successful recovery.
    verification = {
        "recovered": False,
        "amount_recovered": 0,
        "status": "RECOVERY_PENDING"
    }

    # 7. Audit
    try:

        audit_log = create_audit_log(
            payment,
            risk,
            root_cause,
            strategy,
            guardrail,
            execution,
            verification
        )

    except Exception as e:

        print(
            f"[RazorRecover] Audit log warning: {e}"
        )

        audit_log = {
            "status": "AUDIT_LOG_FALLBACK",
            "transaction_id": payment.transaction_id,
            "error": str(e)
        }

    return {
        "transaction_id": payment.transaction_id,
        "amount": payment.amount,
        "risk_analysis": risk,
        "root_cause_analysis": root_cause,
        "recommended_recovery": strategy,
        "guardrail_decision": guardrail,
        "execution_result": execution,
        "recovery_verification": verification,
        "audit_log": audit_log
    }


# =========================================================
# BATCH ANALYSIS
# =========================================================

@router.post("/batch")
def analyze_batch(count: int = 1000):

    if count < 1:
        raise HTTPException(
            status_code=400,
            detail="Count must be greater than 0"
        )

    if count > 10000:
        raise HTTPException(
            status_code=400,
            detail="Maximum batch size is 10000"
        )

    return process_batch(count)


# =========================================================
# CREATE TEST PAYMENT
# =========================================================

@router.post("/payments/create")
def create_payment(
    request: CreatePaymentRequest
):

    payment = create_test_payment(
        customer_id=request.customer_id,
        amount=request.amount,
        failure_reason=request.failure_reason,
        payment_type=request.payment_type
    )

    return {
        "message": "Test payment created",
        "transaction_id": payment.transaction_id,
        "customer_id": payment.customer_id,
        "amount": payment.amount,
        "status": payment.status,
        "failure_reason": payment.failure_reason
    }


# =========================================================
# AUTONOMOUS REVENUE RECOVERY
# =========================================================

@router.post(
    "/transactions/{transaction_id}/recover"
)
def recover_transaction(
    transaction_id: str
):

    # -----------------------------------------------------
    # GET PAYMENT
    # -----------------------------------------------------

    payment = get_payment(
        transaction_id
    )

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    # -----------------------------------------------------
    # 1. REVENUE RISK
    # -----------------------------------------------------

    risk = calculate_revenue_risk(
        payment
    )

    # -----------------------------------------------------
    # 2. ROOT CAUSE
    # -----------------------------------------------------

    root_cause = analyze_root_cause(
        payment
    )

    # -----------------------------------------------------
    # 3. AI DECISION
    # -----------------------------------------------------

    try:

        strategy = get_ai_recovery_decision(
            payment,
            risk,
            root_cause
        )

    except Exception as e:

        print(
            f"[RazorRecover] AI decision failed: {e}"
        )

        strategy = {
            "action": "SCHEDULE_RETRY",
            "reason": (
                "AI service unavailable. "
                "Safe fallback recovery selected."
            ),
            "retry_after_hours": 24,
            "max_attempts": 2,
            "recovery_window_hours": 72,
            "customer_message": (
                "Your payment could not be completed. "
                "We will retry it automatically."
            ),
            "decision_source": "emergency_fallback"
        }

    # -----------------------------------------------------
    # 4. GUARDRAIL
    # -----------------------------------------------------

    guardrail = validate_recovery_action(
        payment,
        strategy.get(
            "action",
            "NO_ACTION"
        ),
        risk.get(
            "risk_score",
            0
        )
    )

    # -----------------------------------------------------
    # 5. EXECUTE ACTION
    # -----------------------------------------------------

    execution = execute_recovery_action(
        payment,
        guardrail
    )

    # -----------------------------------------------------
    # 6. CREATE RECOVERY PLAN
    # -----------------------------------------------------

    try:

        plan = create_recovery_plan(
            payment
        )

    except Exception as e:

        print(
            f"[RazorRecover] Recovery plan error: {e}"
        )

        plan = {
            "status": "planned",
            "recovery_action": guardrail.get(
                "final_action",
                strategy.get(
                    "action",
                    "SCHEDULE_RETRY"
                )
            ),
            "retry_count": getattr(
                payment,
                "retry_count",
                0
            ),
            "max_retries": strategy.get(
                "max_attempts",
                3
            ),
            "next_retry_at": None,
            "expected_recovery_window_hours":
                strategy.get(
                    "recovery_window_hours",
                    72
                ),
            "customer_action_required":
                strategy.get(
                    "action"
                ) == "REQUEST_PAYMENT_METHOD_UPDATE",
            "escalation_required":
                strategy.get(
                    "action"
                ) == "ESCALATE_TO_SUPPORT"
        }

    # -----------------------------------------------------
    # 7. SAVE PLAN
    # -----------------------------------------------------

    save_recovery_plan(
        transaction_id,
        plan
    )

    # -----------------------------------------------------
    # 8. PENDING VERIFICATION
    # -----------------------------------------------------

    verification = {
        "recovered": False,
        "amount_recovered": 0,
        "status": "RECOVERY_PENDING"
    }

    # -----------------------------------------------------
    # 9. AUDIT
    # -----------------------------------------------------

    try:

        audit_log = create_audit_log(
            payment,
            risk,
            root_cause,
            strategy,
            guardrail,
            execution,
            verification
        )

    except Exception as e:

        print(
            f"[RazorRecover] Audit log warning: {e}"
        )

        audit_log = {
            "status": "AUDIT_LOG_FALLBACK",
            "error": str(e),
            "transaction_id": transaction_id
        }

    # -----------------------------------------------------
    # 10. RESPONSE
    # -----------------------------------------------------

    return {
        "transaction_id": transaction_id,
        "amount": payment.amount,
        "risk_analysis": risk,
        "root_cause_analysis": root_cause,
        "recovery_strategy": strategy,
        "guardrail_decision": guardrail,
        "execution_result": execution,
        "recovery_verification": verification,
        "recovery_plan": plan,
        "audit_log": audit_log
    }


# =========================================================
# RETRY PAYMENT
# =========================================================

@router.post(
    "/transactions/{transaction_id}/retry"
)
def retry_transaction(
    transaction_id: str
):

    payment = get_payment(
        transaction_id
    )

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    # -----------------------------------------------------
    # ALREADY SUCCESSFUL
    # -----------------------------------------------------

    if payment.status == "success":

        recovery_plan = {
            "status": "recovered",
            "recovery_action": "COMPLETED",
            "retry_count": payment.retry_count,
            "max_retries": 3,
            "next_retry_at": None,
            "expected_recovery_window_hours": 0,
            "customer_action_required": False,
            "escalation_required": False
        }

        save_recovery_plan(
            transaction_id,
            recovery_plan
        )

        return {
            "transaction_id": transaction_id,
            "retry_count": payment.retry_count,
            "payment_status": "success",
            "recovery_plan": recovery_plan,
            "recovery_verification": {
                "recovered": True,
                "amount_recovered": payment.amount,
                "status": "ALREADY_RECOVERED"
            }
        }

    # -----------------------------------------------------
    # EXECUTE RETRY
    # -----------------------------------------------------

    try:

        payment = retry_payment(
            transaction_id
        )

    except Exception as e:

        print(
            f"[RazorRecover] Retry error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Retry failed: {str(e)}"
        )

    # -----------------------------------------------------
    # VERIFY RETRY
    # -----------------------------------------------------

    try:

        # IMPORTANT:
        # verify_recovery accepts ONLY payment.
        verification = verify_recovery(
            payment
        )

    except Exception as e:

        print(
            f"[RazorRecover] Verification warning: {e}"
        )

        verification = {
            "recovered":
                payment.status == "success",

            "amount_recovered":
                payment.amount
                if payment.status == "success"
                else 0,

            "status":
                "RECOVERED"
                if payment.status == "success"
                else "NOT_RECOVERED"
        }

    # -----------------------------------------------------
    # CREATE UPDATED PLAN
    # -----------------------------------------------------

    if payment.status == "success":

        recovery_plan = {
            "status": "recovered",
            "recovery_action": "COMPLETED",
            "retry_count": payment.retry_count,
            "max_retries": 3,
            "next_retry_at": None,
            "expected_recovery_window_hours": 0,
            "customer_action_required": False,
            "escalation_required": False
        }

    else:

        recovery_plan = create_recovery_plan(
            payment
        )

    # -----------------------------------------------------
    # SAVE PLAN
    # -----------------------------------------------------

    save_recovery_plan(
        transaction_id,
        recovery_plan
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "transaction_id": transaction_id,
        "retry_count": payment.retry_count,
        "payment_status": payment.status,
        "recovery_plan": recovery_plan,
        "recovery_verification": verification
    }


# =========================================================
# GET RECOVERY PLAN
# =========================================================

@router.get(
    "/transactions/{transaction_id}/recovery-plan"
)
def get_transaction_recovery_plan(
    transaction_id: str
):

    plan = get_recovery_plan(
        transaction_id
    )

    if plan is None:

        raise HTTPException(
            status_code=404,
            detail="Recovery plan not found"
        )

    return {
        "transaction_id": transaction_id,
        "recovery_plan": plan
    }


# =========================================================
# CUSTOMER PAYMENT HISTORY
# =========================================================

@router.get(
    "/customers/{customer_id}/payments"
)
def customer_payments(
    customer_id: str
):

    return get_customer_payment_context(
        customer_id
    )


# =========================================================
# CUSTOMER PAYMENT CHAT
# =========================================================

@router.post(
    "/customers/{customer_id}/chat"
)
def chat_with_customer(
    customer_id: str,
    request: ChatRequest
):

    try:

        answer = customer_chat(
            customer_id,
            request.message
        )

    except Exception as e:

        print(
            f"[RazorRecover] Customer chat error: {e}"
        )

        answer = (
            "I’m currently unable to access the "
            "AI assistant. Please try again shortly."
        )

    return {
        "customer_id": customer_id,
        "message": request.message,
        "response": answer
    }