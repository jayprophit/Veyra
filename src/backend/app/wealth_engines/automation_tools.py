"""Passive Automation - Tools for passive income automation"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AutomationTool:
    tool_id: str
    tool_name: str
    income_type: str
    monthly_income: float
    automation_cost: float
    time_saved_hours: float

class PassiveAutomation:
    def __init__(self):
        self.tools: List[AutomationTool] = []
    
    def add(self, t: AutomationTool):
        self.tools.append(t)
    
    def calculate_roi(self, t: AutomationTool) -> float:
        if t.automation_cost == 0:
            return float('inf')
        annual_benefit = t.monthly_income * 12
        return (annual_benefit - t.automation_cost) / t.automation_cost * 100
    
    def get_summary(self) -> Dict:
        if not self.tools:
            return {'status': 'NO_TOOLS'}
        
        by_type = {}
        for t in self.tools:
            it = t.income_type
            if it not in by_type:
                by_type[it] = {'tools': 0, 'monthly_income': 0}
            by_type[it]['tools'] += 1
            by_type[it]['monthly_income'] += t.monthly_income
        
        return {
            'tools': len(self.tools),
            'total_monthly_income': round(sum(t.monthly_income for t in self.tools), 2),
            'total_automation_cost': round(sum(t.automation_cost for t in self.tools), 2),
            'total_time_saved': round(sum(t.time_saved_hours for t in self.tools), 1),
            'by_income_type': by_type
        }
