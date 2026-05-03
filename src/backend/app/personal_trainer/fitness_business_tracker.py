"""
Personal Trainer & Fitness Business Tracker
=============================================
Track personal training income, clients, sessions
Gym ownership, online coaching, nutrition services
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from enum import Enum


class ServiceType(Enum):
    ONE_ON_ONE = "one_on_one"
    GROUP_CLASS = "group_class"
    ONLINE_COACHING = "online_coaching"
    NUTRITION_PLAN = "nutrition_plan"
    CORPORATE_WELLNESS = "corporate_wellness"
    GYM_MEMBERSHIP = "gym_membership"


@dataclass
class Client:
    id: str
    name: str
    service_type: str
    sessions_per_week: int
    rate_per_session: float
    start_date: date
    contract_months: int
    status: str  # 'active', 'paused', 'cancelled'


@dataclass
class Session:
    client_id: str
    date: date
    duration_minutes: int
    type: str
    revenue: float
    notes: str


class PersonalTrainerBusinessTracker:
    """Track personal trainer and fitness business finances"""
    
    # Industry benchmarks
    BENCHMARKS = {
        'avg_session_rate': 65,  # USD
        'avg_sessions_per_week_per_client': 2,
        'client_retention_months': 8,
        'group_class_rate': 25,  # per person
        'online_coaching_monthly': 200,
        'nutrition_plan': 150
    }
    
    def __init__(self, trainer_name: str = "Trainer"):
        self.trainer_name = trainer_name
        self.clients: List[Client] = []
        self.sessions: List[Session] = []
        self.expenses: List[Dict] = []
    
    def add_client(self, client: Client):
        """Add new client to roster"""
        self.clients.append(client)
    
    def record_session(self, session: Session):
        """Record completed training session"""
        self.sessions.append(session)
    
    def calculate_monthly_revenue(self, target_month: date = None) -> Dict:
        """Calculate projected monthly revenue"""
        if target_month is None:
            target_month = date.today()
        
        active_clients = [c for c in self.clients if c.status == 'active']
        
        # Calculate by service type
        revenue_breakdown = {}
        total_monthly = 0
        
        for client in active_clients:
            weekly_sessions = client.sessions_per_week
            monthly_sessions = weekly_sessions * 4.3  # Avg weeks per month
            monthly_revenue = monthly_sessions * client.rate_per_session
            
            service = client.service_type
            if service not in revenue_breakdown:
                revenue_breakdown[service] = 0
            revenue_breakdown[service] += monthly_revenue
            
            total_monthly += monthly_revenue
        
        # Annual projection
        annual_revenue = total_monthly * 12
        
        return {
            'month': target_month.strftime('%Y-%m'),
            'active_clients': len(active_clients),
            'monthly_revenue': round(total_monthly, 2),
            'annual_projection': round(annual_revenue, 2),
            'by_service_type': {k: round(v, 2) for k, v in revenue_breakdown.items()},
            'avg_revenue_per_client': round(total_monthly / len(active_clients), 2) if active_clients else 0,
            'benchmark_comparison': self._compare_to_benchmarks(total_monthly, len(active_clients))
        }
    
    def _compare_to_benchmarks(self, monthly_revenue: float, 
                               client_count: int) -> Dict:
        """Compare to industry benchmarks"""
        if client_count == 0:
            return {}
        
        avg_per_client = monthly_revenue / client_count
        benchmark = self.BENCHMARKS['avg_session_rate'] * self.BENCHMARKS['avg_sessions_per_week_per_client'] * 4.3
        
        return {
            'avg_monthly_per_client': round(avg_per_client, 2),
            'industry_benchmark': round(benchmark, 2),
            'vs_benchmark_pct': round((avg_per_client / benchmark - 1) * 100, 1),
            'performance': 'ABOVE_AVERAGE' if avg_per_client > benchmark * 1.1 else 'BELOW_AVERAGE' if avg_per_client < benchmark * 0.9 else 'AVERAGE'
        }
    
    def calculate_client_lifetime_value(self, client: Client) -> Dict:
        """Calculate client lifetime value"""
        monthly_revenue = (client.sessions_per_week * 4.3 * client.rate_per_session)
        expected_months = min(client.contract_months, self.BENCHMARKS['client_retention_months'])
        
        gross_ltv = monthly_revenue * expected_months
        
        # Acquisition cost estimate
        cac = monthly_revenue * 0.5  # Assume 0.5 months to acquire
        
        # Service costs
        service_cost_pct = 0.15  # 15% for equipment, software, etc.
        service_costs = gross_ltv * service_cost_pct
        
        net_ltv = gross_ltv - cac - service_costs
        
        return {
            'client_id': client.id,
            'client_name': client.name,
            'monthly_revenue': round(monthly_revenue, 2),
            'expected_months': expected_months,
            'gross_ltv': round(gross_ltv, 2),
            'acquisition_cost': round(cac, 2),
            'service_costs': round(service_costs, 2),
            'net_ltv': round(net_ltv, 2),
            'ltv_to_cac_ratio': round(gross_ltv / cac, 1),
            'value_tier': 'HIGH' if net_ltv > 2000 else 'MEDIUM' if net_ltv > 1000 else 'LOW'
        }
    
    def get_business_health_report(self) -> Dict:
        """Get overall business health report"""
        if not self.clients:
            return {'status': 'NO_CLIENTS', 'message': 'Add clients to see metrics'}
        
        active = [c for c in self.clients if c.status == 'active']
        paused = [c for c in self.clients if c.status == 'paused']
        cancelled = [c for c in self.clients if c.status == 'cancelled']
        
        # Churn calculation
        total_ever = len(self.clients)
        churn_rate = len(cancelled) / total_ever if total_ever > 0 else 0
        
        # Capacity utilization
        max_clients = 25  # Typical full-time capacity
        capacity_pct = len(active) / max_clients * 100
        
        # Monthly metrics
        monthly = self.calculate_monthly_revenue()
        
        # Growth rate (if historical data)
        # Would compare to previous month
        
        return {
            'business_name': f"{self.trainer_name} Fitness",
            'status': 'HEALTHY' if len(active) >= 10 else 'BUILDING' if len(active) >= 5 else 'STARTUP',
            'active_clients': len(active),
            'paused_clients': len(paused),
            'churned_clients': len(cancelled),
            'churn_rate_pct': round(churn_rate * 100, 1),
            'capacity_utilization_pct': round(capacity_pct, 1),
            'monthly_revenue': monthly['monthly_revenue'],
            'annual_projection': monthly['annual_projection'],
            'avg_client_tenure_months': self._calculate_avg_tenure(),
            'recommendations': self._generate_recommendations(active, churn_rate, capacity_pct)
        }
    
    def _calculate_avg_tenure(self) -> float:
        """Calculate average client tenure"""
        if not self.clients:
            return 0
        
        tenures = []
        today = date.today()
        
        for client in self.clients:
            if client.status == 'active':
                tenure = (today - client.start_date).days / 30
                tenures.append(tenure)
        
        return round(sum(tenures) / len(tenures), 1) if tenures else 0
    
    def _generate_recommendations(self, active_clients: List[Client],
                                 churn_rate: float, capacity_pct: float) -> List[str]:
        """Generate business recommendations"""
        recs = []
        
        if len(active_clients) < 5:
            recs.append("FOCUS_ON_ACQUISITION - Need more clients for sustainability")
        
        if churn_rate > 0.3:
            recs.append("IMPROVE_RETENTION - High churn, focus on client satisfaction")
        
        if capacity_pct > 90:
            recs.append("RAISE_PRICES - At capacity, increase rates")
            recs.append("CONSIDER_GROUP_CLASSES - Serve more clients efficiently")
        
        if capacity_pct < 50:
            recs.append("MARKETING_PUSH - Low utilization, acquire more clients")
            recs.append("OFFER_INTRO_DEALS - Attract new signups")
        
        # Service mix
        online_clients = [c for c in active_clients if c.service_type == 'online_coaching']
        if len(online_clients) / len(active_clients) < 0.2 if active_clients else 0:
            recs.append("ADD_ONLINE_OFFERING - Expand reach with virtual training")
        
        if not recs:
            recs.append("MAINTAIN_COURSE - Business metrics look healthy")
        
        return recs
    
    def get_service_package_pricing(self) -> Dict:
        """Get recommended service package pricing"""
        return {
            'one_on_one_training': {
                'single_session': 65,
                '10_pack': 550,  # $55/session
                'monthly_unlimited': 800,
                'description': 'In-person individual training'
            },
            'group_classes': {
                'drop_in': 25,
                '10_class_pack': 200,
                'monthly_unlimited': 150,
                'description': 'Small group fitness classes'
            },
            'online_coaching': {
                'basic': 150,  # Programming only
                'premium': 300,  # Programming + weekly check-ins
                'elite': 500,  # Daily support + nutrition
                'description': 'Remote training and accountability'
            },
            'nutrition_services': {
                'meal_plan': 150,
                'monthly_coaching': 200,
                'description': 'Custom nutrition guidance'
            },
            'corporate_wellness': {
                'per_employee_per_month': 50,
                'minimum': 20,
                'description': 'On-site corporate fitness'
            }
        }


# Usage
def quick_trainer_analysis(clients_data: List[Dict]) -> Dict:
    """Quick fitness business analysis"""
    tracker = PersonalTrainerBusinessTracker()
    
    for c in clients_data:
        client = Client(
            id=c['id'],
            name=c['name'],
            service_type=c.get('service', 'one_on_one'),
            sessions_per_week=c.get('sessions', 2),
            rate_per_session=c.get('rate', 65),
            start_date=c.get('start', date.today()),
            contract_months=c.get('contract', 12),
            status=c.get('status', 'active')
        )
        tracker.add_client(client)
    
    return tracker.get_business_health_report()


def calculate_client_value(client_data: Dict) -> Dict:
    """Calculate single client LTV"""
    tracker = PersonalTrainerBusinessTracker()
    
    client = Client(
        id=client_data['id'],
        name=client_data['name'],
        service_type=client_data.get('service', 'one_on_one'),
        sessions_per_week=client_data.get('sessions', 2),
        rate_per_session=client_data.get('rate', 65),
        start_date=client_data.get('start', date.today()),
        contract_months=client_data.get('contract', 12),
        status='active'
    )
    
    return tracker.calculate_client_lifetime_value(client)


def get_pricing_guide() -> Dict:
    """Get service pricing recommendations"""
    tracker = PersonalTrainerBusinessTracker()
    return tracker.get_service_package_pricing()
