"""Real-Time Risk Management System."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskLimit:
    limit_type: str
    value: float
    current_usage: float
    warning_threshold: float
    breach_threshold: float

@dataclass
class RiskEvent:
    event_id: str
    timestamp: datetime
    level: RiskLevel
    category: str
    description: str
    value: float
    limit: float
    action_taken: str

class RiskManagementSystem:
    """
    Comprehensive real-time risk monitoring and control.
    Portfolio, market, operational, and credit risk management.
    """
    
    def __init__(self):
        self.user_limits: Dict[str, Dict[str, RiskLimit]] = {}
        self.global_limits = {
            'max_portfolio_var': 1000000,  # $1M daily VaR
            'max_concentration': 0.2,      # 20% in single asset
            'max_leverage': 5.0,           # 5x max leverage
            'max_drawdown': 0.2            # 20% max drawdown
        }
        self.risk_events: List[RiskEvent] = []
        self.exposure_cache: Dict[str, Dict] = {}
        self.calculations_per_second = 10  # Real-time monitoring frequency
        
    async def set_user_limits(self, user_id: str, limits: Dict[str, float]):
        """Set risk limits for a user."""
        self.user_limits[user_id] = {}
        
        for limit_type, value in limits.items():
            self.user_limits[user_id][limit_type] = RiskLimit(
                limit_type=limit_type,
                value=value,
                current_usage=0.0,
                warning_threshold=value * 0.8,  # 80% warning
                breach_threshold=value          # 100% breach
            )
        
        logger.info(f"Risk limits set for user: {user_id}")
    
    async def check_order_risk(self, user_id: str, order: Dict) -> Dict[str, Any]:
        """Pre-trade risk check."""
        violations = []
        warnings = []
        
        # Check user limits
        if user_id in self.user_limits:
            for limit_type, limit in self.user_limits[user_id].items():
                order_impact = self._calculate_order_impact(order, limit_type)
                projected_usage = limit.current_usage + order_impact
                
                if projected_usage > limit.breach_threshold:
                    violations.append({
                        'type': limit_type,
                        'limit': limit.value,
                        'projected': projected_usage,
                        'severity': 'breach'
                    })
                elif projected_usage > limit.warning_threshold:
                    warnings.append({
                        'type': limit_type,
                        'limit': limit.value,
                        'projected': projected_usage,
                        'severity': 'warning'
                    })
        
        # Check global limits
        if order.get('leverage', 1) > self.global_limits['max_leverage']:
            violations.append({
                'type': 'leverage',
                'limit': self.global_limits['max_leverage'],
                'requested': order['leverage'],
                'severity': 'breach'
            })
        
        return {
            'approved': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
            'requires_approval': len(violations) > 0 or len(warnings) > 0
        }
    
    def _calculate_order_impact(self, order: Dict, limit_type: str) -> float:
        """Calculate how an order affects a specific risk limit."""
        if limit_type == 'position_size':
            return order.get('quantity', 0) * order.get('price', 0)
        elif limit_type == 'daily_loss':
            # Worst case scenario
            return order.get('quantity', 0) * order.get('price', 0) * 0.1
        elif limit_type == 'max_orders':
            return 1
        return 0
    
    async def update_exposure(self, user_id: str, positions: List[Dict]):
        """Update real-time exposure calculations."""
        exposure = {
            'total_value': 0.0,
            'gross_exposure': 0.0,
            'net_exposure': 0.0,
            'long_value': 0.0,
            'short_value': 0.0,
            'concentration': {},
            'leverage': 0.0,
            'margin_used': 0.0,
            'var_95': 0.0
        }
        
        for pos in positions:
            value = pos['quantity'] * pos['mark_price']
            exposure['total_value'] += value
            exposure['gross_exposure'] += abs(value)
            exposure['net_exposure'] += value
            
            if value > 0:
                exposure['long_value'] += value
            else:
                exposure['short_value'] += abs(value)
            
            # Track concentration
            symbol = pos['symbol']
            exposure['concentration'][symbol] = exposure['concentration'].get(symbol, 0) + abs(value)
        
        # Calculate metrics
        if exposure['total_value'] > 0:
            exposure['leverage'] = exposure['gross_exposure'] / exposure['total_value']
            
            for symbol in exposure['concentration']:
                exposure['concentration'][symbol] /= exposure['total_value']
        
        # Calculate VaR (simplified)
        if positions:
            returns = [pos.get('daily_return', 0) for pos in positions]
            exposure['var_95'] = np.percentile(returns, 5) * exposure['total_value']
        
        self.exposure_cache[user_id] = exposure
        
        # Check limits
        await self._check_exposure_limits(user_id, exposure)
        
        return exposure
    
    async def _check_exposure_limits(self, user_id: str, exposure: Dict):
        """Check if exposure violates any limits."""
        if user_id not in self.user_limits:
            return
        
        for limit_type, limit in self.user_limits[user_id].items():
            current = exposure.get(limit_type, 0)
            
            if current > limit.breach_threshold:
                await self._create_risk_event(
                    user_id=user_id,
                    level=RiskLevel.CRITICAL,
                    category='limit_breach',
                    description=f'{limit_type} limit breached',
                    value=current,
                    limit=limit.value,
                    action='notify_and_block'
                )
            elif current > limit.warning_threshold:
                await self._create_risk_event(
                    user_id=user_id,
                    level=RiskLevel.HIGH,
                    category='limit_warning',
                    description=f'{limit_type} approaching limit',
                    value=current,
                    limit=limit.value,
                    action='notify'
                )
    
    async def _create_risk_event(self, **kwargs):
        """Create and log a risk event."""
        event = RiskEvent(
            event_id=f"risk_{datetime.now().strftime('%H%M%S%f')}",
            timestamp=datetime.now(),
            **kwargs
        )
        
        self.risk_events.append(event)
        logger.warning(f"Risk Event: {event.description} - Level: {event.level.value}")
        
        # In production, send alerts, trigger circuit breakers, etc.
        return event
    
    async def calculate_portfolio_var(self, user_id: str, 
                                     positions: List[Dict],
                                     confidence: float = 0.95) -> float:
        """Calculate portfolio Value at Risk using historical simulation."""
        if not positions:
            return 0.0
        
        # Simplified VaR calculation
        portfolio_value = sum(p['quantity'] * p['mark_price'] for p in positions)
        
        # Get historical returns (would come from market data)
        returns = [p.get('volatility', 0.02) for p in positions]
        
        if not returns:
            return portfolio_value * 0.02  # 2% default daily VaR
        
        # Parametric VaR
        portfolio_vol = np.mean(returns)
        z_score = 1.645 if confidence == 0.95 else 2.33  # 95% or 99%
        
        daily_var = portfolio_value * portfolio_vol * z_score
        return daily_var
    
    async def stress_test(self, user_id: str, positions: List[Dict],
                         scenarios: List[str] = None) -> Dict[str, float]:
        """Run stress tests on portfolio."""
        if scenarios is None:
            scenarios = ['market_crash', 'volatility_spike', 'liquidity_crisis']
        
        portfolio_value = sum(p['quantity'] * p['mark_price'] for p in positions)
        
        results = {}
        
        scenario_shocks = {
            'market_crash': -0.3,        # -30%
            'volatility_spike': -0.15,   # -15%
            'liquidity_crisis': -0.2,    # -20%
            'interest_rate_shock': -0.1, # -10%
            'correlation_breakdown': -0.25
        }
        
        for scenario in scenarios:
            shock = scenario_shocks.get(scenario, -0.1)
            loss = portfolio_value * shock
            results[scenario] = {
                'shock_pct': shock * 100,
                'loss_amount': loss,
                'remaining_capital': portfolio_value + loss
            }
        
        return results
    
    async def get_risk_report(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive risk report."""
        exposure = self.exposure_cache.get(user_id, {})
        limits = self.user_limits.get(user_id, {})
        
        # Recent events
        recent_events = [
            e for e in self.risk_events
            if e.timestamp > datetime.now() - timedelta(days=1)
        ]
        
        return {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'exposure': exposure,
            'limits': {k: {
                'value': v.value,
                'current': v.current_usage,
                'utilization_pct': (v.current_usage / v.value * 100) if v.value > 0 else 0
            } for k, v in limits.items()},
            'recent_events': len(recent_events),
            'critical_events': sum(1 for e in recent_events if e.level == RiskLevel.CRITICAL),
            'status': 'healthy' if not recent_events else 'attention_required'
        }
    
    async def circuit_breaker_check(self, market_data: Dict) -> bool:
        """Check if circuit breakers should be triggered."""
        # Check for extreme moves
        daily_change = market_data.get('daily_change_pct', 0)
        
        if abs(daily_change) > 10:  # 10% move
            await self._create_risk_event(
                user_id='global',
                level=RiskLevel.CRITICAL,
                category='circuit_breaker',
                description=f'Circuit breaker triggered: {daily_change}% move',
                value=daily_change,
                limit=10,
                action='halt_trading'
            )
            return True
        
        return False

risk_manager = RiskManagementSystem()
