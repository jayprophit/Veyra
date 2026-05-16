"""Bond Analyzer - Analyze bond investments and fixed income securities"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import math

@dataclass
class Bond:
    cusip: str
    issuer: str
    coupon: float
    maturity_date: datetime
    face_value: float
    current_price: float
    credit_rating: str
    yield_to_maturity: float

class BondAnalyzer:
    """Analyze bond investments and fixed income securities"""
    
    def __init__(self):
        self.rating_scale = {
            "AAA": 1, "AA+": 2, "AA": 3, "AA-": 4,
            "A+": 5, "A": 6, "A-": 7,
            "BBB+": 8, "BBB": 9, "BBB-": 10,
            "BB+": 11, "BB": 12, "BB-": 13,  # Junk
            "B+": 14, "B": 15, "B-": 16,
            "CCC": 17, "CC": 18, "C": 19, "D": 20
        }
    
    def calculate_duration(self, bond: Bond) -> Dict:
        """Calculate Macaulay and Modified Duration"""
        # Simplified duration calculation
        years_to_maturity = (bond.maturity_date - datetime.utcnow()).days / 365.25
        
        # Macaulay duration approximation
        macaulay_duration = years_to_maturity * (1 - 1 / (1 + bond.yield_to_maturity) ** years_to_maturity)
        macaulay_duration = max(0.5, macaulay_duration)  # Minimum floor
        
        # Modified duration (price sensitivity)
        modified_duration = macaulay_duration / (1 + bond.yield_to_maturity)
        
        return {
            "macaulay_duration": round(macaulay_duration, 2),
            "modified_duration": round(modified_duration, 2),
            "years_to_maturity": round(years_to_maturity, 2),
            "interpretation": f"Price changes ~{round(modified_duration * 100, 1)}% for 1% yield change"
        }
    
    def calculate_convexity(self, bond: Bond) -> Dict:
        """Calculate bond convexity"""
        years = (bond.maturity_date - datetime.utcnow()).days / 365.25
        ytm = bond.yield_to_maturity
        coupon = bond.coupon
        
        # Convexity formula (simplified)
        if ytm == 0:
            convexity = years ** 2
        else:
            convexity = (years * (years + 1)) / ((1 + ytm) ** 2)
        
        return {
            "convexity": round(convexity, 2),
            "convexity_adjustment": True,
            "benefit": "Positive convexity benefits price when rates move"
        }
    
    def calculate_yield_metrics(self, bond: Bond) -> Dict:
        """Calculate comprehensive yield metrics"""
        # Current yield
        current_yield = bond.coupon / bond.current_price
        
        # Yield to maturity (provided in bond data)
        ytm = bond.yield_to_maturity
        
        # Yield to worst (if callable - simplified)
        ytw = ytm  # Assume not callable for simplicity
        
        # Taxable equivalent yield (for municipals)
        tax_rate = 0.35
        taxable_equivalent = ytm / (1 - tax_rate) if ytm > 0 else 0
        
        # Real yield (inflation adjusted, assume 2.5%)
        inflation = 0.025
        real_yield = ((1 + ytm) / (1 + inflation)) - 1
        
        return {
            "current_yield": round(current_yield * 100, 2),
            "yield_to_maturity": round(ytm * 100, 2),
            "yield_to_worst": round(ytw * 100, 2),
            "taxable_equivalent_yield": round(taxable_equivalent * 100, 2),
            "real_yield": round(real_yield * 100, 2),
            "yield_pickup_vs_treasury": round((ytm - 0.045) * 100, 2)  # Assume 4.5% treasury
        }
    
    def analyze_credit_risk(self, bond: Bond) -> Dict:
        """Analyze credit risk of bond"""
        rating_numeric = self.rating_scale.get(bond.credit_rating, 10)
        
        # Credit spread estimate based on rating
        spread_by_rating = {
            1: 0.005, 2: 0.006, 3: 0.007, 4: 0.008,  # AAA to AA-
            5: 0.010, 6: 0.012, 7: 0.015,             # A ratings
            8: 0.020, 9: 0.025, 10: 0.030,            # BBB ratings
            11: 0.040, 12: 0.050, 13: 0.060,          # BB ratings (junk)
            14: 0.080, 15: 0.100, 16: 0.120,          # B ratings
            17: 0.150, 18: 0.200, 19: 0.250, 20: 0.30 # Distressed
        }
        
        estimated_spread = spread_by_rating.get(rating_numeric, 0.05)
        
        # Default probability (simplified Merton model approximation)
        default_prob = min(0.30, rating_numeric / 50)  # Rough estimate
        
        # Recovery rate assumption
        recovery_rate = 0.40 if rating_numeric > 10 else 0.60
        
        expected_loss = default_prob * (1 - recovery_rate)
        
        return {
            "credit_rating": bond.credit_rating,
            "rating_numeric": rating_numeric,
            "investment_grade": rating_numeric <= 10,
            "estimated_credit_spread": round(estimated_spread * 100, 2),
            "default_probability_pct": round(default_prob * 100, 2),
            "expected_recovery_rate": round(recovery_rate * 100, 2),
            "expected_loss_pct": round(expected_loss * 100, 2),
            "risk_level": "LOW" if rating_numeric <= 6 else "MEDIUM" if rating_numeric <= 10 else "HIGH"
        }
    
    def price_sensitivity_analysis(self, bond: Bond, 
                                   yield_changes: List[float] = None) -> Dict:
        """Analyze price sensitivity to yield changes"""
        if yield_changes is None:
            yield_changes = [-0.02, -0.01, -0.005, 0, 0.005, 0.01, 0.02]
        
        duration_data = self.calculate_duration(bond)
        convexity_data = self.calculate_convexity(bond)
        
        mod_dur = duration_data["modified_duration"]
        convexity = convexity_data["convexity"]
        
        scenarios = []
        for yield_change in yield_changes:
            # Price change using duration and convexity
            price_change_pct = (-mod_dur * yield_change * 100 + 
                               0.5 * convexity * (yield_change * 100) ** 2 / 100)
            
            new_price = bond.current_price * (1 + price_change_pct / 100)
            
            scenarios.append({
                "yield_change_bps": int(yield_change * 10000),
                "price_change_pct": round(price_change_pct, 2),
                "new_price": round(new_price, 2),
                "new_yield": round((bond.yield_to_maturity + yield_change) * 100, 2)
            })
        
        return {
            "current_price": bond.current_price,
            "current_yield": round(bond.yield_to_maturity * 100, 2),
            "scenarios": scenarios,
            "break_even_yield": round(bond.yield_to_maturity * 100 - (1/mod_dur), 2)
        }
    
    def compare_bonds(self, bonds: List[Bond]) -> List[Dict]:
        """Compare multiple bonds"""
        comparisons = []
        
        for bond in bonds:
            yield_metrics = self.calculate_yield_metrics(bond)
            credit = self.analyze_credit_risk(bond)
            duration = self.calculate_duration(bond)
            
            # Risk-adjusted yield score
            risk_score = credit["rating_numeric"]
            adjusted_yield = yield_metrics["yield_to_maturity"] / risk_score
            
            comparisons.append({
                "cusip": bond.cusip,
                "issuer": bond.issuer,
                "rating": bond.credit_rating,
                "ytm": yield_metrics["yield_to_maturity"],
                "duration": duration["modified_duration"],
                "credit_spread": credit["estimated_credit_spread"],
                "risk_adjusted_score": round(adjusted_yield, 3),
                "recommendation": "BUY" if adjusted_yield > 2 and credit["investment_grade"] else "HOLD"
            })
        
        return sorted(comparisons, key=lambda x: x["risk_adjusted_score"], reverse=True)
    
    def ladder_builder(self, capital: float, rungs: int = 5,
                      start_year: int = 1) -> List[Dict]:
        """Build bond ladder for income and reinvestment"""
        ladder = []
        capital_per_rung = capital / rungs
        
        for i in range(rungs):
            maturity_year = start_year + i
            
            # Estimate yield for this maturity (assume upward sloping curve)
            estimated_yield = 0.045 + (maturity_year * 0.005)  # 0.5% per year
            
            # Estimate price (assume par)
            estimated_price = 100
            
            ladder.append({
                "rung": i + 1,
                "maturity_year": maturity_year,
                "investment_amount": round(capital_per_rung, 2),
                "estimated_yield": round(estimated_yield * 100, 2),
                "annual_income": round(capital_per_rung * estimated_yield, 2),
                "estimated_bonds_purchased": int(capital_per_rung / estimated_price),
                "maturity_reinvestment_year": datetime.utcnow().year + maturity_year
            })
        
        total_annual_income = sum(r["annual_income"] for r in ladder)
        
        return {
            "ladder_structure": ladder,
            "total_invested": round(capital, 2),
            "average_yield": round(sum(r["estimated_yield"] for r in ladder) / rungs, 2),
            "annual_income_stream": round(total_annual_income, 2),
            "monthly_income_estimate": round(total_annual_income / 12, 2),
            "ladder_benefits": [
                "Regular maturity schedule",
                "Reinvestment flexibility",
                "Interest rate risk mitigation",
                "Predictable income"
            ]
        }
