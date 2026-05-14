"""Wine Investing - Fine wine portfolio analytics"""
from typing import Dict

class WineInvesting:
    """Analyze wine investments and cellars"""
    
    def bottle_valuation(self, vintage: int, producer: str, critic_score: int) -> Dict:
        base_price = 50
        vintage_premium = max(0, (2024 - vintage) * 5) if vintage < 2020 else 0
        score_premium = (critic_score - 85) * 10 if critic_score > 85 else 0
        value = base_price + vintage_premium + score_premium
        return {"bottle_value": round(value, 0), "vintage": vintage, "score": critic_score}
    
    def cellar_returns(self, bottles: int, avg_cost: float, current_value: float, years_held: float) -> Dict:
        total_cost = bottles * avg_cost
        total_value = bottles * current_value
        profit = total_value - total_cost
        cagr = ((total_value / total_cost) ** (1/years_held) - 1) * 100 if years_held > 0 else 0
        return {"total_invested": total_cost, "current_value": total_value, "profit": profit, "cagr": round(cagr, 1)}
