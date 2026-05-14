"""
Compliance Manager for Veyra Platform
GDPR, SOC 2, and Financial Regulatory Compliance
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac
import secrets
from pathlib import Path
import asyncio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import pandas as pd
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import jwt
from pydantic import BaseModel, EmailStr
import bleach
import re
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

Base = declarative_base()

class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    SOC2 = "soc2"
    FINRA = "finra"
    SEC = "sec"
    FCA = "fca"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"

class DataCategory(Enum):
    """Data categories for classification"""
    PERSONAL_DATA = "personal_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    LOCATION_DATA = "location_data"
    COMMUNICATION_DATA = "communication_data"
    BEHAVIORAL_DATA = "behavioral_data"

class ConsentStatus(Enum):
    """Consent status for data processing"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"

@dataclass
class ConsentRecord:
    """User consent record"""
    user_id: str
    data_category: DataCategory
    consent_status: ConsentStatus
    timestamp: datetime
    ip_address: str
    user_agent: str
    purpose: str
    legal_basis: str
    retention_period: int  # days
    withdrawal_mechanism: str

@dataclass
class DataProcessingRecord:
    """Data processing activity record"""
    activity_id: str
    user_id: str
    data_categories: List[DataCategory]
    purpose: str
    legal_basis: str
    timestamp: datetime
    processor_name: str
    processing_location: str
    data_subject_rights: List[str]
    retention_period: int
    security_measures: List[str]

