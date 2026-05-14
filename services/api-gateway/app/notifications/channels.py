"""Notification Channel Implementations"""
from abc import ABC, abstractmethod
from typing import Dict

class NotificationChannel(ABC):
    @abstractmethod
    async def send(self, recipient: str, message: str, **kwargs) -> bool:
        pass

class EmailChannel(NotificationChannel):
    async def send(self, recipient: str, message: str, subject: str = "", **kwargs) -> bool:
        print(f"[EMAIL] To: {recipient}, Subject: {subject}")
        return True

class SMSChannel(NotificationChannel):
    async def send(self, recipient: str, message: str, **kwargs) -> bool:
        print(f"[SMS] To: {recipient}: {message[:100]}...")
        return True

class PushChannel(NotificationChannel):
    async def send(self, recipient: str, message: str, title: str = "", **kwargs) -> bool:
        print(f"[PUSH] To: {recipient}, Title: {title}")
        return True

class InAppChannel(NotificationChannel):
    async def send(self, recipient: str, message: str, **kwargs) -> bool:
        print(f"[IN_APP] To: {recipient}: {message}")
        return True
