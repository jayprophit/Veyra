"""Decision Analyzer - Analyze financial decisions"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Decision:
    decision_id: str
    description: str
    outcome: str
    rational_score: float

class DecisionAnalyzer:
    """Analyze financial decision patterns"""
    
    def __init__(self):
        self.decisions: List[Decision] = []
    
    def add_decision(self, decision: Decision):
        self.decisions.append(decision)
    
    def get_summary(self) -> Dict:
        return {
            'decisions_analyzed': len(self.decisions),
            'avg_rational_score': sum(d.rational_score for d in self.decisions) / len(self.decisions) if self.decisions else 0
        }
