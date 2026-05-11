"""
Enterprise Alerting System
==========================
Advanced alerting with multiple channels and intelligent routing
"""

import asyncio
import json
import smtplib
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import aiohttp
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    FIRING = "firing"
    RESOLVED = "resolved"
    SILENCED = "silenced"


@dataclass
class Alert:
    name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    description: str
    timestamp: datetime
    labels: Dict[str, str]
    annotations: Dict[str, str]
    start_time: datetime
    end_time: Optional[datetime] = None
    fingerprint: Optional[str] = None


@dataclass
class AlertRule:
    name: str
    condition: str  # PromQL-like condition
    severity: AlertSeverity
    message: str
    description: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    for_duration: timedelta
    enabled: bool = True


@dataclass
class AlertChannel:
    name: str
    type: str  # email, slack, pagerduty, webhook, etc.
    config: Dict[str, Any]
    enabled: bool = True
    rate_limit: Optional[timedelta] = None


class AlertingSystem:
    """Enterprise alerting system with multiple channels"""
    
    def __init__(self, service_name: str = "veyra"):
        self.service_name = service_name
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.channels: Dict[str, AlertChannel] = {}
        self.silences: Dict[str, datetime] = {}
        self.evaluation_interval = 30  # seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.channel_last_sent: Dict[str, datetime] = {}
        
    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.rules[rule.name] = rule
        
    def add_channel(self, channel: AlertChannel):
        """Add an alert channel"""
        self.channels[channel.name] = channel
        
    def add_silence(self, alert_fingerprint: str, duration: timedelta):
        """Add a silence for an alert"""
        self.silences[alert_fingerprint] = datetime.now() + duration
        
    async def start(self):
        """Start alerting system"""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._evaluation_loop())
        logger.info("Alerting system started")
        
    async def stop(self):
        """Stop alerting system"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Alerting system stopped")
        
    async def _evaluation_loop(self):
        """Background evaluation loop"""
        while self._running:
            try:
                await self._evaluate_rules()
                await self._cleanup_expired_silences()
                await asyncio.sleep(self.evaluation_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alerting evaluation loop: {e}")
                await asyncio.sleep(5)
                
    async def _evaluate_rules(self):
        """Evaluate all alert rules"""
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            try:
                # This would evaluate the rule condition
                # For now, we'll simulate rule evaluation
                is_firing = await self._evaluate_condition(rule.condition)
                
                fingerprint = self._generate_fingerprint(rule.name, rule.labels)
                
                if is_firing:
                    await self._handle_firing_alert(rule, fingerprint)
                else:
                    await self._handle_resolved_alert(rule, fingerprint)
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
                
    async def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a rule condition"""
        # This would implement PromQL-like evaluation
        # For now, we'll return False (no alerts)
        return False
        
    async def _handle_firing_alert(self, rule: AlertRule, fingerprint: str):
        """Handle a firing alert"""
        now = datetime.now()
        
        if fingerprint in self.alerts:
            # Update existing alert
            alert = self.alerts[fingerprint]
            alert.status = AlertStatus.FIRING
            alert.timestamp = now
        else:
            # Create new alert
            alert = Alert(
                name=rule.name,
                severity=rule.severity,
                status=AlertStatus.FIRING,
                message=rule.message,
                description=rule.description,
                timestamp=now,
                start_time=now,
                labels=rule.labels,
                annotations=rule.annotations,
                fingerprint=fingerprint
            )
            self.alerts[fingerprint] = alert
            
        # Check if alert should be sent
        if self._should_send_alert(alert, fingerprint):
            await self._send_alert(alert)
            
    async def _handle_resolved_alert(self, rule: AlertRule, fingerprint: str):
        """Handle a resolved alert"""
        if fingerprint in self.alerts:
            alert = self.alerts[fingerprint]
            if alert.status == AlertStatus.FIRING:
                alert.status = AlertStatus.RESOLVED
                alert.end_time = datetime.now()
                await self._send_alert(alert)
                
    def _should_send_alert(self, alert: Alert, fingerprint: str) -> bool:
        """Check if alert should be sent"""
        # Check if alert is silenced
        if fingerprint in self.silences:
            if datetime.now() < self.silences[fingerprint]:
                return False
            else:
                del self.silences[fingerprint]
                
        # Check rate limiting for each channel
        for channel in self.channels.values():
            if not channel.enabled:
                continue
                
            if channel.rate_limit:
                last_sent = self.channel_last_sent.get(channel.name)
                if last_sent and (datetime.now() - last_sent) < channel.rate_limit:
                    return False
                    
        return True
        
    async def _send_alert(self, alert: Alert):
        """Send alert to all configured channels"""
        for channel in self.channels.values():
            if not channel.enabled:
                continue
                
            try:
                if channel.type == "email":
                    await self._send_email_alert(channel, alert)
                elif channel.type == "slack":
                    await self._send_slack_alert(channel, alert)
                elif channel.type == "webhook":
                    await self._send_webhook_alert(channel, alert)
                elif channel.type == "pagerduty":
                    await self._send_pagerduty_alert(channel, alert)
                    
                # Update rate limiting
                self.channel_last_sent[channel.name] = datetime.now()
                
            except Exception as e:
                logger.error(f"Error sending alert to {channel.name}: {e}")
                
    async def _send_email_alert(self, channel: AlertChannel, alert: Alert):
        """Send email alert"""
        config = channel.config
        
        msg = MimeMultipart()
        msg['From'] = config['from']
        msg['To'] = config['to']
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.name}"
        
        body = f"""
Alert: {alert.name}
Severity: {alert.severity.value}
Status: {alert.status.value}
Time: {alert.timestamp.isoformat()}

Description:
{alert.description}

Labels:
{json.dumps(alert.labels, indent=2)}

Annotations:
{json.dumps(alert.annotations, indent=2)}
"""
        
        msg.attach(MimeText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(config['smtp_host'], config['smtp_port'])
            if config.get('use_tls'):
                server.starttls()
            if config.get('username'):
                server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
        except Exception as e:
            raise Exception(f"Failed to send email: {e}")
            
    async def _send_slack_alert(self, channel: AlertChannel, alert: Alert):
        """Send Slack alert"""
        config = channel.config
        
        color_map = {
            AlertSeverity.INFO: "good",
            AlertSeverity.WARNING: "warning",
            AlertSeverity.ERROR: "danger",
            AlertSeverity.CRITICAL: "danger"
        }
        
        payload = {
            "attachments": [{
                "color": color_map.get(alert.severity, "warning"),
                "title": f"{alert.severity.value.upper()}: {alert.name}",
                "text": alert.description,
                "fields": [
                    {"title": "Status", "value": alert.status.value, "short": True},
                    {"title": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), "short": True}
                ],
                "footer": "Veyra",
                "ts": int(alert.timestamp.timestamp())
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(config['webhook_url'], json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Slack API returned status {response.status}")
                    
    async def _send_webhook_alert(self, channel: AlertChannel, alert: Alert):
        """Send webhook alert"""
        config = channel.config
        
        payload = {
            "alert": asdict(alert),
            "service": self.service_name
        }
        
        headers = config.get('headers', {})
        
        async with aiohttp.ClientSession() as session:
            async with session.post(config['url'], json=payload, headers=headers) as response:
                if response.status not in [200, 201, 202]:
                    raise Exception(f"Webhook returned status {response.status}")
                    
    async def _send_pagerduty_alert(self, channel: AlertChannel, alert: Alert):
        """Send PagerDuty alert"""
        config = channel.config
        
        severity_map = {
            AlertSeverity.INFO: "info",
            AlertSeverity.WARNING: "warning",
            AlertSeverity.ERROR: "error",
            AlertSeverity.CRITICAL: "critical"
        }
        
        payload = {
            "routing_key": config['routing_key'],
            "event_action": "trigger" if alert.status == AlertStatus.FIRING else "resolve",
            "payload": {
                "summary": alert.name,
                "source": self.service_name,
                "severity": severity_map.get(alert.severity, "warning"),
                "timestamp": alert.timestamp.isoformat(),
                "custom_details": {
                    "description": alert.description,
                    "labels": alert.labels,
                    "annotations": alert.annotations
                }
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://events.pagerduty.com/v2/enqueue", json=payload) as response:
                if response.status != 202:
                    raise Exception(f"PagerDuty API returned status {response.status}")
                    
    def _generate_fingerprint(self, name: str, labels: Dict[str, str]) -> str:
        """Generate alert fingerprint"""
        import hashlib
        label_str = json.dumps(sorted(labels.items()), sort_keys=True)
        content = f"{name}:{label_str}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
        
    async def _cleanup_expired_silences(self):
        """Clean up expired silences"""
        now = datetime.now()
        expired = [fp for fp, end_time in self.silences.items() if now >= end_time]
        for fp in expired:
            del self.silences[fp]
            
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.alerts.values() if alert.status == AlertStatus.FIRING]
        
    def get_alert_history(self, since: Optional[datetime] = None) -> List[Alert]:
        """Get alert history"""
        if since:
            return [alert for alert in self.alerts.values() if alert.start_time >= since]
        return list(self.alerts.values())


# Global alerting system instance
_alerting_system = None

def get_alerting_system() -> AlertingSystem:
    """Get the global alerting system instance"""
    global _alerting_system
    if _alerting_system is None:
        _alerting_system = AlertingSystem()
        
        # Add default channels (would be configured from environment)
        try:
            _alerting_system.add_channel(AlertChannel(
                name="default_email",
                type="email",
                config={
                    "smtp_host": "localhost",
                    "smtp_port": 587,
                    "from": "alerts@veyra.com",
                    "to": "admin@veyra.com",
                    "use_tls": True
                }
            ))
        except Exception:
            pass
            
    return _alerting_system


# Convenience functions for creating alerts
async def trigger_alert(name: str, severity: AlertSeverity, message: str, 
                       description: str = "", labels: Optional[Dict[str, str]] = None,
                       annotations: Optional[Dict[str, str]] = None):
    """Trigger a manual alert"""
    alerting = get_alerting_system()
    
    fingerprint = alerting._generate_fingerprint(name, labels or {})
    alert = Alert(
        name=name,
        severity=severity,
        status=AlertStatus.FIRING,
        message=message,
        description=description,
        timestamp=datetime.now(),
        start_time=datetime.now(),
        labels=labels or {},
        annotations=annotations or {},
        fingerprint=fingerprint
    )
    
    alerting.alerts[fingerprint] = alert
    await alerting._send_alert(alert)


async def resolve_alert(name: str, labels: Optional[Dict[str, str]] = None):
    """Resolve a manual alert"""
    alerting = get_alerting_system()
    
    fingerprint = alerting._generate_fingerprint(name, labels or {})
    if fingerprint in alerting.alerts:
        alert = alerting.alerts[fingerprint]
        alert.status = AlertStatus.RESOLVED
        alert.end_time = datetime.now()
        await alerting._send_alert(alert)
