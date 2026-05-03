"""Subscription Management for Marketplace"""
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"

@dataclass
class Subscription:
    id: str
    customer_id: str
    product_id: str
    status: SubscriptionStatus
    start_date: datetime
    end_date: datetime
    next_billing_date: datetime
    amount: float
    currency: str

class SubscriptionManager:
    def __init__(self):
        self._subscriptions: Dict[str, Subscription] = {}
    
    def create_subscription(self, customer_id: str, product_id: str,
                           amount: float, interval_days: int = 30,
                           currency: str = "USD") -> Subscription:
        now = datetime.now()
        sub = Subscription(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            product_id=product_id,
            status=SubscriptionStatus.ACTIVE,
            start_date=now,
            end_date=now + timedelta(days=interval_days),
            next_billing_date=now + timedelta(days=interval_days),
            amount=amount,
            currency=currency
        )
        self._subscriptions[sub.id] = sub
        return sub
    
    def get_customer_subscriptions(self, customer_id: str) -> list:
        return [s for s in self._subscriptions.values() if s.customer_id == customer_id]
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        if sub := self._subscriptions.get(subscription_id):
            sub.status = SubscriptionStatus.CANCELLED
            return True
        return False
    
    def get_upcoming_renewals(self, days: int = 7) -> list:
        cutoff = datetime.now() + timedelta(days=days)
        return [s for s in self._subscriptions.values() 
                if s.status == SubscriptionStatus.ACTIVE and s.next_billing_date <= cutoff]
