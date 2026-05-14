"""Economic Calendar Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class EventImpact(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class EconomicEvent:
    event_id: str
    name: str
    country: str
    impact: EventImpact
    forecast_time: datetime

class EconomicCalendar:
    """Economic calendar with event impact analysis."""
    
    def __init__(self):
        self.events: Dict[str, EconomicEvent] = {}
        self._init_events()
    
    def _init_events(self):
        events = [
            ("US Non-Farm Payrolls", "US", EventImpact.HIGH),
            ("Fed Interest Rate", "US", EventImpact.HIGH),
            ("US CPI", "US", EventImpact.HIGH),
            ("US GDP", "US", EventImpact.HIGH),
            ("ECB Rate", "EU", EventImpact.HIGH)
        ]
        for i, (name, country, impact) in enumerate(events):
            evt_id = f"evt_{i}"
            self.events[evt_id] = EconomicEvent(
                event_id=evt_id, name=name, country=country,
                impact=impact, forecast_time=datetime.now() + timedelta(days=i)
            )
    
    async def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict]:
        now = datetime.now()
        cutoff = now + timedelta(days=days_ahead)
        return [{
            'event_id': e.event_id,
            'name': e.name,
            'country': e.country,
            'impact': e.impact.value,
            'forecast_time': e.forecast_time.isoformat()
        } for e in self.events.values() if now <= e.forecast_time <= cutoff]

economic_calendar = EconomicCalendar()
