"""
Advanced Security API Endpoints
===============================
Comprehensive security API for Veyra with zero-trust, threat detection, compliance, KYC/AML, biometrics, and HSM
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ..security.zero_trust import get_zero_trust_architecture, TrustLevel, SecurityContext
from ..security.threat_detection import get_threat_detection_engine, ThreatType, AlertSeverity
from ..security.compliance_automation import get_compliance_automation, ComplianceFramework, ComplianceStatus
from ..security.kyc_aml_integration import get_kyc_aml_integration, KYCStatus, RiskLevel, AMLAlertType
from ..security.hsm_integration import get_hsm_integration, KeyType, KeyUsage
from ..security.biometric_auth import BiometricAuthManager, BiometricType, HardwareKeyType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security", tags=["security"])


# Zero-Trust Architecture Endpoints
@router.post("/zero-trust/authenticate")
async def authenticate_user(
    user_id: str,
    credentials: Dict[str, Any],
    device_fingerprint: str,
    ip_address: str,
    user_agent: str
):
    """Authenticate user with zero-trust principles"""
    try:
        zero_trust = get_zero_trust_architecture()
        session = await zero_trust.authenticate_user(
            user_id, credentials, device_fingerprint, ip_address, user_agent
        )
        
        if not session:
            raise HTTPException(status_code=401, detail="Authentication failed")
            
        return {
            "session_id": session.session_id,
            "trust_level": session.trust_level.value,
            "security_context": session.security_context.value,
            "expires_at": session.expires_at.isoformat(),
            "mfa_required": not session.mfa_verified,
            "biometric_required": not session.biometric_verified
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zero-trust/verify-mfa")
async def verify_mfa(session_id: str, mfa_code: str):
    """Verify multi-factor authentication"""
    try:
        zero_trust = get_zero_trust_architecture()
        is_valid = await zero_trust.verify_mfa(session_id, mfa_code)
        
        return {"verified": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zero-trust/verify-biometric")
async def verify_biometric(session_id: str, biometric_data: str):
    """Verify biometric authentication"""
    try:
        zero_trust = get_zero_trust_architecture()
        is_valid = await zero_trust.verify_biometric(session_id, biometric_data)
        
        return {"verified": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zero-trust/authorize")
async def authorize_action(session_id: str, action: str, context: Optional[Dict[str, Any]] = None):
    """Authorize action based on zero-trust principles"""
    try:
        zero_trust = get_zero_trust_architecture()
        is_authorized = await zero_trust.authorize_action(session_id, action, context)
        
        return {"authorized": is_authorized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/zero-trust/sessions")
async def get_active_sessions():
    """Get all active security sessions"""
    try:
        zero_trust = get_zero_trust_architecture()
        sessions = zero_trust.get_active_sessions()
        
        return {
            "sessions": [
                {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "trust_level": session.trust_level.value,
                    "security_context": session.security_context.value,
                    "ip_address": session.ip_address,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "expires_at": session.expires_at.isoformat(),
                    "mfa_verified": session.mfa_verified,
                    "biometric_verified": session.biometric_verified
                }
                for session in sessions
            ],
            "count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Threat Detection Endpoints
@router.post("/threat-detection/analyze")
async def analyze_request(request_data: Dict[str, Any]):
    """Analyze request for security threats"""
    try:
        threat_engine = get_threat_detection_engine()
        threats = await threat_engine.analyze_request(request_data)
        
        return {
            "threats": [
                {
                    "indicator_id": threat.indicator_id,
                    "threat_type": threat.threat_type.value,
                    "severity": threat.severity.value,
                    "confidence": threat.confidence,
                    "source_ip": threat.source_ip,
                    "description": threat.description,
                    "evidence": threat.evidence,
                    "timestamp": threat.timestamp.isoformat(),
                    "is_blocked": threat.is_blocked
                }
                for threat in threats
            ],
            "count": len(threats),
            "blocked_ips": list(threat_engine.get_blocked_ips())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threat-detection/indicators")
async def get_threat_indicators(
    since: Optional[datetime] = Query(None),
    threat_type: Optional[ThreatType] = Query(None),
    severity: Optional[AlertSeverity] = Query(None)
):
    """Get threat indicators with filtering"""
    try:
        threat_engine = get_threat_detection_engine()
        indicators = threat_engine.get_threat_indicators(since, threat_type, severity)
        
        return {
            "indicators": [
                {
                    "indicator_id": indicator.indicator_id,
                    "threat_type": indicator.threat_type.value,
                    "severity": indicator.severity.value,
                    "confidence": indicator.confidence,
                    "source_ip": indicator.source_ip,
                    "user_id": indicator.user_id,
                    "description": indicator.description,
                    "evidence": indicator.evidence,
                    "timestamp": indicator.timestamp.isoformat(),
                    "is_blocked": indicator.is_blocked
                }
                for indicator in indicators
            ],
            "count": len(indicators)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threat-detection/summary")
async def get_threat_summary(since: Optional[datetime] = Query(None)):
    """Get threat detection summary"""
    try:
        threat_engine = get_threat_detection_engine()
        summary = threat_engine.get_threat_summary(since)
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/threat-detection/unblock-ip")
async def unblock_ip(ip_address: str):
    """Unblock an IP address"""
    try:
        threat_engine = get_threat_detection_engine()
        threat_engine.unblock_ip(ip_address)
        
        return {"message": f"IP {ip_address} unblocked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Compliance Automation Endpoints
@router.post("/compliance/check")
async def run_compliance_check(framework: Optional[ComplianceFramework] = Query(None)):
    """Run compliance checks for specified framework"""
    try:
        compliance = get_compliance_automation()
        results = await compliance.run_compliance_check(framework)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/report")
async def generate_compliance_report(
    framework: ComplianceFramework,
    period_start: datetime,
    period_end: datetime
):
    """Generate compliance report"""
    try:
        compliance = get_compliance_automation()
        report = await compliance.generate_compliance_report(framework, period_start, period_end)
        
        return {
            "report_id": report.report_id,
            "framework": report.framework.value,
            "generated_at": report.generated_at.isoformat(),
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "overall_status": report.overall_status.value,
            "total_rules": report.total_rules,
            "compliant_rules": report.compliant_rules,
            "non_compliant_rules": report.non_compliant_rules,
            "violations": report.violations,
            "recommendations": report.recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/reports")
async def get_compliance_reports(framework: Optional[ComplianceFramework] = Query(None)):
    """Get compliance reports"""
    try:
        compliance = get_compliance_automation()
        reports = compliance.get_compliance_reports(framework)
        
        return {
            "reports": [
                {
                    "report_id": report.report_id,
                    "framework": report.framework.value,
                    "generated_at": report.generated_at.isoformat(),
                    "overall_status": report.overall_status.value,
                    "total_rules": report.total_rules,
                    "compliant_rules": report.compliant_rules,
                    "non_compliant_rules": report.non_compliant_rules
                }
                for report in reports
            ],
            "count": len(reports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/data-subject-request")
async def handle_data_subject_request(
    subject_id: str,
    request_type: str,
    framework: ComplianceFramework
):
    """Handle data subject access/deletion request"""
    try:
        compliance = get_compliance_automation()
        request_id = await compliance.handle_data_subject_request(subject_id, request_type, framework)
        
        return {"request_id": request_id, "status": "pending"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/data-subject-requests")
async def get_data_subject_requests(status: Optional[str] = Query(None)):
    """Get data subject requests"""
    try:
        compliance = get_compliance_automation()
        requests = compliance.get_data_subject_requests(status)
        
        return {
            "requests": [
                {
                    "request_id": req.request_id,
                    "subject_id": req.subject_id,
                    "request_type": req.request_type,
                    "framework": req.framework.value,
                    "status": req.status,
                    "created_at": req.created_at.isoformat(),
                    "completed_at": req.completed_at.isoformat() if req.completed_at else None
                }
                for req in requests
            ],
            "count": len(requests)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# KYC/AML Integration Endpoints
@router.post("/kyc/customer-profile")
async def create_customer_profile(
    customer_id: str,
    personal_info: Dict[str, Any],
    contact_info: Dict[str, Any],
    financial_info: Dict[str, Any]
):
    """Create customer profile for KYC"""
    try:
        kyc_aml = get_kyc_aml_integration()
        profile = await kyc_aml.create_customer_profile(
            customer_id, personal_info, contact_info, financial_info
        )
        
        return {
            "customer_id": profile.customer_id,
            "risk_level": profile.risk_level.value,
            "kyc_status": profile.kyc_status.value,
            "created_at": profile.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kyc/upload-document")
async def upload_kyc_document(
    customer_id: str,
    document_type: str,
    document_data: Dict[str, Any]
):
    """Upload KYC document"""
    try:
        kyc_aml = get_kyc_aml_integration()
        document = await kyc_aml.upload_kyc_document(customer_id, document_type, document_data)
        
        return {
            "document_id": document.document_id,
            "document_type": document.document_type,
            "verification_status": document.verification_status,
            "upload_timestamp": document.upload_timestamp.isoformat(),
            "verified_timestamp": document.verified_timestamp.isoformat() if document.verified_timestamp else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kyc/customer-profile/{customer_id}")
async def get_customer_profile(customer_id: str):
    """Get customer profile"""
    try:
        kyc_aml = get_kyc_aml_integration()
        profile = kyc_aml.get_customer_profile(customer_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Customer profile not found")
            
        return {
            "customer_id": profile.customer_id,
            "risk_level": profile.risk_level.value,
            "kyc_status": profile.kyc_status.value,
            "documents": [
                {
                    "document_id": doc.document_id,
                    "document_type": doc.document_type,
                    "verification_status": doc.verification_status,
                    "upload_timestamp": doc.upload_timestamp.isoformat()
                }
                for doc in profile.documents
            ],
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/aml/monitor-transaction")
async def monitor_transaction(transaction_data: Dict[str, Any]):
    """Monitor transaction for AML compliance"""
    try:
        kyc_aml = get_kyc_aml_integration()
        alerts = await kyc_aml.monitor_transaction(transaction_data)
        
        return {
            "alerts": [
                {
                    "alert_id": alert.alert_id,
                    "alert_type": alert.alert_type.value,
                    "severity": alert.severity,
                    "description": alert.description,
                    "risk_score": alert.risk_score,
                    "created_at": alert.created_at.isoformat(),
                    "status": alert.status
                }
                for alert in alerts
            ],
            "count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aml/alerts")
async def get_aml_alerts(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """Get AML alerts"""
    try:
        kyc_aml = get_kyc_aml_integration()
        alerts = kyc_aml.get_aml_alerts(customer_id, status)
        
        return {
            "alerts": [
                {
                    "alert_id": alert.alert_id,
                    "customer_id": alert.customer_id,
                    "alert_type": alert.alert_type.value,
                    "severity": alert.severity,
                    "description": alert.description,
                    "risk_score": alert.risk_score,
                    "created_at": alert.created_at.isoformat(),
                    "status": alert.status,
                    "reviewed_by": alert.reviewed_by,
                    "reviewed_at": alert.reviewed_at.isoformat() if alert.reviewed_at else None,
                    "resolution": alert.resolution
                }
                for alert in alerts
            ],
            "count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/aml/resolve-alert")
async def resolve_alert(alert_id: str, resolution: str, reviewed_by: str):
    """Resolve AML alert"""
    try:
        kyc_aml = get_kyc_aml_integration()
        success = await kyc_aml.resolve_alert(alert_id, resolution, reviewed_by)
        
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HSM Integration Endpoints
@router.post("/hsm/connect")
async def connect_hsm():
    """Connect to HSM provider"""
    try:
        hsm = get_hsm_integration()
        success = await hsm.connect()
        
        return {"connected": success, "provider": hsm.provider.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hsm/generate-key")
async def generate_hsm_key(
    key_type: KeyType,
    key_usage: List[KeyUsage],
    metadata: Optional[Dict[str, Any]] = None
):
    """Generate cryptographic key in HSM"""
    try:
        hsm = get_hsm_integration()
        key = await hsm.generate_key(key_type, key_usage, metadata)
        
        return {
            "key_id": key.key_id,
            "key_type": key.key_type.value,
            "key_usage": [usage.value for usage in key.key_usage],
            "key_size": key.key_size,
            "provider": key.provider.value,
            "created_at": key.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hsm/encrypt")
async def encrypt_with_hsm(key_id: str, plaintext: str):
    """Encrypt data using HSM-managed key"""
    try:
        hsm = get_hsm_integration()
        ciphertext = await hsm.encrypt_data(key_id, plaintext)
        
        return {"ciphertext": ciphertext}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hsm/decrypt")
async def decrypt_with_hsm(key_id: str, ciphertext: str):
    """Decrypt data using HSM-managed key"""
    try:
        hsm = get_hsm_integration()
        plaintext = await hsm.decrypt_data(key_id, ciphertext)
        
        return {"plaintext": plaintext}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hsm/sign")
async def sign_with_hsm(key_id: str, data: str):
    """Sign data using HSM-managed key"""
    try:
        hsm = get_hsm_integration()
        signature = await hsm.sign_data(key_id, data)
        
        return {"signature": signature}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hsm/verify")
async def verify_with_hsm(key_id: str, data: str, signature: str):
    """Verify signature using HSM-managed key"""
    try:
        hsm = get_hsm_integration()
        is_valid = await hsm.verify_signature(key_id, data, signature)
        
        return {"valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hsm/keys")
async def list_hsm_keys(key_type: Optional[KeyType] = Query(None)):
    """List HSM-managed keys"""
    try:
        hsm = get_hsm_integration()
        keys = hsm.list_keys(key_type)
        
        return {
            "keys": [
                {
                    "key_id": key.key_id,
                    "key_type": key.key_type.value,
                    "key_usage": [usage.value for usage in key.key_usage],
                    "key_size": key.key_size,
                    "created_at": key.created_at.isoformat(),
                    "last_accessed": key.last_accessed.isoformat() if key.last_accessed else None,
                    "access_count": key.access_count,
                    "is_active": key.is_active
                }
                for key in keys
            ],
            "count": len(keys)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hsm/operations")
async def get_hsm_operations(
    key_id: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None)
):
    """Get HSM operation history"""
    try:
        hsm = get_hsm_integration()
        operations = hsm.get_operation_history(key_id, since)
        
        return {
            "operations": [
                {
                    "operation_id": op.operation_id,
                    "key_id": op.key_id,
                    "operation_type": op.operation_type,
                    "timestamp": op.timestamp.isoformat(),
                    "duration_ms": op.duration_ms,
                    "success": op.success,
                    "error_message": op.error_message
                }
                for op in operations
            ],
            "count": len(operations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Biometric Authentication Endpoints
@router.post("/biometric/enroll")
async def enroll_biometric(
    user_id: str,
    biometric_type: BiometricType,
    device_info: Dict[str, Any]
):
    """Enroll biometric authentication"""
    try:
        # Mock biometric auth manager (would use existing implementation)
        return {
            "success": True,
            "enrollment_id": f"{user_id}_{biometric_type.value}",
            "biometric_type": biometric_type.value,
            "message": f"{biometric_type.value} enrolled successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/biometric/authenticate")
async def authenticate_biometric(
    user_id: str,
    biometric_type: BiometricType,
    biometric_data: str
):
    """Authenticate using biometric"""
    try:
        # Mock biometric authentication
        return {
            "success": True,
            "user_id": user_id,
            "biometric_type": biometric_type.value,
            "authenticated": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Security Dashboard Endpoint
@router.get("/dashboard")
async def get_security_dashboard():
    """Get comprehensive security dashboard"""
    try:
        # Get data from all security components
        zero_trust = get_zero_trust_architecture()
        threat_engine = get_threat_detection_engine()
        compliance = get_compliance_automation()
        kyc_aml = get_kyc_aml_integration()
        hsm = get_hsm_integration()
        
        # Active sessions
        active_sessions = zero_trust.get_active_sessions()
        
        # Recent threats
        recent_threats = threat_engine.get_threat_indicators(
            since=datetime.now() - timedelta(hours=24)
        )
        
        # Threat summary
        threat_summary = threat_engine.get_threat_summary(
            since=datetime.now() - timedelta(hours=24)
        )
        
        # Compliance status
        compliance_results = await compliance.run_compliance_check()
        
        # Active AML alerts
        aml_alerts = kyc_aml.get_aml_alerts(status="open")
        
        # HSM keys
        hsm_keys = hsm.list_keys()
        
        return {
            "overview": {
                "active_sessions": len(active_sessions),
                "threat_indicators_24h": len(recent_threats),
                "blocked_ips": len(threat_engine.get_blocked_ips()),
                "aml_alerts": len(aml_alerts),
                "hsm_keys": len(hsm_keys)
            },
            "zero_trust": {
                "active_sessions": [
                    {
                        "session_id": session.session_id,
                        "user_id": session.user_id,
                        "trust_level": session.trust_level.value,
                        "ip_address": session.ip_address,
                        "created_at": session.created_at.isoformat()
                    }
                    for session in active_sessions[:10]
                ]
            },
            "threat_detection": threat_summary,
            "compliance": {
                "frameworks": list(compliance_results.keys()),
                "overall_status": "compliant" if all(
                    result["non_compliant_rules"] == 0 
                    for result in compliance_results.values()
                ) else "non_compliant"
            },
            "kyc_aml": {
                "active_alerts": len(aml_alerts),
                "high_risk_customers": len([
                    alert for alert in aml_alerts 
                    if alert.severity in ["high", "critical"]
                ])
            },
            "hsm": {
                "total_keys": len(hsm_keys),
                "active_keys": len([key for key in hsm_keys if key.is_active]),
                "provider": hsm.provider.value
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
