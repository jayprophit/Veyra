"""
Geopolitical Risk Monitor
=========================
Track geopolitical risks and their market impact
Country risk scores, sanctions tracking, conflict zones
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GeopoliticalEvent:
    event_type: str
    region: str
    countries: List[str]
    risk_level: str
    market_impact: str
    affected_sectors: List[str]
    timestamp: datetime
    description: str


class GeopoliticalRiskMonitor:
    """Monitor geopolitical risks and market impacts"""
    
    # Country risk scores (0-100, higher = riskier)
    COUNTRY_RISKS = {
        'RUSSIA': {'score': 85, 'issues': ['Sanctions', 'Ukraine conflict', 'Isolation']},
        'UKRAINE': {'score': 90, 'issues': ['Active war', 'Infrastructure damage', 'Economic collapse']},
        'CHINA': {'score': 55, 'issues': ['Taiwan tension', 'Tech restrictions', 'Property crisis']},
        'IRAN': {'score': 80, 'issues': ['Nuclear program', 'Sanctions', 'Regional tensions']},
        'NORTH_KOREA': {'score': 75, 'issues': ['Nuclear threat', 'Instability', 'Sanctions']},
        'VENEZUELA': {'score': 70, 'issues': ['Political crisis', 'Economic collapse', 'Sanctions']},
        'TAIWAN': {'score': 60, 'issues': ['China tension', 'Strategic importance', 'Semiconductor chokepoint']},
        'ISRAEL': {'score': 65, 'issues': ['Regional conflicts', 'Iran tension', 'Security focused']},
        'SAUDI_ARABIA': {'score': 50, 'issues': ['Regional rivalry', 'Oil dependence', 'Reform risks']},
        'BRAZIL': {'score': 45, 'issues': ['Political polarization', 'Economic volatility']}
    }
    
    # Ongoing conflicts and tensions
    ACTIVE_CONFLICTS = {
        'russia_ukraine': {
            'start_date': '2022-02-24',
            'severity': 'HIGH',
            'impact': 'Energy prices, food security, defense spending',
            'affected_sectors': ['Energy', 'Agriculture', 'Defense', 'Aerospace']
        },
        'israel_gaza': {
            'start_date': '2023-10-07',
            'severity': 'HIGH',
            'impact': 'Regional stability, energy routes, humanitarian',
            'affected_sectors': ['Defense', 'Energy', 'Travel', 'Insurance']
        },
        'china_taiwan_tension': {
            'start_date': 'ongoing',
            'severity': 'MEDIUM',
            'impact': 'Semiconductor supply chain, tech trade, strategic competition',
            'affected_sectors': ['Semiconductors', 'Technology', 'Defense', 'Shipping']
        },
        'iran_tensions': {
            'start_date': 'ongoing',
            'severity': 'MEDIUM',
            'impact': 'Oil prices, regional stability, shipping routes',
            'affected_sectors': ['Energy', 'Shipping', 'Insurance']
        }
    }
    
    def get_country_risk(self, country: str) -> Dict:
        """Get country risk assessment"""
        country_upper = country.upper()
        
        if country_upper not in self.COUNTRY_RISKS:
            return {'error': f'No risk data for {country}'}
        
        data = self.COUNTRY_RISKS[country_upper]
        
        return {
            'country': country,
            'risk_score': data['score'],
            'risk_level': self._score_to_level(data['score']),
            'key_issues': data['issues'],
            'investment_recommendation': self._country_recommendation(data['score']),
            'timestamp': datetime.now().isoformat()
        }
    
    def _score_to_level(self, score: int) -> str:
        """Convert score to risk level"""
        if score >= 80:
            return RiskLevel.CRITICAL.value
        elif score >= 60:
            return RiskLevel.HIGH.value
        elif score >= 40:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value
    
    def _country_recommendation(self, score: int) -> str:
        """Generate investment recommendation"""
        if score >= 80:
            return 'AVOID - Extreme risk, consider exiting positions'
        elif score >= 60:
            return 'CAUTION - High risk, limit exposure, hedges required'
        elif score >= 40:
            return 'SELECTIVE - Moderate risk, quality assets only'
        else:
            return 'STANDARD_RISK - Normal due diligence applies'
    
    def get_conflict_impact(self, conflict_id: str) -> Dict:
        """Get specific conflict impact analysis"""
        if conflict_id not in self.ACTIVE_CONFLICTS:
            return {'error': f'Conflict {conflict_id} not found'}
        
        conflict = self.ACTIVE_CONFLICTS[conflict_id]
        
        return {
            'conflict': conflict_id,
            'start_date': conflict['start_date'],
            'severity': conflict['severity'],
            'market_impact_summary': conflict['impact'],
            'affected_sectors': conflict['affected_sectors'],
            'hedge_recommendations': self._generate_hedges(conflict['affected_sectors']),
            'opportunity_sectors': self._generate_opportunities(conflict['severity'])
        }
    
    def _generate_hedges(self, sectors: List[str]) -> List[str]:
        """Generate hedge recommendations"""
        hedges = []
        
        if 'Energy' in sectors:
            hedges.extend([
                'Long crude oil futures',
                'Energy sector put options',
                'Renewable energy long exposure'
            ])
        
        if 'Semiconductors' in sectors:
            hedges.extend([
                'SOXX put spreads',
                'Diversify chip exposure geographically',
                'Monitor inventory levels'
            ])
        
        if 'Shipping' in sectors:
            hedges.extend([
                'Baltic Dry Index monitoring',
                'Container shipping rate hedges',
                'Alternative route planning'
            ])
        
        if 'Defense' in sectors:
            hedges.extend([
                'Long defense contractors (RTX, LMT, NOC)',
                'NATO member defense stocks'
            ])
        
        return hedges
    
    def _generate_opportunities(self, severity: str) -> List[str]:
        """Generate opportunity recommendations"""
        if severity == 'HIGH':
            return [
                'Defense contractors - increased spending',
                'Energy - supply disruptions create pricing power',
                'Cybersecurity - state-sponsored threats increase',
                'Gold/USD - safe haven flows',
                'Agriculture - food security priority'
            ]
        elif severity == 'MEDIUM':
            return [
                'Selective defense exposure',
                'Regional diversification',
                'Supply chain monitoring'
            ]
        else:
            return ['Normal market conditions prevail']
    
    def get_global_risk_dashboard(self) -> Dict:
        """Get global geopolitical risk dashboard"""
        
        # Calculate average risk
        scores = [c['score'] for c in self.COUNTRY_RISKS.values()]
        avg_risk = sum(scores) / len(scores)
        
        # High risk countries
        high_risk = [
            {'country': k, 'score': v['score']}
            for k, v in self.COUNTRY_RISKS.items()
            if v['score'] >= 70
        ]
        
        # Risk trends (would be dynamic in production)
        trends = {
            'escalating': ['Russia-Ukraine', 'Middle East tensions'],
            'stable': ['US-China trade (controlled decoupling)'],
            'improving': ['Venezuela (slow stabilization)']
        }
        
        return {
            'global_avg_risk_score': round(avg_risk, 1),
            'risk_level': self._score_to_level(int(avg_risk)),
            'high_risk_countries': sorted(high_risk, key=lambda x: x['score'], reverse=True),
            'active_conflict_count': len(self.ACTIVE_CONFLICTS),
            'risk_trends': trends,
            'market_implications': {
                'volatility_expectation': 'ELEVATED' if avg_risk > 60 else 'NORMAL',
                'safe_haven_flows': 'LIKELY' if any(c['score'] > 80 for c in self.COUNTRY_RISKS.values()) else 'NORMAL',
                'energy_premium': 'SUSTAINED' if 'RUSSIA' in self.COUNTRY_RISKS else 'NORMAL'
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_sector_risk_exposure(self, sectors: List[str]) -> Dict:
        """Get geopolitical risk exposure by sector"""
        
        sector_risks = {
            'Energy': {
                'risk_score': 75,
                'key_threats': ['Middle East instability', 'Russian sanctions', 'Strait of Hormuz'],
                'mitigation': 'Diversify sources, strategic reserves'
            },
            'Semiconductors': {
                'risk_score': 70,
                'key_threats': ['Taiwan tension', 'China tech war', 'Supply concentration'],
                'mitigation': 'Reshoring, alternative suppliers, inventory'
            },
            'Technology': {
                'risk_score': 60,
                'key_threats': ['Data sovereignty', 'Export controls', 'Cyber warfare'],
                'mitigation': 'Geographic diversification, compliance focus'
            },
            'Defense': {
                'risk_score': 55,
                'key_threats': ['Budget dependency', 'Political cycles'],
                'mitigation': 'NATO exposure, multi-year contracts'
            },
            'Agriculture': {
                'risk_score': 65,
                'key_threats': ['Export restrictions', 'Climate change', 'Ukraine supply'],
                'mitigation': 'Diverse sourcing, futures hedging'
            }
        }
        
        results = {}
        for sector in sectors:
            if sector in sector_risks:
                results[sector] = sector_risks[sector]
        
        return {
            'sector_exposures': results,
            'avg_sector_risk': round(
                sum(s['risk_score'] for s in results.values()) / len(results), 1
            ) if results else 0,
            'highest_risk_sector': max(results.items(), key=lambda x: x[1]['risk_score'])[0] if results else None
        }


# Usage
def check_country_risk(country: str) -> Dict:
    """Quick country risk check"""
    monitor = GeopoliticalRiskMonitor()
    return monitor.get_country_risk(country)


def get_conflict_analysis(conflict: str) -> Dict:
    """Get conflict impact analysis"""
    monitor = GeopoliticalRiskMonitor()
    return monitor.get_conflict_impact(conflict)


def get_global_risk_summary() -> Dict:
    """Get global risk dashboard"""
    monitor = GeopoliticalRiskMonitor()
    return monitor.get_global_risk_dashboard()
