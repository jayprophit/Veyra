"""
KYC/AML Integration Module
=========================
Know Your Customer and Anti-Money Laundering compliance for Veyra
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import re
from collections import defaultdict, deque
import aiohttp

logger = logging.getLogger(__name__)


class KYCStatus(Enum):
    """KYC verification status"""
    NOT_STARTED = "not_started"
    PENDING = "pending"
    IN_REVIEW = "in_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class AMLAlertType(Enum):
    """AML alert types"""
    SUSPICIOUS_TRANSACTION = "suspicious_transaction"
    UNUSUAL_ACTIVITY = "unusual_activity"
    SANCTIONS_MATCH = "sanctions_match"
    PEP_MATCH = "pep_match"
    HIGH_RISK_COUNTRY = "high_risk_country"
    STRUCTURING = "structuring"
    ROUNDING = "rounding"


@dataclass
class KYCDocument:
    """KYC document information"""
    document_id: str
    user_id: str
    document_type: str  # passport, driver_license, id_card, etc.
    document_number: str
    issuing_country: str
    issue_date: datetime
    expiry_date: datetime
    verification_status: str
    verification_method: str
    extracted_data: Dict[str, Any]
    upload_timestamp: datetime
    verified_timestamp: Optional[datetime]


@dataclass
class CustomerProfile:
    """Customer profile for KYC"""
    customer_id: str
    personal_info: Dict[str, Any]
    contact_info: Dict[str, Any]
    financial_info: Dict[str, Any]
    risk_level: RiskLevel
    kyc_status: KYCStatus
    documents: List[KYCDocument]
    created_at: datetime
    updated_at: datetime
    last_reviewed: Optional[datetime]


@dataclass
class AMLAlert:
    """AML alert information"""
    alert_id: str
    customer_id: str
    alert_type: AMLAlertType
    severity: str
    description: str
    transaction_details: Dict[str, Any]
    risk_score: float
    created_at: datetime
    status: str
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    resolution: Optional[str]


@dataclass
class Transaction:
    """Transaction for AML monitoring"""
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    transaction_type: str
    counterpart: str
    timestamp: datetime
    location: str
    risk_score: float
    is_suspicious: bool


class KYCAMLIntegration:
    """KYC and AML integration service"""
    
    def __init__(self):
        self.customer_profiles: Dict[str, CustomerProfile] = {}
        self.aml_alerts: Dict[str, AMLAlert] = {}
        self.transactions: deque = deque(maxlen=1000000)
        self.sanctions_list: Set[str] = set()
        self.pep_list: Set[str] = set()
        self.high_risk_countries: Set[str] = {"IR", "KP", "SY", "AF", "MM", "LR"}
        self.monitoring_rules: Dict[str, Dict[str, Any]] = {}
        
        # Initialize monitoring rules
        self._initialize_monitoring_rules()
        
        # Load sanctions and PEP lists (mock data)
        self._load_watchlists()
        
    def _initialize_monitoring_rules(self):
        """Initialize AML monitoring rules"""
        self.monitoring_rules = {
            "large_transaction": {
                "threshold": 10000,
                "currency": "USD",
                "description": "Large transaction threshold"
            },
            "frequent_small_transactions": {
                "count_threshold": 10,
                "amount_threshold": 1000,
                "time_window_hours": 24,
                "description": "Frequent small transactions"
            },
            "round_amount_transactions": {
                "round_threshold": 0.95,
                "description": "Round amount transactions"
            },
            "high_risk_countries": {
                "countries": self.high_risk_countries,
                "description": "Transactions with high-risk countries"
            },
            "unusual_hours": {
                "start_hour": 22,
                "end_hour": 6,
                "description": "Transactions during unusual hours"
            }
        }
        
    def _load_watchlists(self):
        """Load sanctions and PEP watchlists"""
        # Mock sanctions list (would integrate with actual sanctions databases)
        self.sanctions_list = {
            "ALI QADIM MOHAMMAD AL-ABDALLAH",
            "ABU NIDAL",
            "OSAMA BIN LADEN",
            "AL-QAEDA"
        }
        
        # Mock PEP list (would integrate with actual PEP databases)
        self.pep_list = {
            "JOHN DOE",
            "JANE SMITH",
            "POLITICALLY EXPOSED PERSON 1"
        }
        
    async def create_customer_profile(self, customer_id: str,
                                    personal_info: Dict[str, Any],
                                    contact_info: Dict[str, Any],
                                    financial_info: Dict[str, Any]) -> CustomerProfile:
        """Create new customer profile for KYC"""
        try:
            # Assess initial risk level
            risk_level = await self._assess_customer_risk(personal_info, contact_info, financial_info)
            
            # Create customer profile
            profile = CustomerProfile(
                customer_id=customer_id,
                personal_info=personal_info,
                contact_info=contact_info,
                financial_info=financial_info,
                risk_level=risk_level,
                kyc_status=KYCStatus.NOT_STARTED,
                documents=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_reviewed=None
            )
            
            self.customer_profiles[customer_id] = profile
            
            # Log profile creation
            await self._log_aml_event(
                event_type="customer_profile_created",
                customer_id=customer_id,
                details={
                    "risk_level": risk_level.value,
                    "kyc_status": profile.kyc_status.value
                }
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error creating customer profile: {e}")
            raise
            
    async def upload_kyc_document(self, customer_id: str, document_type: str,
                                document_data: Dict[str, Any]) -> KYCDocument:
        """Upload and process KYC document"""
        try:
            profile = self.customer_profiles.get(customer_id)
            if not profile:
                raise ValueError("Customer profile not found")
                
            # Create document record
            document = KYCDocument(
                document_id=secrets.token_urlsafe(16),
                user_id=customer_id,
                document_type=document_type,
                document_number=document_data.get("document_number", ""),
                issuing_country=document_data.get("issuing_country", ""),
                issue_date=document_data.get("issue_date", datetime.now()),
                expiry_date=document_data.get("expiry_date", datetime.now() + timedelta(days=3650)),
                verification_status="pending",
                verification_method="ocr",
                extracted_data=document_data,
                upload_timestamp=datetime.now(),
                verified_timestamp=None
            )
            
            # Verify document
            verification_result = await self._verify_document(document)
            document.verification_status = verification_result["status"]
            if verification_result["status"] == "verified":
                document.verified_timestamp = datetime.now()
                
            # Add to profile
            profile.documents.append(document)
            profile.updated_at = datetime.now()
            
            # Update KYC status if all documents verified
            await self._update_kyc_status(customer_id)
            
            # Log document upload
            await self._log_aml_event(
                event_type="kyc_document_uploaded",
                customer_id=customer_id,
                details={
                    "document_id": document.document_id,
                    "document_type": document_type,
                    "verification_status": document.verification_status
                }
            )
            
            return document
            
        except Exception as e:
            logger.error(f"Error uploading KYC document: {e}")
            raise
            
    async def _verify_document(self, document: KYCDocument) -> Dict[str, Any]:
        """Verify KYC document using OCR and validation"""
        try:
            # Mock document verification (would integrate with actual OCR/verification services)
            
            # Check document format and structure
            if not document.extracted_data.get("name"):
                return {"status": "rejected", "reason": "Missing name"}
                
            if not document.extracted_data.get("document_number"):
                return {"status": "rejected", "reason": "Missing document number"}
                
            # Check expiry date
            if document.expiry_date < datetime.now():
                return {"status": "rejected", "reason": "Document expired"}
                
            # Check against watchlists
            full_name = document.extracted_data.get("name", "").upper()
            if full_name in self.sanctions_list:
                return {"status": "rejected", "reason": "Match found in sanctions list"}
                
            if full_name in self.pep_list:
                return {"status": "flagged", "reason": "Match found in PEP list"}
                
            return {"status": "verified", "confidence": 0.95}
            
        except Exception as e:
            logger.error(f"Document verification error: {e}")
            return {"status": "error", "reason": str(e)}
            
    async def _update_kyc_status(self, customer_id: str):
        """Update KYC status based on documents"""
        profile = self.customer_profiles.get(customer_id)
        if not profile:
            return
            
        if not profile.documents:
            return
            
        # Check if all documents are verified
        verified_docs = [doc for doc in profile.documents if doc.verification_status == "verified"]
        rejected_docs = [doc for doc in profile.documents if doc.verification_status == "rejected"]
        
        if rejected_docs:
            profile.kyc_status = KYCStatus.REJECTED
        elif len(verified_docs) == len(profile.documents):
            profile.kyc_status = KYCStatus.VERIFIED
        elif verified_docs:
            profile.kyc_status = KYCStatus.IN_REVIEW
        else:
            profile.kyc_status = KYCStatus.PENDING
            
        profile.updated_at = datetime.now()
        
    async def _assess_customer_risk(self, personal_info: Dict[str, Any],
                                  contact_info: Dict[str, Any],
                                  financial_info: Dict[str, Any]) -> RiskLevel:
        """Assess customer risk level"""
        risk_score = 0
        
        # Country risk
        country = personal_info.get("country", "").upper()
        if country in self.high_risk_countries:
            risk_score += 30
            
        # Age risk (simplified)
        birth_date = personal_info.get("birth_date")
        if birth_date:
            age = (datetime.now() - birth_date).days / 365
            if age < 18 or age > 80:
                risk_score += 20
                
        # Occupation risk
        occupation = personal_info.get("occupation", "").lower()
        high_risk_occupations = ["politician", "government official", "cash intensive business"]
        if any(occ in occupation for occ in high_risk_occupations):
            risk_score += 25
            
        # Financial risk
        expected_annual_income = financial_info.get("expected_annual_income", 0)
        if expected_annual_income > 1000000:
            risk_score += 15
        elif expected_annual_income < 10000:
            risk_score += 10
            
        # Determine risk level
        if risk_score >= 60:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 40:
            return RiskLevel.HIGH
        elif risk_score >= 20:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
            
    async def monitor_transaction(self, transaction_data: Dict[str, Any]) -> List[AMLAlert]:
        """Monitor transaction for AML compliance"""
        alerts = []
        
        try:
            # Create transaction record
            transaction = Transaction(
                transaction_id=transaction_data.get("transaction_id", secrets.token_urlsafe(16)),
                customer_id=transaction_data["customer_id"],
                amount=transaction_data["amount"],
                currency=transaction_data["currency"],
                transaction_type=transaction_data["transaction_type"],
                counterpart=transaction_data.get("counterpart", ""),
                timestamp=transaction_data.get("timestamp", datetime.now()),
                location=transaction_data.get("location", ""),
                risk_score=0.0,
                is_suspicious=False
            )
            
            # Add to transaction history
            self.transactions.append(transaction)
            
            # Apply monitoring rules
            rule_alerts = await self._apply_monitoring_rules(transaction)
            alerts.extend(rule_alerts)
            
            # Check against watchlists
            watchlist_alerts = await self._check_watchlists(transaction)
            alerts.extend(watchlist_alerts)
            
            # Behavioral analysis
            behavioral_alerts = await self._behavioral_analysis(transaction)
            alerts.extend(behavioral_alerts)
            
            # Update transaction risk score
            if alerts:
                transaction.risk_score = max(alert.risk_score for alert in alerts)
                transaction.is_suspicious = True
                
            # Log transaction monitoring
            await self._log_aml_event(
                event_type="transaction_monitored",
                customer_id=transaction.customer_id,
                details={
                    "transaction_id": transaction.transaction_id,
                    "amount": transaction.amount,
                    "currency": transaction.currency,
                    "risk_score": transaction.risk_score,
                    "alerts_generated": len(alerts)
                }
            )
            
        except Exception as e:
            logger.error(f"Transaction monitoring error: {e}")
            
        return alerts
        
    async def _apply_monitoring_rules(self, transaction: Transaction) -> List[AMLAlert]:
        """Apply AML monitoring rules to transaction"""
        alerts = []
        
        # Large transaction rule
        large_txn_rule = self.monitoring_rules["large_transaction"]
        if (transaction.currency == large_txn_rule["currency"] and 
            transaction.amount > large_txn_rule["threshold"]):
            
            alerts.append(AMLAlert(
                alert_id=secrets.token_urlsafe(16),
                customer_id=transaction.customer_id,
                alert_type=AMLAlertType.SUSPICIOUS_TRANSACTION,
                severity="high",
                description=f"Large transaction: {transaction.amount} {transaction.currency}",
                transaction_details={
                    "transaction_id": transaction.transaction_id,
                    "amount": transaction.amount,
                    "currency": transaction.currency,
                    "threshold": large_txn_rule["threshold"]
                },
                risk_score=0.8,
                created_at=datetime.now(),
                status="open",
                reviewed_by=None,
                reviewed_at=None,
                resolution=None
            ))
            
        # Frequent small transactions rule
        frequent_rule = self.monitoring_rules["frequent_small_transactions"]
        recent_transactions = [
            tx for tx in self.transactions
            if (tx.customer_id == transaction.customer_id and
                tx.timestamp >= datetime.now() - timedelta(hours=frequent_rule["time_window_hours"]))
        ]
        
        if len(recent_transactions) > frequent_rule["count_threshold"]:
            total_amount = sum(tx.amount for tx in recent_transactions)
            if total_amount > frequent_rule["amount_threshold"]:
                
                alerts.append(AMLAlert(
                    alert_id=secrets.token_urlsafe(16),
                    customer_id=transaction.customer_id,
                    alert_type=AMLAlertType.STRUCTURING,
                    severity="medium",
                    description=f"Frequent small transactions detected",
                    transaction_details={
                        "transaction_count": len(recent_transactions),
                        "total_amount": total_amount,
                        "time_window_hours": frequent_rule["time_window_hours"]
                    },
                    risk_score=0.6,
                    created_at=datetime.now(),
                    status="open",
                    reviewed_by=None,
                    reviewed_at=None,
                    resolution=None
                ))
                
        # Round amount transactions rule
        rounding_rule = self.monitoring_rules["round_amount_transactions"]
        if transaction.amount % 1000 < 100:  # Check if amount is close to round thousand
            alerts.append(AMLAlert(
                alert_id=secrets.token_urlsafe(16),
                customer_id=transaction.customer_id,
                alert_type=AMLAlertType.ROUNDING,
                severity="low",
                description="Round amount transaction detected",
                transaction_details={
                    "transaction_id": transaction.transaction_id,
                    "amount": transaction.amount
                },
                risk_score=0.3,
                created_at=datetime.now(),
                status="open",
                reviewed_by=None,
                reviewed_at=None,
                resolution=None
            ))
            
        return alerts
        
    async def _check_watchlists(self, transaction: Transaction) -> List[AMLAlert]:
        """Check transaction against watchlists"""
        alerts = []
        
        profile = self.customer_profiles.get(transaction.customer_id)
        if not profile:
            return alerts
            
        # Check sanctions list
        customer_name = profile.personal_info.get("name", "").upper()
        if customer_name in self.sanctions_list:
            alerts.append(AMLAlert(
                alert_id=secrets.token_urlsafe(16),
                customer_id=transaction.customer_id,
                alert_type=AMLAlertType.SANCTIONS_MATCH,
                severity="critical",
                description="Customer matches sanctions list",
                transaction_details={
                    "customer_name": customer_name,
                    "transaction_id": transaction.transaction_id
                },
                risk_score=1.0,
                created_at=datetime.now(),
                status="open",
                reviewed_by=None,
                reviewed_at=None,
                resolution=None
            ))
            
        # Check PEP list
        if customer_name in self.pep_list:
            alerts.append(AMLAlert(
                alert_id=secrets.token_urlsafe(16),
                customer_id=transaction.customer_id,
                alert_type=AMLAlertType.PEP_MATCH,
                severity="high",
                description="Customer is a Politically Exposed Person",
                transaction_details={
                    "customer_name": customer_name,
                    "transaction_id": transaction.transaction_id
                },
                risk_score=0.9,
                created_at=datetime.now(),
                status="open",
                reviewed_by=None,
                reviewed_at=None,
                resolution=None
            ))
            
        return alerts
        
    async def _behavioral_analysis(self, transaction: Transaction) -> List[AMLAlert]:
        """Analyze transaction patterns for unusual behavior"""
        alerts = []
        
        # Get customer's transaction history
        customer_transactions = [
            tx for tx in self.transactions
            if tx.customer_id == transaction.customer_id
        ]
        
        if len(customer_transactions) < 5:
            return alerts  # Not enough history for analysis
            
        # Calculate transaction patterns
        amounts = [tx.amount for tx in customer_transactions]
        avg_amount = sum(amounts) / len(amounts)
        
        # Check for unusual transaction amount
        if transaction.amount > avg_amount * 5:
            alerts.append(AMLAlert(
                alert_id=secrets.token_urlsafe(16),
                customer_id=transaction.customer_id,
                alert_type=AMLAlertType.UNUSUAL_ACTIVITY,
                severity="medium",
                description="Unusual transaction amount detected",
                transaction_details={
                    "transaction_amount": transaction.amount,
                    "average_amount": avg_amount,
                    "ratio": transaction.amount / avg_amount
                },
                risk_score=0.5,
                created_at=datetime.now(),
                status="open",
                reviewed_by=None,
                reviewed_at=None,
                resolution=None
            ))
            
        return alerts
        
    async def _log_aml_event(self, event_type: str, customer_id: str,
                           details: Dict[str, Any] = None):
        """Log AML event for audit trail"""
        event = {
            "event_id": secrets.token_urlsafe(16),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "customer_id": customer_id,
            "details": details or {}
        }
        
        # In production, would send to SIEM system or audit log
        logger.info(f"AML Event: {event}")
        
    def get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """Get customer profile"""
        return self.customer_profiles.get(customer_id)
        
    def get_aml_alerts(self, customer_id: Optional[str] = None,
                      status: Optional[str] = None) -> List[AMLAlert]:
        """Get AML alerts with filtering"""
        alerts = list(self.aml_alerts.values())
        
        if customer_id:
            alerts = [alert for alert in alerts if alert.customer_id == customer_id]
            
        if status:
            alerts = [alert for alert in alerts if alert.status == status]
            
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)
        
    def get_transaction_history(self, customer_id: str,
                             since: Optional[datetime] = None) -> List[Transaction]:
        """Get customer transaction history"""
        transactions = [
            tx for tx in self.transactions
            if tx.customer_id == customer_id
        ]
        
        if since:
            transactions = [tx for tx in transactions if tx.timestamp >= since]
            
        return sorted(transactions, key=lambda x: x.timestamp, reverse=True)
        
    async def resolve_alert(self, alert_id: str, resolution: str,
                          reviewed_by: str) -> bool:
        """Resolve AML alert"""
        alert = self.aml_alerts.get(alert_id)
        if not alert:
            return False
            
        alert.status = "resolved"
        alert.resolution = resolution
        alert.reviewed_by = reviewed_by
        alert.reviewed_at = datetime.now()
        
        await self._log_aml_event(
            event_type="alert_resolved",
            customer_id=alert.customer_id,
            details={
                "alert_id": alert_id,
                "resolution": resolution,
                "reviewed_by": reviewed_by
            }
        )
        
        return True


# Global KYC/AML integration instance
_kyc_aml = None

def get_kyc_aml_integration() -> KYCAMLIntegration:
    """Get the global KYC/AML integration instance"""
    global _kyc_aml
    if _kyc_aml is None:
        _kyc_aml = KYCAMLIntegration()
    return _kyc_aml
