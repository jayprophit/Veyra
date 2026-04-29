"""Neural Implant Valuation"""
from typing import Dict

class NeuralImplantValuation:
    """Deep brain stimulation and neural implant devices"""
    
    def __init__(self, condition: str = "parkinsons"):
        self.condition = condition  # parkinsons, epilepsy, depression, obesity
    
    def patient_economics(self) -> Dict:
        conditions = {
            "parkinsons": {
                "prevalence_us": 1000000,
                "candidates_for_dbs": 0.10,
                "device_cost": 35000,
                "surgical_cost": 50000,
                "annual_programming": 5000
            },
            "epilepsy": {
                "prevalence_us": 3400000,
                "candidates_for_rns": 0.05,
                "device_cost": 40000,
                "surgical_cost": 60000,
                "annual_monitoring": 3000
            },
            "depression": {
                "prevalence_us": 21000000,
                "candidates_for_vns": 0.01,
                "device_cost": 30000,
                "surgical_cost": 40000,
                "annual_adjustment": 2000
            }
        }
        
        data = conditions.get(self.condition, conditions["parkinsons"])
        
        addressable = data["prevalence_us"] * data["candidates_for_dbs"]
        total_first_year = data["device_cost"] + data["surgical_cost"]
        
        return {
            "condition": self.condition,
            "us_prevalence": data["prevalence_us"],
            "addressable_patients": int(addressable),
            "device_cost": data["device_cost"],
            "total_first_year_cost": total_first_year,
            "annual_follow_up": data.get("annual_programming", 3000),
            "market_value_millions": (addressable * total_first_year) / 1e6
        }
    
    def manufacturer_economics(self, units_sold: int = 5000) -> Dict:
        # Deep brain stimulation device costs
        device_bom = 8000
        manufacturing = 2000
        sales_marketing = 5000
        r_and_d_allocation = 3000
        
        total_cost = device_bom + manufacturing + sales_marketing + r_and_d_allocation
        
        device_price = 35000
        margin = device_price - total_cost
        
        return {
            "device_price": device_price,
            "total_cost": total_cost,
            "gross_margin": margin,
            "margin_pct": round(margin / device_price * 100, 1),
            "units_sold": units_sold,
            "revenue_millions": (device_price * units_sold) / 1e6,
            "profit_millions": (margin * units_sold) / 1e6
        }
    
    def competitive_landscape(self) -> Dict:
        return {
            "medtronic": {
                "market_share": 0.60,
                "devices": ["Activa PC", "Percept PC"],
                "revenue_segment_billions": 1.8,
                "focus": "Movement disorders"
            },
            "boston_scientific": {
                "market_share": 0.25,
                "devices": ["Vercise"],
                "revenue_segment_billions": 0.5,
                "focus": "Directional leads"
            },
            "abbott": {
                "market_share": 0.15,
                "devices": ["Infinity"],
                "revenue_segment_billions": 0.3,
                "focus": "MRI compatibility"
            },
            "emerging": [
                "Newronika (adaptive DBS)",
                "Aleva (directional)",
                "Pixium (retinal)"
            ]
        }
    
    def technology_trends(self) -> Dict:
        return {
            "current_generation": {
                "features": ["Open-loop stimulation", "Fixed parameters", "Periodic programming"],
                "battery_life": "3-5 years",
                "replacement_surgery": "Required"
            },
            "next_generation": {
                "features": ["Closed-loop (adaptive)", "AI-optimized", "Remote monitoring"],
                "battery_life": "10+ years (rechargeable)",
                "surgical_revision": "Minimized"
            },
            "breakthrough": {
                "features": ["Wireless power", "Bidirectional communication", "Cortical implants"],
                "timeline": "2028-2032"
            },
            "pricing_trend": "Premium for closed-loop (20-30% higher)"
        }
    
    def reimbursement_analysis(self) -> Dict:
        return {
            "medicare_coverage": "Established for PD and essential tremor",
            "private_insurance": "Generally favorable",
            "prior_authorization": "Required, criteria vary",
            "patient_out_of_pocket": {
                "medicare": "20% coinsurance after deductible",
                "typical_cost": "$5000-15000"
            },
            "coding": {
                "device_cpt": "61885",
                "surgery_cpt": "61867",
                "programming": "95983-95984"
            }
        }
