import os
import json

from dotenv import load_dotenv
from google import genai

from backend.models.payment import Payment


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if API_KEY:
    client = genai.Client(
        api_key=API_KEY
    )


# ============================================================
# FALLBACK RECOVERY POLICY
# ============================================================

def fallback_recovery_decision(payment, risk, root_cause):

    failure_reason = str(
        getattr(payment, "failure_reason", "")
    ).lower()

    amount = float(
        getattr(payment, "amount", 0)
    )

    # Network / temporary failure
    if failure_reason in [
        "network_timeout",
        "timeout",
        "temporary_failure"
    ]:
        return {
            "action": "SCHEDULE_RETRY",
            "reason": "Temporary payment failure detected.",
            "retry_after_hours": 4,
            "max_attempts": 3,
            "recovery_window_hours": 72,
            "customer_message": (
                "Your payment could not be completed due to a "
                "temporary issue. We will automatically retry "
                "the payment after 4 hours."
            ),
            "decision_source": "fallback_policy"
        }

    # Insufficient funds
    if failure_reason == "insufficient_funds":
        return {
            "action": "SCHEDULE_RETRY",
            "reason": "Insufficient funds detected.",
            "retry_after_hours": 24,
            "max_attempts": 2,
            "recovery_window_hours": 72,
            "customer_message": (
                "Your payment could not be completed because "
                "of insufficient funds. We will retry the "
                "payment after 24 hours."
            ),
            "decision_source": "fallback_policy"
        }

    # Expired card
    if failure_reason == "expired_card":
        return {
            "action": "REQUEST_PAYMENT_METHOD_UPDATE",
            "reason": "The customer's payment method has expired.",
            "retry_after_hours": 0,
            "max_attempts": 0,
            "recovery_window_hours": 48,
            "customer_message": (
                "Your payment method appears to have expired. "
                "Please update your payment method to complete "
                f"the ₹{amount:,.0f} payment."
            ),
            "decision_source": "fallback_policy"
        }

    # Payment declined
    if failure_reason in [
        "payment_declined",
        "declined",
        "card_declined"
    ]:
        return {
            "action": "ALTERNATIVE_PAYMENT_METHOD",
            "reason": "Payment was declined by the payment provider.",
            "retry_after_hours": 24,
            "max_attempts": 1,
            "recovery_window_hours": 48,
            "customer_message": (
                "Your payment was declined by the payment provider. "
                "Please use another payment method."
            ),
            "decision_source": "fallback_policy"
        }

    # Default
    return {
        "action": "SCHEDULE_RETRY",
        "reason": "Payment failure requires a safe retry.",
        "retry_after_hours": 24,
        "max_attempts": 2,
        "recovery_window_hours": 72,
        "customer_message": (
            "Your payment could not be completed. "
            "We will retry it automatically."
        ),
        "decision_source": "fallback_policy"
    }


# ============================================================
# AI RECOVERY DECISION
# ============================================================

def get_ai_recovery_decision(payment, risk, root_cause):

    # --------------------------------------------------------
    # No API key
    # --------------------------------------------------------

    if not API_KEY or client is None:

        print(
            "[RazorRecover] Gemini API key not configured. "
            "Using fallback recovery policy."
        )

        return fallback_recovery_decision(
            payment,
            risk,
            root_cause
        )

    # --------------------------------------------------------
    # Payment data
    # --------------------------------------------------------

    payment_data = {
        "transaction_id": getattr(
            payment,
            "transaction_id",
            None
        ),
        "customer_id": getattr(
            payment,
            "customer_id",
            None
        ),
        "amount": getattr(
            payment,
            "amount",
            0
        ),
        "status": getattr(
            payment,
            "status",
            None
        ),
        "failure_reason": getattr(
            payment,
            "failure_reason",
            None
        ),
        "payment_type": getattr(
            payment,
            "payment_type",
            None
        ),
        "retry_count": getattr(
            payment,
            "retry_count",
            0
        )
    }

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are RazorRecover, an AI revenue recovery agent.

Your job is to select a SAFE recovery action for a failed payment.

Payment:
{json.dumps(payment_data, indent=2, default=str)}

Risk analysis:
{json.dumps(risk, indent=2, default=str)}

Root cause:
{json.dumps(root_cause, indent=2, default=str)}

Choose exactly one action from:

1. SCHEDULE_RETRY
2. REQUEST_PAYMENT_METHOD_UPDATE
3. ALTERNATIVE_PAYMENT_METHOD
4. ESCALATE_TO_SUPPORT
5. NO_ACTION

Recovery must be bounded.

Maximum retry attempts: 3
Maximum recovery window: 72 hours.

Return ONLY valid JSON.

Required format:

{{
    "action": "SCHEDULE_RETRY",
    "reason": "short explanation",
    "retry_after_hours": 4,
    "max_attempts": 3,
    "recovery_window_hours": 72,
    "customer_message": "short customer-friendly explanation"
}}
"""

    # --------------------------------------------------------
    # Gemini
    # --------------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        text = response.text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        result = json.loads(text)

        allowed_actions = {
            "SCHEDULE_RETRY",
            "REQUEST_PAYMENT_METHOD_UPDATE",
            "ALTERNATIVE_PAYMENT_METHOD",
            "ESCALATE_TO_SUPPORT",
            "NO_ACTION"
        }

        if result.get("action") not in allowed_actions:
            raise ValueError(
                "Gemini returned an invalid recovery action."
            )

        result["decision_source"] = "gemini"

        return result

    except Exception as e:

        print(
            f"[RazorRecover] Gemini unavailable: {e}"
        )

        print(
            "[RazorRecover] Switching to fallback recovery policy."
        )

        return fallback_recovery_decision(
            payment,
            risk,
            root_cause
        )