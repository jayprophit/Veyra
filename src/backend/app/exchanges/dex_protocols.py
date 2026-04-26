"""
Decentralized Exchange (DEX) Protocol Integrations
Uniswap, SushiSwap, PancakeSwap, Curve, 1inch, dYdX
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import asyncio
import json


class Chain(Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BSC = "bsc"
    AVALANCHE = "avalanche"


class DEXType(Enum):
    AMM = "amm"  # Automated Market Maker (Uniswap, Sushi)
    ORDERBOOK = "orderbook"  # dYdX, Loopring
    AGGREGATOR = "aggregator"  # 1inch, Paraswap
    STABLE = "stable"  # Curve


@dataclass
class DEXSwap:
    """DEX swap parameters"""
    token_in: str
    token_out: str
    amount_in: Decimal
    min_amount_out: Optional[Decimal] = None
    max_slippage: Decimal = Decimal("0.01")  # 1%
    deadline_minutes: int = 20


@dataclass
class LiquidityPool:
    """Liquidity pool info"""
    pool_address: str
    dex_name: str
    token0: str
    token1: str
    reserve0: Decimal
    reserve1: Decimal
    total_supply: Decimal
    apy: Optional[Decimal] = None
    fee_tier: Decimal = Decimal("0.003")  # 0.3%


class DEXProtocolManager:
    """
    Manages DEX protocol integrations
    
    Supports:
    - AMMs: Uniswap V2/V3, SushiSwap, PancakeSwap
    - Stable swaps: Curve Finance
    - Aggregators: 1inch, Paraswap
    - Orderbook DEXs: dYdX
    """
    
    # Router addresses by chain
    ROUTERS = {
        Chain.ETHEREUM: {
            "uniswap_v3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "sushiswap": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
            "curve": "0xF98B45fa12E8Cf3aE3d1D0bAaeE57064bD54653F",
            "1inch": "0x1111111254EEB25477B68fb85Ed929f73A960582"
        },
        Chain.POLYGON: {
            "uniswap_v3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "sushiswap": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
            "quickswap": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"
        },
        Chain.BSC: {
            "pancakeswap": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
            "biswap": "0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8"
        },
        Chain.ARBITRUM: {
            "uniswap_v3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "sushiswap": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
        }
    }
    
    # Token addresses (mainnet examples)
    TOKENS = {
        Chain.ETHEREUM: {
            "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "USDC": "0xA0b86a33E6441E6C7D3D4B4f6B7E8f9a2B3c4D5e",
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
        }
    }
    
    def __init__(self, provider_url: str, chain: Chain = Chain.ETHEREUM):
        self.provider_url = provider_url
        self.chain = chain
        self.web3 = None  # Web3 instance would be initialized here
        self.routers = self.ROUTERS.get(chain, {})
        self.price_cache: Dict[str, Dict] = {}
    
    async def get_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: Decimal,
        dex_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get swap quote from best DEX
        
        Compares prices across DEXs and returns best route
        """
        quotes = []
        
        # Get quotes from each DEX
        for dex_name, router in self.routers.items():
            try:
                if dex_preference and dex_name != dex_preference:
                    continue
                
                # In production: Call DEX router contract
                # Mock quote calculation
                output_amount = amount_in * Decimal("0.997")  # 0.3% fee
                
                quotes.append({
                    "dex": dex_name,
                    "router": router,
                    "amount_out": float(output_amount),
                    "price_impact": 0.5,  # Mock 0.5%
                    "fee": float(amount_in * Decimal("0.003")),
                    "gas_estimate": 150000  # Mock gas
                })
                
            except Exception as e:
                print(f"Error getting quote from {dex_name}: {e}")
        
        if not quotes:
            return {"error": "No quotes available"}
        
        # Sort by best output
        best = max(quotes, key=lambda x: x["amount_out"])
        
        return {
            "token_in": token_in,
            "token_out": token_out,
            "amount_in": float(amount_in),
            "best_quote": best,
            "all_quotes": quotes,
            "savings_vs_worst": float(best["amount_out"] - min(q["amount_out"] for q in quotes))
        }
    
    async def execute_swap(
        self,
        swap: DEXSwap,
        wallet_address: str,
        private_key: str
    ) -> Dict[str, Any]:
        """
        Execute swap on DEX
        
        1. Approve token if needed
        2. Build swap transaction
        3. Sign and send
        4. Wait for confirmation
        """
        # Get best quote
        quote = await self.get_quote(
            swap.token_in,
            swap.token_out,
            swap.amount_in
        )
        
        if "error" in quote:
            return quote
        
        best_dex = quote["best_quote"]["dex"]
        
        # In production:
        # 1. Check/approve token allowance
        # 2. Build transaction with router
        # 3. Estimate gas
        # 4. Sign transaction
        # 5. Send and wait
        
        # Mock execution
        tx_hash = "0x" + "abc123" * 8
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "dex": best_dex,
            "amount_in": float(swap.amount_in),
            "expected_out": quote["best_quote"]["amount_out"],
            "slippage": float(swap.max_slippage),
            "gas_estimate": quote["best_quote"]["gas_estimate"],
            "explorer_url": f"https://etherscan.io/tx/{tx_hash}"
        }
    
    async def get_liquidity_pools(
        self,
        token0: Optional[str] = None,
        token1: Optional[str] = None,
        min_tvl: Optional[Decimal] = None
    ) -> List[LiquidityPool]:
        """
        Get available liquidity pools
        
        Filter by tokens and minimum TVL
        """
        # In production: Query subgraph or contract
        
        mock_pools = [
            LiquidityPool(
                pool_address="0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8",
                dex_name="uniswap_v3",
                token0="USDC",
                token1="ETH",
                reserve0=Decimal("5000000"),
                reserve1=Decimal("2500"),
                total_supply=Decimal("100000"),
                apy=Decimal("0.25"),
                fee_tier=Decimal("0.0005")
            ),
            LiquidityPool(
                pool_address="0xCBCdF9626bC03E24f779434178A73a0B4bad62eD",
                dex_name="sushiswap",
                token0="WBTC",
                token1="ETH",
                reserve0=Decimal("100"),
                reserve1=Decimal("1500"),
                total_supply=Decimal("50000"),
                apy=Decimal("0.15"),
                fee_tier=Decimal("0.003")
            ),
            LiquidityPool(
                pool_address="0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
                dex_name="curve",
                token0="DAI",
                token1="USDC",
                reserve0=Decimal("10000000"),
                reserve1=Decimal("10000000"),
                total_supply=Decimal("20000000"),
                apy=Decimal("0.05"),
                fee_tier=Decimal("0.0004")
            )
        ]
        
        # Filter by TVL if specified
        if min_tvl:
            tvl = min_tvl
            mock_pools = [p for p in mock_pools if (p.reserve0 + p.reserve1) >= tvl]
        
        return mock_pools
    
    async def add_liquidity(
        self,
        pool_address: str,
        amount0: Decimal,
        amount1: Decimal,
        wallet_address: str,
        slippage: Decimal = Decimal("0.01")
    ) -> Dict[str, Any]:
        """Add liquidity to pool"""
        # In production: Call DEX router addLiquidity
        
        return {
            "success": True,
            "pool": pool_address,
            "amount0": float(amount0),
            "amount1": float(amount1),
            "lp_tokens_received": float((amount0 + amount1) / 2),  # Mock
            "tx_hash": "0x" + "def456" * 8
        }
    
    async def remove_liquidity(
        self,
        pool_address: str,
        lp_amount: Decimal,
        wallet_address: str
    ) -> Dict[str, Any]:
        """Remove liquidity from pool"""
        return {
            "success": True,
            "pool": pool_address,
            "lp_burned": float(lp_amount),
            "amount0_received": float(lp_amount / 2),
            "amount1_received": float(lp_amount / 2),
            "tx_hash": "0x" + "ghi789" * 8
        }
    
    async def get_1inch_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: Decimal
    ) -> Dict[str, Any]:
        """
        Get quote from 1inch aggregator
        
        1inch finds best route across all DEXs
        """
        # In production: Call 1inch API
        # 1inch finds optimal path through multiple hops
        
        router = self.routers.get("1inch")
        if not router:
            return {"error": "1inch not available on this chain"}
        
        # Mock 1inch quote (usually better than single DEX)
        amount_out = amount_in * Decimal("0.9985")  # Better rate
        
        return {
            "aggregator": "1inch",
            "router": router,
            "token_in": token_in,
            "token_out": token_out,
            "amount_in": float(amount_in),
            "amount_out": float(amount_out),
            "price_impact": 0.3,
            "protocols": ["uniswap_v3", "sushiswap"],  # Route through multiple
            "gas_estimate": 180000
        }
    
    async def get_yield_farming_opportunities(
        self,
        min_apy: Decimal = Decimal("0.05")
    ) -> List[Dict[str, Any]]:
        """
        Get yield farming opportunities
        
        LP positions with rewards
        """
        pools = await self.get_liquidity_pools()
        
        opportunities = []
        for pool in pools:
            if pool.apy and pool.apy >= min_apy:
                opportunities.append({
                    "pool": pool.pool_address,
                    "dex": pool.dex_name,
                    "pair": f"{pool.token0}/{pool.token1}",
                    "apy": float(pool.apy),
                    "tvl_usd": float(pool.reserve0 + pool.reserve1),
                    "risk_level": "medium",  # Assess based on pool age, volume
                    "impermanent_loss_risk": "medium"
                })
        
        return sorted(opportunities, key=lambda x: x["apy"], reverse=True)
    
    def calculate_impermanent_loss(
        self,
        price_ratio_change: Decimal
    ) -> Decimal:
        """
        Calculate impermanent loss
        
        Formula: IL = 2*sqrt(r) / (1+r) - 1
        where r = price_ratio_change
        """
        import math
        
        r = float(price_ratio_change)
        il = 2 * math.sqrt(r) / (1 + r) - 1
        
        return Decimal(str(abs(il)))


# Helper functions for DEX operations
def encode_path(tokens: List[str], fees: List[int]) -> bytes:
    """Encode swap path for Uniswap V3"""
    # V3 uses encoded path: token + fee + token + fee + token
    # In production: Proper encoding
    return b""


def calculate_optimal_slippage(
    trade_size_usd: Decimal,
    pool_liquidity_usd: Decimal
) -> Decimal:
    """
    Calculate optimal slippage based on trade size vs liquidity
    
    Higher trade relative to liquidity = higher slippage needed
    """
    ratio = trade_size_usd / pool_liquidity_usd
    
    if ratio < Decimal("0.001"):  # < 0.1% of liquidity
        return Decimal("0.001")  # 0.1%
    elif ratio < Decimal("0.01"):  # < 1% of liquidity
        return Decimal("0.005")  # 0.5%
    elif ratio < Decimal("0.05"):  # < 5% of liquidity
        return Decimal("0.01")  # 1%
    else:
        return Decimal("0.02")  # 2% for large trades
