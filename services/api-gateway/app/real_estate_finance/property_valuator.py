"""Property Valuator - Real estate property valuation and analysis"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Property:
    address: str
    property_type: str  # Residential, Commercial, Industrial, Mixed
    square_feet: float
    year_built: int
    bedrooms: int
    bathrooms: float
    lot_size_acres: float
    condition: str  # Excellent, Good, Fair, Poor

@dataclass
class Comparable:
    address: str
    sale_price: float
    square_feet: float
    sale_date: str
    bedrooms: int
    bathrooms: float
    condition: str
    distance_miles: float

class PropertyValuator:
    """Value real estate properties using multiple methods"""
    
    def __init__(self):
        self.cap_rates = {
            "Residential": 0.05,
            "Commercial": 0.06,
            "Industrial": 0.07,
            "Mixed": 0.055,
            "Retail": 0.065,
            "Office": 0.06,
            "Multifamily": 0.05
        }
        self.comparables_db: List[Comparable] = []
    
    def add_comparable(self, comp: Comparable):
        """Add comparable sale to database"""
        self.comparables_db.append(comp)
    
    def comparable_sales_analysis(self, property: Property, 
                                   radius_miles: float = 1.0) -> Dict:
        """Value property using comparable sales"""
        # Filter comparables by distance and property characteristics
        relevant_comps = [
            c for c in self.comparables_db
            if c.distance_miles <= radius_miles
            and abs(c.bedrooms - property.bedrooms) <= 1
            and abs(c.bathrooms - property.bathrooms) <= 1
        ]
        
        if not relevant_comps:
            return {"error": "No comparable sales found", "method": "COMPS"}
        
        # Calculate price per square foot for each comp
        for comp in relevant_comps:
            comp.ppsf = comp.sale_price / comp.square_feet if comp.square_feet > 0 else 0
        
        # Adjust for condition differences
        condition_adjustment = {
            ("Excellent", "Good"): 0.95,
            ("Excellent", "Fair"): 0.90,
            ("Excellent", "Poor"): 0.80,
            ("Good", "Fair"): 0.95,
            ("Good", "Poor"): 0.85,
            ("Fair", "Poor"): 0.90
        }
        
        adjusted_values = []
        for comp in relevant_comps:
            base_ppsf = comp.ppsf
            
            # Apply condition adjustment
            if comp.condition != property.condition:
                adjustment_key = (comp.condition, property.condition)
                reverse_key = (property.condition, comp.condition)
                
                if adjustment_key in condition_adjustment:
                    adjusted_ppsf = base_ppsf / condition_adjustment[adjustment_key]
                elif reverse_key in condition_adjustment:
                    adjusted_ppsf = base_ppsf * condition_adjustment[reverse_key]
                else:
                    adjusted_ppsf = base_ppsf
            else:
                adjusted_ppsf = base_ppsf
            
            adjusted_values.append({
                "comp_address": comp.address,
                "sale_price": comp.sale_price,
                "ppsf": round(base_ppsf, 2),
                "adjusted_ppsf": round(adjusted_ppsf, 2),
                "distance": comp.distance_miles
            })
        
        # Calculate weighted average (closer comps weighted more)
        total_weight = sum(1/c["distance"] for c in adjusted_values if c["distance"] > 0)
        weighted_ppsf = sum(
            c["adjusted_ppsf"] * (1/c["distance"] if c["distance"] > 0 else 1) / total_weight
            for c in adjusted_values
        ) if total_weight > 0 else 0
        
        estimated_value = weighted_ppsf * property.square_feet
        
        # Calculate confidence interval
        ppsf_values = [c["adjusted_ppsf"] for c in adjusted_values]
        if ppsf_values:
            import statistics
            std_dev = statistics.stdev(ppsf_values) if len(ppsf_values) > 1 else 0
            confidence_range = std_dev * property.square_feet
        else:
            confidence_range = estimated_value * 0.10
        
        return {
            "method": "COMPARABLE_SALES",
            "property": property.address,
            "num_comps": len(relevant_comps),
            "weighted_ppsf": round(weighted_ppsf, 2),
            "estimated_value": round(estimated_value, 0),
            "value_range_low": round(estimated_value - confidence_range, 0),
            "value_range_high": round(estimated_value + confidence_range, 0),
            "comparables": adjusted_values[:5],  # Top 5
            "confidence": "HIGH" if len(relevant_comps) >= 5 else "MODERATE" if len(relevant_comps) >= 3 else "LOW"
        }
    
    def income_capitalization(self, property: Property,
                             annual_rental_income: float,
                             operating_expenses: float,
                             vacancy_rate: float = 0.05) -> Dict:
        """Value property using income capitalization"""
        # Calculate Net Operating Income (NOI)
        effective_gross_income = annual_rental_income * (1 - vacancy_rate)
        net_operating_income = effective_gross_income - operating_expenses
        
        # Apply cap rate
        cap_rate = self.cap_rates.get(property.property_type, 0.06)
        
        property_value = net_operating_income / cap_rate if cap_rate > 0 else 0
        
        # Calculate gross rent multiplier
        grm = property_value / annual_rental_income if annual_rental_income > 0 else 0
        
        # Calculate cash on cash return (assuming 70% LTV)
        down_payment = property_value * 0.30
        mortgage_payment = (property_value * 0.70) * 0.045  # Simplified
        cash_flow = net_operating_income - mortgage_payment
        cash_on_cash = (cash_flow / down_payment * 100) if down_payment > 0 else 0
        
        return {
            "method": "INCOME_CAPITALIZATION",
            "property": property.address,
            "annual_rental_income": annual_rental_income,
            "effective_gross_income": round(effective_gross_income, 0),
            "operating_expenses": operating_expenses,
            "noi": round(net_operating_income, 0),
            "cap_rate_used": round(cap_rate * 100, 2),
            "estimated_value": round(property_value, 0),
            "gross_rent_multiplier": round(grm, 1),
            "cash_on_cash_return": round(cash_on_cash, 2),
            "property_type": property.property_type
        }
    
    def cost_approach(self, property: Property,
                     land_value: float,
                     depreciation_rate: float = 0.015) -> Dict:
        """Value property using cost approach (replacement cost)"""
        # Calculate replacement cost
        current_year = 2024
        age = current_year - property.year_built
        
        # Cost per square foot by property type
        replacement_costs = {
            "Residential": 150,
            "Commercial": 200,
            "Industrial": 120,
            "Mixed": 175,
            "Retail": 180,
            "Office": 190,
            "Multifamily": 160
        }
        
        cost_per_sf = replacement_costs.get(property.property_type, 150)
        replacement_cost_new = property.square_feet * cost_per_sf
        
        # Apply depreciation
        accumulated_depreciation = replacement_cost_new * (depreciation_rate * age)
        depreciated_value = replacement_cost_new - accumulated_depreciation
        
        # Add land value
        total_value = depreciated_value + land_value
        
        return {
            "method": "COST_APPROACH",
            "property": property.address,
            "replacement_cost_new": round(replacement_cost_new, 0),
            "age_years": age,
            "accumulated_depreciation": round(accumulated_depreciation, 0),
            "depreciated_building_value": round(depreciated_value, 0),
            "land_value": land_value,
            "total_estimated_value": round(total_value, 0),
            "effective_age": age  # Could be adjusted for condition
        }
    
    def reconcile_values(self, comp_value: Dict, 
                         income_value: Dict = None,
                         cost_value: Dict = None) -> Dict:
        """Reconcile multiple valuation methods"""
        values = []
        weights = []
        
        if comp_value and "estimated_value" in comp_value:
            values.append(comp_value["estimated_value"])
            weights.append(0.50)  # Comparable sales weighted most heavily
        
        if income_value and "estimated_value" in income_value:
            values.append(income_value["estimated_value"])
            weights.append(0.35)  # Income approach
        
        if cost_value and "estimated_value" in cost_value:
            values.append(cost_value["estimated_value"])
            weights.append(0.15)  # Cost approach (least reliable)
        
        if not values:
            return {"error": "No valid valuations to reconcile"}
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w/total_weight for w in weights]
        
        # Weighted average
        reconciled_value = sum(v * w for v, w in zip(values, normalized_weights))
        
        # Value range
        min_val = min(values)
        max_val = max(values)
        
        return {
            "reconciled_value": round(reconciled_value, 0),
            "value_range": {
                "low": round(min_val, 0),
                "high": round(max_val, 0)
            },
            "methods_used": len(values),
            "weights": {
                "comparable_sales": "50%" if comp_value else "0%",
                "income_capitalization": "35%" if income_value else "0%",
                "cost_approach": "15%" if cost_value else "0%"
            },
            "confidence": "HIGH" if len(values) >= 3 else "MODERATE" if len(values) == 2 else "LOW"
        }
    
    def investment_analysis(self, property: Property,
                           purchase_price: float,
                           annual_rent: float,
                           expenses: float,
                           holding_period: int = 5,
                           appreciation_rate: float = 0.03) -> Dict:
        """Analyze property as investment"""
        # Initial investment
        down_payment = purchase_price * 0.25
        closing_costs = purchase_price * 0.03
        initial_investment = down_payment + closing_costs
        
        # Annual cash flows
        noi = annual_rent - expenses
        mortgage = (purchase_price * 0.75) * 0.045  # Simplified
        annual_cash_flow = noi - mortgage
        
        # Projected sale
        future_value = purchase_price * ((1 + appreciation_rate) ** holding_period)
        selling_costs = future_value * 0.06
        loan_balance = (purchase_price * 0.75) - (mortgage * holding_period * 0.3)  # Rough
        net_sale_proceeds = future_value - selling_costs - loan_balance
        
        # Total return
        total_cash_flows = annual_cash_flow * holding_period
        total_profit = total_cash_flows + net_sale_proceeds - down_payment
        total_return_pct = (total_profit / initial_investment) * 100
        
        # IRR approximation
        irr = (total_return_pct / holding_period)
        
        return {
            "initial_investment": round(initial_investment, 0),
            "annual_cash_flow": round(annual_cash_flow, 0),
            "projected_sale_price": round(future_value, 0),
            "net_sale_proceeds": round(net_sale_proceeds, 0),
            "total_return": round(total_profit, 0),
            "total_return_pct": round(total_return_pct, 1),
            "annualized_return_pct": round(irr, 2),
            "cap_rate_at_purchase": round((noi / purchase_price) * 100, 2),
            "cash_on_cash_return": round((annual_cash_flow / initial_investment) * 100, 2),
            "recommendation": "BUY" if irr > 12 else "HOLD" if irr > 8 else "PASS"
        }
