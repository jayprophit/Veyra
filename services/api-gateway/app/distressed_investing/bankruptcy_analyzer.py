"""Bankruptcy Analyzer - Chapter 7/11 analysis"""
from typing import Dict

class BankruptcyAnalyzer:
    """Analyze bankruptcy proceedings"""
    
    def chapter11_analysis(self, assets: float, liabilities: float,
                          annual_ebitda: float) -> Dict:
        """Analyze Chapter 11 reorganization"""
        debt_to_assets = liabilities / assets if assets > 0 else 1
        
        # DIP financing need
        dip_need = liabilities * 0.15 if debt_to_assets > 0.8 else liabilities * 0.10
        
        # Recovery estimates by creditor class
        recovery = {
            "secured": min(100, assets * 0.7 / liabilities * 100) if liabilities > 0 else 0,
            "senior_unsecured": min(80, assets * 0.5 / liabilities * 100) if liabilities > 0 else 0,
            "junior": min(30, assets * 0.2 / liabilities * 100) if liabilities > 0 else 0,
            "equity": max(0, (assets - liabilities) / assets * 100) if assets > 0 else 0
        }
        
        return {
            "chapter": 11,
            "debt_to_assets": round(debt_to_assets * 100, 1),
            "dip_financing_needed": dip_need,
            "estimated_recovery": recovery,
            "reorganization_viable": annual_ebitda > 0
        }
    
    def chapter7_liquidation(self, assets: float, liabilities: float) -> Dict:
        """Analyze Chapter 7 liquidation"""
        liquidation_value = assets * 0.7  # Fire sale discount
        recovery = liquidation_value / liabilities * 100 if liabilities > 0 else 0
        
        return {
            "chapter": 7,
            "liquidation_value": liquidation_value,
            "recovery_rate": round(recovery, 1),
            "shortfall": max(0, liabilities - liquidation_value)
        }
