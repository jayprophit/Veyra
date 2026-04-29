"""Petcare Economics - Pet retail and services analysis"""
from typing import Dict

class PetcareEconomics:
    """Analyze pet care business economics"""
    
    def pet_store_unit_economics(self, sqft: int,
                                annual_sales_per_sqft: float,
                                cogs_pct: float,
                                rent_per_sqft: float) -> Dict:
        """Calculate pet store unit economics"""
        annual_revenue = sqft * annual_sales_per_sqft
        cogs = annual_revenue * (cogs_pct / 100)
        rent = sqft * rent_per_sqft
        labor_estimate = sqft * 15  # $15/sqft labor
        
        ebitda = annual_revenue - cogs - rent - labor_estimate
        margin = (ebitda / annual_revenue) * 100 if annual_revenue > 0 else 0
        
        return {
            "annual_revenue": round(annual_revenue, 0),
            "ebitda": round(ebitda, 0),
            "ebitda_margin": round(margin, 1),
            "revenue_per_sqft": annual_sales_per_sqft,
            "sqft_required": sqft,
            "viability": "strong" if margin > 15 else "moderate" if margin > 8 else "weak"
        }
    
    def services_attachment_rate(self, product_sales: float,
                                 grooming_attachment: float,
                                 vet_attachment: float,
                                 training_attachment: float) -> Dict:
        """Calculate services revenue from product customers"""
        grooming_revenue = product_sales * grooming_attachment
        vet_revenue = product_sales * vet_attachment
        training_revenue = product_sales * training_attachment
        
        total_services = grooming_revenue + vet_revenue + training_revenue
        
        return {
            "grooming_revenue": round(grooming_revenue, 0),
            "vet_services_revenue": round(vet_revenue, 0),
            "training_revenue": round(training_revenue, 0),
            "total_services": round(total_services, 0),
            "services_mix": round(total_services / product_sales * 100, 1)
        }
