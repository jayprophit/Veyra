"""Robotics ROI - Return on investment analysis for robotic automation"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class RobotDeployment:
    deployment_id: str
    robot_type: str  # 'industrial', 'warehouse', 'agricultural', 'service'
    purchase_cost: float
    installation_cost: float
    annual_maintenance: float
    labor_hours_saved_per_year: float
    labor_cost_per_hour: float
    productivity_gain_pct: float
    deployment_date: datetime

class RoboticsROI:
    """Calculate ROI for robotic automation investments"""
    
    def __init__(self, analysis_years: int = 5):
        self.deployments: List[RobotDeployment] = []
        self.analysis_years = analysis_years
    
    def add_deployment(self, deployment: RobotDeployment):
        self.deployments.append(deployment)
    
    def calculate_deployment_roi(self, deployment: RobotDeployment) -> Dict:
        initial_investment = deployment.purchase_cost + deployment.installation_cost
        annual_savings = (deployment.labor_hours_saved_per_year * deployment.labor_cost_per_hour)
        annual_net_benefit = annual_savings - deployment.annual_maintenance
        
        # Simple ROI calculation
        if annual_net_benefit > 0:
            payback_years = initial_investment / annual_net_benefit
        else:
            payback_years = float('inf')
        
        # Total benefit over analysis period
        total_benefit = annual_net_benefit * self.analysis_years
        total_roi = ((total_benefit - initial_investment) / initial_investment * 100) if initial_investment else 0
        
        return {
            'deployment_id': deployment.deployment_id,
            'robot_type': deployment.robot_type,
            'initial_investment': round(initial_investment, 2),
            'annual_savings': round(annual_savings, 2),
            'annual_maintenance': round(deployment.annual_maintenance, 2),
            'annual_net_benefit': round(annual_net_benefit, 2),
            'payback_period_years': round(payback_years, 1),
            f'{self.analysis_years}_year_roi_pct': round(total_roi, 1),
            'productivity_gain_pct': deployment.productivity_gain_pct
        }
    
    def get_portfolio_summary(self) -> Dict:
        if not self.deployments:
            return {'status': 'NO_DEPLOYMENTS'}
        
        analyses = [self.calculate_deployment_roi(d) for d in self.deployments]
        total_investment = sum(a['initial_investment'] for a in analyses)
        total_annual_benefit = sum(a['annual_net_benefit'] for a in analyses)
        
        by_type = {}
        for a in analyses:
            t = a['robot_type']
            if t not in by_type:
                by_type[t] = {'count': 0, 'investment': 0, 'annual_benefit': 0}
            by_type[t]['count'] += 1
            by_type[t]['investment'] += a['initial_investment']
            by_type[t]['annual_benefit'] += a['annual_net_benefit']
        
        return {
            'total_deployments': len(self.deployments),
            'total_investment': round(total_investment, 2),
            'total_annual_benefit': round(total_annual_benefit, 2),
            'portfolio_payback_years': round(total_investment / total_annual_benefit, 1) if total_annual_benefit else 0,
            'by_robot_type': by_type,
            'deployment_details': analyses
        }
