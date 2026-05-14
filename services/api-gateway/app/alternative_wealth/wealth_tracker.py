"""
Alternative Wealth Tracker
=========================
Comprehensive tracking of non-traditional income sources
Content creation, digital products, physical businesses, IP
Passive income, side hustles, alternative investments
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IncomeType(Enum):
    CONTENT_CREATION = "content_creation"
    DIGITAL_PRODUCTS = "digital_products"
    PHYSICAL_BUSINESS = "physical_business"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    SHARING_ECONOMY = "sharing_economy"
    ALTERNATIVE_INVESTMENTS = "alternative_investments"
    ENERGY_INFRASTRUCTURE = "energy_infrastructure"
    DIGITAL_ASSETS = "digital_assets"


@dataclass
class IncomeStream:
    """Alternative income stream"""
    name: str
    income_type: str
    monthly_revenue: float
    monthly_expenses: float
    hours_per_month: float
    start_date: datetime
    scalability: str  # 'high', 'medium', 'low'
    passive_score: int  # 1-10 (10 = fully passive)
    notes: str = ""


class AlternativeWealthTracker:
    """
    Track and optimize alternative wealth generation methods
    
    Covers 50+ alternative income sources beyond traditional investing
    """
    
    def __init__(self):
        self.income_streams: List[IncomeStream] = []
        
    # ===== 1. CONTENT CREATION ECONOMY =====
    
    def add_youtube_channel(self, subscribers: int, avg_views: int,
                          cpm: float = 4.0, name: str = "YouTube Channel"):
        """
        Add YouTube channel income
        
        Revenue estimate: Views/1000 * CPM
        """
        monthly_views = avg_views * 4  # 4 videos per month
        revenue = (monthly_views / 1000) * cpm
        
        # Add affiliate/merch (typically 2x AdSense)
        total_revenue = revenue * 3
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.CONTENT_CREATION.value,
            monthly_revenue=total_revenue,
            monthly_expenses=500,  # Equipment, editing software
            hours_per_month=40,
            start_date=datetime.now(),
            scalability='high',
            passive_score=7,  # Content lives forever
            notes=f"{subscribers} subs, {avg_views} avg views"
        )
        
        self.income_streams.append(stream)
        return stream
    
    def add_newsletter(self, subscribers: int, 
                      monthly_price: float = 10,
                      name: str = "Paid Newsletter"):
        """
        Add newsletter income (Substack model)
        
        Revenue: Subscribers * Monthly Price * Conversion Rate (5%)
        """
        paying_subs = int(subscribers * 0.05)  # 5% conversion
        revenue = paying_subs * monthly_price
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.CONTENT_CREATION.value,
            monthly_revenue=revenue,
            monthly_expenses=50,  # Platform fees
            hours_per_month=20,
            start_date=datetime.now(),
            scalability='high',
            passive_score=9,  # Written once, read forever
            notes=f"{subscribers} total, {paying_subs} paying"
        )
        
        self.income_streams.append(stream)
        return stream
    
    def add_podcast(self, downloads_per_episode: int,
                   episodes_per_month: int = 4,
                   name: str = "Podcast"):
        """Add podcast sponsorship income"""
        # CPM $25-50 for podcasts
        cpm = 30
        monthly_downloads = downloads_per_episode * episodes_per_month
        revenue = (monthly_downloads / 1000) * cpm
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.CONTENT_CREATION.value,
            monthly_revenue=revenue,
            monthly_expenses=100,  # Hosting, equipment
            hours_per_month=16,
            start_date=datetime.now(),
            scalability='medium',
            passive_score=8,
            notes=f"{monthly_downloads} monthly downloads"
        )
        
        self.income_streams.append(stream)
        return stream
    
    # ===== 2. DIGITAL PRODUCTS =====
    
    def add_saas_mrr(self, monthly_recurring_revenue: float,
                    customers: int, churn_rate: float = 0.05,
                    name: str = "SaaS Business"):
        """Add SaaS MRR tracking"""
        # Account for churn
        effective_revenue = monthly_recurring_revenue * (1 - churn_rate)
        
        # Expenses typically 30-50% for SaaS
        expenses = monthly_recurring_revenue * 0.4
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.DIGITAL_PRODUCTS.value,
            monthly_revenue=effective_revenue,
            monthly_expenses=expenses,
            hours_per_month=80,
            start_date=datetime.now(),
            scalability='high',
            passive_score=6,  # Requires maintenance
            notes=f"{customers} customers, {churn_rate*100}% churn"
        )
        
        self.income_streams.append(stream)
        return stream
    
    def add_online_course(self, price: float, 
                         monthly_sales: int,
                         platform_fee_pct: float = 0.30,
                         name: str = "Online Course"):
        """Add online course income (Udemy/Teachable)"""
        gross_revenue = price * monthly_sales
        net_revenue = gross_revenue * (1 - platform_fee_pct)
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.DIGITAL_PRODUCTS.value,
            monthly_revenue=net_revenue,
            monthly_expenses=100,  # Platform, ads
            hours_per_month=5,  # Support only after creation
            start_date=datetime.now(),
            scalability='high',
            passive_score=9,
            notes=f"${price} course, {monthly_sales} monthly sales"
        )
        
        self.income_streams.append(stream)
        return stream
    
    def add_mobile_app(self, monthly_downloads: int,
                      arpu: float = 2.0,  # Average revenue per user
                      name: str = "Mobile App"):
        """Add mobile app store income"""
        revenue = monthly_downloads * arpu
        
        # App store takes 30%
        net_revenue = revenue * 0.7
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.DIGITAL_PRODUCTS.value,
            monthly_revenue=net_revenue,
            monthly_expenses=200,  # Maintenance, ASO
            hours_per_month=10,
            start_date=datetime.now(),
            scalability='high',
            passive_score=7,
            notes=f"{monthly_downloads} downloads/month"
        )
        
        self.income_streams.append(stream)
        return stream
    
    # ===== 3. PHYSICAL BUSINESSES =====
    
    def add_laundromat(self, machines: int, 
                      avg_daily_revenue_per_machine: float = 50,
                      rent: float = 2000,
                      name: str = "Laundromat"):
        """Add laundromat passive income"""
        monthly_revenue = machines * avg_daily_revenue_per_machine * 30
        expenses = rent + (machines * 100)  # Utilities, maintenance
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.PHYSICAL_BUSINESS.value,
            monthly_revenue=monthly_revenue,
            monthly_expenses=expenses,
            hours_per_month=20,  # Collection, maintenance
            start_date=datetime.now(),
            scalability='low',
            passive_score=8,
            notes=f"{machines} machines"
        )
        
        self.income_streams.append(stream)
        return stream
    
    def add_vending_machine_route(self, machines: int,
                                   avg_monthly_per_machine: float = 300,
                                   name: str = "Vending Route"):
        """Add vending machine route income"""
        revenue = machines * avg_monthly_per_machine
        expenses = machines * 50  # Product, maintenance
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.PHYSICAL_BUSINESS.value,
            monthly_revenue=revenue,
            monthly_expenses=expenses,
            hours_per_month=40,  # Restocking
            start_date=datetime.now(),
            scalability='medium',
            passive_score=7,
            notes=f"{machines} machines"
        )
        
        self.income_streams.append(stream)
        return stream
    
    def add_car_wash(self, bays: int,
                    avg_daily_per_bay: float = 200,
                    name: str = "Car Wash"):
        """Add car wash investment"""
        monthly_revenue = bays * avg_daily_per_bay * 30
        expenses = 3000 + (bays * 500)  # Rent, utilities, soap
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.PHYSICAL_BUSINESS.value,
            monthly_revenue=monthly_revenue,
            monthly_expenses=expenses,
            hours_per_month=10,  # Minimal if automated
            start_date=datetime.now(),
            scalability='medium',
            passive_score=9,
            notes=f"{bays} bays, automated"
        )
        
        self.income_streams.append(stream)
        return stream
    
    # ===== 4. SHARING ECONOMY =====
    
    def add_turo_car(self, car_value: float,
                    monthly_days_rented: int = 15,
                    daily_rate: float = 50,
                    name: str = "Turo Car"):
        """Add Turo car rental income"""
        revenue = monthly_days_rented * daily_rate
        
        # Insurance, depreciation, cleaning
        expenses = 200 + (car_value * 0.01)  # 1% monthly depreciation
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.SHARING_ECONOMY.value,
            monthly_revenue=revenue,
            monthly_expenses=expenses,
            hours_per_month=4,
            start_date=datetime.now(),
            scalability='medium',
            passive_score=8,
            notes=f"{monthly_days_rented} days rented"
        )
        
        self.income_streams.append(stream)
        return stream
    
    def add_airbnb_arbitrage(self, units: int,
                            avg_monthly_revenue_per_unit: float = 2500,
                            rent_per_unit: float = 1500,
                            name: str = "Airbnb Arbitrage"):
        """Add Airbnb rental arbitrage (rent and re-rent)"""
        revenue = units * avg_monthly_revenue_per_unit
        expenses = units * (rent_per_unit + 500)  # Rent + utilities/cleaning
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.SHARING_ECONOMY.value,
            monthly_revenue=revenue,
            monthly_expenses=expenses,
            hours_per_month=20 * units,
            start_date=datetime.now(),
            scalability='high',
            passive_score=5,  # Requires management
            notes=f"{units} units, rental arbitrage model"
        )
        
        self.income_streams.append(stream)
        return stream
    
    # ===== 5. INTELLECTUAL PROPERTY =====
    
    def add_book_royalties(self, books: int,
                          avg_monthly_per_book: float = 200,
                          name: str = "Book Royalties"):
        """Add book publishing income"""
        revenue = books * avg_monthly_per_book
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.INTELLECTUAL_PROPERTY.value,
            monthly_revenue=revenue,
            monthly_expenses=0,
            hours_per_month=0,  # Passive
            start_date=datetime.now(),
            scalability='high',
            passive_score=10,
            notes=f"{books} books published"
        )
        
        self.income_streams.append(stream)
        return stream
    
    def add_music_streaming(self, tracks: int,
                           avg_monthly_streams_per_track: int = 1000,
                           name: str = "Music Royalties"):
        """Add Spotify/Apple Music streaming income"""
        # ~$0.003 per stream
        revenue_per_stream = 0.003
        total_streams = tracks * avg_monthly_streams_per_track
        revenue = total_streams * revenue_per_stream
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.INTELLECTUAL_PROPERTY.value,
            monthly_revenue=revenue,
            monthly_expenses=0,
            hours_per_month=0,
            start_date=datetime.now(),
            scalability='high',
            passive_score=10,
            notes=f"{tracks} tracks, {total_streams} monthly streams"
        )
        
        self.income_streams.append(stream)
        return stream
    
    def add_patent_licensing(self, patents: int,
                            avg_monthly_per_patent: float = 500,
                            name: str = "Patent Licensing"):
        """Add patent licensing income"""
        revenue = patents * avg_monthly_per_patent
        
        stream = IncomeStream(
            name=name,
            income_type=IncomeType.INTELLECTUAL_PROPERTY.value,
            monthly_revenue=revenue,
            monthly_expenses=50,  # Legal maintenance
            hours_per_month=2,
            start_date=datetime.now(),
            scalability='high',
            passive_score=10,
            notes=f"{patents} licensed patents"
        )
        
        self.income_streams.append(stream)
        return stream
    
    # ===== ANALYTICS & SUMMARY =====
    
    def get_wealth_summary(self) -> Dict:
        """Get comprehensive alternative wealth summary"""
        if not self.income_streams:
            return {'error': 'No income streams tracked'}
        
        total_monthly_revenue = sum(s.monthly_revenue for s in self.income_streams)
        total_monthly_expenses = sum(s.monthly_expenses for s in self.income_streams)
        total_monthly_profit = total_monthly_revenue - total_monthly_expenses
        total_hours = sum(s.hours_per_month for s in self.income_streams)
        
        # Group by type
        by_type = {}
        for stream in self.income_streams:
            if stream.income_type not in by_type:
                by_type[stream.income_type] = []
            by_type[stream.income_type].append(stream)
        
        # Calculate passive income (score >= 8)
        passive_streams = [s for s in self.income_streams if s.passive_score >= 8]
        passive_monthly = sum(s.monthly_revenue - s.monthly_expenses for s in passive_streams)
        
        return {
            'total_monthly_revenue': round(total_monthly_revenue, 2),
            'total_monthly_expenses': round(total_monthly_expenses, 2),
            'total_monthly_profit': round(total_monthly_profit, 2),
            'annual_profit_projection': round(total_monthly_profit * 12, 2),
            'total_hours_per_month': round(total_hours, 1),
            'hourly_rate': round(total_monthly_profit / total_hours, 2) if total_hours > 0 else 0,
            'passive_monthly_income': round(passive_monthly, 2),
            'passive_annual_income': round(passive_monthly * 12, 2),
            'passive_percentage': round(passive_monthly / total_monthly_profit * 100, 1) if total_monthly_profit > 0 else 0,
            'streams_by_type': {k: len(v) for k, v in by_type.items()},
            'top_performers': [
                {
                    'name': s.name,
                    'monthly_profit': round(s.monthly_revenue - s.monthly_expenses, 2),
                    'passive_score': s.passive_score
                }
                for s in sorted(self.income_streams, 
                              key=lambda x: x.monthly_revenue - x.monthly_expenses, 
                              reverse=True)[:5]
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_passive_income_roadmap(self, target_monthly: float = 5000) -> Dict:
        """Generate roadmap to reach passive income target"""
        current = self.get_wealth_summary()
        current_passive = current.get('passive_monthly_income', 0)
        gap = target_monthly - current_passive
        
        if gap <= 0:
            return {'status': 'TARGET_REACHED', 'message': 'Already at target!'}
        
        # Suggest income streams to add
        suggestions = []
        
        # If gap is large, suggest scalable options
        if gap > 3000:
            suggestions.append({
                'type': 'SaaS Business',
                'target_mrr': gap,
                'time_to_build': '6-12 months',
                'passive_score': 6
            })
        
        if gap > 2000:
            suggestions.append({
                'type': 'Online Course',
                'target_monthly_sales': int(gap / 100),  # $100 course
                'time_to_build': '2-3 months',
                'passive_score': 9
            })
        
        if gap > 1000:
            suggestions.append({
                'type': 'YouTube Channel',
                'target_monthly_views': int(gap * 1000 / 4),  # $4 CPM
                'time_to_build': '6-12 months',
                'passive_score': 7
            })
        
        suggestions.append({
            'type': 'Laundromat/Car Wash',
            'investment_needed': gap * 50,  # 50x monthly income
            'time_to_build': '1-2 months',
            'passive_score': 9
        })
        
        return {
            'current_passive_income': round(current_passive, 2),
            'target_monthly': target_monthly,
            'gap': round(gap, 2),
            'suggestions': suggestions,
            'estimated_timeline': '1-3 years depending on effort'
        }


# Usage
def quick_income_analysis() -> Dict:
    """Quick demo of alternative wealth tracking"""
    tracker = AlternativeWealthTracker()
    
    # Add some example streams
    tracker.add_youtube_channel(10000, 5000, name="Finance Channel")
    tracker.add_online_course(199, 20, name="Trading Masterclass")
    tracker.add_laundromat(15, name="Downtown Laundromat")
    tracker.add_turo_car(25000, name="Tesla Model 3")
    tracker.add_book_royalties(2, name="Investment Books")
    
    return tracker.get_wealth_summary()


def calculate_passive_income_target(monthly_target: float) -> Dict:
    """Calculate what it takes to reach passive income target"""
    tracker = AlternativeWealthTracker()
    return tracker.get_passive_income_roadmap(monthly_target)
