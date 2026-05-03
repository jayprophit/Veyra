"""Anomaly Detector - Detect anomalies in financial data"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

@dataclass
class Anomaly:
    timestamp: datetime
    value: float
    expected_range: tuple
    severity: str  # 'low', 'medium', 'high', 'critical'
    metric_name: str

class AnomalyDetector:
    def __init__(self, threshold_sigma: float = 2.0):
        self.threshold_sigma = threshold_sigma
        self.anomalies: List[Anomaly] = []
    
    def detect(self, data: List[float], timestamps: List[datetime], metric_name: str) -> List[Anomaly]:
        if len(data) < 10:
            return []
        
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        std = variance ** 0.5
        
        detected = []
        for i, (ts, val) in enumerate(zip(timestamps, data)):
            if abs(val - mean) > self.threshold_sigma * std:
                severity = 'low' if abs(val - mean) < 2.5 * std else 'medium' if abs(val - mean) < 3 * std else 'high' if abs(val - mean) < 4 * std else 'critical'
                detected.append(Anomaly(
                    ts, val, (mean - std, mean + std), severity, metric_name
                ))
        
        self.anomalies.extend(detected)
        return detected
    
    def get_summary(self) -> Dict:
        if not self.anomalies:
            return {'status': 'NO_ANOMALIES'}
        by_severity = {}
        for a in self.anomalies:
            s = a.severity
            by_severity[s] = by_severity.get(s, 0) + 1
        
        return {
            'total_anomalies': len(self.anomalies),
            'by_severity': by_severity
        }
