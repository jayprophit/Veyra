"""Sentiment Bias Analyzer - Detect sentiment-based biases"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class SentimentBias:
    bias_type: str
    severity: float
    description: str

class SentimentBiasAnalyzer:
    """Analyze sentiment biases in market decisions"""
    
    def __init__(self):
        self.biases: List[SentimentBias] = []
    
    def add_bias(self, bias: SentimentBias):
        self.biases.append(bias)
    
    def get_summary(self) -> Dict:
        return {
            'biases_detected': len(self.biases),
            'avg_severity': sum(b.severity for b in self.biases) / len(self.biases) if self.biases else 0
        }
