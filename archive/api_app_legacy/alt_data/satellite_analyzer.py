"""Satellite Data Analyzer - Retail traffic, car counts, oil tanks"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SatelliteSignal:
    company: str
    ticker: str
    signal_type: str  # PARKING, OIL_TANK, CROP, etc
    current_reading: float
    historical_avg: float
    change_pct: float
    confidence: str
    trade_implication: str

class SatelliteDataAnalyzer:
    """Analyze satellite imagery data for trading signals"""
    
    def __init__(self):
        self.data_sources = {
            "parking_lots": ["WMT", "TGT", "COST", "HD", "LOW"],
            "oil_tanks": ["XOM", "CVX", "COP", "SLB"],
            "mining_sites": ["FCX", "BHP", "RIO"],
            "shipping_ports": ["MAERSK", "SINGAPORE"],
            "crop_fields": ["CORN", "SOYB", "WEAT"]
        }
    
    def analyze_retail_traffic(self, ticker: str, 
                               parking_counts: List[int],
                               dates: List[datetime]) -> SatelliteSignal:
        """Analyze retail parking lot data"""
        if len(parking_counts) < 30:
            return None
        
        current = parking_counts[-1]
        
        # Compare to same day last year (seasonal adjustment)
        year_ago_idx = -252 if len(parking_counts) >= 252 else -len(parking_counts)
        year_ago = parking_counts[year_ago_idx] if abs(year_ago_idx) <= len(parking_counts) else parking_counts[0]
        
        # Compare to recent average
        recent_avg = sum(parking_counts[-30:]) / 30
        
        # YoY change
        yoy_change = (current - year_ago) / year_ago * 100 if year_ago > 0 else 0
        
        # Recent trend
        recent_trend = (current - recent_avg) / recent_avg * 100 if recent_avg > 0 else 0
        
        # Determine signal
        if recent_trend > 20 and yoy_change > 10:
            implication = "STRONG_BUY"
            confidence = "HIGH"
        elif recent_trend > 10:
            implication = "BUY"
            confidence = "MEDIUM"
        elif recent_trend < -20 and yoy_change < -10:
            implication = "STRONG_SELL"
            confidence = "HIGH"
        elif recent_trend < -10:
            implication = "SELL"
            confidence = "MEDIUM"
        else:
            implication = "NEUTRAL"
            confidence = "LOW"
        
        return SatelliteSignal(
            company=ticker,
            ticker=ticker,
            signal_type="RETAIL_TRAFFIC",
            current_reading=current,
            historical_avg=recent_avg,
            change_pct=round(recent_trend, 1),
            confidence=confidence,
            trade_implication=implication
        )
    
    def analyze_oil_storage(self, ticker: str,
                           tank_levels: List[float],
                           dates: List[datetime]) -> SatelliteSignal:
        """Analyze oil storage tank levels from satellite"""
        if len(tank_levels) < 12:  # Monthly data
            return None
        
        current = tank_levels[-1]
        avg_12m = sum(tank_levels[-12:]) / 12
        
        change_pct = (current - avg_12m) / avg_12m * 100 if avg_12m > 0 else 0
        
        # High storage = bearish for oil
        # Low storage = bullish for oil
        if change_pct > 20:
            implication = "BEARISH_OIL"  # Too much supply
            confidence = "HIGH"
        elif change_pct > 10:
            implication = "SLIGHTLY_BEARISH"
            confidence = "MEDIUM"
        elif change_pct < -20:
            implication = "BULLISH_OIL"  # Supply constraint
            confidence = "HIGH"
        elif change_pct < -10:
            implication = "SLIGHTLY_BULLISH"
            confidence = "MEDIUM"
        else:
            implication = "NEUTRAL"
            confidence = "LOW"
        
        return SatelliteSignal(
            company=ticker,
            ticker=ticker,
            signal_type="OIL_STORAGE",
            current_reading=current,
            historical_avg=avg_12m,
            change_pct=round(change_pct, 1),
            confidence=confidence,
            trade_implication=implication
        )
    
    def analyze_mining_activity(self, ticker: str,
                               activity_index: List[float]) -> SatelliteSignal:
        """Analyze mining site activity from satellite"""
        if len(activity_index) < 6:
            return None
        
        current = activity_index[-1]
        avg_6m = sum(activity_index[-6:]) / 6
        
        change_pct = (current - avg_6m) / avg_6m * 100 if avg_6m > 0 else 0
        
        # Higher activity = more production
        if change_pct > 30:
            implication = "PRODUCTION_SURGE"
            confidence = "HIGH"
        elif change_pct > 15:
            implication = "INCREASING_ACTIVITY"
            confidence = "MEDIUM"
        elif change_pct < -30:
            implication = "PRODUCTION_HALT"
            confidence = "HIGH"
        elif change_pct < -15:
            implication = "DECREASING_ACTIVITY"
            confidence = "MEDIUM"
        else:
            implication = "NORMAL"
            confidence = "LOW"
        
        return SatelliteSignal(
            company=ticker,
            ticker=ticker,
            signal_type="MINING_ACTIVITY",
            current_reading=current,
            historical_avg=avg_6m,
            change_pct=round(change_pct, 1),
            confidence=confidence,
            trade_implication=implication
        )
    
    def get_alternative_data_summary(self, ticker: str) -> Dict:
        """Get summary of all alternative data signals for a ticker"""
        signals = []
        
        # Check which data types apply
        if ticker in self.data_sources["parking_lots"]:
            signals.append({"type": "RETAIL_TRAFFIC", "available": True, "frequency": "Weekly"})
        
        if ticker in self.data_sources["oil_tanks"]:
            signals.append({"type": "OIL_STORAGE", "available": True, "frequency": "Monthly"})
        
        if ticker in self.data_sources["mining_sites"]:
            signals.append({"type": "MINING_ACTIVITY", "available": True, "frequency": "Monthly"})
        
        return {
            "ticker": ticker,
            "available_signals": len(signals),
            "signals": signals,
            "data_quality": "HIGH" if len(signals) > 1 else "MEDIUM" if signals else "NONE",
            "edge_potential": "Significant" if len(signals) > 1 else "Limited"
        }
    
    def generate_alternative_alpha(self, universe: List[str],
                                  data_map: Dict[str, Dict]) -> List[Dict]:
        """Generate alpha signals from alternative data"""
        alpha_signals = []
        
        for ticker in universe:
            if ticker not in data_map:
                continue
            
            data = data_map[ticker]
            
            # Combine multiple signals if available
            signal_strength = 0
            confidence_sum = 0
            
            if "retail_traffic" in data:
                retail_change = data["retail_traffic"]["change_pct"]
                signal_strength += retail_change * 0.4  # 40% weight
                confidence_sum += 0.4
            
            if "oil_storage" in data:
                oil_change = -data["oil_storage"]["change_pct"]  # Inverse (high storage = bearish)
                signal_strength += oil_change * 0.3
                confidence_sum += 0.3
            
            if "mining_activity" in data:
                mining_change = data["mining_activity"]["change_pct"]
                signal_strength += mining_change * 0.3
                confidence_sum += 0.3
            
            if confidence_sum > 0:
                normalized_signal = signal_strength / confidence_sum
                
                alpha_signals.append({
                    "ticker": ticker,
                    "composite_signal": round(normalized_signal, 2),
                    "direction": "LONG" if normalized_signal > 5 else "SHORT" if normalized_signal < -5 else "NEUTRAL",
                    "confidence": "HIGH" if confidence_sum > 0.8 else "MEDIUM",
                    "expected_return": round(normalized_signal * 0.5, 2),  # 0.5% per unit signal
                    "sources_used": len(data)
                })
        
        return sorted(alpha_signals, key=lambda x: abs(x["composite_signal"]), reverse=True)
