"""Stock Screener - Multi-Factor Filter Engine"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FilterOperator(Enum):
    GT = ">"
    LT = "<"
    EQ = "=="
    GTE = ">="
    LTE = "<="
    BETWEEN = "between"
    IN = "in"


@dataclass
class Filter:
    field: str
    operator: FilterOperator
    value: Any


@dataclass
class ScreenResult:
    symbol: str
    matches: List[str]
    scores: Dict[str, float]
    passed: bool


class StockScreener:
    """Multi-factor stock screening engine"""
    
    # Pre-built screen templates
    TEMPLATES = {
        'value_growth': [
            Filter('pe_ratio', FilterOperator.LT, 20),
            Filter('peg_ratio', FilterOperator.LT, 1.5),
            Filter('revenue_growth', FilterOperator.GT, 10),
        ],
        'momentum': [
            Filter('rsi_14', FilterOperator.BETWEEN, (50, 70)),
            Filter('price_above_sma50', FilterOperator.EQ, True),
            Filter('volume_spike', FilterOperator.GT, 1.5),
        ],
        'swing_trading': [
            Filter('atr_percent', FilterOperator.GT, 3),
            Filter('volume_10d_avg', FilterOperator.GT, 1000000),
            Filter('beta', FilterOperator.BETWEEN, (0.8, 2.0)),
        ],
        'dividend': [
            Filter('dividend_yield', FilterOperator.GT, 3),
            Filter('payout_ratio', FilterOperator.LT, 60),
            Filter('dividend_growth_5y', FilterOperator.GT, 5),
        ],
        'penny_breakout': [
            Filter('price', FilterOperator.BETWEEN, (0.5, 10)),
            Filter('volume_spike', FilterOperator.GT, 3),
            Filter('rsi_14', FilterOperator.BETWEEN, (60, 80)),
        ],
    }
    
    def __init__(self):
        self.filters: List[Filter] = []
    
    def add_filter(self, field: str, operator: str, value: Any):
        """Add a filter criterion"""
        op = FilterOperator(operator) if isinstance(operator, str) else operator
        self.filters.append(Filter(field, op, value))
    
    def screen(self, universe: List[Dict]) -> List[ScreenResult]:
        """Run screening on stock universe"""
        results = []
        
        for stock in universe:
            matches = []
            scores = {}
            
            for filt in self.filters:
                value = stock.get(filt.field)
                if value is None:
                    continue
                
                passed, score = self._evaluate_filter(filt, value)
                scores[filt.field] = score
                if passed:
                    matches.append(filt.field)
            
            results.append(ScreenResult(
                symbol=stock.get('symbol', ''),
                matches=matches,
                scores=scores,
                passed=len(matches) == len(self.filters)
            ))
        
        return [r for r in results if r.passed]
    
    def _evaluate_filter(self, filt: Filter, value: Any) -> tuple:
        """Evaluate single filter"""
        op = filt.operator
        target = filt.value
        
        if op == FilterOperator.GT:
            return value > target, 1.0 if value > target else value / target
        elif op == FilterOperator.LT:
            return value < target, 1.0 if value < target else target / value
        elif op == FilterOperator.GTE:
            return value >= target, 1.0 if value >= target else value / target
        elif op == FilterOperator.LTE:
            return value <= target, 1.0 if value <= target else target / value
        elif op == FilterOperator.EQ:
            return value == target, 1.0 if value == target else 0.0
        elif op == FilterOperator.BETWEEN:
            return target[0] <= value <= target[1], 1.0
        
        return False, 0.0
    
    def apply_template(self, template_name: str):
        """Apply pre-built template"""
        if template_name in self.TEMPLATES:
            self.filters = self.TEMPLATES[template_name].copy()
    
    def get_templates(self) -> List[str]:
        """Get available template names"""
        return list(self.TEMPLATES.keys())
