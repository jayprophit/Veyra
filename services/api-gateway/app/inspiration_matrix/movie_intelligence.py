"""Movie Intelligence Extractor - Trading strategies from financial movies"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class Movie(Enum):
    BIG_SHORT = "The Big Short"
    BILLIONS = "Billions"
    WOLF_WALL_STREET = "The Wolf of Wall Street"
    MARGIN_CALL = "Margin Call"
    WALL_STREET = "Wall Street"
    TRADING_PLACES = "Trading Places"
    MONEYBALL = "Moneyball"
    FLASH_BOYS = "Flash Boys"

@dataclass
class StrategyExtract:
    movie: Movie
    concept: str
    application: str
    risk_level: str
    expected_roi: float

class MovieIntelligenceExtractor:
    """Extract trading strategies from financial movies and TV"""
    
    def __init__(self):
        self.strategy_database = self._init_strategies()
        
    def _init_strategies(self) -> Dict:
        return {
            Movie.BIG_SHORT: {
                "concepts": [
                    {
                        "name": "Synthetic CDO Analysis",
                        "description": "Find mispriced risk in complex derivatives",
                        "application": "Detect overvalued assets through deep analysis",
                        "indicators": ["High correlation assumptions", "Mispriced risk premiums"],
                        "risk": "high",
                        "roi_potential": 10.0  # 1000% like Burry
                    },
                    {
                        "name": "Contrarian Conviction",
                        "description": "Bet against consensus when you have unique insight",
                        "application": "Hold positions through drawdowns if thesis is correct",
                        "indicators": ["Crowd wrong", "Data supports contrarian view"],
                        "risk": "very_high",
                        "roi_potential": 5.0
                    }
                ]
            },
            Movie.BILLIONS: {
                "concepts": [
                    {
                        "name": "Information Warfare",
                        "description": "Use legal information edge through superior network",
                        "application": "Build information advantage through expert networks",
                        "indicators": ["Legal edge detection", "Network intelligence"],
                        "risk": "medium",
                        "roi_potential": 0.5
                    },
                    {
                        "name": "Cohen Strategy",
                        "description": "Aggressive prosecution of information advantage",
                        "application": "Act decisively when conviction is high",
                        "indicators": ["High conviction", "Information edge"],
                        "risk": "medium",
                        "roi_potential": 0.8
                    }
                ]
            },
            Movie.WOLF_WALL_STREET: {
                "concepts": [
                    {
                        "name": "Pump Detection",
                        "description": "Recognize when assets are artificially inflated",
                        "application": "Avoid or short pump schemes",
                        "indicators": ["Hype without fundamentals", "Coordinated promotion"],
                        "risk": "medium",
                        "roi_potential": 0.4
                    },
                    {
                        "name": "Sell Pressure",
                        "description": "Aggressive sales tactics work in bull markets",
                        "application": "Recognize market sentiment through volume patterns",
                        "indicators": ["High volume", "Retail frenzy"],
                        "risk": "high",
                        "roi_potential": 0.3
                    }
                ]
            },
            Movie.MARGIN_CALL: {
                "concepts": [
                    {
                        "name": "Risk Cascade Modeling",
                        "description": "Understand how risk propagates through system",
                        "application": "Exit before cascade effects trigger",
                        "indicators": ["Interconnected risk", "Leverage buildup"],
                        "risk": "medium",
                        "roi_potential": 0.2  # Loss avoidance
                    },
                    {
                        "name": "First Mover Advantage",
                        "description": "Be first to exit when systemic risk detected",
                        "application": "Liquidate before others realize danger",
                        "indicators": ["Model breakdown", "Liquidity crunch"],
                        "risk": "high",
                        "roi_potential": 0.5
                    }
                ]
            },
            Movie.TRADING_PLACES: {
                "concepts": [
                    {
                        "name": "Information Arbitrage",
                        "description": "Trade on information asymmetry",
                        "application": "Use superior data to predict crop reports, earnings",
                        "indicators": ["Information edge", "Before public release"],
                        "risk": "high",
                        "roi_potential": 1.0
                    },
                    {
                        "name": "Behavioral Prediction",
                        "description": "Predict how others will react to information",
                        "application": "Front-run crowd reactions",
                        "indicators": ["Sentiment analysis", "Crowd psychology"],
                        "risk": "medium",
                        "roi_potential": 0.3
                    }
                ]
            },
            Movie.MONEYBALL: {
                "concepts": [
                    {
                        "name": "Statistical Arbitrage",
                        "description": "Find undervalued assets through data",
                        "application": "Quantitative edge finding through ignored metrics",
                        "indicators": ["Mispriced by market", "Superior metrics"],
                        "risk": "low",
                        "roi_potential": 0.2
                    },
                    {
                        "name": "Value Over Hype",
                        "description": "Buy what works, not what's popular",
                        "application": "Focus on cash flow, not growth stories",
                        "indicators": ["Low P/E", "High FCF"],
                        "risk": "low",
                        "roi_potential": 0.15
                    }
                ]
            }
        }
    
    def extract_strategy(self, movie: Movie, concept_name: str) -> Optional[Dict]:
        """Extract specific strategy from movie database"""
        movie_data = self.strategy_database.get(movie)
        if not movie_data:
            return None
        
        for concept in movie_data["concepts"]:
            if concept["name"].lower() == concept_name.lower():
                return {
                    "movie": movie.value,
                    "concept": concept["name"],
                    "description": concept["description"],
                    "application": concept["application"],
                    "indicators": concept["indicators"],
                    "risk_level": concept["risk"],
                    "expected_roi_multiplier": concept["roi_potential"]
                }
        
        return None
    
    def get_all_strategies(self) -> List[Dict]:
        """Get all extractable strategies from all movies"""
        all_strategies = []
        
        for movie, data in self.strategy_database.items():
            for concept in data["concepts"]:
                all_strategies.append({
                    "movie": movie.value,
                    "concept": concept["name"],
                    "risk": concept["risk"],
                    "roi_potential": concept["roi_potential"]
                })
        
        return sorted(all_strategies, key=lambda x: x["roi_potential"], reverse=True)
    
    def find_strategy_for_market_condition(self, condition: str) -> List[Dict]:
        """Find relevant strategies based on current market condition"""
        condition_mapping = {
            "bubble": [Movie.BIG_SHORT, Movie.WOLF_WALL_STREET],
            "crisis": [Movie.MARGIN_CALL, Movie.BIG_SHORT],
            "bull_market": [Movie.WOLF_WALL_STREET, Movie.BILLIONS],
            "correction": [Movie.MARGIN_CALL, Movie.TRADING_PLACES],
            "undervalued": [Movie.MONEYBALL],
            "manipulation": [Movie.WOLF_WALL_STREET, Movie.BILLIONS]
        }
        
        movies = condition_mapping.get(condition, [])
        strategies = []
        
        for movie in movies:
            data = self.strategy_database.get(movie, {})
            for concept in data.get("concepts", []):
                strategies.append({
                    "movie": movie.value,
                    "strategy": concept["name"],
                    "application": concept["application"]
                })
        
        return strategies
    
    def generate_movie_portfolio(self, risk_tolerance: str = "medium") -> Dict:
        """Generate portfolio strategy inspired by movie concepts"""
        if risk_tolerance == "high":
            selections = [
                (Movie.BIG_SHORT, "Synthetic CDO Analysis", 0.2),
                (Movie.BILLIONS, "Information Warfare", 0.3),
                (Movie.TRADING_PLACES, "Information Arbitrage", 0.2),
                (Movie.MARGIN_CALL, "Risk Cascade Modeling", 0.3)
            ]
        elif risk_tolerance == "medium":
            selections = [
                (Movie.BILLIONS, "Cohen Strategy", 0.25),
                (Movie.MONEYBALL, "Statistical Arbitrage", 0.35),
                (Movie.MARGIN_CALL, "Risk Cascade Modeling", 0.2),
                (Movie.WOLF_WALL_STREET, "Pump Detection", 0.2)
            ]
        else:  # low risk
            selections = [
                (Movie.MONEYBALL, "Statistical Arbitrage", 0.4),
                (Movie.MONEYBALL, "Value Over Hype", 0.3),
                (Movie.MARGIN_CALL, "Risk Cascade Modeling", 0.3)
            ]
        
        portfolio = {
            "theme": f"Cinema-Inspired {risk_tolerance.title()} Risk Portfolio",
            "allocations": [],
            "expected_roi": 0,
            "max_drawdown_estimate": 0.15 if risk_tolerance == "low" else 0.3 if risk_tolerance == "medium" else 0.5
        }
        
        for movie, concept, allocation in selections:
            strategy = self.extract_strategy(movie, concept)
            if strategy:
                portfolio["allocations"].append({
                    "movie": strategy["movie"],
                    "strategy": strategy["concept"],
                    "allocation_pct": allocation * 100,
                    "risk": strategy["risk_level"],
                    "expected_contribution": strategy["expected_roi_multiplier"] * allocation
                })
                portfolio["expected_roi"] += strategy["expected_roi_multiplier"] * allocation
        
        return portfolio
    
    def compare_to_real_traders(self) -> Dict:
        """Compare movie strategies to real-world trader styles"""
        comparisons = {
            "The Big Short": {
                "real_trader": "Michael Burry",
                "style": "Deep value, contrarian",
                "accuracy": "High - Burry actually made 489% in 2008"
            },
            "Billions": {
                "real_trader": "Steven Cohen (inspired by)",
                "style": "Information edge, aggressive",
                "accuracy": "Medium - dramatized but based on SAC Capital"
            },
            "Wolf of Wall Street": {
                "real_trader": "Jordan Belfort",
                "style": "Pump and dump",
                "accuracy": "High - Belfort's firm Stratton Oakmont crashed"
            },
            "Margin Call": {
                "real_trader": "Lehman Brothers traders",
                "style": "Risk management during crisis",
                "accuracy": "High - captures 2008 crisis dynamics"
            }
        }
        
        return comparisons
