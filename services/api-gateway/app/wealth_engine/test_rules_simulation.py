"""Test Rules Simulation - Compare £20/week under different allocation rules"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

@dataclass
class SimulationResult:
    rule_name: str
    final_capital: float
    total_contributed: float
    total_return: float
    return_pct: float
    max_drawdown: float
    monthly_values: List[float]

class RulesSimulation:
    """Simulate wealth growth under different allocation rules"""
    
    # Historical return assumptions (annual)
    ASSET_RETURNS = {
        'safe': {'mean': 0.045, 'std': 0.01},      # 4.5% ±1%
        'growth': {'mean': 0.08, 'std': 0.15},      # 8% ±15%
        'income': {'mean': 0.055, 'std': 0.05},      # 5.5% ±5%
        'alternative': {'mean': 0.06, 'std': 0.12}, # 6% ±12%
    }
    
    RULES = {
        '10_90': {'safe': 0.10, 'growth': 0.90, 'income': 0, 'alternative': 0},
        '50_30_20': {'safe': 0, 'growth': 0.50, 'income': 0.30, 'alternative': 0.20},
        '90_10': {'safe': 0.90, 'growth': 0.10, 'income': 0, 'alternative': 0},
        '60_40': {'safe': 0, 'growth': 0.60, 'income': 0.40, 'alternative': 0},
        'equal_thirds': {'safe': 0.33, 'growth': 0.33, 'income': 0.34, 'alternative': 0},
        'all_growth': {'safe': 0, 'growth': 1.0, 'income': 0, 'alternative': 0},
        'all_safe': {'safe': 1.0, 'growth': 0, 'income': 0, 'alternative': 0},
    }
    
    def __init__(self, weekly_contribution: float = 20, years: int = 5):
        self.weekly = weekly_contribution
        self.years = years
        self.weeks = years * 52
        
    def run_simulation(self, rule_name: str, random_seed: int = 42) -> SimulationResult:
        """Run single simulation"""
        random.seed(random_seed)
        
        rule = self.RULES[rule_name]
        capital = 0
        total_contributed = 0
        monthly_values = []
        max_capital = 0
        max_drawdown = 0
        
        for week in range(self.weeks):
            # Add contribution
            capital += self.weekly
            total_contributed += self.weekly
            
            # Apply weekly returns (compound weekly)
            weekly_return = self._calculate_weekly_return(rule)
            capital *= (1 + weekly_return)
            
            # Track monthly for chart
            if week % 4 == 0:
                monthly_values.append(capital)
            
            # Track drawdown
            if capital > max_capital:
                max_capital = capital
            drawdown = (max_capital - capital) / max_capital if max_capital > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        total_return = capital - total_contributed
        return_pct = (total_return / total_contributed) * 100 if total_contributed > 0 else 0
        
        return SimulationResult(
            rule_name=rule_name,
            final_capital=capital,
            total_contributed=total_contributed,
            total_return=total_return,
            return_pct=return_pct,
            max_drawdown=max_drawdown,
            monthly_values=monthly_values
        )
    
    def _calculate_weekly_return(self, rule: Dict) -> float:
        """Calculate blended weekly return"""
        annual_return = 0
        annual_variance = 0
        
        for asset, pct in rule.items():
            if pct == 0:
                continue
            asset_data = self.ASSET_RETURNS[asset]
            annual_return += asset_data['mean'] * pct
            annual_variance += (asset_data['std'] * pct) ** 2
        
        # Add randomness
        annual_std = annual_variance ** 0.5
        random_annual = random.gauss(annual_return, annual_std)
        
        # Convert to weekly
        weekly_return = (1 + random_annual) ** (1/52) - 1
        
        return weekly_return
    
    def compare_all_rules(self) -> Dict:
        """Run all rules and compare"""
        results = {}
        
        print(f"\n{'='*70}")
        print(f"£{self.weekly}/week SIMULATION COMPARISON")
        print(f"Duration: {self.years} years ({self.weeks} weeks)")
        print(f"{'='*70}\n")
        
        for rule_name in self.RULES.keys():
            result = self.run_simulation(rule_name)
            results[rule_name] = result
            
            print(f"{result.rule_name:15} | Final: £{result.final_capital:7,.0f} | "
                  f"Profit: £{result.total_return:6,.0f} ({result.return_pct:5.1f}%) | "
                  f"Max DD: {result.max_drawdown*100:5.1f}%")
        
        return results
    
    def get_recommendation(self, risk_tolerance: str, has_debt: bool = False) -> str:
        """Recommend rule based on profile"""
        if has_debt:
            return "Pay off >10% APR debt first, then use 90/10 until emergency fund built"
        
        recommendations = {
            'conservative': '90/10 or 60/40 - Capital preservation priority',
            'moderate': '50/30/20 - Balanced growth and income',
            'aggressive': '10/90 - Maximize long-term growth'
        }
        
        return recommendations.get(risk_tolerance, '50/30/20 - Balanced approach')
    
    def print_yearly_breakdown(self, rule_name: str):
        """Print year-by-year for one rule"""
        result = self.run_simulation(rule_name)
        
        print(f"\n{'='*70}")
        print(f"YEAR-BY-YEAR: {rule_name.upper()}")
        print(f"{'='*70}")
        print(f"{'Year':<6} {'Contributed':>12} {'Capital':>12} {'Return':>10} {'Cumulative':>12}")
        print(f"{'-'*60}")
        
        contributed_per_year = self.weekly * 52
        
        for year in range(self.years + 1):
            month_index = year * 12
            if month_index < len(result.monthly_values):
                capital = result.monthly_values[month_index]
                contributed = contributed_per_year * year
                ret = capital - contributed
                cumulative_pct = (ret / contributed * 100) if contributed > 0 else 0
                
                print(f"{year:<6} £{contributed:>11,.0f} £{capital:>11,.0f} "
                      f"£{ret:>9,.0f} {cumulative_pct:>10.1f}%")

def main():
    """Run comparison test"""
    sim = RulesSimulation(weekly_contribution=20, years=5)
    
    # Compare all rules
    results = sim.compare_all_rules()
    
    # Show best and worst
    best = max(results.values(), key=lambda x: x.final_capital)
    worst = min(results.values(), key=lambda x: x.final_capital)
    safest = min(results.values(), key=lambda x: x.max_drawdown)
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"🏆 Highest Final Capital: {best.rule_name} (£{best.final_capital:,.0f})")
    print(f"🛡️  Safest (Lowest Drawdown): {safest.rule_name} ({safest.max_drawdown*100:.1f}%)")
    print(f"📉 Lowest Final Capital: {worst.rule_name} (£{worst.final_capital:,.0f})")
    
    # Year-by-year for top 3
    print(f"\n{'='*70}")
    print("DETAILED BREAKDOWN - TOP 3 RULES")
    print(f"{'='*70}")
    
    top_3 = sorted(results.values(), key=lambda x: x.final_capital, reverse=True)[:3]
    for result in top_3:
        sim.print_yearly_breakdown(result.rule_name)
    
    # Recommendations
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS BY PROFILE")
    print(f"{'='*70}")
    print(f"Conservative (safety first):     {sim.get_recommendation('conservative')}")
    print(f"Moderate (balanced):             {sim.get_recommendation('moderate')}")
    print(f"Aggressive (growth focused):     {sim.get_recommendation('aggressive')}")
    print(f"With high-interest debt:         {sim.get_recommendation('moderate', has_debt=True)}")
    
    print(f"\n{'='*70}")
    print("NOTE: Simulations use historical volatility. Actual results will vary.")
    print("Past performance does not guarantee future results.")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
