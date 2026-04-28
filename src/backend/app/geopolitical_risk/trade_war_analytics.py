"""Trade War Analytics"""
from typing import Dict

class TradeWarAnalytics:
    def tariff_impact(self, import_volume: float, tariff_rate: float, pass_through: float) -> Dict:
        tariff_revenue = import_volume * tariff_rate
        consumer_cost = tariff_revenue * pass_through
        return {"tariff_revenue": tariff_revenue, "consumer_burden": consumer_cost}
    
    def supply_chain_relocation(self, current_cost: float, alternative_cost: float, switching_cost: float) -> Dict:
        savings = current_cost - alternative_cost
        return {"net_savings": savings - switching_cost, "payback_years": switching_cost / savings if savings > 0 else float('inf')}
