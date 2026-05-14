"""Sentry Error Monitoring - Production error tracking"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from typing import Dict, Optional
import os

class SentryManager:
    """SSS-Grade error monitoring with Sentry"""
    
    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or os.getenv("SENTRY_DSN")
        self.enabled = bool(self.dsn)
        
        if self.enabled:
            sentry_sdk.init(
                dsn=self.dsn,
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
                integrations=[
                    FastApiIntegration(),
                ],
                environment=os.getenv("ENVIRONMENT", "production"),
                release=os.getenv("RELEASE", "unknown"),
                send_default_pii=False
            )
    
    def capture_exception(self, exception: Exception, context: Dict = None):
        """Capture and send exception to Sentry"""
        if not self.enabled:
            return
        
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_exception(exception)
    
    def capture_message(self, message: str, level: str = "info"):
        """Send custom message to Sentry"""
        if not self.enabled:
            return
        
        sentry_sdk.capture_message(message, level=level)
    
    def set_user(self, user_id: str, email: str = None):
        """Set user context"""
        if not self.enabled:
            return
        
        sentry_sdk.set_user({
            "id": user_id,
            "email": email
        })
    
    def start_transaction(self, name: str, op: str = "http"):
        """Start performance monitoring transaction"""
        if not self.enabled:
            return None
        
        return sentry_sdk.start_transaction(
            name=name,
            op=op
        )

print("Sentry Monitoring loaded")
