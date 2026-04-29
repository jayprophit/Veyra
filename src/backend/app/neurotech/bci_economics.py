"""Brain-Computer Interface Economics"""
from typing import Dict

class BCImain:
    """Analyze BCI companies and market economics"""
    
    def __init__(self, application: str = "medical"):
        self.application = application  # medical, consumer, research
    
    def market_sizing(self) -> Dict:
        markets = {
            "medical": {
                "target_patients": 5000000,  # Paralysis, ALS, stroke
                "device_cost": 50000,
                "tam_billions": 50,
                "penetration_2030": 0.10
            },
            "consumer": {
                "target_users": 100000000,  # Gaming, productivity
                "device_cost": 5000,
                "tam_billions": 500,
                "penetration_2030": 0.02
            },
            "research": {
                "target_labs": 50000,
                "device_cost": 20000,
                "tam_billions": 1,
                "penetration_2030": 0.30
            }
        }
        
        return markets.get(self.application, markets["medical"])
    
    def device_economics(self, units_annual: int = 10000) -> Dict:
        # Hardware costs
        electrode_array = 2000
        signal_processor = 1500
        wireless_transmitter = 800
        battery = 300
        enclosure = 400
        
        bom_cost = electrode_array + signal_processor + wireless_transmitter + battery + enclosure
        
        # Manufacturing
        manufacturing = bom_cost * 0.30
        
        # Total cost
        total_cost = bom_cost + manufacturing
        
        # Pricing
        if self.application == "medical":
            price = 50000
        elif self.application == "consumer":
            price = 5000
        else:
            price = 20000
        
        margin = price - total_cost
        
        return {
            "bom_cost": bom_cost,
            "manufacturing_cost": manufacturing,
            "total_cost": total_cost,
            "retail_price": price,
            "gross_margin": margin,
            "margin_pct": round(margin / price * 100, 1),
            "annual_units": units_annual,
            "annual_revenue_millions": (price * units_annual) / 1e6
        }
    
    def company_valuation(self, revenue: float = 50e6, stage: str = "growth") -> Dict:
        multiples = {
            "seed": 15,
            "early": 25,
            "growth": 40,
            "public": 20
        }
        
        multiple = multiples.get(stage, 40)
        
        # Key players for comparison
        comparables = {
            "neuralink": {"valuation": 5e9, "stage": "private", "employees": 300},
            "synchron": {"valuation": 0.5e9, "stage": "clinical", "employees": 100},
            "blackrock_neurotech": {"valuation": 0.1e9, "stage": "commercial", "employees": 50},
            "paradromics": {"valuation": 0.1e9, "stage": "development", "employees": 40}
        }
        
        implied_value = revenue * multiple
        
        return {
            "revenue": revenue,
            "valuation_multiple": multiple,
            "implied_valuation": implied_value,
            "stage": stage,
            "comparable_companies": comparables,
            "market_cap_revenue_ratio": round(implied_value / revenue, 1)
        }
    
    def clinical_trial_costs(self, phases: int = 3) -> Dict:
        # BCI clinical trials are expensive
        phase_1 = 10e6  # Safety
        phase_2 = 30e6  # Efficacy
        phase_3 = 100e6  # Pivotal
        
        costs = [phase_1, phase_2, phase_3][:phases]
        total = sum(costs)
        
        # Timeline
        years_per_phase = 2
        total_years = phases * years_per_phase
        
        return {
            "total_cost_millions": total / 1e6,
            "cost_by_phase": [c/1e6 for c in costs],
            "timeline_years": total_years,
            "patients_per_phase": [10, 50, 200][:phases],
            "success_probability": 0.30  # High failure rate
        }
    
    def risk_factors(self) -> Dict:
        return {
            "technical_risks": [
                "Biocompatibility and longevity",
                "Signal degradation over time",
                "Infection risk from implantation",
                "Bandwidth limitations"
            ],
            "regulatory_risks": [
                "FDA Class III device pathway",
                "Long approval timelines (5-10 years)",
                "Post-market surveillance requirements"
            ],
            "commercial_risks": [
                "Reimbursement uncertainty",
                "High initial cost barrier",
                "Surgical infrastructure required"
            ],
            "mitigation_strategies": [
                "Partner with academic medical centers",
                "Start with humanitarian use",
                "Build surgical training programs"
            ]
        }
