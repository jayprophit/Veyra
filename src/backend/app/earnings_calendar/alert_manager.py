"""
Earnings Alert Manager
Manages notifications for earnings announcements
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Callable
import asyncio

from .models import EarningsEvent

class AlertManager:
    """Manages earnings alerts across multiple channels"""
    
    def __init__(self):
        self._alerts: Dict[str, Dict] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default notification handlers"""
        self._handlers = {
            "email": self._send_email,
            "sms": self._send_sms,
            "push": self._send_push,
            "in_app": self._send_in_app,
        }
    
    async def create_alert(
        self,
        user_id: str,
        ticker: str,
        channels: List[str],
        advance_notice_hours: int = 24
    ) -> str:
        """Create a new earnings alert"""
        
        alert_id = f"alert_{user_id}_{ticker}_{datetime.now().timestamp()}"
        
        self._alerts[alert_id] = {
            "id": alert_id,
            "user_id": user_id,
            "ticker": ticker,
            "channels": channels,
            "advance_notice_hours": advance_notice_hours,
            "created_at": datetime.now(),
            "is_active": True,
            "last_triggered": None
        }
        
        return alert_id
    
    async def check_and_trigger_alerts(self, upcoming_earnings: List[EarningsEvent]):
        """Check alerts and trigger notifications"""
        
        now = datetime.now()
        
        for alert_id, alert in self._alerts.items():
            if not alert["is_active"]:
                continue
            
            # Find matching earnings
            for earnings in upcoming_earnings:
                if earnings.ticker == alert["ticker"]:
                    # Check if it's time to alert
                    notice_time = datetime.combine(
                        earnings.report_date, 
                        datetime.min.time()
                    ) - timedelta(hours=alert["advance_notice_hours"])
                    
                    if now >= notice_time:
                        await self._trigger_alert(alert, earnings)
    
    async def _trigger_alert(self, alert: Dict, earnings: EarningsEvent):
        """Trigger alert on all specified channels"""
        
        message = self._format_alert_message(earnings)
        
        for channel in alert["channels"]:
            handler = self._handlers.get(channel)
            if handler:
                try:
                    await handler(alert["user_id"], message, earnings)
                except Exception as e:
                    print(f"Failed to send {channel} alert: {e}")
        
        alert["last_triggered"] = datetime.now()
    
    def _format_alert_message(self, earnings: EarningsEvent) -> str:
        """Format alert message"""
        
        time_str = earnings.report_time.value
        
        msg = f"📊 Earnings Alert: {earnings.ticker}\n"
        msg += f"📅 Date: {earnings.report_date}\n"
        msg += f"⏰ Time: {time_str}\n"
        
        if earnings.eps_estimate:
            msg += f"📈 EPS Estimate: ${earnings.eps_estimate}\n"
        
        if earnings.whisper_number:
            msg += f"🤫 Whisper: ${earnings.whisper_number}\n"
        
        if not earnings.is_confirmed:
            msg += "⚠️ Date not confirmed\n"
        
        return msg
    
    async def _send_email(self, user_id: str, message: str, earnings: EarningsEvent):
        """Send email notification"""
        # Integration with SendGrid/AWS SES
        print(f"[EMAIL] To {user_id}: {message[:50]}...")
    
    async def _send_sms(self, user_id: str, message: str, earnings: EarningsEvent):
        """Send SMS notification"""
        # Integration with Twilio
        print(f"[SMS] To {user_id}: {message[:100]}...")
    
    async def _send_push(self, user_id: str, message: str, earnings: EarningsEvent):
        """Send push notification"""
        # Integration with Firebase
        print(f"[PUSH] To {user_id}: {message[:50]}...")
    
    async def _send_in_app(self, user_id: str, message: str, earnings: EarningsEvent):
        """Send in-app notification"""
        print(f"[IN_APP] To {user_id}: {message[:50]}...")
    
    def get_user_alerts(self, user_id: str) -> List[Dict]:
        """Get all alerts for a user"""
        return [
            alert for alert in self._alerts.values()
            if alert["user_id"] == user_id
        ]
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        if alert_id in self._alerts:
            del self._alerts[alert_id]
            return True
        return False
    
    def toggle_alert(self, alert_id: str) -> bool:
        """Toggle alert active state"""
        if alert_id in self._alerts:
            self._alerts[alert_id]["is_active"] = not self._alerts[alert_id]["is_active"]
            return self._alerts[alert_id]["is_active"]
        return False
