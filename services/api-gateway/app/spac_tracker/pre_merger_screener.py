"""Pre-Merger Screener - Analyze SPACs before merger completion"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SPAC:
    ticker: str
    target_company: str
    trust_value: float  # NAV typically $10
    current_price: float
    redemption_deadline: datetime
    merger_vote_date: datetime
    estimated_completion_date: datetime
    institutional_ownership: float
    short_interest: float
    redemption_rate_estimate: float
    target_valuation: float
    premium_to_nav: float
    sector: str
    pipe_size: float
    pipe_price: float

class PreMergerScreener:
    """Screen and analyze pre-merger SPAC opportunities"""
    
    def __init__(self):
        self.spacs: List[SPAC] = []
        self.nav_price = 10.0  # Standard SPAC NAV
    
    def add_spac(self, spac: SPAC):
        """Add SPAC to tracker"""
        self.spacs.append(spac)
    
    def calculate_arbitrage_spread(self, spac: SPAC) -> Dict:
        """Calculate merger arbitrage spread"""
        nav = self.nav_price
        price = spac.current_price
        
        # If price below NAV, there's redemption value
        redemption_value = max(0, nav - price)
        redemption_yield = (redemption_value / price) * 100 if price > 0 else 0
        
        # Days until redemption deadline
        days_until = (spac.redemption_deadline - datetime.utcnow()).days
        
        # Annualized yield
        annualized_yield = 0
        if days_until > 0 and redemption_yield > 0:
            annualized_yield = redemption_yield * (365 / days_until)
        
        return {
            "ticker": spac.ticker,
            "current_price": price,
            "nav": nav,
            "discount_to_nav": round((nav - price) / nav * 100, 2),
            "redemption_value": round(redemption_value, 2),
            "redemption_yield": round(redemption_yield, 2),
            "days_until_deadline": days_until,
            "annualized_yield": round(annualized_yield, 2),
            "arbitrage_opportunity": price < nav * 0.98  # 2% discount threshold
        }
    
    def assess_merger_probability(self, spac: SPAC) -> Dict:
        """Assess probability of successful merger completion"""
        score = 50  # Base probability
        factors = []
        
        # Institutional ownership (higher = more confidence)
        if spac.institutional_ownership > 0.7:
            score += 15
            factors.append("High institutional ownership")
        elif spac.institutional_ownership > 0.5:
            score += 5
        elif spac.institutional_ownership < 0.3:
            score -= 10
            factors.append("Low institutional interest")
        
        # Short interest (high = skepticism)
        if spac.short_interest > 0.15:
            score -= 15
            factors.append("High short interest - market skepticism")
        elif spac.short_interest < 0.05:
            score += 5
        
        # Premium to NAV (moderate premium = confidence)
        if 0 < spac.premium_to_nav < 0.10:
            score += 10
            factors.append("Reasonable premium reflects confidence")
        elif spac.premium_to_nav > 0.20:
            score -= 10
            factors.append("Excessive premium - overvalued risk")
        
        # PIPE size (larger = more institutional support)
        if spac.pipe_size > 500e6:
            score += 15
            factors.append("Large PIPE demonstrates institutional support")
        elif spac.pipe_size > 100e6:
            score += 5
        
        # Sector (some sectors more reliable)
        reliable_sectors = ["technology", "healthcare", "fintech"]
        if spac.sector.lower() in reliable_sectors:
            score += 5
        
        final_probability = max(10, min(95, score))
        
        return {
            "ticker": spac.ticker,
            "target": spac.target_company,
            "completion_probability": final_probability,
            "probability_label": "HIGH" if final_probability >= 75 else "MODERATE" if final_probability >= 55 else "LOW",
            "key_factors": factors,
            "risk_level": "HIGH" if final_probability < 60 else "MODERATE" if final_probability < 80 else "LOW"
        }
    
    def screen_arbitrage_opportunities(self, min_annualized_yield: float = 5.0) -> List[Dict]:
        """Find SPAC arbitrage opportunities"""
        opportunities = []
        
        for spac in self.spacs:
            arb_data = self.calculate_arbitrage_spread(spac)
            
            if arb_data["arbitrage_opportunity"] and arb_data["annualized_yield"] >= min_annualized_yield:
                prob_data = self.assess_merger_probability(spac)
                
                opportunities.append({
                    "ticker": spac.ticker,
                    "target": spac.target_company,
                    "current_price": spac.current_price,
                    "discount_to_nav": arb_data["discount_to_nav"],
                    "annualized_yield": arb_data["annualized_yield"],
                    "days_until_deadline": arb_data["days_until_deadline"],
                    "completion_probability": prob_data["completion_probability"],
                    "risk_adjusted_yield": round(arb_data["annualized_yield"] * (prob_data["completion_probability"] / 100), 2),
                    "risk_level": prob_data["risk_level"],
                    "sector": spac.sector
                })
        
        return sorted(opportunities, key=lambda x: x["risk_adjusted_yield"], reverse=True)
    
    def analyze_redemption_risk(self, spac: SPAC) -> Dict:
        """Analyze risk of high redemption rates"""
        # High redemption = less cash for company
        estimated_redemption = spac.redemption_rate_estimate
        
        trust_value = spac.trust_value
        remaining_cash = trust_value * (1 - estimated_redemption)
        
        # Check if remaining cash sufficient for target needs
        target_need_ratio = remaining_cash / spac.target_valuation if spac.target_valuation > 0 else 0
        
        return {
            "ticker": spac.ticker,
            "estimated_redemption_rate": round(estimated_redemption * 100, 1),
            "trust_value": round(trust_value / 1e6, 1),  # In millions
            "remaining_cash": round(remaining_cash / 1e6, 1),
            "cash_coverage_ratio": round(target_need_ratio, 2),
            "redemption_risk": "HIGH" if estimated_redemption > 0.5 else "MODERATE" if estimated_redemption > 0.3 else "LOW",
            "deal_viability": "AT_RISK" if target_need_ratio < 0.5 else "VIABLE"
        }
    
    def get_pre_merger_summary(self) -> Dict:
        """Get summary of pre-merger SPAC landscape"""
        total_spacs = len(self.spacs)
        
        # Categorize by phase
        near_vote = [s for s in self.spacs 
                     if (s.merger_vote_date - datetime.utcnow()).days <= 30]
        
        # Arbitrage opportunities
        arb_opps = self.screen_arbitrage_opportunities(min_annualized_yield=3.0)
        
        # Average metrics
        avg_premium = statistics.mean([s.premium_to_nav for s in self.spacs]) if self.spacs else 0
        avg_redemption = statistics.mean([s.redemption_rate_estimate for s in self.spacs]) if self.spacs else 0
        
        return {
            "total_pre_merger_spacs": total_spacs,
            "votes_within_30_days": len(near_vote),
            "arbitrage_opportunities": len(arb_opps),
            "average_premium_to_nav": round(avg_premium * 100, 2),
            "average_redemption_estimate": round(avg_redemption * 100, 1),
            "best_arbitrage_opportunities": arb_opps[:5],
            "market_sentiment": "BULLISH" if avg_premium > 0.05 else "CAUTIOUS" if avg_premium > 0 else "BEARISH"
        }

import statistics
