"""Reputation System - Decentralized reputation scoring"""
from typing import Dict

class ReputationSystem:
    """Calculate decentralized reputation scores"""
    
    def calculate_score(self, address: str, transactions: int, age_days: int) -> Dict:
        """Calculate reputation score"""
        base = min(transactions / 100, 1.0) * 50
        age_bonus = min(age_days / 365, 1.0) * 30
        score = base + age_bonus + 20  # Starting reputation
        
        return {
            "address": address[:10] + "...",
            "score": round(score, 1),
            "tier": "GOLD" if score > 80 else "SILVER" if score > 60 else "BRONZE"
        }
