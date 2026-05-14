"""
Cross-Asset Arbitrage Detection
===============================
Detect arbitrage opportunities across:
- ETF vs underlying basket
- ADR vs underlying foreign stock
- Crypto spot vs futures
- Options vs underlying (conversion/reversal)
- Multi-exchange price differences
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ArbitrageType(Enum):
    ETF_BASKET = "etf_basket"  # ETF vs components
    ADR_UNDERLYING = "adr_underlying"  # ADR vs foreign stock
    CRYPTO_SPOT_FUTURES = "crypto_spot_futures"  # Basis trade
    OPTIONS_CONVERSION = "options_conversion"  # Put-call parity
    MULTI_EXCHANGE = "multi_exchange"  # Cross-exchange arb
    CASH_CARRY = "cash_carry"  # Futures basis


@dataclass
class ArbitrageOpportunity:
    """Detected arbitrage opportunity"""
    arb_type: ArbitrageType
    leg1: str  # Buy this
    leg2: str  # Sell this
    leg1_price: float
    leg2_price: float
    spread: float
    spread_pct: float
    profit_potential: float
    confidence: float
    timestamp: datetime
    metadata: Dict


class CrossAssetArbitrageDetector:
    """
    Multi-asset arbitrage detection engine
    
    Detects mispricings across different asset types and venues
    """
    
    def __init__(self, transaction_cost_pct: float = 0.001):
        self.transaction_cost = transaction_cost_pct  # 0.1% default
        self.min_spread_threshold = 0.002  # 0.2% minimum
        self.price_cache: Dict[str, Dict] = {}
    
    def update_prices(self, ticker: str, price: float, 
                     source: str, timestamp: Optional[datetime] = None):
        """Update price cache"""
        if ticker not in self.price_cache:
            self.price_cache[ticker] = {}
        
        self.price_cache[ticker][source] = {
            'price': price,
            'timestamp': timestamp or datetime.now()
        }
    
    def detect_etf_basket_arbitrage(self, 
                                   etf_ticker: str,
                                   components: Dict[str, float],
                                   component_prices: Dict[str, float]) -> Optional[ArbitrageOpportunity]:
        """
        Detect arbitrage between ETF and underlying basket
        
        Args:
            etf_ticker: ETF symbol
            components: Dict of {ticker: weight} for ETF components
            component_prices: Current prices of components
        """
        if etf_ticker not in self.price_cache:
            return None
        
        etf_price = list(self.price_cache[etf_ticker].values())[0]['price']
        
        # Calculate NAV
        nav = sum(
            component_prices.get(ticker, 0) * weight
            for ticker, weight in components.items()
        )
        
        # Calculate spread
        spread = etf_price - nav
        spread_pct = abs(spread) / nav if nav > 0 else 0
        
        if spread_pct > self.min_spread_threshold + self.transaction_cost:
            profit = spread_pct - self.transaction_cost
            
            if spread > 0:
                # ETF overpriced: short ETF, buy basket
                return ArbitrageOpportunity(
                    arb_type=ArbitrageType.ETF_BASKET,
                    leg1=etf_ticker,
                    leg2=f"BASKET_{etf_ticker}",
                    leg1_price=etf_price,
                    leg2_price=nav,
                    spread=spread,
                    spread_pct=round(spread_pct * 100, 4),
                    profit_potential=round(profit * 100, 4),
                    confidence=0.8 if spread_pct > 0.005 else 0.6,
                    timestamp=datetime.now(),
                    metadata={
                        'direction': 'short_etf_long_basket',
                        'nav': nav,
                        'premium_discount': 'premium' if spread > 0 else 'discount',
                        'component_count': len(components)
                    }
                )
            else:
                # ETF underpriced: buy ETF, short basket
                return ArbitrageOpportunity(
                    arb_type=ArbitrageType.ETF_BASKET,
                    leg1=f"BASKET_{etf_ticker}",
                    leg2=etf_ticker,
                    leg1_price=nav,
                    leg2_price=etf_price,
                    spread=abs(spread),
                    spread_pct=round(spread_pct * 100, 4),
                    profit_potential=round(profit * 100, 4),
                    confidence=0.8 if spread_pct > 0.005 else 0.6,
                    timestamp=datetime.now(),
                    metadata={
                        'direction': 'long_etf_short_basket',
                        'nav': nav,
                        'premium_discount': 'discount',
                        'component_count': len(components)
                    }
                )
        
        return None
    
    def detect_adr_arbitrage(self,
                            adr_ticker: str,
                            underlying_ticker: str,
                            adr_ratio: float,
                            fx_rate: float) -> Optional[ArbitrageOpportunity]:
        """
        Detect ADR arbitrage
        
        ADR Price should ≈ Underlying Price × Ratio × FX Rate
        """
        if adr_ticker not in self.price_cache or underlying_ticker not in self.price_cache:
            return None
        
        adr_price = list(self.price_cache[adr_ticker].values())[0]['price']
        underlying_price = list(self.price_cache[underlying_ticker].values())[0]['price']
        
        # Calculate implied ADR price
        implied_adr = underlying_price * adr_ratio * fx_rate
        
        spread = adr_price - implied_adr
        spread_pct = abs(spread) / implied_adr if implied_adr > 0 else 0
        
        if spread_pct > self.min_spread_threshold + self.transaction_cost:
            profit = spread_pct - self.transaction_cost
            
            if adr_price > implied_adr:
                return ArbitrageOpportunity(
                    arb_type=ArbitrageType.ADR_UNDERLYING,
                    leg1=underlying_ticker,
                    leg2=adr_ticker,
                    leg1_price=underlying_price,
                    leg2_price=adr_price,
                    spread=spread,
                    spread_pct=round(spread_pct * 100, 4),
                    profit_potential=round(profit * 100, 4),
                    confidence=0.75,
                    timestamp=datetime.now(),
                    metadata={
                        'direction': 'buy_underlying_sell_adr',
                        'adr_ratio': adr_ratio,
                        'fx_rate': fx_rate,
                        'implied_adr': implied_adr
                    }
                )
            else:
                return ArbitrageOpportunity(
                    arb_type=ArbitrageType.ADR_UNDERLYING,
                    leg1=adr_ticker,
                    leg2=underlying_ticker,
                    leg1_price=adr_price,
                    leg2_price=underlying_price,
                    spread=abs(spread),
                    spread_pct=round(spread_pct * 100, 4),
                    profit_potential=round(profit * 100, 4),
                    confidence=0.75,
                    timestamp=datetime.now(),
                    metadata={
                        'direction': 'buy_adr_sell_underlying',
                        'adr_ratio': adr_ratio,
                        'fx_rate': fx_rate,
                        'implied_adr': implied_adr
                    }
                )
        
        return None
    
    def detect_crypto_basis_arbitrage(self,
                                     spot_ticker: str,
                                     futures_ticker: str,
                                     days_to_expiry: float,
                                     funding_rate: float = 0) -> Optional[ArbitrageOpportunity]:
        """
        Detect crypto spot vs futures arbitrage (basis trade)
        
        Fair Futures = Spot × (1 + r × t) + funding adjustments
        """
        if spot_ticker not in self.price_cache or futures_ticker not in self.price_cache:
            return None
        
        spot_price = list(self.price_cache[spot_ticker].values())[0]['price']
        futures_price = list(self.price_cache[futures_ticker].values())[0]['price']
        
        # Assume 5% risk-free rate
        r = 0.05
        t = days_to_expiry / 365
        
        # Calculate fair futures price
        fair_futures = spot_price * (1 + r * t) * (1 + funding_rate * t)
        
        basis = futures_price - spot_price
        basis_pct = basis / spot_price if spot_price > 0 else 0
        
        fair_basis = fair_futures - spot_price
        fair_basis_pct = fair_basis / spot_price if spot_price > 0 else 0
        
        deviation = basis_pct - fair_basis_pct
        
        if abs(deviation) > self.min_spread_threshold + self.transaction_cost:
            profit = abs(deviation) - self.transaction_cost
            
            if basis_pct > fair_basis_pct:
                # Futures overpriced: short futures, buy spot
                return ArbitrageOpportunity(
                    arb_type=ArbitrageType.CRYPTO_SPOT_FUTURES,
                    leg1=spot_ticker,
                    leg2=futures_ticker,
                    leg1_price=spot_price,
                    leg2_price=futures_price,
                    spread=basis,
                    spread_pct=round(abs(deviation) * 100, 4),
                    profit_potential=round(profit * 100, 4),
                    confidence=0.8,
                    timestamp=datetime.now(),
                    metadata={
                        'direction': 'long_spot_short_futures',
                        'basis_pct': round(basis_pct * 100, 4),
                        'fair_basis_pct': round(fair_basis_pct * 100, 4),
                        'days_to_expiry': days_to_expiry,
                        'annualized_return_pct': round(deviation * 365 / days_to_expiry * 100, 2)
                    }
                )
            else:
                # Futures underpriced: buy futures (if contango is very negative)
                return ArbitrageOpportunity(
                    arb_type=ArbitrageType.CRYPTO_SPOT_FUTURES,
                    leg1=futures_ticker,
                    leg2=spot_ticker,
                    leg1_price=futures_price,
                    leg2_price=spot_price,
                    spread=abs(basis),
                    spread_pct=round(abs(deviation) * 100, 4),
                    profit_potential=round(profit * 100, 4),
                    confidence=0.7,
                    timestamp=datetime.now(),
                    metadata={
                        'direction': 'long_futures_short_spot',
                        'basis_pct': round(basis_pct * 100, 4),
                        'fair_basis_pct': round(fair_basis_pct * 100, 4),
                        'days_to_expiry': days_to_expiry
                    }
                )
        
        return None
    
    def detect_options_conversion_arbitrage(self,
                                           underlying_price: float,
                                           strike: float,
                                           call_price: float,
                                           put_price: float,
                                           risk_free_rate: float,
                                           days_to_expiry: float,
                                           dividend_yield: float = 0) -> Optional[ArbitrageOpportunity]:
        """
        Detect put-call parity arbitrage
        
        C - P = S × e^(-qT) - K × e^(-rT)
        
        Where:
        C = Call price
        P = Put price  
        S = Stock price
        K = Strike price
        r = Risk-free rate
        q = Dividend yield
        T = Time to expiry
        """
        T = days_to_expiry / 365
        
        # Put-call parity left side
        lhs = call_price - put_price
        
        # Put-call parity right side
        rhs = underlying_price * np.exp(-dividend_yield * T) - strike * np.exp(-risk_free_rate * T)
        
        spread = lhs - rhs
        spread_pct = abs(spread) / underlying_price if underlying_price > 0 else 0
        
        if spread_pct > self.min_spread_threshold + self.transaction_cost:
            profit = spread_pct - self.transaction_cost
            
            if lhs > rhs:
                # Call overpriced relative to put
                return ArbitrageOpportunity(
                    arb_type=ArbitrageType.OPTIONS_CONVERSION,
                    leg1=f"PUT_{strike}",
                    leg2=f"CALL_{strike}",
                    leg1_price=put_price,
                    leg2_price=call_price,
                    spread=spread,
                    spread_pct=round(spread_pct * 100, 4),
                    profit_potential=round(profit * 100, 4),
                    confidence=0.85,
                    timestamp=datetime.now(),
                    metadata={
                        'direction': 'buy_put_sell_call_buy_stock',
                        'synthetic_price': rhs,
                        'parity_deviation': round(spread, 4),
                        'days_to_expiry': days_to_expiry
                    }
                )
            else:
                # Put overpriced relative to call
                return ArbitrageOpportunity(
                    arb_type=ArbitrageType.OPTIONS_CONVERSION,
                    leg1=f"CALL_{strike}",
                    leg2=f"PUT_{strike}",
                    leg1_price=call_price,
                    leg2_price=put_price,
                    spread=abs(spread),
                    spread_pct=round(spread_pct * 100, 4),
                    profit_potential=round(profit * 100, 4),
                    confidence=0.85,
                    timestamp=datetime.now(),
                    metadata={
                        'direction': 'buy_call_sell_put_sell_stock',
                        'synthetic_price': rhs,
                        'parity_deviation': round(spread, 4),
                        'days_to_expiry': days_to_expiry
                    }
                )
        
        return None
    
    def detect_multi_exchange_arbitrage(self, ticker: str) -> List[ArbitrageOpportunity]:
        """
        Detect price differences across exchanges
        """
        if ticker not in self.price_cache:
            return []
        
        prices = self.price_cache[ticker]
        
        if len(prices) < 2:
            return []
        
        opportunities = []
        
        # Find min and max prices
        exchanges = list(prices.keys())
        price_list = [prices[ex]['price'] for ex in exchanges]
        
        min_price = min(price_list)
        max_price = max(price_list)
        min_ex = exchanges[price_list.index(min_price)]
        max_ex = exchanges[price_list.index(max_price)]
        
        spread = max_price - min_price
        spread_pct = spread / min_price if min_price > 0 else 0
        
        if spread_pct > self.min_spread_threshold + self.transaction_cost:
            profit = spread_pct - self.transaction_cost
            
            opportunities.append(
                ArbitrageOpportunity(
                    arb_type=ArbitrageType.MULTI_EXCHANGE,
                    leg1=ticker,
                    leg2=ticker,
                    leg1_price=min_price,
                    leg2_price=max_price,
                    spread=spread,
                    spread_pct=round(spread_pct * 100, 4),
                    profit_potential=round(profit * 100, 4),
                    confidence=0.9,
                    timestamp=datetime.now(),
                    metadata={
                        'direction': f'buy_{min_ex}_sell_{max_ex}',
                        'buy_exchange': min_ex,
                        'sell_exchange': max_ex,
                        'exchanges_compared': len(exchanges)
                    }
                )
            )
        
        return opportunities
    
    def scan_all_opportunities(self) -> List[ArbitrageOpportunity]:
        """Scan all price cache for arbitrage opportunities"""
        opportunities = []
        
        # Check each ticker for multi-exchange arb
        for ticker in self.price_cache.keys():
            ex_arbs = self.detect_multi_exchange_arbitrage(ticker)
            opportunities.extend(ex_arbs)
        
        # Sort by profit potential
        opportunities.sort(key=lambda x: x.profit_potential, reverse=True)
        
        return opportunities
    
    def get_arbitrage_summary(self) -> Dict:
        """Get summary of current arbitrage landscape"""
        opportunities = self.scan_all_opportunities()
        
        if not opportunities:
            return {
                'status': 'no_opportunities',
                'count': 0,
                'timestamp': datetime.now().isoformat()
            }
        
        by_type = {}
        for opp in opportunities:
            t = opp.arb_type.value
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(opp)
        
        return {
            'status': 'opportunities_found',
            'total_count': len(opportunities),
            'by_type': {k: len(v) for k, v in by_type.items()},
            'highest_profit_bps': max(opp.profit_potential for opp in opportunities),
            'avg_profit_bps': np.mean([opp.profit_potential for opp in opportunities]),
            'top_opportunities': [
                {
                    'type': opp.arb_type.value,
                    'leg1': opp.leg1,
                    'leg2': opp.leg2,
                    'profit_bps': opp.profit_potential,
                    'confidence': opp.confidence
                }
                for opp in opportunities[:10]
            ],
            'timestamp': datetime.now().isoformat()
        }


# Quick usage
def quick_arbitrage_scan(prices: Dict[str, Dict[str, float]]) -> List[Dict]:
    """Quick arbitrage scan from price data"""
    detector = CrossAssetArbitrageDetector()
    
    for ticker, sources in prices.items():
        for source, price in sources.items():
            detector.update_prices(ticker, price, source)
    
    opps = detector.scan_all_opportunities()
    
    return [
        {
            'type': opp.arb_type.value,
            'buy': opp.leg1,
            'sell': opp.leg2,
            'profit_bps': opp.profit_potential,
            'confidence': opp.confidence
        }
        for opp in opps[:10]
    ]
