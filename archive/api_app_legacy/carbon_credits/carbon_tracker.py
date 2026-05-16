"""
Carbon Credits Tracker
======================
Track carbon credit markets, pricing, compliance
Voluntary and compliance markets, project types
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CarbonMarketType(Enum):
    COMPLIANCE = "compliance"  # EU ETS, California Cap-and-Trade
    VOLUNTARY = "voluntary"    # VCS, Gold Standard


class ProjectType(Enum):
    FORESTRY = "forestry"
    RENEWABLE = "renewable_energy"
    METHANE = "methane_capture"
    DIRECT_AIR = "direct_air_capture"
    SOIL = "soil_carbon"
    BLUE_CARBON = "blue_carbon"  # Mangroves, seagrass


@dataclass
class CarbonCredit:
    project_name: str
    project_type: str
    vintage: int
    tonnes_co2: float
    price_per_tonne: float
    verification_standard: str  # VCS, Gold Standard, CAR
    location: str
    additional_benefits: List[str]  # biodiversity, community, etc.


class CarbonCreditsTracker:
    """Track carbon credit investments and markets"""
    
    # Market prices per tonne CO2 (approximate)
    MARKET_PRICES = {
        'eu_ets': 85,  # EUR
        'california': 32,  # USD
        'rggi': 14,  # USD - Regional Greenhouse Gas Initiative
        'voluntary_nature': 15,  # Nature-based
        'voluntary_tech': 80,  # Technology-based (DAC)
        'forestry_redd': 8,
        'renewable': 3,
        'methane': 12
    }
    
    # Carbon credit ETFs and stocks
    INVESTMENT_VEHICLES = {
        'etfs': {
            'GRN': 'iPath Series B Carbon ETN (EU ETS)',
            'KOL': 'VanEck Coal ETF (inverse carbon play)',
            'PBW': 'Invesco WilderHill Clean Energy',
            'ICLN': 'iShares Global Clean Energy'
        },
        'carbon_credit_stocks': {
            'NETZ': 'Carbon Transition ETF',
            'PBR': 'Petrobras (carbon exposure)',
            'CEG': 'Constellation Energy (nuclear, low carbon)'
        },
        'project_developers': {
            'PRES': 'Perseus (carbon credit developer)',
            'CNT': 'Carbon Streaming Corp'
        }
    }
    
    def calculate_portfolio_value(self, credits: List[CarbonCredit]) -> Dict:
        """Calculate value of carbon credit portfolio"""
        if not credits:
            return {'error': 'No credits in portfolio'}
        
        total_tonnes = sum(c.tonnes_co2 for c in credits)
        total_value = sum(c.tonnes_co2 * c.price_per_tonne for c in credits)
        avg_price = total_value / total_tonnes if total_tonnes > 0 else 0
        
        # By project type
        by_type = {}
        for credit in credits:
            pt = credit.project_type
            if pt not in by_type:
                by_type[pt] = {'tonnes': 0, 'value': 0}
            by_type[pt]['tonnes'] += credit.tonnes_co2
            by_type[pt]['value'] += credit.tonnes_co2 * credit.price_per_tonne
        
        return {
            'total_credits': len(credits),
            'total_tonnes_co2': round(total_tonnes, 1),
            'portfolio_value_usd': round(total_value, 0),
            'average_price_per_tonne': round(avg_price, 2),
            'by_project_type': by_type,
            'co2_equivalent_cars': round(total_tonnes / 4.6, 0),  # Avg car annual emissions
            'timestamp': datetime.now().isoformat()
        }
    
    def get_market_outlook(self) -> Dict:
        """Get carbon credit market outlook"""
        return {
            'compliance_markets': {
                'eu_ets': {
                    'current_price': 85,
                    'trend': 'RISING',
                    'drivers': ['Fit for 55 package', 'CBAM implementation', 'Supply cuts']
                },
                'california': {
                    'current_price': 32,
                    'trend': 'STABLE',
                    'drivers': ['Cap reduction', 'Linkage with Quebec']
                }
            },
            'voluntary_markets': {
                'trend': 'GROWING_RAPIDLY',
                'projected_2030': '$50B',
                'key_buyers': ['Corporates (SBTi commitments)', 'Airlines (CORSIA)', 'Crypto (offsetting)'],
                'quality_concerns': ['Additionality', 'Permanence', 'Double counting']
            },
            'investment_thesis': {
                'bullish_factors': [
                    'Increasing global carbon pricing',
                    'Corporate net-zero commitments',
                    'Article 6 Paris Agreement implementation',
                    'Supply constraints in compliance markets'
                ],
                'risks': [
                    'Regulatory changes',
                    'Quality concerns in voluntary markets',
                    'Technological disruption (DAC)',
                    'Economic slowdown reducing demand'
                ],
                'recommendation': 'OVERWEIGHT - Structural growth story with policy tailwinds'
            }
        }
    
    def evaluate_project(self, project_type: str, location: str,
                        tonnes_annual: float, project_life_years: int) -> Dict:
        """Evaluate carbon credit project economics"""
        
        # Base carbon price by project type
        base_prices = {
            ProjectType.FORESTRY.value: 12,
            ProjectType.RENEWABLE.value: 4,
            ProjectType.METHANE.value: 15,
            ProjectType.DIRECT_AIR.value: 400,
            ProjectType.SOIL.value: 20,
            ProjectType.BLUE_CARBON.value: 25
        }
        
        price_per_tonne = base_prices.get(project_type, 10)
        
        # Annual revenue
        annual_revenue = tonnes_annual * price_per_tonne
        
        # Total project revenue
        total_revenue = annual_revenue * project_life_years
        
        # Costs (varies by type)
        cost_factors = {
            ProjectType.FORESTRY.value: 0.3,  # 30% of revenue
            ProjectType.RENEWABLE.value: 0.1,
            ProjectType.METHANE.value: 0.25,
            ProjectType.DIRECT_AIR.value: 0.7,
            ProjectType.SOIL.value: 0.4,
            ProjectType.BLUE_CARBON.value: 0.35
        }
        
        cost_pct = cost_factors.get(project_type, 0.3)
        total_costs = total_revenue * cost_pct
        
        # Net project value
        npv = total_revenue - total_costs
        
        return {
            'project_type': project_type,
            'location': location,
            'annual_tonnes': tonnes_annual,
            'project_life': project_life_years,
            'price_per_tonne': price_per_tonne,
            'annual_revenue': round(annual_revenue, 0),
            'total_revenue': round(total_revenue, 0),
            'total_costs': round(total_costs, 0),
            'net_project_value': round(npv, 0),
            'roi_pct': round((npv / total_costs) * 100, 1) if total_costs > 0 else 0,
            'payback_years': round(total_costs / annual_revenue, 1) if annual_revenue > 0 else 0,
            'viable': npv > 0
        }


# Usage
def evaluate_carbon_portfolio(credits: List[Dict]) -> Dict:
    """Quick carbon portfolio evaluation"""
    tracker = CarbonCreditsTracker()
    
    credit_objects = [
        CarbonCredit(
            project_name=c['name'],
            project_type=c['type'],
            vintage=c['vintage'],
            tonnes_co2=c['tonnes'],
            price_per_tonne=c['price'],
            verification_standard=c.get('standard', 'VCS'),
            location=c.get('location', 'Unknown'),
            additional_benefits=c.get('benefits', [])
        )
        for c in credits
    ]
    
    return tracker.calculate_portfolio_value(credit_objects)


def analyze_carbon_project(project_type: str, location: str,
                            tonnes: float, years: int) -> Dict:
    """Analyze carbon project economics"""
    tracker = CarbonCreditsTracker()
    return tracker.evaluate_project(project_type, location, tonnes, years)
