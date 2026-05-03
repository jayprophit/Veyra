"""Client Progress Tracking"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, date
import uuid

@dataclass
class ProgressMetric:
    id: str
    client_id: str
    metric_type: str
    value: float
    unit: str
    recorded_at: datetime
    notes: str

class ClientProgressTracker:
    def __init__(self):
        self._metrics: Dict[str, ProgressMetric] = {}
        self._sessions: Dict[str, Dict] = {}
    
    def record_metric(self, client_id: str, metric_type: str, value: float,
                     unit: str, notes: str = "") -> ProgressMetric:
        metric = ProgressMetric(
            id=str(uuid.uuid4()),
            client_id=client_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            recorded_at=datetime.now(),
            notes=notes
        )
        self._metrics[metric.id] = metric
        return metric
    
    def record_session(self, client_id: str, advisor_id: str, session_type: str,
                      duration_minutes: int, notes: str = "") -> Dict:
        session = {
            "id": str(uuid.uuid4()),
            "client_id": client_id,
            "advisor_id": advisor_id,
            "session_type": session_type,
            "duration_minutes": duration_minutes,
            "notes": notes,
            "date": datetime.now()
        }
        self._sessions[session["id"]] = session
        return session
    
    def get_client_metrics(self, client_id: str, metric_type: Optional[str] = None) -> List[ProgressMetric]:
        metrics = [m for m in self._metrics.values() if m.client_id == client_id]
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        return sorted(metrics, key=lambda x: x.recorded_at, reverse=True)
    
    def get_client_summary(self, client_id: str) -> Dict:
        metrics = self.get_client_metrics(client_id)
        sessions = [s for s in self._sessions.values() if s["client_id"] == client_id]
        
        # Group by metric type
        by_type = {}
        for m in metrics:
            if m.metric_type not in by_type:
                by_type[m.metric_type] = []
            by_type[m.metric_type].append(m)
        
        return {
            "client_id": client_id,
            "total_sessions": len(sessions),
            "total_metrics_recorded": len(metrics),
            "latest_metrics": {t: sorted(ms, key=lambda x: x.recorded_at)[-1].value 
                             for t, ms in by_type.items()},
            "engagement_score": self._calculate_engagement(client_id),
            "last_session": max(sessions, key=lambda x: x["date"]) if sessions else None
        }
    
    def _calculate_engagement(self, client_id: str) -> int:
        sessions = [s for s in self._sessions.values() if s["client_id"] == client_id]
        metrics_count = len([m for m in self._metrics.values() if m.client_id == client_id])
        
        # Simple scoring
        score = min(100, len(sessions) * 10 + metrics_count * 2)
        return score
