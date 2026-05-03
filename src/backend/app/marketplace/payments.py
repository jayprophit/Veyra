"""Payment Processing for Marketplace"""
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
from enum import Enum
import uuid

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class Payment:
    id: str
    order_id: str
    customer_id: str
    amount: float
    currency: str
    status: PaymentStatus
    payment_method: str
    created_at: datetime

class PaymentProcessor:
    SUPPORTED_METHODS = ["stripe", "paypal", "crypto"]
    
    def __init__(self):
        self._payments: Dict[str, Payment] = {}
    
    def process_payment(self, order_id: str, customer_id: str,
                       amount: float, currency: str,
                       payment_method: str) -> Payment:
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status=PaymentStatus.COMPLETED,
            payment_method=payment_method,
            created_at=datetime.now()
        )
        self._payments[payment.id] = payment
        return payment
    
    def get_payment(self, payment_id: str) -> Optional[Payment]:
        return self._payments.get(payment_id)
    
    def refund_payment(self, payment_id: str) -> bool:
        if payment := self._payments.get(payment_id):
            payment.status = PaymentStatus.REFUNDED
            return True
        return False
