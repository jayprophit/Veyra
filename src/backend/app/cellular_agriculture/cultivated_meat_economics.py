"""Cultivated Meat Economics - Lab-grown meat production analysis"""
from typing import Dict

class CultivatedMeatEconomics:
    """Analyze cultivated meat facility investments"""
    
    def __init__(self, product_type: str = "beef", annual_volume_tons: float = 1000):
        self.product = product_type  # beef, chicken, pork, seafood
        self.volume = annual_volume_tons
    
    def production_cost_trajectory(self, year: int = 2030) -> Dict:
        # Cost per kg projections (industry estimates)
        cost_projections = {
            "beef": {2024: 100, 2030: 30, 2040: 15},
            "chicken": {2024: 50, 2030: 15, 2040: 8},
            "pork": {2024: 60, 2030: 18, 2040: 10},
            "seafood": {2024: 80, 2030: 25, 2040: 12}
        }
        
        product_costs = cost_projections.get(self.product, cost_projections["beef"])
        cost = product_costs.get(year, 30)
        
        conventional_price = {
            "beef": 12,
            "chicken": 4,
            "pork": 6,
            "seafood": 15
        }.get(self.product, 10)
        
        return {
            "cultivated_cost_per_kg": cost,
            "conventional_price": conventional_price,
            "premium_pct": round((cost / conventional_price - 1) * 100, 0),
            "cost_competitive": cost <= conventional_price,
            "year": year
        }
    
    def facility_capex(self, bioreactor_size_liters: float = 50000) -> Dict:
        # Bioreactor costs per liter capacity
        reactor_cost_per_liter = 1000  # $/L for food-grade bioreactors
        
        total_reactor_cost = bioreactor_size_liters * reactor_cost_per_liter
        
        # Additional equipment
        media_prep = total_reactor_cost * 0.20
        downstream = total_reactor_cost * 0.30
        clean_room = total_reactor_cost * 0.25
        
        total = total_reactor_cost + media_prep + downstream + clean_room
        
        return {
            "total_capex": round(total, 0),
            "per_ton_annual_capacity": round(total / self.volume, 0),
            "breakdown": {
                "bioreactors": round(total_reactor_cost, 0),
                "media_prep": round(media_prep, 0),
                "downstream": round(downstream, 0),
                "facility": round(clean_room, 0)
            }
        }
    
    def market_opportunity(self, addressable_market_pct: float = 1) -> Dict:
        # Global meat market sizes
        market_sizes = {
            "beef": 400e9,    # $400B
            "chicken": 250e9,
            "pork": 300e9,
            "seafood": 200e9
        }
        
        tam = market_sizes.get(self.product, 300e9)
        sam = tam * (addressable_market_pct / 100)
        
        return {
            "total_addressable_market": round(tam / 1e9, 1),
            "served_addressable_market": round(sam / 1e9, 1),
            "cagr_projected": 15,  # 15% annual growth
            "2030_market_size": round(sam * (1.15 ** 6) / 1e9, 1)
        }
    
    def investment_landscape(self) -> Dict:
        companies = [
            ("UPSIDE Foods", 0.6e9),
            ("Mosa Meat", 0.1e9),
            ("Memphis Meats", 0.2e9),
            ("Aleph Farms", 0.12e9),
            ("BlueNalu", 0.08e9)
        ]
        
        total_funding = sum(c[1] for c in companies)
        
        return {
            "total_venture_funding": round(total_funding / 1e9, 2),
            "leading_companies": len(companies),
            "avg_round_size": round(total_funding / len(companies) / 1e6, 0),
            "sector_status": "Pre-commercial",
            "regulatory_approval": "Singapore, USA (limited)"
        }
