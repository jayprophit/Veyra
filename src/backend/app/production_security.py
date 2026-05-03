"""
Production Security Layer for Financial Master
===============================================
Critical safety features for live trading:
- API authentication & authorization
- Rate limiting
- Environment validation
- Trading safety switches
- Circuit breakers
- Audit logging

MUST be enabled before live trading.
"""

import os
import time
import hashlib
import hmac
import secrets
import logging
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class TradingMode(Enum):
    """Trading mode - controls whether orders go to live or paper"""
    PAPER_ONLY = "paper_only"      # All trades are paper/sandbox
    HYBRID = "hybrid"               # Paper for testing, real for prod
    LIVE = "live"                   # All trades are live (DANGEROUS)


class Environment(Enum):
    """Deployment environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class SecurityConfig:
    """Security configuration"""
    trading_mode: TradingMode = TradingMode.PAPER_ONLY
    environment: Environment = Environment.DEVELOPMENT
    
    # API Security
    jwt_secret: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    api_key_header: str = "X-API-Key"
    
    # Rate Limiting
    rate_limit_requests: int = 100  # per window
    rate_limit_window_seconds: int = 60
    
    # Trading Safety
    max_daily_loss_pct: float = 5.0  # Stop trading after 5% loss
    max_position_size_pct: float = 20.0  # Max 20% in single position
    max_order_value_usd: float = 100000.0
    
    # Circuit Breakers
    enable_circuit_breakers: bool = True
    max_api_failures: int = 5
    circuit_breaker_reset_seconds: int = 300
    
    # Audit
    enable_audit_logging: bool = True
    audit_log_path: str = "./logs/audit.log"


class APIKeyManager:
    """Manage API keys for client authentication"""
    
    def __init__(self):
        self._keys: Dict[str, Dict] = {}  # key -> {user_id, created, permissions}
        self._revoked: Set[str] = set()
    
    def generate_key(self, user_id: str, permissions: List[str] = None) -> str:
        """Generate new API key for user"""
        key = f"fm_{secrets.token_urlsafe(32)}"
        self._keys[key] = {
            'user_id': user_id,
            'created': datetime.now(),
            'permissions': permissions or ['read'],
            'last_used': None,
            'use_count': 0
        }
        return key
    
    def validate_key(self, key: str, required_permission: str = None) -> bool:
        """Validate API key and check permission"""
        if key in self._revoked:
            return False
        
        key_data = self._keys.get(key)
        if not key_data:
            return False
        
        # Update usage stats
        key_data['last_used'] = datetime.now()
        key_data['use_count'] += 1
        
        # Check permission
        if required_permission:
            return required_permission in key_data['permissions']
        
        return True
    
    def revoke_key(self, key: str):
        """Revoke an API key"""
        self._revoked.add(key)
        if key in self._keys:
            del self._keys[key]
    
    def get_key_info(self, key: str) -> Optional[Dict]:
        """Get information about a key"""
        return self._keys.get(key)


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests: int = 100, window_seconds: int = 60):
        self.requests = requests
        self.window = window_seconds
        self._buckets: Dict[str, Dict] = {}  # key -> {tokens, last_update}
    
    def _get_bucket(self, key: str) -> Dict:
        """Get or create rate limit bucket"""
        now = time.time()
        
        if key not in self._buckets:
            self._buckets[key] = {
                'tokens': self.requests,
                'last_update': now
            }
        
        bucket = self._buckets[key]
        
        # Add tokens based on time elapsed
        elapsed = now - bucket['last_update']
        tokens_to_add = elapsed * (self.requests / self.window)
        bucket['tokens'] = min(self.requests, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = now
        
        return bucket
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        bucket = self._get_bucket(key)
        
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        
        return False
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests in window"""
        bucket = self._get_bucket(key)
        return int(bucket['tokens'])
    
    def get_reset_time(self, key: str) -> int:
        """Get seconds until rate limit resets"""
        bucket = self._get_bucket(key)
        if bucket['tokens'] >= 1:
            return 0
        
        # Time to get 1 token
        return int((1 - bucket['tokens']) * (self.window / self.requests))


