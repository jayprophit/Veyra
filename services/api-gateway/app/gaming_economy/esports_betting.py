"""Esports Betting - Competitive gaming markets"""
from typing import Dict

class EsportsBetting:
    """Esports betting analytics"""
    
    GAMES = ["cs2", "lol", "dota2", "valorant", "rocket_league"]
    
    def calculate_odds(self, team_a_rating: float, team_b_rating: float) -> Dict:
        """Calculate win probability and odds"""
        prob_a = team_a_rating / (team_a_rating + team_b_rating)
        prob_b = 1 - prob_a
        
        odds_a = 1 / prob_a if prob_a > 0 else 0
        odds_b = 1 / prob_b if prob_b > 0 else 0
        
        return {
            "team_a_win_prob": round(prob_a * 100, 1),
            "team_b_win_prob": round(prob_b * 100, 1),
            "decimal_odds_a": round(odds_a, 2),
            "decimal_odds_b": round(odds_b, 2),
            "vig": 0.05
        }
