"""
Precious Metals & Industrial Metals Tracker
Comprehensive tracking for gold, silver, copper, palladium, platinum, lithium, etc.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class MetalType(Enum):
    GOLD = "gold"
    SILVER = "silver"
    COPPER = "copper"
    PALLADIUM = "palladium"
    PLATINUM = "platinum"
    LITHIUM = "lithium"
    COBALT = "cobalt"
    NICKEL = "nickel"
    ALUMINUM = "aluminum"
    ZINC = "zinc"


@dataclass
class MetalPrice:
    metal_type: MetalType
    spot_price: float
    currency: str
    timestamp: datetime
    bid: float
    ask: float
    change_24h: float
    change_pct_24h: float
    source: str


@dataclass
class PhysicalHolding:
    metal_type: MetalType
    ounces: float
    purchase_price: float
    purchase_date: datetime
    storage_location: str
    dealer: str
    premiums_paid: float


class MetalsTracker:
    """
    Comprehensive precious and industrial metals tracking
    
    Features:
    - Real-time spot prices from multiple sources
    - Physical holdings tracking
    - Premium calculations
    - Gold/silver ratio analysis
    - Portfolio valuation
    - Price alerts
    """
    
    # API endpoints for metal prices
    PRICE_SOURCES = {
        'goldapi': 'https://www.goldapi.io/api/{metal}/USD',
        'metals_api': 'https://metals-api.com/api/latest',
        'kitco': 'https://www.kitco.com/gold.londonfix.json',
    }
    
    # Ticker symbols for correlation with mining stocks
    MINING_ETFS = {
        MetalType.GOLD: ['GLD', 'IAU', 'GDX', 'GDXJ'],
        MetalType.SILVER: ['SLV', 'SIL', 'SILJ'],
        MetalType.COPPER: ['COPX', 'JJC'],
        MetalType.LITHIUM: ['LIT', 'BATT'],
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or 'goldapi-demo-key'  # Free tier
        self.prices: Dict[MetalType, MetalPrice] = {}
        self.holdings: List[PhysicalHolding] = []
        self.price_history: Dict[MetalType, List[MetalPrice]] = {}
        self.alerts: List[Dict] = []
    
    async def fetch_live_prices(self) -> Dict[MetalType, MetalPrice]:
        """Fetch real-time metal prices from APIs"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for metal in MetalType:
                tasks.append(self._fetch_metal_price(session, metal))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for metal, result in zip(MetalType, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to fetch {metal.value}: {result}")
                elif result:
                    self.prices[metal] = result
                    self._add_to_history(metal, result)
        
        return self.prices
    
    async def _fetch_metal_price(self, session: aiohttp.ClientSession, 
                                  metal: MetalType) -> Optional[MetalPrice]:
        """Fetch price for specific metal"""
        try:
            # Try GoldAPI first (free tier available)
            metal_code = self._get_metal_code(metal)
            url = self.PRICE_SOURCES['goldapi'].format(metal=metal_code)
            
            headers = {
                'x-access-token': self.api_key,
                'Content-Type': 'application/json'
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return MetalPrice(
                        metal_type=metal,
                        spot_price=data.get('price', 0),
                        currency='USD',
                        timestamp=datetime.now(),
                        bid=data.get('bid', data.get('price', 0)),
                        ask=data.get('ask', data.get('price', 0)),
                        change_24h=data.get('ch', 0),
                        change_pct_24h=data.get('chp', 0),
                        source='goldapi'
                    )
                else:
                    # Fallback to simulated data for demo
                    return self._get_fallback_price(metal)
        except Exception as e:
            logger.warning(f"Price fetch error for {metal.value}: {e}")
            return self._get_fallback_price(metal)
    
    def _get_fallback_price(self, metal: MetalType) -> MetalPrice:
        """Get fallback/demo prices when API fails"""
        # Approximate spot prices (will be updated by real API)
        fallback_prices = {
            MetalType.GOLD: 2300.00,
            MetalType.SILVER: 27.00,
            MetalType.COPPER: 4.50,
            MetalType.PALLADIUM: 1000.00,
            MetalType.PLATINUM: 950.00,
            MetalType.LITHIUM: 12000.00,  # Per metric ton
            MetalType.COBALT: 28000.00,
            MetalType.NICKEL: 17500.00,
            MetalType.ALUMINUM: 2200.00,
            MetalType.ZINC: 2500.00,
        }
        
        price = fallback_prices.get(metal, 100.0)
        
        return MetalPrice(
            metal_type=metal,
            spot_price=price,
            currency='USD',
            timestamp=datetime.now(),
            bid=price * 0.995,
            ask=price * 1.005,
            change_24h=0,
            change_pct_24h=0,
            source='fallback'
        )
    
    def _get_metal_code(self, metal: MetalType) -> str:
        """Get API metal code"""
        codes = {
            MetalType.GOLD: 'XAU',
            MetalType.SILVER: 'XAG',
            MetalType.COPPER: 'XCU',
            MetalType.PALLADIUM: 'XPD',
            MetalType.PLATINUM: 'XPT',
            MetalType.LITHIUM: 'XLIT',
            MetalType.COBALT: 'XCOB',
            MetalType.NICKEL: 'XNI',
            MetalType.ALUMINUM: 'XAL',
            MetalType.ZINC: 'XZI',
        }
        return codes.get(metal, metal.value.upper())
    
    def _add_to_history(self, metal: MetalType, price: MetalPrice):
        """Add price to historical record"""
        if metal not in self.price_history:
            self.price_history[metal] = []
        
        self.price_history[metal].append(price)
        
        # Keep only last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        self.price_history[metal] = [
            p for p in self.price_history[metal]
            if p.timestamp > cutoff
        ]
    
    def add_physical_holding(self, holding: PhysicalHolding):
        """Add a physical metal holding"""
        self.holdings.append(holding)
        logger.info(f"Added {holding.ounces}oz {holding.metal_type.value} holding")
    
    def calculate_portfolio_value(self) -> Dict:
        """Calculate total portfolio value with current prices"""
        if not self.prices:
            return {'error': 'No prices available. Call fetch_live_prices() first.'}
        
        total_value = 0.0
        total_cost = 0.0
        breakdown = {}
        
        for holding in self.holdings:
            metal = holding.metal_type
            current_price = self.prices.get(metal)
            
            if current_price:
                current_value = holding.ounces * current_price.spot_price
                cost_basis = holding.ounces * holding.purchase_price
                
                if metal not in breakdown:
                    breakdown[metal] = {
                        'ounces': 0,
                        'current_value': 0,
                        'cost_basis': 0,
                        'unrealized_pnl': 0
                    }
                
                breakdown[metal]['ounces'] += holding.ounces
                breakdown[metal]['current_value'] += current_value
                breakdown[metal]['cost_basis'] += cost_basis
                breakdown[metal]['unrealized_pnl'] += (current_value - cost_basis)
                
                total_value += current_value
                total_cost += cost_basis
        
        return {
            'total_value_usd': round(total_value, 2),
            'total_cost_basis': round(total_cost, 2),
            'unrealized_pnl': round(total_value - total_cost, 2),
            'pnl_percentage': round((total_value - total_cost) / total_cost * 100, 2) if total_cost > 0 else 0,
            'metal_breakdown': {
                k.value: {
                    'ounces': round(v['ounces'], 3),
                    'current_value': round(v['current_value'], 2),
                    'cost_basis': round(v['cost_basis'], 2),
                    'unrealized_pnl': round(v['unrealized_pnl'], 2)
                }
                for k, v in breakdown.items()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_gold_silver_ratio(self) -> Dict:
        """Calculate and analyze gold/silver ratio"""
        gold = self.prices.get(MetalType.GOLD)
        silver = self.prices.get(MetalType.SILVER)
        
        if not gold or not silver:
            return {'error': 'Gold or silver price not available'}
        
        ratio = gold.spot_price / silver.spot_price if silver.spot_price > 0 else 0
        historical_mean = 65.0
        
        deviation = ratio - historical_mean
        deviation_pct = (deviation / historical_mean) * 100
        
        # Trading signal based on ratio
        if ratio > 80:
            signal = 'BUY_SILVER'
            strength = 'strong'
        elif ratio > 70:
            signal = 'BUY_SILVER'
            strength = 'moderate'
        elif ratio < 40:
            signal = 'BUY_GOLD'
            strength = 'strong'
        elif ratio < 50:
            signal = 'BUY_GOLD'
            strength = 'moderate'
        else:
            signal = 'NEUTRAL'
            strength = 'none'
        
        return {
            'ratio': round(ratio, 2),
            'gold_price': gold.spot_price,
            'silver_price': silver.spot_price,
            'historical_mean': historical_mean,
            'deviation_from_mean': round(deviation, 2),
            'deviation_percentage': round(deviation_pct, 2),
            'signal': signal,
            'signal_strength': strength,
            'interpretation': self._interpret_ratio(ratio)
        }
    
    def _interpret_ratio(self, ratio: float) -> str:
        """Provide interpretation of gold/silver ratio"""
        if ratio > 80:
            return "Gold is expensive relative to silver. Consider silver."
        elif ratio > 70:
            return "Gold moderately expensive vs silver."
        elif ratio < 40:
            return "Silver is expensive relative to gold. Consider gold."
        elif ratio < 50:
            return "Silver moderately expensive vs gold."
        else:
            return "Ratio near historical average."
    
    def get_correlated_stocks(self, metal: MetalType) -> List[str]:
        """Get mining ETFs/stocks correlated with metal"""
        return self.MINING_ETFS.get(metal, [])
    
    def analyze_premium(self, metal: MetalType, dealer_price: float) -> Dict:
        """Analyze if dealer price represents good value"""
        current = self.prices.get(metal)
        if not current:
            return {'error': f'No price data for {metal.value}'}
        
        premium = dealer_price - current.spot_price
        premium_pct = (premium / current.spot_price) * 100
        
        # Typical premiums for physical metals
        typical_premiums = {
            MetalType.GOLD: 3.0,      # 3% for bullion
            MetalType.SILVER: 15.0,   # 15% for silver (higher due to fabrication)
            MetalType.PLATINUM: 5.0,
            MetalType.PALLADIUM: 4.0,
        }
        
        typical = typical_premiums.get(metal, 5.0)
        
        return {
            'metal': metal.value,
            'spot_price': current.spot_price,
            'dealer_price': dealer_price,
            'premium_amount': round(premium, 2),
            'premium_percentage': round(premium_pct, 2),
            'typical_premium': typical,
            'expensive': premium_pct > typical * 1.5,
            'good_value': premium_pct < typical * 0.8,
            'recommendation': 'BUY' if premium_pct < typical * 0.8 else 'WAIT' if premium_pct > typical * 1.5 else 'FAIR'
        }
    
    def set_price_alert(self, metal: MetalType, target_price: float, 
                       condition: str = 'above') -> Dict:
        """Set a price alert"""
        alert = {
            'id': len(self.alerts) + 1,
            'metal': metal.value,
            'target_price': target_price,
            'condition': condition,
            'created_at': datetime.now().isoformat(),
            'triggered': False
        }
        self.alerts.append(alert)
        return alert
    
    def check_alerts(self) -> List[Dict]:
        """Check if any price alerts should trigger"""
        triggered = []
        
        for alert in self.alerts:
            if alert['triggered']:
                continue
            
            metal = MetalType(alert['metal'])
            current = self.prices.get(metal)
            
            if not current:
                continue
            
            should_trigger = False
            if alert['condition'] == 'above' and current.spot_price > alert['target_price']:
                should_trigger = True
            elif alert['condition'] == 'below' and current.spot_price < alert['target_price']:
                should_trigger = True
            
            if should_trigger:
                alert['triggered'] = True
                alert['triggered_at'] = datetime.now().isoformat()
                alert['trigger_price'] = current.spot_price
                triggered.append(alert)
        
        return triggered
    
    def get_price_history_chart_data(self, metal: MetalType, 
                                      days: int = 30) -> List[Dict]:
        """Get price history formatted for charting"""
        history = self.price_history.get(metal, [])
        cutoff = datetime.now() - timedelta(days=days)
        
        recent = [p for p in history if p.timestamp > cutoff]
        
        return [
            {
                'timestamp': p.timestamp.isoformat(),
                'price': p.spot_price,
                'bid': p.bid,
                'ask': p.ask
            }
            for p in sorted(recent, key=lambda x: x.timestamp)
        ]
    
    def generate_report(self) -> Dict:
        """Generate comprehensive metals portfolio report"""
        portfolio = self.calculate_portfolio_value()
        ratio_analysis = self.calculate_gold_silver_ratio()
        
        # Get latest prices
        prices_dict = {
            m.value: {
                'spot': p.spot_price,
                'change_24h': p.change_pct_24h
            }
            for m, p in self.prices.items()
        }
        
        return {
            'portfolio': portfolio,
            'gold_silver_ratio': ratio_analysis,
            'current_prices': prices_dict,
            'holdings_count': len(self.holdings),
            'active_alerts': len([a for a in self.alerts if not a['triggered']]),
            'timestamp': datetime.now().isoformat()
        }


# Convenience functions
def get_live_metal_prices(api_key: Optional[str] = None) -> Dict[MetalType, MetalPrice]:
    """Quick function to get live metal prices"""
    tracker = MetalsTracker(api_key=api_key)
    asyncio.run(tracker.fetch_live_prices())
    return tracker.prices


def calculate_gold_silver_ratio(api_key: Optional[str] = None) -> Dict:
    """Quick calculation of gold/silver ratio"""
    tracker = MetalsTracker(api_key=api_key)
    asyncio.run(tracker.fetch_live_prices())
    return tracker.calculate_gold_silver_ratio()
