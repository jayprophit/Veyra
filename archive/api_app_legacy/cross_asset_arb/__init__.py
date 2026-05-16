"""Cross-Asset Arbitrage - Multi-asset class arbitrage opportunities"""

from .convertible_arb import ConvertibleArbitrage
from .capital_structure import CapitalStructureArbitrage
from .index_arbitrage import IndexArbitrage

__all__ = [
    "ConvertibleArbitrage",
    "CapitalStructureArbitrage",
    "IndexArbitrage"
]