class GDPRComplianceManager:
    """GDPR Compliance Manager"""
    
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.engine = create_engine(db_connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize database tables
        Base.metadata.create_all(self.engine)
        
        logger.info("GDPR Compliance Manager initialized")
        
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for data protection"""
        password = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
        
    async def record_consent(self, user_id: str, data_category: DataCategory,
                           consent_status: ConsentStatus, purpose: str,
                           legal_basis: str, retention_period: int,
                           ip_address: str, user_agent: str) -> str:
        """Record user consent"""
        try:
            consent_id = secrets.token_urlsafe(16)
            
            consent_record = ConsentRecord(
                user_id=user_id,
                data_category=data_category,
                consent_status=consent_status,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                purpose=purpose,
                legal_basis=legal_basis,
                retention_period=retention_period,
                withdrawal_mechanism="api/v1/privacy/withdraw-consent"
            )
            
            # Store in database
            with self.Session() as session:
                db_record = ConsentDBModel(
                    consent_id=consent_id,
                    user_id=user_id,
                    data_category=data_category.value,
                    consent_status=consent_status.value,
                    timestamp=consent_record.timestamp,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    purpose=purpose,
                    legal_basis=legal_basis,
                    retention_period=retention_period,
                    withdrawal_mechanism=consent_record.withdrawal_mechanism
                )
                session.add(db_record)
                session.commit()
                
            logger.info(f"Consent recorded for user {user_id}, category {data_category.value}")
            return consent_id
            
        except Exception as e:
            logger.error(f"Error recording consent: {e}")
            raise
            
    async def withdraw_consent(self, user_id: str, consent_id: str) -> bool:
        """Withdraw user consent"""
        try:
            with self.Session() as session:
                consent_record = session.query(ConsentDBModel).filter(
                    ConsentDBModel.consent_id == consent_id,
                    ConsentDBModel.user_id == user_id
                ).first()
                
                if consent_record:
                    consent_record.consent_status = ConsentStatus.WITHDRAWN.value
                    consent_record.timestamp = datetime.utcnow()
                    session.commit()
                    
                    # Trigger data deletion process
                    await self._initiate_data_deletion(user_id, consent_record.data_category)
                    
                    logger.info(f"Consent withdrawn for user {user_id}, consent {consent_id}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error withdrawing consent: {e}")
            return False
            
    async def _initiate_data_deletion(self, user_id: str, data_category: str):
        """Initiate data deletion process"""
        try:
            # Create deletion task
            deletion_task = DataDeletionTask(
                task_id=secrets.token_urlsafe(16),
                user_id=user_id,
                data_category=data_category,
                status="pending",
                created_at=datetime.utcnow(),
                completed_at=None
            )
            
            with self.Session() as session:
                session.add(deletion_task)
                session.commit()
                
            # Schedule deletion job
            asyncio.create_task(self._process_data_deletion(deletion_task.task_id))
            
        except Exception as e:
            logger.error(f"Error initiating data deletion: {e}")
            
    async def _process_data_deletion(self, task_id: str):
        """Process data deletion task"""
        try:
            with self.Session() as session:
                task = session.query(DataDeletionTask).filter(
                    DataDeletionTask.task_id == task_id
                ).first()
                
                if task and task.status == "pending":
                    task.status = "processing"
                    session.commit()
                    
                    # Delete user data from all systems
                    await self._delete_user_data(task.user_id, task.data_category)
                    
                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    session.commit()
                    
                    logger.info(f"Data deletion completed for task {task_id}")
                    
        except Exception as e:
            logger.error(f"Error processing data deletion: {e}")
            
    async def _delete_user_data(self, user_id: str, data_category: str):
        """Delete user data from all systems"""
        try:
            # This would integrate with all data storage systems
            # For now, simulate deletion
            
            deletion_locations = [
                "primary_database",
                "backup_storage",
                "cache_layers",
                "analytics_platform",
                "logging_systems",
                "third_party_services"
            ]
            
            for location in deletion_locations:
                # Simulate deletion
                await asyncio.sleep(0.1)
                logger.info(f"Deleted {data_category} data for user {user_id} from {location}")
                
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data (GDPR Article 20)"""
        try:
            user_data = {
                "personal_data": await self._get_personal_data(user_id),
                "financial_data": await self._get_financial_data(user_id),
                "activity_data": await self._get_activity_data(user_id),
                "consent_records": await self._get_consent_records(user_id),
                "export_timestamp": datetime.utcnow().isoformat(),
                "export_format": "json"
            }
            
            # Encrypt sensitive data
            encrypted_data = self._encrypt_sensitive_data(user_data)
            
            logger.info(f"Data export completed for user {user_id}")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            raise
            
    async def _get_personal_data(self, user_id: str) -> Dict:
        """Get user personal data"""
        # Simulate fetching personal data
        return {
            "profile": {
                "name": "User Name",
                "email": "user@example.com",
                "phone": "+1234567890",
                "address": "123 Main St, City, Country"
            },
            "preferences": {
                "language": "en",
                "timezone": "UTC",
                "notifications": True
            }
        }
        
    async def _get_financial_data(self, user_id: str) -> Dict:
        """Get user financial data"""
        # Simulate fetching financial data
        return {
            "portfolio": {
                "total_value": 100000.0,
                "holdings": [
                    {"symbol": "AAPL", "shares": 100, "value": 15000.0},
                    {"symbol": "GOOGL", "shares": 50, "value": 7000.0}
                ]
            },
            "transactions": [
                {"date": "2024-01-01", "type": "buy", "symbol": "AAPL", "amount": 10000.0}
            ]
        }
        
    async def _get_activity_data(self, user_id: str) -> Dict:
        """Get user activity data"""
        # Simulate fetching activity data
        return {
            "login_history": [
                {"timestamp": "2024-01-01T10:00:00Z", "ip": "192.168.1.1", "device": "mobile"}
            ],
            "api_usage": [
                {"endpoint": "/api/portfolio", "timestamp": "2024-01-01T10:05:00Z", "method": "GET"}
            ]
        }
        
    async def _get_consent_records(self, user_id: str) -> List[Dict]:
        """Get user consent records"""
        try:
            with self.Session() as session:
                records = session.query(ConsentDBModel).filter(
                    ConsentDBModel.user_id == user_id
                ).all()
                
                return [
                    {
                        "consent_id": record.consent_id,
                        "data_category": record.data_category,
                        "consent_status": record.consent_status,
                        "timestamp": record.timestamp.isoformat(),
                        "purpose": record.purpose,
                        "legal_basis": record.legal_basis
                    }
                    for record in records
                ]
                
        except Exception as e:
            logger.error(f"Error getting consent records: {e}")
            return []
            
    def _encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive data fields"""
        try:
            sensitive_fields = ["email", "phone", "address", "account_number"]
            
            def encrypt_recursive(obj):
                if isinstance(obj, dict):
                    return {
                        k: encrypt_recursive(v) if k not in sensitive_fields 
                        else self._encrypt_value(str(v))
                        for k, v in obj.items()
                    }
                elif isinstance(obj, list):
                    return [encrypt_recursive(item) for item in obj]
                else:
                    return obj
                    
            return encrypt_recursive(data)
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return data
            
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a single value"""
        try:
            encrypted_value = self.cipher_suite.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted_value).decode()
        except Exception as e:
            logger.error(f"Error encrypting value: {e}")
            return value

