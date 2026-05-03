"""Model Zoo - Curated collection of AI models"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ZooModel:
    model_id: str
    category: str
    task: str
    accuracy: float
    latency_ms: float
    size_mb: float

class ModelZoo:
    def __init__(self):
        self.models: List[ZooModel] = []
        self._load_collection()
    
    def _load_collection(self):
        collection = [
            ZooModel("resnet18", "cv", "classification", 0.698, 15, 45),
            ZooModel("yolov8n", "cv", "object_detection", 0.523, 25, 6),
            ZooModel("bert-base", "nlp", "classification", 0.845, 120, 440),
            ZooModel("whisper-tiny", "audio", "transcription", 0.785, 800, 39),
        ]
        self.models.extend(collection)
    
    def get_by_category(self, category: str) -> List[ZooModel]:
        return [m for m in self.models if m.category == category]
    
    def find_optimal(self, task: str, max_latency: float) -> Optional[ZooModel]:
        candidates = [m for m in self.models if m.task == task and m.latency_ms <= max_latency]
        return max(candidates, key=lambda m: m.accuracy) if candidates else None
    
    def get_summary(self) -> Dict:
        by_category = {}
        for m in self.models:
            by_category[m.category] = by_category.get(m.category, 0) + 1
        
        return {
            'total_models': len(self.models),
            'by_category': by_category,
            'avg_accuracy': round(sum(m.accuracy for m in self.models) / len(self.models), 3) if self.models else 0
        }
