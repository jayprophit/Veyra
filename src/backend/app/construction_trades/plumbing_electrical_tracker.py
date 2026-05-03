"""
Plumbing & Electrical Trade Business Tracker
=============================================
Track plumbing and electrical business operations
Service calls, installations, repairs, new construction
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from enum import Enum


class TradeType(Enum):
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"


class JobCategory(Enum):
    SERVICE_CALL = "service_call"
    INSTALLATION = "installation"
    REPAIR = "repair"
    REMODEL = "remodel"
    NEW_CONSTRUCTION = "new_construction"
    EMERGENCY = "emergency"


@dataclass
class ServiceJob:
    job_id: str
    trade_type: str  # plumbing, electrical, hvac
    category: str
    client_name: str
    description: str
    
    # Financial
    labor_charge: float
    materials_cost: float
    parts_markup_pct: float
    trip_charge: float
    total_billed: float
    
    # Operations
    technician: str
    date: date
    hours_worked: float
    callback_required: bool
    
    # Status
    status: str  # 'scheduled', 'completed', 'invoiced', 'paid'


class PlumbingElectricalTracker:
    """Track plumbing and electrical service business"""
    
    # Industry benchmarks
    BENCHMARKS = {
        'plumbing': {
            'service_call_rate': 125,  # Trip charge + first hour
            'hourly_rate': 95,
            'parts_markup': 0.50,  # 50% markup
            'avg_service_ticket': 450,
            'callback_rate_target': 0.05  # 5%
        },
        'electrical': {
            'service_call_rate': 135,
            'hourly_rate': 105,
            'parts_markup': 0.45,
            'avg_service_ticket': 525,
            'callback_rate_target': 0.04
        },
        'hvac': {
            'service_call_rate': 150,
            'hourly_rate': 120,
            'parts_markup': 0.40,
            'avg_service_ticket': 650,
            'callback_rate_target': 0.03
        }
    }
    
    def __init__(self, company_name: str = "Trade Services"):
        self.company_name = company_name
        self.jobs: List[ServiceJob] = []
        self.technicians: List[str] = []
    
    def add_job(self, job: ServiceJob):
        """Add service job"""
        self.jobs.append(job)
        if job.technician not in self.technicians:
            self.technicians.append(job.technician)
    
    def calculate_job_profitability(self, job: ServiceJob) -> Dict:
        """Calculate profitability of a single job"""
        
        # Parts revenue with markup
        parts_revenue = job.materials_cost * (1 + job.parts_markup_pct)
        
        # Total revenue
        total_revenue = job.labor_charge + parts_revenue + job.trip_charge
        
        # Costs
        labor_cost = job.hours_worked * 35  # Assume $35/hr technician cost
        material_cost = job.materials_cost
        overhead_per_hour = 15  # Truck, insurance, etc
        overhead_cost = job.hours_worked * overhead_per_hour
        
        total_costs = labor_cost + material_cost + overhead_cost
        
        # Profit
        gross_profit = total_revenue - total_costs
        margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Revenue per hour
        revenue_per_hour = total_revenue / job.hours_worked if job.hours_worked > 0 else 0
        
        return {
            'job_id': job.job_id,
            'trade': job.trade_type,
            'category': job.category,
            'total_revenue': round(total_revenue, 2),
            'total_costs': round(total_costs, 2),
            'gross_profit': round(gross_profit, 2),
            'margin_pct': round(margin_pct, 1),
            'revenue_per_hour': round(revenue_per_hour, 2),
            'efficiency_rating': 'HIGH' if margin_pct > 40 else 'GOOD' if margin_pct > 25 else 'NEEDS_REVIEW',
            'callback': job.callback_required
        }
    
    def get_technician_performance(self, technician_name: str) -> Dict:
        """Get performance metrics for specific technician"""
        
        tech_jobs = [j for j in self.jobs if j.technician == technician_name and j.status == 'completed']
        
        if not tech_jobs:
            return {'error': f'No completed jobs found for {technician_name}'}
        
        # Financial metrics
        total_revenue = sum(j.total_billed for j in tech_jobs)
        total_hours = sum(j.hours_worked for j in tech_jobs)
        
        # Callbacks
        callbacks = sum(1 for j in tech_jobs if j.callback_required)
        callback_rate = callbacks / len(tech_jobs)
        
        # Job categories
        by_category = {}
        for j in tech_jobs:
            cat = j.category
            if cat not in by_category:
                by_category[cat] = {'count': 0, 'revenue': 0}
            by_category[cat]['count'] += 1
            by_category[cat]['revenue'] += j.total_billed
        
        # Daily average
        days_worked = len(set(j.date for j in tech_jobs))
        avg_daily_revenue = total_revenue / max(days_worked, 1)
        
        return {
            'technician': technician_name,
            'jobs_completed': len(tech_jobs),
            'total_revenue': round(total_revenue, 2),
            'total_hours': round(total_hours, 1),
            'revenue_per_hour': round(total_revenue / total_hours, 2) if total_hours > 0 else 0,
            'avg_daily_revenue': round(avg_daily_revenue, 2),
            'callback_rate_pct': round(callback_rate * 100, 1),
            'callback_status': 'EXCELLENT' if callback_rate < 0.03 else 'GOOD' if callback_rate < 0.06 else 'NEEDS_IMPROVEMENT',
            'job_mix': by_category,
            'performance_rating': self._rate_technician(callback_rate, total_revenue / max(days_worked, 1))
        }
    
    def _rate_technician(self, callback_rate: float, daily_revenue: float) -> str:
        """Rate technician performance"""
        score = 50
        
        # Callback penalty/bonus
        if callback_rate < 0.02:
            score += 30
        elif callback_rate < 0.05:
            score += 15
        elif callback_rate > 0.08:
            score -= 20
        
        # Revenue generation
        if daily_revenue > 800:
            score += 20
        elif daily_revenue > 600:
            score += 10
        elif daily_revenue < 400:
            score -= 10
        
        if score >= 80:
            return 'TOP_PERFORMER'
        elif score >= 60:
            return 'SOLID'
        elif score >= 40:
            return 'AVERAGE'
        else:
            return 'NEEDS_COACHING'
    
    def get_business_dashboard(self) -> Dict:
        """Get overall business dashboard"""
        
        completed = [j for j in self.jobs if j.status == 'completed']
        
        if not completed:
            return {
                'status': 'NEW_BUSINESS',
                'message': 'No completed jobs to analyze'
            }
        
        # Overall metrics
        total_revenue = sum(j.total_billed for j in completed)
        total_jobs = len(completed)
        
        # By trade
        by_trade = {}
        for j in completed:
            trade = j.trade_type
            if trade not in by_trade:
                by_trade[trade] = {'jobs': 0, 'revenue': 0, 'hours': 0}
            by_trade[trade]['jobs'] += 1
            by_trade[trade]['revenue'] += j.total_billed
            by_trade[trade]['hours'] += j.hours_worked
        
        # Add averages
        for trade in by_trade:
            data = by_trade[trade]
            data['avg_ticket'] = round(data['revenue'] / data['jobs'], 2)
            data['revenue_per_hour'] = round(data['revenue'] / data['hours'], 2) if data['hours'] > 0 else 0
        
        # Callback analysis
        total_callbacks = sum(1 for j in completed if j.callback_required)
        overall_callback_rate = total_callbacks / total_jobs
        
        # Job categories
        by_category = {}
        for j in completed:
            cat = j.category
            if cat not in by_category:
                by_category[cat] = {'count': 0, 'revenue': 0}
            by_category[cat]['count'] += 1
            by_category[cat]['revenue'] += j.total_billed
        
        # Most profitable category
        best_category = max(by_category.items(),
                           key=lambda x: x[1]['revenue'] / x[1]['count'] if x[1]['count'] > 0 else 0)[0]
        
        return {
            'company_name': self.company_name,
            'status': 'HEALTHY' if overall_callback_rate < 0.05 else 'NEEDS_ATTENTION',
            'total_jobs_completed': total_jobs,
            'total_revenue': round(total_revenue, 2),
            'avg_ticket_value': round(total_revenue / total_jobs, 2),
            'callback_rate_pct': round(overall_callback_rate * 100, 1),
            'callback_status': 'EXCELLENT' if overall_callback_rate < 0.03 else 'ACCEPTABLE' if overall_callback_rate < 0.06 else 'CONCERNING',
            'by_trade': by_trade,
            'by_category': by_category,
            'most_profitable_category': best_category,
            'technician_count': len(self.technicians),
            'recommendations': self._business_recommendations(by_trade, overall_callback_rate)
        }
    
    def _business_recommendations(self, by_trade: Dict, callback_rate: float) -> List[str]:
        """Generate business recommendations"""
        recs = []
        
        if callback_rate > 0.06:
            recs.append("QUALITY_CONTROL - High callback rate impacts profitability")
            recs.append("TECHNICIAN_TRAINING - Review installation procedures")
        
        # Check for trade expansion opportunities
        if 'plumbing' in by_trade and 'electrical' not in by_trade:
            recs.append("CONSIDER_ELECTRICAL - Add electrical services for cross-selling")
        
        if 'hvac' not in by_trade:
            recs.append("EXPAND_HVAC - Highest ticket values in HVAC")
        
        # Emergency service
        emergency_jobs = sum(1 for j in self.jobs if j.category == 'emergency')
        if emergency_jobs / len(self.jobs) < 0.10:
            recs.append("PROMOTE_EMERGENCY - Higher margins on after-hours work")
        
        if not recs:
            recs.append("MAINTAIN_QUALITY - Business metrics look strong")
        
        return recs
    
    def get_service_rate_card(self) -> Dict:
        """Get recommended service rate card"""
        return {
            'plumbing': {
                'service_call_trip': 85,
                'first_hour': 125,
                'additional_hours': 95,
                'after_hours_premium': 1.5,  # 50% more
                'weekend_premium': 1.75,
                'parts_markup': 0.50,
                'common_jobs': {
                    'faucet_repair': '175-250',
                    'toilet_replacement': '350-500',
                    'water_heater_install': '1200-1800',
                    'sewer_line_cleaning': '250-450',
                    'pipe_leak_repair': '200-400'
                }
            },
            'electrical': {
                'service_call_trip': 95,
                'first_hour': 135,
                'additional_hours': 105,
                'after_hours_premium': 1.5,
                'weekend_premium': 1.75,
                'parts_markup': 0.45,
                'common_jobs': {
                    'outlet_installation': '150-250',
                    'panel_upgrade': '2000-3500',
                    'ceiling_fan_install': '200-350',
                    'rewire_circuit': '500-900',
                    'generator_install': '3500-8000'
                }
            },
            'hvac': {
                'service_call_trip': 100,
                'diagnostic': 150,
                'tune_up': 150,
                'after_hours_premium': 1.5,
                'weekend_premium': 1.75,
                'parts_markup': 0.40,
                'common_jobs': {
                    'ac_repair': '300-650',
                    'furnace_repair': '350-800',
                    'ac_replacement': '3500-7500',
                    'furnace_replacement': '2500-6000',
                    'duct_cleaning': '400-700'
                }
            }
        }


# Usage
def analyze_trade_business(jobs_data: List[Dict]) -> Dict:
    """Quick plumbing/electrical business analysis"""
    tracker = PlumbingElectricalTracker()
    
    for j in jobs_data:
        job = ServiceJob(
            job_id=j['id'],
            trade_type=j.get('trade', 'plumbing'),
            category=j.get('category', 'service_call'),
            client_name=j['client'],
            description=j.get('description', ''),
            labor_charge=j.get('labor', 200),
            materials_cost=j.get('materials', 100),
            parts_markup_pct=j.get('markup', 0.50),
            trip_charge=j.get('trip', 85),
            total_billed=j['total'],
            technician=j.get('tech', 'Tech1'),
            date=j.get('date', date.today()),
            hours_worked=j.get('hours', 2),
            callback_required=j.get('callback', False),
            status=j.get('status', 'completed')
        )
        tracker.add_job(job)
    
    return tracker.get_business_dashboard()


def check_technician_performance(tech_name: str, jobs_data: List[Dict]) -> Dict:
    """Check technician performance"""
    tracker = PlumbingElectricalTracker()
    
    for j in jobs_data:
        job = ServiceJob(
            job_id=j['id'],
            trade_type=j.get('trade', 'plumbing'),
            category=j.get('category', 'service_call'),
            client_name=j['client'],
            description=j.get('description', ''),
            labor_charge=j.get('labor', 200),
            materials_cost=j.get('materials', 100),
            parts_markup_pct=0.50,
            trip_charge=j.get('trip', 85),
            total_billed=j['total'],
            technician=j['tech'],
            date=j.get('date', date.today()),
            hours_worked=j.get('hours', 2),
            callback_required=j.get('callback', False),
            status='completed'
        )
        tracker.add_job(job)
    
    return tracker.get_technician_performance(tech_name)


def get_rate_card() -> Dict:
    """Get service rate card"""
    tracker = PlumbingElectricalTracker()
    return tracker.get_service_rate_card()
