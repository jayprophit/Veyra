"""Disaster Prediction AI - Predict natural disasters and their market impact"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

class DisasterType(Enum):
    HURRICANE = "hurricane"
    EARTHQUAKE = "earthquake"
    WILDFIRE = "wildfire"
    FLOOD = "flood"
    DROUGHT = "drought"
    TORNADO = "tornado"
    TSUNAMI = "tsunami"
    VOLCANIC = "volcanic"
    PANDEMIC = "pandemic"
    CYBER = "cyber_attack"

class Severity(Enum):
    LOW = 1
    MODERATE = 2
    HIGH = 3
    EXTREME = 4
    CATASTROPHIC = 5

@dataclass
class DisasterEvent:
    disaster_type: DisasterType
    severity: Severity
    location: str
    predicted_date: datetime
    confidence: float
    affected_sectors: List[str]
    estimated_damage_usd: Decimal

class DisasterPredictionAI:
    """Predict natural disasters and calculate market hedging strategies"""
    
    def __init__(self):
        self.monitored_regions = []
        self.disaster_history = []
        self.sector_impact_map = self._init_sector_impacts()
        
    def _init_sector_impacts(self) -> Dict:
        """Map disasters to affected sectors and typical impact"""
        return {
            DisasterType.HURRICANE: {
                "direct_sectors": ["Insurance", "Energy", "Real Estate", "Retail", "Agriculture"],
                "indirect_sectors": ["Construction", "Home Improvement", "Utilities"],
                "typique_duration_days": 30,
                "avg_market_impact_pct": -2.0,
                "recovery_sectors": ["Construction", "Building Materials"]
            },
            DisasterType.EARTHQUAKE: {
                "direct_sectors": ["Insurance", "Real Estate", "Utilities", "Transportation"],
                "indirect_sectors": ["Construction", "Engineering", "Medical"],
                "typique_duration_days": 90,
                "avg_market_impact_pct": -3.0,
                "recovery_sectors": ["Construction", "Infrastructure"]
            },
            DisasterType.WILDFIRE: {
                "direct_sectors": ["Insurance", "Real Estate", "Agriculture", "Forestry"],
                "indirect_sectors": ["Utilities", "Tourism"],
                "typique_duration_days": 60,
                "avg_market_impact_pct": -1.5,
                "recovery_sectors": ["Construction", "Landscaping"]
            },
            DisasterType.FLOOD: {
                "direct_sectors": ["Insurance", "Agriculture", "Real Estate", "Automotive"],
                "indirect_sectors": ["Construction", "Utilities"],
                "typique_duration_days": 45,
                "avg_market_impact_pct": -1.0,
                "recovery_sectors": ["Construction", "Agriculture"]
            },
            DisasterType.DROUGHT: {
                "direct_sectors": ["Agriculture", "Water Utilities", "Energy"],
                "indirect_sectors": ["Food Processing", "Beverages"],
                "typique_duration_days": 180,
                "avg_market_impact_pct": -0.5,
                "recovery_sectors": ["Agriculture Technology"]
            },
            DisasterType.PANDEMIC: {
                "direct_sectors": ["Travel", "Hospitality", "Entertainment", "Retail"],
                "indirect_sectors": ["Healthcare", "Pharma", "Technology", "Delivery"],
                "typique_duration_days": 365,
                "avg_market_impact_pct": -10.0,
                "recovery_sectors": ["Healthcare", "Technology"],
                "beneficiaries": ["Pharma", "Biotech", "Telehealth", "E-commerce"]
            }
        }
    
    def predict_weather_disaster(self, 
                                region: str,
                                weather_data: Dict,
                                season: str) -> Optional[DisasterEvent]:
        """Predict natural disasters from weather patterns"""
        predictions = []
        
        # Hurricane prediction (Atlantic/Gulf coast, June-November)
        if region in ["US_GULF", "US_ATLANTIC", "CARIBBEAN"] and season in ["summer", "fall"]:
            sea_surface_temp = weather_data.get("sea_surface_temp", 26)
            wind_shear = weather_data.get("wind_shear", 10)
            pressure = weather_data.get("pressure", 1010)
            
            # Hurricane formation conditions
            if sea_surface_temp > 26.5 and wind_shear < 20 and pressure < 1008:
                confidence = min((sea_surface_temp - 26) * 10 + (20 - wind_shear) * 2, 100)
                predictions.append(DisasterEvent(
                    disaster_type=DisasterType.HURRICANE,
                    severity=Severity.HIGH if sea_surface_temp > 28 else Severity.MODERATE,
                    location=region,
                    predicted_date=datetime.utcnow() + timedelta(days=5),
                    confidence=confidence / 100,
                    affected_sectors=self.sector_impact_map[DisasterType.HURRICANE]["direct_sectors"],
                    estimated_damage_usd=Decimal("10000000000")  # $10B default
                ))
        
        # Drought prediction
        if weather_data.get("rainfall_mm", 100) < 50 and weather_data.get("temperature_c", 25) > 30:
            predictions.append(DisasterEvent(
                disaster_type=DisasterType.DROUGHT,
                severity=Severity.MODERATE,
                location=region,
                predicted_date=datetime.utcnow() + timedelta(days=30),
                confidence=0.6,
                affected_sectors=self.sector_impact_map[DisasterType.DROUGHT]["direct_sectors"],
                estimated_damage_usd=Decimal("5000000000")
            ))
        
        return predictions[0] if predictions else None
    
    def calculate_market_impact(self, disaster: DisasterEvent) -> Dict:
        """Calculate expected market impact from disaster"""
        impact_data = self.sector_impact_map.get(disaster.disaster_type, {})
        
        severity_multiplier = disaster.severity.value / 3  # Normalize to 1.0
        
        # Calculate sector-specific impacts
        sector_impacts = {}
        
        for sector in impact_data.get("direct_sectors", []):
            base_impact = -5.0 * severity_multiplier  # -5% to -25%
            sector_impacts[sector] = {
                "expected_impact_pct": round(base_impact, 1),
                "impact_timing": "immediate",
                "recovery_timeline_days": impact_data.get("typique_duration_days", 30)
            }
        
        for sector in impact_data.get("indirect_sectors", []):
            base_impact = -2.0 * severity_multiplier  # -2% to -10%
            sector_impacts[sector] = {
                "expected_impact_pct": round(base_impact, 1),
                "impact_timing": "1-2 weeks",
                "recovery_timeline_days": impact_data.get("typique_duration_days", 30) + 15
            }
        
        # Beneficiaries (positive impact)
        for sector in impact_data.get("recovery_sectors", []):
            sector_impacts[sector] = {
                "expected_impact_pct": round(3.0 * severity_multiplier, 1),
                "impact_timing": "1-4 weeks post-disaster",
                "recovery_timeline_days": impact_data.get("typique_duration_days", 30),
                "type": "beneficiary"
            }
        
        # Overall market impact
        market_impact = impact_data.get("avg_market_impact_pct", -1.0) * severity_multiplier
        
        return {
            "disaster_type": disaster.disaster_type.value,
            "severity": disaster.severity.name,
            "location": disaster.location,
            "predicted_date": disaster.predicted_date.isoformat(),
            "confidence": disaster.confidence,
            "overall_market_impact_pct": round(market_impact, 1),
            "sector_impacts": sector_impacts,
            "estimated_damage": float(disaster.estimated_damage_usd),
            "vix_spike_expected": disaster.severity.value > 3
        }
    
    def generate_hedge_strategy(self, 
                               portfolio: Dict[str, Decimal],
                               predicted_disaster: DisasterEvent) -> Dict:
        """Generate hedging strategy for predicted disaster"""
        impact = self.calculate_market_impact(predicted_disaster)
        
        hedges = []
        
        # Identify portfolio exposure
        exposed_holdings = []
        for symbol, value in portfolio.items():
            # Check if symbol is in affected sector
            for sector, data in impact["sector_impacts"].items():
                if data["expected_impact_pct"] < -3:  # Significant negative impact
                    exposed_holdings.append({
                        "symbol": symbol,
                        "value": float(value),
                        "exposed_sector": sector,
                        "expected_loss_pct": abs(data["expected_impact_pct"])
                    })
        
        # Suggest hedges
        if predicted_disaster.disaster_type == DisasterType.HURRICANE:
            hedges = [
                {
                    "type": "short_insurance",
                    "target": "Insurance ETFs (KIE, IAK)",
                    "allocation_pct": 10,
                    "rationale": "Insurance stocks drop after hurricanes"
                },
                {
                    "type": "long_construction",
                    "target": "Construction/Home Improvement (HD, LOW)",
                    "allocation_pct": 5,
                    "rationale": "Post-disaster rebuild demand"
                },
                {
                    "type": "vix_calls",
                    "target": "VIX call options",
                    "allocation_pct": 2,
                    "rationale": "Volatility spike expected"
                }
            ]
        elif predicted_disaster.disaster_type == DisasterType.PANDEMIC:
            hedges = [
                {
                    "type": "short_travel",
                    "target": "Airlines, Hotels, Cruise lines",
                    "allocation_pct": 15,
                    "rationale": "Travel restrictions and fear"
                },
                {
                    "type": "long_healthcare",
                    "target": "Pharma, Biotech, Telehealth",
                    "allocation_pct": 20,
                    "rationale": "Healthcare demand surge"
                },
                {
                    "type": "long_tech",
                    "target": "Remote work enablers",
                    "allocation_pct": 10,
                    "rationale": "Work from home acceleration"
                }
            ]
        
        # Calculate total exposure
        total_exposure = sum(h["value"] for h in exposed_holdings)
        portfolio_value = sum(float(v) for v in portfolio.values())
        
        return {
            "predicted_disaster": predicted_disaster.disaster_type.value,
            "prediction_confidence": predicted_disaster.confidence,
            "portfolio_at_risk_pct": (total_exposure / portfolio_value * 100) if portfolio_value > 0 else 0,
            "exposed_holdings": exposed_holdings,
            "recommended_hedges": hedges,
            "estimated_hedge_cost_pct": 3.0,  # 3% of portfolio
            "potential_loss_without_hedge": total_exposure * 0.05,  # Assume 5% avg loss
            "hedge_effectiveness": "Medium-High" if predicted_disaster.confidence > 0.7 else "Medium"
        }
    
    def get_catastrophe_bond_opportunities(self, 
                                           disaster_probabilities: List[Dict]) -> List[Dict]:
        """Analyze catastrophe bond investment opportunities"""
        opportunities = []
        
        for prob in disaster_probabilities:
            if prob["probability"] > 0.3:  # Significant risk
                # Higher probability = higher cat bond yields
                base_yield = 0.05  # 5% base
                risk_premium = prob["probability"] * 0.15  # Up to 15% additional
                
                opportunities.append({
                    "disaster_type": prob["type"],
                    "region": prob["region"],
                    "probability": prob["probability"],
                    "cat_bond_yield_pct": (base_yield + risk_premium) * 100,
                    "risk_adjusted_return": (base_yield + risk_premium) / max(prob["probability"], 0.01),
                    "recommendation": "ATTRACTIVE" if prob["probability"] < 0.5 and risk_premium > 0.08 else "FAIR"
                })
        
        return sorted(opportunities, key=lambda x: x["risk_adjusted_return"], reverse=True)
    
    def monitor_seismic_activity(self, 
                                seismic_data: List[Dict],
                                region: str) -> Optional[DisasterEvent]:
        """Monitor seismic activity for earthquake prediction"""
        if len(seismic_data) < 10:
            return None
        
        # Look for foreshock patterns
        magnitudes = [s["magnitude"] for s in seismic_data]
        frequency = len(seismic_data) / 30  # per day
        
        # Swarm detection
        if frequency > 5 and max(magnitudes) > 3.0:
            confidence = min(frequency / 10 + max(magnitudes) / 10, 1.0)
            
            return DisasterEvent(
                disaster_type=DisasterType.EARTHQUAKE,
                severity=Severity.HIGH if max(magnitudes) > 4.0 else Severity.MODERATE,
                location=region,
                predicted_date=datetime.utcnow() + timedelta(days=7),
                confidence=confidence,
                affected_sectors=self.sector_impact_map[DisasterType.EARTHQUAKE]["direct_sectors"],
                estimated_damage_usd=Decimal("50000000000") if max(magnitudes) > 5.0 else Decimal("10000000000")
            )
        
        return None
