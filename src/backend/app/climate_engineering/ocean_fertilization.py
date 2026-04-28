"""Ocean Fertilization - Iron fertilization economics"""
from typing import Dict

class OceanFertilization:
    """Economics of ocean iron fertilization"""
    
    def iron_fertilization_cost(self, iron_tons: float,
                                 shipping_distance_nm: float,
                                 carbon_sequestered_per_ton_iron: float) -> Dict:
        """Calculate iron fertilization program cost"""
        iron_cost = iron_tons * 500  # $500/ton iron ore
        shipping_cost = shipping_distance_nm * 0.1 * iron_tons  # $0.1 per nm per ton
        vessel_charter = 50000 * 30  # 30 days
        
        total_cost = iron_cost + shipping_cost + vessel_charter
        carbon_sequestered = iron_tons * carbon_sequestered_per_ton_iron
        
        cost_per_ton_carbon = total_cost / carbon_sequestered if carbon_sequestered > 0 else float('inf')
        
        return {
            "iron_cost": round(iron_cost, 0),
            "shipping_cost": round(shipping_cost, 0),
            "vessel_charter": vessel_charter,
            "total_program_cost": round(total_cost, 0),
            "carbon_sequestered_tons": round(carbon_sequestered, 0),
            "cost_per_ton_co2": round(cost_per_ton_carbon, 2),
            "competitive": cost_per_ton_carbon < 100
        }
    
    def whale_poop_multiplier(self, whale_population: int,
                             iron_defecation_per_whale: float,
                             carbon_multiplier: float) -> Dict:
        """Value of whale population for carbon sequestration"""
        total_iron = whale_population * iron_defecation_per_whale
        carbon_sequestered = total_iron * carbon_multiplier
        
        # At $50/ton carbon
        value = carbon_sequestered * 50
        value_per_whale = value / whale_population if whale_population > 0 else 0
        
        return {
            "whale_population": whale_population,
            "total_iron_fertilizer_tons": round(total_iron, 0),
            "carbon_sequestered_tons": round(carbon_sequestered, 0),
            "total_value": round(value, 0),
            "value_per_whale": round(value_per_whale, 0),
            "ecosystem_service": "carbon sequestration"
        }
    
    def upwelling_pump_economics(self, pumps: int,
                                pump_cost: float,
                                maintenance_per_year: float,
                                carbon_exported_per_pump: float) -> Dict:
        """Artificial upwelling pump economics"""
        capex = pumps * pump_cost
        annual_opex = pumps * maintenance_per_year
        annual_carbon = pumps * carbon_exported_per_pump
        
        # At $50/ton carbon
        annual_revenue = annual_carbon * 50
        
        # Simple payback
        payback = capex / (annual_revenue - annual_opex) if (annual_revenue - annual_opex) > 0 else float('inf')
        
        return {
            "number_of_pumps": pumps,
            "capex": capex,
            "annual_opex": annual_opex,
            "annual_carbon_exported": round(annual_carbon, 0),
            "annual_revenue": round(annual_revenue, 0),
            "simple_payback_years": round(payback, 1),
            "profitable": annual_revenue > annual_opex
        }
