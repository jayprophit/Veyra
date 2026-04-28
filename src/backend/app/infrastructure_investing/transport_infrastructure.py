"""Transport Infrastructure"""
from typing import Dict

class TransportInfrastructure:
    """Toll roads, bridges, tunnels, ports"""
    
    def toll_road_dcf(self, daily_traffic: int, toll_rate: float, 
                     operating_cost_ratio: float, years: int) -> Dict:
        """DCF valuation for toll road concession"""
        annual_revenue = daily_traffic * toll_rate * 365
        annual_cost = annual_revenue * operating_cost_ratio
        net_cash_flow = annual_revenue - annual_cost
        
        # Concession DCF
        discount_rate = 0.08
        dcf_value = sum(net_cash_flow / ((1 + discount_rate) ** y) for y in range(1, years + 1))
        
        return {
            "annual_revenue": annual_revenue,
            "net_cash_flow": net_cash_flow,
            "concession_value": dcf_value,
            "traffic_multiple": daily_traffic * 1000
        }
    
    def port_throughput_value(self, teu_capacity: int, utilization: float,
                              handling_fee: float) -> Dict:
        """Container port valuation"""
        throughput = teu_capacity * utilization
        revenue = throughput * handling_fee
        return {"annual_revenue": revenue, "throughput": throughput, "capacity_value": teu_capacity * 50}
