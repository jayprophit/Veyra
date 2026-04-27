"""Convertible Arbitrage - Analyze convertible bond arbitrage opportunities"""
from typing import Dict
from dataclasses import dataclass

@dataclass
class ConvertibleBond:
    issuer: str
    bond_price: float
    conversion_price: float
    stock_price: float
    coupon: float
    years_to_maturity: float
    credit_spread: float
    volatility: float

class ConvertibleArbitrage:
    """Analyze convertible bond arbitrage"""
    
    def __init__(self):
        self.risk_free_rate = 0.05
    
    def calculate_conversion_value(self, bond: ConvertibleBond) -> Dict:
        """Calculate conversion parity and premium"""
        conversion_ratio = 100 / bond.conversion_price  # Assume $1000 par
        conversion_value = conversion_ratio * bond.stock_price
        
        conversion_premium = bond.bond_price - conversion_value
        conversion_premium_pct = (conversion_premium / conversion_value) * 100
        
        # Breakeven (years to earn premium back through coupon advantage)
        stock_div_yield = 0.015  # Assume 1.5% dividend yield
        coupon_advantage = bond.coupon - stock_div_yield
        
        if coupon_advantage > 0:
            breakeven_years = conversion_premium_pct / (coupon_advantage * 100)
        else:
            breakeven_years = float('inf')
        
        return {
            "issuer": bond.issuer,
            "bond_price": bond.bond_price,
            "conversion_value": round(conversion_value, 2),
            "conversion_premium": round(conversion_premium, 2),
            "conversion_premium_pct": round(conversion_premium_pct, 2),
            "breakeven_years": round(breakeven_years, 1) if breakeven_years != float('inf') else "NEVER",
            "parity_status": "PREMIUM" if conversion_premium_pct > 10 else "AT_PARITY" if conversion_premium_pct < 5 else "FAIR"
        }
    
    def calculate_arbitrage_metrics(self, bond: ConvertibleBond) -> Dict:
        """Calculate convertible arbitrage metrics"""
        conv_data = self.calculate_conversion_value(bond)
        
        # Delta (sensitivity to stock price)
        conversion_ratio = 100 / bond.conversion_price
        delta = min(1.0, conv_data["conversion_value"] / bond.bond_price)
        
        # Gamma estimate (how delta changes)
        gamma = delta * (1 - delta) * bond.volatility
        
        # Implied credit spread vs actual
        # Simplified: if implied > actual, bond is cheap
        implied_credit = bond.credit_spread * (1 + (conv_data["conversion_premium_pct"] / 100))
        
        # Arbitrage score
        arb_score = 0
        if conv_data["conversion_premium_pct"] < 15:
            arb_score += 20
        if delta > 0.5:
            arb_score += 20
        if bond.volatility > 0.25:
            arb_score += 15  # More volatility = more option value
        if bond.credit_spread > 0.03:
            arb_score += 15  # Higher yield
        
        return {
            "issuer": bond.issuer,
            "arbitrage_score": arb_score,
            "delta": round(delta, 3),
            "gamma": round(gamma, 4),
            "hedge_ratio": round(delta * conversion_ratio, 1),
            "strategy": "LONG_CONVERTIBLE_SHORT_STOCK" if delta > 0.5 else "LONG_CONVERTIBLE_ONLY",
            "expected_return_pct": round(arb_score * 0.5, 1),
            "risk_level": "HIGH" if bond.credit_spread > 0.05 else "MODERATE",
            **conv_data
        }
    
    def find_opportunities(self, bonds: list, min_score: int = 50) -> list:
        """Find best convertible arbitrage opportunities"""
        opportunities = []
        
        for bond in bonds:
            metrics = self.calculate_arbitrage_metrics(bond)
            if metrics["arbitrage_score"] >= min_score:
                opportunities.append(metrics)
        
        return sorted(opportunities, key=lambda x: x["arbitrage_score"], reverse=True)
