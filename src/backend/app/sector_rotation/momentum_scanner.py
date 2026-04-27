"""Sector Momentum Scanner - Track industry momentum and relative strength"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SectorPerformance:
    sector_name: str
    etf_symbol: str
    returns_1m: float
    returns_3m: float
    returns_6m: float
    relative_strength_vs_sp500: float

class SectorMomentumScanner:
    """Scan and rank sector momentum"""
    
    def __init__(self):
        self.sectors: List[SectorPerformance] = []
    
    def calculate_momentum_score(self, sector: SectorPerformance) -> float:
        """Calculate composite momentum score"""
        return (sector.returns_1m * 0.40 + sector.returns_3m * 0.30 + 
                sector.returns_6m * 0.20 + sector.relative_strength_vs_sp500 * 0.10)
    
    def rank_sectors(self) -> List[Dict]:
        """Rank all sectors by momentum"""
        scored = [(s, self.calculate_momentum_score(s)) for s in self.sectors]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [{"sector": s.sector_name, "score": round(score * 100, 2), "rank": i+1} 
                for i, (s, score) in enumerate(scored)]
    
    def detect_leaders_laggards(self) -> Dict:
        """Identify leading and lagging sectors"""
        ranked = self.rank_sectors()
        return {
            "leaders": ranked[:3],
            "laggards": ranked[-3:],
            "recommendation": "ROTATE_TO_LEADERS"
        }
