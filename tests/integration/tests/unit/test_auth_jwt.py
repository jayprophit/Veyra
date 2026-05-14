"""
Comprehensive Test Suite - Authentication Tests
"""

import pytest
from datetime import datetime, timedelta
from app.auth.jwt_security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    TOKEN_EXPIRE_MINUTES
)


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_consistency(self):
        """Test that password hashing is consistent (produces same hash)"""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different but both verify correctly
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token generation and verification"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        user_id = 123
        token = create_access_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_access_token(self):
        """Test verification of valid access token"""
        user_id = 123
        token = create_access_token(user_id)
        
        verified_user_id = verify_token(token, token_type="access")
        assert verified_user_id == user_id
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.token.here"
        
        result = verify_token(invalid_token, token_type="access")
        assert result is None
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        user_id = 123
        token = create_refresh_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_refresh_token(self):
        """Test refresh token verification"""
        user_id = 123
        token = create_refresh_token(user_id)
        
        verified_user_id = verify_token(token, token_type="refresh")
        assert verified_user_id == user_id
    
    def test_token_type_mismatch(self):
        """Test that token with wrong type fails verification"""
        user_id = 123
        access_token = create_access_token(user_id)
        
        # Try to verify access token as refresh token
        result = verify_token(access_token, token_type="refresh")
        assert result is None
    
    def test_expired_token(self):
        """Test that expired token fails verification"""
        user_id = 123
        
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(user_id, expires_delta)
        
        # Token should be expired
        result = verify_token(token, token_type="access")
        assert result is None


class TestTokenExpiration:
    """Test token expiration"""
    
    def test_token_has_expiration(self):
        """Test that tokens have expiration time"""
        user_id = 123
        token = create_access_token(user_id)
        
        # Token should be valid (not expired immediately)
        result = verify_token(token, token_type="access")
        assert result == user_id


class TestTokenSecurity:
    """Test token security aspects"""
    
    def test_token_different_each_time(self):
        """Test that tokens created at different times are different"""
        user_id = 123
        token1 = create_access_token(user_id)
        
        import time
        time.sleep(0.1)  # Small delay to ensure different creation times
        
        token2 = create_access_token(user_id)
        
        # Tokens should be different (contain different iat times)
        assert token1 != token2
        # But both should verify to same user
        assert verify_token(token1, token_type="access") == user_id
        assert verify_token(token2, token_type="access") == user_id
    
    def test_modified_token_fails(self):
        """Test that modified token fails verification"""
        user_id = 123
        token = create_access_token(user_id)
        
        # Modify token (change one character)
        modified_token = token[:-5] + "xxxxx"
        
        result = verify_token(modified_token, token_type="access")
        assert result is None
