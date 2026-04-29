"""Breeding Economics - Exotic animal breeding ROI"""
from typing import Dict

class BreedingEconomics:
    """Analyze exotic animal breeding economics"""
    
    def breeding_program_roi(self, acquisition_cost: float,
                            annual_care_cost: float,
                            offspring_per_year: float,
                            offspring_value: float,
                            years_to_maturity: int) -> Dict:
        """Calculate breeding program ROI"""
        total_cost_first_year = acquisition_cost + annual_care_cost
        annual_revenue = offspring_per_year * offspring_value
        
        # Payback including maturation period
        total_cost_to_maturity = acquisition_cost + (annual_care_cost * years_to_maturity)
        payback_from_maturity = total_cost_to_maturity / annual_revenue if annual_revenue > 0 else 999
        
        return {
            "total_setup_cost": total_cost_first_year,
            "annual_revenue": round(annual_revenue, 0),
            "years_to_maturity": years_to_maturity,
            "payback_years": round(payback_from_maturity + years_to_maturity, 1),
            "conservation_note": "cites_permits_required"
        }
    
    def rarity_premium(self, wild_population: int,
                      captive_population: int,
                      base_price: float) -> Dict:
        """Calculate rarity premium for endangered species"""
        total_population = wild_population + captive_population
        scarcity_ratio = 10000 / total_population if total_population > 0 else 0
        
        premium = min(scarcity_ratio, 50)  # Cap at 50x
        adjusted_price = base_price * (1 + premium)
        
        return {
            "wild_population": wild_population,
            "captive_population": captive_population,
            "scarcity_ratio": round(scarcity_ratio, 2),
            "price_premium": round(premium, 2),
            "adjusted_value": round(adjusted_price, 0)
        }
