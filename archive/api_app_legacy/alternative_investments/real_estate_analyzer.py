"""Real Estate Analyzer - REITs, property analysis, market trends"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class REIT:
    symbol: str
    name: str
    property_type: str  # Residential, Commercial, Industrial, Healthcare, etc.
    nav_per_share: float
    current_price: float
    dividend_yield: float
    debt_to_assets: float
    portfolio_value: float
    occupancy_rate: float

class RealEstateAnalyzer:
    """Analyze REITs and real estate investments"""
    
    def __init__(self):
        self.reits: List[REIT] = []
        self.property_types = {
            "residential": {"avg_yield": 0.035, "risk": "medium"},
            "commercial": {"avg_yield": 0.045, "risk": "medium-high"},
            "industrial": {"avg_yield": 0.04, "risk": "medium"},
            "healthcare": {"avg_yield": 0.05, "risk": "low"},
            "data_center": {"avg_yield": 0.03, "risk": "low"},
            "retail": {"avg_yield": 0.06, "risk": "high"},
            "hotel": {"avg_yield": 0.055, "risk": "high"},
            "self_storage": {"avg_yield": 0.035, "risk": "low"}
        }
    
    def add_reit(self, reit: REIT):
        """Add REIT to tracker"""
        self.reits.append(reit)
    
    def calculate_premium_discount(self, reit: REIT) -> Dict:
        """Calculate NAV premium/discount"""
        nav = reit.nav_per_share
        price = reit.current_price
        
        premium = (price - nav) / nav
        
        return {
            "symbol": reit.symbol,
            "nav_per_share": nav,
            "current_price": price,
            "premium_discount_pct": round(premium * 100, 2),
            "valuation": "PREMIUM" if premium > 0.05 else "DISCOUNT" if premium < -0.05 else "FAIR",
            "opportunity": "SELL" if premium > 0.15 else "BUY" if premium < -0.10 else "HOLD"
        }
    
    def analyze_dividend_safety(self, reit: REIT) -> Dict:
        """Analyze dividend sustainability"""
        # FFO (Funds From Operations) estimation
        estimated_ffo = reit.portfolio_value * 0.06 * reit.occupancy_rate
        ffo_per_share = estimated_ffo / (reit.portfolio_value / reit.current_price)
        
        # FFO payout ratio
        annual_dividend = reit.current_price * reit.dividend_yield
        payout_ratio = annual_dividend / ffo_per_share if ffo_per_share > 0 else 1
        
        # Debt coverage
        debt_coverage = (1 - reit.debt_to_assets) * 2  # Simplified
        
        safety_score = 100
        if payout_ratio > 0.9:
            safety_score -= 30
        elif payout_ratio > 0.8:
            safety_score -= 15
        
        if reit.debt_to_assets > 0.5:
            safety_score -= 20
        
        return {
            "symbol": reit.symbol,
            "dividend_yield": round(reit.dividend_yield * 100, 2),
            "estimated_ffo_payout_ratio": round(payout_ratio * 100, 1),
            "debt_to_assets": round(reit.debt_to_assets * 100, 1),
            "occupancy_rate": round(reit.occupancy_rate * 100, 1),
            "safety_score": safety_score,
            "dividend_safety": "SAFE" if safety_score > 80 else "CAUTION" if safety_score > 60 else "AT_RISK",
            "recommendation": "QUALITY_INCOME" if safety_score > 80 else "MONITOR"
        }
    
    def screen_reits(self, min_yield: float = 0.03, max_debt: float = 0.6,
                    property_types: List[str] = None) -> List[Dict]:
        """Screen REITs based on criteria"""
        results = []
        
        for reit in self.reits:
            # Filter by yield
            if reit.dividend_yield < min_yield:
                continue
            
            # Filter by debt
            if reit.debt_to_assets > max_debt:
                continue
            
            # Filter by property type
            if property_types and reit.property_type.lower() not in property_types:
                continue
            
            valuation = self.calculate_premium_discount(reit)
            div_safety = self.analyze_dividend_safety(reit)
            
            results.append({
                "symbol": reit.symbol,
                "name": reit.name,
                "property_type": reit.property_type,
                "yield": round(reit.dividend_yield * 100, 2),
                "premium_discount": valuation["premium_discount_pct"],
                "dividend_safety": div_safety["dividend_safety"],
                "total_score": self._calculate_total_score(reit, valuation, div_safety)
            })
        
        return sorted(results, key=lambda x: x["total_score"], reverse=True)
    
    def _calculate_total_score(self, reit: REIT, valuation: Dict, 
                               div_safety: Dict) -> float:
        """Calculate composite quality score"""
        score = 0
        
        # Dividend safety (40%)
        score += div_safety["safety_score"] * 0.4
        
        # Valuation (30%) - prefer discounts
        discount = abs(min(0, valuation["premium_discount_pct"]))
        score += min(30, discount * 3)
        
        # Yield (20%)
        yield_score = min(20, reit.dividend_yield * 100 * 2)
        score += yield_score
        
        # Occupancy (10%)
        score += reit.occupancy_rate * 10
        
        return round(score, 1)
    
    def get_sector_allocation(self) -> Dict:
        """Analyze sector allocation of tracked REITs"""
        total_value = sum(r.portfolio_value for r in self.reits)
        
        by_sector = {}
        for reit in self.reits:
            sector = reit.property_type
            if sector not in by_sector:
                by_sector[sector] = {"value": 0, "count": 0, "avg_yield": 0}
            
            by_sector[sector]["value"] += reit.portfolio_value
            by_sector[sector]["count"] += 1
        
        # Calculate averages
        for sector in by_sector:
            sector_reits = [r for r in self.reits if r.property_type == sector]
            by_sector[sector]["avg_yield"] = round(
                sum(r.dividend_yield for r in sector_reits) / len(sector_reits) * 100, 2
            )
            by_sector[sector]["allocation_pct"] = round(
                by_sector[sector]["value"] / total_value * 100, 2
            ) if total_value > 0 else 0
        
        return {
            "sector_breakdown": by_sector,
            "total_reits": len(self.reits),
            "diversification_score": len(by_sector) / 8,  # 8 property types
            "recommended_focus": self._recommend_sectors(by_sector)
        }
    
    def _recommend_sectors(self, by_sector: Dict) -> List[str]:
        """Recommend sectors based on yield and risk"""
        recommendations = []
        
        for sector, data in by_sector.items():
            sector_info = self.property_types.get(sector.lower(), {"avg_yield": 0.04})
            
            if data["avg_yield"] > sector_info["avg_yield"] * 1.2:
                recommendations.append(f"{sector}: Above average yield")
        
        return recommendations if recommendations else ["Diversified exposure recommended"]
    
    def compare_to_rates(self, reit: REIT, treasury_10y: float = 0.045) -> Dict:
        """Compare REIT yield to treasury rates"""
        spread = reit.dividend_yield - treasury_10y
        
        return {
            "symbol": reit.symbol,
            "reit_yield": round(reit.dividend_yield * 100, 2),
            "treasury_10y": round(treasury_10y * 100, 2),
            "yield_spread": round(spread * 100, 2),
            "spread_sufficient": spread > 0.02,  # Want at least 200bps spread
            "rate_sensitivity": "HIGH" if reit.debt_to_assets > 0.5 else "MODERATE"
        }
