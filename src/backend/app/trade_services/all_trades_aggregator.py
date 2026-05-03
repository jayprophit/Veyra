"""
All Trades Service Aggregator
==============================
Aggregate all trade services - carpenter, handyman, landscaping, etc
Unified tracking for multi-service trade businesses
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum


class TradeService(Enum):
    CARPENTER = "carpenter"
    HANDYMAN = "handyman"
    LANDSCAPING = "landscaping"
    ROOFING = "roofing"
    FLOORING = "flooring"
    MASONRY = "masonry"
    GLAZING = "glazing"
    FENCING = "fencing"
    POOL_SERVICE = "pool_service"
    PEST_CONTROL = "pest_control"
    CLEANING = "cleaning"
    LOCKSMITH = "locksmith"
    APPLIANCE_REPAIR = "appliance_repair"
    GARAGE_DOOR = "garage_door"
    SOLAR_INSTALL = "solar_install"
    HOME_INSPECTION = "home_inspection"
    MOVING = "moving"
    JUNK_REMOVAL = "junk_removal"


@dataclass
class TradeJob:
    job_id: str
    trade_type: str
    service_category: str
    client_name: str
    description: str
    
    # Financial
    labor_hours: float
    hourly_rate: float
    materials_cost: float
    materials_markup: float
    total_billed: float
    
    # Operations
    technician: str
    date: date
    completion_status: str  # 'completed', 'in_progress', 'scheduled'
    customer_rating: Optional[int]  # 1-5
    callback_required: bool


class AllTradesAggregator:
    """Aggregate all trade service businesses"""
    
    # Industry benchmarks by trade
    TRADE_BENCHMARKS = {
        'carpenter': {
            'hourly_rate': 65,
            'daily_capacity': 8,
            'avg_ticket': 850,
            'materials_markup': 0.25
        },
        'handyman': {
            'hourly_rate': 55,
            'daily_capacity': 8,
            'avg_ticket': 350,
            'materials_markup': 0.30
        },
        'landscaping': {
            'hourly_rate': 50,
            'daily_capacity': 10,
            'avg_ticket': 500,
            'materials_markup': 0.35
        },
        'roofing': {
            'hourly_rate': 45,
            'sqft_rate': 4.50,  # per sq ft
            'avg_ticket': 12000,
            'materials_markup': 0.20
        },
        'flooring': {
            'sqft_rate': 8.00,
            'avg_ticket': 3500,
            'materials_markup': 0.25
        },
        'masonry': {
            'hourly_rate': 60,
            'sqft_rate': 25,  # per sq ft
            'avg_ticket': 4500,
            'materials_markup': 0.30
        },
        'fencing': {
            'linear_ft_rate': 35,
            'avg_ticket': 4200,
            'materials_markup': 0.30
        },
        'pool_service': {
            'monthly_maintenance': 150,
            'repair_hourly': 85,
            'avg_ticket': 300
        },
        'pest_control': {
            'monthly_service': 50,
            'one_time': 150,
            'avg_ticket': 175
        },
        'cleaning': {
            'hourly_rate': 45,
            'sqft_rate': 0.15,
            'avg_ticket': 200
        },
        'locksmith': {
            'service_call': 85,
            'hourly_rate': 75,
            'avg_ticket': 225
        },
        'appliance_repair': {
            'diagnostic': 85,
            'hourly_rate': 95,
            'parts_markup': 0.50,
            'avg_ticket': 325
        },
        'garage_door': {
            'service_call': 95,
            'repair_avg': 250,
            'new_install': 1200,
            'avg_ticket': 425
        },
        'solar_install': {
            'per_watt': 3.00,
            'avg_system_size': 8000,  # watts
            'avg_ticket': 24000
        },
        'home_inspection': {
            'flat_rate': 450,
            'avg_ticket': 450
        },
        'moving': {
            'hourly_rate_2man': 150,
            'avg_ticket': 1200
        },
        'junk_removal': {
            'truck_load': 450,
            'avg_ticket': 350
        }
    }
    
    def __init__(self):
        self.jobs: List[TradeJob] = []
        self.active_trades: List[str] = []
    
    def add_job(self, job: TradeJob):
        """Add trade job"""
        self.jobs.append(job)
        if job.trade_type not in self.active_trades:
            self.active_trades.append(job.trade_type)
    
    def get_trade_performance(self, trade_type: str) -> Dict:
        """Get performance for specific trade"""
        
        trade_jobs = [j for j in self.jobs if j.trade_type == trade_type and j.completion_status == 'completed']
        
        if not trade_jobs:
            return {'error': f'No completed jobs for {trade_type}'}
        
        total_revenue = sum(j.total_billed for j in trade_jobs)
        total_hours = sum(j.labor_hours for j in trade_jobs)
        
        # Calculate costs
        total_materials = sum(j.materials_cost for j in trade_jobs)
        labor_cost = total_hours * 35  # Assume $35/hr labor cost
        overhead = total_hours * 12  # $12/hr overhead
        
        total_costs = total_materials + labor_cost + overhead
        gross_profit = total_revenue - total_costs
        margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Callbacks
        callbacks = sum(1 for j in trade_jobs if j.callback_required)
        
        # Customer satisfaction
        rated_jobs = [j for j in trade_jobs if j.customer_rating]
        avg_rating = sum(j.customer_rating for j in rated_jobs) / len(rated_jobs) if rated_jobs else 0
        
        # Benchmark comparison
        benchmark = self.TRADE_BENCHMARKS.get(trade_type, {})
        benchmark_rate = benchmark.get('hourly_rate', 60)
        actual_rate = total_revenue / total_hours if total_hours > 0 else 0
        
        return {
            'trade_type': trade_type,
            'jobs_completed': len(trade_jobs),
            'total_revenue': round(total_revenue, 2),
            'total_hours': round(total_hours, 1),
            'revenue_per_hour': round(actual_rate, 2),
            'benchmark_rate': benchmark_rate,
            'vs_benchmark_pct': round((actual_rate / benchmark_rate - 1) * 100, 1),
            'gross_profit': round(gross_profit, 2),
            'margin_pct': round(margin_pct, 1),
            'callback_rate_pct': round(callbacks / len(trade_jobs) * 100, 1),
            'avg_customer_rating': round(avg_rating, 1),
            'performance_tier': 'TOP' if margin_pct > 35 else 'GOOD' if margin_pct > 20 else 'NEEDS_IMPROVEMENT'
        }
    
    def get_all_trades_dashboard(self) -> Dict:
        """Get dashboard for all active trades"""
        
        if not self.active_trades:
            return {'status': 'NO_DATA', 'message': 'No trade jobs recorded'}
        
        # Individual trade performance
        trade_performance = {}
        for trade in self.active_trades:
            perf = self.get_trade_performance(trade)
            if 'error' not in perf:
                trade_performance[trade] = perf
        
        # Combined metrics
        all_completed = [j for j in self.jobs if j.completion_status == 'completed']
        
        if not all_completed:
            return {
                'status': 'NO_COMPLETED',
                'active_trades': self.active_trades,
                'trade_performance': trade_performance
            }
        
        total_revenue = sum(j.total_billed for j in all_completed)
        total_jobs = len(all_completed)
        
        # Most profitable trade
        best_trade = max(trade_performance.items(),
                        key=lambda x: x[1].get('margin_pct', 0))[0] if trade_performance else None
        
        # Trade mix
        by_trade = {}
        for j in all_completed:
            t = j.trade_type
            if t not in by_trade:
                by_trade[t] = {'count': 0, 'revenue': 0}
            by_trade[t]['count'] += 1
            by_trade[t]['revenue'] += j.total_billed
        
        return {
            'status': 'ACTIVE',
            'active_trades_count': len(self.active_trades),
            'trades_list': self.active_trades,
            'total_revenue_all_trades': round(total_revenue, 2),
            'total_jobs_completed': total_jobs,
            'avg_job_value': round(total_revenue / total_jobs, 2),
            'most_profitable_trade': best_trade,
            'trade_mix': by_trade,
            'individual_trade_performance': trade_performance,
            'recommendations': self._generate_trade_recommendations(trade_performance, by_trade)
        }
    
    def _generate_trade_recommendations(self, performance: Dict, mix: Dict) -> List[str]:
        """Generate recommendations for trade portfolio"""
        recs = []
        
        # Find underperforming trades
        for trade, perf in performance.items():
            if perf.get('margin_pct', 0) < 15:
                recs.append(f"REVIEW_{trade.upper()} - Low margins, audit pricing/costs")
        
        # Find high performers
        for trade, perf in performance.items():
            if perf.get('margin_pct', 0) > 35:
                recs.append(f"EXPAND_{trade.upper()} - High margins, add capacity")
        
        # Cross-selling opportunities
        if 'handyman' in mix and 'plumbing' not in mix:
            recs.append("ADD_PLUMBING - Natural upsell from handyman work")
        
        if 'landscaping' in mix and 'fencing' not in mix:
            recs.append("ADD_FENCING - Landscape customers need fencing")
        
        if 'cleaning' in mix and 'pest_control' not in mix:
            recs.append("ADD_PEST_CONTROL - Complementary to cleaning services")
        
        if not recs:
            recs.append("DIVERSIFY_SERVICES - Consider adding complementary trades")
        
        return recs
    
    def get_rate_card_all_trades(self) -> Dict:
        """Get rate card for all supported trades"""
        rate_card = {}
        
        for trade, benchmarks in self.TRADE_BENCHMARKS.items():
            rate_card[trade] = {
                'pricing_structure': self._get_pricing_structure(trade, benchmarks),
                'avg_market_rate': self._get_avg_rate(trade, benchmarks),
                'margin_target': '25-35%'
            }
        
        return rate_card
    
    def _get_pricing_structure(self, trade: str, benchmarks: Dict) -> str:
        """Get pricing structure description"""
        if 'hourly_rate' in benchmarks:
            return f"Hourly: ${benchmarks['hourly_rate']}/hr"
        elif 'sqft_rate' in benchmarks:
            return f"Per sq ft: ${benchmarks['sqft_rate']}/sq ft"
        elif 'linear_ft_rate' in benchmarks:
            return f"Per linear ft: ${benchmarks['linear_ft_rate']}/ft"
        elif 'monthly_maintenance' in benchmarks:
            return f"Monthly: ${benchmarks['monthly_maintenance']}/month"
        else:
            return f"Flat rate: ${benchmarks.get('flat_rate', 'Variable')}"
    
    def _get_avg_rate(self, trade: str, benchmarks: Dict) -> str:
        """Get average rate/ticket info"""
        if 'avg_ticket' in benchmarks:
            return f"${benchmarks['avg_ticket']}"
        return "Variable"


# Usage
def analyze_multi_trade_business(jobs_data: List[Dict]) -> Dict:
    """Analyze multi-trade service business"""
    aggregator = AllTradesAggregator()
    
    for j in jobs_data:
        job = TradeJob(
            job_id=j['id'],
            trade_type=j['trade'],
            service_category=j.get('category', 'service'),
            client_name=j['client'],
            description=j.get('description', ''),
            labor_hours=j.get('hours', 4),
            hourly_rate=j.get('rate', 60),
            materials_cost=j.get('materials', 100),
            materials_markup=j.get('markup', 0.25),
            total_billed=j['total'],
            technician=j.get('tech', 'Tech1'),
            date=j.get('date', date.today()),
            completion_status=j.get('status', 'completed'),
            customer_rating=j.get('rating'),
            callback_required=j.get('callback', False)
        )
        aggregator.add_job(job)
    
    return aggregator.get_all_trades_dashboard()


def get_specific_trade_analysis(trade_type: str, jobs_data: List[Dict]) -> Dict:
    """Get analysis for specific trade"""
    aggregator = AllTradesAggregator()
    
    for j in jobs_data:
        job = TradeJob(
            job_id=j['id'],
            trade_type=j['trade'],
            service_category=j.get('category', 'service'),
            client_name=j['client'],
            description=j.get('description', ''),
            labor_hours=j.get('hours', 4),
            hourly_rate=j.get('rate', 60),
            materials_cost=j.get('materials', 100),
            materials_markup=0.25,
            total_billed=j['total'],
            technician=j.get('tech', 'Tech1'),
            date=j.get('date', date.today()),
            completion_status=j.get('status', 'completed'),
            customer_rating=j.get('rating'),
            callback_required=j.get('callback', False)
        )
        aggregator.add_job(job)
    
    return aggregator.get_trade_performance(trade_type)


def get_all_trades_rates() -> Dict:
    """Get rate card for all trades"""
    aggregator = AllTradesAggregator()
    return aggregator.get_rate_card_all_trades()
