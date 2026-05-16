"""IPO Pipeline Tracker."""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class IPOStatus(Enum):
    FILING = "filing"
    ROADSHOW = "roadshow"
    PRICING = "pricing"
    TRADING = "trading"
    POST_LOCKUP = "post_lockup"

@dataclass
class IPODetails:
    symbol: str
    company_name: str
    exchange: str
    offer_price: float
    share_count: int
    valuation: float
    status: IPOStatus
    debut_date: Optional[datetime]

class IPOPipelineTracker:
    """Track upcoming and recent IPOs."""
    
    def __init__(self):
        self.upcoming_ipos: Dict[str, IPODetails] = {}
        self.recent_ipos: Dict[str, IPODetails] = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with sample IPO data."""
        sample_ipos = [
            IPODetails("STTECH", "StarTech AI", "NASDAQ", 25.0, 10000000, 2500000000, IPOStatus.ROADSHOW, None),
            IPODetails("CLDY", "CloudDynamics", "NYSE", 18.5, 15000000, 2775000000, IPOStatus.FILING, None),
            IPODetails("BIONX", "BioNexus Health", "NASDAQ", 32.0, 8000000, 2560000000, IPOStatus.PRICING, None),
            IPODetails("CYBSAFE", "CyberSafe Inc", "NYSE", 28.0, 12000000, 3360000000, IPOStatus.TRADING, datetime.now()),
        ]
        for ipo in sample_ipos:
            if ipo.status == IPOStatus.TRADING:
                self.recent_ipos[ipo.symbol] = ipo
            else:
                self.upcoming_ipos[ipo.symbol] = ipo
    
    async def get_upcoming_ipos(self, min_valuation: Optional[float] = None) -> List[Dict]:
        """Get list of upcoming IPOs."""
        results = []
        for ipo in self.upcoming_ipos.values():
            if min_valuation and ipo.valuation < min_valuation:
                continue
            results.append({
                'symbol': ipo.symbol,
                'company': ipo.company_name,
                'exchange': ipo.exchange,
                'expected_price': ipo.offer_price,
                'shares': ipo.share_count,
                'valuation': ipo.valuation,
                'status': ipo.status.value
            })
        return sorted(results, key=lambda x: x['valuation'], reverse=True)
    
    async def get_ipo_details(self, symbol: str) -> Dict[str, Any]:
        """Get detailed information about specific IPO."""
        ipo = self.upcoming_ipos.get(symbol) or self.recent_ipos.get(symbol)
        if not ipo:
            return {'error': 'IPO not found'}
        
        return {
            'symbol': ipo.symbol,
            'company_name': ipo.company_name,
            'exchange': ipo.exchange,
            'offer_price': ipo.offer_price,
            'share_count': ipo.share_count,
            'valuation': ipo.valuation,
            'status': ipo.status.value,
            'debut_date': ipo.debut_date.isoformat() if ipo.debut_date else None,
            'price_range': [ipo.offer_price * 0.85, ipo.offer_price * 1.15]
        }
    
    async def request_allocation(self, user_id: str, symbol: str, shares_requested: int) -> Dict[str, Any]:
        """Request IPO share allocation."""
        ipo = self.upcoming_ipos.get(symbol)
        if not ipo:
            return {'error': 'IPO not available for allocation'}
        
        if ipo.status not in [IPOStatus.FILING, IPOStatus.ROADSHOW, IPOStatus.PRICING]:
            return {'error': 'IPO allocation window closed'}
        
        allocation = min(shares_requested, max(100, shares_requested // 10))  # 10% or min 100
        
        return {
            'request_id': f"req_{user_id}_{symbol}_{int(datetime.now().timestamp())}",
            'symbol': symbol,
            'shares_requested': shares_requested,
            'estimated_allocation': allocation,
            'estimated_value': allocation * ipo.offer_price,
            'status': 'submitted'
        }
    
    async def track_performance(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """Track post-IPO performance."""
        ipo = self.recent_ipos.get(symbol)
        if not ipo:
            return {'error': 'Recent IPO not found'}
        
        # Simulate performance data
        return {
            'symbol': symbol,
            'ipo_price': ipo.offer_price,
            'current_price': ipo.offer_price * 1.25,  # Simulated 25% gain
            'day_1_return': 18.5,
            'week_1_return': 32.0,
            'month_1_return': 25.0,
            'vs_sp500': 15.2,
            'lockup_expiry': (ipo.debut_date + datetime.timedelta(days=180)).isoformat() if ipo.debut_date else None
        }

ipo_tracker = IPOPipelineTracker()
