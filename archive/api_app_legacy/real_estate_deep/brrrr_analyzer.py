"""BRRRR Analyzer - Buy, Rehab, Rent, Refinance, Repeat"""
from typing import Dict

class BRRRRAnalyzer:
    """Analyze BRRRR real estate strategy"""
    
    def brrrr_calculation(self, purchase_price: float,
                         rehab_cost: float,
                         arv: float,  # After Repair Value
                         monthly_rent: float,
                         refinance_ltv: float = 0.75) -> Dict:
        """Calculate complete BRRRR cycle"""
        total_investment = purchase_price + rehab_cost
        
        # Refinance amount
        refinance_amount = arv * refinance_ltv
        
        # Cash left in deal
        cash_left = total_investment - refinance_amount
        
        # Cash flow
        # Assume mortgage payment on refinance amount at 7%
        mortgage_rate = 0.07 / 12
        loan_term_months = 360
        mortgage_payment = (refinance_amount * mortgage_rate * (1 + mortgage_rate)**loan_term_months) / \
                          ((1 + mortgage_rate)**loan_term_months - 1)
        
        monthly_cashflow = monthly_rent - mortgage_payment - (monthly_rent * 0.3)  # 30% expenses
        
        # Cash on cash return (infinite if all cash pulled out)
        coc_return = (monthly_cashflow * 12 / cash_left * 100) if cash_left > 0 else float('inf')
        
        return {
            "total_investment": total_investment,
            "refinance_amount": refinance_amount,
            "cash_left_in_deal": max(0, cash_left),
            "monthly_cashflow": round(monthly_cashflow, 0),
            "cash_on_cash_return": "infinite" if coc_return == float('inf') else round(coc_return, 1),
            "brrrr_success": cash_left <= 0,
            "velocity_capital": cash_left <= 0  # Can repeat immediately
        }
    
    def velocity_potential(self, starting_capital: float,
                          avg_deal_size: float,
                          recycle_rate: float = 0.9) -> Dict:
        """Calculate how many properties can be acquired with velocity"""
        properties = []
        remaining_capital = starting_capital
        
        for i in range(1, 11):  # Max 10 iterations
            if remaining_capital >= avg_deal_size * 0.25:  # Need 25% down
                properties.append(i)
                cash_used = avg_deal_size * 0.25
                cash_recovered = cash_used * recycle_rate
                remaining_capital = remaining_capital - cash_used + cash_recovered
            else:
                break
        
        return {
            "properties_in_5_years": len(properties),
            "final_capital": round(remaining_capital, 0),
            "capital_efficiency": len(properties) * avg_deal_size / starting_capital,
            "strategy": "high_velocity" if len(properties) > 5 else "moderate_velocity"
        }
    
    def rehab_roi(self, rehab_costs: Dict[str, float],
                 value_adds: Dict[str, float]) -> Dict:
        """Calculate ROI on specific rehab items"""
        results = {}
        
        for item, cost in rehab_costs.items():
            value = value_adds.get(item, 0)
            roi = (value - cost) / cost * 100 if cost > 0 else 0
            results[item] = {
                "cost": cost,
                "value_added": value,
                "roi": round(roi, 1),
                "recommendation": "do" if roi > 50 else "consider" if roi > 20 else "skip"
            }
        
        return results
