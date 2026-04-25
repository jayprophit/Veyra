"""DeFi Integration"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Yield:
    protocol: str
    asset: str
    apy: float

class DeFi:
    async def get_yields(self, asset: str = None) -> List[Yield]:
        ops = [
            Yield("Lido", "ETH", 4.2),
            Yield("Aave", "USDC", 6.5),
            Yield("Compound", "DAI", 5.8),
            Yield("Uniswap", "ETH/USDC", 15.5),
        ]
        return [o for o in ops if not asset or asset in o.asset]
    
    async def swap_quote(self, from_t: str, to_t: str, amt: float) -> dict:
        return {"from": from_t, "to": to_t, "out": amt * 3500, "impact": 0.3}
