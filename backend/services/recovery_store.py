recovery_plans = {}


def save_recovery_plan(
    transaction_id,
    plan
):

    recovery_plans[
        transaction_id
    ] = plan

    return plan


def get_recovery_plan(
    transaction_id
):

    return recovery_plans.get(
        transaction_id
    )