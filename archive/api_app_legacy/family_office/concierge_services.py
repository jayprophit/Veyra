"""Concierge Services"""
from typing import Dict

class ConciergeServices:
    def service_budget(self, net_worth: float, service_tier: str) -> Dict:
        rates = {"essential": 0.001, "standard": 0.002, "premium": 0.005}
        rate = rates.get(service_tier, 0.002)
        budget = net_worth * rate
        return {"tier": service_tier, "annual_budget": budget, "rate": rate}
    
    def aircraft_management(self, aircraft_value: float, hours_flown: int) -> Dict:
        fixed_cost = aircraft_value * 0.10
        variable_cost = hours_flown * 3000
        return {"fixed": fixed_cost, "variable": variable_cost, "total": fixed_cost + variable_cost}
    
    def art_collection_mgmt(self, collection_value: float, pieces: int) -> Dict:
        insurance = collection_value * 0.005
        storage = pieces * 5000
        return {"insurance": insurance, "storage": storage, "total_annual": insurance + storage}
