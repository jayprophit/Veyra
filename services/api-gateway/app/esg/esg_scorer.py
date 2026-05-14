"""
ESG (Environmental, Social, Governance) Scoring System
Provides ESG ratings for stocks and portfolios
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ESGCategory(Enum):
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"


class ESGRating(Enum):
    LEADER = "AAA"  # Top 10%
    ABOVE_AVERAGE = "AA"  # Top 20%
    AVERAGE = "A"  # Middle 50%
    BELOW_AVERAGE = "BBB"  # Bottom 20%
    LAGGARD = "BB"  # Bottom 10%


@dataclass
class ESGScore:
    """ESG score for a company"""
    symbol: str
    company_name: str
    
    # Overall score (0-100)
    overall_score: float
    overall_rating: ESGRating
    
    # Component scores (0-100 each)
    environmental_score: float
    social_score: float
    governance_score: float
    
    # Detailed metrics
    environmental_metrics: Dict[str, float]  # carbon_intensity, waste_management, etc.
    social_metrics: Dict[str, float]  # diversity, labor_practices, etc.
    governance_metrics: Dict[str, float]  # board_independence, ethics, etc.
    
    # Controversies
    controversy_score: float  # 0-100, higher = more controversial
    controversy_flags: List[str]
    
    # Metadata
    sector: str
    industry: str
    market_cap: float
    last_updated: datetime
    data_source: str = "msci"  # msci, sustainalytics, refinitiv
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "company_name": self.company_name,
            "overall_score": self.overall_score,
            "overall_rating": self.overall_rating.value,
            "environmental_score": self.environmental_score,
            "social_score": self.social_score,
            "governance_score": self.governance_score,
            "controversy_level": self.controversy_score,
            "controversies": self.controversy_flags,
            "sector": self.sector,
            "industry": self.industry
        }


class ESGScorer:
    """
    ESG scoring and analysis system
    Integrates data from multiple ESG data providers
    """
    
    # ESG rating thresholds
    RATING_THRESHOLDS = {
        ESGRating.LEADER: 85,
        ESGRating.ABOVE_AVERAGE: 70,
        ESGRating.AVERAGE: 50,
        ESGRating.BELOW_AVERAGE: 30,
        ESGRating.LAGGARD: 0
    }
    
    def __init__(self):
        self.scores_cache: Dict[str, ESGScore] = {}
        self.sector_averages: Dict[str, Dict[str, float]] = {}
    
    async def get_esg_score(self, symbol: str) -> Optional[ESGScore]:
        """
        Get ESG score for a company
        
        In production: Fetch from MSCI, Sustainalytics, or Refinitiv API
        """
        # Mock ESG data for demonstration
        mock_scores = {
            "AAPL": ESGScore(
                symbol="AAPL",
                company_name="Apple Inc.",
                overall_score=76.5,
                overall_rating=ESGRating.ABOVE_AVERAGE,
                environmental_score=82.0,
                social_score=72.0,
                governance_score=75.0,
                environmental_metrics={
                    "carbon_intensity": 85.0,
                    "renewable_energy": 90.0,
                    "waste_recycling": 78.0,
                    "water_usage": 75.0
                },
                social_metrics={
                    "diversity_inclusion": 80.0,
                    "labor_practices": 70.0,
                    "product_safety": 85.0,
                    "community_impact": 65.0
                },
                governance_metrics={
                    "board_independence": 80.0,
                    "executive_compensation": 70.0,
                    "shareholder_rights": 75.0,
                    "business_ethics": 75.0
                },
                controversy_score=15.0,
                controversy_flags=["supply_chain_labor"],
                sector="Technology",
                industry="Consumer Electronics",
                market_cap=2.8e12,
                last_updated=datetime.utcnow()
            ),
            "TSLA": ESGScore(
                symbol="TSLA",
                company_name="Tesla, Inc.",
                overall_score=68.0,
                overall_rating=ESGRating.AVERAGE,
                environmental_score=88.0,
                social_score=55.0,
                governance_score=61.0,
                environmental_metrics={
                    "carbon_intensity": 95.0,
                    "renewable_energy": 85.0,
                    "battery_recycling": 70.0
                },
                social_metrics={
                    "workplace_safety": 50.0,
                    "labor_practices": 55.0
                },
                governance_metrics={
                    "board_structure": 45.0,
                    "executive_compensation": 75.0
                },
                controversy_score=35.0,
                controversy_flags=["workplace_safety", "twitter_distraction"],
                sector="Consumer Cyclical",
                industry="Auto Manufacturers",
                market_cap=800e9,
                last_updated=datetime.utcnow()
            ),
            "XOM": ESGScore(
                symbol="XOM",
                company_name="Exxon Mobil Corp",
                overall_score=42.0,
                overall_rating=ESGRating.BELOW_AVERAGE,
                environmental_score=25.0,
                social_score=55.0,
                governance_score=45.0,
                environmental_metrics={
                    "carbon_intensity": 15.0,
                    "renewable_investment": 20.0
                },
                social_metrics={},
                governance_metrics={},
                controversy_score=45.0,
                controversy_flags=["climate_lobbying", "oil_spills"],
                sector="Energy",
                industry="Oil & Gas",
                market_cap=450e9,
                last_updated=datetime.utcnow()
            )
        }
        
        return mock_scores.get(symbol)
    
    async def calculate_portfolio_esg_score(
        self,
        holdings: Dict[str, float]  # symbol -> weight (0-1)
    ) -> Dict[str, Any]:
        """
        Calculate weighted ESG score for portfolio
        
        Args:
            holdings: Dictionary of symbol -> portfolio weight
        """
        total_weight = sum(holdings.values())
        
        weighted_scores = {
            "overall": 0,
            "environmental": 0,
            "social": 0,
            "governance": 0
        }
        
        scores_found = []
        
        for symbol, weight in holdings.items():
            score = await self.get_esg_score(symbol)
            if score:
                normalized_weight = weight / total_weight
                weighted_scores["overall"] += score.overall_score * normalized_weight
                weighted_scores["environmental"] += score.environmental_score * normalized_weight
                weighted_scores["social"] += score.social_score * normalized_weight
                weighted_scores["governance"] += score.governance_score * normalized_weight
                scores_found.append(score)
        
        # Calculate overall rating
        overall = weighted_scores["overall"]
        rating = self._score_to_rating(overall)
        
        # Collect all controversies
        all_controversies = []
        for score in scores_found:
            all_controversies.extend(score.controversy_flags)
        
        return {
            "portfolio_overall_score": round(weighted_scores["overall"], 2),
            "portfolio_rating": rating.value,
            "environmental_score": round(weighted_scores["environmental"], 2),
            "social_score": round(weighted_scores["social"], 2),
            "governance_score": round(weighted_scores["governance"], 2),
            "holdings_analyzed": len(scores_found),
            "total_holdings": len(holdings),
            "controversies_exposure": list(set(all_controversies)),
            "recommendation": self._generate_esg_recommendation(overall, all_controversies)
        }
    
    async def get_esg_comparison(
        self,
        symbols: List[str]
    ) -> Dict[str, Any]:
        """Compare ESG scores across multiple companies"""
        scores = []
        for symbol in symbols:
            score = await self.get_esg_score(symbol)
            if score:
                scores.append(score.to_dict())
        
        if not scores:
            return {"error": "No ESG data available"}
        
        # Rankings
        scores_sorted = sorted(scores, key=lambda x: x["overall_score"], reverse=True)
        
        return {
            "companies": scores,
            "rankings": {
                "best_overall": scores_sorted[0]["symbol"],
                "best_environmental": max(scores, key=lambda x: x["environmental_score"])["symbol"],
                "best_social": max(scores, key=lambda x: x["social_score"])["symbol"],
                "best_governance": max(scores, key=lambda x: x["governance_score"])["symbol"]
            },
            "average_scores": {
                "overall": sum(s["overall_score"] for s in scores) / len(scores),
                "environmental": sum(s["environmental_score"] for s in scores) / len(scores),
                "social": sum(s["social_score"] for s in scores) / len(scores),
                "governance": sum(s["governance_score"] for s in scores) / len(scores)
            }
        }
    
    async def get_sustainable_alternatives(
        self,
        symbol: str,
        min_esg_score: float = 70.0
    ) -> List[Dict[str, Any]]:
        """
        Get sustainable alternatives to a given stock
        
        Finds similar companies with better ESG scores
        """
        target_score = await self.get_esg_score(symbol)
        if not target_score:
            return []
        
        # Mock alternatives
        alternatives = [
            {
                "symbol": "MSFT",
                "company_name": "Microsoft Corp",
                "esg_score": 78.5,
                "rating": "AA",
                "sector": target_score.sector,
                "reason": "Better governance practices"
            },
            {
                "symbol": "GOOGL",
                "company_name": "Alphabet Inc",
                "esg_score": 74.0,
                "rating": "AA",
                "sector": target_score.sector,
                "reason": "Strong renewable energy commitment"
            }
        ]
        
        return [a for a in alternatives if a["esg_score"] >= min_esg_score]
    
    def _score_to_rating(self, score: float) -> ESGRating:
        """Convert numeric score to letter rating"""
        for rating, threshold in sorted(
            self.RATING_THRESHOLDS.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if score >= threshold:
                return rating
        return ESGRating.LAGGARD
    
    def _generate_esg_recommendation(
        self,
        score: float,
        controversies: List[str]
    ) -> str:
        """Generate ESG recommendation based on score and controversies"""
        if score >= 70 and not controversies:
            return "Excellent ESG profile - suitable for sustainability-focused investors"
        elif score >= 70 and controversies:
            return "Good ESG score but monitor controversy flags"
        elif score >= 50:
            return "Average ESG profile - consider improvement opportunities"
        elif controversies:
            return "Multiple controversies and low ESG score - high risk for ESG investors"
        else:
            return "Below average ESG performance - consider alternatives"
