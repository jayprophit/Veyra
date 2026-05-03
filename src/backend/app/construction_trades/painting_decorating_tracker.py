"""
Painting & Decorating Business Tracker
========================================
Track painting and decorating business income
Residential, commercial, interior, exterior projects
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum


class PaintProjectType(Enum):
    INTERIOR_RESIDENTIAL = "interior_residential"
    EXTERIOR_RESIDENTIAL = "exterior_residential"
    INTERIOR_COMMERCIAL = "interior_commercial"
    EXTERIOR_COMMERCIAL = "exterior_commercial"
    DECORATIVE_FINISH = "decorative_finish"
    WALLPAPER = "wallpaper"
    CABINET_REFINISH = "cabinet_refinish"


class PaintSurface(Enum):
    DRYWALL = "drywall"
    PLASTER = "plaster"
    WOOD_SIDING = "wood_siding"
    BRICK = "brick"
    STUCCO = "stucco"
    METAL = "metal"


@dataclass
class PaintJob:
    job_id: str
    client_name: str
    project_type: str
    square_feet: float
    surfaces: List[str]
    paint_quality: str  # 'economy', 'standard', 'premium'
    num_colors: int
    num_coats: int
    
    # Financial
    quoted_price: float
    paint_materials_cost: float
    labor_hours_estimated: float
    labor_hours_actual: Optional[float]
    start_date: date
    completion_date: Optional[date]
    status: str


class PaintingDecoratingTracker:
    """Track painting and decorating business"""
    
    # Industry pricing benchmarks (per sq ft)
    PRICING_GUIDE = {
        'interior_residential': {
            'drywall_standard': 2.50,  # $/sq ft
            'drywall_premium': 4.00,
            'plaster_standard': 3.50,
            'plaster_premium': 5.50,
            'trim_baseboards': 3.00,  # linear ft
            'cabinets_per_door': 75,
            'cabinets_per_drawer': 50
        },
        'exterior_residential': {
            'wood_siding': 3.00,
            'stucco': 4.50,
            'brick': 5.00,
            'vinyl_siding': 2.50,
            'trim': 2.00
        },
        'interior_commercial': {
            'office_space': 1.50,
            'retail': 2.00,
            'warehouse': 0.75,
            'medical': 3.00
        },
        'wallpaper': {
            'standard_install': 8.00,  # per roll
            'removal': 3.00,  # per sq ft
            'premium_paper': 12.00
        },
        'decorative_finish': {
            'faux_finish': 15.00,
            'venetian_plaster': 25.00,
            'metallic': 20.00,
            'murals_per_sqft': 50.00
        }
    }
    
    # Material costs (per gallon)
    PAINT_COSTS = {
        'economy': 25,
        'standard': 45,
        'premium': 75,
        'designer': 120
    }
    
    # Production rates (sq ft per hour)
    PRODUCTION_RATES = {
        'interior_rolling': 150,
        'interior_brushing': 50,
        'exterior_brush_roll': 100,
        'exterior_spray': 300,
        'prep_sanding': 75,
        'trim_cutting': 30
    }
    
    def __init__(self, business_name: str = "Painting Co"):
        self.business_name = business_name
        self.jobs: List[PaintJob] = []
        self.hourly_labor_rate: float = 45
    
    def add_job(self, job: PaintJob):
        """Add painting job"""
        self.jobs.append(job)
    
    def estimate_job_cost(self, project_type: str, square_feet: float,
                         surfaces: List[str], paint_quality: str,
                         num_coats: int = 2) -> Dict:
        """
        Estimate job cost for quoting
        """
        # Base paint cost
        paint_cost_per_gallon = self.PAINT_COSTS.get(paint_quality, 45)
        
        # Coverage: 350 sq ft per gallon per coat
        gallons_needed = (square_feet / 350) * num_coats * 1.1  # 10% waste factor
        paint_materials_cost = gallons_needed * paint_cost_per_gallon
        
        # Add primer if needed (30% extra)
        if any(s in ['bare_wood', 'new_drywall', 'stain'] for s in surfaces):
            primer_gallons = (square_feet / 350) * 1.1
            paint_materials_cost += primer_gallons * 35  # Primer cost
        
        # Labor estimate
        # Assume rolling mostly, some cutting
        rolling_hours = square_feet / self.PRODUCTION_RATES['interior_rolling']
        cutting_hours = (square_feet * 0.15) / self.PRODUCTION_RATES['trim_cutting']
        total_labor_hours = (rolling_hours + cutting_hours) * num_coats
        
        labor_cost = total_labor_hours * self.hourly_labor_rate
        
        # Materials (tape, plastic, brushes, etc)
        other_materials = square_feet * 0.15  # $0.15 per sq ft
        
        total_cost = paint_materials_cost + labor_cost + other_materials
        
        # Recommended price (30% markup)
        recommended_price = total_cost * 1.30
        
        return {
            'project_type': project_type,
            'square_feet': square_feet,
            'paint_quality': paint_quality,
            'num_coats': num_coats,
            'materials_cost': round(paint_materials_cost, 2),
            'labor_hours': round(total_labor_hours, 1),
            'labor_cost': round(labor_cost, 2),
            'other_materials': round(other_materials, 2),
            'total_cost': round(total_cost, 2),
            'recommended_price': round(recommended_price, 2),
            'margin_pct': 23,  # 23% margin at 30% markup
            'price_per_sqft': round(recommended_price / square_feet, 2)
        }
    
    def analyze_job_profitability(self, job: PaintJob) -> Dict:
        """Analyze actual job profitability"""
        
        if job.status != 'completed' or job.labor_hours_actual is None:
            return {'error': 'Job not completed or hours not recorded'}
        
        # Actual costs
        actual_labor_cost = job.labor_hours_actual * self.hourly_labor_rate
        total_cost = job.paint_materials_cost + actual_labor_cost + (job.square_feet * 0.10)
        
        gross_profit = job.quoted_price - total_cost
        margin_pct = (gross_profit / job.quoted_price * 100) if job.quoted_price > 0 else 0
        
        # Labor efficiency
        if job.labor_hours_estimated > 0:
            efficiency = job.labor_hours_estimated / job.labor_hours_actual
            efficiency_pct = efficiency * 100
        else:
            efficiency_pct = 100
        
        # Days to complete
        days_taken = (job.completion_date - job.start_date).days if job.completion_date else 0
        
        return {
            'job_id': job.job_id,
            'client': job.client_name,
            'quoted_price': round(job.quoted_price, 2),
            'total_costs': round(total_cost, 2),
            'gross_profit': round(gross_profit, 2),
            'margin_pct': round(margin_pct, 1),
            'margin_status': 'PROFITABLE' if margin_pct > 20 else 'BREAK_EVEN' if margin_pct > 10 else 'LOSS',
            'labor_efficiency_pct': round(efficiency_pct, 1),
            'days_to_complete': days_taken,
            'revenue_per_day': round(job.quoted_price / max(days_taken, 1), 2),
            'cost_breakdown': {
                'paint_materials': round(job.paint_materials_cost, 2),
                'labor': round(actual_labor_cost, 2),
                'other': round(job.square_feet * 0.10, 2)
            }
        }
    
    def get_business_summary(self) -> Dict:
        """Get business health summary"""
        
        completed = [j for j in self.jobs if j.status == 'completed']
        in_progress = [j for j in self.jobs if j.status == 'in_progress']
        quoted = [j for j in self.jobs if j.status == 'quoted']
        
        if not completed:
            return {
                'status': 'NEW_BUSINESS',
                'completed_jobs': 0,
                'in_progress': len(in_progress),
                'quoted_pending': len(quoted),
                'message': 'Build completed job history for analytics'
            }
        
        total_revenue = sum(j.quoted_price for j in completed)
        total_sqft = sum(j.square_feet for j in completed)
        
        # Estimate costs for completed jobs
        estimated_costs = 0
        for j in completed:
            actual_hours = j.labor_hours_actual or j.labor_hours_estimated
            labor = actual_hours * self.hourly_labor_rate
            other = j.square_feet * 0.10
            estimated_costs += j.paint_materials_cost + labor + other
        
        gross_profit = total_revenue - estimated_costs
        avg_margin = gross_profit / total_revenue * 100 if total_revenue > 0 else 0
        
        # By project type
        by_type = {}
        for j in completed:
            pt = j.project_type
            if pt not in by_type:
                by_type[pt] = {'count': 0, 'revenue': 0, 'sqft': 0}
            by_type[pt]['count'] += 1
            by_type[pt]['revenue'] += j.quoted_price
            by_type[pt]['sqft'] += j.square_feet
        
        # Best performing type
        best_type = max(by_type.items(),
                       key=lambda x: x[1]['revenue'] / x[1]['count'] if x[1]['count'] > 0 else 0)[0]
        
        return {
            'business_name': self.business_name,
            'status': 'HEALTHY' if avg_margin > 25 else 'MARGINAL' if avg_margin > 15 else 'NEEDS_ATTENTION',
            'completed_jobs': len(completed),
            'in_progress': len(in_progress),
            'quoted_pending': len(quoted),
            'total_revenue': round(total_revenue, 2),
            'total_sqft_painted': round(total_sqft, 0),
            'estimated_gross_profit': round(gross_profit, 2),
            'avg_margin_pct': round(avg_margin, 1),
            'avg_job_value': round(total_revenue / len(completed), 2),
            'avg_price_per_sqft': round(total_revenue / total_sqft, 2) if total_sqft > 0 else 0,
            'by_project_type': by_type,
            'most_profitable_type': best_type,
            'seasonal_trend': self._analyze_seasonality(completed),
            'recommendations': self._generate_recommendations(avg_margin, by_type)
        }
    
    def _analyze_seasonality(self, jobs: List[PaintJob]) -> str:
        """Analyze seasonal trends"""
        # Simplified - would analyze by month
        return 'Exterior work peaks in spring/summer, Interior steady year-round'
    
    def _generate_recommendations(self, margin: float, by_type: Dict) -> List[str]:
        """Generate business recommendations"""
        recs = []
        
        if margin < 20:
            recs.append("REVIEW_PRICING - Margins below industry standard")
            recs.append("MATERIAL_COST_CONTROL - Negotiate supplier discounts")
        
        if margin > 35:
            recs.append("COMPETITIVE_POSITION - May have pricing power")
        
        # Check for profitable niches
        for ptype, data in by_type.items():
            if 'decorative' in ptype or 'faux' in ptype:
                recs.append(f"EXPAND_{ptype.upper()} - High-value specialty work")
        
        if not recs:
            recs.append("MAINTAIN_OPERATIONS - Continue current strategy")
        
        return recs
    
    def get_pricing_recommendations(self) -> Dict:
        """Get pricing recommendations by project type"""
        return {
            'interior_residential': {
                'range_per_sqft': '$2.00 - $4.50',
                'factors': ['Number of colors', 'Ceiling height', 'Furniture moving', 'Wall condition'],
                'upsell_opportunities': ['Cabinet refinishing', 'Accent walls', 'Decorative finishes']
            },
            'exterior_residential': {
                'range_per_sqft': '$2.00 - $5.50',
                'factors': ['Surface type', 'Height/scaffolding', 'Prep work needed', 'Number of stories'],
                'seasonal': 'Peak pricing in spring, discounts in winter'
            },
            'commercial': {
                'range_per_sqft': '$0.75 - $3.00',
                'factors': ['Volume discount', 'After-hours work premium', 'Maintenance contracts'],
                'strategy': 'Volume over margin, recurring revenue focus'
            },
            'specialty_services': {
                'wallpaper': '$8-15 per roll installed',
                'faux_finish': '$15-30 per sq ft',
                'cabinet_refinishing': '$75-150 per door',
                'strategy': 'Premium pricing for specialized skills'
            }
        }


# Usage
def estimate_painting_job(project_type: str, sqft: float, 
                         quality: str = 'standard', coats: int = 2) -> Dict:
    """Quick painting job estimate"""
    tracker = PaintingDecoratingTracker()
    return tracker.estimate_job_cost(project_type, sqft, ['drywall'], quality, coats)


def analyze_painting_business(jobs_data: List[Dict]) -> Dict:
    """Analyze painting business performance"""
    tracker = PaintingDecoratingTracker()
    
    for j in jobs_data:
        job = PaintJob(
            job_id=j['id'],
            client_name=j['client'],
            project_type=j.get('type', 'interior_residential'),
            square_feet=j['sqft'],
            surfaces=j.get('surfaces', ['drywall']),
            paint_quality=j.get('quality', 'standard'),
            num_colors=j.get('colors', 2),
            num_coats=j.get('coats', 2),
            quoted_price=j['price'],
            paint_materials_cost=j.get('materials', j['price'] * 0.25),
            labor_hours_estimated=j.get('hours_est', j['sqft'] / 100),
            labor_hours_actual=j.get('hours_actual'),
            start_date=j.get('start', date.today()),
            completion_date=j.get('completed'),
            status=j.get('status', 'completed')
        )
        tracker.add_job(job)
    
    return tracker.get_business_summary()


def get_painting_prices() -> Dict:
    """Get pricing guide"""
    tracker = PaintingDecoratingTracker()
    return tracker.get_pricing_recommendations()
