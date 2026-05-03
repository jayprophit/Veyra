"""
Data Quality Scoring for Portfolio Views
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

@dataclass
class QualityScore:
    completeness: float  # 0-100
    accuracy: float
    freshness: float
    consistency: float
    overall: float
    details: Dict

class DataQualityScorer:
    """Scores portfolio data quality across multiple dimensions"""
    
    # Thresholds
    FRESHNESS_HOURS = 24  # Data older than this is stale
    ACCURACY_THRESHOLD = 0.05  # 5% deviation allowed
    
    def score_position(self, position: Dict, market_data: Optional[Dict] = None) -> QualityScore:
        """Score a single position's data quality"""
        
        # Completeness - check required fields
        required_fields = ['ticker', 'quantity', 'avg_price', 'current_price', 'last_updated']
        present_fields = sum(1 for f in required_fields if f in position and position[f] is not None)
        completeness = (present_fields / len(required_fields)) * 100
        
        # Freshness - check last update time
        freshness = self._calculate_freshness(position.get('last_updated'))
        
        # Accuracy - compare to market data if available
        accuracy = 100.0
        if market_data and 'current_price' in market_data:
            deviation = abs(position.get('current_price', 0) - market_data['current_price']) / market_data['current_price']
            accuracy = max(0, 100 - (deviation * 100 * 2))  # Penalize deviation
        
        # Consistency - check for logical errors
        consistency = self._check_consistency(position)
        
        # Calculate overall
        overall = (completeness * 0.3 + freshness * 0.3 + accuracy * 0.25 + consistency * 0.15)
        
        return QualityScore(
            completeness=round(completeness, 1),
            accuracy=round(accuracy, 1),
            freshness=round(freshness, 1),
            consistency=round(consistency, 1),
            overall=round(overall, 1),
            details={
                "missing_fields": [f for f in required_fields if f not in position or position[f] is None],
                "price_deviation": deviation if market_data else None,
                "data_age_hours": self._get_data_age_hours(position.get('last_updated'))
            }
        )
    
    def _calculate_freshness(self, last_updated: Optional[datetime]) -> float:
        """Calculate freshness score (0-100)"""
        if not last_updated:
            return 0
        
        age_hours = self._get_data_age_hours(last_updated)
        
        if age_hours < 1:
            return 100
        elif age_hours < self.FRESHNESS_HOURS:
            return max(0, 100 - (age_hours / self.FRESHNESS_HOURS * 100))
        else:
            return 0
    
    def _get_data_age_hours(self, last_updated: Optional[datetime]) -> float:
        """Get age of data in hours"""
        if not last_updated:
            return float('inf')
        
        if isinstance(last_updated, str):
            try:
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            except:
                return float('inf')
        
        age = datetime.now() - last_updated
        return age.total_seconds() / 3600
    
    def _check_consistency(self, position: Dict) -> float:
        """Check data consistency (0-100)"""
        issues = []
        
        # Check for negative quantities
        if position.get('quantity', 0) < 0:
            issues.append("negative_quantity")
        
        # Check for zero prices
        if position.get('avg_price', 1) <= 0 or position.get('current_price', 1) <= 0:
            issues.append("invalid_price")
        
        # Check market value calculation
        expected_mv = position.get('quantity', 0) * position.get('current_price', 0)
        reported_mv = position.get('market_value', expected_mv)
        if abs(expected_mv - reported_mv) > 0.01:
            issues.append("mv_mismatch")
        
        return max(0, 100 - len(issues) * 25)
    
    def get_quality_badge(self, score: float) -> Dict:
        """Get badge info for quality score"""
        if score >= 80:
            return {"color": "green", "label": "Excellent", "icon": "✓"}
        elif score >= 60:
            return {"color": "yellow", "label": "Good", "icon": "~"}
        elif score >= 40:
            return {"color": "orange", "label": "Fair", "icon": "!"}
        else:
            return {"color": "red", "label": "Poor", "icon": "✗"}
    
    def batch_score_positions(
        self,
        positions: List[Dict],
        market_data: Optional[Dict[str, Dict]] = None
    ) -> Dict[str, QualityScore]:
        """Score multiple positions"""
        results = {}
        for pos in positions:
            ticker = pos.get('ticker', 'unknown')
            md = market_data.get(ticker) if market_data else None
            results[ticker] = self.score_position(pos, md)
        return results
