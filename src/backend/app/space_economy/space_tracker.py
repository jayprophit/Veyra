"""
Space Economy Tracker
=====================
Track space economy investments: SpaceX, Blue Origin, satellite companies
Asteroid mining, space tourism, lunar real estate, orbital manufacturing
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass
class SpaceCompany:
    name: str
    ticker: Optional[str]
    sector: str
    stage: str  # 'public', 'private', 'pre-ipo'
    valuation: float
    focus: str


class SpaceEconomyTracker:
    """
    Track the emerging space economy
    
    Sectors:
    - Launch services (rockets)
    - Satellite services (communications, imaging)
    - Space tourism (human spaceflight)
    - In-orbit manufacturing
    - Asteroid mining (future)
    - Lunar/Mars infrastructure
    """
    
    COMPANIES = [
        # Launch Services
        SpaceCompany('SpaceX', 'PRIVATE', 'launch', 'private', 180000000000, 
                    'reusable rockets, Starlink, Starship'),
        SpaceCompany('Rocket Lab', 'RKLB', 'launch', 'public', 2500000000,
                    'small sat launch, Electron rocket'),
        SpaceCompany('Virgin Galactic', 'SPCE', 'space_tourism', 'public', 1500000000,
                    'suborbital tourism, SpaceShipTwo'),
        SpaceCompany('Astra Space', 'ASTR', 'launch', 'public', 300000000,
                    'small sat launch'),
        SpaceCompany('Relativity Space', 'PRIVATE', 'launch', 'private', 4200000000,
                    '3D printed rockets'),
        
        # Satellite Services
        SpaceCompany('Intelsat', 'INTE', 'satellite_comms', 'public', 3000000000,
                    'GEO satellite communications'),
        SpaceCompany('SES', 'SESG', 'satellite_comms', 'public', 5000000000,
                    'satellite communications'),
        SpaceCompany('Iridium', 'IRDM', 'satellite_comms', 'public', 6000000000,
                    'LEO satellite constellation'),
        SpaceCompany('Globalstar', 'GSAT', 'satellite_comms', 'public', 2500000000,
                    'satellite messaging'),
        SpaceCompany('AST SpaceMobile', 'ASTS', 'satellite_comms', 'public', 3000000000,
                    'space-based cellular broadband'),
        SpaceCompany('Planet Labs', 'PL', 'satellite_imaging', 'public', 2500000000,
                    'Earth imaging satellites'),
        SpaceCompany('BlackSky', 'BKSY', 'satellite_imaging', 'public', 500000000,
                    'real-time geospatial intelligence'),
        SpaceCompany('Spire', 'SPIR', 'satellite_data', 'public', 400000000,
                    'weather and maritime data'),
        
        # Space Infrastructure
        SpaceCompany('Redwire', 'RDW', 'space_infrastructure', 'public', 1500000000,
                    'space manufacturing, on-orbit servicing'),
        SpaceCompany('Momentus', 'MNTS', 'space_infrastructure', 'public', 200000000,
                    'in-space transportation'),
        SpaceCompany('Axiom Space', 'PRIVATE', 'space_stations', 'private', 1300000000,
                    'commercial space stations'),
        SpaceCompany('Sierra Space', 'PRIVATE', 'space_stations', 'private', 3000000000,
                    'Dream Chaser, LIFE habitat'),
        
        # Materials & Manufacturing
        SpaceCompany('Varda Space', 'PRIVATE', 'in_orbit_manufacturing', 'private', 500000000,
                    'microgravity manufacturing'),
        SpaceCompany('Space Tango', 'PRIVATE', 'in_orbit_manufacturing', 'private', 100000000,
                    'automated research in space'),
        
        # Resources (Asteroid Mining - Future)
        SpaceCompany('Planetary Resources', 'PRIVATE', 'asteroid_mining', 'defunct', 0,
                    'acquired by ConsenSys'),
        SpaceCompany('Deep Space Industries', 'PRIVATE', 'asteroid_mining', 'defunct', 0,
                    'acquired by Bradford Space'),
        SpaceCompany('TransAstra', 'PRIVATE', 'asteroid_mining', 'private', 50000000,
                    'optical mining technology'),
        
        # Ground Infrastructure
        SpaceCompany('Kratos Defense', 'KTOS', 'ground_systems', 'public', 2500000000,
                    'satellite ground systems'),
        SpaceCompany('Gilat Satellite', 'GILT', 'ground_systems', 'public', 800000000,
                    'satellite networking'),
    ]
    
    def __init__(self):
        self.market_size_2040 = 1000000000000  # $1T projected
    
    def get_by_sector(self, sector: str) -> List[SpaceCompany]:
        """Get companies by space sector"""
        return [c for c in self.COMPANIES if c.sector == sector]
    
    def get_public_companies(self) -> List[SpaceCompany]:
        """Get publicly traded space companies"""
        return [c for c in self.COMPANIES if c.stage == 'public']
    
    def get_private_unicorns(self) -> List[SpaceCompany]:
        """Get private companies valued over $1B"""
        return [c for c in self.COMPANIES if c.stage == 'private' and c.valuation >= 1000000000]
    
    def get_investment_themes(self) -> Dict:
        """Get space economy investment themes"""
        return {
            'launch_services': {
                'description': 'Rocket launch providers and space transportation',
                'market_size_2030': '50000000000',
                'key_companies': ['SpaceX', 'Rocket Lab', 'Relativity'],
                'growth_drivers': [
                    'Reusable rocket technology lowering costs',
                    'Increased satellite deployment (Starlink, OneWeb)',
                    'Government contracts (NASA, DoD)',
                    'Space tourism demand'
                ],
                'risks': [
                    'High capital requirements',
                    'Technical failures',
                    'Regulatory delays'
                ]
            },
            'satellite_services': {
                'description': 'Satellite communications, Earth observation, navigation',
                'market_size_2030': '150000000000',
                'key_companies': ['Iridium', 'Planet Labs', 'AST SpaceMobile'],
                'growth_drivers': [
                    '5G from space (AST SpaceMobile)',
                    'IoT connectivity everywhere',
                    'Climate monitoring demand',
                    'Agriculture optimization'
                ],
                'risks': [
                    'Orbital debris',
                    'Spectrum interference',
                    'Competition from terrestrial 5G'
                ]
            },
            'space_infrastructure': {
                'description': 'Space stations, in-orbit servicing, manufacturing',
                'market_size_2030': '25000000000',
                'key_companies': ['Axiom Space', 'Sierra Space', 'Redwire'],
                'growth_drivers': [
                    'ISS retirement in 2030',
                    'Pharmaceutical manufacturing in microgravity',
                    'Fiber optic manufacturing',
                    'Tourism destinations'
                ],
                'risks': [
                    'Unproven business models',
                    'High development costs',
                    'Technical complexity'
                ]
            },
            'in_orbit_manufacturing': {
                'description': 'Manufacturing in microgravity environment',
                'market_size_2040': '20000000000',
                'key_companies': ['Varda Space', 'Space Tango'],
                'growth_drivers': [
                    'Perfect fiber optics (ZBLAN)',
                    'Protein crystallization for drugs',
                    'Semiconductor manufacturing',
                    'Novel material alloys'
                ],
                'risks': [
                    'Early stage technology',
                    'Return logistics challenges',
                    'Uncertain economics'
                ]
            },
            'asteroid_mining': {
                'description': 'Extraction of resources from asteroids',
                'market_size_2050': '100000000000',
                'key_companies': ['TransAstra'],
                'growth_drivers': [
                    'Platinum group metals scarcity',
                    'Water for rocket fuel in space',
                    'Construction materials',
                    'Environmental benefits (less Earth mining)'
                ],
                'risks': [
                    'Technology not mature',
                    'Legal framework uncertain',
                    'Decades to profitability',
                    'High initial investment'
                ]
            },
            'space_tourism': {
                'description': 'Commercial human spaceflight',
                'market_size_2030': '8000000000',
                'key_companies': ['Virgin Galactic', 'Blue Origin', 'SpaceX'],
                'growth_drivers': [
                    'Wealthy individuals demand',
                    'Price reduction over time',
                    'Orbital hotels planned',
                    'Lunar tourism potential'
                ],
                'risks': [
                    'Safety concerns',
                    'High ticket prices limit market',
                    'Regulatory hurdles',
                    'Accident could halt industry'
                ]
            }
        }
    
    def get_space_resource_targets(self) -> Dict:
        """Get asteroid mining target data"""
        return {
            'near_earth_asteroids': {
                'total_count': 30000,
                'minable_count': 1500,
                'accessibility': 'Reachable with current technology'
            },
            'key_resources': {
                'water': {
                    'value': ' rocket fuel (LH2/LOX) and life support',
                    'estimated_value_per_ton': 50000000,  # Cost to launch from Earth
                    'market': 'In-space refueling'
                },
                'platinum_group_metals': {
                    'value': 'Industrial and catalytic applications',
                    'estimated_value_per_ton': 50000000,
                    'market': 'Earth-based manufacturing'
                },
                'iron_nickel': {
                    'value': 'Construction materials in space',
                    'estimated_value_per_ton': 10000,
                    'market': 'In-space construction'
                },
                'rare_earth_elements': {
                    'value': 'Electronics manufacturing',
                    'estimated_value_per_ton': 1000000,
                    'market': 'Technology production'
                }
            },
            'target_asteroids': [
                {'name': 'Ryugu', 'type': 'C-type', 'distance_km': 300000000, 'resources': 'water, organics'},
                {'name': 'Bennu', 'type': 'B-type', 'distance_km': 300000000, 'resources': 'water, carbon'},
                {'name': '16 Psyche', 'type': 'M-type', 'distance_km': 400000000, 'resources': 'iron, nickel, gold'},
            ]
        }
    
    def get_lunar_economy_projection(self) -> Dict:
        """Get lunar economy projections"""
        return {
            'milestones': {
                '2025': 'Artemis III - First crewed lunar landing',
                '2028': 'Lunar Gateway operational',
                '2030': 'Sustained lunar presence',
                '2035': 'Lunar mining operations begin',
                '2040': 'Lunar manufacturing starts'
            },
            'resources': {
                'water_ice': {
                    'location': 'South pole permanently shadowed regions',
                    'use': 'Drinking water, rocket fuel, oxygen',
                    'estimated_reserves_tons': 600000000
                },
                'helium_3': {
                    'location': 'Lunar regolith',
                    'use': 'Fusion fuel',
                    'estimated_value_per_ton': 4000000000
                },
                'rare_earths': {
                    'location': 'KREEP terrains',
                    'use': 'Technology manufacturing'
                }
            },
            'investment_opportunities': [
                'Lunar lander manufacturers',
                'Regolith mining equipment',
                'In-situ resource utilization (ISRU) tech',
                'Lunar habitat construction',
                'Power systems (solar, nuclear)'
            ]
        }
    
    def get_portfolio_recommendations(self, risk_tolerance: str = 'moderate') -> Dict:
        """Get space economy investment recommendations"""
        
        if risk_tolerance == 'conservative':
            return {
                'strategy': 'Established public companies with revenue',
                'allocation': {
                    'Iridium (IRDM)': '25%',
                    'Planet Labs (PL)': '20%',
                    'Rocket Lab (RKLB)': '15%',
                    'Kratos (KTOS)': '20%',
                    'Cash/Wait for SpaceX IPO': '20%'
                },
                'rationale': 'Focus on companies with existing revenue and contracts'
            }
        
        elif risk_tolerance == 'moderate':
            return {
                'strategy': 'Mix of established and growth companies',
                'allocation': {
                    'Iridium (IRDM)': '15%',
                    'Rocket Lab (RKLB)': '15%',
                    'Virgin Galactic (SPCE)': '10%',
                    'AST SpaceMobile (ASTS)': '15%',
                    'Redwire (RDW)': '15%',
                    'Axiom Space (Private)': '15%',
                    'Relativity Space (Private)': '15%'
                },
                'rationale': 'Balanced exposure across launch, satellites, and infrastructure'
            }
        
        else:  # aggressive
            return {
                'strategy': 'High-risk, high-reward frontier investments',
                'allocation': {
                    'Virgin Galactic (SPCE)': '10%',
                    'AST SpaceMobile (ASTS)': '15%',
                    'Axiom Space (Private)': '20%',
                    'Relativity Space (Private)': '15%',
                    'Varda Space (Private)': '20%',
                    'TransAstra (Private)': '10%',
                    'Lunar/Mining Ventures': '10%'
                },
                'rationale': 'Maximum exposure to emerging technologies and private unicorns'
            }
    
    def get_space_economy_summary(self) -> Dict:
        """Get comprehensive space economy summary"""
        public = self.get_public_companies()
        private_unicorns = self.get_private_unicorns()
        
        return {
            'public_companies_count': len(public),
            'private_unicorns_count': len(private_unicorns),
            'total_valuation_public': sum(c.valuation for c in public if c.valuation > 0),
            'total_valuation_private': sum(c.valuation for c in private_unicorns),
            'sectors_covered': len(set(c.sector for c in self.COMPANIES)),
            'investment_themes': list(self.get_investment_themes().keys()),
            'market_size_projection_2040': self.market_size_2040,
            'top_public_picks': [
                {'name': c.name, 'ticker': c.ticker, 'focus': c.focus}
                for c in public[:5]
            ],
            'top_private_picks': [
                {'name': c.name, 'valuation_b': round(c.valuation/1e9, 1), 'focus': c.focus}
                for c in private_unicorns[:5]
            ],
            'timestamp': datetime.now().isoformat()
        }


# Usage
def get_space_investment_summary() -> Dict:
    """Quick space economy summary"""
    tracker = SpaceEconomyTracker()
    return tracker.get_space_economy_summary()


def get_space_portfolio(risk: str = 'moderate') -> Dict:
    """Get recommended space portfolio"""
    tracker = SpaceEconomyTracker()
    return tracker.get_portfolio_recommendations(risk)


def get_asteroid_mining_data() -> Dict:
    """Get asteroid mining information"""
    tracker = SpaceEconomyTracker()
    return tracker.get_space_resource_targets()
