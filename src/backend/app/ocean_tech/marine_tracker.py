"""Ocean & Marine Technology Tracker
Deep-sea mining, marine aquaculture, offshore wind, ocean carbon capture"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class OceanCompany:
    name: str
    ticker: str
    sector: str
    stage: str
    market_cap: float

class OceanTechTracker:
    """Track ocean and marine technology investments"""
    
    COMPANIES = [
        # Deep-sea mining
        OceanCompany('The Metals Company', 'TMC', 'deep_sea_mining', 'exploration', 800000000),
        OceanCompany('DeepGreen', 'PRIVATE', 'deep_sea_mining', 'research', 0),
        OceanCompany('Nautilus Minerals', 'PRIVATE', 'deep_sea_mining', 'development', 0),
        
        # Marine aquaculture
        OceanCompany('Aquabounty', 'AQB', 'aquaculture', 'production', 50000000),
        OceanCompany('Mowi', 'MHGVY', 'aquaculture', 'production', 12000000000),
        OceanCompany('BioMarin', 'BMRN', 'marine_biotech', 'production', 14000000000),
        
        # Offshore wind
        OceanCompany('Orsted', 'DNNGY', 'offshore_wind', 'production', 35000000000),
        OceanCompany('Vestas', 'VWDRY', 'offshore_wind', 'production', 25000000000),
        OceanCompany('Siemens Gamesa', 'GCTAY', 'offshore_wind', 'production', 12000000000),
        
        # Ocean carbon capture
        OceanCompany('Running Tide', 'PRIVATE', 'ocean_CDR', 'pilot', 0),
        OceanCompany('Planetary Technologies', 'PRIVATE', 'ocean_alkalinity', 'research', 0),
        
        # Marine robotics
        OceanCompany('Oceaneering', 'OII', 'marine_robotics', 'production', 2000000000),
        OceanCompany('Teledyne Marine', 'TDY', 'marine_sensors', 'production', 25000000000),
        
        # Seawater desalination
        OceanCompany('IDE Technologies', 'PRIVATE', 'desalination', 'production', 0),
        OceanCompany('Acciona', 'ANA', 'desalination', 'production', 8000000000),
    ]
    
    def get_by_sector(self, sector: str) -> List[OceanCompany]:
        """Get companies by ocean sector"""
        return [c for c in self.COMPANIES if c.sector == sector]
    
    def get_investment_themes(self) -> Dict:
        """Get ocean tech investment themes"""
        return {
            'deep_sea_mining': {
                'description': 'Extraction of polymetallic nodules from ocean floor',
                'companies': ['TMC'],
                'risks': 'High - regulatory uncertainty, environmental concerns',
                'timeline': '2027-2030 commercialization',
                'catalysts': ['ISA regulations', 'EV battery demand', 'ESG acceptance']
            },
            'marine_aquaculture': {
                'description': 'Sustainable seafood production',
                'companies': ['AQB', 'MHGVY'],
                'risks': 'Medium - disease, feed costs, regulation',
                'timeline': 'Ongoing scaling',
                'catalysts': ['Land based farming', 'Genetic improvement', 'Demand growth']
            },
            'offshore_wind': {
                'description': 'Floating and fixed offshore wind farms',
                'companies': ['DNNGY', 'VWDRY', 'GCTAY'],
                'risks': 'Low-Medium - installation complexity, grid connection',
                'timeline': 'Active deployment',
                'catalysts': ['Green energy mandates', 'Turbine scale-up', 'Cost declines']
            },
            'ocean_CDR': {
                'description': 'Ocean-based carbon dioxide removal',
                'companies': ['Running Tide', 'Planetary Technologies'],
                'risks': 'High - unproven at scale, measurement challenges',
                'timeline': '2030+ commercialization',
                'catalysts': ['Carbon credits', 'Corporate net-zero', 'Technology maturation']
            },
            'marine_robotics': {
                'description': 'Underwater drones and autonomous systems',
                'companies': ['OII', 'TDY'],
                'risks': 'Low - established market, defense applications',
                'timeline': 'Active deployment',
                'catalysts': ['Offshore energy', 'Defense spending', 'Ocean monitoring']
            }
        }
    
    def track_metal_nodules(self) -> Dict:
        """Track deep-sea mining metal content"""
        return {
            'polymetallic_nodules': {
                'manganese_pct': 29,
                'nickel_pct': 1.4,
                'copper_pct': 1.3,
                'cobalt_pct': 0.25,
                'estimated_value_per_ton': 350,
                'reserves_million_tons': 40000,
                'regulatory_status': 'ISA drafting regulations'
            },
            'seafloor_massive_sulfides': {
                'copper_pct': 8,
                'zinc_pct': 5,
                'gold_ppm': 2,
                'silver_ppm': 100
            }
        }

# Usage
def get_ocean_tech_summary() -> Dict:
    """Quick ocean tech sector summary"""
    tracker = OceanTechTracker()
    
    return {
        'investment_themes': tracker.get_investment_themes(),
        'deep_sea_mining_companies': [
            {'name': c.name, 'ticker': c.ticker, 'stage': c.stage}
            for c in tracker.get_by_sector('deep_sea_mining')
        ],
        'metal_nodule_content': tracker.track_metal_nodules()
    }