class CircuitBreaker:
    """Circuit breaker for external API calls"""
    
    class State(Enum):
        CLOSED = "closed"      # Normal operation
        OPEN = "open"          # Failing, reject calls
        HALF_OPEN = "half_open"  # Testing if recovered
    
    def __init__(
        self,
        name: str,
        max_failures: int = 5,
        reset_timeout: int = 300
    ):
        self.name = name
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self._state = self.State.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._success_count = 0
    
    @property
    def state(self) -> State:
        """Get current state"""
        if self._state == self.State.OPEN:
            # Check if we should try half-open
            if self._last_failure_time:
                elapsed = time.time() - self._last_failure_time
                if elapsed > self.reset_timeout:
                    self._state = self.State.HALF_OPEN
                    logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
        
        return self._state
    
    def can_execute(self) -> bool:
        """Check if operation can execute"""
        return self.state in [self.State.CLOSED, self.State.HALF_OPEN]
    
    def record_success(self):
        """Record successful operation"""
        if self._state == self.State.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= 3:  # Need 3 successes to close
                self._state = self.State.CLOSED
                self._failure_count = 0
                logger.info(f"Circuit breaker '{self.name}' CLOSED (recovered)")
        else:
            self._failure_count = 0
    
    def record_failure(self):
        """Record failed operation"""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == self.State.HALF_OPEN:
            # Failed during test, go back to open
            self._state = self.State.OPEN
            logger.warning(f"Circuit breaker '{self.name}' OPEN (recovery failed)")
        elif self._failure_count >= self.max_failures:
            self._state = self.State.OPEN
            logger.error(f"Circuit breaker '{self.name}' OPEN ({self._failure_count} failures)")
    
    @asynccontextmanager
    async def __aenter__(self):
        if not self.can_execute():
            raise CircuitBreakerOpen(f"Circuit breaker '{self.name}' is OPEN")
        yield self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.record_failure()
        else:
            self.record_success()


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open"""
    pass


class TradingSafety:
    """
    Trading safety controls
    Prevents dangerous trading behavior
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._daily_stats: Dict[str, Dict] = {}  # date -> stats
        self._positions: Dict[str, Decimal] = {}  # symbol -> size
        self._trades_today: List[Dict] = []
        
        self._load_daily_stats()
    
    def _load_daily_stats(self):
        """Load or initialize today's stats"""
        today = datetime.now().date().isoformat()
        if today not in self._daily_stats:
            self._daily_stats[today] = {
                'starting_portfolio_value': 0,
                'current_portfolio_value': 0,
                'total_trades': 0,
                'realized_pnl': 0,
                'unrealized_pnl': 0,
                'circuit_breaker_triggered': False
            }
    
    def check_order_safety(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        portfolio_value: float
    ) -> Dict[str, Any]:
        """
        Check if order is safe to execute
        
        Returns:
            {'allowed': bool, 'reason': str, 'warnings': List[str]}
        """
        warnings = []
        order_value = quantity * price
        
        # Check daily loss limit
        stats = self._daily_stats.get(datetime.now().date().isoformat(), {})
        daily_pnl = stats.get('realized_pnl', 0) + stats.get('unrealized_pnl', 0)
        
        if portfolio_value > 0:
            daily_loss_pct = abs(daily_pnl) / portfolio_value * 100
            if daily_loss_pct >= self.config.max_daily_loss_pct:
                return {
                    'allowed': False,
                    'reason': f"Daily loss limit reached ({self.config.max_daily_loss_pct}%)",
                    'warnings': warnings
                }
        
        # Check position size limit
        position_value = self._positions.get(symbol, 0) * price
        if side == 'BUY':
            new_position_value = position_value + order_value
            position_pct = (new_position_value / portfolio_value * 100) if portfolio_value > 0 else 0
            
            if position_pct > self.config.max_position_size_pct:
                return {
                    'allowed': False,
                    'reason': f"Position size limit exceeded ({self.config.max_position_size_pct}% max)",
                    'warnings': warnings
                }
            
            if position_pct > self.config.max_position_size_pct * 0.8:
                warnings.append(f"Position approaching size limit ({position_pct:.1f}%)")
        
        # Check order value limit
        if order_value > self.config.max_order_value_usd:
            return {
                'allowed': False,
                'reason': f"Order value exceeds maximum (${self.config.max_order_value_usd:,.0f})",
                'warnings': warnings
            }
        
        # Check for unusual activity
        if stats.get('total_trades', 0) > 50:  # More than 50 trades today
            warnings.append("High trading activity detected")
        
        return {
            'allowed': True,
            'reason': None,
            'warnings': warnings
        }
    
    def update_position(self, symbol: str, quantity: float, avg_price: float):
        """Update position tracking"""
        self._positions[symbol] = quantity
    
    def record_trade(self, trade: Dict):
        """Record a trade for monitoring"""
        self._trades_today.append({
            **trade,
            'timestamp': datetime.now().isoformat()
        })
        
        today = datetime.now().date().isoformat()
        if today in self._daily_stats:
            self._daily_stats[today]['total_trades'] += 1
    
    def get_daily_summary(self) -> Dict:
        """Get today's trading summary"""
        today = datetime.now().date().isoformat()
        return self._daily_stats.get(today, {})


