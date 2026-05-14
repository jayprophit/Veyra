"""
Crypto Derivatives Trading
=========================
Robinhood+ level crypto derivatives and options trading
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DerivativeType(Enum):
    """Crypto derivative types"""
    FUTURES = "futures"
    OPTIONS = "options"
    PERPETUAL_SWAPS = "perpetual_swaps"
    LEVERAGED_TOKENS = "leveraged_tokens"
    SYNTHETICS = "synthetics"


class OptionType(Enum):
    """Option types"""
    CALL = "call"
    PUT = "put"


class OptionStyle(Enum):
    """Option styles"""
    EUROPEAN = "european"
    AMERICAN = "american"


@dataclass
class CryptoDerivative:
    """Crypto derivative instrument"""
    symbol: str
    derivative_type: DerivativeType
    underlying_asset: str
    strike_price: Optional[float]
    expiration_date: Optional[datetime]
    option_type: Optional[OptionType]
    option_style: Optional[OptionStyle]
    contract_size: float
    leverage: float
    margin_requirement: float
    funding_rate: Optional[float]
    mark_price: float
    bid_price: float
    ask_price: float
    volume_24h: float
    open_interest: float
    implied_volatility: Optional[float]
    delta: Optional[float]
    gamma: Optional[float]
    theta: Optional[float]
    vega: Optional[float]
    created_at: datetime


@dataclass
class DerivativeOrder:
    """Derivative trading order"""
    order_id: str
    symbol: str
    side: str  # buy/sell
    order_type: str  # market/limit/stop
    quantity: float
    price: Optional[float]
    stop_price: Optional[float]
    time_in_force: str
    leverage: float
    margin_used: float
    liquidation_price: float
    created_at: datetime
    status: str = "pending"


@dataclass
class Position:
    """Trading position"""
    symbol: str
    side: str
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    margin_used: float
    liquidation_price: float
    funding_fees_paid: float
    created_at: datetime


class CryptoDerivativesTrading:
    """Crypto derivatives trading engine"""
    
    def __init__(self):
        self.available_derivatives: Dict[str, CryptoDerivative] = {}
        self.open_positions: Dict[str, Position] = {}
        self.active_orders: Dict[str, DerivativeOrder] = {}
        self.order_history: List[DerivativeOrder] = []
        self.margin_requirements: Dict[str, float] = {}
        self.risk_limits: Dict[str, float] = {}
        self.funding_rates: Dict[str, float] = {}
        
        # Initialize default settings
        self._initialize_derivatives()
        self._initialize_risk_limits()
        
    def _initialize_derivatives(self):
        """Initialize available crypto derivatives"""
        # BTC Futures
        self.available_derivatives["BTC-PERP"] = CryptoDerivative(
            symbol="BTC-PERP",
            derivative_type=DerivativeType.PERPETUAL_SWAPS,
            underlying_asset="BTC",
            strike_price=None,
            expiration_date=None,
            option_type=None,
            option_style=None,
            contract_size=1.0,
            leverage=10.0,
            margin_requirement=0.1,
            funding_rate=0.0001,
            mark_price=45000.0,
            bid_price=44999.0,
            ask_price=45001.0,
            volume_24h=1000000.0,
            open_interest=50000.0,
            implied_volatility=None,
            delta=None,
            gamma=None,
            theta=None,
            vega=None,
            created_at=datetime.now()
        )
        
        # ETH Futures
        self.available_derivatives["ETH-PERP"] = CryptoDerivative(
            symbol="ETH-PERP",
            derivative_type=DerivativeType.PERPETUAL_SWAPS,
            underlying_asset="ETH",
            strike_price=None,
            expiration_date=None,
            option_type=None,
            option_style=None,
            contract_size=1.0,
            leverage=10.0,
            margin_requirement=0.1,
            funding_rate=0.0001,
            mark_price=3000.0,
            bid_price=2999.0,
            ask_price=3001.0,
            volume_24h=800000.0,
            open_interest=40000.0,
            implied_volatility=None,
            delta=None,
            gamma=None,
            theta=None,
            vega=None,
            created_at=datetime.now()
        )
        
        # BTC Options
        self.available_derivatives["BTC-45000-C"] = CryptoDerivative(
            symbol="BTC-45000-C",
            derivative_type=DerivativeType.OPTIONS,
            underlying_asset="BTC",
            strike_price=45000.0,
            expiration_date=datetime.now() + timedelta(days=30),
            option_type=OptionType.CALL,
            option_style=OptionStyle.EUROPEAN,
            contract_size=1.0,
            leverage=5.0,
            margin_requirement=0.2,
            funding_rate=None,
            mark_price=1500.0,
            bid_price=1495.0,
            ask_price=1505.0,
            volume_24h=10000.0,
            open_interest=5000.0,
            implied_volatility=0.8,
            delta=0.55,
            gamma=0.02,
            theta=-0.05,
            vega=0.3,
            created_at=datetime.now()
        )
        
    def _initialize_risk_limits(self):
        """Initialize risk limits"""
        self.risk_limits = {
            "max_leverage": 20.0,
            "max_position_size": 1000000.0,
            "max_margin_usage": 0.8,
            "max_open_positions": 50,
            "min_margin_requirement": 0.05,
            "liquidation_threshold": 0.9
        }
        
    async def place_derivative_order(self, order_params: Dict[str, Any]) -> DerivativeOrder:
        """Place derivative trading order"""
        try:
            # Validate order parameters
            validation_result = await self._validate_order(order_params)
            if not validation_result["valid"]:
                raise ValueError(validation_result["error"])
                
            # Create order
            order = DerivativeOrder(
                order_id=f"deriv_order_{datetime.now().timestamp()}",
                symbol=order_params["symbol"],
                side=order_params["side"],
                order_type=order_params["order_type"],
                quantity=order_params["quantity"],
                price=order_params.get("price"),
                stop_price=order_params.get("stop_price"),
                time_in_force=order_params.get("time_in_force", "GTC"),
                leverage=order_params.get("leverage", 1.0),
                margin_used=0.0,
                liquidation_price=0.0,
                created_at=datetime.now()
            )
            
            # Calculate margin and liquidation price
            derivative = self.available_derivatives.get(order.symbol)
            if derivative:
                order.margin_used = await self._calculate_margin_requirement(order, derivative)
                order.liquidation_price = await self._calculate_liquidation_price(order, derivative)
                
            # Check margin limits
            if not await self._check_margin_limits(order):
                raise ValueError("Insufficient margin or exceeds margin limits")
                
            # Execute order
            await self._execute_derivative_order(order)
            
            # Update positions
            await self._update_positions(order)
            
            # Store order
            self.active_orders[order.order_id] = order
            self.order_history.append(order)
            
            logger.info(f"Derivative order placed: {order.order_id}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing derivative order: {e}")
            raise
            
    async def _validate_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate order parameters"""
        try:
            # Check required fields
            required_fields = ["symbol", "side", "order_type", "quantity"]
            for field in required_fields:
                if field not in order_params:
                    return {"valid": False, "error": f"Missing required field: {field}"}
                    
            # Check symbol exists
            if order_params["symbol"] not in self.available_derivatives:
                return {"valid": False, "error": "Invalid derivative symbol"}
                
            # Check side
            if order_params["side"] not in ["buy", "sell"]:
                return {"valid": False, "error": "Invalid order side"}
                
            # Check order type
            if order_params["order_type"] not in ["market", "limit", "stop"]:
                return {"valid": False, "error": "Invalid order type"}
                
            # Check quantity
            if order_params["quantity"] <= 0:
                return {"valid": False, "error": "Quantity must be positive"}
                
            # Check leverage limits
            leverage = order_params.get("leverage", 1.0)
            if leverage > self.risk_limits["max_leverage"]:
                return {"valid": False, "error": f"Leverage exceeds maximum of {self.risk_limits['max_leverage']}x"}
                
            # Check price for limit orders
            if order_params["order_type"] == "limit" and "price" not in order_params:
                return {"valid": False, "error": "Limit orders require a price"}
                
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Error validating order: {e}")
            return {"valid": False, "error": str(e)}
            
    async def _calculate_margin_requirement(self, order: DerivativeOrder, derivative: CryptoDerivative) -> float:
        """Calculate margin requirement for order"""
        try:
            # Get current price
            current_price = derivative.mark_price
            
            # Calculate notional value
            if order.order_type == "market":
                notional_value = order.quantity * current_price
            else:
                notional_value = order.quantity * (order.price or current_price)
                
            # Apply leverage
            margin_requirement = notional_value / order.leverage * derivative.margin_requirement
            
            return margin_requirement
            
        except Exception as e:
            logger.error(f"Error calculating margin requirement: {e}")
            return 0.0
            
    async def _calculate_liquidation_price(self, order: DerivativeOrder, derivative: CryptoDerivative) -> float:
        """Calculate liquidation price for position"""
        try:
            # Get current price
            current_price = derivative.mark_price
            
            # Calculate liquidation price based on leverage and side
            if order.side == "buy":
                # Long position
                liquidation_price = current_price * (1 - 1 / order.leverage * 0.9)
            else:
                # Short position
                liquidation_price = current_price * (1 + 1 / order.leverage * 0.9)
                
            return liquidation_price
            
        except Exception as e:
            logger.error(f"Error calculating liquidation price: {e}")
            return 0.0
            
    async def _check_margin_limits(self, order: DerivativeOrder) -> bool:
        """Check if order respects margin limits"""
        try:
            # Calculate total margin usage
            current_margin_usage = sum(pos.margin_used for pos in self.open_positions.values())
            new_margin_usage = current_margin_usage + order.margin_used
            
            # Check margin usage limit
            max_margin_usage = self.risk_limits["max_margin_usage"]
            if new_margin_usage > max_margin_usage:
                return False
                
            # Check position size limit
            if order.quantity > self.risk_limits["max_position_size"]:
                return False
                
            # Check open positions limit
            if len(self.open_positions) >= self.risk_limits["max_open_positions"]:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking margin limits: {e}")
            return False
            
    async def _execute_derivative_order(self, order: DerivativeOrder):
        """Execute derivative order"""
        try:
            # Simulate order execution
            derivative = self.available_derivatives.get(order.symbol)
            if not derivative:
                return
                
            # Determine execution price
            if order.order_type == "market":
                execution_price = derivative.mark_price
            else:
                execution_price = order.price or derivative.mark_price
                
            # Update order status
            order.status = "filled"
            
            logger.info(f"Derivative order executed: {order.order_id} at {execution_price}")
            
        except Exception as e:
            logger.error(f"Error executing derivative order: {e}")
            order.status = "failed"
            
    async def _update_positions(self, order: DerivativeOrder):
        """Update trading positions"""
        try:
            derivative = self.available_derivatives.get(order.symbol)
            if not derivative:
                return
                
            # Get or create position
            position_key = f"{order.symbol}_{order.side}"
            if position_key in self.open_positions:
                position = self.open_positions[position_key]
                # Update existing position
                position.size += order.quantity
                position.margin_used += order.margin_used
            else:
                # Create new position
                position = Position(
                    symbol=order.symbol,
                    side=order.side,
                    size=order.quantity,
                    entry_price=derivative.mark_price,
                    current_price=derivative.mark_price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    margin_used=order.margin_used,
                    liquidation_price=order.liquidation_price,
                    funding_fees_paid=0.0,
                    created_at=datetime.now()
                )
                self.open_positions[position_key] = position
                
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
            
    async def calculate_options_greeks(self, symbol: str, underlying_price: float, 
                                     time_to_expiry: float, risk_free_rate: float) -> Dict[str, float]:
        """Calculate options Greeks using Black-Scholes model"""
        try:
            derivative = self.available_derivatives.get(symbol)
            if not derivative or derivative.derivative_type != DerivativeType.OPTIONS:
                return {}
                
            # Black-Scholes parameters
            S = underlying_price  # Underlying price
            K = derivative.strike_price  # Strike price
            T = time_to_expiry  # Time to expiry
            r = risk_free_rate  # Risk-free rate
            sigma = derivative.implied_volatility or 0.8  # Volatility
            
            # Calculate d1 and d2
            from scipy.stats import norm
            
            d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            # Calculate Greeks
            if derivative.option_type == OptionType.CALL:
                delta = norm.cdf(d1)
                theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
                vega = S * norm.pdf(d1) * np.sqrt(T)
            else:  # PUT
                delta = norm.cdf(d1) - 1
                theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
                vega = S * norm.pdf(d1) * np.sqrt(T)
                
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            
            return {
                "delta": delta,
                "gamma": gamma,
                "theta": theta,
                "vega": vega
            }
            
        except Exception as e:
            logger.error(f"Error calculating options Greeks: {e}")
            return {}
            
    async def calculate_funding_rate(self, symbol: str) -> float:
        """Calculate funding rate for perpetual swaps"""
        try:
            derivative = self.available_derivatives.get(symbol)
            if not derivative or derivative.derivative_type != DerivativeType.PERPETUAL_SWAPS:
                return 0.0
                
            # Mock funding rate calculation
            # In production, would calculate based on index price and mark price difference
            base_rate = 0.0001  # 0.01% base rate
            
            # Adjust based on market conditions
            market_pressure = (derivative.ask_price - derivative.bid_price) / derivative.mark_price
            funding_rate = base_rate + market_pressure * 0.00001
            
            # Store funding rate
            self.funding_rates[symbol] = funding_rate
            
            return funding_rate
            
        except Exception as e:
            logger.error(f"Error calculating funding rate: {e}")
            return 0.0
            
    async def calculate_position_pnl(self, position: Position) -> Dict[str, float]:
        """Calculate position P&L"""
        try:
            derivative = self.available_derivatives.get(position.symbol)
            if not derivative:
                return {"unrealized_pnl": 0.0, "total_pnl": 0.0}
                
            # Calculate unrealized P&L
            if position.side == "buy":
                unrealized_pnl = (derivative.mark_price - position.entry_price) * position.size
            else:
                unrealized_pnl = (position.entry_price - derivative.mark_price) * position.size
                
            # Add funding fees
            funding_pnl = -position.funding_fees_paid
            
            # Total P&L
            total_pnl = unrealized_pnl + position.realized_pnl + funding_pnl
            
            return {
                "unrealized_pnl": unrealized_pnl,
                "realized_pnl": position.realized_pnl,
                "funding_pnl": funding_pnl,
                "total_pnl": total_pnl
            }
            
        except Exception as e:
            logger.error(f"Error calculating position P&L: {e}")
            return {"unrealized_pnl": 0.0, "total_pnl": 0.0}
            
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary"""
        try:
            total_margin_used = sum(pos.margin_used for pos in self.open_positions.values())
            total_unrealized_pnl = 0.0
            total_realized_pnl = 0.0
            
            for position in self.open_positions.values():
                pnl = await self.calculate_position_pnl(position)
                total_unrealized_pnl += pnl["unrealized_pnl"]
                total_realized_pnl += pnl["realized_pnl"]
                
            return {
                "total_positions": len(self.open_positions),
                "total_margin_used": total_margin_used,
                "total_unrealized_pnl": total_unrealized_pnl,
                "total_realized_pnl": total_realized_pnl,
                "total_pnl": total_unrealized_pnl + total_realized_pnl,
                "margin_utilization": total_margin_used / self.risk_limits["max_margin_usage"],
                "active_orders": len(self.active_orders),
                "available_derivatives": len(self.available_derivatives)
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {}
            
    async def close_position(self, symbol: str, side: str, quantity: float) -> bool:
        """Close trading position"""
        try:
            position_key = f"{symbol}_{side}"
            if position_key not in self.open_positions:
                return False
                
            position = self.open_positions[position_key]
            
            # Create closing order
            close_order_params = {
                "symbol": symbol,
                "side": "sell" if side == "buy" else "buy",
                "order_type": "market",
                "quantity": min(quantity, position.size),
                "leverage": 1.0
            }
            
            # Place closing order
            await self.place_derivative_order(close_order_params)
            
            # Update position
            position.size -= close_order_params["quantity"]
            if position.size <= 0:
                del self.open_positions[position_key]
                
            return True
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False
            
    async def get_risk_metrics(self) -> Dict[str, Any]:
        """Get risk metrics for the portfolio"""
        try:
            # Calculate portfolio-level metrics
            total_exposure = 0.0
            total_leverage = 0.0
            liquidation_risk = 0.0
            
            for position in self.open_positions.values():
                derivative = self.available_derivatives.get(position.symbol)
                if derivative:
                    exposure = position.size * derivative.mark_price
                    total_exposure += exposure
                    total_leverage += exposure * derivative.leverage
                    
                    # Check liquidation risk
                    price_diff = abs(derivative.mark_price - position.liquidation_price) / derivative.mark_price
                    if price_diff < 0.1:  # Within 10% of liquidation price
                        liquidation_risk += 1
                        
            # Calculate risk scores
            leverage_ratio = total_leverage / total_exposure if total_exposure > 0 else 0
            liquidation_risk_score = liquidation_risk / len(self.open_positions) if self.open_positions else 0
            
            return {
                "total_exposure": total_exposure,
                "total_leverage": total_leverage,
                "leverage_ratio": leverage_ratio,
                "liquidation_risk": liquidation_risk_score,
                "risk_level": self._calculate_risk_level(leverage_ratio, liquidation_risk_score),
                "margin_utilization": sum(pos.margin_used for pos in self.open_positions.values()) / self.risk_limits["max_margin_usage"]
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
            
    def _calculate_risk_level(self, leverage_ratio: float, liquidation_risk: float) -> str:
        """Calculate overall risk level"""
        risk_score = leverage_ratio * 0.6 + liquidation_risk * 0.4
        
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "medium"
        elif risk_score < 0.8:
            return "high"
        else:
            return "extreme"


# Global crypto derivatives trading instance
_crypto_derivatives_trading = None

def get_crypto_derivatives_trading() -> CryptoDerivativesTrading:
    """Get the global crypto derivatives trading instance"""
    global _crypto_derivatives_trading
    if _crypto_derivatives_trading is None:
        _crypto_derivatives_trading = CryptoDerivativesTrading()
    return _crypto_derivatives_trading
