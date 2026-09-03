import os

from dotenv import load_dotenv
from google import genai

from backend.services.customer_context import (
    get_customer_payment_context
)


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY:
    client = genai.Client(
        api_key=API_KEY
    )


def customer_chat(customer_id: str, message: str):

    context = get_customer_payment_context(
        customer_id
    )

    # ========================================================
    # FALLBACK
    # ========================================================

    if not API_KEY or client is None:

        return (
            "I’m currently unable to access the AI assistant. "
            "Please check your payment details or try again shortly."
        )

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are RazorRecover Customer Payment Assistant.

You help customers understand their payment status
and recovery process.

CUSTOMER PAYMENT CONTEXT:
{context}

CUSTOMER MESSAGE:
{message}

Rules:

1. Only discuss information available in the payment context.
2. Never invent payment status.
3. Never claim that money was recovered unless status is success.
4. Explain payment failures in simple language.
5. Be polite and customer-friendly.
6. Never expose internal AI reasoning.
7. If the customer asks when a retry will happen but
   no retry schedule exists, say that the recovery team
   is determining the next action.
8. If the payment is successful, clearly confirm it.
9. If the payment is failed, explain the current status
   and available recovery process.

Return a concise customer-friendly answer.
"""

    # ========================================================
    # GEMINI
    # ========================================================

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if not response or not response.text:

            raise ValueError(
                "Gemini returned an empty response."
            )

        return response.text.strip()

    except Exception as e:

        print(
            f"[RazorRecover] Customer chat Gemini error: {e}"
        )

        return (
            "I’m currently unable to access the AI assistant. "
            "Your payment information is still available. "
            "Please try again shortly."
        )