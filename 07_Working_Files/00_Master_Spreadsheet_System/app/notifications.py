"""Notification System - Multi-channel alerts and messaging.

Supports:
- Telegram (already implemented in 12_Telegram_Bot.py)
- Email (SMTP)
- Windows native notifications
- Webhook (Discord/Slack)
- Desktop alerts
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import json

logger = logging.getLogger('Notifications')

class NotificationChannel(Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    DESKTOP = "desktop"
    WEBHOOK = "webhook"
    WINDOWS = "windows"

@dataclass
class Notification:
    """Notification message."""
    title: str
    message: str
    priority: str = "normal"  # low, normal, high, critical
    channels: List[NotificationChannel] = None
    data: Optional[Dict] = None

class NotificationManager:
    """Central notification dispatcher."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.enabled_channels: List[NotificationChannel] = []
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment."""
        import os
        
        # Check which channels are configured
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self.enabled_channels.append(NotificationChannel.TELEGRAM)
        
        if os.getenv('SMTP_HOST'):
            self.enabled_channels.append(NotificationChannel.EMAIL)
        
        if os.getenv('WEBHOOK_URL'):
            self.enabled_channels.append(NotificationChannel.WEBHOOK)
        
        # Desktop is always available
        self.enabled_channels.append(NotificationChannel.DESKTOP)
        
        # Windows native if on Windows
        if os.sys.platform == 'win32':
            self.enabled_channels.append(NotificationChannel.WINDOWS)
    
    async def send(self, notification: Notification):
        """Send notification through all configured channels."""
        channels = notification.channels or self.enabled_channels
        
        tasks = []
        for channel in channels:
            if channel in self.enabled_channels:
                tasks.append(self._send_to_channel(channel, notification))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_to_channel(self, channel: NotificationChannel, notification: Notification):
        """Send to specific channel."""
        try:
            if channel == NotificationChannel.TELEGRAM:
                await self._send_telegram(notification)
            elif channel == NotificationChannel.EMAIL:
                await self._send_email(notification)
            elif channel == NotificationChannel.DESKTOP:
                self._send_desktop(notification)
            elif channel == NotificationChannel.WINDOWS:
                self._send_windows(notification)
            elif channel == NotificationChannel.WEBHOOK:
                await self._send_webhook(notification)
        except Exception as e:
            logger.error(f"Failed to send {channel.value} notification: {e}")
    
    async def _send_telegram(self, notification: Notification):
        """Send Telegram notification."""
        from telegram_bot import TelegramBot
        
        bot = TelegramBot()
        emoji = {"low": "ℹ️", "normal": "✅", "high": "⚠️", "critical": "🚨"}
        prefix = emoji.get(notification.priority, "✅")
        
        message = f"{prefix} <b>{notification.title}</b>\n\n{notification.message}"
        
        if notification.data:
            message += f"\n\n<code>{json.dumps(notification.data, indent=2)}</code>"
        
        await bot.send_message(message)
    
    async def _send_email(self, notification: Notification):
        """Send email notification."""
        import os
        
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASS')
        to_email = os.getenv('NOTIFICATION_EMAIL')
        
        if not all([smtp_host, smtp_user, smtp_pass, to_email]):
            logger.warning("Email not configured")
            return
        
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = f"[Financial Master] {notification.title}"
        
        body = f"""
Financial Master Notification

Priority: {notification.priority.upper()}
Title: {notification.title}

