"""Team Valuation - Professional sports franchise analytics"""
from typing import Dict

class TeamValuation:
    """Value professional sports franchises"""
    
    def franchise_dcf(self, annual_revenue: float,
                      growth_rate: float,
                      operating_margin: float,
                      discount_rate: float = 0.08) -> Dict:
        """DCF valuation for sports franchise"""
        # Sports teams have unique characteristics - brand premium, scarcity
        terminal_multiple = 12  # Higher than typical businesses
        
        # 10-year projection
        cash_flows = []
        for year in range(1, 11):
            revenue = annual_revenue * ((1 + growth_rate) ** year)
            ebitda = revenue * operating_margin
            cash_flows.append(ebitda)
        
        # Terminal value
        terminal_value = cash_flows[-1] * terminal_multiple
        
        # Discount
        npv = sum(cf / ((1 + discount_rate) ** (i+1)) for i, cf in enumerate(cash_flows))
        npv += terminal_value / ((1 + discount_rate) ** 10)
        
        return {
            "annual_revenue": annual_revenue,
            "operating_margin": operating_margin,
            "enterprise_value": round(npv, 0),
            "revenue_multiple": round(npv / annual_revenue, 1),
            "scarcity_premium": "20-40% above DCF",
            "intangible_value": round(npv * 0.3, 0)  # Brand, history, fanbase
        }
    
    def media_rights_value(self, viewership_millions: float,
                         contract_years: int,
                         annual_rights_fee: float) -> Dict:
        """Value media rights contracts"""
        cost_per_viewer = annual_rights_fee / (viewership_millions * 1e6)
        
        return {
            "viewership_millions": viewership_millions,
            "annual_rights_fee": annual_rights_fee,
            "cost_per_viewer": round(cost_per_viewer, 2),
            "contract_value": annual_rights_fee * contract_years,
            "value_per_year": round(annual_rights_fee / viewership_millions, 2)
        }
    
    def stadium_economics(self, capacity: int,
                         avg_ticket_price: float,
                         games_per_year: int,
                         naming_rights: float) -> Dict:
        """Analyze stadium revenue economics"""
        ticket_revenue = capacity * avg_ticket_price * games_per_year * 0.85  # 85% occupancy
        concession_estimate = ticket_revenue * 0.3
        
        return {
            "capacity": capacity,
            "ticket_revenue": round(ticket_revenue, 0),
            "concession_estimate": round(concession_estimate, 0),
            "naming_rights_annual": naming_rights,
            "total_annual_revenue": round(ticket_revenue + concession_estimate + naming_rights, 0),
            "revenue_per_seat": round((ticket_revenue + concession_estimate) / capacity, 0)
        }
