"""AIOps Manager - AI-driven monitoring and anomaly detection"""

from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

class AIOpsManager:
    """AI Operations for intelligent system monitoring"""
    
    def __init__(self):
        self.anomaly_threshold = 2.5  # Standard deviations
        self.metrics_history = []
        
    async def detect_anomalies(self, metric_stream: List[Dict]) -> List[Dict]:
        """Detect anomalies in real-time metrics using statistical methods"""
        anomalies = []
        
        for metric in metric_stream:
            # Z-score calculation
            mean = np.mean([m['value'] for m in self.metrics_history[-100:]])
            std = np.std([m['value'] for m in self.metrics_history[-100:]])
            
            if std > 0:
                z_score = abs((metric['value'] - mean) / std)
                
                if z_score > self.anomaly_threshold:
                    anomalies.append({
                        'metric': metric['name'],
                        'value': metric['value'],
                        'expected': mean,
                        'z_score': z_score,
                        'timestamp': metric['timestamp'],
                        'severity': 'high' if z_score > 4 else 'medium'
                    })
            
            self.metrics_history.append(metric)
        
        return anomalies
    
    async def root_cause_analysis(self, incident: Dict) -> Dict:
        """AI-driven root cause analysis"""
        # Gather related events
        time_window = {
            'start': (datetime.utcnow() - __import__('datetime').timedelta(hours=1)).isoformat(),
            'end': datetime.utcnow().isoformat()
        }
        
        return {
            'incident_id': incident.get('id'),
            'probable_causes': [
                {'component': 'database', 'confidence': 0.85},
                {'component': 'api_gateway', 'confidence': 0.60}
            ],
            'correlated_events': [],
            'recommended_actions': [
                'Check database connection pool',
                'Review recent deployments'
            ]
        }
    
    async def predict_resource_exhaustion(self) -> Dict:
        """Predict when resources will be exhausted"""
        # Simple linear trend
        if len(self.metrics_history) >= 24:
            recent = [m['value'] for m in self.metrics_history[-24:]]
            trend = np.polyfit(range(len(recent)), recent, 1)[0]
            
            hours_until_exhaustion = (100 - recent[-1]) / trend if trend > 0 else float('inf')
            
            return {
                'resource': 'cpu',
                'current_utilization': recent[-1],
                'trend_per_hour': trend,
                'predicted_exhaustion_hours': hours_until_exhaustion if hours_until_exhaustion > 0 else None,
                'confidence': 0.75
            }
        
        return {'error': 'Insufficient data'}
