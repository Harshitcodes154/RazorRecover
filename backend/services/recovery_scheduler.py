from datetime import datetime, timedelta


MAX_RETRIES = 3

RETRY_DELAYS = {
    1: 6,    # first retry after 6 hours
    2: 24,   # second retry after 24 hours
    3: 24    # third retry after another 24 hours
}


def create_recovery_plan(payment):

    retry_count = payment.retry_count

    if retry_count >= MAX_RETRIES:
        return {
            "status": "escalated",
            "recovery_action": "ESCALATE",
            "retry_count": retry_count,
            "max_retries": MAX_RETRIES,
            "next_retry_at": None,
            "expected_recovery_window_hours": 0,
            "customer_action_required": True,
            "escalation_required": True
        }

    next_attempt = retry_count + 1

    delay_hours = RETRY_DELAYS.get(
        next_attempt,
        24
    )

    next_retry_at = (
        datetime.now()
        + timedelta(hours=delay_hours)
    )

    remaining_window = (
        delay_hours
        + (MAX_RETRIES - next_attempt) * 24
    )

    return {
        "status": "recovery_in_progress",

        "recovery_action": "SCHEDULE_RETRY",

        "retry_count": retry_count,

        "max_retries": MAX_RETRIES,

        "next_retry_at": next_retry_at.isoformat(),

        "expected_recovery_window_hours":
            remaining_window,

        "customer_action_required": False,

        "escalation_required": False
    }