"""Style Rotation"""
from typing import Dict

class StyleRotation:
    def rotation_signal(self, value_return: float, growth_return: float) -> Dict:
        return {"favor": "growth" if growth_return > value_return else "value", "spread": growth_return - value_return}
