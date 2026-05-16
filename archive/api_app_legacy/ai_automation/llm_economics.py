"""LLM Economics - Cost and ROI analysis"""
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"

@dataclass
class LLMUsage:
    model: str
    provider: LLMProvider
    input_tokens: int
    output_tokens: int
    cost_per_1k_in: float
    cost_per_1k_out: float

class LLMEconomics:
    def __init__(self):
        self.records: List[LLMUsage] = []
    
    def add_usage(self, u: LLMUsage):
        self.records.append(u)
    
    def calculate_cost(self, u: LLMUsage) -> float:
        return (u.input_tokens / 1000 * u.cost_per_1k_in + 
                u.output_tokens / 1000 * u.cost_per_1k_out)
    
    def get_summary(self) -> Dict:
        if not self.records:
            return {'status': 'NO_DATA'}
        total = sum(self.calculate_cost(r) for r in self.records)
        return {
            'total_records': len(self.records),
            'total_cost': round(total, 2),
            'avg_per_record': round(total / len(self.records), 4)
        }
