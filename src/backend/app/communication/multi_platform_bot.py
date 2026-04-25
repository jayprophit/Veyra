"""Multi-Platform Communication Bots"""
from typing import Dict, Optional
from abc import ABC, abstractmethod

class MessageBot(ABC):
    """Base class for all platform bots"""
    
    @abstractmethod
    def send_message(self, user_id: str, message: str) -> bool:
        pass
    
    @abstractmethod
    def get_status(self) -> Dict:
        pass

class WhatsAppBot(MessageBot):
    """WhatsApp Business API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://graph.facebook.com/v18.0"
        self.connected = False
    
    def send_message(self, user_id: str, message: str) -> bool:
        # WhatsApp Business API implementation
        print(f"[WhatsApp] To {user_id}: {message[:50]}...")
        return True
    
    def get_status(self) -> Dict:
        return {"platform": "WhatsApp", "connected": self.connected}

class SignalBot(MessageBot):
    """Signal CLI integration"""
    
    def __init__(self, phone_number: str):
        self.phone = phone_number
        self.connected = False
    
    def send_message(self, user_id: str, message: str) -> bool:
        # Signal CLI implementation
        print(f"[Signal] To {user_id}: {message[:50]}...")
        return True
    
    def get_status(self) -> Dict:
        return {"platform": "Signal", "connected": self.connected}

class SlackBot(MessageBot):
    """Slack Web API integration"""
    
    def __init__(self, bot_token: str):
        self.token = bot_token
        self.connected = True
    
    def send_message(self, channel: str, message: str) -> bool:
        # Slack API implementation
        print(f"[Slack] To #{channel}: {message[:50]}...")
        return True
    
    def get_status(self) -> Dict:
        return {"platform": "Slack", "connected": self.connected}

class UnifiedCommunicator:
    """Manages all platform communications"""
    
    def __init__(self):
        self.bots = {}
        self.preferred_order = ["telegram", "whatsapp", "signal", "slack"]
    
    def add_bot(self, name: str, bot: MessageBot):
        self.bots[name] = bot
    
    def send_alert(self, message: str, priority: str = "normal") -> Dict[str, bool]:
        """Send to all available platforms"""
        results = {}
        for name, bot in self.bots.items():
            results[name] = bot.send_message("user", f"[{priority.upper()}] {message}")
        return results
    
    def get_all_status(self) -> Dict:
        return {name: bot.get_status() for name, bot in self.bots.items()}
