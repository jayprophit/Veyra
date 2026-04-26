"""
Security Hardening Module
Implements fixes for security audit findings
"""

import re
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class SecurityPolicy(Enum):
    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


class SecurityHardening:
    """Security Hardening Manager"""
    
    def __init__(self, policy: SecurityPolicy = SecurityPolicy.STRICT):
        self.policy = policy
    
    def validate_password_policy(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password against NIST SP 800-63B policy"""
        errors = []
        
        if len(password) < 12:
            errors.append("Password must be at least 12 characters")
        if len(password) > 64:
            errors.append("Password must not exceed 64 characters")
        
        common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*]', password))
        
        if sum([has_upper, has_lower, has_digit, has_special]) < 3:
            errors.append("Need 3 of 4: uppercase, lowercase, digits, special")
        
        return len(errors) == 0, errors
    
    def get_rate_limits(self, endpoint: str, user_tier: str = "standard") -> Dict[str, int]:
        """Get rate limits for endpoint"""
        limits = {
            "public": {"per_minute": 30, "per_hour": 500},
            "standard": {"per_minute": 100, "per_hour": 5000},
            "authenticated": {"per_minute": 200, "per_hour": 10000},
            "trading": {"per_minute": 60, "per_hour": 1000},
            "admin": {"per_minute": 300, "per_hour": 20000}
        }
        
        endpoint_tiers = {
            "/api/v1/auth": "public",
            "/api/v1/market": "public",
            "/api/v1/portfolio": "authenticated",
            "/api/v1/trade": "trading",
            "/api/v1/admin": "admin"
        }
        
        tier = "public"
        for path_prefix, path_tier in endpoint_tiers.items():
            if endpoint.startswith(path_prefix):
                tier = path_tier
                break
        
        return limits.get(user_tier, limits["standard"])
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
    
    def mask_pii(self, data: str, pii_type: str) -> str:
        """Mask PII in logs"""
        if not data:
            return ""
        
        if pii_type == "email":
            if '@' in data:
                user, domain = data.split('@')
                masked = user[0] + '*' * (len(user) - 2) + user[-1] if len(user) > 2 else '*'
                return f"{masked}@{domain}"
        
        elif pii_type in ["ssn", "phone"]:
            digits = re.sub(r'\D', '', data)
            if len(digits) >= 4:
                return f"***-***-{digits[-4:]}"
        
        elif pii_type == "credit_card":
            digits = re.sub(r'\D', '', data)
            if len(digits) >= 13:
                return f"****-****-****-{digits[-4:]}"
        
        return '*' * len(data)
    
    def get_encryption_config(self) -> Dict[str, Any]:
        """Get encryption configuration"""
        return {
            "data_at_rest": {"algorithm": "AES-256-GCM", "key_rotation_days": 90},
            "data_in_transit": {"minimum_tls_version": "1.3"},
            "password_hashing": {"algorithm": "Argon2id", "memory_kb": 65536}
        }
