"""Notification Manager - Multi-channel notification orchestration"""
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid

from .channels import EmailChannel, SMSChannel, PushChannel, InAppChannel

class NotificationType(Enum):
    EARNINGS = "earnings"
    PRICE_ALERT = "price_alert"
    TRANSACTION = "transaction"
    SECURITY = "security"
    MARKETING = "marketing"

@dataclass
class Notification:
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    channels: List[str]
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

class NotificationManager:
    def __init__(self):
        self._channels = {
            "email": EmailChannel(),
            "sms": SMSChannel(),
            "push": PushChannel(),
            "in_app": InAppChannel()
        }
        self._preferences: Dict[str, Dict] = {}
        self._history: Dict[str, Notification] = {}
    
    def set_user_preferences(self, user_id: str, preferences: Dict):
        self._preferences[user_id] = preferences
    
    async def send_notification(self, user_id: str, notification_type: NotificationType,
                               title: str, message: str, **kwargs) -> Notification:
        prefs = self._preferences.get(user_id, {"channels": ["in_app"]})
        channels = prefs.get("channels", ["in_app"])
        
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            channels=channels
        )
        
        for channel_name in channels:
            if channel := self._channels.get(channel_name):
                await channel.send(user_id, message, subject=title, **kwargs)
        
        notification.sent_at = datetime.now()
        self._history[notification.id] = notification
        return notification
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        notifs = [n for n in self._history.values() if n.user_id == user_id]
        if unread_only:
            notifs = [n for n in notifs if n.read_at is None]
        return sorted(notifs, key=lambda x: x.sent_at or datetime.min, reverse=True)
    
    def mark_as_read(self, notification_id: str) -> bool:
        if notif := self._history.get(notification_id):
            notif.read_at = datetime.now()
            return True
        return False
