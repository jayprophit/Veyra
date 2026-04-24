"""Goal-Based Investing - Track goals with probability"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional
import numpy as np

@dataclass
class InvestmentGoal:
    id: str
    name: str
    target_amount: float
    target_date: date
    current_amount: float
    monthly_contribution: float
    goal_type: str  # "retirement", "house", "college", "emergency", "custom"
    priority: int = 5  # 1-10, 10 = highest
    
class GoalBasedInvesting:
    """SSS-Grade goal tracking with Monte Carlo"""
    
    def __init__(self, mc_simulator=None):
        self.mc = mc_simulator
    
    def calculate_goal_probability(
        self,
        goal: InvestmentGoal,
        portfolio_return_mean: float = 0.08,
        portfolio_return_std: float = 0.15
    ) -> Dict:
        """Calculate probability of achieving goal"""
        
        years = (goal.target_date - date.today()).days / 365.25
        if years <= 0:
            return {"probability": 0, "status": "target_date_passed"}
        
        # Monte Carlo simulation
        n_simulations = 10000
        final_values = []
        
        for _ in range(n_simulations):
            value = goal.current_amount
            for _ in range(int(years)):
                # Random annual return
                annual_return = np.random.normal(
                    portfolio_return_mean, 
                    portfolio_return_std
                )
                # Monthly contributions + growth
                monthly_growth = (1 + annual_return) ** (1/12)
                for _ in range(12):
                    value = (value + goal.monthly_contribution) * monthly_growth
            
            final_values.append(value)
        
        final_values = np.array(final_values)
        probability = np.mean(final_values >= goal.target_amount)
        
        return {
            "goal_id": goal.id,
            "goal_name": goal.name,
            "probability": round(probability * 100, 2),
            "median_outcome": round(np.median(final_values), 2),
            "percentile_10": round(np.percentile(final_values, 10), 2),
            "percentile_90": round(np.percentile(final_values, 90), 2),
            "shortfall_risk": round(np.mean(final_values < goal.target_amount) * 100, 2),
            "years_remaining": round(years, 1),
            "recommended_monthly": self._calculate_required_contribution(
                goal, portfolio_return_mean
            )
        }
    
    def _calculate_required_contribution(
        self,
        goal: InvestmentGoal,
        expected_return: float
    ) -> float:
        """Calculate monthly contribution needed"""
        years = (goal.target_date - date.today()).days / 365.25
        if years <= 0:
            return 0
        
        # Future value of current amount
        fv_current = goal.current_amount * (1 + expected_return) ** years
        
        # Remaining needed
        remaining = goal.target_amount - fv_current
        if remaining <= 0:
            return 0
        
        # Annuity calculation
        monthly_rate = expected_return / 12
        months = years * 12
        
        if monthly_rate == 0:
            return remaining / months
        
        pmt = remaining * monthly_rate / ((1 + monthly_rate) ** months - 1)
        return round(pmt, 2)
    
    def get_all_goals_summary(
        self,
        goals: List[InvestmentGoal]
    ) -> Dict:
        """Summary of all goals"""
        
        results = []
        total_target = 0
        total_current = 0
        
        for goal in goals:
            prob = self.calculate_goal_probability(goal)
            results.append({
                "goal": {
                    "id": goal.id,
                    "name": goal.name,
                    "target": goal.target_amount,
                    "current": goal.current_amount,
                    "date": goal.target_date.isoformat()
                },
                "probability": prob["probability"],
                "status": self._get_goal_status(prob["probability"]),
                "on_track": prob["probability"] >= 70
            })
            total_target += goal.target_amount
            total_current += goal.current_amount
        
        on_track = sum(1 for r in results if r["on_track"])
        
        return {
            "goals": results,
            "summary": {
                "total_goals": len(goals),
                "on_track": on_track,
                "at_risk": len(goals) - on_track,
                "total_target": total_target,
                "total_current": total_current,
                "overall_progress": round(total_current / total_target * 100, 2) if total_target > 0 else 0
            }
        }
    
    def _get_goal_status(self, probability: float) -> str:
        """Get status based on probability"""
        if probability >= 80:
            return "on_track"
        elif probability >= 50:
            return "at_risk"
        else:
            return "off_track"
    
    def rebalance_for_goals(
        self,
        goals: List[InvestmentGoal],
        current_allocation: Dict[str, float]
    ) -> Dict:
        """Suggest allocation changes based on goals"""
        
        # Find nearest goal
        nearest = min(
            goals,
            key=lambda g: abs((g.target_date - date.today()).days)
        )
        
        years_to_nearest = (nearest.target_date - date.today()).days / 365.25
        
        # Glide path: reduce equity as goal approaches
        recommended_equity = max(20, 100 - (years_to_nearest * 5))
        
        current_equity = current_allocation.get("stocks", 50)
        
        return {
            "nearest_goal": nearest.name,
            "years_to_goal": round(years_to_nearest, 1),
            "current_equity_pct": current_equity,
            "recommended_equity_pct": recommended_equity,
            "suggested_changes": {
                "stocks": round(recommended_equity - current_equity, 1),
                "bonds": round(current_equity - recommended_equity, 1)
            }
        }

print("Goal-Based Investing loaded - SSS-grade goal tracking")
