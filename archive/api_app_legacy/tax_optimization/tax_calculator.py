"""Tax Calculator"""
from typing import Dict

class TaxCalculator:
    """Calculate taxes and effective rates"""
    
    US_BRACKETS = [
        (0, 11600, 0.10), (11600, 47150, 0.12), (47150, 100525, 0.22),
        (100525, 191950, 0.24), (191950, 243725, 0.32),
        (243725, 609350, 0.35), (609350, float('inf'), 0.37)
    ]
    
    def us_federal_tax(self, income: float, filing_status: str = "single") -> Dict:
        """Calculate US federal income tax"""
        tax = 0
        bracket_breakdown = []
        
        for low, high, rate in self.US_BRACKETS:
            if income > low:
                taxable_in_bracket = min(income, high) - low
                bracket_tax = taxable_in_bracket * rate
                tax += bracket_tax
                bracket_breakdown.append({
                    "bracket": f"${low:,} - ${high:,}",
                    "rate": f"{rate*100}%",
                    "tax": round(bracket_tax, 0)
                })
        
        effective_rate = tax / income if income > 0 else 0
        
        return {
            "gross_income": income,
            "federal_tax": round(tax, 0),
            "effective_rate": round(effective_rate * 100, 2),
            "take_home": round(income - tax, 0),
            "bracket_breakdown": bracket_breakdown
        }
    
    def capital_gains_tax(self, gains: float, holding_period_months: int,
                         ordinary_income: float) -> Dict:
        """Calculate capital gains tax"""
        # Determine long-term vs short-term
        is_long_term = holding_period_months > 12
        
        if is_long_term:
            # LTCG brackets based on income
            if ordinary_income < 47025:
                rate = 0.0
            elif ordinary_income < 518900:
                rate = 0.15
            else:
                rate = 0.20
        else:
            # STCG taxed as ordinary income
            rate = self._estimate_ordinary_rate(ordinary_income)
        
        tax = gains * rate
        
        return {
            "capital_gains": gains,
            "holding_period_months": holding_period_months,
            "long_term": is_long_term,
            "applicable_rate": rate * 100,
            "tax_owed": round(tax, 0),
            "net_proceeds": round(gains - tax, 0)
        }
    
    def _estimate_ordinary_rate(self, income: float) -> float:
        """Estimate ordinary income tax rate"""
        for low, high, rate in self.US_BRACKETS:
            if income <= high:
                return rate
        return 0.37
    
    def self_employment_tax(self, net_profit: float) -> Dict:
        """Calculate self-employment tax"""
        # 92.35% of net earnings subject to SE tax
        taxable = net_profit * 0.9235
        
        # Social Security (12.4% up to wage base) + Medicare (2.9%)
        ss_wage_base = 168600
        ss_tax = min(taxable, ss_wage_base) * 0.124
        medicare_tax = taxable * 0.029
        
        # Additional Medicare (0.9% over thresholds)
        addl_medicare = max(0, taxable - 200000) * 0.009
        
        total_se_tax = ss_tax + medicare_tax + addl_medicare
        
        # Deductible portion (50%)
        deductible = total_se_tax * 0.5
        
        return {
            "net_profit": net_profit,
            "se_taxable": round(taxable, 0),
            "social_security_tax": round(ss_tax, 0),
            "medicare_tax": round(medicare_tax, 0),
            "additional_medicare": round(addl_medicare, 0),
            "total_se_tax": round(total_se_tax, 0),
            "deductible_portion": round(deductible, 0)
        }
