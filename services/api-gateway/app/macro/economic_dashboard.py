"""
Macroeconomic Dashboard
=======================
Track key macroeconomic indicators and their market impact
GDP, inflation, unemployment, interest rates, yield curve
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class EconomicIndicator:
    """Economic indicator data"""
    name: str
    value: float
    previous: float
    expected: float
    unit: str
    frequency: str  # monthly, quarterly, annual
    last_updated: datetime
    impact: str  # high, medium, low


class MacroeconomicDashboard:
    """
    Comprehensive macroeconomic tracking
    
    Indicators:
    - GDP growth
    - Inflation (CPI, PCE, PPI)
    - Employment (unemployment, non-farm payrolls)
    - Interest rates (Fed funds, Treasury yields)
    - Manufacturing (PMI, ISM)
    - Housing (starts, permits, prices)
    """
    
    def __init__(self):
        self.indicators = self._initialize_indicators()
    
    def _initialize_indicators(self) -> Dict[str, EconomicIndicator]:
        """Initialize with current economic data"""
        now = datetime.now()
        
        return {
            'gdp_growth_qoq': EconomicIndicator(
                'GDP Growth (QoQ Annualized)',
                1.6, 3.4, 2.5, '%', 'quarterly', now, 'high'
            ),
            'gdp_growth_yoy': EconomicIndicator(
                'GDP Growth (YoY)',
                2.9, 3.1, 2.8, '%', 'quarterly', now, 'high'
            ),
            'cpi_yoy': EconomicIndicator(
                'CPI Inflation (YoY)',
                3.4, 3.2, 3.3, '%', 'monthly', now, 'high'
            ),
            'core_cpi_yoy': EconomicIndicator(
                'Core CPI (YoY)',
                3.8, 3.9, 3.7, '%', 'monthly', now, 'high'
            ),
            'pce_yoy': EconomicIndicator(
                'PCE Inflation (YoY)',
                2.7, 2.8, 2.6, '%', 'monthly', now, 'high'
            ),
            'unemployment': EconomicIndicator(
                'Unemployment Rate',
                3.8, 3.9, 3.8, '%', 'monthly', now, 'high'
            ),
            'nfp': EconomicIndicator(
                'Non-Farm Payrolls',
                272000, 185000, 180000, 'jobs', 'monthly', now, 'high'
            ),
            'fed_funds': EconomicIndicator(
                'Fed Funds Rate',
                5.50, 5.50, 5.50, '%', 'daily', now, 'high'
            ),
            'pmi_manufacturing': EconomicIndicator(
                'ISM Manufacturing PMI',
                48.7, 49.2, 49.0, 'index', 'monthly', now, 'medium'
            ),
            'pmi_services': EconomicIndicator(
                'ISM Services PMI',
                53.8, 52.6, 52.0, 'index', 'monthly', now, 'medium'
            ),
            'retail_sales': EconomicIndicator(
                'Retail Sales (MoM)',
                0.1, 0.6, 0.4, '%', 'monthly', now, 'medium'
            ),
            'housing_starts': EconomicIndicator(
                'Housing Starts',
                1360000, 1287000, 1420000, 'units', 'monthly', now, 'medium'
            ),
            'consumer_confidence': EconomicIndicator(
                'Consumer Confidence Index',
                102.0, 97.0, 100.0, 'index', 'monthly', now, 'medium'
            ),
            'dxy': EconomicIndicator(
                'US Dollar Index (DXY)',
                105.2, 104.8, 105.0, 'index', 'daily', now, 'medium'
            ),
        }
    
    def get_economic_snapshot(self) -> Dict:
        """Get current economic snapshot"""
        return {
            'growth': {
                'gdp_qoq': self._format_indicator('gdp_growth_qoq'),
                'gdp_yoy': self._format_indicator('gdp_growth_yoy'),
            },
            'inflation': {
                'cpi': self._format_indicator('cpi_yoy'),
                'core_cpi': self._format_indicator('core_cpi_yoy'),
                'pce': self._format_indicator('pce_yoy'),
            },
            'employment': {
                'unemployment_rate': self._format_indicator('unemployment'),
                'nfp': self._format_indicator('nfp'),
            },
            'monetary': {
                'fed_funds': self._format_indicator('fed_funds'),
            },
            'activity': {
                'manufacturing_pmi': self._format_indicator('pmi_manufacturing'),
                'services_pmi': self._format_indicator('pmi_services'),
                'retail_sales': self._format_indicator('retail_sales'),
            },
            'housing': {
                'housing_starts': self._format_indicator('housing_starts'),
            },
            'sentiment': {
                'consumer_confidence': self._format_indicator('consumer_confidence'),
                'dxy': self._format_indicator('dxy'),
            }
        }
    
    def _format_indicator(self, key: str) -> Dict:
        """Format indicator for display"""
        ind = self.indicators[key]
        change = ind.value - ind.previous
        vs_expected = ind.value - ind.expected
        
        return {
            'name': ind.name,
            'value': ind.value,
            'unit': ind.unit,
            'previous': ind.previous,
            'change': round(change, 2),
            'expected': ind.expected,
            'surprise': round(vs_expected, 2),
            'impact': ind.impact,
            'trend': 'improving' if change > 0 else 'declining' if change < 0 else 'stable'
        }
    
    def get_yield_curve(self) -> Dict:
        """Get current Treasury yield curve"""
        yields = {
            '3M': 5.42,
            '6M': 5.38,
            '1Y': 5.15,
            '2Y': 4.85,
            '5Y': 4.45,
            '10Y': 4.42,
            '30Y': 4.55
        }
        
        # Calculate spreads
        spreads = {
            '2s10s': yields['10Y'] - yields['2Y'],
            '10s30s': yields['30Y'] - yields['10Y'],
            '3m10y': yields['10Y'] - yields['3M']
        }
        
        # Inversion detection
        inverted = spreads['2s10s'] < 0
        
        return {
            'yields': yields,
            'spreads': spreads,
            'inverted': inverted,
            'recession_probability': self._estimate_recession_prob(spreads),
            'interpretation': self._interpret_yield_curve(spreads)
        }
    
    def _estimate_recession_prob(self, spreads: Dict) -> float:
        """Estimate recession probability from yield curve"""
        # Simplified model based on 2s10s spread
        spread_2s10s = spreads['2s10s']
        
        if spread_2s10s > 1.0:
            return 0.05
        elif spread_2s10s > 0.5:
            return 0.15
        elif spread_2s10s > 0:
            return 0.25
        elif spread_2s10s > -0.5:
            return 0.45
        else:
            return 0.65
    
    def _interpret_yield_curve(self, spreads: Dict) -> str:
        """Interpret yield curve shape"""
        if spreads['2s10s'] < -0.5:
            return "Deeply inverted - High recession risk"
        elif spreads['2s10s'] < 0:
            return "Inverted - Elevated recession risk"
        elif spreads['2s10s'] < 0.5:
            return "Flat - Uncertainty"
        elif spreads['2s10s'] < 1.0:
            return "Modestly steep - Growth expected"
        else:
            return "Steep - Strong growth expected"
    
    def get_economic_regime(self) -> Dict:
        """Determine current economic regime"""
        gdp = self.indicators['gdp_growth_yoy'].value
        inflation = self.indicators['cpi_yoy'].value
        unemployment = self.indicators['unemployment'].value
        
        # Determine regime
        if gdp > 2.5 and inflation < 3.0:
            regime = "Goldilocks"
            description = "Strong growth with low inflation - Ideal for equities"
            asset_allocation = {"stocks": 60, "bonds": 25, "alternatives": 10, "cash": 5}
        elif gdp > 2.0 and inflation > 3.0:
            regime = "Overheating"
            description = "Strong growth with high inflation - Favor commodities, TIPS"
            asset_allocation = {"stocks": 40, "bonds": 15, "commodities": 25, "cash": 20}
        elif gdp < 2.0 and inflation > 4.0:
            regime = "Stagflation"
            description = "Weak growth with high inflation - Favor gold, commodities, cash"
            asset_allocation = {"stocks": 25, "bonds": 15, "gold": 20, "cash": 40}
        elif gdp < 1.5 and inflation < 2.0:
            regime = "Deflation"
            description = "Weak growth with low inflation - Favor long-duration bonds, defensive equities"
            asset_allocation = {"stocks": 30, "bonds": 50, "gold": 10, "cash": 10}
        else:
            regime = "Transition"
            description = "Mixed signals - Diversified approach recommended"
            asset_allocation = {"stocks": 45, "bonds": 30, "alternatives": 15, "cash": 10}
        
        return {
            'regime': regime,
            'description': description,
            'recommended_allocation': asset_allocation,
            'key_indicators': {
                'gdp': gdp,
                'inflation': inflation,
                'unemployment': unemployment
            }
        }
    
    def get_market_implications(self) -> Dict:
        """Get market implications of current macro environment"""
        regime = self.get_economic_regime()
        yield_curve = self.get_yield_curve()
        
        implications = {
            'equities': self._equity_outlook(regime, yield_curve),
            'bonds': self._bond_outlook(regime, yield_curve),
            'commodities': self._commodity_outlook(regime),
            'dollar': self._dollar_outlook(regime),
            'fed_policy': self._fed_policy_outlook()
        }
        
        return implications
    
    def _equity_outlook(self, regime: Dict, yield_curve: Dict) -> Dict:
        """Equity market outlook"""
        regime_name = regime['regime']
        
        if regime_name == 'Goldilocks':
            return {'outlook': 'BULLISH', 'sectors': ['Tech', 'Growth', 'Cyclicals']}
        elif regime_name == 'Overheating':
            return {'outlook': 'MIXED', 'sectors': ['Value', 'Energy', 'Materials']}
        elif regime_name == 'Stagflation':
            return {'outlook': 'BEARISH', 'sectors': ['Defensive', 'Utilities', 'Consumer Staples']}
        else:
            return {'outlook': 'NEUTRAL', 'sectors': ['Diversified', 'Quality']}
    
    def _bond_outlook(self, regime: Dict, yield_curve: Dict) -> Dict:
        """Bond market outlook"""
        if yield_curve['inverted']:
            return {'outlook': 'FAVOR SHORT DURATION', 'strategy': 'T-Bills, Short-term bonds'}
        else:
            return {'outlook': 'NEUTRAL', 'strategy': 'Barbell strategy'}
    
    def _commodity_outlook(self, regime: Dict) -> Dict:
        """Commodity outlook"""
        if regime['regime'] in ['Overheating', 'Stagflation']:
            return {'outlook': 'BULLISH', 'focus': ['Gold', 'Energy', 'Agriculture']}
        else:
            return {'outlook': 'NEUTRAL', 'focus': ['Diversified commodities']}
    
    def _dollar_outlook(self, regime: Dict) -> Dict:
        """USD outlook"""
        if regime['regime'] == 'Goldilocks':
            return {'outlook': 'MODERATE', 'drivers': ['Interest rate differential']}
        else:
            return {'outlook': 'UNCERTAIN', 'drivers': ['Safe haven flows', 'Fed policy']}
    
    def _fed_policy_outlook(self) -> Dict:
        """Federal Reserve policy outlook"""
        inflation = self.indicators['cpi_yoy'].value
        unemployment = self.indicators['unemployment'].value
        
        if inflation > 3.5 and unemployment < 4.0:
            return {'bias': 'HAWKISH', 'next_move': 'Hold or Hike'}
        elif inflation < 2.5 and unemployment > 4.5:
            return {'bias': 'DOVISH', 'next_move': 'Cut likely'}
        else:
            return {'bias': 'NEUTRAL', 'next_move': 'Hold'}


# Usage
def get_macro_summary() -> Dict:
    """Quick macroeconomic summary"""
    dashboard = MacroeconomicDashboard()
    
    return {
        'economic_snapshot': dashboard.get_economic_snapshot(),
        'yield_curve': dashboard.get_yield_curve(),
        'regime': dashboard.get_economic_regime(),
        'market_implications': dashboard.get_market_implications()
    }


def check_recession_risk() -> Dict:
    """Check current recession risk"""
    dashboard = MacroeconomicDashboard()
    yield_curve = dashboard.get_yield_curve()
    
    return {
        'recession_probability': f"{yield_curve['recession_probability']*100:.1f}%",
        'yield_curve_status': yield_curve['interpretation'],
        'inverted': yield_curve['inverted'],
        'spreads': yield_curve['spreads']
    }
