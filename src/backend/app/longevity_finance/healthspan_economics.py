"""Healthspan Economics - Economics of healthy lifespan"""
from typing import Dict

class HealthspanEconomics:
    """Economic analysis of healthspan extension"""
    
    def healthspan_npv(self, current_age: int,
                      expected_lifespan: int,
                      healthspan_extension: int,
                      annual_healthcare_savings: float,
                      productivity_gain: float) -> Dict:
        """Calculate NPV of healthspan extension"""
        discount_rate = 0.03
        
        # Years of additional healthy life
        additional_years = healthspan_extension
        
        # Annual benefit
        annual_benefit = annual_healthcare_savings + productivity_gain
        
        # NPV calculation
        npv = sum(annual_benefit / ((1 + discount_rate) ** i) 
                 for i in range(1, additional_years + 1))
        
        return {
            "current_age": current_age,
            "expected_lifespan": expected_lifespan,
            "healthspan_extension": healthspan_extension,
            "annual_benefit": annual_benefit,
            "npv_of_extension": round(npv, 0),
            "per_year_value": round(npv / additional_years, 0) if additional_years > 0 else 0
        }
    
    def compression_of_morbidity(self, chronic_care_years_saved: float,
                                 cost_per_year: float) -> Dict:
        """Calculate savings from compressing morbidity"""
        total_savings = chronic_care_years_saved * cost_per_year
        
        return {
            "years_of_illness_avoided": chronic_care_years_saved,
            "cost_per_year": cost_per_year,
            "total_savings": round(total_savings, 0),
            "quality_adjusted_life_years": chronic_care_years_saved * 0.7  # QALY estimate
        }
    
    def longevity_dividend(self, population: int,
                          life_expectancy_gain: float,
                          gdp_per_capita: float) -> Dict:
        """Calculate macroeconomic longevity dividend"""
        # Additional productive years
        productive_years = life_expectancy_gain * 0.6  # Assume 60% productive
        
        # Value per person
        value_per_person = productive_years * gdp_per_capita * 0.7  # 70% of GDP is labor-related
        
        total_dividend = value_per_person * population
        
        return {
            "population": population,
            "life_expectancy_gain": life_expectancy_gain,
            "productive_years_added": productive_years,
            "value_per_person": round(value_per_person, 0),
            "total_longevity_dividend": round(total_dividend, 0),
            "gdp_impact_percent": round((total_dividend / (population * gdp_per_capita)) * 100, 2)
        }
