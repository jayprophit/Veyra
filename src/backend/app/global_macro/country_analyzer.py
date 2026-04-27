"""Country Analyzer - Analyze country ETFs and economic indicators"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CountryData:
    country_code: str
    country_name: str
    etf_symbol: str
    gdp_growth: float
    inflation_rate: float
    interest_rate: float
    political_stability: int

class CountryAnalyzer:
    """Analyze countries for investment opportunities"""
    
    def __init__(self):
        self.countries: Dict[str, CountryData] = {}
    
    def add_country(self, data: CountryData):
        self.countries[data.country_code] = data
    
    def calculate_country_score(self, code: str) -> Dict:
        if code not in self.countries:
            return {"error": "Not found"}
        
        data = self.countries[code]
        score = 50
        
        if data.gdp_growth > 3:
            score += 20
        elif data.gdp_growth < 0:
            score -= 15
        
        if 1.5 <= data.inflation_rate <= 3:
            score += 15
        elif data.inflation_rate > 5:
            score -= 15
        
        score += (data.political_stability - 50) / 5
        
        return {
            "country": data.country_name,
            "etf": data.etf_symbol,
            "score": round(max(0, min(100, score)), 1),
            "grade": "A" if score >= 80 else "B" if score >= 65 else "C"
        }
    
    def rank_countries(self) -> List[Dict]:
        scored = [self.calculate_country_score(c) for c in self.countries]
        return sorted([s for s in scored if "error" not in s], key=lambda x: x["score"], reverse=True)
