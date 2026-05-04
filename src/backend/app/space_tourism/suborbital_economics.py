"""Suborbital Space Tourism Economics"""
from typing import Dict

class SuborbitalEconomics:
    """Analyze suborbital tourism market and investments"""
    
    def __init__(self, vehicle: str = "spaceship_two"):
        self.vehicle = vehicle
        self.providers = {
            "virgin_galactic": {"ticket_price": 450000, "capacity": 6, "development_cost": 1e9},
            "blue_origin": {"ticket_price": 500000, "capacity": 6, "development_cost": 2.5e9},
            "space_perspective": {"ticket_price": 125000, "capacity": 8, "development_cost": 0.5e9}
        }
    
    def flight_economics(self, flights_per_year: int = 50) -> Dict:
        provider = self.providers.get("virgin_galactic")
        
        revenue_per_flight = provider["ticket_price"] * provider["capacity"]
        annual_revenue = revenue_per_flight * flights_per_year
        
        # Costs
        vehicle_prep = 50000
        fuel = 30000
        crew = 40000
        maintenance = 100000
        insurance = 50000
        
        cost_per_flight = vehicle_prep + fuel + crew + maintenance + insurance
        annual_cost = cost_per_flight * flights_per_year
        
        annual_profit = annual_revenue - annual_cost
        
        return {
            "revenue_per_flight": revenue_per_flight,
            "cost_per_flight": cost_per_flight,
            "profit_per_flight": revenue_per_flight - cost_per_flight,
            "annual_revenue": annual_revenue,
            "annual_profit": annual_profit,
            "flights_per_year": flights_per_year,
            "margin_pct": round((revenue_per_flight - cost_per_flight) / revenue_per_flight * 100, 1)
        }
    
    def market_sizing(self, wealth_threshold_usd: int = 5e6) -> Dict:
        # High net worth individuals globally
        hnw_over_5m = 3.0e6  # 3 million people
        
        # Addressable market (interested in space)
        interest_rate = 0.05  # 5%
        addressable = hnw_over_5m * interest_rate
        
        # Willing to pay at current prices
        willingness = 0.20  # 20% of interested
        total_addressable = addressable * willingness
        
        # Market value
        avg_ticket = 350000
        tam_value = total_addressable * avg_ticket
        
        return {
            "global_hnw_over_5m": int(hnw_over_5m),
            "interested_in_space": int(addressable),
            "willing_to_pay": int(total_addressable),
            "tam_usd_billions": round(tam_value / 1e9, 1),
            "avg_ticket_price": avg_ticket
        }
    
    def fleet_investment(self, vehicle_count: int = 5) -> Dict:
        provider = self.providers.get("virgin_galactic")
        
        # Vehicle costs
        vehicle_unit_cost = 50e6
        fleet_cost = vehicle_count * vehicle_unit_cost
        
        # Development amortization
        dev_cost = provider["development_cost"]
        amortization_years = 10
        annual_dev_charge = dev_cost / amortization_years
        
        # Operations
        per_vehicle_flights = 50
        total_flights = vehicle_count * per_vehicle_flights
        
        flight_econ = self.flight_economics(per_vehicle_flights)
        annual_profit = flight_econ["profit_per_flight"] * total_flights
        
        # Total investment
        total_investment = fleet_cost + dev_cost
        
        # ROI
        simple_roi = annual_profit / total_investment * 100
        payback = total_investment / annual_profit if annual_profit > 0 else float('inf')
        
        return {
            "fleet_cost_millions": fleet_cost / 1e6,
            "development_cost_millions": dev_cost / 1e6,
            "total_investment_millions": total_investment / 1e6,
            "annual_profit_millions": annual_profit / 1e6,
            "roi_pct": round(simple_roi, 1),
            "payback_years": round(payback, 1),
            "vehicle_count": vehicle_count
        }
    
    def vs_travel_alternatives(self) -> Dict:
        return {
            "suborbital_space": {
                "price": 450000,
                "duration": "10-15 minutes",
                "experience": "Weightlessness, Earth view"
            },
            "luxury_cruise": {
                "price": 50000,
                "duration": "7 days",
                "experience": "Traditional luxury"
            },
            "antarctica_expedition": {
                "price": 30000,
                "duration": "10 days",
                "experience": "Extreme environment"
            },
            "private_island": {
                "price": 100000,
                "duration": "1 week",
                "experience": "Exclusive relaxation"
            },
            "premium_pricing_factor": 5  # Space costs 5x vs alternatives
        }
