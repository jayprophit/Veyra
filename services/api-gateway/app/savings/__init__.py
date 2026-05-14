"""
Automated Savings Rules Module
Grade SSS Feature: AI-powered savings automation
Inspired by Plum, Chip, Monzo
"""

from .savings_rules import SavingsRulesEngine, AutoSaveRule
from .roundups import RoundUpManager
from .ai_savings import AISavingsOptimizer

__all__ = [
    "SavingsRulesEngine",
    "AutoSaveRule",
    "RoundUpManager",
    "AISavingsOptimizer"
]
