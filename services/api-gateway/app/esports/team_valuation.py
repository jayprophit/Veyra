"""Esports Team Valuation"""
from typing import Dict

class TeamValuation:
    """Valuation models for esports organizations"""
    
    def revenue_streams(self) -> Dict:
        return {
            "sponsorships": {"share": 0.40, "growth": 0.15},
            "media_rights": {"share": 0.25, "growth": 0.20},
            "merchandise": {"share": 0.15, "growth": 0.10},
            "ticket_sales": {"share": 0.10, "growth": 0.25},
            "prize_pool": {"share": 0.10, "growth": 0.05}
        }
    
    def top_teams_valuation(self) -> Dict:
        return {
            "tsm": {"valuation_millions": 540, "revenue_millions": 56, "games": ["LoL", "Valorant"]},
            "cloud9": {"valuation_millions": 460, "revenue_millions": 48, "games": ["LoL", "CS:GO"]},
            "team_liquid": {"valuation_millions": 440, "revenue_millions": 42, "games": ["Dota 2", "LoL"]},
            "fnatic": {"valuation_millions": 260, "revenue_millions": 28, "games": ["CS:GO", "LoL"]},
            "gen_g": {"valuation_millions": 250, "revenue_millions": 26, "games": ["LoL"], "region": "Korea"}
        }
    
    def valuation_multiples(self) -> Dict:
        return {
            "ev_revenue": 8.5,
            "traditional_sports_comparison": "NBA teams: 8-10x, Esports: 8-12x",
            "premium_for": ["Large fanbase", "Multi-game presence", "Winning history"],
            "discount_for": ["Single game dependence", "Unstable rosters"]
        }
    
    def investment_thesis(self) -> Dict:
        return {
            "bull_case": "Media rights explosion, mainstream adoption",
            "bear_case": "Game publisher control, player cost inflation",
            "key_risk": "Game popularity decline = team value collapse",
            "opportunity": "Undervalued vs traditional sports given audience size"
        }
