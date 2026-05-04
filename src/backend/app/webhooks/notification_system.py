"""Webhook Notification System."""
import logging
import hmac
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class WebhookEvent(Enum):
    TRADE_FILLED = "trade.filled"
    PRICE_ALERT = "price.alert"
    ORDER_STATUS = "order.status"
    PORTFOLIO_UPDATE = "portfolio.update"
    RISK_ALERT = "risk.alert"
    NEWS_SENTIMENT = "news.sentiment"

@dataclass
class WebhookSubscription:
    webhook_id: str
    user_id: str
    url: str
    events: List[WebhookEvent]
    secret: str
    is_active: bool
    created_at: datetime
    last_delivery: Optional[datetime]
    delivery_count: int
    failure_count: int

class WebhookSystem:
    """Real-time webhook notification system."""
    
    def __init__(self):
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self.delivery_log: List[Dict] = []
        self.retry_attempts = 3
        self.timeout_seconds = 10
    
    async def register_webhook(self,
                              user_id: str,
                              url: str,
                              events: List[str],
                              secret: Optional[str] = None) -> Dict[str, Any]:
        """Register new webhook subscription."""
        webhook_id = f"wh_{user_id}_{datetime.now().strftime('%H%M%S%f')}"
        
        if not secret:
            import secrets
            secret = secrets.token_hex(16)
        
        subscription = WebhookSubscription(
            webhook_id=webhook_id,
            user_id=user_id,
            url=url,
            events=[WebhookEvent(e) for e in events],
            secret=secret,
            is_active=True,
            created_at=datetime.now(),
            last_delivery=None,
            delivery_count=0,
            failure_count=0
        )
        
        self.subscriptions[webhook_id] = subscription
        
        logger.info(f"Webhook registered: {webhook_id} for {url}")
        
        return {
            'webhook_id': webhook_id,
            'url': url,
            'events': events,
            'secret': secret[:8] + '...',  # Show partial
            'status': 'active'
        }
    
    async def send_notification(self,
                               event_type: WebhookEvent,
                               payload: Dict[str, Any]) -> List[Dict]:
        """Send notification to all subscribed webhooks."""
        results = []
        
        for webhook in self.subscriptions.values():
            if not webhook.is_active:
                continue
            
            if event_type not in webhook.events:
                continue
            
            # Sign payload
            signed_payload = self._sign_payload(payload, webhook.secret)
            
            # Simulate delivery
            success = True
            
            webhook.last_delivery = datetime.now()
            if success:
                webhook.delivery_count += 1
            else:
                webhook.failure_count += 1
            
            self.delivery_log.append({
                'webhook_id': webhook.webhook_id,
                'event': event_type.value,
                'timestamp': datetime.now().isoformat(),
                'success': success
            })
            
            results.append({
                'webhook_id': webhook.webhook_id,
                'delivered': success
            })
        
        return results
    
    def _sign_payload(self, payload: Dict, secret: str) -> Dict:
        """Sign webhook payload with HMAC."""
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'payload': payload,
            'signature': signature,
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_webhook_status(self, webhook_id: str) -> Dict[str, Any]:
        """Get webhook delivery status."""
        if webhook_id not in self.subscriptions:
            return {'error': 'Webhook not found'}
        
        wh = self.subscriptions[webhook_id]
        
        return {
            'webhook_id': webhook_id,
            'url': wh.url,
            'status': 'active' if wh.is_active else 'inactive',
            'events': [e.value for e in wh.events],
            'deliveries': wh.delivery_count,
            'failures': wh.failure_count,
            'success_rate': wh.delivery_count / (wh.delivery_count + wh.failure_count) * 100 if (wh.delivery_count + wh.failure_count) > 0 else 0,
            'last_delivery': wh.last_delivery.isoformat() if wh.last_delivery else None
        }
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook subscription."""
        if webhook_id in self.subscriptions:
            del self.subscriptions[webhook_id]
            return True
        return False

webhook_system = WebhookSystem()
