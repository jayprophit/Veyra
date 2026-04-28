"""Digital Infrastructure"""
from typing import Dict

class DigitalInfrastructure:
    def data_center_valuation(self, mw_capacity: float, utilization: float, rate_per_mw: float) -> Dict:
        revenue = mw_capacity * utilization * rate_per_mw * 12
        return {"annual_revenue": revenue, "per_mw_value": rate_per_mw * 100}
    
    def cell_tower_lease(self, tenants: int, rent_per_tenant: float) -> Dict:
        return {"annual_rent": tenants * rent_per_tenant, "tenant_count": tenants}
