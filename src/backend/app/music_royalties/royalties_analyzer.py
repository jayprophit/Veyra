"""
Music Royalties Analyzer
========================
Analyze music royalty investments
Streaming, publishing, performance rights
Catalog valuation, income projections
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RoyaltyStream:
    asset_name: str  # Song/album name or catalog
    asset_type: str  # 'songwriter', 'recording', 'publisher'
    annual_royalties: float
    years_owned: int
    purchase_price: Optional[float]
    streaming_streams_annual: int
    
    def yield_on_cost(self) -> float:
        """Calculate current yield on purchase price"""
        if self.purchase_price and self.purchase_price > 0:
            return (self.annual_royalties / self.purchase_price) * 100
        return 0


class MusicRoyaltiesAnalyzer:
    """Analyze music royalty investments"""
    
    # Industry multiples (annual royalties)
    VALUATION_MULTIPLES = {
        'hit_songwriter_catalog': 15,  # 15x annual
        'established_catalog': 12,
        'emerging_catalog': 8,
        'classic_rock': 14,
        'pop_contemporary': 10,
        'hip_hop': 11,
        'country': 9
    }
    
    # Streaming rates (approximate per stream)
    STREAMING_RATES = {
        'spotify': 0.003,
        'apple_music': 0.01,
        'youtube': 0.0007,
        'amazon_music': 0.004,
        'pandora': 0.0013
    }
    
    # Public royalty companies
    ROYALTY_STOCKS = {
        'HPG': 'Hipgnosis Songs Fund (UK)',
        'ANRG': 'Round Hill Music (private)',
        'SHND': 'Shadowlight (MLC rights)',
        'SCRM': 'Scorpio Music (French)'
    }
    
    def analyze_catalog(self, catalog: RoyaltyStream) -> Dict:
        """Analyze music catalog value"""
        
        # Determine multiple based on catalog characteristics
        multiple = self.VALUATION_MULTIPLES.get('established_catalog', 10)
        
        # Estimated catalog value
        estimated_value = catalog.annual_royalties * multiple
        
        # Yield if buying now
        current_yield = (catalog.annual_royalties / estimated_value) * 100
        
        # Historical performance if owned
        yoc = catalog.yield_on_cost()
        
        return {
            'asset_name': catalog.asset_name,
            'annual_royalties': round(catalog.annual_royalties, 0),
            'estimated_catalog_value': round(estimated_value, 0),
            'valuation_multiple': multiple,
            'current_yield_pct': round(current_yield, 1),
            'yield_on_cost_pct': round(yoc, 1) if yoc > 0 else None,
            'streaming_revenue_pct': 65,  # Typical for modern catalogs
            'performance_revenue_pct': 25,
            'sync_revenue_pct': 10,
            'recommendation': self._generate_recommendation(catalog, estimated_value)
        }
    
    def _generate_recommendation(self, catalog: RoyaltyStream, 
                                  estimated_value: float) -> str:
        """Generate investment recommendation"""
        yoc = catalog.yield_on_cost()
        
        if yoc > 8:
            return "HOLD - Strong yield on cost, cash cow asset"
        elif catalog.purchase_price and estimated_value > catalog.purchase_price * 1.3:
            return "CONSIDER_SALE - Significant appreciation achieved"
        elif catalog.annual_royalties > 100000:
            return "BUY_CANDIDATE - Established catalog with scale"
        else:
            return "HOLD/MONITOR - Smaller catalog, limited upside"
    
    def calculate_streaming_income(self, streams_monthly: Dict[str, int]) -> Dict:
        """
        Calculate streaming income by platform
        
        streams_monthly: Dict of {platform: monthly_streams}
        """
        annual_total = 0
        by_platform = {}
        
        for platform, monthly in streams_monthly.items():
            rate = self.STREAMING_RATES.get(platform, 0.003)
            annual = monthly * 12 * rate
            
            by_platform[platform] = {
                'monthly_streams': monthly,
                'annual_revenue': round(annual, 0),
                'effective_rate': rate
            }
            annual_total += annual
        
        # Streams needed for income targets
        gold_record = 500000  # Units
        platinum_record = 1000000
        
        return {
            'annual_streaming_revenue': round(annual_total, 0),
            'by_platform': by_platform,
            'streams_for_1000_month': 333333,  # At avg $0.003/stream
            'streams_for_10000_month': 3333333,
            'equivalent_to': {
                'gold_records': annual_total / (gold_record * 0.003 * 12),
                'platinum_records': annual_total / (platinum_record * 0.003 * 12)
            }
        }
    
    def get_royalty_investment_thesis(self) -> Dict:
        """Get music royalty investment thesis"""
        return {
            'market_size': '$25B+ annual global royalties',
            'growth_drivers': [
                'Streaming growth (global penetration still low)',
                'TikTok/short-form video monetization',
                'Emerging markets adoption',
                'Fitness/gaming/peloton royalties',
                'Podcast background music'
            ],
            'yield_range': '4-8% annual cash yield',
            'appreciation_potential': 'Multiple expansion as asset class matures',
            'risks': [
                'Streaming rate compression',
                'Catalog concentration',
                'Artist reputation risk',
                'Regulatory changes (mechanical rates)'
            ],
            'investment_vehicles': [
                'Direct catalog acquisition (requires scale)',
                'Royalty exchange platforms (Royalty Exchange)',
                'Public funds (Hipgnosis)',
                'Private funds (Round Hill)'
            ],
            'recommendation': 'SELECTIVE_BUY - Quality catalogs at reasonable multiples'
        }
    
    def compare_catalog_eras(self, catalog_year: int) -> Dict:
        """Compare catalog value by era"""
        
        era_multiples = {
            '1960s_1970s': 14,  # Classic rock, highly valuable
            '1980s': 12,
            '1990s': 11,
            '2000s': 9,
            '2010s': 8,
            '2020s': 7  # Streaming era, different economics
        }
        
        if catalog_year < 1980:
            era = '1960s_1970s'
        elif catalog_year < 1990:
            era = '1980s'
        elif catalog_year < 2000:
            era = '1990s'
        elif catalog_year < 2010:
            era = '2000s'
        elif catalog_year < 2020:
            era = '2010s'
        else:
            era = '2020s'
        
        multiple = era_multiples[era]
        
        return {
            'era': era,
            'valuation_multiple': multiple,
            'era_characteristics': {
                '1960s_1970s': 'Classic rock, high nostalgia, evergreen',
                '1980s': 'MTV generation, sync licensing value',
                '1990s': 'Alternative rock, hip-hop emergence',
                '2000s': 'Digital transition, mixed economics',
                '2010s': 'Streaming native, volume over value',
                '2020s': 'Playlist era, shorter lifecycle'
            }[era],
            'investment_grade': 'PREMIUM' if multiple >= 12 else 'STANDARD'
        }


# Usage
def analyze_music_catalog(name: str, annual_royalties: float, 
                          purchase_price: Optional[float] = None) -> Dict:
    """Quick music catalog analysis"""
    analyzer = MusicRoyaltiesAnalyzer()
    
    catalog = RoyaltyStream(
        asset_name=name,
        asset_type='songwriter',
        annual_royalties=annual_royalties,
        years_owned=0,
        purchase_price=purchase_price,
        streaming_streams_annual=int(annual_royalties / 0.003)
    )
    
    return analyzer.analyze_catalog(catalog)


def calculate_streaming_revenue(streams_per_month: int) -> Dict:
    """Calculate streaming revenue"""
    analyzer = MusicRoyaltiesAnalyzer()
    
    streams = {
        'spotify': int(streams_per_month * 0.4),
        'apple_music': int(streams_per_month * 0.25),
        'youtube': int(streams_per_month * 0.20),
        'amazon_music': int(streams_per_month * 0.10),
        'pandora': int(streams_per_month * 0.05)
    }
    
    return analyzer.calculate_streaming_income(streams)


def get_royalty_thesis() -> Dict:
    """Get royalty investment thesis"""
    analyzer = MusicRoyaltiesAnalyzer()
    return analyzer.get_royalty_investment_thesis()
