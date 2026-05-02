"""
Expanded Physical Metals Tracker
================================
Additional precious and industrial metals tracking
Copper, Palladium, Nickel, Aluminum, Zinc, Lead, Tin
Rare earth elements, battery metals
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MetalInfo:
    symbol: str
    name: str
    category: str  # 'precious', 'industrial', 'battery', 'rare_earth'
    unit: str
    primary_use: str
    price_usd: float
    price_change_24h: float


class ExpandedMetalsTracker:
    """
    Comprehensive metal tracking beyond gold/silver
    
    Categories:
    - Precious: Gold, Silver, Platinum, Palladium, Rhodium
    - Industrial: Copper, Aluminum, Zinc, Nickel, Lead, Tin
    - Battery Metals: Lithium, Cobalt, Nickel, Manganese
    - Rare Earth: Neodymium, Dysprosium, Terbium, Lanthanum
    """
    
    METALS = [
        # Precious Metals
        MetalInfo('XAU', 'Gold', 'precious', 'USD/oz', 'Investment, jewelry', 2340.50, 1.2),
        MetalInfo('XAG', 'Silver', 'precious', 'USD/oz', 'Industry, investment', 28.45, 2.5),
        MetalInfo('XPT', 'Platinum', 'precious', 'USD/oz', 'Catalysts, jewelry', 985.00, 0.5),
        MetalInfo('XPD', 'Palladium', 'precious', 'USD/oz', 'Auto catalysts', 1025.00, -1.2),
        MetalInfo('XRH', 'Rhodium', 'precious', 'USD/oz', 'Auto catalysts', 4500.00, -0.8),
        
        # Industrial Metals
        MetalInfo('CU', 'Copper', 'industrial', 'USD/lb', 'Construction, electrical', 4.25, -0.8),
        MetalInfo('AL', 'Aluminum', 'industrial', 'USD/lb', 'Packaging, transport', 1.15, 0.3),
        MetalInfo('ZN', 'Zinc', 'industrial', 'USD/lb', 'Galvanizing, batteries', 1.35, 1.2),
        MetalInfo('NI', 'Nickel', 'industrial', 'USD/lb', 'Stainless steel, batteries', 8.50, 1.8),
        MetalInfo('PB', 'Lead', 'industrial', 'USD/lb', 'Batteries, radiation', 0.95, 0.5),
        MetalInfo('SN', 'Tin', 'industrial', 'USD/lb', 'Solder, plating', 12.50, 2.1),
        
        # Battery Metals
        MetalInfo('LI', 'Lithium', 'battery', 'USD/ton', 'EV batteries', 14500.00, 3.5),
        MetalInfo('CO', 'Cobalt', 'battery', 'USD/ton', 'EV batteries', 32000.00, -2.1),
        MetalInfo('MN', 'Manganese', 'battery', 'USD/ton', 'Steel, batteries', 1800.00, 1.2),
        MetalInfo('V', 'Vanadium', 'battery', 'USD/lb', 'Flow batteries', 12.00, 0.8),
        MetalInfo('GR', 'Graphite', 'battery', 'USD/ton', 'Battery anodes', 800.00, 2.5),
        
        # Rare Earth Elements
        MetalInfo('ND', 'Neodymium', 'rare_earth', 'USD/kg', 'Magnets, EVs', 105.00, 3.2),
        MetalInfo('DY', 'Dysprosium', 'rare_earth', 'USD/kg', 'High-tech magnets', 285.00, 4.1),
        MetalInfo('TB', 'Terbium', 'rare_earth', 'USD/kg', 'Phosphors, magnets', 1450.00, 2.8),
        MetalInfo('LA', 'Lanthanum', 'rare_earth', 'USD/kg', 'Catalysts, batteries', 2.50, 0.5),
        MetalInfo('CE', 'Cerium', 'rare_earth', 'USD/kg', 'Glass, catalysts', 2.00, 0.3),
        
        # Other Strategic Metals
        MetalInfo('U', 'Uranium', 'energy', 'USD/lb', 'Nuclear fuel', 85.00, 5.2),
        MetalInfo('MO', 'Molybdenum', 'industrial', 'USD/lb', 'Steel alloy', 22.00, 1.5),
        MetalInfo('W', 'Tungsten', 'industrial', 'USD/kg', 'Hard materials', 35.00, 0.8),
        MetalInfo('TI', 'Titanium', 'industrial', 'USD/kg', 'Aerospace, medical', 12.00, 0.6),
        MetalInfo('ZR', 'Zirconium', 'industrial', 'USD/kg', 'Nuclear, chemical', 45.00, 1.2),
    ]
    
    def __init__(self):
        self.metals_dict = {m.symbol: m for m in self.METALS}
    
    def get_by_category(self, category: str) -> List[MetalInfo]:
        """Get metals by category"""
        return [m for m in self.METALS if m.category == category]
    
    def get_battery_metals(self) -> List[MetalInfo]:
        """Get battery-related metals"""
        return self.get_by_category('battery')
    
    def get_rare_earths(self) -> List[MetalInfo]:
        """Get rare earth elements"""
        return self.get_by_category('rare_earth')
    
    def get_industrial_metals(self) -> List[MetalInfo]:
        """Get industrial metals (excl. precious)"""
        return [m for m in self.METALS if m.category in ['industrial', 'battery']]
    
    def get_etf_recommendations(self) -> Dict:
        """Get ETF recommendations for metal exposure"""
        return {
            'broad_metal': {
                'GLD': 'SPDR Gold Trust',
                'SLV': 'iShares Silver Trust',
                'PPLT': 'Aberdeen Platinum ETF',
                'PALL': 'Aberdeen Palladium ETF'
            },
            'copper': {
                'COPX': 'Global X Copper Miners',
                'CPER': 'United States Copper Index'
            },
            'battery': {
                'LIT': 'Global X Lithium & Battery Tech',
                'BATT': 'Amplify Lithium & Battery Technology',
                'REMX': 'VanEck Rare Earth/Strategic Metals'
            },
            'industrial': {
                'DBB': 'Invesco DB Base Metals Fund',
                'JJM': 'iPath Series B Bloomberg Industrial Metals',
                'PICK': 'iShares MSCI Global Metals & Mining'
            },
            'uranium': {
                'URA': 'Global X Uranium ETF',
                'URNM': 'North Shore Global Uranium Mining'
            }
        }
    
    def get_metal_supply_demand(self) -> Dict:
        """Get supply/demand outlook for key metals"""
        return {
            'copper': {
                'demand_growth': '3-4% annually',
                'primary_drivers': ['EVs (4x more than ICE)', 'Renewable energy', 'Grid infrastructure'],
                'supply_constraints': ['Grade decline', 'Project delays', 'ESG restrictions'],
                'outlook': 'BULLISH - Structural deficit expected'
            },
            'lithium': {
                'demand_growth': '20-25% annually',
                'primary_drivers': ['EV adoption', 'Grid storage', 'Consumer electronics'],
                'supply_constraints': ['Long project timelines (5-7 years)', 'Environmental concerns', 'Water usage'],
                'outlook': 'BULLISH - Supply lagging demand significantly'
            },
            'nickel': {
                'demand_growth': '7-8% annually',
                'primary_drivers': ['Stainless steel', 'EV batteries (NMC chemistries)'],
                'supply_constraints': ['Indonesia ore export bans', 'Class 1 nickel shortage'],
                'outlook': 'BULLISH for Class 1 nickel'
            },
            'cobalt': {
                'demand_growth': '8-10% annually',
                'primary_drivers': ['EV batteries', 'Aerospace alloys'],
                'supply_constraints': ['DRC concentration (70%)', 'Ethical sourcing concerns', 'Cobalt-free battery R&D'],
                'outlook': 'NEUTRAL - Substitution risk from LFP batteries'
            },
            'rare_earths': {
                'demand_growth': '10-15% annually',
                'primary_drivers': ['EV motors', 'Wind turbines', 'Electronics', 'Defense'],
                'supply_constraints': ['China dominance (80%)', 'Environmental mining concerns', 'Processing bottlenecks'],
                'outlook': 'BULLISH - Geopolitical supply risk premium'
            },
            'uranium': {
                'demand_growth': '3-4% annually',
                'primary_drivers': ['Nuclear renaissance', 'Energy security', 'Decarbonization'],
                'supply_constraints': ['Underinvestment 2011-2020', 'Mine restarts slow', 'Kazakhstan concentration'],
                'outlook': 'BULLISH - Supply deficit emerging'
            }
        }
    
    def get_metal_investment_thesis(self) -> Dict:
        """Get investment thesis for metal categories"""
        return {
            'precious_metals': {
                'thesis': 'Store of value, inflation hedge, currency debasement protection',
                'allocation_pct': '10-20',
                'recommendation': 'GOLD core holding, SILVER for leverage',
                'timing': 'Accumulate on dips'
            },
            'copper': {
                'thesis': 'Electrification of everything, EVs, renewables, grid',
                'allocation_pct': '5-10',
                'recommendation': 'COPX ETF or major miners (FCX, SCCO)',
                'timing': 'BULLISH - entering supercycle'
            },
            'battery_metals': {
                'thesis': 'EV revolution, energy storage, decarbonization megatrend',
                'allocation_pct': '5-15',
                'recommendation': 'LIT ETF, direct lithium/cobalt exposure',
                'timing': 'VOLATILE but long-term BULLISH'
            },
            'rare_earths': {
                'thesis': 'Critical for EVs, wind, defense, electronics. Supply concentrated in China',
                'allocation_pct': '3-5',
                'recommendation': 'REMX ETF, MP Materials (rare earth mine)',
                'timing': 'BULLISH - geopolitical premium increasing'
            },
            'uranium': {
                'thesis': 'Nuclear renaissance, clean baseload power, supply deficit',
                'allocation_pct': '3-7',
                'recommendation': 'URA/URNM ETFs, Cameco, Kazatomprom',
                'timing': 'BULLISH - multi-year bull market beginning'
            }
        }
    
    def get_summary(self) -> Dict:
        """Get comprehensive metals summary"""
        return {
            'total_metals_tracked': len(self.METALS),
            'by_category': {
                'precious': len(self.get_by_category('precious')),
                'industrial': len(self.get_by_category('industrial')),
                'battery': len(self.get_by_category('battery')),
                'rare_earth': len(self.get_by_category('rare_earth')),
                'energy': len(self.get_by_category('energy'))
            },
            'top_performers_24h': [
                {'symbol': m.symbol, 'name': m.name, 'change': m.price_change_24h}
                for m in sorted(self.METALS, key=lambda x: x.price_change_24h, reverse=True)[:5]
            ],
            'etfs_available': len(self.get_etf_recommendations()),
            'investment_thesis': self.get_metal_investment_thesis(),
            'supply_demand_outlook': self.get_metal_supply_demand(),
            'timestamp': datetime.now().isoformat()
        }


# Usage
def get_expanded_metals_summary() -> Dict:
    """Quick expanded metals summary"""
    tracker = ExpandedMetalsTracker()
    return tracker.get_summary()


def get_battery_metals_investment_case() -> Dict:
    """Get battery metals investment thesis"""
    tracker = ExpandedMetalsTracker()
    return {
        'metals': [m.__dict__ for m in tracker.get_battery_metals()],
        'thesis': tracker.get_metal_investment_thesis().get('battery_metals'),
        'outlook': tracker.get_metal_supply_demand().get('lithium')
    }


def get_metal_etf_guide() -> Dict:
    """Get metal ETF investment guide"""
    tracker = ExpandedMetalsTracker()
    return tracker.get_etf_recommendations()