class EnvironmentValidator:
    """Validate environment configuration before startup"""
    
    REQUIRED_VARS = {
        'development': [],
        'staging': ['ALPACA_API_KEY', 'ALPACA_SECRET_KEY'],
        'production': [
            'ALPACA_API_KEY',
            'ALPACA_SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_URL'
        ]
    }
    
    @classmethod
    def validate(cls, env: Environment) -> Dict[str, Any]:
        """
        Validate environment configuration
        
        Returns:
            {'valid': bool, 'missing': List[str], 'warnings': List[str]}
        """
        missing = []
        warnings = []
        
        required = cls.REQUIRED_VARS.get(env.value, [])
        
        for var in required:
            if not os.getenv(var):
                missing.append(var)
        
        # Check for default secrets
        jwt_secret = os.getenv('JWT_SECRET_KEY', '')
        if jwt_secret and ('default' in jwt_secret.lower() or 'change' in jwt_secret.lower()):
            warnings.append("JWT_SECRET_KEY appears to be a default value - change for production!")
        
        if env == Environment.PRODUCTION:
            # Additional production checks
            trading_mode = os.getenv('TRADING_MODE', 'paper_only')
            if trading_mode == 'live':
                warnings.append("⚠️ TRADING_MODE is set to 'live' - real money at risk!")
            
            # Check data source
            data_source = os.getenv('DATA_SOURCE', 'mock')
            if data_source == 'mock':
                warnings.append("DATA_SOURCE is 'mock' - using simulated data")
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'warnings': warnings,
            'environment': env.value
        }


