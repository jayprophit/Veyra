"""IPO Pipeline Tracker - Track upcoming and recent IPOs"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class IPOStatus(Enum):
    FILING = "filing"
    PRICING = "pricing"
    OPEN = "open"
    LOCKUP = "lockup_period"
    POST_LOCKUP = "post_lockup"

@dataclass
class IPO:
    symbol: str
    company_name: str
    sector: str
    offer_price: float
    offer_shares: int
    market_cap: float
    exchange: str
    pricing_date: datetime
    first_trade_date: datetime
    status: IPOStatus
    lockup_date: datetime
    lead_underwriters: List[str]
    greenshoe_option: bool
    price_range_low: float
    price_range_high: float

class IPOPipelineTracker:
    """Track and analyze IPO pipeline"""
    
    def __init__(self):
        self.upcoming_ipos: List[IPO] = []
        self.recent_ipos: List[IPO] = []
        self.ipo_history: Dict[str, List[Dict]] = {}
    
    def add_ipo(self, ipo: IPO):
        """Add IPO to pipeline"""
        now = datetime.utcnow()
        
        if ipo.first_trade_date > now:
            self.upcoming_ipos.append(ipo)
        else:
            self.recent_ipos.append(ipo)
    
    def get_pricing_analysis(self, ipo: IPO) -> Dict:
        """Analyze IPO pricing"""
        # Check if priced above/below/within range
        if ipo.offer_price < ipo.price_range_low:
            pricing_status = "BELOW_RANGE"
            pricing_score = -20
        elif ipo.offer_price > ipo.price_range_high:
            pricing_status = "ABOVE_RANGE"
            pricing_score = 20
        else:
            # Within range - how close to top?
            range_pct = (ipo.offer_price - ipo.price_range_low) / (ipo.price_range_high - ipo.price_range_low)
            if range_pct > 0.8:
                pricing_status = "TOP_OF_RANGE"
                pricing_score = 15
            elif range_pct > 0.5:
                pricing_status = "MID_UPPER_RANGE"
                pricing_score = 5
            else:
                pricing_status = "LOWER_RANGE"
                pricing_score = -5
        
        return {
            "symbol": ipo.symbol,
            "company": ipo.company_name,
            "offer_price": ipo.offer_price,
            "price_range": f"${ipo.price_range_low:.2f}-${ipo.price_range_high:.2f}",
            "pricing_status": pricing_status,
            "pricing_score": pricing_score,
            "interpretation": self._interpret_pricing(pricing_status),
            "valuation_aggressiveness": "HIGH" if pricing_status in ["ABOVE_RANGE", "TOP_OF_RANGE"] else "MODERATE" if pricing_status == "MID_UPPER_RANGE" else "CONSERVATIVE"
        }
    
    def _interpret_pricing(self, status: str) -> str:
        """Interpret what pricing means for demand"""
        interpretations = {
            "BELOW_RANGE": "Weak demand - reduced price to get deal done",
            "LOWER_RANGE": "Cautious demand - conservative pricing",
            "MID_UPPER_RANGE": "Good demand - solid pricing",
            "TOP_OF_RANGE": "Strong demand - priced aggressively",
            "ABOVE_RANGE": "Very strong demand - exceeded expectations"
        }
        return interpretations.get(status, "Unknown")
    
    def analyze_underwriter_quality(self, ipo: IPO) -> Dict:
        """Analyze underwriter reputation and track record"""
        tier1_underwriters = ["Goldman Sachs", "Morgan Stanley", "JP Morgan", 
                           "Bank of America", "Citigroup", "Credit Suisse"]
        
        lead_quality_score = 0
        for underwriter in ipo.lead_underwriters:
            if any(tier in underwriter for tier in tier1_underwriters):
                lead_quality_score += 10
        
        # Greenshoe option adds stability
        stability_bonus = 5 if ipo.greenshoe_option else 0
        
        total_score = lead_quality_score + stability_bonus
        
        return {
            "underwriters": ipo.lead_underwriters,
            "tier1_count": lead_quality_score // 10,
            "quality_score": total_score,
            "has_greenshoe": ipo.greenshoe_option,
            "underwriter_tier": "PREMIER" if total_score >= 20 else "ESTABLISHED" if total_score >= 10 else "BOUTIQUE",
            "reliability_indicator": "HIGH" if total_score >= 15 else "MODERATE"
        }
    
    def score_ipo_opportunity(self, ipo: IPO) -> Dict:
        """Score IPO as investment opportunity"""
        pricing = self.get_pricing_analysis(ipo)
        underwriters = self.analyze_underwriter_quality(ipo)
        
        # Start with base score
        score = 50
        
        # Add pricing score
        score += pricing["pricing_score"]
        
        # Add underwriter quality
        score += underwriters["quality_score"]
        
        # Market cap factor (prefer mid-cap for growth)
        if 1e9 <= ipo.market_cap <= 10e9:
            score += 10  # Sweet spot
        elif ipo.market_cap > 50e9:
            score -= 5  # Mega-cap may have less upside
        elif ipo.market_cap < 500e6:
            score -= 10  # Too small, risky
        
        # Sector momentum (simplified)
        hot_sectors = ["technology", "healthcare", "fintech"]
        if ipo.sector.lower() in hot_sectors:
            score += 5
        
        final_score = max(0, min(100, score))
        
        return {
            "symbol": ipo.symbol,
            "company": ipo.company_name,
            "total_score": final_score,
            "rating": "STRONG_BUY" if final_score >= 80 else "BUY" if final_score >= 65 else "NEUTRAL" if final_score >= 50 else "AVOID",
            "score_breakdown": {
                "pricing": pricing["pricing_score"],
                "underwriter_quality": underwriters["quality_score"],
                "market_cap_fit": 10 if 1e9 <= ipo.market_cap <= 10e9 else -5 if ipo.market_cap > 50e9 else -10,
                "sector_momentum": 5 if ipo.sector.lower() in hot_sectors else 0
            },
            "key_details": {
                "pricing_analysis": pricing,
                "underwriter_analysis": underwriters,
                "market_cap_billions": round(ipo.market_cap / 1e9, 2)
            }
        }
    
    def get_pipeline_summary(self) -> Dict:
        """Get summary of IPO pipeline"""
        upcoming_count = len(self.upcoming_ipos)
        recent_count = len(self.recent_ipos)
        
        # Sector breakdown
        sectors = {}
        for ipo in self.upcoming_ipos + self.recent_ipos:
            sectors[ipo.sector] = sectors.get(ipo.sector, 0) + 1
        
        # Score all upcoming IPOs
        scored = []
        for ipo in self.upcoming_ipos:
            scored.append(self.score_ipo_opportunity(ipo))
        
        # Sort by score
        scored.sort(key=lambda x: x["total_score"], reverse=True)
        
        return {
            "upcoming_ipos": upcoming_count,
            "recently_priced": recent_count,
            "sector_breakdown": sectors,
            "top_opportunities": scored[:5],
            "avoid_list": [s for s in scored if s["rating"] == "AVOID"],
            "market_temperature": "HOT" if upcoming_count > 20 else "WARM" if upcoming_count > 10 else "COOL",
            "recommendation": "ACTIVE_PARTICIPATION" if scored and scored[0]["total_score"] > 75 else "SELECTIVE"
        }
    
    def track_lockup_expiration(self, days_ahead: int = 30) -> List[Dict]:
        """Track upcoming lockup expirations"""
        cutoff = datetime.utcnow().timestamp() + (days_ahead * 86400)
        
        expiring_lockups = []
        for ipo in self.recent_ipos:
            if ipo.lockup_date.timestamp() < cutoff:
                days_until = (ipo.lockup_date - datetime.utcnow()).days
                
                expiring_lockups.append({
                    "symbol": ipo.symbol,
                    "company": ipo.company_name,
                    "lockup_expiration": ipo.lockup_date.strftime("%Y-%m-%d"),
                    "days_until": days_until,
                    "potential_supply": ipo.offer_shares * 0.8,  # Assume 80% in lockup
                    "strategy": "WATCH_FOR_SELLING_PRESSURE" if days_until < 7 else "MONITOR"
                })
        
        return sorted(expiring_lockups, key=lambda x: x["days_until"])
