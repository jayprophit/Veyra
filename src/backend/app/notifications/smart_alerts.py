"""Smart Alert and Notification System."""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

class AlertType(Enum):
    PRICE = "price"
    VOLUME = "volume"
    INDICATOR = "indicator"
    PNL = "pnl"
    NEWS = "news"
    ANOMALY = "anomaly"
    SYSTEM = "system"

class AlertCondition(Enum):
    ABOVE = "above"
    BELOW = "below"
    CROSSES_UP = "crosses_up"
    CROSSES_DOWN = "crosses_down"
    PERCENT_CHANGE = "percent_change"
    VOLUME_SPIKE = "volume_spike"

@dataclass
class Alert:
    alert_id: str
    user_id: str
    alert_type: AlertType
    symbol: Optional[str]
    condition: AlertCondition
    threshold: float
    message: str
    created_at: datetime
    is_active: bool = True
    triggered_count: int = 0
    last_triggered: Optional[datetime] = None
    cooldown_minutes: int = 60
    notification_channels: List[str] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ['push', 'email']

class SmartAlertSystem:
    """Intelligent alerting with multi-channel delivery."""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.user_alerts: Dict[str, List[str]] = defaultdict(list)
        self.alert_counter = 0
        self.notification_handlers: Dict[str, Callable] = {}
        self.running = False
    
    def _generate_id(self) -> str:
        self.alert_counter += 1
        return f"alert_{self.alert_counter}_{datetime.now().strftime('%H%M%S')}"
    
    async def create_alert(self, user_id: str, alert_data: Dict) -> Alert:
        """Create a new alert."""
        alert_id = self._generate_id()
        
        alert = Alert(
            alert_id=alert_id,
            user_id=user_id,
            alert_type=AlertType(alert_data['type']),
            symbol=alert_data.get('symbol'),
            condition=AlertCondition(alert_data['condition']),
            threshold=alert_data['threshold'],
            message=alert_data.get('message', ''),
            created_at=datetime.now(),
            cooldown_minutes=alert_data.get('cooldown', 60),
            notification_channels=alert_data.get('channels', ['push'])
        )
        
        self.alerts[alert_id] = alert
        self.user_alerts[user_id].append(alert_id)
        
        logger.info(f"Alert created: {alert_id} for user {user_id}")
        return alert
    
    async def check_price_alert(self, alert: Alert, current_price: float) -> bool:
        """Check if price alert should trigger."""
        if not alert.is_active:
            return False
        
        # Check cooldown
        if alert.last_triggered:
            minutes_since = (datetime.now() - alert.last_triggered).total_seconds() / 60
            if minutes_since < alert.cooldown_minutes:
                return False
        
        condition_met = False
        
        if alert.condition == AlertCondition.ABOVE:
            condition_met = current_price > alert.threshold
        elif alert.condition == AlertCondition.BELOW:
            condition_met = current_price < alert.threshold
        elif alert.condition == AlertCondition.PERCENT_CHANGE:
            # Would need previous price for this
            pass
        
        if condition_met:
            alert.triggered_count += 1
            alert.last_triggered = datetime.now()
            await self._send_notification(alert, current_price)
            return True
        
        return False
    
    async def check_pnl_alert(self, alert: Alert, current_pnl: float) -> bool:
        """Check P&L-based alerts."""
        if not alert.is_active:
            return False
        
        condition_met = False
        
        if alert.condition == AlertCondition.ABOVE and current_pnl > alert.threshold:
            condition_met = True
        elif alert.condition == AlertCondition.BELOW and current_pnl < alert.threshold:
            condition_met = True
        
        if condition_met:
            alert.triggered_count += 1
            alert.last_triggered = datetime.now()
            await self._send_notification(alert, current_pnl)
            return True
        
        return False
    
    async def _send_notification(self, alert: Alert, trigger_value: float):
        """Send notification through configured channels."""
        notification = {
            'alert_id': alert.alert_id,
            'user_id': alert.user_id,
            'type': alert.alert_type.value,
            'symbol': alert.symbol,
            'message': alert.message,
            'trigger_value': trigger_value,
            'threshold': alert.threshold,
            'timestamp': datetime.now().isoformat()
        }
        
        for channel in alert.notification_channels:
            if channel in self.notification_handlers:
                try:
                    handler = self.notification_handlers[channel]
                    await handler(notification)
                except Exception as e:
                    logger.error(f"Failed to send {channel} notification: {e}")
        
        logger.info(f"Alert triggered: {alert.alert_id} - {alert.message}")
    
    def register_notification_handler(self, channel: str, handler: Callable):
        """Register a handler for a notification channel."""
        self.notification_handlers[channel] = handler
        logger.info(f"Registered handler for {channel}")
    
    async def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert."""
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        self.user_alerts[alert.user_id].remove(alert_id)
        del self.alerts[alert_id]
        
        return True
    
    async def toggle_alert(self, alert_id: str) -> bool:
        """Toggle alert active status."""
        if alert_id not in self.alerts:
            return False
        
        self.alerts[alert_id].is_active = not self.alerts[alert_id].is_active
        return self.alerts[alert_id].is_active
    
    async def get_user_alerts(self, user_id: str, active_only: bool = False) -> List[Dict]:
        """Get all alerts for a user."""
        alert_ids = self.user_alerts.get(user_id, [])
        alerts = []
        
        for aid in alert_ids:
            if aid in self.alerts:
                alert = self.alerts[aid]
                if active_only and not alert.is_active:
                    continue
                alerts.append({
                    'alert_id': alert.alert_id,
                    'type': alert.alert_type.value,
                    'symbol': alert.symbol,
                    'condition': alert.condition.value,
                    'threshold': alert.threshold,
                    'message': alert.message,
                    'is_active': alert.is_active,
                    'triggered_count': alert.triggered_count,
                    'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None,
                    'channels': alert.notification_channels
                })
        
        return alerts
    
    async def create_preset_alerts(self, user_id: str, preset: str) -> List[str]:
        """Create preset alert configurations."""
        created_ids = []
        
        presets = {
            'conservative': [
                {'type': 'pnl', 'condition': 'below', 'threshold': -1000, 'message': 'Daily loss limit reached'},
                {'type': 'price', 'symbol': 'BTC/USD', 'condition': 'above', 'threshold': 50000, 'message': 'BTC above 50k'}
            ],
            'aggressive': [
                {'type': 'pnl', 'condition': 'above', 'threshold': 5000, 'message': 'Take some profits!'},
                {'type': 'pnl', 'condition': 'below', 'threshold': -2000, 'message': 'Stop trading - loss limit'}
            ],
            'hodler': [
                {'type': 'price', 'symbol': 'BTC/USD', 'condition': 'below', 'threshold': 30000, 'message': 'BTC dip - buying opportunity?'},
                {'type': 'volume', 'symbol': 'BTC/USD', 'condition': 'volume_spike', 'threshold': 2.0, 'message': 'High volume detected'}
            ]
        }
        
        if preset in presets:
            for alert_data in presets[preset]:
                alert = await self.create_alert(user_id, alert_data)
                created_ids.append(alert.alert_id)
        
        return created_ids

smart_alerts = SmartAlertSystem()
