"""Squeeze Detector - Detect potential short squeeze setups"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ShortInterestData:
    symbol: str
    short_interest: int  # shares short
    float: int  # shares available for trading
    average_daily_volume: int
    days_to_cover: float
    borrow_rate: float  # annualized borrow fee
    price_change_5d: float
    price_change_20d: float
    volume_surge_ratio: float  # current vol / avg vol

class SqueezeDetector:
    """Detect stocks with short squeeze potential"""
    
    def __init__(self):
        self.data: Dict[str, ShortInterestData] = {}
    
    def add_data(self, data: ShortInterestData):
        """Add short interest data for a stock"""
        self.data[data.symbol] = data
    
    def calculate_short_interest_ratio(self, data: ShortInterestData) -> Dict:
        """Calculate short interest as % of float"""
        short_pct = (data.short_interest / data.float) * 100 if data.float > 0 else 0
        
        return {
            "symbol": data.symbol,
            "short_interest_shares": data.short_interest,
            "float": data.float,
            "short_pct_of_float": round(short_pct, 2),
            "category": "EXTREME" if short_pct > 50 else "HIGH" if short_pct > 30 else "ELEVATED" if short_pct > 20 else "NORMAL",
            "squeeze_potential": short_pct > 30
        }
    
    def calculate_squeeze_risk_score(self, data: ShortInterestData) -> Dict:
        """Calculate short squeeze risk score (0-100)"""
        score = 0
        components = {}
        
        # Short % of float (max 30 points)
        short_data = self.calculate_short_interest_ratio(data)
        short_pct = short_data["short_pct_of_float"]
        short_score = min(30, short_pct * 0.6)
        score += short_score
        components["short_pct_score"] = round(short_score, 1)
        
        # Days to cover (max 25 points) - higher is riskier for shorts
        dtc_score = min(25, data.days_to_cover * 2.5)
        score += dtc_score
        components["days_to_cover_score"] = round(dtc_score, 1)
        
        # Borrow rate (max 20 points) - expensive to short = pressure
        borrow_score = min(20, data.borrow_rate / 10)
        score += borrow_score
        components["borrow_cost_score"] = round(borrow_score, 1)
        
        # Recent price momentum (max 15 points) - rising price adds pressure
        if data.price_change_5d > 0.10:
            momentum_score = 15
        elif data.price_change_5d > 0.05:
            momentum_score = 10
        elif data.price_change_5d > 0:
            momentum_score = 5
        else:
            momentum_score = 0
        score += momentum_score
        components["momentum_score"] = momentum_score
        
        # Volume surge (max 10 points) - high volume can trigger squeeze
        vol_score = min(10, data.volume_surge_ratio * 2)
        score += vol_score
        components["volume_score"] = round(vol_score, 1)
        
        return {
            "symbol": data.symbol,
            "squeeze_risk_score": round(score, 1),
            "risk_level": "EXTREME" if score >= 80 else "HIGH" if score >= 65 else "MODERATE" if score >= 50 else "LOW",
            "squeeze_probability": "VERY_HIGH" if score >= 80 else "HIGH" if score >= 65 else "MODERATE" if score >= 50 else "LOW",
            "score_components": components,
            "key_factors": self._identify_key_factors(data, score)
        }
    
    def _identify_key_factors(self, data: ShortInterestData, score: float) -> List[str]:
        """Identify key factors contributing to squeeze risk"""
        factors = []
        
        short_pct = (data.short_interest / data.float) * 100 if data.float > 0 else 0
        
        if short_pct > 40:
            factors.append(f"Very high short interest: {short_pct:.1f}% of float")
        if data.days_to_cover > 5:
            factors.append(f"High days to cover: {data.days_to_cover:.1f} days")
        if data.borrow_rate > 50:
            factors.append(f"Expensive borrow: {data.borrow_rate:.1f}% annual fee")
        if data.price_change_5d > 0.10:
            factors.append(f"Strong momentum: +{data.price_change_5d*100:.1f}% in 5 days")
        if data.volume_surge_ratio > 2:
            factors.append(f"Volume surge: {data.volume_surge_ratio:.1f}x average")
        
        return factors
    
    def find_squeeze_candidates(self, min_score: float = 50) -> List[Dict]:
        """Find stocks with high squeeze potential"""
        candidates = []
        
        for symbol, data in self.data.items():
            squeeze_data = self.calculate_squeeze_risk_score(data)
            
            if squeeze_data["squeeze_risk_score"] >= min_score:
                candidates.append({
                    "symbol": symbol,
                    "score": squeeze_data["squeeze_risk_score"],
                    "risk_level": squeeze_data["risk_level"],
                    "short_pct": self.calculate_short_interest_ratio(data)["short_pct_of_float"],
                    "days_to_cover": data.days_to_cover,
                    "borrow_rate": data.borrow_rate,
                    "recent_momentum": round(data.price_change_5d * 100, 1),
                    "key_factors": squeeze_data["key_factors"]
                })
        
        return sorted(candidates, key=lambda x: x["score"], reverse=True)
    
    def detect_gamma_squeeze_potential(self, data: ShortInterestData, 
                                       call_open_interest: int,
                                       put_call_ratio: float) -> Dict:
        """Detect potential gamma squeeze setup (short + heavy call buying)"""
        # High call OI relative to float creates gamma squeeze risk
        float_size = data.float
        call_coverage = (call_open_interest * 100) / float_size if float_size > 0 else 0
        
        # Short squeeze + gamma squeeze combo
        short_pct = (data.short_interest / data.float) * 100 if data.float > 0 else 0
        
        # Both shorts and market makers need to buy if price rises
        gamma_squeeze_score = 0
        
        if short_pct > 20:
            gamma_squeeze_score += short_pct / 2
        
        if call_coverage > 10:  # Calls cover >10% of float
            gamma_squeeze_score += call_coverage
        
        if put_call_ratio < 0.5:  # Very bullish options positioning
            gamma_squeeze_score += 10
        
        return {
            "symbol": data.symbol,
            "gamma_squeeze_score": round(gamma_squeeze_score, 1),
            "short_pct": round(short_pct, 1),
            "call_coverage_pct": round(call_coverage, 1),
            "put_call_ratio": round(put_call_ratio, 2),
            "setup_type": "GAMMA_SQUEEZE" if gamma_squeeze_score > 40 and call_coverage > 15 else "SHORT_SQUEEZE",
            "explosive_potential": gamma_squeeze_score > 50 and short_pct > 30
        }
    
    def monitor_squeeze_progression(self, symbol: str, 
                                    price_history: List[float],
                                    volume_history: List[int]) -> Dict:
        """Monitor if a squeeze is in progress"""
        if len(price_history) < 5 or symbol not in self.data:
            return {"error": "Insufficient data"}
        
        data = self.data[symbol]
        
        # Price progression
        price_change_1d = (price_history[-1] - price_history[-2]) / price_history[-2]
        price_change_5d = (price_history[-1] - price_history[-5]) / price_history[-5]
        
        # Volume progression
        avg_vol = sum(volume_history) / len(volume_history)
        current_vol = volume_history[-1]
        volume_trend = current_vol / avg_vol
        
        # Squeeze indicators
        squeeze_indicators = []
        
        if price_change_1d > 0.10:  # 10% day
            squeeze_indicators.append("Large daily gain")
        
        if price_change_5d > 0.30:  # 30% week
            squeeze_indicators.append("Strong weekly momentum")
        
        if volume_trend > 3:  # 3x volume
            squeeze_indicators.append("Volume explosion")
        
        if data.borrow_rate > 100:  # 100% borrow fee
            squeeze_indicators.append("Extreme borrow cost")
        
        squeeze_stage = "NOT_STARTED"
        if len(squeeze_indicators) >= 3:
            squeeze_stage = "ACTIVE_SQUEEZE"
        elif len(squeeze_indicators) >= 2:
            squeeze_stage = "EARLY_SQUEEZE"
        elif len(squeeze_indicators) >= 1:
            squeeze_stage = "SETUP_PHASE"
        
        return {
            "symbol": symbol,
            "squeeze_stage": squeeze_stage,
            "indicators_present": len(squeeze_indicators),
            "indicator_list": squeeze_indicators,
            "price_change_1d": round(price_change_1d * 100, 2),
            "price_change_5d": round(price_change_5d * 100, 2),
            "volume_vs_avg": round(volume_trend, 1),
            "assessment": "Squeeze in progress - high volatility expected" if squeeze_stage == "ACTIVE_SQUEEZE" else "Early squeeze signs" if squeeze_stage == "EARLY_SQUEEZE" else "Watch closely"
        }
