"""Open Source AI - Open source AI model integration"""
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class ModelFramework(Enum):
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    JAX = "jax"
    ONNX = "onnx"

@dataclass
class OpenSourceModel:
    name: str
    framework: ModelFramework
    parameters: int  # in millions
    license: str
    use_case: str

class OpenSourceAI:
    def __init__(self):
        self.models: List[OpenSourceModel] = []
        self._load_catalog()
    
    def _load_catalog(self):
        catalog = [
            OpenSourceModel("Llama-2-7B", ModelFramework.PYTORCH, 7000, "LLaMA-2", "text_generation"),
            OpenSourceModel("Mistral-7B", ModelFramework.PYTORCH, 7000, "Apache-2.0", "text_generation"),
            OpenSourceModel("Stable Diffusion XL", ModelFramework.PYTORCH, 3500, "OpenRAIL", "image_generation"),
        ]
        self.models.extend(catalog)
    
    def get_by_framework(self, framework: ModelFramework) -> List[OpenSourceModel]:
        return [m for m in self.models if m.framework == framework]
    
    def get_by_use_case(self, use_case: str) -> List[OpenSourceModel]:
        return [m for m in self.models if use_case in m.use_case]
    
    def get_summary(self) -> Dict:
        by_framework = {}
        for m in self.models:
            fw = m.framework.value
            by_framework[fw] = by_framework.get(fw, 0) + 1
        
        return {
            'total_models': len(self.models),
            'total_parameters': sum(m.parameters for m in self.models),
            'by_framework': by_framework
        }
