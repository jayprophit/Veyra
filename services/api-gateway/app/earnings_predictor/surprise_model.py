"""Surprise Model - Predict earnings surprises using multiple factors"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import statistics

@dataclass
class EarningsFeatures:
    symbol: str
    report_date: datetime
    # Historical metrics
    surprise_history: List[float]  # Last 8 quarters surprises
    surprise_consistency: float  # % of positive surprises
    
    # Analyst metrics
    consensus_eps: float
    num_estimates: int
    estimate_std: float
    revision_4w: float  # % change in consensus 4 weeks ago
    revision_1w: float  # % change in consensus 1 week ago
    
    # Alternative data
    sentiment_score: float  # -1 to 1
    unusual_options_flow: bool
    insider_buying: float  # Net insider buying ratio
    
    # Technical
    price_momentum_1m: float
    relative_strength: float
    volatility_expansion: bool

class SurpriseModel:
    """Predict earnings surprise probability and magnitude"""
    
    def __init__(self):
        self.weights = {
            "revision_momentum": 0.25,
            "surprise_history": 0.20,
            "sentiment": 0.15,
            "technical": 0.15,
            "estimate_quality": 0.15,
            "insider_activity": 0.10
        }
    
    def calculate_surprise_probability(self, features: EarningsFeatures) -> Dict:
        """Calculate probability of positive earnings surprise"""
        score = 50  # Base probability
        
        # Revision momentum (25%)
        if features.revision_1w > 0.03:
            score += 15
        elif features.revision_1w > 0.01:
            score += 8
        elif features.revision_1w < -0.03:
            score -= 15
        elif features.revision_1w < -0.01:
            score -= 8
        
        if features.revision_4w > 0.05:
            score += 10
        elif features.revision_4w < -0.05:
            score -= 10
        
        # Surprise history (20%)
        if features.surprise_consistency > 0.7:
            score += 15
        elif features.surprise_consistency > 0.5:
            score += 8
        elif features.surprise_consistency < 0.3:
            score -= 10
        
        # Check recent surprise magnitude
        if features.surprise_history:
            avg_surprise = statistics.mean(features.surprise_history[-4:])  # Last 4 quarters
            if avg_surprise > 0.10:  # 10% avg beat
                score += 8
            elif avg_surprise < -0.05:
                score -= 8
        
        # Sentiment (15%)
        if features.sentiment_score > 0.5:
            score += 12
        elif features.sentiment_score > 0.2:
            score += 6
        elif features.sentiment_score < -0.5:
            score -= 12
        elif features.sentiment_score < -0.2:
            score -= 6
        
        # Technical (15%)
        if features.price_momentum_1m > 0.10 and features.relative_strength > 1.0:
            score += 10  # Strong momentum + RS
        elif features.price_momentum_1m < -0.10:
            score -= 8  # Weak momentum
        
        if features.volatility_expansion:
            score += 5  # Often precedes surprise
        
        # Estimate quality (15%)
        if features.num_estimates < 5:
            score -= 5  # Low coverage = less reliable
        
        if features.estimate_std > 0.20:  # High dispersion
            score += 5  # More room for surprise
        
        # Insider activity (10%)
        if features.insider_buying > 0.05:
            score += 10  # Heavy insider buying
        elif features.insider_buying < -0.05:
            score -= 8  # Heavy insider selling
        
        # Unusual options flow bonus
        if features.unusual_options_flow:
            if score > 50:
                score += 5
            else:
                score -= 5
        
        final_score = max(10, min(90, score))
        
        return {
            "symbol": features.symbol,
            "report_date": features.report_date.strftime("%Y-%m-%d"),
            "consensus_eps": features.consensus_eps,
            "positive_surprise_probability": round(final_score, 1),
            "surprise_prediction": "BEAT" if final_score > 60 else "MISS" if final_score < 40 else "IN_LINE",
            "confidence": "HIGH" if abs(final_score - 50) > 20 else "MODERATE" if abs(final_score - 50) > 10 else "LOW",
            "expected_surprise_magnitude": self._estimate_magnitude(features, final_score),
            "key_factors": self._identify_key_factors(features)
        }
    
    def _estimate_magnitude(self, features: EarningsFeatures, probability: float) -> Dict:
        """Estimate potential surprise magnitude"""
        base_magnitude = 0.05  # 5% base
        
        # Adjust by estimate dispersion
        if features.estimate_std > 0.15:
            base_magnitude += 0.03
        
        # Historical volatility
        if features.surprise_history:
            hist_vol = statistics.stdev(features.surprise_history) if len(features.surprise_history) > 1 else 0.05
            base_magnitude = max(base_magnitude, hist_vol)
        
        # Probability adjustment
        if probability > 70:
            expected = base_magnitude * 1.5
        elif probability < 30:
            expected = -base_magnitude * 1.5
        else:
            expected = base_magnitude * (probability - 50) / 50
        
        return {
            "expected_surprise_pct": round(expected * 100, 1),
            "implied_eps": round(features.consensus_eps * (1 + expected), 3),
            "range_low": round(features.consensus_eps * (1 - base_magnitude), 3),
            "range_high": round(features.consensus_eps * (1 + base_magnitude), 3)
        }
    
    def _identify_key_factors(self, features: EarningsFeatures) -> List[str]:
        """Identify the most predictive factors"""
        factors = []
        
        if abs(features.revision_1w) > 0.02:
            direction = "up" if features.revision_1w > 0 else "down"
            factors.append(f"Analyst revisions {direction} {abs(features.revision_1w)*100:.0f}% in last week")
        
        if features.surprise_consistency > 0.6 or features.surprise_consistency < 0.4:
            factors.append(f"Strong {'beat' if features.surprise_consistency > 0.6 else 'miss'} history ({features.surprise_consistency*100:.0f}%)")
        
        if abs(features.sentiment_score) > 0.4:
            factors.append(f"{'Positive' if features.sentiment_score > 0 else 'Negative'} social sentiment")
        
        if abs(features.insider_buying) > 0.03:
            factors.append(f"Insider {'buying' if features.insider_buying > 0 else 'selling'} activity")
        
        if features.unusual_options_flow:
            factors.append("Unusual options flow detected")
        
        if not factors:
            factors.append("Mixed signals - no dominant factor")
        
        return factors[:3]
    
    def rank_earnings_opportunities(self, 
                                    earnings_list: List[EarningsFeatures],
                                    min_confidence: str = "MODERATE") -> List[Dict]:
        """Rank upcoming earnings by opportunity"""
        results = []
        
        confidence_levels = {"HIGH": 3, "MODERATE": 2, "LOW": 1}
        min_level = confidence_levels.get(min_confidence, 2)
        
        for features in earnings_list:
            prediction = self.calculate_surprise_probability(features)
            
            conf_level = confidence_levels.get(prediction["confidence"], 0)
            if conf_level >= min_level and prediction["surprise_prediction"] != "IN_LINE":
                # Score by conviction * magnitude
                conviction = abs(prediction["positive_surprise_probability"] - 50)
                magnitude = abs(prediction["expected_surprise_magnitude"]["expected_surprise_pct"])
                opportunity_score = conviction * magnitude
                
                results.append({
                    **prediction,
                    "opportunity_score": round(opportunity_score, 1)
                })
        
        # Sort by opportunity score
        results.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        return results
    
    def generate_trading_signal(self, prediction: Dict, 
                                options_available: bool = True) -> Dict:
        """Generate trading signal based on prediction"""
        surprise_pred = prediction["surprise_prediction"]
        confidence = prediction["confidence"]
        magnitude = prediction["expected_surprise_magnitude"]["expected_surprise_pct"]
        
        if confidence == "LOW":
            return {
                "action": "NO_TRADE",
                "rationale": "Low confidence prediction - skip"
            }
        
        # Strategy selection
        if options_available:
            if confidence == "HIGH" and abs(magnitude) > 8:
                strategy = "DIRECTIONAL_OPTIONS"
                direction = "CALLS" if surprise_pred == "BEAT" else "PUTS"
            else:
                strategy = "STRADDLE"
                direction = "LONG_VOL"
        else:
            strategy = "DIRECTIONAL_EQUITY"
            direction = "LONG" if surprise_pred == "BEAT" else "SHORT"
        
        return {
            "action": "TRADE",
            "strategy": strategy,
            "direction": direction,
            "size": "FULL" if confidence == "HIGH" else "HALF",
            "entry_timing": "PRE_EARNINGS" if confidence == "HIGH" else "POST_EARNINGS",
            "hold_period": "1-3_DAYS",
            "stop_loss": "10%"
        }
