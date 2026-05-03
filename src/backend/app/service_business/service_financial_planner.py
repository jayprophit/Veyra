"""
Service Business Financial Planner
===================================
Comprehensive financial planning for all service businesses
Cash flow, profit forecasting, tax planning for service professionals
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from enum import Enum
import numpy as np


class ServiceType(Enum):
    PROFESSIONAL = "professional"  # Lawyers, accountants, consultants
    CREATIVE = "creative"  # Designers, writers, photographers
    TECHNICAL = "technical"  # IT, engineering
    PERSONAL = "personal"  # Beauty, wellness, fitness
    HOME = "home"  # Cleaning, organizing, maintenance
    EVENT = "event"  # Planning, catering, entertainment


@dataclass
class ServiceBusiness:
    business_name: str
    owner_name: str
    service_type: str
    years_in_operation: int
    
    # Monthly metrics
    avg_monthly_revenue: float
    revenue_growth_rate: float  # monthly
    
    # Cost structure
    fixed_costs_monthly: float  # Rent, insurance, subscriptions
    variable_cost_pct: float  # % of revenue
    owner_draw_monthly: float
    
    # Staffing
    num_employees: int
    avg_employee_cost_monthly: float


class ServiceBusinessFinancialPlanner:
    """Financial planning for service-based businesses"""
    
    # Industry benchmarks by service type
    BENCHMARKS = {
        'professional': {
            'target_margin': 0.35,
            'avg_hourly_rate': 150,
            'billable_hours_target': 25,  # per week
            'overhead_pct': 0.25
        },
        'creative': {
            'target_margin': 0.40,
            'avg_project_value': 2500,
            'overhead_pct': 0.20
        },
        'technical': {
            'target_margin': 0.30,
            'avg_hourly_rate': 125,
            'billable_hours_target': 30,
            'overhead_pct': 0.15
        },
        'personal': {
            'target_margin': 0.45,
            'avg_transaction': 85,
            'overhead_pct': 0.30
        },
        'home': {
            'target_margin': 0.30,
            'avg_job_value': 350,
            'overhead_pct': 0.25
        },
        'event': {
            'target_margin': 0.25,
            'avg_event_value': 5000,
            'overhead_pct': 0.35
        }
    }
    
    # Tax brackets (simplified)
    TAX_BRACKETS = [
        (0, 11000, 0.10),
        (11000, 44725, 0.12),
        (44725, 95375, 0.22),
        (95375, 182100, 0.24),
        (182100, 231250, 0.32),
        (231250, 578125, 0.35),
        (578125, float('inf'), 0.37)
    ]
    
    def __init__(self):
        self.businesses: List[ServiceBusiness] = []
    
    def add_business(self, business: ServiceBusiness):
        """Add service business for planning"""
        self.businesses.append(business)
    
    def generate_cash_flow_forecast(self, business: ServiceBusiness,
                                     months: int = 12) -> Dict:
        """Generate cash flow forecast"""
        
        projections = []
        cumulative_cash = 0
        
        for month in range(1, months + 1):
            # Revenue (with growth)
            monthly_revenue = business.avg_monthly_revenue * (
                (1 + business.revenue_growth_rate) ** month
            )
            
            # Variable costs
            variable_costs = monthly_revenue * business.variable_cost_pct
            
            # Total costs
            total_costs = business.fixed_costs_monthly + variable_costs
            
            # Staff costs
            staff_costs = business.num_employees * business.avg_employee_cost_monthly
            
            # Net before owner draw
            net_operating = monthly_revenue - total_costs - staff_costs
            
            # Owner draw
            owner_draw = min(business.owner_draw_monthly, net_operating * 0.8)
            
            # Cash flow
            cash_flow = net_operating - owner_draw
            cumulative_cash += cash_flow
            
            projections.append({
                'month': month,
                'revenue': round(monthly_revenue, 2),
                'fixed_costs': round(business.fixed_costs_monthly, 2),
                'variable_costs': round(variable_costs, 2),
                'staff_costs': round(staff_costs, 2),
                'net_operating': round(net_operating, 2),
                'owner_draw': round(owner_draw, 2),
                'cash_flow': round(cash_flow, 2),
                'cumulative_cash': round(cumulative_cash, 2)
            })
        
        return {
            'business_name': business.business_name,
            'forecast_period_months': months,
            'total_projected_revenue': round(sum(p['revenue'] for p in projections), 2),
            'total_projected_cash_flow': round(sum(p['cash_flow'] for p in projections), 2),
            'ending_cash_position': round(cumulative_cash, 2),
            'avg_monthly_cash_flow': round(cumulative_cash / months, 2),
            'monthly_projections': projections,
            'breakeven_month': self._find_breakeven(projections)
        }
    
    def _find_breakeven(self, projections: List[Dict]) -> Optional[int]:
        """Find month where cumulative cash turns positive"""
        for p in projections:
            if p['cumulative_cash'] > 0:
                return p['month']
        return None
    
    def calculate_tax_estimate(self, business: ServiceBusiness) -> Dict:
        """Calculate estimated tax liability"""
        
        # Annual projections
        annual_revenue = business.avg_monthly_revenue * 12 * (
            (1 + business.revenue_growth_rate) ** 6  # Average growth over year
        )
        
        # Deductible expenses
        annual_fixed = business.fixed_costs_monthly * 12
        annual_variable = annual_revenue * business.variable_cost_pct
        annual_staff = business.num_employees * business.avg_employee_cost_monthly * 12
        
        # Additional deductions (estimated)
        home_office_pct = 0.20  # Assume 20% home office
        vehicle_expense = 6000 if business.service_type in ['home', 'personal'] else 3000
        equipment_depreciation = 5000
        professional_fees = 3000
        insurance = business.fixed_costs_monthly * 12 * 0.30
        
        total_deductions = (
            annual_fixed + annual_variable + annual_staff +
            vehicle_expense + equipment_depreciation +
            professional_fees + insurance
        )
        
        # Self-employment tax calculation
        net_profit = annual_revenue - total_deductions
        se_tax_base = min(net_profit, 160200)  # Social Security cap
        se_tax = se_tax_base * 0.9235 * 0.153  # 15.3% on 92.35% of income
        
        # Deductible portion of SE tax
        se_tax_deduction = se_tax * 0.50
        
        # Taxable income
        taxable_income = net_profit - se_tax_deduction
        
        # Federal income tax (simplified)
        federal_tax = self._calculate_federal_tax(taxable_income)
        
        # State tax estimate (average 5%)
        state_tax = taxable_income * 0.05
        
        total_tax = se_tax + federal_tax + state_tax
        effective_rate = total_tax / annual_revenue if annual_revenue > 0 else 0
        
        return {
            'annual_revenue': round(annual_revenue, 2),
            'total_deductions': round(total_deductions, 2),
            'net_profit': round(net_profit, 2),
            'self_employment_tax': round(se_tax, 2),
            'federal_income_tax': round(federal_tax, 2),
            'state_tax_estimate': round(state_tax, 2),
            'total_tax_liability': round(total_tax, 2),
            'effective_tax_rate_pct': round(effective_rate * 100, 1),
            'quarterly_estimate': round(total_tax / 4, 2),
            'after_tax_income': round(net_profit - total_tax, 2)
        }
    
    def _calculate_federal_tax(self, taxable_income: float) -> float:
        """Calculate federal tax using brackets"""
        tax = 0
        remaining = taxable_income
        
        for low, high, rate in self.TAX_BRACKETS:
            bracket_income = min(remaining, high - low)
            if bracket_income > 0:
                tax += bracket_income * rate
                remaining -= bracket_income
            if remaining <= 0:
                break
        
        return tax
    
    def get_health_check(self, business: ServiceBusiness) -> Dict:
        """Get business health assessment"""
        
        benchmark = self.BENCHMARKS.get(business.service_type, {})
        
        # Current metrics
        current_margin = 1 - (business.fixed_costs_monthly + 
                             (business.avg_monthly_revenue * business.variable_cost_pct)) / business.avg_monthly_revenue
        
        target_margin = benchmark.get('target_margin', 0.30)
        
        # Cash cushion
        monthly_expenses = (
            business.fixed_costs_monthly + 
            business.owner_draw_monthly +
            (business.num_employees * business.avg_employee_cost_monthly)
        )
        cash_cushion_months = business.avg_monthly_revenue / monthly_expenses if monthly_expenses > 0 else 0
        
        # Growth rate health
        growth_healthy = business.revenue_growth_rate > 0.005  # >0.5% monthly
        
        return {
            'business_name': business.business_name,
            'service_type': business.service_type,
            'years_in_operation': business.years_in_operation,
            'current_profit_margin_pct': round(current_margin * 100, 1),
            'target_margin_pct': round(target_margin * 100, 1),
            'margin_status': 'HEALTHY' if current_margin > target_margin else 'BELOW_TARGET',
            'cash_cushion_months': round(cash_cushion_months, 1),
            'cash_status': 'STRONG' if cash_cushion_months > 3 else 'ADEQUATE' if cash_cushion_months > 1.5 else 'TIGHT',
            'growth_trend': 'GROWING' if growth_healthy else 'FLAT',
            'overall_health': self._overall_health_rating(current_margin, cash_cushion_months, growth_healthy),
            'priority_actions': self._priority_actions(current_margin, cash_cushion_months, business)
        }
    
    def _overall_health_rating(self, margin: float, cash_months: float, growth: bool) -> str:
        """Calculate overall health rating"""
        score = 50
        
        if margin > 0.30:
            score += 25
        elif margin > 0.20:
            score += 10
        
        if cash_months > 3:
            score += 20
        elif cash_months > 2:
            score += 10
        
        if growth:
            score += 5
        
        if score >= 80:
            return 'EXCELLENT'
        elif score >= 65:
            return 'GOOD'
        elif score >= 45:
            return 'FAIR'
        else:
            return 'NEEDS_ATTENTION'
    
    def _priority_actions(self, margin: float, cash_months: float, 
                         business: ServiceBusiness) -> List[str]:
        """Generate priority action items"""
        actions = []
        
        if margin < 0.20:
            actions.append("URGENT: Review pricing - margins critically low")
            actions.append("URGENT: Audit all variable costs for savings")
        
        if cash_months < 1.5:
            actions.append("PRIORITY: Build cash reserve - 3+ months expenses")
            actions.append("PRIORITY: Secure line of credit for emergencies")
        
        if business.years_in_operation < 2:
            actions.append("FOCUS: Customer acquisition - build client base")
        
        if business.num_employees > 0 and business.avg_employee_cost_monthly > 5000:
            actions.append("REVIEW: Staff efficiency and utilization rates")
        
        if not actions:
            actions.append("MAINTAIN: Continue current strategy")
            actions.append("OPTIMIZE: Consider growth investments")
        
        return actions
    
    def get_optimization_recommendations(self, business: ServiceBusiness) -> Dict:
        """Get optimization recommendations"""
        
        benchmark = self.BENCHMARKS.get(business.service_type, {})
        
        recommendations = {
            'pricing': [],
            'costs': [],
            'operations': [],
            'growth': []
        }
        
        # Pricing recommendations
        if 'avg_hourly_rate' in benchmark:
            target_rate = benchmark['avg_hourly_rate']
            recommendations['pricing'].append(
                f"Target hourly rate: ${target_rate}. Review current rates."
            )
        
        if business.revenue_growth_rate < 0.005:
            recommendations['pricing'].append(
                "Implement annual rate increases (3-5%)"
            )
        
        # Cost recommendations
        current_overhead = business.fixed_costs_monthly / business.avg_monthly_revenue
        target_overhead = benchmark.get('overhead_pct', 0.25)
        
        if current_overhead > target_overhead + 0.05:
            recommendations['costs'].append(
                f"Overhead at {current_overhead*100:.0f}%. Target: {target_overhead*100:.0f}%. Review fixed costs."
            )
        
        # Operations
        if business.num_employees > 0:
            recommendations['operations'].append(
                "Track employee utilization - target 80%+ billable"
            )
        
        # Growth
        if business.years_in_operation > 2 and business.revenue_growth_rate > 0.01:
            recommendations['growth'].append(
                "Consider expansion: add staff or new service lines"
            )
        
        return recommendations


# Usage
def plan_service_business(name: str, service_type: str,
                          monthly_revenue: float, fixed_costs: float,
                          variable_pct: float, growth_rate: float = 0.01) -> Dict:
    """Quick service business planning"""
    planner = ServiceBusinessFinancialPlanner()
    
    business = ServiceBusiness(
        business_name=name,
        owner_name="Owner",
        service_type=service_type,
        years_in_operation=3,
        avg_monthly_revenue=monthly_revenue,
        revenue_growth_rate=growth_rate,
        fixed_costs_monthly=fixed_costs,
        variable_cost_pct=variable_pct,
        owner_draw_monthly=monthly_revenue * 0.30,
        num_employees=1 if monthly_revenue > 15000 else 0,
        avg_employee_cost_monthly=4000
    )
    
    planner.add_business(business)
    
    return {
        'health_check': planner.get_health_check(business),
        'cash_flow_forecast': planner.generate_cash_flow_forecast(business, 12),
        'tax_estimate': planner.calculate_tax_estimate(business),
        'optimization': planner.get_optimization_recommendations(business)
    }


def get_business_health(name: str, service_type: str, 
                       revenue: float, costs: float) -> Dict:
    """Get quick health check"""
    planner = ServiceBusinessFinancialPlanner()
    
    business = ServiceBusiness(
        business_name=name,
        owner_name="Owner",
        service_type=service_type,
        years_in_operation=3,
        avg_monthly_revenue=revenue,
        revenue_growth_rate=0.01,
        fixed_costs_monthly=costs * 0.6,
        variable_cost_pct=0.30,
        owner_draw_monthly=revenue * 0.25,
        num_employees=0,
        avg_employee_cost_monthly=0
    )
    
    return planner.get_health_check(business)
