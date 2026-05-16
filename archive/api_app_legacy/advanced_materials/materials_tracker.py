"""Advanced Materials Tracker
Graphene, metamaterials, self-healing materials, programmable matter"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class MaterialCompany:
    name: str
    ticker: str
    material: str
    application: str
    stage: str

class AdvancedMaterialsTracker:
    """Track advanced materials companies and technologies"""
    
    COMPANIES = [
        # Graphene
        MaterialCompany('Graphene Manufacturing Group', 'GMG', 'graphene', 'batteries', 'commercialization'),
        MaterialCompany('NanoXplore', 'GRA', 'graphene', 'composites', 'production'),
        MaterialCompany('Haydale', 'HAYD', 'graphene', 'coatings', 'production'),
        MaterialCompany('Versarien', 'VRS', 'graphene', 'thermal', 'commercialization'),
        
        # Metamaterials
        MaterialCompany('Metamaterial Inc', 'MMAT', 'metamaterials', '5G', 'pilot'),
        MaterialCompany('Kymeta', 'PRIVATE', 'metamaterials', 'satellite', 'production'),
        MaterialCompany('Echodyne', 'PRIVATE', 'metamaterials', 'radar', 'production'),
        
        # Self-healing materials
        MaterialCompany('Autonomic Materials', 'PRIVATE', 'self_healing', 'coatings', 'research'),
        MaterialCompany('Suprapolix', 'PRIVATE', 'self_healing', 'polymers', 'pilot'),
        
        # Aerogels
        MaterialCompany('Aspen Aerogels', 'ASPN', 'aerogel', 'insulation', 'production'),
        MaterialCompany('Cabot Corporation', 'CBT', 'aerogel', 'insulation', 'production'),
        
        # Shape memory alloys
        MaterialCompany('Nitinol Products', 'PRIVATE', 'sma', 'medical', 'production'),
        MaterialCompany('SAES Getters', 'PRIVATE', 'sma', 'aerospace', 'production'),
        
        # Carbon fiber
        MaterialCompany('Hexcel', 'HXL', 'carbon_fiber', 'aerospace', 'production'),
        MaterialCompany('Toray', 'TRYIY', 'carbon_fiber', 'automotive', 'production'),
        MaterialCompany('SGL Carbon', 'SGL', 'carbon_fiber', 'industrial', 'production'),
        
        # Ceramics
        MaterialCompany('CoorsTek', 'PRIVATE', 'technical_ceramics', 'semiconductor', 'production'),
        MaterialCompany('Morgan Advanced Materials', 'MGAM', 'ceramics', 'industrial', 'production'),
        
        # Nanomaterials
        MaterialCompany('Nanophase Technologies', 'NANX', 'nanomaterials', 'coatings', 'production'),
    ]
    
    def get_by_material(self, material: str) -> List[MaterialCompany]:
        """Get companies by material type"""
        return [c for c in self.COMPANIES if c.material == material]
    
    def get_material_applications(self) -> Dict:
        """Get applications for each advanced material"""
        return {
            'graphene': {
                'description': 'Single layer carbon, 200x stronger than steel',
                'applications': [
                    'Battery electrodes (faster charging)',
                    'Thermal management (electronics cooling)',
                    'Composite reinforcement (lightweight)',
                    'Water filtration (desalination)',
                    'Transparent conductors (displays)'
                ],
                'market_size_2030': '1500000000',
                'key_companies': ['GMG', 'GRA', 'VRS'],
                'catalysts': ['EV adoption', 'Electronics miniaturization']
            },
            'metamaterials': {
                'description': 'Engineered materials with unnatural properties',
                'applications': [
                    'Invisibility cloaking (military)',
                    '5G/6G antenna beam steering',
                    'Satellite communications',
                    'Medical imaging enhancement',
                    'Acoustic insulation'
                ],
                'market_size_2030': '2500000000',
                'key_companies': ['MMAT'],
                'catalysts': ['5G rollout', 'Defense spending', 'Space economy']
            },
            'self_healing_materials': {
                'description': 'Materials that autonomously repair damage',
                'applications': [
                    'Concrete infrastructure (bridges, roads)',
                    'Electronic circuits (wearables)',
                    'Protective coatings (automotive)',
                    'Aerospace components',
                    'Medical implants'
                ],
                'market_size_2030': '500000000',
                'key_companies': ['PRIVATE'],
                'catalysts': ['Infrastructure spending', 'EV longevity needs']
            },
            'aerogels': {
                'description': 'Ultra-light, highly insulating materials',
                'applications': [
                    'Building insulation',
                    'EV battery thermal management',
                    'Oil & gas pipelines',
                    'Aerospace',
                    'Cold chain logistics'
                ],
                'market_size_2030': '1200000000',
                'key_companies': ['ASPN', 'CBT'],
                'catalysts': ['Energy efficiency codes', 'EV battery safety']
            },
            'shape_memory_alloys': {
                'description': 'Materials that return to shape when heated',
                'applications': [
                    'Medical stents and devices',
                    'Aerospace actuators',
                    'Automotive valves',
                    'Consumer electronics',
                    'Robotics'
                ],
                'market_size_2030': '20000000000',
                'key_companies': ['PRIVATE'],
                'catalysts': ['Aging population', 'Minimally invasive surgery']
            }
        }
    
    def get_investment_thesis(self) -> Dict:
        """Get investment thesis for advanced materials"""
        return {
            'near_term_12_24_months': {
                'focus': 'Graphene batteries, Aerogel insulation',
                'companies': ['GMG', 'ASPN', 'GRA'],
                'catalysts': ['EV battery commercialization', 'Building retrofits']
            },
            'medium_term_3_5_years': {
                'focus': 'Metamaterials 5G, Carbon fiber automotive',
                'companies': ['MMAT', 'HXL', 'TRYIY'],
                'catalysts': ['6G development', 'Lightweight vehicle mandates']
            },
            'long_term_5_10_years': {
                'focus': 'Self-healing infrastructure, Programmable matter',
                'companies': ['PRIVATE'],
                'catalysts': ['Smart cities', 'Space manufacturing']
            }
        }

# Usage
def get_advanced_materials_summary() -> Dict:
    """Quick advanced materials summary"""
    tracker = AdvancedMaterialsTracker()
    
    return {
        'materials_overview': tracker.get_material_applications(),
        'graphene_companies': [
            {'name': c.name, 'ticker': c.ticker}
            for c in tracker.get_by_material('graphene')
        ],
        'investment_thesis': tracker.get_investment_thesis()
    }
