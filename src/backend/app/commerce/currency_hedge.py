"""
Currency Exchange & Hedging System
Manages FX exposure, hedging strategies, and multi-currency operations
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
import asyncio


class HedgeType(Enum):
    FORWARD = "forward"  # Lock in rate for future date
    OPTIONS = "options"  # Right but not obligation
    SWAP = "swap"  # Exchange one currency for another
    SPOT = "spot"  # Immediate exchange
    FUTURES = "futures"  # Standardized contract


class HedgeStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    EXERCISED = "exercised"
    CANCELLED = "cancelled"


@dataclass
class FXRate:
    """Foreign exchange rate"""
    base_currency: str
    quote_currency: str
    rate: Decimal
    bid: Decimal
    ask: Decimal
    timestamp: datetime
    source: str = "market"


@dataclass
class CurrencyExposure:
    """Currency exposure for a business/individual"""
    entity_id: str
    currency: str
    
    # Exposures
    receivables: Decimal = Decimal("0")  # Money coming in
    payables: Decimal = Decimal("0")  # Money going out
    assets: Decimal = Decimal("0")  # Foreign currency assets
    liabilities: Decimal = Decimal("0")  # Foreign currency liabilities
    
    # Net exposure
    @property
    def net_exposure(self) -> Decimal:
        return self.receivables + self.assets - self.payables - self.liabilities
    
    @property
    def gross_exposure(self) -> Decimal:
        return self.receivables + self.payables + self.assets + self.liabilities


@dataclass
class HedgePosition:
    """Currency hedge position"""
    hedge_id: str
    entity_id: str
    hedge_type: HedgeType
    status: HedgeStatus
    
    # Details
    base_currency: str
    quote_currency: str
    amount: Decimal
    
    # Rates
    entry_rate: Decimal  # Rate when hedge created
    target_rate: Optional[Decimal] = None  # For options
    locked_rate: Optional[Decimal] = None  # For forwards
    
    # Dates
    entry_date: datetime
    maturity_date: datetime
    settlement_date: Optional[datetime] = None
    
    # Pricing
    premium_paid: Decimal = Decimal("0")  # For options
    margin_required: Decimal = Decimal("0")  # For futures/forwards
    
    # Current value
    current_value: Decimal = Decimal("0")
    unrealized_pnl: Decimal = Decimal("0")
    
    # Metadata
    purpose: str = ""  # "payable", "receivable", "speculation"
    counterparty: str = ""  # Bank/broker name


class CurrencyHedgeManager:
    """
    Manages foreign exchange and hedging operations
    
    Features:
    - Real-time FX rates
    - Exposure tracking
    - Hedge strategies (forwards, options, swaps)
    - P&L monitoring
    - Risk analysis
    """
    
    def __init__(self):
        self.fx_rates: Dict[str, FXRate] = {}  # "USD/EUR" -> rate
        self.exposures: Dict[str, List[CurrencyExposure]] = {}  # entity_id -> exposures
        self.hedges: Dict[str, HedgePosition] = {}
        
        # Major currency pairs
        self.major_pairs = [
            "EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF",
            "USD/CAD", "AUD/USD", "NZD/USD", "EUR/GBP",
            "EUR/JPY", "GBP/JPY"
        ]
        
        # Historical rates for analysis
        self.rate_history: Dict[str, List[Dict]] = {}
    
    async def update_fx_rates(self) -> Dict[str, Any]:
        """
        Fetch latest FX rates from market data providers
        
        Sources: Bloomberg, Reuters, AlphaVantage, etc.
        """
        # In production: Call FX API
        # Mock rates for demonstration
        mock_rates = {
            "EUR/USD": Decimal("1.0850"),
            "USD/JPY": Decimal("149.50"),
            "GBP/USD": Decimal("1.2650"),
            "USD/CHF": Decimal("0.8850"),
            "USD/CAD": Decimal("1.3550"),
            "AUD/USD": Decimal("0.6550"),
            "USD/CNY": Decimal("7.2250"),
            "USD/SGD": Decimal("1.3450"),
            "USD/AED": Decimal("3.6725"),
        }
        
        updated = 0
        for pair, rate in mock_rates.items():
            base, quote = pair.split("/")
            
            # Calculate bid/ask spread (typically 0.01-0.05% for majors)
            spread = rate * Decimal("0.0002")
            
            fx_rate = FXRate(
                base_currency=base,
                quote_currency=quote,
                rate=rate,
                bid=rate - spread,
                ask=rate + spread,
                timestamp=datetime.utcnow()
            )
            
            self.fx_rates[pair] = fx_rate
            
            # Store history
            if pair not in self.rate_history:
                self.rate_history[pair] = []
            self.rate_history[pair].append({
                "rate": float(rate),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            updated += 1
        
        return {
            "updated_pairs": updated,
            "timestamp": datetime.utcnow().isoformat(),
            "rates": {pair: float(rate.rate) for pair, rate in self.fx_rates.items()}
        }
    
    async def get_rate(
        self,
        base_currency: str,
        quote_currency: str
    ) -> Optional[FXRate]:
        """Get current FX rate for currency pair"""
        pair = f"{base_currency}/{quote_currency}"
        
        if pair in self.fx_rates:
            return self.fx_rates[pair]
        
        # Try inverse
        inverse_pair = f"{quote_currency}/{base_currency}"
        if inverse_pair in self.fx_rates:
            inverse_rate = self.fx_rates[inverse_pair]
            return FXRate(
                base_currency=base_currency,
                quote_currency=quote_currency,
                rate=Decimal("1") / inverse_rate.rate,
                bid=Decimal("1") / inverse_rate.ask,
                ask=Decimal("1") / inverse_rate.bid,
                timestamp=inverse_rate.timestamp
            )
        
        return None
    
    async def calculate_exposure(
        self,
        entity_id: str
    ) -> Dict[str, Any]:
        """
        Calculate total FX exposure for entity
        
        Sums all receivables, payables, assets, liabilities by currency
        """
        exposures = self.exposures.get(entity_id, [])
        
        if not exposures:
            return {
                "entity_id": entity_id,
                "base_currency": "USD",
                "total_exposure": 0,
                "currencies": []
            }
        
        # Convert all to base currency (USD)
        base_currency = "USD"
        total_exposure = Decimal("0")
        currency_details = []
        
        for exp in exposures:
            # Get rate
            if exp.currency == base_currency:
                rate = Decimal("1")
            else:
                fx_rate = await self.get_rate(exp.currency, base_currency)
                rate = fx_rate.rate if fx_rate else Decimal("1")
            
            usd_value = exp.net_exposure * rate
            total_exposure += usd_value
            
            currency_details.append({
                "currency": exp.currency,
                "local_exposure": float(exp.net_exposure),
                "usd_equivalent": float(usd_value),
                "rate_used": float(rate),
                "receivables": float(exp.receivables),
                "payables": float(exp.payables),
                "assets": float(exp.assets),
                "liabilities": float(exp.liabilities)
            })
        
        return {
            "entity_id": entity_id,
            "base_currency": base_currency,
            "total_exposure_usd": float(total_exposure),
            "currencies": currency_details,
            "hedge_ratio": await self._calculate_hedge_ratio(entity_id, total_exposure),
            "risk_level": self._assess_risk_level(total_exposure)
        }
    
    async def _calculate_hedge_ratio(
        self,
        entity_id: str,
        total_exposure: Decimal
    ) -> float:
        """Calculate percentage of exposure that's hedged"""
        hedged = Decimal("0")
        
        for hedge in self.hedges.values():
            if hedge.entity_id == entity_id and hedge.status == HedgeStatus.ACTIVE:
                # Get USD value
                fx_rate = await self.get_rate(hedge.base_currency, "USD")
                if fx_rate:
                    usd_value = hedge.amount * fx_rate.rate
                    hedged += usd_value
        
        if total_exposure == 0:
            return 0.0
        
        return float((hedged / total_exposure) * 100)
    
    def _assess_risk_level(self, exposure_usd: Decimal) -> str:
        """Assess risk level based on exposure size"""
        thresholds = {
            "low": Decimal("100000"),      # <$100k
            "medium": Decimal("1000000"),  # <$1M
            "high": Decimal("10000000"),   # <$10M
        }
        
        if exposure_usd < thresholds["low"]:
            return "low"
        elif exposure_usd < thresholds["medium"]:
            return "medium"
        elif exposure_usd < thresholds["high"]:
            return "high"
        else:
            return "critical"
    
    async def create_forward_hedge(
        self,
        entity_id: str,
        base_currency: str,
        quote_currency: str,
        amount: Decimal,
        maturity_date: datetime,
        purpose: str = "payable"
    ) -> HedgePosition:
        """
        Create forward contract hedge
        
        Locks in exchange rate for future date
        """
        hedge_id = f"FWD_{entity_id}_{datetime.utcnow().timestamp()}"
        
        # Get current forward rate (usually current spot + forward points)
        fx_rate = await self.get_rate(base_currency, quote_currency)
        if not fx_rate:
            raise ValueError(f"No rate available for {base_currency}/{quote_currency}")
        
        # Forward premium/discount (simplified)
        days_to_maturity = (maturity_date - datetime.utcnow()).days
        forward_adjustment = Decimal(str(days_to_maturity * 0.0001))  # Mock adjustment
        
        locked_rate = fx_rate.rate + forward_adjustment
        
        # Calculate margin requirement (typically 5-10%)
        margin = amount * locked_rate * Decimal("0.05")
        
        hedge = HedgePosition(
            hedge_id=hedge_id,
            entity_id=entity_id,
            hedge_type=HedgeType.FORWARD,
            status=HedgeStatus.ACTIVE,
            base_currency=base_currency,
            quote_currency=quote_currency,
            amount=amount,
            entry_rate=fx_rate.rate,
            locked_rate=locked_rate,
            entry_date=datetime.utcnow(),
            maturity_date=maturity_date,
            margin_required=margin,
            purpose=purpose
        )
        
        self.hedges[hedge_id] = hedge
        
        return hedge
    
    async def create_option_hedge(
        self,
        entity_id: str,
        base_currency: str,
        quote_currency: str,
        amount: Decimal,
        option_type: str,  # call or put
        strike_rate: Decimal,
        maturity_date: datetime,
        purpose: str = "payable"
    ) -> HedgePosition:
        """
        Create FX option hedge
        
        Gives right but not obligation to exchange at strike rate
        """
        hedge_id = f"OPT_{entity_id}_{datetime.utcnow().timestamp()}"
        
        # Calculate option premium (simplified Black-Scholes)
        fx_rate = await self.get_rate(base_currency, quote_currency)
        if not fx_rate:
            raise ValueError("No rate available")
        
        # Volatility assumption (20% annual)
        volatility = Decimal("0.20")
        
        # Premium calculation (simplified)
        days_to_expiry = (maturity_date - datetime.utcnow()).days
        time_value = volatility * Decimal(str(days_to_expiry / 365)).sqrt()
        
        intrinsic_value = abs(strike_rate - fx_rate.rate)
        premium_per_unit = intrinsic_value + (fx_rate.rate * time_value * Decimal("0.1"))
        
        total_premium = amount * premium_per_unit
        
        hedge = HedgePosition(
            hedge_id=hedge_id,
            entity_id=entity_id,
            hedge_type=HedgeType.OPTIONS,
            status=HedgeStatus.ACTIVE,
            base_currency=base_currency,
            quote_currency=quote_currency,
            amount=amount,
            entry_rate=fx_rate.rate,
            target_rate=strike_rate,
            entry_date=datetime.utcnow(),
            maturity_date=maturity_date,
            premium_paid=total_premium,
            purpose=purpose
        )
        
        self.hedges[hedge_id] = hedge
        
        return hedge
    
    async def value_hedges(self, entity_id: str) -> Dict[str, Any]:
        """
        Mark-to-market all hedges for entity
        
        Calculates current value and unrealized P&L
        """
        entity_hedges = [
            h for h in self.hedges.values()
            if h.entity_id == entity_id and h.status == HedgeStatus.ACTIVE
        ]
        
        total_value = Decimal("0")
        total_pnl = Decimal("0")
        
        for hedge in entity_hedges:
            # Get current market rate
            current_rate = await self.get_rate(hedge.base_currency, hedge.quote_currency)
            if not current_rate:
                continue
            
            if hedge.hedge_type == HedgeType.FORWARD:
                # Forward value = (locked_rate - current_rate) * amount
                value = (hedge.locked_rate - current_rate.rate) * hedge.amount
                
            elif hedge.hedge_type == HedgeType.OPTIONS:
                # Option intrinsic value
                if hedge.target_rate:
                    if hedge.base_currency == hedge.quote_currency:  # Call
                        intrinsic = max(current_rate.rate - hedge.target_rate, Decimal("0"))
                    else:  # Put
                        intrinsic = max(hedge.target_rate - current_rate.rate, Decimal("0"))
                    value = intrinsic * hedge.amount - hedge.premium_paid
                else:
                    value = Decimal("0")
            else:
                value = Decimal("0")
            
            hedge.current_value = value
            hedge.unrealized_pnl = value
            
            total_value += value
            total_pnl += value
        
        return {
            "entity_id": entity_id,
            "hedges_count": len(entity_hedges),
            "total_current_value": float(total_value),
            "total_unrealized_pnl": float(total_pnl),
            "hedges": [
                {
                    "hedge_id": h.hedge_id,
                    "type": h.hedge_type.value,
                    "pair": f"{h.base_currency}/{h.quote_currency}",
                    "amount": float(h.amount),
                    "entry_rate": float(h.entry_rate),
                    "current_value": float(h.current_value),
                    "unrealized_pnl": float(h.unrealized_pnl),
                    "maturity_date": h.maturity_date.isoformat()
                }
                for h in entity_hedges
            ]
        }
    
    async def convert_currency(
        self,
        from_currency: str,
        to_currency: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Convert currency at current market rate"""
        if from_currency == to_currency:
            return {
                "from": from_currency,
                "to": to_currency,
                "amount": float(amount),
                "converted": float(amount),
                "rate": 1.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        fx_rate = await self.get_rate(from_currency, to_currency)
        if not fx_rate:
            raise ValueError(f"No rate available for {from_currency}/{to_currency}")
        
        converted = amount * fx_rate.rate
        
        return {
            "from": from_currency,
            "to": to_currency,
            "amount": float(amount),
            "converted": float(converted),
            "rate": float(fx_rate.rate),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_hedge_recommendations(
        self,
        entity_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate hedge recommendations based on exposure
        """
        exposure = await self.calculate_exposure(entity_id)
        recommendations = []
        
        for curr in exposure.get("currencies", []):
            if abs(curr["usd_equivalent"]) > 10000:  # Significant exposure
                currency = curr["currency"]
                
                # Calculate volatility (simplified)
                pair = f"{currency}/USD" if currency != "USD" else "EUR/USD"
                volatility = 0.15  # 15% annual
                
                # Recommend hedge if volatility > 10%
                if volatility > 0.10:
                    exposure_type = "payable" if curr["local_exposure"] < 0 else "receivable"
                    
                    recommendations.append({
                        "currency": currency,
                        "exposure_usd": curr["usd_equivalent"],
                        "exposure_type": exposure_type,
                        "recommended_hedge_type": "forward",
                        "recommended_percentage": min(80, max(20, int(volatility * 100 * 5))),
                        "reasoning": f"{currency} exposure of ${abs(curr['usd_equivalent']):,.0f} with high volatility",
                        "estimated_cost": float(abs(Decimal(str(curr['usd_equivalent'])) * Decimal("0.005")))  # 0.5% premium
                    })
        
        return sorted(recommendations, key=lambda x: abs(x["exposure_usd"]), reverse=True)
