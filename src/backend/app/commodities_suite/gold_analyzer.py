"""Gold Analyzer - Gold price analysis, seasonal patterns, safe haven flows"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GoldData:
    price: float
    real_yield_10y: float  # Real Treasury yield (inverse correlation)
    dxy_index: float  # Dollar index (inverse correlation)
    etf_holdings: float  # Total ETF holdings in tonnes
    central_bank_purchases: float  # Monthly CB purchases in tonnes
    geopolitical_risk_index: float  # 0-100
    inflation_expectations: float  # 5Y5Y forward
    timestamp: datetime

class GoldAnalyzer:
    """Analyze gold market dynamics and generate signals"""
    
    def __init__(self):
        self.data_history: List[GoldData] = []
        self.fair_value_model_weights = {
            "real_yield": -0.4,  # Negative correlation
            "dxy": -0.3,
            "inflation": 0.2,
            "geopolitical": 0.1
        }
    
    def add_data(self, data: GoldData):
        """Add gold market data"""
        self.data_history.append(data)
    
    def calculate_fair_value(self, data: GoldData) -> Dict:
        """Calculate gold fair value based on fundamental drivers"""
        # Simplified fair value model
        base_price = 1800  # Historical average base
        
        # Real yield impact (inverted)
        yield_impact = (2.0 - data.real_yield_10y) * 100  # Higher yields = lower gold price
        
        # Dollar impact (inverted)
        dxy_impact = (100 - data.dxy_index) * 5
        
        # Inflation expectations impact
        inflation_impact = data.inflation_expectations * 50
        
        # Geopolitical risk premium
        geo_premium = data.geopolitical_risk_index * 2
        
        fair_value = base_price + yield_impact + dxy_impact + inflation_impact + geo_premium
        
        deviation = ((data.price - fair_value) / fair_value) * 100
        
        return {
            "current_price": data.price,
            "fair_value": round(fair_value, 2),
            "deviation_pct": round(deviation, 2),
            "valuation": "OVERVALUED" if deviation > 10 else "UNDERVALUED" if deviation < -10 else "FAIR",
            "components": {
                "base": base_price,
                "yield_impact": round(yield_impact, 2),
                "dollar_impact": round(dxy_impact, 2),
                "inflation_impact": round(inflation_impact, 2),
                "geopolitical_premium": round(geo_premium, 2)
            }
        }
    
    def analyze_demand_flows(self, data: GoldData) -> Dict:
        """Analyze demand flows from ETFs and central banks"""
        # ETF flow momentum
        if len(self.data_history) >= 2:
            prev_data = self.data_history[-2]
            etf_change = data.etf_holdings - prev_data.etf_holdings
            etf_flow_trend = "INCREASING" if etf_change > 0 else "DECREASING"
        else:
            etf_change = 0
            etf_flow_trend = "NEUTRAL"
        
        # Central bank demand strength
        cb_demand_rating = "STRONG" if data.central_bank_purchases > 30 else "MODERATE" if data.central_bank_purchases > 10 else "WEAK"
        
        return {
            "etf_holdings_tonnes": round(data.etf_holdings, 1),
            "etf_change_tonnes": round(etf_change, 1),
            "etf_flow_trend": etf_flow_trend,
            "central_bank_monthly_purchases": round(data.central_bank_purchases, 1),
            "central_bank_demand": cb_demand_rating,
            "demand_assessment": "BULLISH" if etf_change > 0 and data.central_bank_purchases > 20 else "BEARISH" if etf_change < -10 else "NEUTRAL"
        }
    
    def seasonal_analysis(self, month: int = None) -> Dict:
        """Analyze seasonal gold patterns"""
        if month is None:
            month = datetime.utcnow().month
        
        # Historical seasonal performance (simplified)
        seasonal_strength = {
            1: "STRONG",    # January - strong
            2: "MODERATE",  # February
            3: "WEAK",      # March - often weak
            4: "WEAK",      # April
            5: "MODERATE",  # May
            6: "MODERATE",  # June
            7: "MODERATE",  # July
            8: "STRONG",    # August - strong
            9: "STRONG",    # September - strongest
            10: "MODERATE", # October
            11: "MODERATE", # November
            12: "WEAK"      # December - profit taking
        }
        
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        return {
            "current_month": month_names[month - 1],
            "seasonal_bias": seasonal_strength.get(month, "NEUTRAL"),
            "seasonal_commentary": self._seasonal_commentary(month),
            "best_months": ["August", "September", "January"],
            "weakest_months": ["March", "April", "December"]
        }
    
    def _seasonal_commentary(self, month: int) -> str:
        """Generate seasonal commentary"""
        comments = {
            1: "New year investment demand typically strong",
            2: "Chinese New Year buying provides support",
            3: "Often weakest month - patience required",
            4: "Spring weakness before summer rally",
            8: "Seasonal strength begins - festival demand",
            9: "Historically strongest month",
            12: "Year-end profit taking pressure"
        }
        return comments.get(month, "No strong seasonal bias")
    
    def generate_signal(self, data: GoldData = None) -> Dict:
        """Generate comprehensive gold trading signal"""
        if data is None and self.data_history:
            data = self.data_history[-1]
        elif data is None:
            return {"error": "No data available"}
        
        fair_value = self.calculate_fair_value(data)
        demand = self.analyze_demand_flows(data)
        seasonal = self.seasonal_analysis()
        
        # Composite score (-100 to +100)
        score = 0
        
        # Valuation signal
        if fair_value["valuation"] == "UNDERVALUED":
            score += 30
        elif fair_value["valuation"] == "OVERVALUED":
            score -= 20
        
        # Demand signal
        if demand["demand_assessment"] == "BULLISH":
            score += 25
        elif demand["demand_assessment"] == "BEARISH":
            score -= 15
        
        # Real yield signal (inverse)
        if data.real_yield_10y < 0:
            score += 20  # Negative real rates bullish for gold
        elif data.real_yield_10y > 2:
            score -= 20
        
        # Geopolitical signal
        if data.geopolitical_risk_index > 70:
            score += 15
        
        # Seasonal adjustment
        if seasonal["seasonal_bias"] == "STRONG":
            score += 10
        elif seasonal["seasonal_bias"] == "WEAK":
            score -= 10
        
        signal_strength = abs(score)
        
        return {
            "timestamp": data.timestamp.isoformat(),
            "gold_price": data.price,
            "composite_score": score,
            "signal": "BUY" if score > 20 else "SELL" if score < -20 else "HOLD",
            "confidence": "HIGH" if signal_strength > 50 else "MODERATE" if signal_strength > 30 else "LOW",
            "analysis": {
                "fair_value": fair_value,
                "demand_flows": demand,
                "seasonal": seasonal
            },
            "key_drivers": self._identify_key_drivers(data, score)
        }
    
    def _identify_key_drivers(self, data: GoldData, score: int) -> List[str]:
        """Identify the most important factors"""
        drivers = []
        
        if data.real_yield_10y < 0:
            drivers.append(f"Negative real yields ({data.real_yield_10y}%)")
        
        if data.geopolitical_risk_index > 60:
            drivers.append(f"Elevated geopolitical risk ({data.geopolitical_risk_index})")
        
        if data.central_bank_purchases > 20:
            drivers.append(f"Strong central bank buying ({data.central_bank_purchases} tonnes)")
        
        if data.dxy_index > 105:
            drivers.append(f"Strong dollar headwind (DXY {data.dxy_index})")
        elif data.dxy_index < 95:
            drivers.append(f"Weak dollar tailwind (DXY {data.dxy_index})")
        
        if not drivers:
            drivers.append("Mixed factors - no dominant driver")
        
        return drivers
