"""Sports Betting - Odds analysis and arbitrage"""
from typing import Dict

class SportsBetting:
    """Analyze sports betting markets"""
    
    def decimal_to_implied_prob(self, odds: float) -> float:
        """Convert decimal odds to implied probability"""
        return 1 / odds if odds > 0 else 0
    
    def find_arbitrage(self, odds_a: float, odds_b: float) -> Dict:
        """Find arbitrage opportunities"""
        prob_a = self.decimal_to_implied_prob(odds_a)
        prob_b = self.decimal_to_implied_prob(odds_b)
        total_prob = prob_a + prob_b
        
        return {
            "arbitrage_exists": total_prob < 1.0,
            "profit_margin": round((1 - total_prob) * 100, 2) if total_prob < 1 else 0,
            "stake_a": round(prob_b / total_prob, 2) if total_prob > 0 else 0,
            "stake_b": round(prob_a / total_prob, 2) if total_prob > 0 else 0
        }
    
    def kelly_criterion(self, prob: float, odds: float) -> float:
        """Calculate Kelly criterion bet size"""
        if odds <= 1 or prob <= 0:
            return 0
        return (prob * odds - 1) / (odds - 1)
