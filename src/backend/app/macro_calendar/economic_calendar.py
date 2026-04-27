"""Economic Calendar - Track and analyze economic events"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class EventImpact(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class EconomicEvent:
    name: str
    date: datetime
    country: str
    impact: EventImpact
    forecast: Optional[float]
    previous: Optional[float]
    actual: Optional[float]
    unit: str

class EconomicCalendar:
    """Track and analyze economic events"""
    
    def __init__(self):
        self.events: List[EconomicEvent] = []
        self.market_movers = [
            "Non-Farm Payrolls",
            "CPI",
            "GDP",
            "Fed Interest Rate Decision",
            "Unemployment Rate",
            "Retail Sales",
            "ISM Manufacturing",
            "PPI",
            "FOMC Minutes"
        ]
    
    def add_event(self, event: EconomicEvent):
        """Add event to calendar"""
        self.events.append(event)
        # Sort by date
        self.events.sort(key=lambda x: x.date)
    
    def get_upcoming_events(self, days: int = 7) -> List[EconomicEvent]:
        """Get events in next N days"""
        now = datetime.utcnow()
        future = now + timedelta(days=days)
        
        return [e for e in self.events if now <= e.date <= future]
    
    def get_high_impact_events(self, days: int = 7) -> List[EconomicEvent]:
        """Get high impact events"""
        upcoming = self.get_upcoming_events(days)
        return [e for e in upcoming if e.impact in [EventImpact.HIGH, EventImpact.CRITICAL]]
    
    def analyze_surprise(self, event: EconomicEvent) -> Dict:
        """Analyze if actual result surprised vs forecast"""
        if event.actual is None or event.forecast is None:
            return {"error": "Missing data"}
        
        surprise = event.actual - event.forecast
        surprise_pct = (surprise / event.forecast * 100) if event.forecast != 0 else 0
        
        # Determine significance
        if abs(surprise_pct) > 10:
            significance = "MAJOR"
            market_reaction = "Significant"
        elif abs(surprise_pct) > 5:
            significance = "MODERATE"
            market_reaction = "Notable"
        else:
            significance = "MINOR"
            market_reaction = "Limited"
        
        # Direction
        direction = "BEAT" if surprise > 0 else "MISS"
        
        return {
            "event": event.name,
            "forecast": event.forecast,
            "actual": event.actual,
            "surprise": round(surprise, 3),
            "surprise_pct": round(surprise_pct, 2),
            "direction": direction,
            "significance": significance,
            "expected_market_reaction": market_reaction,
            "trading_implication": self._get_trading_implication(event.name, surprise)
        }
    
    def _get_trading_implication(self, event_name: str, surprise: float) -> str:
        """Get trading implication based on event and surprise"""
        implications = {
            "Non-Farm Payrolls": {
                "positive": "Dollar strength, rates up, tech pressure",
                "negative": "Dollar weakness, rates down, growth stocks rally"
            },
            "CPI": {
                "positive": "Inflation fears, rate hike expectations, volatility",
                "negative": "Disinflation relief, growth stocks rally"
            },
            "GDP": {
                "positive": "Economic strength, cyclicals rally",
                "negative": "Recession fears, defensive rotation"
            },
            "Fed Interest Rate Decision": {
                "positive": "Hawkish - dollar up, bonds down, tech pressure",
                "negative": "Dovish - dollar down, bonds up, growth rally"
            }
        }
        
        direction = "positive" if surprise > 0 else "negative"
        return implications.get(event_name, {}).get(direction, "Monitor market reaction")
    
    def calculate_economic_momentum(self, 
                                   gdp_growth: List[float],
                                   unemployment: List[float],
                                   inflation: List[float]) -> Dict:
        """Calculate overall economic momentum"""
        if len(gdp_growth) < 2 or len(unemployment) < 2 or len(inflation) < 2:
            return {"error": "Insufficient data"}
        
        # Recent vs historical
        recent_gdp = statistics.mean(gdp_growth[-2:])
        historical_gdp = statistics.mean(gdp_growth[:-2])
        
        recent_unemp = statistics.mean(unemployment[-2:])
        historical_unemp = statistics.mean(unemployment[:-2])
        
        recent_cpi = statistics.mean(inflation[-2:])
        historical_cpi = statistics.mean(inflation[:-2])
        
        # Score each component
        gdp_score = 50 + (recent_gdp - historical_gdp) * 10
        unemp_score = 50 - (recent_unemp - historical_unemp) * 15  # Lower unemployment is better
        cpi_score = 50 - (recent_cpi - historical_cpi) * 10  # Lower inflation is better (usually)
        
        momentum = (gdp_score + unemp_score + cpi_score) / 3
        
        return {
            "economic_momentum": round(momentum, 1),
            "regime": "EXPANSION" if momentum > 60 else "SLOWDOWN" if momentum < 40 else "STABLE",
            "components": {
                "growth": round(gdp_score, 1),
                "employment": round(unemp_score, 1),
                "inflation": round(cpi_score, 1)
            },
            "trading_environment": "Cyclical favor" if momentum > 60 else "Defensive favor" if momentum < 40 else "Mixed"
        }
    
    def get_event_risk_calendar(self, portfolio_exposure: Dict[str, float]) -> Dict:
        """Get event risk for specific portfolio"""
        high_impact = self.get_high_impact_events(7)
        
        risk_by_sector = {}
        
        for event in high_impact:
            affected_sectors = self._get_affected_sectors(event.name)
            
            for sector in affected_sectors:
                exposure = portfolio_exposure.get(sector, 0)
                if exposure > 0:
                    risk_by_sector[sector] = {
                        "exposure_pct": exposure,
                        "risk_level": event.impact.value,
                        "upcoming_event": event.name,
                        "event_date": event.date.isoformat()
                    }
        
        total_at_risk = sum(r["exposure_pct"] for r in risk_by_sector.values())
        
        return {
            "events_next_7_days": len(high_impact),
            "portfolio_at_risk_pct": round(total_at_risk, 1),
            "risk_by_sector": risk_by_sector,
            "hedging_recommended": total_at_risk > 30,
            "calendar_heatmap": self._generate_heatmap(high_impact)
        }
    
    def _get_affected_sectors(self, event_name: str) -> List[str]:
        """Get sectors affected by economic event"""
        mappings = {
            "Non-Farm Payrolls": ["consumer", "financials", "industrials"],
            "CPI": ["consumer", "technology", "utilities", "reits"],
            "GDP": ["industrials", "materials", "energy", "consumer"],
            "Fed Interest Rate Decision": ["financials", "reits", "utilities", "technology"],
            "Retail Sales": ["consumer", "retail"],
            "ISM Manufacturing": ["industrials", "materials", "energy"]
        }
        return mappings.get(event_name, ["broad_market"])
    
    def _generate_heatmap(self, events: List[EconomicEvent]) -> List[Dict]:
        """Generate calendar heatmap of event risk"""
        heatmap = []
        
        for i in range(7):
            date = datetime.utcnow() + timedelta(days=i)
            day_events = [e for e in events if e.date.date() == date.date()]
            
            risk_score = sum(
                3 if e.impact == EventImpact.CRITICAL else
                2 if e.impact == EventImpact.HIGH else
                1 if e.impact == EventImpact.MEDIUM else 0
                for e in day_events
            )
            
            heatmap.append({
                "date": date.strftime("%Y-%m-%d"),
                "risk_score": risk_score,
                "risk_level": "HIGH" if risk_score >= 5 else "MEDIUM" if risk_score >= 2 else "LOW",
                "event_count": len(day_events),
                "top_event": day_events[0].name if day_events else None
            })
        
        return heatmap

import statistics
