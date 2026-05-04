"""Battery Energy Storage System (BESS) Economics"""
from typing import Dict

class BESSMain:
    """Analyze grid-scale battery storage investments"""
    
    def __init__(self, capacity_mwh: float, duration_hours: float = 4):
        self.capacity_mwh = capacity_mwh
        self.duration = duration_hours
        self.power_mw = capacity_mwh / duration_hours
    
    def capex_analysis(self, battery_type: str = "lithium_ion") -> Dict:
        costs_per_kwh = {
            "lithium_ion": 300,
            "lithium_ferro_phosphate": 280,
            "solid_state": 450,
            "sodium_ion": 150,
            "flow_battery": 400
        }
        
        cost_per_kwh = costs_per_kwh.get(battery_type, 300)
        total_kwh = self.capacity_mwh * 1000
        
        battery_cost = total_kwh * cost_per_kwh
        
        # Balance of system (BOS)
        inverter = 50 * self.power_mw * 1000
        containers = 200000
        installation = battery_cost * 0.15
        soft_costs = battery_cost * 0.10
        
        total_capex = battery_cost + inverter + containers + installation + soft_costs
        
        return {
            "total_capex": round(total_capex, 0),
            "battery_cost": round(battery_cost, 0),
            "bos_cost": round(inverter + containers + installation + soft_costs, 0),
            "cost_per_kwh_installed": round(total_capex / total_kwh, 0),
            "battery_type": battery_type
        }
    
    def revenue_streams(self, cycles_per_year: int = 300) -> Dict:
        # Energy arbitrage
        spread = 50  # $/MWh buy/sell spread
        arbitrage = self.capacity_mwh * cycles_per_year * spread * 0.85  # 85% efficiency
        
        # Ancillary services
        frequency_regulation = self.power_mw * 8760 * 10  # $10/kW-year
        capacity_payment = self.power_mw * 50000  # $50/kW-year
        
        # Demand charge reduction (behind meter)
        demand_reduction = self.power_mw * 200000  # Industrial demand charge avoidance
        
        total_revenue = arbitrage + frequency_regulation + capacity_payment
        
        return {
            "energy_arbitrage": round(arbitrage, 0),
            "ancillary_services": round(frequency_regulation + capacity_payment, 0),
            "total_annual_revenue": round(total_revenue, 0),
            "revenue_per_kwh": round(total_revenue / (self.capacity_mwh * 1000), 2),
            "cycles_per_year": cycles_per_year
        }
    
    def project_returns(self, battery_type: str = "lithium_ion") -> Dict:
        capex = self.capex_analysis(battery_type)["total_capex"]
        revenue = self.revenue_streams()["total_annual_revenue"]
        
        # O&M costs
        om_fixed = self.power_mw * 10000  # $10/kW-year
        om_variable = revenue * 0.02
        total_om = om_fixed + om_variable
        
        # Battery replacement at year 10
        replacement_cost = capex * 0.60
        
        # Simple 20-year analysis
        annual_ebitda = revenue - total_om
        
        # Simple payback
        payback = capex / annual_ebitda
        
        # IRR estimation
        years = 20
        cash_flows = [-capex] + [annual_ebitda] * 10 + [annual_ebitda - replacement_cost] + [annual_ebitda] * 9
        
        return {
            "capex": round(capex, 0),
            "annual_ebitda": round(annual_ebitda, 0),
            "simple_payback_years": round(payback, 1),
            "irr_estimate_pct": round((annual_ebitda / capex) * 100, 1),
            "lcoe_usd_per_mwh": round(capex / (self.capacity_mwh * years), 0),
            "battery_replacement_year": 10
        }
    
    def vs_grid_alternatives(self, gas_peaker_cost_per_kw: float = 800) -> Dict:
        # Compare to gas peaker
        gas_capex = self.power_mw * 1000 * gas_peaker_cost_per_kw
        storage_capex = self.capex_analysis()["total_capex"]
        
        # Gas has fuel costs, storage doesn't
        gas_annual_fuel = self.power_mw * 8760 * 0.10 * 50  # 10% CF, $50/MWh fuel
        storage_annual_fuel = 0
        
        return {
            "bess_capex": round(storage_capex, 0),
            "gas_peaker_capex": round(gas_capex, 0),
            "capex_premium_pct": round((storage_capex / gas_capex - 1) * 100, 0),
            "gas_annual_fuel_cost": round(gas_annual_fuel, 0),
            "storage_fuel_cost": 0,
            "operational_advantage": "No fuel cost, instant response"
        }
