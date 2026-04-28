"""Tax Strategist - Tax optimization strategies"""
from typing import Dict, List

class TaxStrategist:
    """Generate tax optimization strategies"""
    
    def retirement_contribution_strategy(self, income: float, age: int,
                                        current_contribution: float) -> Dict:
        """Optimize retirement contributions"""
        # 401k limits
        base_limit = 23000
        catchup = 7500 if age >= 50 else 0
        total_limit = base_limit + catchup
        
        # Space remaining
        space_remaining = total_limit - current_contribution
        
        # Tax savings at marginal rate (estimate 24%)
        marginal_rate = 0.24
        potential_savings = space_remaining * marginal_rate
        
        return {
            "current_contribution": current_contribution,
            "annual_limit": total_limit,
            "space_remaining": space_remaining,
            "potential_tax_savings": round(potential_savings, 0),
            "recommended_contribution": total_limit,
            "catchup_available": age >= 50
        }
    
    def tax_loss_harvesting(self, positions: List[Dict]) -> Dict:
        """Identify tax loss harvesting opportunities"""
        total_losses = 0
        total_gains = 0
        opportunities = []
        
        for pos in positions:
            unrealized = pos.get("unrealized_pnl", 0)
            if unrealized < 0:
                total_losses += abs(unrealized)
                opportunities.append({
                    "symbol": pos.get("symbol"),
                    "loss": abs(unrealized),
                    "tax_value": abs(unrealized) * 0.24  # At 24% rate
                })
            elif unrealized > 0:
                total_gains += unrealized
        
        # Max deduction $3000 against ordinary income
        deduction_against_income = min(3000, total_losses)
        remaining_losses = total_losses - deduction_against_income
        
        # Offset capital gains
        gain_offset = min(remaining_losses, total_gains)
        carryforward = remaining_losses - gain_offset
        
        return {
            "total_losses_available": round(total_losses, 0),
            "harvesting_opportunities": opportunities,
            "ordinary_income_deduction": deduction_against_income,
            "capital_gain_offset": round(gain_offset, 0),
            "tax_savings_this_year": round((deduction_against_income + gain_offset) * 0.24, 0),
            "carryforward_losses": round(carryforward, 0),
            "wash_sale_warning": "Check 30-day rule before buying back"
        }
    
    def charitable_giving_optimization(self, income: float, 
                                      appreciated_assets: List[Dict]) -> Dict:
        """Optimize charitable giving strategy"""
        # Strategy: donate appreciated assets instead of cash
        total_appreciation = sum(a.get("unrealized_gain", 0) for a in appreciated_assets)
        
        # Avoid capital gains tax + get deduction
        marginal_rate = 0.24
        tax_avoided = total_appreciation * 0.15  # LTCG rate
        deduction_value = sum(a.get("current_value", 0) for a in appreciated_assets) * marginal_rate
        
        total_benefit = tax_avoided + deduction_value
        
        return {
            "strategy": "Donate appreciated assets instead of cash",
            "appreciation_donated": round(total_appreciation, 0),
            "capital_gains_avoided": round(tax_avoided, 0),
            "deduction_value": round(deduction_value, 0),
            "total_tax_benefit": round(total_benefit, 0),
            "cash_preserved": round(sum(a.get("current_value", 0) for a in appreciated_assets), 0)
        }
    
    def business_structure_optimization(self, revenue: float, 
                                     expenses: float, 
                                     salary: float) -> Dict:
        """Compare business structures"""
        profit = revenue - expenses
        
        # Sole proprietor - SE tax on all profit
        se_tax = profit * 0.9235 * 0.153
        
        # S-Corp - SE tax only on salary, rest as distribution
        s_corp_se = salary * 0.9235 * 0.153
        s_corp_savings = se_tax - s_corp_se
        
        # QBI deduction (20% of profit)
        qbi_deduction = profit * 0.20
        qbi_tax_savings = qbi_deduction * 0.24
        
        return {
            "current_profit": profit,
            "sole_proprietor_se_tax": round(se_tax, 0),
            "s_corp_se_tax": round(s_corp_se, 0),
            "s_corp_savings": round(s_corp_savings, 0),
            "qbi_deduction": round(qbi_deduction, 0),
            "qbi_tax_savings": round(qbi_tax_savings, 0),
            "recommendation": "S-Corp" if s_corp_savings > 2000 else "LLC"
        }
