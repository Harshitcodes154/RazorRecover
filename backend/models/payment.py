from pydantic import BaseModel
from typing import Optional



class Payment(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    status: str = "pending"
    failure_reason: Optional[str] = None
    previous_successful_payments: int = 0
    retry_count: int = 0
    payment_type: str = "payment"


class CreatePaymentRequest(BaseModel):
    customer_id: str
    amount: float
    failure_reason: Optional[str] = None
    payment_type: str = "payment"