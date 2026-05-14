"""Small Modular Reactor Economics"""
from typing import Dict

class SMREconomics:
    """Analyze SMR investments"""
    
    def __init__(self, capacity_mw: float, design: str = "PWR"):
        self.capacity = capacity_mw
        self.design = design  # PWR, BWR, HTGR, MSR
    
    def overnight_cost(self) -> Dict:
        costs_per_kw = {
            "PWR": 5000,
            "BWR": 5500,
            "HTGR": 6000,
            "MSR": 7000
        }
        cost_per_kw = costs_per_kw.get(self.design, 5500)
        total = self.capacity * 1000 * cost_per_kw
        
        return {
            "total_overnight_cost": round(total, 0),
            "cost_per_kw": cost_per_kw,
            "cost_per_mw": round(cost_per_kw * 1000, 0),
            "category": "SMR" if self.capacity < 300 else "Large Reactor"
        }
    
    def lcoe(self, capacity_factor: float = 90, construction_years: int = 4) -> Dict:
        overnight = self.overnight_cost()["total_overnight_cost"]
        
        # Overnight cost with interest during construction (IDC)
        idc_rate = 0.06
        idc_factor = ((1 + idc_rate) ** construction_years - 1) / idc_rate / construction_years if construction_years > 0 else 1
        total_capital = overnight * idc_factor
        
        # Fixed charges (capital recovery)
        fixed_charge_rate = 0.10  # 10% per year
        annual_fixed = total_capital * fixed_charge_rate
        
        # Fuel cost
        fuel_cost_per_mwh = 8
        
        # O&M
        om_fixed_per_kw = 200
        om_variable_per_mwh = 2
        
        annual_output = self.capacity * 8760 * (capacity_factor / 100)
        
        annual_fuel = annual_output * fuel_cost_per_mwh
        annual_om_fixed = self.capacity * 1000 * om_fixed_per_kw
        annual_om_var = annual_output * om_variable_per_mwh
        
        total_annual = annual_fixed + annual_fuel + annual_om_fixed + annual_om_var
        lcoe = total_annual / annual_output if annual_output > 0 else 0
        
        return {
            "lcoe_usd_per_mwh": round(lcoe, 2),
            "capacity_factor": capacity_factor,
            "annual_output_gwh": round(annual_output / 1000, 1),
            "capital_component": round(annual_fixed / total_annual * 100, 1),
            "fuel_component": round(annual_fuel / total_annual * 100, 1),
            "om_component": round((annual_om_fixed + annual_om_var) / total_annual * 100, 1)
        }
    
    def vs_gas_comparison(self, gas_price_per_mmbtu: float = 3.0) -> Dict:
        nuclear_lcoe = self.lcoe()["lcoe_usd_per_mwh"]
        
        # Gas plant economics
        gas_heat_rate = 7000  # Btu/kWh
        gas_var_cost = gas_heat_rate * gas_price_per_mmbtu / 1000
        gas_lcoe = gas_var_cost + 15  # $15/MWh fixed
        
        carbon_savings = 0.4 * 8760 * self.capacity * (self.lcoe()["capacity_factor"] / 100)  # tons CO2 avoided
        
        return {
            "nuclear_lcoe": nuclear_lcoe,
            "gas_ccgt_lcoe": round(gas_lcoe, 2),
            "nuclear_premium": round(nuclear_lcoe - gas_lcoe, 2),
            "annual_carbon_avoided_tons": round(carbon_savings, 0),
            "carbon_credit_revenue_50": round(carbon_savings * 50, 0)
        }