class AuditLogger:
    """Audit logging for all trading activity"""
    
    def __init__(self, log_path: str = "./logs/audit.log"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Setup audit logger
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        fh.setFormatter(formatter)
        self.audit_logger.addHandler(fh)
    
    def log_api_call(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float
    ):
        """Log API call"""
        self.audit_logger.info(
            f"API_CALL | user={user_id} | {method} {endpoint} | "
            f"status={status_code} | duration={duration_ms:.2f}ms"
        )
    
    def log_trade(
        self,
        user_id: str,
        broker: str,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        order_id: str,
        trading_mode: str
    ):
        """Log trade execution"""
        self.audit_logger.info(
            f"TRADE | user={user_id} | broker={broker} | mode={trading_mode} | "
            f"{side} {quantity} {symbol} @ {price} | order_id={order_id}"
        )
    
    def log_security_event(
        self,
        event_type: str,
        user_id: str,
        details: str,
        severity: str = "INFO"
    ):
        """Log security-related event"""
        self.audit_logger.info(
            f"SECURITY | {severity} | {event_type} | user={user_id} | {details}"
        )
    
    def log_risk_event(
        self,
        event_type: str,
        user_id: str,
        details: str,
        action_taken: str
    ):
        """Log risk management event"""
        self.audit_logger.warning(
            f"RISK | {event_type} | user={user_id} | {details} | action={action_taken}"
        )


class ProductionSecurity:
    """Main security manager - combines all security features"""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        
        # Initialize components
        self.api_keys = APIKeyManager()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window_seconds
        )
        self.trading_safety = TradingSafety(self.config)
        self.audit_logger = AuditLogger(self.config.audit_log_path)
        
        # Circuit breakers for external services
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        logger.info(f"Production Security initialized (mode={self.config.trading_mode.value})")
    
    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                name=name,
                max_failures=self.config.max_api_failures,
                reset_timeout=self.config.circuit_breaker_reset_seconds
            )
        return self.circuit_breakers[name]
    
    def validate_api_key(self, key: str, permission: str = None) -> bool:
        """Validate API key"""
        return self.api_keys.validate_key(key, permission)
    
    def check_rate_limit(self, key: str) -> Dict[str, Any]:
        """Check rate limit for key"""
        allowed = self.rate_limiter.is_allowed(key)
        return {
            'allowed': allowed,
            'remaining': self.rate_limiter.get_remaining(key),
            'reset_in': self.rate_limiter.get_reset_time(key)
        }
    
    def is_live_trading_allowed(self) -> bool:
        """Check if live trading is permitted"""
        if self.config.trading_mode == TradingMode.PAPER_ONLY:
            return False
        if self.config.trading_mode == TradingMode.LIVE:
            return True
        # Hybrid mode - depends on other checks
        return self.config.environment == Environment.PRODUCTION
    
    def get_trading_mode_display(self) -> str:
        """Get human-readable trading mode status"""
        mode = self.config.trading_mode.value.upper()
        env = self.config.environment.value.upper()
        
        if self.config.trading_mode == TradingMode.LIVE:
            return f"🔴 LIVE TRADING ({env}) - REAL MONEY AT RISK"
        elif self.config.trading_mode == TradingMode.HYBRID:
            return f"🟡 HYBRID MODE ({env})"
        else:
            return f"🟢 PAPER TRADING ONLY ({env}) - SAFE"


# Global security instance
_security_instance: Optional[ProductionSecurity] = None


def get_security() -> ProductionSecurity:
    """Get global security instance"""
    global _security_instance
    if _security_instance is None:
        _security_instance = ProductionSecurity()
    return _security_instance


def init_security(config: SecurityConfig):
    """Initialize global security with config"""
    global _security_instance
    _security_instance = ProductionSecurity(config)
    return _security_instance


# Decorators for easy integration
def require_api_key(permission: str = None):
    """Decorator to require valid API key"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get API key from request context
            api_key = kwargs.get('api_key') or kwargs.get('headers', {}).get('X-API-Key')
            
            if not api_key:
                raise PermissionError("API key required")
            
            security = get_security()
            if not security.validate_api_key(api_key, permission):
                raise PermissionError("Invalid or unauthorized API key")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limited(key_func: Callable = None):
    """Decorator to apply rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Determine rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = kwargs.get('api_key', 'default')
            
            security = get_security()
            limit_info = security.check_rate_limit(key)
            
            if not limit_info['allowed']:
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Reset in {limit_info['reset_in']}s"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    pass


# Example usage
if __name__ == "__main__":
    # Validate environment
    env_check = EnvironmentValidator.validate(Environment.PRODUCTION)
    print(f"Environment valid: {env_check['valid']}")
    if env_check['missing']:
        print(f"Missing: {env_check['missing']}")
    if env_check['warnings']:
        print(f"Warnings: {env_check['warnings']}")
    
    # Initialize security
    config = SecurityConfig(
        trading_mode=TradingMode.PAPER_ONLY,
        environment=Environment.STAGING
    )
    security = init_security(config)
    print(security.get_trading_mode_display())
