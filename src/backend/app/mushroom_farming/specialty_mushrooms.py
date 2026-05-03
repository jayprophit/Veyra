"""Specialty Mushrooms - Rare and gourmet mushroom investing"""
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class MushroomRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EXOTIC = "exotic"

@dataclass
class SpecialtyMushroom:
    species: str
    rarity: MushroomRarity
    market_price_per_kg: float
    cultivation_difficulty: int  # 1-10
    demand_score: int  # 1-10
    medicinal_value: bool
    culinary_prestige: int  # 1-10

class SpecialtyMushrooms:
    """Track and analyze specialty mushroom markets"""
    
    def __init__(self):
        self.mushrooms: List[SpecialtyMushroom] = []
        self._load_catalog()
    
    def _load_catalog(self):
        """Load default specialty mushroom catalog"""
        catalog = [
            SpecialtyMushroom("Lion's Mane", MushroomRarity.UNCOMMON, 45.0, 5, 8, True, 7),
            SpecialtyMushroom("Reishi", MushroomRarity.RARE, 120.0, 7, 7, True, 5),
            SpecialtyMushroom("Morel", MushroomRarity.EXOTIC, 200.0, 9, 9, False, 10),
            SpecialtyMushroom("Chanterelle", MushroomRarity.UNCOMMON, 35.0, 4, 8, False, 9),
            SpecialtyMushroom("Truffle (Black)", MushroomRarity.EXOTIC, 800.0, 10, 10, False, 10),
            SpecialtyMushroom("Cordyceps", MushroomRarity.RARE, 250.0, 8, 8, True, 4),
            SpecialtyMushroom("Turkey Tail", MushroomRarity.COMMON, 25.0, 3, 6, True, 3),
            SpecialtyMushroom("Maitake", MushroomRarity.UNCOMMON, 40.0, 5, 7, True, 8),
        ]
        self.mushrooms.extend(catalog)
    
    def get_by_rarity(self, rarity: MushroomRarity) -> List[SpecialtyMushroom]:
        return [m for m in self.mushrooms if m.rarity == rarity]
    
    def get_investment_opportunities(self) -> List[Dict]:
        """Rank mushrooms by investment potential"""
        opportunities = []
        for m in self.mushrooms:
            score = (m.market_price_per_kg * 0.3 + 
                    m.demand_score * 10 + 
                    (11 - m.cultivation_difficulty) * 5 +
                    m.culinary_prestige * 3)
            if m.medicinal_value:
                score += 20
            
            opportunities.append({
                'species': m.species,
                'rarity': m.rarity.value,
                'price_per_kg': m.market_price_per_kg,
                'investment_score': round(score, 1),
                'difficulty': m.cultivation_difficulty,
                'demand': m.demand_score,
                'medicinal': m.medicinal_value
            })
        
        return sorted(opportunities, key=lambda x: x['investment_score'], reverse=True)
    
    def analyze_market(self) -> Dict:
        by_rarity = {r.value: len(self.get_by_rarity(r)) for r in MushroomRarity}
        avg_price = sum(m.market_price_per_kg for m in self.mushrooms) / len(self.mushrooms)
        
        return {
            'total_species': len(self.mushrooms),
            'by_rarity': by_rarity,
            'average_price_per_kg': round(avg_price, 2),
            'medicinal_species': sum(1 for m in self.mushrooms if m.medicinal_value),
            'top_opportunities': self.get_investment_opportunities()[:5]
        }
