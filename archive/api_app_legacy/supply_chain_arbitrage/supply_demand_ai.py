"""Supply Demand AI - Predict imbalances, optimize inventory, forecast shortages"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum

class SupplySignal(Enum):
    SURPLUS = "surplus"; SHORTAGE = "shortage"; BALANCED = "balanced"
    EMERGENCY = "emergency"; HOARDING = "hoarding"; GLUT = "glut"

@dataclass
class SupplyForecast:
    resource: str; region: str; signal: SupplySignal
    confidence: float; predicted_date: date
    price_impact_pct: float; recommended_action: str

class SupplyDemandAI:
    """AI for predicting and profiting from supply/demand imbalances"""
    
    def __init__(self):
        self.forecasts: List[SupplyForecast] = []
        self.historical_imbalances = []
        self.inventory_positions = {}
        
    def predict_shortage(self, resource: str, region: str,
                        horizon_days: int = 90) -> Dict:
        """Predict future supply shortage"""
        # AI model would analyze:
        # - Weather patterns (for agriculture)
        # - Production data
        # - Inventory levels
        # - Import/export flows
        # - Geopolitical risk
        
        # Mock prediction
        confidence = 0.75
        signal = SupplySignal.SHORTAGE
        price_impact = 25  # 25% price increase
        
        forecast = SupplyForecast(
            resource=resource,
            region=region,
            signal=signal,
            confidence=confidence,
            predicted_date=date.today() + timedelta(days=horizon_days),
            price_impact_pct=price_impact,
            recommended_action="buy_now_store"
        )
        
        self.forecasts.append(forecast)
        
        return {
            "resource": resource,
            "region": region,
            "prediction": signal.value,
            "confidence": confidence,
            "predicted_date": forecast.predicted_date.isoformat(),
            "price_impact_pct": price_impact,
            "recommended_action": "Buy and store before shortage",
            "optimal_purchase_timing": "immediate",
            "expected_roi_pct": price_impact * 0.8  # 80% capture of price move
        }
    
    def predict_surplus(self, resource: str, region: str,
                       horizon_days: int = 90) -> Dict:
        """Predict future supply surplus (glut)"""
        confidence = 0.70
        signal = SupplySignal.GLUT
        price_impact = -20  # 20% price decrease
        
        return {
            "resource": resource,
            "region": region,
            "prediction": signal.value,
            "confidence": confidence,
            "predicted_date": (date.today() + timedelta(days=horizon_days)).isoformat(),
            "price_impact_pct": price_impact,
            "recommended_action": "Sell before glut, short if possible",
            "optimal_timing": "within 30 days",
            "expected_roi_pct": abs(price_impact) * 0.7
        }
    
    def get_opportunities(self) -> List[Dict]:
        """Get all supply/demand profit opportunities"""
        opportunities = []
        
        # Weather-based ag opportunities
        weather_opps = [
            {"resource": "corn", "region": "US Midwest", "event": "drought",
             "probability": 0.65, "price_impact": 30, "timeline": "60 days"},
            {"resource": "wheat", "region": "Ukraine", "event": "conflict_disruption",
             "probability": 0.80, "price_impact": 45, "timeline": "ongoing"},
            {"resource": "coffee", "region": "Brazil", "event": "frost",
             "probability": 0.40, "price_impact": 50, "timeline": "seasonal"},
            {"resource": "natural_gas", "region": "Europe", "event": "winter_surge",
             "probability": 0.85, "price_impact": 60, "timeline": "3 months"}
        ]
        
        for w in weather_opps:
            opportunities.append({
                "type": "weather_disruption",
                "resource": w["resource"],
                "region": w["region"],
                "event": w["event"],
                "probability": w["probability"],
                "expected_price_impact_pct": w["price_impact"],
                "strategy": "buy_before_event" if w["probability"] > 0.6 else "watch",
                "timeline": w["timeline"],
                "confidence_score": w["probability"],
                "potential_roi_pct": w["price_impact"] * w["probability"]
            })
        
        # Geopolitical opportunities
        geo_opps = [
            {"resource": "oil", "region": "Middle East", "risk": "supply_disruption",
             "probability": 0.55, "price_impact": 35},
            {"resource": "rare_earth", "region": "China", "risk": "export_restrictions",
             "probability": 0.70, "price_impact": 80},
            {"resource": "lithium", "region": "Chile/Argentina", "risk": "nationalization",
             "probability": 0.45, "price_impact": 40}
        ]
        
        for g in geo_opps:
            opportunities.append({
                "type": "geopolitical",
                "resource": g["resource"],
                "region": g["region"],
                "risk": g["risk"],
                "probability": g["probability"],
                "expected_price_impact_pct": g["price_impact"],
                "strategy": "hedge_or_stockpile",
                "hedge_instrument": f"{g['resource']}_futures",
                "potential_roi_pct": g["price_impact"] * g["probability"]
            })
        
        # Supply chain bottleneck opportunities
        bottleneck_opps = [
            {"resource": "semiconductors", "bottleneck": "TSMC capacity",
             "lead_time_months": 12, "price_impact": 25},
            {"resource": "shipping_containers", "bottleneck": "port_congestion",
             "lead_time_months": 3, "price_impact": 200},
            {"resource": "fertilizer", "bottleneck": "natural_gas_price",
             "lead_time_months": 6, "price_impact": 60}
        ]
        
        for b in bottleneck_opps:
            opportunities.append({
                "type": "supply_chain_bottleneck",
                "resource": b["resource"],
                "bottleneck": b["bottleneck"],
                "lead_time_months": b["lead_time_months"],
                "price_impact_pct": b["price_impact"],
                "strategy": "pre_position_before_shortage",
                "optimal_entry": f"{b['lead_time_months'] - 2} months before peak",
                "potential_roi_pct": b["price_impact"] * 0.9
            })
        
        return sorted(opportunities, key=lambda x: x["potential_roi_pct"], reverse=True)
    
    def optimize_inventory(self, current_inventory: Dict) -> Dict:
        """Optimize inventory levels for maximum profit"""
        recommendations = []
        
        for item, qty in current_inventory.items():
            # AI determines optimal level
            optimal = qty * 1.2  # 20% buffer
            
            # Check against forecasts
            relevant_forecasts = [f for f in self.forecasts if f.resource == item]
            
            if relevant_forecasts:
                forecast = relevant_forecasts[0]
                if forecast.signal == SupplySignal.SHORTAGE:
                    optimal = qty * 2.5  # Stock up before shortage
                    recommendations.append({
                        "item": item,
                        "current": qty,
                        "recommended": optimal,
                        "action": "increase_stock",
                        "reason": f"Predicted shortage in {forecast.region}",
                        "expected_savings": forecast.price_impact_pct
                    })
                elif forecast.signal == SupplySignal.GLUT:
                    optimal = qty * 0.5  # Reduce before price drop
                    recommendations.append({
                        "item": item,
                        "current": qty,
                        "recommended": optimal,
                        "action": "decrease_stock",
                        "reason": f"Predicted surplus in {forecast.region}",
                        "expected_savings": abs(forecast.price_impact_pct)
                    })
        
        return {
            "total_recommendations": len(recommendations),
            "potential_savings_pct": sum(r["expected_savings"] for r in recommendations) / len(recommendations) if recommendations else 0,
            "actions": recommendations
        }
    
    def seasonal_patterns(self, resource: str) -> Dict:
        """Get seasonal supply/demand patterns"""
        patterns = {
            "natural_gas": {"peak": ["Dec", "Jan", "Feb"], "low": ["Jun", "Jul", "Aug"],
                          "price_variance_pct": 45},
            "gasoline": {"peak": ["Jun", "Jul", "Aug"], "low": ["Jan", "Feb"],
                        "price_variance_pct": 30},
            "agriculture": {"peak": ["Aug", "Sep", "Oct"], "low": ["Mar", "Apr"],
                          "price_variance_pct": 25},
            "heating_oil": {"peak": ["Nov", "Dec", "Jan"], "low": ["Jun", "Jul"],
                          "price_variance_pct": 35}
        }
        
        return patterns.get(resource, {"pattern": "unknown"})
