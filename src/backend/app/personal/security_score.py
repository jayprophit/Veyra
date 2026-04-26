"""
Security Score Module
Track password strength, 2FA coverage, credit freezes, fraud monitoring
"""
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    CRITICAL = "critical"  # Immediate risk
    HIGH = "high"        # Significant vulnerability
    MEDIUM = "medium"    # Should address
    LOW = "low"          # Minor concern
    GOOD = "good"        # Properly secured


@dataclass
class AccountSecurity:
    account_name: str
    account_type: str  # bank, investment, crypto, email, etc.
    has_2fa: bool
    has_strong_password: bool
    password_last_changed: Optional[date]
    uses_unique_password: bool  # Not reused elsewhere
    uses_password_manager: bool
    has_backup_codes: bool
    is_monitored: bool  # Part of credit monitoring
    last_security_check: datetime
    alerts_enabled: bool


@dataclass
class SecurityIssue:
    category: str
    severity: SecurityLevel
    description: str
    affected_accounts: List[str]
    recommendation: str
    effort_to_fix: str  # quick, medium, complex
    potential_impact: str


@dataclass
class SecurityScore:
    overall_score: int  # 0-100
    category_scores: Dict[str, int]
    risk_level: str  # low, medium, high, critical
    issues: List[SecurityIssue]
    strengths: List[str]
    action_items: List[Dict[str, Any]]
    last_updated: datetime


