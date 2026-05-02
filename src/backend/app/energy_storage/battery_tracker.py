"""Energy Storage & Battery Technology Tracker
Solid-state, lithium-ion, grid storage, and alternative chemistries"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BatteryCompany:
    name: str
    ticker: str
    technology: str  # 'solid_state', 'lithium_ion', 'sodium_ion', 'flow'
    stage: str  # 'research', 'pilot', 'production'
    market_cap: float

class BatteryTracker:
    """Track battery technology investments"""
    
    COMPANIES = [
        BatteryCompany('QuantumScape', 'QS', 'solid_state', 'pilot', 3000000000),
        BatteryCompany('Solid Power', 'SLDP', 'solid_state', 'pilot', 500000000),
        BatteryCompany('CATL', 'PRIVATE', 'lithium_ion', 'production', 140000000000),
        BatteryCompany('BYD', 'BYDDY', 'lithium_ion', 'production', 90000000000),
        BatteryCompany('Tesla', 'TSLA', 'lithium_ion', 'production', 800000000000),
        BatteryCompany('Albemarle', 'ALB', 'lithium_mining', 'production', 25000000000),
        BatteryCompany('Livent', 'LTHM', 'lithium_mining', 'production', 5000000000),
        BatteryCompany('Fluence', 'FLNC', 'grid_storage', 'production', 6000000000),
        BatteryCompany('Stem', 'STEM', 'grid_software', 'production', 500000000),
        BatteryCompany('Enovix', 'ENVX', 'silicon_anode', 'pilot', 2000000000),
        BatteryCompany('Sila Nanotech', 'PRIVATE', 'silicon_anode', 'research', 0),
        BatteryCompany('Natron Energy', 'PRIVATE', 'sodium_ion', 'pilot', 0),
        BatteryCompany('Form Energy', 'PRIVATE', 'iron_air', 'research', 0),
    ]
    
    def __init__(self):
        self.price_data = {}
    
    def get_by_technology(self, tech: str) -> List[BatteryCompany]:
        """Get companies by battery technology"""
        return [c for c in self.COMPANIES if c.technology == tech]
    
    def get_investment_recommendations(self) -> Dict:
        """Get battery sector investment recommendations"""
        return {
            'solid_state_leaders': ['QS', 'SLDP'],
            'lithium_mining': ['ALB', 'LTHM', 'SQM'],
            'grid_storage': ['FLNC', 'STEM'],
            'established_producers': ['TSLA', 'BYDDY'],
            'emerging_tech': ['ENVX'],
            'risk_level': 'high',
            'expected_timeline': '3-5 years to commercialization',
            'key_metrics_to_watch': [
                'energy_density_improvements',
                'charging_speed',
                'cycle_life',
                'manufacturing_scale',
                'auto_partnerships'
            ]
        }
    
    def track_lithium_prices(self) -> Dict:
        """Track lithium carbonate prices"""
        return {
            'lithium_carbonate_cny_per_ton': 120000,
            'trend': 'declining',
            'ytd_change_pct': -15,
            'impact_on_miners': 'margin_pressure'
        }
    
    def get_battery_supply_chain(self) -> Dict:
        """Map battery supply chain investment opportunities"""
        return {
            'mining': ['ALB', 'SQM', 'LTHM', 'MIN'],
            'cathode_materials': ['Umicore', 'PRIVATE'],
            'anode_materials': ['NOVONIX', 'PRIVATE'],
            'electrolytes': ['Mitsubishi Chemical', 'PRIVATE'],
            'separators': ['ENTEK', 'PRIVATE'],
            'cell_manufacturers': ['TSLA', 'BYDDY', 'CATL', 'LG Chem'],
            'pack_assemblers': ['FLNC', 'STEM', 'Powin'],
            'recycling': ['Li-Cycle', 'PRIVATE']
        }

# Usage
def get_battery_sector_summary() -> Dict:
    """Quick battery sector summary"""
    tracker = BatteryTracker()
    
    return {
        'recommendations': tracker.get_investment_recommendations(),
        'solid_state_companies': [
            {'name': c.name, 'ticker': c.ticker, 'stage': c.stage}
            for c in tracker.get_by_technology('solid_state')
        ],
        'lithium_prices': tracker.track_lithium_prices(),
        'supply_chain': tracker.get_battery_supply_chain()
    }
