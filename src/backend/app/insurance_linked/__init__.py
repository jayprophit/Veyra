"""Insurance Linked Securities - Catastrophe bonds, longevity swaps"""

from .cat_bonds import CatBonds
from .longevity_swaps import LongevitySwaps
from .mortality_linked import MortalityLinked

__all__ = ["CatBonds", "LongevitySwaps", "MortalityLinked"]
