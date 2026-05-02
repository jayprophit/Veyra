"""
DeFi (Decentralized Finance) Tracker
====================================
Track DeFi protocols, yields, TVL, and opportunities
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DeFiProtocol:
    """DeFi protocol information"""
    name: str
    chain: str
    tvl: float  # Total Value Locked in USD
    category: str  # lending, dex, yield, derivatives
    apy: Dict[str, float]  # APY by asset
    risk_score: int  # 1-10
    audits: int


class DeFiTracker:
    """
    Track DeFi protocols and yield opportunities
    
    Categories:
    - Lending/Borrowing (Aave, Compound)
    - DEXs (Uniswap, Curve, Sushi)
    - Yield Aggregators (Yearn, Convex)
    - Derivatives (dYdX, GMX)
    - Liquid Staking (Lido, Rocket Pool)
    """
    
    PROTOCOLS = [
        # Lending
        DeFiProtocol('Aave', 'Ethereum', 8500000000, 'lending', 
                    {'USDC': 4.5, 'DAI': 4.2, 'ETH': 2.1}, 3, 5),
        DeFiProtocol('Compound', 'Ethereum', 3200000000, 'lending',
                    {'USDC': 4.1, 'DAI': 3.9, 'ETH': 1.8}, 3, 4),
        DeFiProtocol('Aave V3', 'Polygon', 1200000000, 'lending',
                    {'USDC': 5.2, 'MATIC': 3.5}, 4, 3),
        
        # DEXs
        DeFiProtocol('Uniswap V3', 'Ethereum', 4200000000, 'dex',
                    {'ETH-USDC': 15.5, 'WBTC-ETH': 8.2}, 4, 4),
        DeFiProtocol('Curve', 'Ethereum', 5800000000, 'dex',
                    {'3pool': 3.8, 'stETH': 4.5}, 2, 6),
        DeFiProtocol('GMX', 'Arbitrum', 850000000, 'dex',
                    {'GLP': 18.5}, 5, 3),
        
        # Yield Aggregators
        DeFiProtocol('Yearn Finance', 'Ethereum', 800000000, 'yield',
                    {'USDC': 6.2, 'DAI': 5.8, 'ETH': 3.5}, 5, 4),
        DeFiProtocol('Convex Finance', 'Ethereum', 4200000000, 'yield',
                    {'cvxCRV': 25.5, '3pool': 8.2}, 4, 3),
        
        # Liquid Staking
        DeFiProtocol('Lido', 'Ethereum', 21000000000, 'staking',
                    {'stETH': 4.2}, 2, 5),
        DeFiProtocol('Rocket Pool', 'Ethereum', 1800000000, 'staking',
                    {'rETH': 4.3}, 3, 4),
        
        # Derivatives
        DeFiProtocol('dYdX', 'Ethereum', 450000000, 'derivatives',
                    {}, 5, 4),
        DeFiProtocol('GMX Perps', 'Arbitrum', 750000000, 'derivatives',
                    {}, 6, 2),
    ]
    
    def __init__(self):
        self.yield_cache = {}
        self.last_update = None
    
    def get_top_yields(self, min_tvl: float = 100000000, 
                      max_risk: int = 5) -> List[Dict]:
        """Get top yield opportunities"""
        opportunities = []
        
        for protocol in self.PROTOCOLS:
            if protocol.tvl < min_tvl or protocol.risk_score > max_risk:
                continue
            
            for asset, apy in protocol.apy.items():
                opportunities.append({
                    'protocol': protocol.name,
                    'chain': protocol.chain,
                    'asset': asset,
                    'apy': apy,
                    'tvl': protocol.tvl,
                    'risk_score': protocol.risk_score,
                    'category': protocol.category,
                    'risk_adjusted_yield': apy / protocol.risk_score
                })
        
        # Sort by risk-adjusted yield
        opportunities.sort(key=lambda x: x['risk_adjusted_yield'], reverse=True)
        
        return opportunities[:20]
    
    def get_yield_by_category(self) -> Dict[str, List[Dict]]:
        """Group yields by category"""
        by_category = {
            'lending': [],
            'dex': [],
            'yield': [],
            'staking': [],
            'derivatives': []
        }
        
        for protocol in self.PROTOCOLS:
            for asset, apy in protocol.apy.items():
                by_category[protocol.category].append({
                    'protocol': protocol.name,
                    'asset': asset,
                    'apy': apy,
                    'tvl': protocol.tvl
                })
        
        # Sort each category by APY
        for category in by_category:
            by_category[category].sort(key=lambda x: x['apy'], reverse=True)
        
        return by_category
    
    def calculate_impermanent_loss(self, price_change_pct: float) -> float:
        """Calculate impermanent loss for AMM LPs"""
        # IL = 2*sqrt(r) / (1+r) - 1
        # where r = price ratio
        r = 1 + price_change_pct / 100
        il = (2 * (r ** 0.5) / (1 + r)) - 1
        return il * 100  # As percentage
    
    def get_il_risk_assessment(self, pool: str, 
                               volatility_30d: float) -> Dict:
        """Assess impermanent loss risk"""
        # Simulate price changes
        price_changes = [-30, -20, -10, -5, 0, 5, 10, 20, 30]
        
        il_scenarios = []
        for change in price_changes:
            il = self.calculate_impermanent_loss(change)
            il_scenarios.append({
                'price_change': change,
                'impermanent_loss': round(il, 2)
            })
        
        # Risk rating
        if volatility_30d > 100:
            risk = 'EXTREME'
        elif volatility_30d > 70:
            risk = 'HIGH'
        elif volatility_30d > 40:
            risk = 'MEDIUM'
        else:
            risk = 'LOW'
        
        return {
            'pool': pool,
            'volatility_30d': volatility_30d,
            'il_risk': risk,
            'il_scenarios': il_scenarios,
            'recommendation': 'HOLD' if risk == 'LOW' else 'CAUTION' if risk == 'MEDIUM' else 'AVOID'
        }
    
    def find_arbitrage_opportunities(self) -> List[Dict]:
        """Find stablecoin yield arbitrage"""
        stable_yields = []
        
        for protocol in self.PROTOCOLS:
            for asset, apy in protocol.apy.items():
                if asset in ['USDC', 'DAI', 'USDT']:
                    stable_yields.append({
                        'protocol': protocol.name,
                        'chain': protocol.chain,
                        'asset': asset,
                        'apy': apy,
                        'tvl': protocol.tvl
                    })
        
        # Find highest and lowest
        if len(stable_yields) < 2:
            return []
        
        stable_yields.sort(key=lambda x: x['apy'], reverse=True)
        
        highest = stable_yields[0]
        lowest = stable_yields[-1]
        
        spread = highest['apy'] - lowest['apy']
        
        if spread > 2:  # 2% spread
            return [{
                'strategy': 'Yield Arbitrage',
                'action': f"Borrow from {lowest['protocol']} at {lowest['apy']:.2f}%, "
                         f"deposit to {highest['protocol']} at {highest['apy']:.2f}%",
                'spread': round(spread, 2),
                'expected_profit': f"~{spread:.2f}% APY",
                'risks': ['Smart contract risk', 'Bridge risk if cross-chain']
            }]
        
        return []
    
    def get_tvl_leaders(self, top_n: int = 10) -> List[Dict]:
        """Get protocols with highest TVL"""
        sorted_protocols = sorted(
            self.PROTOCOLS,
            key=lambda x: x.tvl,
            reverse=True
        )
        
        return [
            {
                'rank': i + 1,
                'protocol': p.name,
                'chain': p.chain,
                'tvl_billions': round(p.tvl / 1e9, 2),
                'category': p.category,
                'risk_score': p.risk_score
            }
            for i, p in enumerate(sorted_protocols[:top_n])
        ]
    
    def get_defi_summary(self) -> Dict:
        """Get comprehensive DeFi summary"""
        total_tvl = sum(p.tvl for p in self.PROTOCOLS)
        
        category_tvls = {}
        for p in self.PROTOCOLS:
            if p.category not in category_tvls:
                category_tvls[p.category] = 0
            category_tvls[p.category] += p.tvl
        
        return {
            'total_tvl_billions': round(total_tvl / 1e9, 2),
            'protocols_tracked': len(self.PROTOCOLS),
            'category_breakdown': {
                cat: round(tvl / 1e9, 2)
                for cat, tvl in category_tvls.items()
            },
            'tvl_leaders': self.get_tvl_leaders(5),
            'top_yields': self.get_top_yields()[:5],
            'arbitrage_opportunities': self.find_arbitrage_opportunities(),
            'timestamp': datetime.now().isoformat()
        }


# Usage
def get_defi_yields() -> Dict:
    """Quick DeFi yields summary"""
    tracker = DeFiTracker()
    
    return {
        'top_yields': tracker.get_top_yields(10),
        'by_category': tracker.get_yield_by_category(),
        'tvl_leaders': tracker.get_tvl_leaders(5)
    }


def assess_lp_risk(pool: str, volatility: float) -> Dict:
    """Assess impermanent loss risk for LP position"""
    tracker = DeFiTracker()
    return tracker.get_il_risk_assessment(pool, volatility)
