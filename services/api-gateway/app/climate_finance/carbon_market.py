"""Carbon Market - Carbon credit pricing and market analysis"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CarbonCredit:
    vintage: int  # Year of credit generation
    tonnes: float
    credit_type: str  # EUA, CCA, VCU, etc.
    project_location: str
    registry: str
    verified: bool
    additional_certifications: List[str]

class CarbonMarket:
    """Analyze carbon credit markets and pricing"""
    
    def __init__(self):
        self.carbon_prices = {
            "EUA": 85.0,      # EU Allowances
            "CCA": 32.0,      # California Carbon Allowances
            "RGGI": 15.0,     # Regional Greenhouse Gas Initiative
            "VCU": 8.0,       # Verified Carbon Units (voluntary)
            "GS": 12.0,       # Gold Standard
        }
        self.credits: List[CarbonCredit] = []
    
    def add_credit(self, credit: CarbonCredit):
        """Add carbon credit to portfolio"""
        self.credits.append(credit)
    
    def calculate_credit_value(self, credit: CarbonCredit, 
                               market_price_per_tonne: float = None) -> Dict:
        """Calculate value of carbon credit"""
        # Get base price for credit type
        base_price = market_price_per_tonne or self.carbon_prices.get(credit.credit_type, 10.0)
        
        # Apply quality premiums/discounts
        price_adjustment = 0
        
        # Vintage premium (newer = more valuable)
        current_year = datetime.utcnow().year
        vintage_age = current_year - credit.vintage
        if vintage_age <= 2:
            price_adjustment += 0.15  # 15% premium
        elif vintage_age > 5:
            price_adjustment -= 0.10  # 10% discount for old credits
        
        # Verification premium
        if credit.verified:
            price_adjustment += 0.10
        
        # Certification premiums
        cert_premiums = {
            "CORSIA": 0.20,
            "VCS": 0.15,
            "Gold_Standard": 0.15,
            "CDM": 0.10,
            "SOCIAL_CARBON": 0.25
        }
        
        for cert in credit.additional_certifications:
            price_adjustment += cert_premiums.get(cert, 0)
        
        # Location factor (developed markets premium)
        developed_markets = ["USA", "EU", "UK", "Canada", "Australia", "Japan"]
        if credit.project_location in developed_markets:
            price_adjustment += 0.10
        
        adjusted_price = base_price * (1 + price_adjustment)
        total_value = credit.tonnes * adjusted_price
        
        return {
            "credit_type": credit.credit_type,
            "vintage": credit.vintage,
            "tonnes": credit.tonnes,
            "base_price_per_tonne": round(base_price, 2),
            "adjusted_price_per_tonne": round(adjusted_price, 2),
            "total_value": round(total_value, 2),
            "price_premium_pct": round(price_adjustment * 100, 1),
            "key_factors": self._identify_pricing_factors(credit, price_adjustment)
        }
    
    def _identify_pricing_factors(self, credit: CarbonCredit, adjustment: float) -> List[str]:
        """Identify factors affecting credit price"""
        factors = []
        
        if credit.verified:
            factors.append("Verified credit (+10%)")
        
        current_year = datetime.utcnow().year
        if current_year - credit.vintage <= 2:
            factors.append("Recent vintage (+15%)")
        
        if credit.additional_certifications:
            factors.append(f"Certifications: {', '.join(credit.additional_certifications)}")
        
        if adjustment < 0:
            factors.append("Age discount applied")
        
        return factors
    
    def analyze_portfolio(self) -> Dict:
        """Analyze carbon credit portfolio"""
        if not self.credits:
            return {"error": "No credits in portfolio"}
        
        total_tonnes = sum(c.tonnes for c in self.credits)
        total_value = 0
        
        by_type = {}
        by_vintage = {}
        
        for credit in self.credits:
            valuation = self.calculate_credit_value(credit)
            total_value += valuation["total_value"]
            
            # Group by type
            by_type[credit.credit_type] = by_type.get(credit.credit_type, 0) + credit.tonnes
            
            # Group by vintage
            by_vintage[credit.vintage] = by_vintage.get(credit.vintage, 0) + credit.tonnes
        
        # Calculate vintage diversification
        vintage_concentration = max(by_vintage.values()) / total_tonnes if total_tonnes > 0 else 0
        
        # Calculate type diversification
        type_concentration = max(by_type.values()) / total_tonnes if total_tonnes > 0 else 0
        
        return {
            "total_credits": len(self.credits),
            "total_tonnes": total_tonnes,
            "total_value_usd": round(total_value, 2),
            "avg_price_per_tonne": round(total_value / total_tonnes, 2) if total_tonnes > 0 else 0,
            "by_credit_type": by_type,
            "by_vintage": by_vintage,
            "diversification_score": round((1 - max(vintage_concentration, type_concentration)) * 100, 1),
            "risk_rating": "HIGH" if type_concentration > 0.7 else "MODERATE" if type_concentration > 0.5 else "LOW"
        }
    
    def price_forward_contract(self, tonnes: float, 
                               delivery_year: int,
                               credit_type: str = "EUA") -> Dict:
        """Price carbon forward contract"""
        current_price = self.carbon_prices.get(credit_type, 50.0)
        
        # Forward curve assumption (simplified)
        # Prices generally rise due to declining caps
        years_forward = delivery_year - datetime.utcnow().year
        
        if years_forward <= 0:
            forward_price = current_price
        else:
            # Assume 8% annual appreciation
            appreciation_rate = 0.08
            forward_price = current_price * ((1 + appreciation_rate) ** years_forward)
        
        contract_value = tonnes * forward_price
        
        # Discount for credit risk
        credit_risk_discount = 0.02 * years_forward  # 2% per year
        adjusted_value = contract_value * (1 - credit_risk_discount)
        
        return {
            "credit_type": credit_type,
            "delivery_year": delivery_year,
            "tonnes": tonnes,
            "spot_price": round(current_price, 2),
            "forward_price": round(forward_price, 2),
            "contract_value": round(contract_value, 2),
            "adjusted_value": round(adjusted_value, 2),
            "appreciation_assumption": "8% annual",
            "hedge_ratio": "Consider offsetting with physical credits"
        }
    
    def get_market_summary(self) -> Dict:
        """Get carbon market summary"""
        total_market_value = sum(
            self.carbon_prices.values()
        ) * 1000000  # Rough estimate in millions
        
        return {
            "compliance_markets": {
                "EUA": {"price": self.carbon_prices["EUA"], "cap_mt": 1500},
                "CCA": {"price": self.carbon_prices["CCA"], "cap_mt": 350},
                "RGGI": {"price": self.carbon_prices["RGGI"], "cap_mt": 75}
            },
            "voluntary_markets": {
                "VCU": {"price": self.carbon_prices["VCU"], "volume_mt": 300},
                "GS": {"price": self.carbon_prices["GS"], "volume_mt": 180}
            },
            "trends": {
                "direction": "UPWARD",
                "driver": "Tightening regulations and net-zero commitments",
                "forecast_2025": "EUA: $100-120, Voluntary: $15-25"
            },
            "total_market_value_estimate_usd_millions": round(total_market_value, 0)
        }
    
    def calculate_arbitrage_opportunities(self) -> List[Dict]:
        """Find carbon market arbitrage opportunities"""
        opportunities = []
        
        # Compare voluntary vs compliance markets
        vcu_price = self.carbon_prices["VCU"]
        eua_price = self.carbon_prices["EUA"]
        
        spread = eua_price - vcu_price
        if spread > 20:  # Significant spread
            opportunities.append({
                "strategy": "BUY_VCU_SELL_EUA",
                "long_market": "VCU (Voluntary)",
                "short_market": "EUA (Compliance)",
                "spread_usd": round(spread, 2),
                "potential_return_pct": round((spread / vcu_price) * 100, 1),
                "risk": "Basis risk - credits may not be fungible",
                "execution_complexity": "HIGH"
            })
        
        # Compare geographic markets
        cca_price = self.carbon_prices["CCA"]
        rggi_price = self.carbon_prices["RGGI"]
        
        geo_spread = abs(cca_price - rggi_price)
        if geo_spread > 10:
            cheap = "RGGI" if rggi_price < cca_price else "CCA"
            expensive = "CCA" if rggi_price < cca_price else "RGGI"
            
            opportunities.append({
                "strategy": f"BUY_{cheap}_SELL_{expensive}",
                "spread_usd": round(geo_spread, 2),
                "risk": "Regulatory divergence risk",
                "execution_complexity": "MEDIUM"
            })
        
        return opportunities