{notification.message}
        """
        
        if notification.data:
            body += f"\n\nData:\n{json.dumps(notification.data, indent=2)}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent to {to_email}")
    
    def _send_desktop(self, notification: Notification):
        """Send desktop notification using plyer."""
        try:
            from plyer import notification as plyer_notify
            
            plyer_notify.notify(
                title=notification.title,
                message=notification.message,
                app_name="Financial Master",
                timeout=10
            )
            logger.info("Desktop notification sent")
        except ImportError:
            logger.warning("plyer not installed, skipping desktop notification")
    
    def _send_windows(self, notification: Notification):
        """Send Windows 10/11 native notification."""
        try:
            from win10toast import ToastNotifier
            
            toaster = ToastNotifier()
            toaster.show_toast(
                notification.title,
                notification.message,
                duration=10,
                threaded=True
            )
            logger.info("Windows notification sent")
        except ImportError:
            logger.warning("win10toast not installed, skipping Windows notification")
    
    async def _send_webhook(self, notification: Notification):
        """Send webhook notification (Discord/Slack)."""
        import os
        import aiohttp
        
        webhook_url = os.getenv('WEBHOOK_URL')
        if not webhook_url:
            return
        
        # Discord format
        payload = {
            "embeds": [{
                "title": notification.title,
                "description": notification.message,
                "color": 3447003 if notification.priority == "normal" else 15158332,
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "Financial Master"}
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as resp:
                if resp.status == 204:
                    logger.info("Webhook notification sent")
                else:
                    logger.error(f"Webhook failed: {resp.status}")

# Pre-configured notification helpers

class AlertTemplates:
    """Common alert templates."""
    
    @staticmethod
    def portfolio_alert(change_percent: float, portfolio_value: float) -> Notification:
        """Portfolio change alert."""
        if change_percent > 5:
            priority = "high"
            title = "🚀 Portfolio Surging!"
        elif change_percent < -5:
            priority = "critical"
            title = "📉 Portfolio Dropping!"
        else:
            priority = "normal"
            title = "📊 Daily Portfolio Update"
        
        return Notification(
            title=title,
            message=f"Portfolio value: £{portfolio_value:,.2f} ({change_percent:+.2f}%)",
            priority=priority,
            channels=[NotificationChannel.TELEGRAM, NotificationChannel.DESKTOP]
        )
    
    @staticmethod
    def tax_loss_opportunity(ticker: str, unrealized_loss: float) -> Notification:
        """Tax-loss harvesting opportunity."""
        return Notification(
            title="💰 Tax-Loss Opportunity",
            message=f"{ticker} has £{unrealized_loss:,.2f} unrealized loss",
            priority="high",
            channels=[NotificationChannel.TELEGRAM, NotificationChannel.EMAIL],
            data={"ticker": ticker, "loss": unrealized_loss}
        )
    
    @staticmethod
    def system_health_alert(status: str, details: Dict) -> Notification:
        """System health warning."""
        return Notification(
            title="⚠️ System Health Alert",
            message=f"System status: {status}",
            priority="critical" if status == "critical" else "high",
            channels=[NotificationChannel.TELEGRAM, NotificationChannel.EMAIL],
            data=details
        )
    
    @staticmethod
    def agent_completed(agent_name: str, result: str) -> Notification:
        """Agent task completed."""
        return Notification(
            title=f"🤖 Agent Complete: {agent_name}",
            message=result,
            priority="normal",
            channels=[NotificationChannel.DESKTOP]
        )

# Global notification manager
_notification_manager: Optional[NotificationManager] = None

def get_notification_manager() -> NotificationManager:
    """Get or create global notification manager."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager

async def send_notification(title: str, message: str, priority: str = "normal", **kwargs):
    """Quick helper to send notification."""
    nm = get_notification_manager()
    notification = Notification(
        title=title,
        message=message,
        priority=priority,
        **kwargs
    )
    await nm.send(notification)

if __name__ == "__main__":
    # Example usage
    import os
    
    # Test notification
    async def test():
        nm = NotificationManager()
        
        # Test different priorities
        for priority in ["low", "normal", "high", "critical"]:
            await send_notification(
                title=f"Test {priority.title()}",
                message=f"This is a {priority} priority test message.",
                priority=priority
            )
            await asyncio.sleep(1)
    
    # Run test
    print("Sending test notifications...")
    print("(Configure TELEGRAM_BOT_TOKEN, SMTP_HOST, or WEBHOOK_URL for real delivery)")
    
    asyncio.run(test())
    print("Done!")