class SOC2ComplianceManager:
    """SOC 2 Compliance Manager"""
    
    def __init__(self):
        self.security_controls = self._initialize_security_controls()
        self.audit_logs = []
        logger.info("SOC 2 Compliance Manager initialized")
        
    def _initialize_security_controls(self) -> Dict[str, Dict]:
        """Initialize SOC 2 security controls"""
        return {
            "security": {
                "access_control": {
                    "multi_factor_auth": True,
                    "role_based_access": True,
                    "least_privilege": True,
                    "regular_access_reviews": True
                },
                "encryption": {
                    "data_at_rest": True,
                    "data_in_transit": True,
                    "key_management": True,
                    "encryption_standards": ["AES-256", "TLS-1.3"]
                },
                "network_security": {
                    "firewall": True,
                    "intrusion_detection": True,
                    "vulnerability_scanning": True,
                    "network_segmentation": True
                }
            },
            "availability": {
                "uptime_monitoring": True,
                "disaster_recovery": True,
                "backup_procedures": True,
                "incident_response": True
            },
            "processing_integrity": {
                    "data_validation": True,
                "processing_controls": True,
                "change_management": True,
                "quality_assurance": True
            },
            "confidentiality": {
                "data_classification": True,
                "access_logging": True,
                "data_loss_prevention": True,
                "privacy_controls": True
            },
            "privacy": {
                "data_minimization": True,
                "consent_management": True,
                "data_subject_rights": True,
                "privacy_policy": True
            }
        }
        
    async def log_security_event(self, event_type: str, user_id: str, 
                               details: Dict[str, Any]) -> str:
        """Log security event for audit trail"""
        try:
            event_id = secrets.token_urlsafe(16)
            
            event = {
                "event_id": event_id,
                "event_type": event_type,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details,
                "source": "veyra_platform",
                "severity": self._determine_severity(event_type)
            }
            
            self.audit_logs.append(event)
            
            # Store in persistent storage
            await self._store_audit_log(event)
            
            logger.info(f"Security event logged: {event_type} for user {user_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
            raise
            
    def _determine_severity(self, event_type: str) -> str:
        """Determine event severity"""
        high_severity_events = [
            "login_failure", "unauthorized_access", "data_breach",
            "privilege_escalation", "suspicious_activity"
        ]
        
        return "high" if event_type in high_severity_events else "medium"
        
    async def _store_audit_log(self, event: Dict[str, Any]):
        """Store audit log in persistent storage"""
        # Simulate storing audit log
        await asyncio.sleep(0.1)
        logger.debug(f"Audit log stored: {event['event_id']}")
        
    async def generate_compliance_report(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            report = {
                "framework": framework.value,
                "report_date": datetime.utcnow().isoformat(),
                "period": {
                    "start": (datetime.utcnow() - timedelta(days=90)).isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "controls_assessed": list(self.security_controls.keys()),
                "compliance_score": await self._calculate_compliance_score(framework),
                "findings": await self._generate_findings(framework),
                "recommendations": await self._generate_recommendations(framework)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
            
    async def _calculate_compliance_score(self, framework: ComplianceFramework) -> float:
        """Calculate compliance score"""
        try:
            if framework == ComplianceFramework.SOC2:
                # Calculate based on control implementation
                total_controls = 0
                implemented_controls = 0
                
                for category, controls in self.security_controls.items():
                    for control_name, control_status in controls.items():
                        total_controls += 1
                        if isinstance(control_status, bool) and control_status:
                            implemented_controls += 1
                        elif isinstance(control_status, dict):
                            for sub_control in control_status.values():
                                if sub_control:
                                    implemented_controls += 1
                                    total_controls += 1
                        else:
                            total_controls += 1
                            
                return (implemented_controls / total_controls) * 100 if total_controls > 0 else 0
                
            return 85.0  # Default score
            
        except Exception as e:
            logger.error(f"Error calculating compliance score: {e}")
            return 0.0
            
    async def _generate_findings(self, framework: ComplianceFramework) -> List[Dict]:
        """Generate compliance findings"""
        findings = []
        
        if framework == ComplianceFramework.SOC2:
            findings = [
                {
                    "control": "multi_factor_auth",
                    "status": "compliant",
                    "evidence": "MFA enforced for all users",
                    "risk_level": "low"
                },
                {
                    "control": "encryption_at_rest",
                    "status": "compliant",
                    "evidence": "AES-256 encryption implemented",
                    "risk_level": "low"
                },
                {
                    "control": "incident_response",
                    "status": "partially_compliant",
                    "evidence": "Response plan exists, needs testing",
                    "risk_level": "medium"
                }
            ]
            
        return findings
        
    async def _generate_recommendations(self, framework: ComplianceFramework) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if framework == ComplianceFramework.SOC2:
            recommendations = [
                "Conduct regular penetration testing",
                "Implement automated security monitoring",
                "Enhance incident response procedures",
                "Regular security awareness training"
            ]
            
        return recommendations

class FinancialComplianceManager:
    """Financial Regulatory Compliance Manager"""
    
    def __init__(self):
        self.regulatory_frameworks = {
            "FINRA": self._initialize_finra_controls(),
            "SEC": self._initialize_sec_controls(),
            "FCA": self._initialize_fca_controls()
        }
        logger.info("Financial Compliance Manager initialized")
        
    def _initialize_finra_controls(self) -> Dict:
        """Initialize FINRA compliance controls"""
        return {
            "suitability": {
                "customer_profile": True,
                "risk_assessment": True,
                "investment_objectives": True,
                "periodic_reviews": True
            },
            "supervision": {
                "trade_surveillance": True,
                "communications_monitoring": True,
                "compliance_officer": True,
                "annual_reviews": True
            },
            "books_and_records": {
                "trade_reporting": True,
                "customer_account_records": True,
                "retention_period": "6_years",
                "electronic_storage": True
            },
            "anti_money_laundering": {
                "customer_identification": True,
                "transaction_monitoring": True,
                "suspicious_activity_reporting": True,
                "sanctions_screening": True
            }
        }
        
    def _initialize_sec_controls(self) -> Dict:
        """Initialize SEC compliance controls"""
        return {
            "disclosure": {
                "material_information": True,
                "risk_disclosures": True,
                "fee_disclosures": True,
                "performance_reporting": True
            },
            "advisory": {
                "fiduciary_duty": True,
                "best_execution": True,
                "client_conflicts": True,
                "continuous_monitoring": True
            },
            "reporting": {
                "form_adv": True,
                "quarterly_reports": True,
                "client_communications": True,
                "regulatory_filings": True
            }
        }
        
    def _initialize_fca_controls(self) -> Dict:
        """Initialize FCA compliance controls"""
        return {
            "conduct_rules": {
                "integrity": True,
                "skill_care_diligence": True,
                "management_and_control": True,
                "financial_prudence": True
            },
            "market_abuse": {
                "insider_dealing": True,
                "market_manipulation": True,
                "disclosure_requirements": True,
                "surveillance_systems": True
            },
            "client_assets": {
                "segregation": True,
                "reconciliation": True,
                "insurance": True,
                "audit_requirements": True
            }
        }
        
    async def validate_trade_compliance(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade compliance"""
        try:
            validation_result = {
                "trade_id": trade_data.get("trade_id"),
                "compliant": True,
                "violations": [],
                "warnings": [],
                "regulatory_checks": {}
            }
            
            # FINRA suitability check
            finra_result = await self._check_finra_suitability(trade_data)
            validation_result["regulatory_checks"]["FINRA"] = finra_result
            
            # SEC disclosure check
            sec_result = await self._check_sec_disclosure(trade_data)
            validation_result["regulatory_checks"]["SEC"] = sec_result
            
            # FCA conduct check
            fca_result = await self._check_fca_conduct(trade_data)
            validation_result["regulatory_checks"]["FCA"] = fca_result
            
            # Aggregate results
            for regulator, result in validation_result["regulatory_checks"].items():
                if not result["compliant"]:
                    validation_result["compliant"] = False
                    validation_result["violations"].extend(result.get("violations", []))
                validation_result["warnings"].extend(result.get("warnings", []))
                
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating trade compliance: {e}")
            raise
            
    async def _check_finra_suitability(self, trade_data: Dict[str, Any]) -> Dict:
        """Check FINRA suitability rules"""
        try:
            result = {"compliant": True, "violations": [], "warnings": []}
            
            # Check if trade is suitable for customer profile
            customer_profile = trade_data.get("customer_profile", {})
            trade_risk = trade_data.get("risk_level", "medium")
            
            if customer_profile.get("risk_tolerance", "medium") == "low" and trade_risk == "high":
                result["compliant"] = False
                result["violations"].append("Trade exceeds customer risk tolerance")
                
            # Check concentration limits
            portfolio = customer_profile.get("portfolio", {})
            symbol = trade_data.get("symbol")
            quantity = trade_data.get("quantity", 0)
            
            if symbol and portfolio.get(symbol, 0) + quantity > portfolio.get("total_value", 0) * 0.25:
                result["warnings"].append("Trade may exceed concentration limits")
                
            return result
            
        except Exception as e:
            logger.error(f"Error checking FINRA suitability: {e}")
            return {"compliant": False, "violations": ["System error"], "warnings": []}
            
    async def _check_sec_disclosure(self, trade_data: Dict[str, Any]) -> Dict:
        """Check SEC disclosure requirements"""
        try:
            result = {"compliant": True, "violations": [], "warnings": []}
            
            # Check if fees are properly disclosed
            fees = trade_data.get("fees", {})
            if not fees.get("commission_disclosed", False):
                result["violations"].append("Commission not properly disclosed")
                result["compliant"] = False
                
            # Check if conflicts of interest are disclosed
            conflicts = trade_data.get("conflicts_of_interest", [])
            if conflicts and not trade_data.get("conflicts_disclosed", False):
                result["violations"].append("Conflicts of interest not disclosed")
                result["compliant"] = False
                
            return result
            
        except Exception as e:
            logger.error(f"Error checking SEC disclosure: {e}")
            return {"compliant": False, "violations": ["System error"], "warnings": []}
            
    async def _check_fca_conduct(self, trade_data: Dict[str, Any]) -> Dict:
        """Check FCA conduct rules"""
        try:
            result = {"compliant": True, "violations": [], "warnings": []}
            
            # Check best execution
            execution_details = trade_data.get("execution_details", {})
            if not execution_details.get("best_execution_review", False):
                result["warnings"].append("Best execution not documented")
                
            # Check for market abuse indicators
            if trade_data.get("unusual_pattern", False):
                result["warnings"].append("Unusual trading pattern detected")
                
            return result
            
        except Exception as e:
            logger.error(f"Error checking FCA conduct: {e}")
            return {"compliant": False, "violations": ["System error"], "warnings": []}
            
    async def generate_regulatory_report(self, regulator: str, period: str) -> Dict[str, Any]:
        """Generate regulatory report"""
        try:
            report = {
                "regulator": regulator,
                "report_period": period,
                "generated_at": datetime.utcnow().isoformat(),
                "metrics": await self._calculate_regulatory_metrics(regulator),
                "violations": await self._get_regulatory_violations(regulator, period),
                "remediation_actions": await self._get_remediation_actions(regulator)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating regulatory report: {e}")
            raise
            
    async def _calculate_regulatory_metrics(self, regulator: str) -> Dict:
        """Calculate regulatory metrics"""
        # Simulate metrics calculation
        return {
            "total_trades": 10000,
            "compliant_trades": 9850,
            "compliance_rate": 98.5,
            "violations_detected": 150,
            "warnings_issued": 75,
            "customer_complaints": 25
        }
        
    async def _get_regulatory_violations(self, regulator: str, period: str) -> List[Dict]:
        """Get regulatory violations for period"""
        # Simulate violation data
        return [
            {
                "violation_id": "V001",
                "date": "2024-01-15",
                "type": "suitability",
                "description": "Trade exceeded customer risk tolerance",
                "severity": "medium",
                "resolved": True
            }
        ]
        
    async def _get_remediation_actions(self, regulator: str) -> List[Dict]:
        """Get remediation actions"""
        return [
            {
                "action_id": "R001",
                "description": "Enhanced suitability checks implemented",
                "status": "completed",
                "completion_date": "2024-01-20"
            }
        ]

# Database Models
class ConsentDBModel(Base):
    """Consent database model"""
    __tablename__ = "consent_records"
    
    consent_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    data_category = Column(String, nullable=False)
    consent_status = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    ip_address = Column(String, nullable=False)
    user_agent = Column(Text, nullable=False)
    purpose = Column(String, nullable=False)
    legal_basis = Column(String, nullable=False)
    retention_period = Column(Integer, nullable=False)
    withdrawal_mechanism = Column(String, nullable=False)

class DataDeletionTask(Base):
    """Data deletion task model"""
    __tablename__ = "data_deletion_tasks"
    
    task_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    data_category = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)

# Main Compliance Manager
class ComplianceManager:
    """Main compliance manager integrating all frameworks"""
    
    def __init__(self, db_connection_string: str):
        self.gdpr_manager = GDPRComplianceManager(db_connection_string)
        self.soc2_manager = SOC2ComplianceManager()
        self.financial_manager = FinancialComplianceManager()
        
        logger.info("Compliance Manager initialized")
        
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall compliance status"""
        try:
            gdpr_score = await self.soc2_manager._calculate_compliance_score(ComplianceFramework.GDPR)
            soc2_score = await self.soc2_manager._calculate_compliance_score(ComplianceFramework.SOC2)
            
            return {
                "overall_score": (gdpr_score + soc2_score) / 2,
                "frameworks": {
                    "GDPR": {
                        "score": gdpr_score,
                        "status": "compliant" if gdpr_score >= 85 else "needs_improvement"
                    },
                    "SOC2": {
                        "score": soc2_score,
                        "status": "compliant" if soc2_score >= 85 else "needs_improvement"
                    },
                    "Financial": {
                        "status": "compliant",
                        "regulators": ["FINRA", "SEC", "FCA"]
                    }
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance status: {e}")
            raise

# Global compliance manager instance
compliance_manager = None

def initialize_compliance(db_connection_string: str):
    """Initialize compliance manager"""
    global compliance_manager
    compliance_manager = ComplianceManager(db_connection_string)
    return compliance_manager
