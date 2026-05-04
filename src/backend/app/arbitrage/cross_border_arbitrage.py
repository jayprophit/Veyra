"""Cross-Border and Cross-Currency Arbitrage Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ArbitrageType(Enum):
    SPATIAL = "spatial"          # Same asset, different venues
    TEMPORAL = "temporal"        # Time-based arbitrage
    CROSS_CURRENCY = "currency"  # FX rate discrepancies
    TRIANGULAR = "triangular"    # Three-currency arbitrage

@dataclass
class ArbitrageOpportunity:
    opportunity_id: str
    type: ArbitrageType
    buy_venue: str
    sell_venue: str
    symbol: str
    buy_price: float
    sell_price: float
    spread: float
    spread_pct: float
    estimated_profit: float
    risk_factors: List[str]
    time_to_execute_ms: int
    timestamp: datetime

class CrossBorderArbitrage:
    """
    Detect and execute cross-border, cross-currency arbitrage opportunities.
    Includes latency arbitrage, triangular arbitrage, and spatial arbitrage.
    """
    
    def __init__(self):
        self.venues: Dict[str, Dict] = {}
        self.fx_rates: Dict[str, float] = {}
        self.opportunities: List[ArbitrageOpportunity] = []
        self.min_profit_threshold_bps = 10  # 10 bps minimum
        self.max_latency_ms = 100
        self.trade_history: List[Dict] = []
    
    async def register_venue(self,
                           venue_id: str,
                           name: str,
                           region: str,
                           currency: str,
                           fees_maker: float,
                           fees_taker: float,
                           latency_ms: float):
        """Register trading venue for arbitrage monitoring."""
        self.venues[venue_id] = {
            'name': name,
            'region': region,
            'currency': currency,
            'fees_maker': fees_maker,
            'fees_taker': fees_taker,
            'latency_ms': latency_ms,
            'last_update': datetime.now()
        }
        logger.info(f"Venue registered: {name} ({region})")
    
    async def update_fx_rates(self, rates: Dict[str, float]):
        """Update foreign exchange rates for currency conversion."""
        self.fx_rates.update(rates)
        logger.info(f"FX rates updated: {len(rates)} pairs")
    
    async def scan_spatial_arbitrage(self,
                                   symbol: str,
                                   venue_prices: Dict[str, Dict]) -> List[ArbitrageOpportunity]:
        """Scan for price differences across venues."""
        opportunities = []
        
        venues = list(venue_prices.keys())
        
        for i, buy_venue in enumerate(venues):
            for sell_venue in venues[i+1:]:
                if buy_venue == sell_venue:
                    continue
                
                buy_data = venue_prices[buy_venue]
                sell_data = venue_prices[sell_venue]
                
                # Account for venue fees
                buy_venue_info = self.venues.get(buy_venue, {})
                sell_venue_info = self.venues.get(sell_venue, {})
                
                buy_fee = buy_venue_info.get('fees_taker', 0.002)
                sell_fee = sell_venue_info.get('fees_taker', 0.002)
                
                # Calculate effective prices
                buy_price = buy_data['ask'] * (1 + buy_fee)
                sell_price = sell_data['bid'] * (1 - sell_fee)
                
                spread = sell_price - buy_price
                spread_pct = (spread / buy_price) * 10000  # bps
                
                if spread_pct > self.min_profit_threshold_bps:
                    # Account for FX conversion if needed
                    buy_currency = buy_venue_info.get('currency', 'USD')
                    sell_currency = sell_venue_info.get('currency', 'USD')
                    
                    fx_cost = 0
                    if buy_currency != sell_currency:
                        fx_pair = f"{buy_currency}/{sell_currency}"
                        fx_rate = self.fx_rates.get(fx_pair, 1.0)
                        fx_cost = (1 - fx_rate) * 10000  # bps
                    
                    net_spread = spread_pct - fx_cost
                    
                    if net_spread > self.min_profit_threshold_bps:
                        opp = ArbitrageOpportunity(
                            opportunity_id=f"arb_{datetime.now().strftime('%H%M%S%f')}",
                            type=ArbitrageType.SPATIAL,
                            buy_venue=buy_venue,
                            sell_venue=sell_venue,
                            symbol=symbol,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            spread=spread,
                            spread_pct=spread_pct,
                            estimated_profit=spread * buy_data.get('volume', 1),
                            risk_factors=self._assess_risks(buy_venue, sell_venue),
                            time_to_execute_ms=buy_venue_info.get('latency_ms', 50) + 
                                              sell_venue_info.get('latency_ms', 50),
                            timestamp=datetime.now()
                        )
                        opportunities.append(opp)
        
        return sorted(opportunities, key=lambda x: x.spread_pct, reverse=True)
    
    async def scan_triangular_arbitrage(self,
                                       currencies: List[str] = None) -> List[ArbitrageOpportunity]:
        """Scan for triangular arbitrage in FX rates."""
        if currencies is None:
            currencies = ['USD', 'EUR', 'GBP', 'JPY']
        
        opportunities = []
        
        # Check all possible triangles
        for i, base in enumerate(currencies):
            for j, quote1 in enumerate(currencies):
                if i == j:
                    continue
                for k, quote2 in enumerate(currencies):
                    if i == k or j == k:
                        continue
                    
                    # Triangle: base -> quote1 -> quote2 -> base
                    pair1 = f"{base}/{quote1}"
                    pair2 = f"{quote1}/{quote2}"
                    pair3 = f"{quote2}/{base}"
                    
                    rate1 = self.fx_rates.get(pair1, 0)
                    rate2 = self.fx_rates.get(pair2, 0)
                    rate3 = self.fx_rates.get(pair3, 0)
                    
                    if rate1 > 0 and rate2 > 0 and rate3 > 0:
                        # Calculate implied cross rate
                        implied = rate1 * rate2 * rate3
                        
                        if implied > 1.001:  # 10 bps profit
                            opp = ArbitrageOpportunity(
                                opportunity_id=f"tri_{datetime.now().strftime('%H%M%S%f')}",
                                type=ArbitrageType.TRIANGULAR,
                                buy_venue="FX_MARKET",
                                sell_venue="FX_MARKET",
                                symbol=f"{base}->{quote1}->{quote2}->{base}",
                                buy_price=1.0,
                                sell_price=implied,
                                spread=implied - 1.0,
                                spread_pct=(implied - 1.0) * 10000,
                                estimated_profit=(implied - 1.0) * 100000,  # Assume 100k trade
                                risk_factors=['execution_risk', 'slippage'],
                                time_to_execute_ms=200,
                                timestamp=datetime.now()
                            )
                            opportunities.append(opp)
        
        return opportunities
    
    def _assess_risks(self, buy_venue: str, sell_venue: str) -> List[str]:
        """Assess risk factors for arbitrage."""
        risks = []
        
        buy_info = self.venues.get(buy_venue, {})
        sell_info = self.venues.get(sell_venue, {})
        
        if buy_info.get('latency_ms', 0) > 50 or sell_info.get('latency_ms', 0) > 50:
            risks.append('latency_risk')
        
        if buy_info.get('currency') != sell_info.get('currency'):
            risks.append('currency_risk')
        
        if buy_venue != sell_venue:
            risks.append('settlement_risk')
        
        return risks
    
    async def execute_arbitrage(self,
                               opportunity_id: str,
                               size: float) -> Dict[str, Any]:
        """Execute arbitrage trade (simulated)."""
        # In production: execute real trades on both venues
        
        return {
            'opportunity_id': opportunity_id,
            'executed': True,
            'size': size,
            'timestamp': datetime.now().isoformat(),
            'status': 'filled'
        }
    
    async def get_arbitrage_history(self,
                                   start_date: str,
                                   end_date: str) -> List[Dict]:
        """Get historical arbitrage trades."""
        return self.trade_history

cross_border_arb = CrossBorderArbitrage()
