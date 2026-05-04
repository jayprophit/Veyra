"""Sector Rotation Engine."""
import logging
from typing import Dict, List, Any
from enum import Enum

logger = logging.getLogger(__name__)

class EconomicCycle(Enum):
    EXPANSION = "expansion"
    PEAK = "peak"
    CONTRACTION = "contraction"
    TROUGH = "trough"

class SectorRotationEngine:
    def __init__(self):
        self.cycle_sectors = {
            EconomicCycle.EXPANSION: ['XLK', 'XLI', 'XLY', 'XLB'],
            EconomicCycle.PEAK: ['XLE', 'XLB', 'XLK', 'XLV'],
            EconomicCycle.CONTRACTION: ['XLP', 'XLU', 'XLV', 'XLF'],
            EconomicCycle.TROUGH: ['XLRE', 'XLF', 'XLK', 'XLY']
        }
    
    async def detect_cycle(self, gdp: float, unemployment: float) -> EconomicCycle:
        if gdp > 2.5 and unemployment < 4.5:
            return EconomicCycle.EXPANSION
        elif gdp < 0 or unemployment > 6:
            return EconomicCycle.CONTRACTION
        elif gdp > 1.5:
            return EconomicCycle.PEAK
        return EconomicCycle.TROUGH
    
    async def get_allocation(self, cycle: EconomicCycle) -> Dict[str, Any]:
        sectors = self.cycle_sectors.get(cycle, [])
        weights = [0.4, 0.25, 0.2, 0.15]
        return {
            'cycle': cycle.value,
            'allocations': [{'sector': s, 'weight': weights[i] * 100} for i, s in enumerate(sectors[:4])]
        }

sector_engine = SectorRotationEngine()
