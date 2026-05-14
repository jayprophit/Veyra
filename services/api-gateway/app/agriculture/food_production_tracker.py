"""
Food Production & Agriculture Tracker
======================================
Comprehensive agriculture investing: farms, food production, agtech
Crop yields, commodity futures, farmland REITs, vertical farming
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CropType(Enum):
    GRAINS = "grains"  # Corn, wheat, soybeans
    OILSEEDS = "oilseeds"  # Canola, sunflower
    SOFTS = "softs"  # Cotton, sugar, coffee
    LIVESTOCK = "livestock"  # Cattle, hogs
    SPECIALTY = "specialty"  # Fruits, vegetables


@dataclass
class FarmInvestment:
    """Farmland or agriculture investment"""
    name: str
    type: str  # 'farmland', 'reit', 'agtech', 'equipment'
    location: str
    size_acres: Optional[float]
    investment_amount: float
    expected_yield_pct: float
    crop_types: List[str]
    risk_level: str


class AgricultureInvestingTracker:
    """
    Comprehensive agriculture and food production investing
    
    Covers:
    - Commodity futures trading
    - Farmland REITs
    - Agricultural equipment
    - Agtech/vertical farming
    - Crop yield forecasting
    - Supply chain arbitrage
    """
    
    # Major agricultural commodity ETFs and futures
    COMMODITY_EXPOSURE = {
        'grains': {
            'CORN': 'Teucrium Corn ETF',
            'WEAT': 'Teucrium Wheat ETF',
            'SOYB': 'Teucrium Soybean ETF',
            'JJG': 'iPath Bloomberg Grains Subindex',
            'GRU': 'Invesco Agriculture Commodity ETF'
        },
        'livestock': {
            'COW': 'iPath Livestock ETN',
            'UBC': 'E-TRACS CMCI Livestock ETN'
        },
        'broad_agriculture': {
            'DBA': 'Invesco DB Agriculture Fund',
            'RJA': 'Elements Rogers Agriculture ETN',
            'FTAG': 'First Trust Indxx Global Agriculture ETF',
            'VEGI': 'iShares MSCI Agriculture Producers'
        },
        'fertilizers': {
            'MOS': 'Mosaic Company (phosphate/potash)',
            'NTR': 'Nutrien Ltd (world\'s largest potash producer)',
            'CF': 'CF Industries (nitrogen)',
            'ICL': 'ICL Group (specialty fertilizers)'
        }
    }
    
    # Farmland REITs
    FARMLAND_REITS = {
        'LAND': 'Gladstone Land Corp (specialty crop farms)',
        'FPI': 'Farmland Partners Inc (row crop farms)',
        'ALCO': 'Alico Inc (Florida citrus and cattle)',
        'LMNR': 'Limoneira Co (citrus and avocados)'
    }
    
    # Agtech companies
    AGTECH_COMPANIES = {
        'public': {
            'DE': 'John Deere (precision agriculture, autonomy)',
            'CAT': 'Caterpillar (farm equipment digitization)',
            'AGCO': 'AGCO Corp (smart farming solutions)',
            'CNHI': 'CNH Industrial (autonomous tractors)',
            'LNN': 'Lindsay Corp (irrigation systems)',
            'VWTR': 'Vidler Water Resources (water for ag)'
        },
        'vertical_farming': {
            'APPH': 'AppHarvest (indoor tomato farming)',
            'HYFM': 'Hydrofarm (hydroponic equipment)',
            'VFF': 'Village Farms (greenhouse produce)',
            'GRWG': 'GrowGeneration (hydroponic supplies)'
        },
        'precision_ag': {
            'CLXT': 'Calyxt (gene editing for crops)',
            'RKDA': 'Arcadia Biosciences (agricultural traits)',
            'IPW': 'iPower (hydroponic equipment)'
        }
    }
    
    # Crop yield forecasts by region
    CROP_REGIONS = {
        'us_midwest': {
            'crops': ['corn', 'soybeans', 'wheat'],
            'major_states': ['Iowa', 'Illinois', 'Nebraska', 'Minnesota', 'Indiana'],
            'production_pct': 35  # % of global corn production
        },
        'black_sea': {
            'crops': ['wheat', 'corn', 'sunflower'],
            'countries': ['Ukraine', 'Russia', 'Romania', 'Bulgaria'],
            'production_pct': 25  # % of global wheat exports
        },
        'south_america': {
            'crops': ['soybeans', 'corn', 'sugar'],
            'countries': ['Brazil', 'Argentina', 'Paraguay'],
            'production_pct': 55  # % of global soybean exports
        },
        'asia_pacific': {
            'crops': ['rice', 'palm oil', 'rubber'],
            'countries': ['Thailand', 'Vietnam', 'Indonesia', 'Malaysia'],
            'production_pct': 90  # % of global rice production
        }
    }
    
    def __init__(self):
        self.investments: List[FarmInvestment] = []
        self.yield_history: Dict[str, List[float]] = {}
    
    def get_commodity_outlook(self) -> Dict:
        """Get agricultural commodity market outlook"""
        return {
            'corn': {
                'current_price': 450,  # cents/bushel
                'yoy_change': 8.5,
                'supply_factors': ['US planting intentions up', 'Brazil second crop strong'],
                'demand_factors': ['Ethanol demand steady', 'China imports increasing'],
                'outlook': 'BULLISH - Supply concerns from weather, strong export demand',
                'etf_exposure': ['CORN', 'JJG', 'DBA']
            },
            'soybeans': {
                'current_price': 1180,  # cents/bushel
                'yoy_change': 3.2,
                'supply_factors': ['South American harvest progressing', 'US acreage debate'],
                'demand_factors': ['China crush margins improving', 'Biodiesel demand growing'],
                'outlook': 'MODERATELY_BULLISH - Strong demand, acreage competition with corn',
                'etf_exposure': ['SOYB', 'JJG', 'DBA']
            },
            'wheat': {
                'current_price': 580,  # cents/bushel
                'yoy_change': -5.2,
                'supply_factors': ['Black Sea exports continue', 'EU crop condition mixed'],
                'demand_factors': ['Feed demand strong', 'Import demand from Africa/Mideast'],
                'outlook': 'NEUTRAL - Adequate global supplies, Black Sea uncertainty premium',
                'etf_exposure': ['WEAT', 'JJG', 'DBA']
            },
            'cattle': {
                'current_price': 185,  # cents/pound
                'yoy_change': 15.3,
                'supply_factors': ['Herd rebuilding underway', 'Drought conditions reducing supply'],
                'demand_factors': ['Strong beef demand', 'Export markets opening'],
                'outlook': 'BULLISH - Multi-year herd rebuilding cycle beginning',
                'etf_exposure': ['COW', 'UBC']
            }
        }
    
    def get_farmland_reit_analysis(self) -> Dict:
        """Analyze farmland REIT opportunities"""
        return {
            'LAND': {
                'name': 'Gladstone Land',
                'focus': 'Specialty crops (berries, vegetables, nuts)',
                'dividend_yield': 3.2,
                'pros': ['Premium crop focus', 'High-value farmland', 'Monthly dividends'],
                'cons': ['Higher valuation', 'Concentrated in CA/AZ', 'Weather risk']
            },
            'FPI': {
                'name': 'Farmland Partners',
                'focus': 'Row crop farms (corn, soybeans, wheat)',
                'dividend_yield': 2.8,
                'pros': ['Diversified geography', 'Lower valuation', 'Inflation hedge'],
                'cons': ['Commodity price exposure', 'Lower yields than specialty']
            },
            'comparison': {
                'avg_farmland_returns': '10-12% annually (income + appreciation)',
                'reit_yield_range': '2.5-3.5%',
                'direct_farmland_yield': '3-5% cash + 5-7% appreciation',
                'inflation_correlation': 0.7,
                'recommendation': 'Use REITs for liquidity, direct ownership for tax benefits'
            }
        }
    
    def get_agtech_investment_thesis(self) -> Dict:
        """Get agtech investment opportunities"""
        return {
            'precision_agriculture': {
                'description': 'GPS-guided equipment, variable rate technology, drones',
                'market_size_2030': '$12B',
                'cagr': '12%',
                'key_players': ['DE', 'CAT', 'AGCO', 'CNHI'],
                'drivers': [
                    'Labor shortages requiring automation',
                    'Need to increase yields on existing land',
                    'Environmental regulation compliance',
                    'Input cost optimization'
                ],
                'investment_thesis': 'Equipment manufacturers with autonomy wins'
            },
            'vertical_farming': {
                'description': 'Indoor controlled environment agriculture',
                'market_size_2030': '$15B',
                'cagr': '25%',
                'key_players': ['APPH', 'HYFM', 'VFF'],
                'drivers': [
                    'Climate-independent production',
                    '90% less water usage',
                    'Year-round consistent supply',
                    'Near urban centers (reduced transport)'
                ],
                'challenges': [
                    'High energy costs',
                    'Capital intensive',
                    'Limited crop variety',
                    'Economic viability questions'
                ],
                'investment_thesis': 'Selective - pick proven operators with path to profitability'
            },
            'gene_editing': {
                'description': 'CRISPR and advanced breeding for crop improvement',
                'market_size_2030': '$8B',
                'cagr': '18%',
                'key_players': ['CLXT', 'RKDA'],
                'drivers': [
                    'Climate resilience needs',
                    'Disease resistance',
                    'Nutritional enhancement',
                    'Reduced chemical inputs'
                ],
                'investment_thesis': 'High risk/high reward - regulatory dependent'
            },
            'irrigation_water': {
                'description': 'Water rights, efficient irrigation, drought solutions',
                'market_size_2030': '$25B',
                'cagr': '8%',
                'key_players': ['LNN', 'VWTR', 'Xylem (XYL)'],
                'drivers': [
                    'Water scarcity increasing',
                    'Agriculture uses 70% of freshwater',
                    'Regulatory pressure on usage',
                    'Efficiency mandates'
                ],
                'investment_thesis': 'Water is the new oil for agriculture'
            }
        }
    
    def calculate_farmland_valuation(self, acres: float, location: str,
                                     soil_quality: str, water_access: bool,
                                     crop_type: str) -> Dict:
        """
        Calculate farmland valuation
        
        Returns estimated value and investment metrics
        """
        # Base prices per acre by region (US)
        base_prices = {
            'corn_belt': 12000,  # Iowa, Illinois
            'delta': 4500,  # Mississippi Delta
            'high_plains': 2500,  # Nebraska, Kansas
            'pacific_northwest': 8000,  # Washington, Oregon
            'california_central': 25000,  # Specialty crops
            'florida': 15000,  # Citrus, vegetables
            'texas': 3500  # Cotton, cattle
        }
        
        # Soil quality multiplier
        soil_multipliers = {
            'excellent': 1.3,
            'good': 1.0,
            'fair': 0.75,
            'poor': 0.5
        }
        
        # Water access premium
        water_premium = 1.3 if water_access else 1.0
        
        # Specialty crop premium
        specialty_premium = 1.5 if crop_type in ['nuts', 'berries', 'vegetables'] else 1.0
        
        # Calculate
        base = base_prices.get(location, 5000)
        soil_mult = soil_multipliers.get(soil_quality, 1.0)
        
        price_per_acre = base * soil_mult * water_premium * specialty_premium
        total_value = acres * price_per_acre
        
        # Expected returns
        cash_yield = price_per_acre * 0.03 if crop_type == 'row_crops' else price_per_acre * 0.025
        appreciation = price_per_acre * 0.05  # Historical farmland appreciation
        total_return = cash_yield + appreciation
        
        return {
            'acres': acres,
            'location': location,
            'crop_type': crop_type,
            'price_per_acre': round(price_per_acre, 0),
            'total_value': round(total_value, 0),
            'annual_cash_yield': round(cash_yield, 0),
            'annual_appreciation': round(appreciation, 0),
            'total_annual_return': round(total_return, 0),
            'return_pct': round(total_return / price_per_acre * 100, 1),
            'valuation_factors': {
                'soil_quality_multiplier': soil_mult,
                'water_access_premium': water_premium,
                'specialty_crop_premium': specialty_premium
            }
        }
    
    def add_investment(self, investment: FarmInvestment):
        """Add agriculture investment to portfolio"""
        self.investments.append(investment)
    
    def get_portfolio_summary(self) -> Dict:
        """Get agriculture investment portfolio summary"""
        if not self.investments:
            return {'message': 'No agriculture investments tracked'}
        
        total_invested = sum(i.investment_amount for i in self.investments)
        total_acres = sum(i.size_acres or 0 for i in self.investments)
        
        by_type = {}
        for inv in self.investments:
            if inv.type not in by_type:
                by_type[inv.type] = []
            by_type[inv.type].append(inv)
        
        # Calculate weighted expected return
        total_expected = sum(
            i.investment_amount * (i.expected_yield_pct / 100)
            for i in self.investments
        )
        weighted_return = total_expected / total_invested * 100 if total_invested > 0 else 0
        
        return {
            'total_invested': round(total_invested, 2),
            'total_acres': round(total_acres, 1),
            'investment_count': len(self.investments),
            'weighted_expected_return': round(weighted_return, 2),
            'by_type': {
                k: {
                    'count': len(v),
                    'amount': round(sum(i.investment_amount for i in v), 2)
                }
                for k, v in by_type.items()
            },
            'diversification_score': len(by_type) / 5,  # 5 types = fully diversified
            'timestamp': datetime.now().isoformat()
        }
    
    def get_food_security_indicators(self) -> Dict:
        """Get global food security indicators for macro investing"""
        return {
            'global_grain_stocks': {
                'wheat_days_of_supply': 105,
                'corn_days_of_supply': 65,
                'rice_days_of_supply': 140,
                'trend': 'DECLINING - Climate impacts reducing buffer stocks'
            },
            'weather_risks': {
                'la_nina_probability': 0.6,
                'drought_regions': ['US Plains', 'Argentina', 'Australia'],
                'excessive_moisture': ['US Midwest', 'EU'],
                'impact': 'MIXED - Regional variations creating volatility'
            },
            'trade_flows': {
                'black_sea_exports': 'RESTRICTED - Ukraine conflict ongoing impact',
                'china_imports': 'STRONG - Record soybean and corn purchases',
                'biofuel_policy': 'EXPANDING - US and EU ethanol mandates increasing demand'
            },
            'investment_implications': {
                'bullish_factors': [
                    'Declining stock-to-use ratios',
                    'Weather volatility increasing',
                    'Input costs (fertilizer, fuel) elevated',
                    'Geopolitical trade disruptions'
                ],
                'bearish_factors': [
                    'Technology improving yields',
                    'Alternative proteins emerging',
                    'Economic slowdown reducing demand'
                ],
                'recommendation': 'OVERWEIGHT - Agriculture as inflation hedge and supply security'
            }
        }
    
    def get_comprehensive_summary(self) -> Dict:
        """Get complete agriculture investing summary"""
        return {
            'commodity_outlook': self.get_commodity_outlook(),
            'farmland_reits': self.get_farmland_reit_analysis(),
            'agtech_thesis': self.get_agtech_investment_thesis(),
            'food_security': self.get_food_security_indicators(),
            'portfolio': self.get_portfolio_summary(),
            'investment_options': {
                'commodity_etfs': list(self.COMMODITY_EXPOSURE['broad_agriculture'].keys()),
                'farmland_reits': list(self.FARMLAND_REITS.keys()),
                'agtech_stocks': list(self.AGTECH_COMPANIES['public'].keys())
            },
            'timestamp': datetime.now().isoformat()
        }


# Usage
def get_agriculture_investment_summary() -> Dict:
    """Quick agriculture investing overview"""
    tracker = AgricultureInvestingTracker()
    return tracker.get_comprehensive_summary()


def calculate_farmland_value(acres: float, location: str, 
                             soil: str, water: bool, crop: str) -> Dict:
    """Calculate farmland valuation"""
    tracker = AgricultureInvestingTracker()
    return tracker.calculate_farmland_valuation(acres, location, soil, water, crop)


def get_commodity_outlook() -> Dict:
    """Get agricultural commodity outlook"""
    tracker = AgricultureInvestingTracker()
    return tracker.get_commodity_outlook()
