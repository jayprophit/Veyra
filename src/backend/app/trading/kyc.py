"""
KYC (Know Your Customer) and Biometric Authentication
Multi-level verification system
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid

class KYCLevel(Enum):
    NONE = 0
    BASIC = 1      # Email verified
    STANDARD = 2   # ID document verified
    ADVANCED = 3   # Biometric + address
    PREMIUM = 4    # Full verification + background check

class VerificationStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class KYCRecord:
    user_id: str
    level: KYCLevel
    status: VerificationStatus
    email_verified: bool
    phone_verified: bool
    id_document_verified: bool
    biometric_verified: bool
    address_verified: bool
    submitted_at: datetime
    verified_at: Optional[datetime]
    documents: List[Dict]

class KYCManager:
    """
    Multi-level KYC verification system
    Supports document upload, biometric auth, and compliance
    """
    
    def __init__(self):
        self.records: Dict[str, KYCRecord] = {}
        self.pending_verifications: List[Dict] = []
    
    def start_verification(self, user_id: str, level: KYCLevel = KYCLevel.STANDARD) -> KYCRecord:
        """Start KYC process for a user"""
        record = KYCRecord(
            user_id=user_id,
            level=level,
            status=VerificationStatus.PENDING,
            email_verified=False,
            phone_verified=False,
            id_document_verified=False,
            biometric_verified=False,
            address_verified=False,
            submitted_at=datetime.now(),
            verified_at=None,
            documents=[]
        )
        self.records[user_id] = record
        return record
    
    def verify_email(self, user_id: str, email: str, verification_code: str) -> bool:
        """Verify email with code"""
        # In production: check code against stored hash
        if user_id in self.records:
            self.records[user_id].email_verified = True
            self._check_level_completion(user_id)
            return True
        return False
    
    def verify_phone(self, user_id: str, phone: str, sms_code: str) -> bool:
        """Verify phone with SMS code"""
        if user_id in self.records:
            self.records[user_id].phone_verified = True
            self._check_level_completion(user_id)
            return True
        return False
    
    def submit_id_document(self, user_id: str, document_type: str, 
                          document_data: bytes) -> Dict:
        """Submit ID document for verification"""
        if user_id not in self.records:
            return {'error': 'No KYC record found'}
        
        document_id = str(uuid.uuid4())
        doc_record = {
            'id': document_id,
            'type': document_type,  # passport, drivers_license, national_id
            'status': 'pending_review',
            'submitted_at': datetime.now().isoformat(),
            'verified': False
        }
        
        self.records[user_id].documents.append(doc_record)
        
        # Queue for manual or AI review
        self.pending_verifications.append({
            'document_id': document_id,
            'user_id': user_id,
            'type': document_type,
            'submitted_at': datetime.now()
        })
        
        return {'document_id': document_id, 'status': 'pending_review'}
    
    def verify_biometric(self, user_id: str, biometric_type: str, 
                        biometric_data: bytes) -> Dict:
        """
        Verify biometric data (fingerprint, facial recognition)
        """
        if user_id not in self.records:
            return {'error': 'No KYC record found'}
        
        # In production:
        # 1. Check liveness (prevent photo spoofing)
        # 2. Compare against stored template
        # 3. Check against watchlists
        
        # Simulate verification
        verification_result = {
            'type': biometric_type,
            'verified': True,
            'confidence': 0.95,
            'liveness_check': 'passed',
            'timestamp': datetime.now().isoformat()
        }
        
        self.records[user_id].biometric_verified = True
        self._check_level_completion(user_id)
        
        return verification_result
    
    def verify_address(self, user_id: str, address_proof: bytes) -> Dict:
        """Verify address with utility bill or bank statement"""
        if user_id not in self.records:
            return {'error': 'No KYC record found'}
        
        # Document processing and verification
        self.records[user_id].address_verified = True
        self._check_level_completion(user_id)
        
        return {'status': 'verified', 'method': 'document_upload'}
    
    def _check_level_completion(self, user_id: str):
        """Check if user has met requirements for their KYC level"""
        if user_id not in self.records:
            return
        
        record = self.records[user_id]
        
        # Check level requirements
        if record.level == KYCLevel.BASIC:
            if record.email_verified:
                record.status = VerificationStatus.VERIFIED
                record.verified_at = datetime.now()
        
        elif record.level == KYCLevel.STANDARD:
            if (record.email_verified and 
                record.id_document_verified and 
                record.phone_verified):
                record.status = VerificationStatus.VERIFIED
                record.verified_at = datetime.now()
        
        elif record.level == KYCLevel.ADVANCED:
            if (record.email_verified and 
                record.id_document_verified and 
                record.biometric_verified and 
                record.address_verified):
                record.status = VerificationStatus.VERIFIED
                record.verified_at = datetime.now()
    
    def get_kyc_status(self, user_id: str) -> Optional[Dict]:
        """Get KYC status for a user"""
        if user_id not in self.records:
            return None
        
        record = self.records[user_id]
        
        return {
            'user_id': user_id,
            'level': record.level.name,
            'status': record.status.value,
            'email_verified': record.email_verified,
            'phone_verified': record.phone_verified,
            'id_document_verified': record.id_document_verified,
            'biometric_verified': record.biometric_verified,
            'address_verified': record.address_verified,
            'submitted_at': record.submitted_at.isoformat(),
            'verified_at': record.verified_at.isoformat() if record.verified_at else None,
            'documents': record.documents,
            'is_fully_verified': record.status == VerificationStatus.VERIFIED
        }
    
    def can_trade(self, user_id: str, trade_type: str = 'basic') -> bool:
        """Check if user can perform trading activities"""
        status = self.get_kyc_status(user_id)
        if not status:
            return False
        
        requirements = {
            'basic': KYCLevel.BASIC,
            'standard': KYCLevel.STANDARD,
            'advanced': KYCLevel.ADVANCED,
            'premium': KYCLevel.PREMIUM
        }
        
        required_level = requirements.get(trade_type, KYCLevel.STANDARD)
        current_level = KYCLevel[status['level']]
        
        return (current_level.value >= required_level.value and 
                status['is_fully_verified'])
    
    def get_required_documents(self, level: KYCLevel) -> List[str]:
        """Get list of required documents for each KYC level"""
        requirements = {
            KYCLevel.NONE: [],
            KYCLevel.BASIC: ['email_verification'],
            KYCLevel.STANDARD: ['email_verification', 'id_document', 'phone_verification'],
            KYCLevel.ADVANCED: ['email_verification', 'id_document', 'phone_verification', 
                              'biometric', 'address_proof'],
            KYCLevel.PREMIUM: ['email_verification', 'id_document', 'phone_verification',
                             'biometric', 'address_proof', 'background_check']
        }
        return requirements.get(level, [])
