"""Sukuk Analyzer - Islamic bonds"""
from typing import Dict

class SukukAnalyzer:
    def sukuk_pricing(self, par_value: float, rental_rate: float, tenor_years: int) -> Dict:
        """Price an Ijarah Sukuk (asset-backed)"""
        annual_rental = par_value * rental_rate
        total_rental = annual_rental * tenor_years
        
        return {
            "par_value": par_value,
            "rental_rate": rental_rate * 100,
            "annual_rental": annual_rental,
            "total_rental_over_tenor": total_rental,
            "structure": "Ijarah (lease-based)",
            "asset_backed": True
        }
    
    def murabaha_sukuk(self, cost_price: float, profit_rate: float, maturity_months: int) -> Dict:
        """Structure Murabaha Sukuk (cost-plus financing)"""
        profit_amount = cost_price * profit_rate * (maturity_months / 12)
        total_repayment = cost_price + profit_amount
        
        return {
            "cost_price": cost_price,
            "profit_amount": profit_amount,
            "total_repayment": total_repayment,
            "profit_rate_annual": profit_rate * 100,
            "structure": "Murabaha",
            "compliant": True  # Deferred payment sale
        }
    
    def sukuk_vs_bond_comparison(self, sukuk_yield: float, bond_yield: float,
                               tax_rate: float) -> Dict:
        """Compare Sukuk to conventional bond"""
        # Sukuk often has different tax treatment
        sukuk_after_tax = sukuk_yield * (1 - tax_rate * 0.8)  # Potential tax advantage
        bond_after_tax = bond_yield * (1 - tax_rate)
        
        return {
            "sukuk_yield": sukuk_yield,
            "bond_yield": bond_yield,
            "sukuk_after_tax": sukuk_after_tax,
            "bond_after_tax": bond_after_tax,
            "advantage": "sukuk" if sukuk_after_tax > bond_after_tax else "bond",
            "spread": abs(sukuk_after_tax - bond_after_tax)
        }
    
    def mudaraba_profit_sharing(self, capital: float, profit: float,
                               investor_share: float) -> Dict:
        """Calculate Mudaraba profit-sharing"""
        # Mudaraba: investor provides capital, manager provides skill
        investor_profit = profit * investor_share
        manager_profit = profit * (1 - investor_share)
        
        return {
            "capital_invested": capital,
            "total_profit": profit,
            "investor_return": investor_profit,
            "manager_return": manager_profit,
            "investor_roi": investor_profit / capital if capital > 0 else 0,
            "structure": "Mudaraba (trust financing)"
        }
