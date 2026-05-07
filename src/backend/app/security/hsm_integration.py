"""
Hardware Security Modules (HSM) Integration
===========================================
Enterprise-grade HSM integration for Financial Master
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import secrets
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)


class HSMProvider(Enum):
    """HSM provider types"""
    AWS_CLOUDHSM = "aws_cloudhsm"
    AZURE_DEDICATED_HSM = "azure_dedicated_hsm"
    THALES_LUNA = "thales_luna"
    UTIMACO_SECURITYSERVER = "utimaco_securityserver"
    SOFT_HSM = "soft_hsm"  # For development/testing


class KeyType(Enum):
    """Cryptographic key types"""
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ECDSA_P256 = "ecdsa_p256"
    ECDSA_P384 = "ecdsa_p384"
    HMAC_SHA256 = "hmac_sha256"
    HMAC_SHA512 = "hmac_sha512"


class KeyUsage(Enum):
    """Key usage purposes"""
    ENCRYPTION = "encryption"
    DECRYPTION = "decryption"
    SIGNING = "signing"
    VERIFICATION = "verification"
    KEY_WRAP = "key_wrap"
    KEY_UNWRAP = "key_unwrap"


@dataclass
class HSMKey:
    """HSM-managed cryptographic key"""
    key_id: str
    key_type: KeyType
    key_usage: List[KeyUsage]
    key_size: int
    provider: HSMProvider
    created_at: datetime
    last_accessed: Optional[datetime]
    access_count: int
    is_active: bool
    metadata: Dict[str, Any]


@dataclass
class HSMOperation:
    """HSM operation record"""
    operation_id: str
    key_id: str
    operation_type: str
    input_data: Optional[str]
    output_data: Optional[str]
    timestamp: datetime
    duration_ms: float
    success: bool
    error_message: Optional[str]


class HSMIntegration:
    """Hardware Security Module integration service"""
    
    def __init__(self, provider: HSMProvider = HSMProvider.SOFT_HSM):
        self.provider = provider
        self.keys: Dict[str, HSMKey] = {}
        self.operations: List[HSMOperation] = []
        self.session_active = False
        self.backend = default_backend()
        
        # Initialize provider-specific configuration
        self._initialize_provider()
        
    def _initialize_provider(self):
        """Initialize provider-specific settings"""
        if self.provider == HSMProvider.AWS_CLOUDHSM:
            self._init_aws_cloudhsm()
        elif self.provider == HSMProvider.AZURE_DEDICATED_HSM:
            self._init_azure_hsm()
        elif self.provider == HSMProvider.THALES_LUNA:
            self._init_thales_luna()
        elif self.provider == HSMProvider.UTIMACO_SECURITYSERVER:
            self._init_utimaco_securityserver()
        else:
            self._init_soft_hsm()
            
    def _init_aws_cloudhsm(self):
        """Initialize AWS CloudHSM"""
        # Mock AWS CloudHSM initialization
        logger.info("Initializing AWS CloudHSM")
        
    def _init_azure_hsm(self):
        """Initialize Azure Dedicated HSM"""
        # Mock Azure HSM initialization
        logger.info("Initializing Azure Dedicated HSM")
        
    def _init_thales_luna(self):
        """Initialize Thales Luna HSM"""
        # Mock Thales Luna initialization
        logger.info("Initializing Thales Luna HSM")
        
    def _init_utimaco_securityserver(self):
        """Initialize Utimaco SecurityServer"""
        # Mock Utimaco initialization
        logger.info("Initializing Utimaco SecurityServer")
        
    def _init_soft_hsm(self):
        """Initialize Soft HSM for development"""
        logger.info("Initializing Soft HSM for development")
        
    async def connect(self) -> bool:
        """Connect to HSM provider"""
        try:
            # Mock connection logic
            self.session_active = True
            logger.info(f"Connected to HSM provider: {self.provider.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to HSM: {e}")
            return False
            
    async def disconnect(self):
        """Disconnect from HSM provider"""
        try:
            self.session_active = False
            logger.info("Disconnected from HSM")
        except Exception as e:
            logger.error(f"Error disconnecting from HSM: {e}")
            
    async def generate_key(self, key_type: KeyType, key_usage: List[KeyUsage],
                          metadata: Optional[Dict[str, Any]] = None) -> HSMKey:
        """Generate a new cryptographic key in HSM"""
        if not self.session_active:
            raise RuntimeError("HSM session not active")
            
        start_time = datetime.now()
        
        try:
            # Generate key based on type
            if key_type == KeyType.RSA_2048:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                    backend=self.backend
                )
                key_size = 2048
            elif key_type == KeyType.RSA_4096:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,
                    backend=self.backend
                )
                key_size = 4096
            else:
                # For other key types, generate appropriate key
                key_size = 256  # Default for AES
                
            # Create HSM key record
            hsm_key = HSMKey(
                key_id=secrets.token_urlsafe(16),
                key_type=key_type,
                key_usage=key_usage,
                key_size=key_size,
                provider=self.provider,
                created_at=datetime.now(),
                last_accessed=None,
                access_count=0,
                is_active=True,
                metadata=metadata or {}
            )
            
            # Store key (in production, would store in actual HSM)
            self.keys[hsm_key.key_id] = hsm_key
            
            # Log operation
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id=hsm_key.key_id,
                operation_type="generate_key",
                input_data=None,
                output_data=None,
                timestamp=start_time,
                duration_ms=duration,
                success=True,
                error_message=None
            )
            self.operations.append(operation)
            
            logger.info(f"Generated {key_type.value} key: {hsm_key.key_id}")
            return hsm_key
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id="",
                operation_type="generate_key",
                input_data=None,
                output_data=None,
                timestamp=start_time,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
            self.operations.append(operation)
            raise
            
    async def encrypt_data(self, key_id: str, plaintext: str) -> str:
        """Encrypt data using HSM-managed key"""
        if not self.session_active:
            raise RuntimeError("HSM session not active")
            
        start_time = datetime.now()
        
        try:
            key = self.keys.get(key_id)
            if not key:
                raise ValueError("Key not found")
                
            if KeyUsage.ENCRYPTION not in key.key_usage:
                raise ValueError("Key not authorized for encryption")
                
            # Perform encryption based on key type
            if key.key_type == KeyType.AES_256:
                ciphertext = await self._encrypt_aes(key, plaintext)
            elif key.key_type in [KeyType.RSA_2048, KeyType.RSA_4096]:
                ciphertext = await self._encrypt_rsa(key, plaintext)
            else:
                raise ValueError(f"Encryption not supported for {key.key_type.value}")
                
            # Update key access
            key.last_accessed = datetime.now()
            key.access_count += 1
            
            # Log operation
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id=key_id,
                operation_type="encrypt",
                input_data=plaintext[:100] + "..." if len(plaintext) > 100 else plaintext,
                output_data=ciphertext[:100] + "..." if len(ciphertext) > 100 else ciphertext,
                timestamp=start_time,
                duration_ms=duration,
                success=True,
                error_message=None
            )
            self.operations.append(operation)
            
            return ciphertext
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id=key_id,
                operation_type="encrypt",
                input_data=plaintext[:100] + "..." if len(plaintext) > 100 else plaintext,
                output_data=None,
                timestamp=start_time,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
            self.operations.append(operation)
            raise
            
    async def decrypt_data(self, key_id: str, ciphertext: str) -> str:
        """Decrypt data using HSM-managed key"""
        if not self.session_active:
            raise RuntimeError("HSM session not active")
            
        start_time = datetime.now()
        
        try:
            key = self.keys.get(key_id)
            if not key:
                raise ValueError("Key not found")
                
            if KeyUsage.DECRYPTION not in key.key_usage:
                raise ValueError("Key not authorized for decryption")
                
            # Perform decryption based on key type
            if key.key_type == KeyType.AES_256:
                plaintext = await self._decrypt_aes(key, ciphertext)
            elif key.key_type in [KeyType.RSA_2048, KeyType.RSA_4096]:
                plaintext = await self._decrypt_rsa(key, ciphertext)
            else:
                raise ValueError(f"Decryption not supported for {key.key_type.value}")
                
            # Update key access
            key.last_accessed = datetime.now()
            key.access_count += 1
            
            # Log operation
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id=key_id,
                operation_type="decrypt",
                input_data=ciphertext[:100] + "..." if len(ciphertext) > 100 else ciphertext,
                output_data=plaintext[:100] + "..." if len(plaintext) > 100 else plaintext,
                timestamp=start_time,
                duration_ms=duration,
                success=True,
                error_message=None
            )
            self.operations.append(operation)
            
            return plaintext
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id=key_id,
                operation_type="decrypt",
                input_data=ciphertext[:100] + "..." if len(ciphertext) > 100 else ciphertext,
                output_data=None,
                timestamp=start_time,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
            self.operations.append(operation)
            raise
            
    async def sign_data(self, key_id: str, data: str) -> str:
        """Sign data using HSM-managed key"""
        if not self.session_active:
            raise RuntimeError("HSM session not active")
            
        start_time = datetime.now()
        
        try:
            key = self.keys.get(key_id)
            if not key:
                raise ValueError("Key not found")
                
            if KeyUsage.SIGNING not in key.key_usage:
                raise ValueError("Key not authorized for signing")
                
            # Generate signature
            if key.key_type in [KeyType.RSA_2048, KeyType.RSA_4096]:
                signature = await self._sign_rsa(key, data)
            elif key.key_type in [KeyType.HMAC_SHA256, KeyType.HMAC_SHA512]:
                signature = await self._sign_hmac(key, data)
            else:
                raise ValueError(f"Signing not supported for {key.key_type.value}")
                
            # Update key access
            key.last_accessed = datetime.now()
            key.access_count += 1
            
            # Log operation
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id=key_id,
                operation_type="sign",
                input_data=data[:100] + "..." if len(data) > 100 else data,
                output_data=signature[:100] + "..." if len(signature) > 100 else signature,
                timestamp=start_time,
                duration_ms=duration,
                success=True,
                error_message=None
            )
            self.operations.append(operation)
            
            return signature
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id=key_id,
                operation_type="sign",
                input_data=data[:100] + "..." if len(data) > 100 else data,
                output_data=None,
                timestamp=start_time,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
            self.operations.append(operation)
            raise
            
    async def verify_signature(self, key_id: str, data: str, signature: str) -> bool:
        """Verify signature using HSM-managed key"""
        if not self.session_active:
            raise RuntimeError("HSM session not active")
            
        start_time = datetime.now()
        
        try:
            key = self.keys.get(key_id)
            if not key:
                raise ValueError("Key not found")
                
            if KeyUsage.VERIFICATION not in key.key_usage:
                raise ValueError("Key not authorized for verification")
                
            # Verify signature
            if key.key_type in [KeyType.RSA_2048, KeyType.RSA_4096]:
                is_valid = await self._verify_rsa(key, data, signature)
            elif key.key_type in [KeyType.HMAC_SHA256, KeyType.HMAC_SHA512]:
                is_valid = await self._verify_hmac(key, data, signature)
            else:
                raise ValueError(f"Verification not supported for {key.key_type.value}")
                
            # Update key access
            key.last_accessed = datetime.now()
            key.access_count += 1
            
            # Log operation
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id=key_id,
                operation_type="verify",
                input_data=data[:100] + "..." if len(data) > 100 else data,
                output_data=str(is_valid),
                timestamp=start_time,
                duration_ms=duration,
                success=True,
                error_message=None
            )
            self.operations.append(operation)
            
            return is_valid
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            operation = HSMOperation(
                operation_id=secrets.token_urlsafe(16),
                key_id=key_id,
                operation_type="verify",
                input_data=data[:100] + "..." if len(data) > 100 else data,
                output_data=None,
                timestamp=start_time,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
            self.operations.append(operation)
            raise
            
    async def _encrypt_aes(self, key: HSMKey, plaintext: str) -> str:
        """Encrypt using AES"""
        # Mock AES encryption (in production, would use actual HSM)
        iv = secrets.token_bytes(16)
        cipher_key = secrets.token_bytes(32)  # AES-256
        
        cipher = Cipher(
            algorithms.AES(cipher_key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Pad plaintext
        padded_data = plaintext.encode()
        padded_data += b'\0' * (16 - len(padded_data) % 16)
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return IV + ciphertext
        return base64.b64encode(iv + ciphertext).decode()
        
    async def _decrypt_aes(self, key: HSMKey, ciphertext: str) -> str:
        """Decrypt using AES"""
        # Mock AES decryption (in production, would use actual HSM)
        data = base64.b64decode(ciphertext)
        iv = data[:16]
        encrypted_data = data[16:]
        
        cipher_key = secrets.token_bytes(32)  # AES-256
        
        cipher = Cipher(
            algorithms.AES(cipher_key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove padding
        plaintext = padded_plaintext.rstrip(b'\0').decode()
        
        return plaintext
        
    async def _encrypt_rsa(self, key: HSMKey, plaintext: str) -> str:
        """Encrypt using RSA"""
        # Mock RSA encryption (in production, would use actual HSM)
        # Generate temporary RSA key for demonstration
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key.key_size,
            backend=self.backend
        )
        public_key = private_key.public_key()
        
        ciphertext = public_key.encrypt(
            plaintext.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(ciphertext).decode()
        
    async def _decrypt_rsa(self, key: HSMKey, ciphertext: str) -> str:
        """Decrypt using RSA"""
        # Mock RSA decryption (in production, would use actual HSM)
        encrypted_data = base64.b64decode(ciphertext)
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key.key_size,
            backend=self.backend
        )
        
        plaintext = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return plaintext.decode()
        
    async def _sign_rsa(self, key: HSMKey, data: str) -> str:
        """Sign using RSA"""
        # Mock RSA signing (in production, would use actual HSM)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key.key_size,
            backend=self.backend
        )
        
        signature = private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()
        
    async def _verify_rsa(self, key: HSMKey, data: str, signature: str) -> bool:
        """Verify RSA signature"""
        # Mock RSA verification (in production, would use actual HSM)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key.key_size,
            backend=self.backend
        )
        public_key = private_key.public_key()
        
        try:
            signature_data = base64.b64decode(signature)
            public_key.verify(
                signature_data,
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
            
    async def _sign_hmac(self, key: HSMKey, data: str) -> str:
        """Sign using HMAC"""
        # Mock HMAC signing (in production, would use actual HSM)
        secret_key = secrets.token_bytes(32)
        
        if key.key_type == KeyType.HMAC_SHA256:
            h = hashlib.sha256()
        else:
            h = hashlib.sha512()
            
        h.update(secret_key + data.encode())
        signature = h.digest()
        
        return base64.b64encode(signature).decode()
        
    async def _verify_hmac(self, key: HSMKey, data: str, signature: str) -> bool:
        """Verify HMAC signature"""
        # Mock HMAC verification (in production, would use actual HSM)
        secret_key = secrets.token_bytes(32)
        
        if key.key_type == KeyType.HMAC_SHA256:
            h = hashlib.sha256()
        else:
            h = hashlib.sha512()
            
        h.update(secret_key + data.encode())
        expected_signature = h.digest()
        
        provided_signature = base64.b64decode(signature)
        
        return secrets.compare_digest(expected_signature, provided_signature)
        
    def get_key_info(self, key_id: str) -> Optional[HSMKey]:
        """Get key information"""
        return self.keys.get(key_id)
        
    def list_keys(self, key_type: Optional[KeyType] = None) -> List[HSMKey]:
        """List all keys, optionally filtered by type"""
        keys = list(self.keys.values())
        
        if key_type:
            keys = [key for key in keys if key.key_type == key_type]
            
        return sorted(keys, key=lambda x: x.created_at, reverse=True)
        
    def get_operation_history(self, key_id: Optional[str] = None,
                           since: Optional[datetime] = None) -> List[HSMOperation]:
        """Get operation history"""
        operations = self.operations.copy()
        
        if key_id:
            operations = [op for op in operations if op.key_id == key_id]
            
        if since:
            operations = [op for op in operations if op.timestamp >= since]
            
        return sorted(operations, key=lambda x: x.timestamp, reverse=True)
        
    async def delete_key(self, key_id: str) -> bool:
        """Delete a key from HSM"""
        try:
            key = self.keys.get(key_id)
            if not key:
                return False
                
            # Mark key as inactive (in production, would delete from actual HSM)
            key.is_active = False
            
            logger.info(f"Deleted key: {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting key {key_id}: {e}")
            return False


# Global HSM integration instance
_hsm_integration = None

def get_hsm_integration() -> HSMIntegration:
    """Get the global HSM integration instance"""
    global _hsm_integration
    if _hsm_integration is None:
        _hsm_integration = HSMIntegration()
    return _hsm_integration
