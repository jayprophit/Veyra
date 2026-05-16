"""GitHub Models - Integration with GitHub's AI model marketplace"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class GitHubModel:
    model_id: str
    name: str
    owner: str
    downloads: int
    rating: float
    tags: List[str]
    license: str

class GitHubModels:
    def __init__(self):
        self.models: List[GitHubModel] = []
        self._load_popular()
    
    def _load_popular(self):
        """Load popular GitHub AI models"""
        popular = [
            GitHubModel("gpt2", "GPT-2", "openai", 50000, 4.5, ["nlp", "transformer"], "MIT"),
            GitHubModel("bert-base", "BERT Base", "google", 45000, 4.7, ["nlp", "embedding"], "Apache-2.0"),
            GitHubModel("resnet50", "ResNet-50", "microsoft", 30000, 4.6, ["cv", "classification"], "MIT"),
        ]
        self.models.extend(popular)
    
    def search(self, query: str) -> List[GitHubModel]:
        return [m for m in self.models if query.lower() in m.name.lower() or query.lower() in m.tags]
    
    def get_by_tag(self, tag: str) -> List[GitHubModel]:
        return [m for m in self.models if tag in m.tags]
    
    def get_summary(self) -> Dict:
        if not self.models:
            return {'status': 'NO_MODELS'}
        by_license = {}
        for m in self.models:
            by_license[m.license] = by_license.get(m.license, 0) + 1
        
        return {
            'total_models': len(self.models),
            'total_downloads': sum(m.downloads for m in self.models),
            'avg_rating': round(sum(m.rating for m in self.models) / len(self.models), 2),
            'by_license': by_license
        }
