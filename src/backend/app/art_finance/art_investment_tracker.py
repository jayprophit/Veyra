"""
Art & Collectibles Investment Tracker
=====================================
Track art investments, valuations, auction results
Blue-chip art, emerging artists, art fund analysis
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ArtCategory(Enum):
    IMPRESSIONIST = "impressionist"
    MODERN = "modern"
    CONTEMPORARY = "contemporary"
    OLD_MASTER = "old_master"
    AMERICAN = "american"
    LATIN_AMERICAN = "latin_american"
    ASIAN = "asian"
    PHOTOGRAPHY = "photography"


@dataclass
class Artwork:
    artist: str
    title: str
    year: int
    medium: str
    dimensions: str
    category: str
    purchase_price: float
    current_estimate_low: float
    current_estimate_high: float
    purchase_date: datetime
    provenance: List[str]


class ArtInvestmentTracker:
    """Track art and collectibles investments"""
    
    # Art market indices (approximate annual returns)
    ART_INDICES = {
        'meissai_all_art': {'cagr_20yr': 0.073, 'volatility': 0.15},
        'contemporary': {'cagr_20yr': 0.089, 'volatility': 0.22},
        'impressionist': {'cagr_20yr': 0.065, 'volatility': 0.12},
        'old_masters': {'cagr_20yr': 0.041, 'volatility': 0.08},
        'modern': {'cagr_20yr': 0.072, 'volatility': 0.14},
        'post_war': {'cagr_20yr': 0.095, 'volatility': 0.18}
    }
    
    # Art investment vehicles
    INVESTMENT_VEHICLES = {
        'masterworks': {
            'type': 'Fractional platform',
            'min_investment': 1000,
            'fees': '1.5% annual + 20% carry',
            'focus': 'Blue-chip contemporary'
        },
        'yieldstreet': {
            'type': 'Art fund',
            'min_investment': 10000,
            'fees': '2% annual + 20% carry',
            'focus': 'Diversified'
        },
        '6am_gallery': {
            'type': 'Emerging art',
            'min_investment': 500,
            'fees': 'Transaction fees',
            'focus': 'Emerging artists'
        }
    }
    
    def analyze_artwork_performance(self, artwork: Artwork) -> Dict:
        """Analyze individual artwork investment performance"""
        
        # Current value estimate
        current_mid = (artwork.current_estimate_low + artwork.current_estimate_high) / 2
        
        # Calculate returns
        holding_period_years = (datetime.now() - artwork.purchase_date).days / 365.25
        
        if holding_period_years > 0:
            total_return = (current_mid - artwork.purchase_price) / artwork.purchase_price
            annualized_return = (1 + total_return) ** (1 / holding_period_years) - 1
        else:
            total_return = 0
            annualized_return = 0
        
        # Compare to category benchmark
        category = artwork.category
        benchmark = self.ART_INDICES.get(category, {'cagr_20yr': 0.07})
        benchmark_annual = benchmark['cagr_20yr']
        
        # Art-specific risk factors
        risk_factors = [
            'Authentication risk',
            'Provenance gaps',
            'Condition issues',
            'Market liquidity',
            'Storage/insurance costs'
        ]
        
        return {
            'artwork': f"{artwork.artist} - {artwork.title} ({artwork.year})",
            'purchase_price': round(artwork.purchase_price, 0),
            'current_estimate': {
                'low': round(artwork.current_estimate_low, 0),
                'high': round(artwork.current_estimate_high, 0),
                'mid': round(current_mid, 0)
            },
            'holding_period_years': round(holding_period_years, 1),
            'total_return_pct': round(total_return * 100, 1),
            'annualized_return_pct': round(annualized_return * 100, 1),
            'vs_category_benchmark': round((annualized_return - benchmark_annual) * 100, 1),
            'outperformed': annualized_return > benchmark_annual,
            'risk_factors': risk_factors,
            'recommendation': self._artwork_recommendation(total_return, holding_period_years)
        }
    
    def _artwork_recommendation(self, total_return: float, 
                                 holding_years: float) -> str:
        """Generate artwork recommendation"""
        if total_return > 0.5 and holding_years > 5:
            return "CONSIDER_SALE - Strong appreciation, lock in gains"
        elif total_return < -0.3:
            return "HOLD - Downside limited, art is cyclical"
        elif holding_years > 10:
            return "DIVERSIFY - Consider trading for different artist"
        else:
            return "HOLD - Continue holding for appreciation"
    
    def get_portfolio_allocation_guide(self, portfolio_value: float) -> Dict:
        """Get art portfolio allocation guide"""
        
        if portfolio_value < 50000:
            allocation_pct = 5
            strategy = 'Fractional platforms (Masterworks)'
        elif portfolio_value < 250000:
            allocation_pct = 10
            strategy = 'Mix of fractional + individual works under $50K'
        elif portfolio_value < 1000000:
            allocation_pct = 15
            strategy = 'Individual works + art fund exposure'
        else:
            allocation_pct = 20
            strategy = 'Direct collection building with advisory'
        
        target_value = portfolio_value * (allocation_pct / 100)
        
        # Diversification by category
        category_alloc = {
            'contemporary': 0.40,
            'modern': 0.25,
            'impressionist': 0.15,
            'emerging': 0.10,
            'other': 0.10
        }
        
        return {
            'portfolio_value': round(portfolio_value, 0),
            'recommended_allocation_pct': allocation_pct,
            'target_art_value': round(target_value, 0),
            'strategy': strategy,
            'category_breakdown': {
                cat: {
                    'allocation_pct': pct * 100,
                    'target_value': round(target_value * pct, 0)
                }
                for cat, pct in category_alloc.items()
            },
            'expected_return': f"{self.ART_INDICES['meissai_all_art']['cagr_20yr']*100:.1f}% annually"
        }
    
    def analyze_auction_result(self, artist: str, work_title: str,
                              hammer_price: float, pre_sale_estimate: Tuple[float, float],
                              year: int, dimensions: str) -> Dict:
        """Analyze auction result for market intelligence"""
        
        estimate_mid = (pre_sale_estimate[0] + pre_sale_estimate[1]) / 2
        vs_estimate = (hammer_price - estimate_mid) / estimate_mid
        
        # Price per square inch (rough proxy)
        # Parse dimensions like "36 x 48 inches"
        try:
            dims = dimensions.lower().replace('inches', '').replace('"', '').split('x')
            if len(dims) == 2:
                width = float(dims[0].strip())
                height = float(dims[1].strip())
                sq_inches = width * height
                price_per_sq_in = hammer_price / sq_inches
            else:
                price_per_sq_in = 0
        except:
            price_per_sq_in = 0
        
        return {
            'artist': artist,
            'work': work_title,
            'year': year,
            'hammer_price': round(hammer_price, 0),
            'pre_sale_estimate': {
                'low': round(pre_sale_estimate[0], 0),
                'high': round(pre_sale_estimate[1], 0)
            },
            'vs_estimate_pct': round(vs_estimate * 100, 1),
            'sale_result': 'STRONG' if vs_estimate > 0.2 else 'WEAK' if vs_estimate < -0.2 else 'IN_LINE',
            'price_per_sq_inch': round(price_per_sq_in, 0) if price_per_sq_in > 0 else None,
            'market_signal': 'BULLISH for artist' if vs_estimate > 0.3 else 'BEARISH' if vs_estimate < -0.3 else 'NEUTRAL'
        }
    
    def get_market_overview(self) -> Dict:
        """Get art market overview"""
        return {
            'market_size': '$65 billion annually',
            'top_auction_houses': ['Christies', 'Sothebys', 'Phillips', 'Heritage'],
            '20yr_returns': {k: f"{v['cagr_20yr']*100:.1f}%" for k, v in self.ART_INDICES.items()},
            'liquidity': 'LOW - 3-6 months typical to sell',
            'storage_costs': '0.5-1% annually',
            'insurance': '0.1-0.5% annually',
            'transaction_costs': 'Buyer premium 25%, Seller commission 10%',
            'investment_characteristics': {
                'correlation_stocks': '0.1-0.2 (low)',
                'inflation_hedge': 'Yes',
                'tangible_asset': 'Yes',
                'emotional_utility': 'High'
            }
        }


# Usage
def analyze_art_investment(artist: str, title: str, year: int,
                           purchase: float, current_low: float, 
                           current_high: float, purchase_date: datetime) -> Dict:
    """Quick artwork analysis"""
    tracker = ArtInvestmentTracker()
    
    artwork = Artwork(
        artist=artist,
        title=title,
        year=year,
        medium='Oil on canvas',
        dimensions='36 x 48 inches',
        category='contemporary',
        purchase_price=purchase,
        current_estimate_low=current_low,
        current_estimate_high=current_high,
        purchase_date=purchase_date,
        provenance=['Gallery', 'Private Collection']
    )
    
    return tracker.analyze_artwork_performance(artwork)


def get_art_allocation(portfolio: float) -> Dict:
    """Get art allocation guide"""
    tracker = ArtInvestmentTracker()
    return tracker.get_portfolio_allocation_guide(portfolio)


def analyze_auction(artist: str, title: str, hammer: float,
                   est_low: float, est_high: float) -> Dict:
    """Analyze auction result"""
    tracker = ArtInvestmentTracker()
    return tracker.analyze_auction_result(artist, title, hammer, (est_low, est_high), 2020, "36 x 48 inches")
