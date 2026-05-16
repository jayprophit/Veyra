"""
Construction Industry Business Tracker
======================================
Track construction business income, projects, costs
General contracting, project management, subcontracting
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum


class ProjectType(Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    RENOVATION = "renovation"
    NEW_CONSTRUCTION = "new_construction"


class ProjectStatus(Enum):
    BIDDING = "bidding"
    CONTRACTED = "contracted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INVOICED = "invoiced"
    PAID = "paid"


@dataclass
class Project:
    project_id: str
    client_name: str
    project_type: str
    status: str
    contract_value: float
    start_date: date
    expected_completion: date
    actual_completion: Optional[date]
    materials_cost: float
    labor_cost: float
    subcontractor_cost: float
    overhead_allocated: float


@dataclass
class Bid:
    project_id: str
    client_name: str
    project_type: str
    bid_amount: float
    estimated_cost: float
    bid_date: date
    status: str  # 'pending', 'won', 'lost'


class ConstructionBusinessTracker:
    """Track construction business finances and projects"""
    
    # Industry benchmarks (as percentages)
    BENCHMARKS = {
        'gross_margin_target': 0.20,  # 20%
        'overhead_rate': 0.15,  # 15% of revenue
        'materials_pct': 0.40,  # 40% of revenue
        'labor_pct': 0.25,  # 25% of revenue
        'subcontractor_pct': 0.15,  # 15% of revenue
        'win_rate_target': 0.25  # Win 25% of bids
    }
    
    def __init__(self, company_name: str = "Construction Co"):
        self.company_name = company_name
        self.projects: List[Project] = []
        self.bids: List[Bid] = []
        self.monthly_overhead: float = 0
    
    def add_project(self, project: Project):
        """Add project to pipeline"""
        self.projects.append(project)
    
    def add_bid(self, bid: Bid):
        """Add bid to tracking"""
        self.bids.append(bid)
    
    def calculate_project_profitability(self, project: Project) -> Dict:
        """Calculate profitability for a project"""
        
        total_costs = (
            project.materials_cost + 
            project.labor_cost + 
            project.subcontractor_cost + 
            project.overhead_allocated
        )
        
        gross_profit = project.contract_value - total_costs
        gross_margin = gross_profit / project.contract_value if project.contract_value > 0 else 0
        
        # Days to complete
        if project.actual_completion:
            days_taken = (project.actual_completion - project.start_date).days
        else:
            days_taken = (date.today() - project.start_date).days
        
        expected_days = (project.expected_completion - project.start_date).days
        schedule_variance = days_taken - expected_days
        
        return {
            'project_id': project.project_id,
            'client': project.client_name,
            'contract_value': round(project.contract_value, 2),
            'total_costs': round(total_costs, 2),
            'gross_profit': round(gross_profit, 2),
            'gross_margin_pct': round(gross_margin * 100, 1),
            'margin_status': 'PROFITABLE' if gross_margin > 0.15 else 'BREAK_EVEN' if gross_margin > 0 else 'LOSS',
            'cost_breakdown': {
                'materials': round(project.materials_cost, 2),
                'labor': round(project.labor_cost, 2),
                'subcontractors': round(project.subcontractor_cost, 2),
                'overhead': round(project.overhead_allocated, 2)
            },
            'schedule_performance': {
                'expected_days': expected_days,
                'actual_days': days_taken,
                'variance': schedule_variance,
                'on_time': schedule_variance <= 0
            }
        }
    
    def get_backlog_analysis(self) -> Dict:
        """Analyze current project backlog"""
        active_projects = [p for p in self.projects 
                          if p.status in ['contracted', 'in_progress']]
        
        total_backlog_value = sum(p.contract_value for p in active_projects)
        
        # Revenue recognition (simplified)
        completed = [p for p in self.projects if p.status == 'completed']
        recognized_revenue = sum(p.contract_value for p in completed)
        
        # Pipeline
        bidding = [b for b in self.bids if b.status == 'pending']
        pipeline_value = sum(b.bid_amount for b in bidding)
        
        return {
            'active_projects': len(active_projects),
            'backlog_value': round(total_backlog_value, 2),
            'completed_ytd_revenue': round(recognized_revenue, 2),
            'pipeline_bids': len(bidding),
            'pipeline_value': round(pipeline_value, 2),
            'months_of_work': round(total_backlog_value / self._avg_monthly_revenue(), 1) if self._avg_monthly_revenue() > 0 else 0
        }
    
    def _avg_monthly_revenue(self) -> float:
        """Calculate average monthly revenue from completed projects"""
        completed = [p for p in self.projects if p.status == 'completed']
        if not completed:
            return 0
        
        total = sum(p.contract_value for p in completed)
        # Assume avg project takes 3 months
        return total / (len(completed) * 3)
    
    def calculate_bid_performance(self) -> Dict:
        """Analyze bidding performance"""
        if not self.bids:
            return {'error': 'No bids tracked'}
        
        total_bids = len(self.bids)
        won = len([b for b in self.bids if b.status == 'won'])
        lost = len([b for b in self.bids if b.status == 'lost'])
        pending = len([b for b in self.bids if b.status == 'pending'])
        
        win_rate = won / (won + lost) if (won + lost) > 0 else 0
        
        # Won bid metrics
        won_bids = [b for b in self.bids if b.status == 'won']
        if won_bids:
            avg_won_value = sum(b.bid_amount for b in won_bids) / len(won_bids)
            total_won_value = sum(b.bid_amount for b in won_bids)
        else:
            avg_won_value = 0
            total_won_value = 0
        
        # Estimating accuracy (for won bids with projects)
        won_with_projects = []
        for bid in won_bids:
            project = next((p for p in self.projects if p.project_id == bid.project_id), None)
            if project:
                won_with_projects.append({
                    'bid': bid.bid_amount,
                    'actual': project.contract_value
                })
        
        if won_with_projects:
            variance = sum(abs(w['bid'] - w['actual']) / w['actual'] for w in won_with_projects)
            avg_variance = variance / len(won_with_projects)
        else:
            avg_variance = 0
        
        return {
            'total_bids_submitted': total_bids,
            'bids_won': won,
            'bids_lost': lost,
            'bids_pending': pending,
            'win_rate_pct': round(win_rate * 100, 1),
            'win_rate_status': 'STRONG' if win_rate > 0.30 else 'GOOD' if win_rate > 0.20 else 'NEEDS_IMPROVEMENT',
            'avg_won_bid_value': round(avg_won_value, 2),
            'total_won_value': round(total_won_value, 2),
            'estimating_accuracy': round((1 - avg_variance) * 100, 1),
            'recommendations': self._bid_recommendations(win_rate)
        }
    
    def _bid_recommendations(self, win_rate: float) -> List[str]:
        """Generate bidding recommendations"""
        recs = []
        
        if win_rate < 0.15:
            recs.append("PRICING_CHECK - Win rate too low, prices may be high")
            recs.append("RELATIONSHIP_BUILDING - Focus on client relationships")
        elif win_rate > 0.40:
            recs.append("RAISE_PRICES - Winning too much, likely underpriced")
        
        if not recs:
            recs.append("BID_STRATEGY_HEALTHY - Maintain current approach")
        
        return recs
    
    def get_business_health_report(self) -> Dict:
        """Get overall construction business health"""
        
        completed_projects = [p for p in self.projects if p.status == 'completed']
        
        if not completed_projects:
            return {
                'status': 'STARTUP',
                'message': 'No completed projects yet',
                'backlog': self.get_backlog_analysis()
            }
        
        # Calculate aggregate margins
        total_revenue = sum(p.contract_value for p in completed_projects)
        total_costs = sum(
            p.materials_cost + p.labor_cost + p.subcontractor_cost + p.overhead_allocated
            for p in completed_projects
        )
        
        overall_margin = (total_revenue - total_costs) / total_revenue
        
        # Project mix
        by_type = {}
        for p in completed_projects:
            pt = p.project_type
            if pt not in by_type:
                by_type[pt] = {'count': 0, 'revenue': 0, 'profit': 0}
            by_type[pt]['count'] += 1
            by_type[pt]['revenue'] += p.contract_value
            
            proj_profit = p.contract_value - (p.materials_cost + p.labor_cost + p.subcontractor_cost + p.overhead_allocated)
            by_type[pt]['profit'] += proj_profit
        
        # Best performing type
        best_type = max(by_type.items(), 
                       key=lambda x: x[1]['profit'] / x[1]['revenue'] if x[1]['revenue'] > 0 else 0)[0]
        
        return {
            'company_name': self.company_name,
            'status': 'HEALTHY' if overall_margin > 0.15 else 'MARGINAL' if overall_margin > 0.08 else 'AT_RISK',
            'completed_projects': len(completed_projects),
            'total_revenue': round(total_revenue, 2),
            'total_costs': round(total_costs, 2),
            'gross_profit': round(total_revenue - total_costs, 2),
            'overall_margin_pct': round(overall_margin * 100, 1),
            'project_mix': by_type,
            'most_profitable_type': best_type,
            'backlog': self.get_backlog_analysis(),
            'bidding_performance': self.calculate_bid_performance(),
            'recommendations': self._business_recommendations(overall_margin, by_type)
        }
    
    def _business_recommendations(self, margin: float, by_type: Dict) -> List[str]:
        """Generate business recommendations"""
        recs = []
        
        if margin < 0.10:
            recs.append("URGENT_MARGIN_IMPROVEMENT - Review all cost categories")
            recs.append("STOP_UNPROFITABLE_WORK - Audit project selection")
        
        if margin > 0.25:
            recs.append("CONSIDER_EXPANSION - Strong margins support growth")
        
        # Check for loss-making project types
        for ptype, data in by_type.items():
            type_margin = data['profit'] / data['revenue'] if data['revenue'] > 0 else 0
            if type_margin < 0.05:
                recs.append(f"REVIEW_{ptype.upper()} - Low margins in this segment")
        
        if not recs:
            recs.append("MAINTAIN_OPERATIONS - Continue current strategy")
        
        return recs


# Usage
def analyze_construction_business(projects_data: List[Dict]) -> Dict:
    """Quick construction business analysis"""
    tracker = ConstructionBusinessTracker()
    
    for p in projects_data:
        project = Project(
            project_id=p['id'],
            client_name=p['client'],
            project_type=p.get('type', 'residential'),
            status=p.get('status', 'in_progress'),
            contract_value=p['value'],
            start_date=p.get('start', date.today()),
            expected_completion=p.get('expected', date.today()),
            actual_completion=p.get('completed'),
            materials_cost=p.get('materials', p['value'] * 0.40),
            labor_cost=p.get('labor', p['value'] * 0.25),
            subcontractor_cost=p.get('subs', p['value'] * 0.15),
            overhead_allocated=p.get('overhead', p['value'] * 0.15)
        )
        tracker.add_project(project)
    
    return tracker.get_business_health_report()


def check_project_profitability(project_data: Dict) -> Dict:
    """Check single project profitability"""
    tracker = ConstructionBusinessTracker()
    
    project = Project(
        project_id=project_data['id'],
        client_name=project_data['client'],
        project_type=project_data.get('type', 'residential'),
        status=project_data.get('status', 'in_progress'),
        contract_value=project_data['value'],
        start_date=project_data.get('start', date.today()),
        expected_completion=project_data.get('expected', date.today()),
        actual_completion=project_data.get('completed'),
        materials_cost=project_data.get('materials', 0),
        labor_cost=project_data.get('labor', 0),
        subcontractor_cost=project_data.get('subs', 0),
        overhead_allocated=project_data.get('overhead', 0)
    )
    
    return tracker.calculate_project_profitability(project)
