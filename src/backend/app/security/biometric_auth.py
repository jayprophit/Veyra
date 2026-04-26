"""
Biometric Authentication System
Supports Fingerprint, FaceID, Hardware Security Keys
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class BiometricType(Enum):
    FINGERPRINT = "fingerprint"
    FACE_ID = "face_id"
    IRIS = "iris"
    VOICE = "voice"


class HardwareKeyType(Enum):
    YUBIKEY = "yubikey"
    GOOGLE_TITAN = "google_titan"
    FEITIAN = "feitian"
    SOLOKEYS = "solokeys"


@dataclass
class BiometricEnrollment:
    """Stored biometric enrollment data"""
    user_id: str
    biometric_type: BiometricType
    template_hash: str  # Hashed biometric template (not raw biometric!)
    public_key: str  # For FIDO2/WebAuthn
    enrolled_at: datetime
    last_used: Optional[datetime] = None
    device_info: Dict[str, Any] = None
    is_active: bool = True


@dataclass
class HardwareKeyEnrollment:
    """Hardware security key enrollment"""
    user_id: str
    key_type: HardwareKeyType
    credential_id: str
    public_key: str
    enrolled_at: datetime
    last_used: Optional[datetime] = None
    key_name: str = ""
    is_active: bool = True


class BiometricAuthManager:
    """
    Manages biometric authentication and hardware security keys
    Implements FIDO2/WebAuthn standards
    """
    
    def __init__(self):
        self.biometric_enrollments: Dict[str, List[BiometricEnrollment]] = {}
        self.hardware_keys: Dict[str, List[HardwareKeyEnrollment]] = {}
        self.auth_challenges: Dict[str, Any] = {}  # Temporary challenges
    
    async def enroll_biometric(
        self,
        user_id: str,
        biometric_type: BiometricType,
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enroll a new biometric authentication method
        
        IMPORTANT: We never store raw biometric data!
        Only store cryptographic representations (templates/hashes)
        """
        # Generate WebAuthn/FIDO2 challenge
        challenge = self._generate_challenge()
        
        enrollment = BiometricEnrollment(
            user_id=user_id,
            biometric_type=biometric_type,
            template_hash="template_placeholder",  # In production: proper hash
            public_key="public_key_placeholder",  # In production: FIDO2 public key
            enrolled_at=datetime.utcnow(),
            device_info=device_info
        )
        
        if user_id not in self.biometric_enrollments:
            self.biometric_enrollments[user_id] = []
        
        self.biometric_enrollments[user_id].append(enrollment)
        
        return {
            "success": True,
            "enrollment_id": f"{user_id}_{biometric_type.value}",
            "biometric_type": biometric_type.value,
            "challenge": challenge,
            "message": f"{biometric_type.value} enrolled successfully"
        }
    
    async def enroll_hardware_key(
        self,
        user_id: str,
        key_type: HardwareKeyType,
        key_name: str = ""
    ) -> Dict[str, Any]:
        """
        Enroll a hardware security key (YubiKey, etc.)
        """
        challenge = self._generate_challenge()
        
        enrollment = HardwareKeyEnrollment(
            user_id=user_id,
            key_type=key_type,
            credential_id=f"cred_{user_id}_{datetime.utcnow().timestamp()}",
            public_key="key_public_placeholder",  # In production: actual public key
            enrolled_at=datetime.utcnow(),
            key_name=key_name or f"{key_type.value.title()} Key"
        )
        
        if user_id not in self.hardware_keys:
            self.hardware_keys[user_id] = []
        
        self.hardware_keys[user_id].append(enrollment)
        
        return {
            "success": True,
            "credential_id": enrollment.credential_id,
            "key_type": key_type.value,
            "challenge": challenge,
            "instructions": f"Touch your {key_type.value} to complete enrollment"
        }
    
    async def authenticate_biometric(
        self,
        user_id: str,
        biometric_type: BiometricType,
        authentication_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Authenticate user with biometric
        
        Returns authentication result with JWT token on success
        """
        enrollments = self.biometric_enrollments.get(user_id, [])
        
        matching = [e for e in enrollments if e.biometric_type == biometric_type and e.is_active]
        
        if not matching:
            return {
                "success": False,
                "error": f"No active {biometric_type.value} enrollment found"
            }
        
        # In production: Verify against stored public key using FIDO2
        # Mock successful authentication
        enrollment = matching[0]
        enrollment.last_used = datetime.utcnow()
        
        return {
            "success": True,
            "user_id": user_id,
            "auth_method": biometric_type.value,
            "token": "mock_jwt_token_biometric",  # In production: actual JWT
            "expires_in": 3600
        }
    
    async def authenticate_hardware_key(
        self,
        user_id: str,
        credential_id: str,
        assertion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Authenticate with hardware security key"""
        keys = self.hardware_keys.get(user_id, [])
        
        matching = [k for k in keys if k.credential_id == credential_id and k.is_active]
        
        if not matching:
            return {
                "success": False,
                "error": "Hardware key not recognized"
            }
        
        # In production: Verify FIDO2 assertion
        key = matching[0]
        key.last_used = datetime.utcnow()
        
        return {
            "success": True,
            "user_id": user_id,
            "auth_method": "hardware_key",
            "key_type": key.key_type.value,
            "token": "mock_jwt_token_hardware_key",
            "expires_in": 3600
        }
    
    async def get_enrolled_methods(self, user_id: str) -> Dict[str, Any]:
        """Get all enrolled biometric and hardware key methods"""
        biometrics = self.biometric_enrollments.get(user_id, [])
        keys = self.hardware_keys.get(user_id, [])
        
        return {
            "user_id": user_id,
            "biometric_methods": [
                {
                    "type": b.biometric_type.value,
                    "enrolled_at": b.enrolled_at.isoformat(),
                    "last_used": b.last_used.isoformat() if b.last_used else None,
                    "device": b.device_info.get("model", "Unknown"),
                    "is_active": b.is_active
                }
                for b in biometrics
            ],
            "hardware_keys": [
                {
                    "credential_id": k.credential_id,
                    "key_type": k.key_type.value,
                    "name": k.key_name,
                    "enrolled_at": k.enrolled_at.isoformat(),
                    "last_used": k.last_used.isoformat() if k.last_used else None,
                    "is_active": k.is_active
                }
                for k in keys
            ],
            "total_methods": len(biometrics) + len(keys)
        }
    
    async def remove_enrollment(
        self,
        user_id: str,
        method_type: str,
        method_id: str
    ) -> Dict[str, Any]:
        """Remove a biometric or hardware key enrollment"""
        if method_type == "biometric":
            enrollments = self.biometric_enrollments.get(user_id, [])
            for e in enrollments:
                if e.template_hash == method_id:  # Simplified matching
                    e.is_active = False
                    return {"success": True, "message": "Biometric enrollment removed"}
        
        elif method_type == "hardware_key":
            keys = self.hardware_keys.get(user_id, [])
            for k in keys:
                if k.credential_id == method_id:
                    k.is_active = False
                    return {"success": True, "message": "Hardware key removed"}
        
        return {"success": False, "error": "Method not found"}
    
    def _generate_challenge(self) -> str:
        """Generate cryptographic challenge for FIDO2"""
        import secrets
        return secrets.token_urlsafe(32)
    
    async def require_biometric_for_sensitive_action(
        self,
        user_id: str,
        action: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Determine if biometric authentication is required for an action
        
        Examples of sensitive actions:
        - Withdrawals > $10,000
        - Changing bank account
        - Changing password
        - Large trades > $50,000
        """
        sensitive_actions = {
            "withdrawal": 10000,
            "large_trade": 50000,
            "password_change": 0,
            "bank_account_change": 0,
            "api_key_generation": 0
        }
        
        requires_biometric = False
        reason = ""
        
        if action in sensitive_actions:
            threshold = sensitive_actions[action]
            if amount and amount >= threshold:
                requires_biometric = True
                reason = f"Amount ${amount:,} exceeds threshold ${threshold:,}"
            elif threshold == 0:
                requires_biometric = True
                reason = "Action requires additional security"
        
        return {
            "action": action,
            "requires_biometric": requires_biometric,
            "reason": reason,
            "available_methods": await self.get_enrolled_methods(user_id) if requires_biometric else None
        }
