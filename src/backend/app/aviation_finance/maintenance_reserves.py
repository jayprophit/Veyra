"""Maintenance Reserves"""
from typing import Dict

class MaintenanceReserves:
    """Calculate maintenance reserves"""
    
    def engine_reserve(self, cycles_per_year: int, 
                      cost_per_cycle: float = 500) -> Dict:
        """Engine maintenance reserve"""
        annual_reserve = cycles_per_year * cost_per_cycle
        return {"annual_reserve": annual_reserve, "per_cycle": cost_per_cycle}
    
    def airframe_check(self, hours_per_year: float, 
                       rate_per_hour: float = 200) -> Dict:
        """Airframe maintenance reserve"""
        annual = hours_per_year * rate_per_hour
        return {"annual_reserve": annual, "per_hour": rate_per_hour}