class SecurityScoreManager:
    """Calculate and track personal security posture"""
    
    def __init__(self):
        self.accounts: Dict[str, AccountSecurity] = {}
        self.credit_frozen: Dict[str, bool] = {  # Agency -> frozen status
            "experian": False,
            "equifax": False,
            "transunion": False
        }
        self.fraud_alerts_active = False
        self.dark_web_alerts: List[Dict[str, Any]] = []
        self.document_inventory: Dict[str, str] = {}  # Document -> storage location
        
    def add_account(
        self,
        name: str,
        account_type: str,
        has_2fa: bool = False,
        password_strength: str = "unknown",
        password_last_changed: Optional[date] = None,
        uses_unique_password: bool = True,
        uses_password_manager: bool = False,
        has_backup_codes: bool = False
    ) -> AccountSecurity:
        """Add account to security tracking"""
        account = AccountSecurity(
            account_name=name,
            account_type=account_type,
            has_2fa=has_2fa,
            has_strong_password=password_strength in ["strong", "very_strong"],
            password_last_changed=password_last_changed,
            uses_unique_password=uses_unique_password,
            uses_password_manager=uses_password_manager,
            has_backup_codes=has_backup_codes,
            is_monitored=False,
            last_security_check=datetime.now(),
            alerts_enabled=True
        )
        
        self.accounts[name] = account
        logger.info(f"Account added to security tracking: {name}")
        return account
    
    def calculate_security_score(self) -> SecurityScore:
        """Calculate overall security score"""
        if not self.accounts:
            return SecurityScore(
                overall_score=0,
                category_scores={},
                risk_level="unknown",
                issues=[],
                strengths=[],
                action_items=[],
                last_updated=datetime.now()
            )
        
        # Category scoring
        scores = {
            "authentication": 0,  # 2FA, strong passwords
            "password_hygiene": 0,  # Unique, manager, rotation
            "monitoring": 0,  # Alerts, credit freeze
            "backup_recovery": 0,  # Backup codes, document storage
            "vigilance": 0  # Last check dates, fraud alerts
        }
        
        issues = []
        strengths = []
        
        # Authentication scoring (30 points max)
        total_accounts = len(self.accounts)
        with_2fa = sum(1 for a in self.accounts.values() if a.has_2fa)
        with_strong = sum(1 for a in self.accounts.values() if a.has_strong_password)
        
        scores["authentication"] = int(((with_2fa / total_accounts * 15) + 
                                        (with_strong / total_accounts * 15)))
        
        if with_2fa == total_accounts:
            strengths.append("2FA enabled on all accounts")
        else:
            missing_2fa = [a.account_name for a in self.accounts.values() if not a.has_2fa]
            issues.append(SecurityIssue(
                category="Authentication",
                severity=SecurityLevel.HIGH,
                description=f"{len(missing_2fa)} accounts without 2FA",
                affected_accounts=missing_2fa,
                recommendation="Enable 2FA on all financial accounts immediately",
                effort_to_fix="quick",
                potential_impact="Prevents 99.9% of account takeovers"
            ))
        
        # Password hygiene (30 points max)
        with_unique = sum(1 for a in self.accounts.values() if a.uses_unique_password)
        with_manager = sum(1 for a in self.accounts.values() if a.uses_password_manager)
        
        # Check password age
        old_passwords = []
        for a in self.accounts.values():
            if a.password_last_changed:
                days_old = (date.today() - a.password_last_changed).days
                if days_old > 365:
                    old_passwords.append((a.account_name, days_old))
        
        scores["password_hygiene"] = int((with_unique / total_accounts * 15) +
                                          (with_manager / total_accounts * 15))
        
        if old_passwords:
            issues.append(SecurityIssue(
                category="Password Hygiene",
                severity=SecurityLevel.MEDIUM,
                description=f"{len(old_passwords)} accounts with passwords over 1 year old",
                affected_accounts=[a[0] for a in old_passwords],
                recommendation="Rotate passwords annually, especially for financial accounts",
                effort_to_fix="medium",
                potential_impact="Reduces exposure from data breaches"
            ))
        
        if with_manager < total_accounts / 2:
            issues.append(SecurityIssue(
                category="Password Management",
                severity=SecurityLevel.MEDIUM,
                description="Not using password manager for most accounts",
                affected_accounts=[],
                recommendation="Use Bitwarden or 1Password for all accounts",
                effort_to_fix="quick",
                potential_impact="Enables strong, unique passwords for all accounts"
            ))
        
        # Monitoring (20 points max)
        frozen_count = sum(1 for v in self.credit_frozen.values() if v)
        scores["monitoring"] = int((frozen_count / 3 * 10) + 
                                    (10 if self.fraud_alerts_active else 0))
        
        if frozen_count < 3:
            unfrozen = [k for k, v in self.credit_frozen.items() if not v]
            issues.append(SecurityIssue(
                category="Credit Protection",
                severity=SecurityLevel.HIGH,
                description=f"Credit not frozen at {', '.join(unfrozen)}",
                affected_accounts=unfrozen,
                recommendation="Freeze credit at all three agencies (free in UK via CRAs)",
                effort_to_fix="quick",
                potential_impact="Prevents new account fraud in your name"
            ))
        else:
            strengths.append("Credit frozen at all three agencies")
        
        # Backup & Recovery (10 points max)
        with_backup = sum(1 for a in self.accounts.values() if a.has_backup_codes)
        scores["backup_recovery"] = int((with_backup / total_accounts * 5) +
                                       (5 if len(self.document_inventory) > 0 else 0))
        
        if not any(a.has_backup_codes for a in self.accounts.values()):
            issues.append(SecurityIssue(
                category="Account Recovery",
                severity=SecurityLevel.MEDIUM,
                description="No backup codes stored for 2FA accounts",
                affected_accounts=[],
                recommendation="Download and securely store backup codes",
                effort_to_fix="quick",
                potential_impact="Prevents lockout if phone is lost"
            ))
        
        # Vigilance (10 points max)
        recently_checked = sum(1 for a in self.accounts.values() 
                               if (datetime.now() - a.last_security_check).days < 30)
        scores["vigilance"] = int(recently_checked / total_accounts * 10)
        
        # Calculate overall
        overall = sum(scores.values())
        
        # Determine risk level
        critical_count = sum(1 for i in issues if i.severity == SecurityLevel.CRITICAL)
        high_count = sum(1 for i in issues if i.severity == SecurityLevel.HIGH)
        
        if critical_count > 0:
            risk_level = "critical"
        elif high_count > 2 or overall < 50:
            risk_level = "high"
        elif overall < 75:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate action items
        action_items = []
        for issue in sorted(issues, key=lambda x: x.severity.value, reverse=True)[:5]:
            action_items.append({
                "priority": issue.severity.value,
                "category": issue.category,
                "action": issue.recommendation,
                "effort": issue.effort_to_fix,
                "impact": issue.potential_impact,
                "accounts": issue.affected_accounts
            })
        
        return SecurityScore(
            overall_score=overall,
            category_scores=scores,
            risk_level=risk_level,
            issues=issues,
            strengths=strengths,
            action_items=action_items,
            last_updated=datetime.now()
        )
    
    def freeze_credit(self, agency: str) -> bool:
        """Mark credit as frozen at agency"""
        if agency in self.credit_frozen:
            self.credit_frozen[agency] = True
            logger.info(f"Credit frozen at {agency}")
            return True
        return False
    
    def thaw_credit(self, agency: str) -> bool:
        """Mark credit as thawed at agency"""
        if agency in self.credit_frozen:
            self.credit_frozen[agency] = False
            logger.info(f"Credit thawed at {agency}")
            return True
        return False
    
    def add_dark_web_alert(self, service: str, data_type: str, date_found: date):
        """Record dark web exposure alert"""
        self.dark_web_alerts.append({
            "service": service,
            "data_type": data_type,
            "date_found": date_found.isoformat(),
            "action_taken": "password_changed" if date_found else None
        })
        logger.warning(f"Dark web alert: {data_type} found on {service}")
    
    def add_document(self, document_type: str, storage_location: str):
        """Track secure document storage"""
        self.document_inventory[document_type] = storage_location
        logger.info(f"Document tracked: {document_type}")
    
    def get_security_checklist(self) -> Dict[str, Any]:
        """Get comprehensive security checklist"""
        score = self.calculate_security_score()
        
        checklist = {
            "critical_actions": [
                item for item in score.action_items 
                if item["priority"] == "critical"
            ],
            "this_week": [
                item for item in score.action_items 
                if item["priority"] in ["high", "medium"] and item["effort"] == "quick"
            ],
            "this_month": [
                item for item in score.action_items 
                if item["priority"] in ["medium", "low"] and item["effort"] in ["quick", "medium"]
            ],
            "maintenance": [
                "Review account access logs monthly",
                "Rotate passwords annually",
                "Verify credit freeze status quarterly",
                "Update document inventory annually"
            ],
            "completed": score.strengths
        }
        
        return checklist


# Global security manager
_security_manager: Optional[SecurityScoreManager] = None


def get_security_manager() -> SecurityScoreManager:
    """Get or create global security manager"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityScoreManager()
    return _security_manager
