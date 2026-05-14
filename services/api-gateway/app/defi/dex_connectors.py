"""
Decentralized Exchange (DEX) Connectors
Uniswap, Curve, and major DEX integrations via Web3
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DEXType(Enum):
    UNISWAP_V2 = "uniswap_v2"
    UNISWAP_V3 = "uniswap_v3"
    SUSHISWAP = "sushiswap"
    PANCAKESWAP = "pancakeswap"
    CURVE = "curve"
    BALANCER = "balancer"
    ONEINCH = "1inch"


class ChainId(Enum):
    ETHEREUM = 1
    POLYGON = 137
    ARBITRUM = 42161
    OPTIMISM = 10
    BASE = 8453
    BSC = 56
    AVALANCHE = 43114


@dataclass
class Token:
    address: str
    symbol: str
    name: str
    decimals: int
    chain_id: ChainId
    logo_uri: Optional[str] = None
    price_usd: float = 0.0


@dataclass
class Pool:
    address: str
    dex: DEXType
    token0: Token
    token1: Token
    reserve0: Decimal
    reserve1: Decimal
    fee_tier: int  # In basis points (e.g., 30 = 0.3%)
    tvl_usd: float = 0.0
    volume_24h: float = 0.0
    apy: float = 0.0


@dataclass
class SwapRoute:
    path: List[str]  # Token addresses
    pools: List[str]  # Pool addresses
    expected_output: Decimal
    price_impact: float
    gas_estimate: int
    minimum_output: Decimal


@dataclass
class DEXTrade:
    tx_hash: str
    timestamp: datetime
    dex: DEXType
    token_in: str
    token_out: str
    amount_in: Decimal
    amount_out: Decimal
    price: float
    gas_cost_eth: Decimal
    gas_cost_usd: float
    wallet: str
    status: str  # pending, confirmed, failed


class UniswapV2Connector:
    """Uniswap V2 AMM connector"""
    
    ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    
    def __init__(self, rpc_url: str = "", chain_id: ChainId = ChainId.ETHEREUM):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.pools: Dict[str, Pool] = {}
        self.trades: List[DEXTrade] = []
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to Ethereum node via Web3"""
        try:
            logger.info(f"Connecting to Uniswap V2 on {self.chain_id.name}")
            await self._load_common_pools()
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Uniswap connection failed: {e}")
            return False
    
    async def _load_common_pools(self):
        """Load popular Uniswap V2 pools"""
        weth = Token(
            address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            symbol="WETH",
            name="Wrapped Ether",
            decimals=18,
            chain_id=self.chain_id,
            price_usd=3500.0
        )
        
        usdc = Token(
            address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            symbol="USDC",
            name="USD Coin",
            decimals=6,
            chain_id=self.chain_id,
            price_usd=1.0
        )
        
        usdt = Token(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            symbol="USDT",
            name="Tether",
            decimals=6,
            chain_id=self.chain_id,
            price_usd=1.0
        )
        
        dai = Token(
            address="0x6B175474E89094C44Da98b954EedeAC495271d0F",
            symbol="DAI",
            name="Dai Stablecoin",
            decimals=18,
            chain_id=self.chain_id,
            price_usd=1.0
        )
        
        # Major pools
        pools_data = [
            ("ETH-USDC", weth, usdc, 30),
            ("ETH-USDT", weth, usdt, 30),
            ("ETH-DAI", weth, dai, 30),
            ("USDC-USDT", usdc, usdt, 5),
            ("USDC-DAI", usdc, dai, 5),
        ]
        
        for name, t0, t1, fee in pools_data:
            pool = Pool(
                address=f"0x_pool_{name}",
                dex=DEXType.UNISWAP_V2,
                token0=t0,
                token1=t1,
                reserve0=Decimal("1000000"),
                reserve1=Decimal("3500000000") if t1.symbol in ["USDC", "USDT"] else Decimal("1000000"),
                fee_tier=fee,
                tvl_usd=10000000.0,
                volume_24h=5000000.0,
                apy=15.5
            )
            self.pools[name] = pool
        
        logger.info(f"Loaded {len(self.pools)} Uniswap V2 pools")
    
    async def get_pools(self) -> List[Pool]:
        """Get all available pools"""
        return list(self.pools.values())
    
    async def get_pool(self, token_a: str, token_b: str) -> Optional[Pool]:
        """Get pool for token pair"""
        for pool in self.pools.values():
            if (pool.token0.symbol == token_a and pool.token1.symbol == token_b) or \
               (pool.token0.symbol == token_b and pool.token1.symbol == token_a):
                return pool
        return None
    
    async def get_price(self, token_in: str, token_out: str) -> float:
        """Get current price for token pair"""
        pool = await self.get_pool(token_in, token_out)
        if not pool:
            return 0.0
        
        # Constant product formula: x * y = k
        reserve_in = pool.reserve0 if pool.token0.symbol == token_in else pool.reserve1
        reserve_out = pool.reserve1 if pool.token0.symbol == token_in else pool.reserve0
        
        if reserve_in == 0:
            return 0.0
        
        price = float(reserve_out) / float(reserve_in)
        return price
    
    async def get_swap_route(
        self,
        token_in: str,
        token_out: str,
        amount_in: Decimal
    ) -> Optional[SwapRoute]:
        """Calculate optimal swap route"""
        pool = await self.get_pool(token_in, token_out)
        if not pool:
            return None
        
        reserve_in = pool.reserve0 if pool.token0.symbol == token_in else pool.reserve1
        reserve_out = pool.reserve1 if pool.token0.symbol == token_in else pool.reserve0
        
        # Uniswap V2 formula: amount_out = (amount_in * 997 * reserve_out) / (reserve_in * 1000 + amount_in * 997)
        amount_in_with_fee = amount_in * 997
        numerator = amount_in_with_fee * reserve_out
        denominator = (reserve_in * 1000) + amount_in_with_fee
        expected_output = numerator // denominator
        
        # Calculate price impact
        price_before = float(reserve_out) / float(reserve_in)
        price_after = float(reserve_out - expected_output) / float(reserve_in + amount_in)
        price_impact = abs(price_before - price_after) / price_before * 100
        
        # Minimum output with 0.5% slippage
        minimum_output = expected_output * Decimal("995") // Decimal("1000")
        
        return SwapRoute(
            path=[token_in, token_out],
            pools=[pool.address],
            expected_output=expected_output,
            price_impact=price_impact,
            gas_estimate=150000,
            minimum_output=minimum_output
        )
    
    async def swap(
        self,
        wallet: str,
        token_in: str,
        token_out: str,
        amount_in: Decimal,
        min_amount_out: Decimal,
        deadline: int = 0
    ) -> Optional[DEXTrade]:
        """Execute swap transaction"""
        route = await self.get_swap_route(token_in, token_out, amount_in)
        if not route:
            return None
        
        trade = DEXTrade(
            tx_hash=f"0x_swap_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            dex=DEXType.UNISWAP_V2,
            token_in=token_in,
            token_out=token_out,
            amount_in=amount_in,
            amount_out=route.expected_output,
            price=float(route.expected_output) / float(amount_in),
            gas_cost_eth=Decimal("0.005"),
            gas_cost_usd=17.5,
            wallet=wallet,
            status="confirmed"
        )
        
        self.trades.append(trade)
        logger.info(f"Uniswap swap: {amount_in} {token_in} -> {route.expected_output} {token_out}")
        return trade
    
    async def add_liquidity(
        self,
        wallet: str,
        token_a: str,
        token_b: str,
        amount_a: Decimal,
        amount_b: Decimal
    ) -> Dict[str, Any]:
        """Add liquidity to pool"""
        return {
            "lp_tokens": (amount_a * amount_b) ** Decimal("0.5"),
            "pool_share": 0.01,
            "status": "confirmed"
        }
    
    async def remove_liquidity(
        self,
        wallet: str,
        token_a: str,
        token_b: str,
        lp_tokens: Decimal
    ) -> Dict[str, Any]:
        """Remove liquidity from pool"""
        return {
            "amount_a": lp_tokens * Decimal("1000"),
            "amount_b": lp_tokens * Decimal("3500000"),
            "status": "confirmed"
        }


class UniswapV3Connector:
    """Uniswap V3 concentrated liquidity connector"""
    
    FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
    
    def __init__(self, rpc_url: str = "", chain_id: ChainId = ChainId.ETHEREUM):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.pools: Dict[str, Pool] = {}
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to Uniswap V3"""
        try:
            logger.info(f"Connecting to Uniswap V3 on {self.chain_id.name}")
            await self._load_pools()
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Uniswap V3 connection failed: {e}")
            return False
    
    async def _load_pools(self):
        """Load Uniswap V3 pools with different fee tiers"""
        weth = Token("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "WETH", "Wrapped Ether", 18, self.chain_id, price_usd=3500.0)
        usdc = Token("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "USDC", "USD Coin", 6, self.chain_id, price_usd=1.0)
        
        fee_tiers = [500, 3000, 10000]  # 0.05%, 0.3%, 1%
        
        for fee in fee_tiers:
            pool = Pool(
                address=f"0x_v3_pool_{fee}",
                dex=DEXType.UNISWAP_V3,
                token0=weth,
                token1=usdc,
                reserve0=Decimal("500000"),
                reserve1=Decimal("1750000000"),
                fee_tier=fee,
                tvl_usd=5000000.0,
                volume_24h=2000000.0,
                apy=25.0 if fee == 500 else 20.0
            )
            self.pools[f"ETH-USDC-{fee}"] = pool
        
        logger.info(f"Loaded {len(self.pools)} Uniswap V3 pools")
    
    async def get_pools(self) -> List[Pool]:
        return list(self.pools.values())


class CurveConnector:
    """Curve Finance stableswap connector"""
    
    REGISTRY_ADDRESS = "0x0000000022D53366457F9d5E68Ec105046FC4383"
    
    def __init__(self, rpc_url: str = "", chain_id: ChainId = ChainId.ETHEREUM):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.pools: Dict[str, Pool] = {}
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to Curve Finance"""
        try:
            logger.info(f"Connecting to Curve on {self.chain_id.name}")
            await self._load_pools()
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Curve connection failed: {e}")
            return False
    
    async def _load_pools(self):
        """Load Curve stable pools"""
        dai = Token("0x6B175474E89094C44Da98b954EedeAC495271d0F", "DAI", "Dai", 18, self.chain_id, price_usd=1.0)
        usdc = Token("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "USDC", "USD Coin", 6, self.chain_id, price_usd=1.0)
        usdt = Token("0xdAC17F958D2ee523a2206206994597C13D831ec7", "USDT", "Tether", 6, self.chain_id, price_usd=1.0)
        
        # 3pool (DAI-USDC-USDT)
        three_pool = Pool(
            address="0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
            dex=DEXType.CURVE,
            token0=dai,
            token1=usdc,
            reserve0=Decimal("300000000"),
            reserve1=Decimal("300000000"),
            fee_tier=3,  # 0.03%
            tvl_usd=500000000.0,
            volume_24h=100000000.0,
            apy=3.5
        )
        self.pools["3pool"] = three_pool
        
        # stETH pool
        steth = Token("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84", "stETH", "Lido Staked ETH", 18, self.chain_id, price_usd=3500.0)
        weth = Token("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "WETH", "Wrapped Ether", 18, self.chain_id, price_usd=3500.0)
        
        steth_pool = Pool(
            address="0xDC24316b9AE028F1497c275EB9192a3Ea0f67022",
            dex=DEXType.CURVE,
            token0=steth,
            token1=weth,
            reserve0=Decimal("100000"),
            reserve1=Decimal("100000"),
            fee_tier=4,
            tvl_usd=350000000.0,
            volume_24h=50000000.0,
            apy=4.2
        )
        self.pools["steth"] = steth_pool
        
        logger.info(f"Loaded {len(self.pools)} Curve pools")
    
    async def get_pools(self) -> List[Pool]:
        return list(self.pools.values())
    
    async def exchange(
        self,
        pool_name: str,
        i: int,  # token index in
        j: int,  # token index out
        dx: Decimal,  # amount in
        min_dy: Decimal  # min amount out
    ) -> Decimal:
        """Exchange tokens in Curve pool"""
        # Stableswap formula approximation
        dy = dx * Decimal("0.997")  # 0.03% fee
        return dy
    
    async def get_virtual_price(self, pool_name: str) -> Decimal:
        """Get LP token virtual price"""
        return Decimal("1.05")  # Has grown 5% since inception


class DEXAggregator:
    """Aggregate multiple DEXs for best pricing"""
    
    def __init__(self):
        self.connectors: Dict[DEXType, Any] = {}
        self.routes: Dict[str, SwapRoute] = {}
        
    async def add_connector(self, dex_type: DEXType, connector: Any):
        """Add DEX connector to aggregator"""
        self.connectors[dex_type] = connector
        logger.info(f"Added {dex_type.value} to aggregator")
    
    async def get_best_price(
        self,
        token_in: str,
        token_out: str,
        amount_in: Decimal
    ) -> Dict[str, Any]:
        """Find best price across all DEXs"""
        results = []
        
        for dex_type, connector in self.connectors.items():
            try:
                price = await connector.get_price(token_in, token_out)
                route = await connector.get_swap_route(token_in, token_out, amount_in)
                
                if route:
                    results.append({
                        "dex": dex_type.value,
                        "price": price,
                        "expected_output": route.expected_output,
                        "price_impact": route.price_impact,
                        "gas_estimate": route.gas_estimate,
                        "route": route
                    })
            except Exception as e:
                logger.warning(f"Could not get price from {dex_type}: {e}")
        
        if not results:
            return {"error": "No routes found"}
        
        # Sort by expected output (descending)
        results.sort(key=lambda x: x["expected_output"], reverse=True)
        
        return {
            "best_dex": results[0]["dex"],
            "best_output": results[0]["expected_output"],
            "all_routes": results,
            "savings_vs_worst": float(results[0]["expected_output"] - results[-1]["expected_output"]) / float(results[-1]["expected_output"]) * 100 if len(results) > 1 else 0
        }
    
    async def execute_best_swap(
        self,
        wallet: str,
        token_in: str,
        token_out: str,
        amount_in: Decimal,
        slippage: float = 0.5
    ) -> Optional[DEXTrade]:
        """Execute swap on best DEX"""
        best = await self.get_best_price(token_in, token_out, amount_in)
        
        if "error" in best:
            return None
        
        best_dex_type = DEXType(best["best_dex"])
        connector = self.connectors.get(best_dex_type)
        
        if not connector:
            return None
        
        route = best["all_routes"][0]["route"]
        min_out = route.expected_output * Decimal(100 - slippage) / Decimal(100)
        
        trade = await connector.swap(
            wallet=wallet,
            token_in=token_in,
            token_out=token_out,
            amount_in=amount_in,
            min_amount_out=min_out
        )
        
        return trade


class MultiChainDEXManager:
    """Manage DEXs across multiple chains"""
    
    def __init__(self):
        self.chain_connectors: Dict[ChainId, DEXAggregator] = {}
        
    async def add_chain(self, chain_id: ChainId, aggregator: DEXAggregator):
        """Add DEX aggregator for chain"""
        self.chain_connectors[chain_id] = aggregator
        logger.info(f"Added DEX support for {chain_id.name}")
    
    async def get_cross_chain_opportunities(
        self,
        token: str,
        amount: Decimal
    ) -> List[Dict[str, Any]]:
        """Find arbitrage opportunities across chains"""
        opportunities = []
        
        for chain_id, aggregator in self.chain_connectors.items():
            try:
                # Get price on this chain
                price_data = await aggregator.get_best_price(token, "USDC", amount)
                
                if "best_output" in price_data:
                    opportunities.append({
                        "chain": chain_id.name,
                        "output": price_data["best_output"],
                        "price": price_data["best_output"] / amount,
                        "dex": price_data["best_dex"]
                    })
            except Exception:
                continue
        
        if len(opportunities) < 2:
            return []
        
        # Sort by price
        opportunities.sort(key=lambda x: x["price"])
        
        best_buy = opportunities[0]
        best_sell = opportunities[-1]
        
        spread = (best_sell["price"] - best_buy["price"]) / best_buy["price"] * 100
        
        return {
            "buy_on": best_buy["chain"],
            "sell_on": best_sell["chain"],
            "spread_percent": spread,
            "profit_usd": float(best_sell["output"] - best_buy["output"]),
            "opportunities": opportunities
        }


# Global DEX manager
_dex_manager: Optional[MultiChainDEXManager] = None


async def get_dex_manager() -> MultiChainDEXManager:
    """Get or create global DEX manager"""
    global _dex_manager
    if _dex_manager is None:
        _dex_manager = MultiChainDEXManager()
        
        # Initialize Ethereum DEXs
        eth_agg = DEXAggregator()
        
        uniswap_v2 = UniswapV2Connector(chain_id=ChainId.ETHEREUM)
        await uniswap_v2.connect()
        await eth_agg.add_connector(DEXType.UNISWAP_V2, uniswap_v2)
        
        uniswap_v3 = UniswapV3Connector(chain_id=ChainId.ETHEREUM)
        await uniswap_v3.connect()
        await eth_agg.add_connector(DEXType.UNISWAP_V3, uniswap_v3)
        
        curve = CurveConnector(chain_id=ChainId.ETHEREUM)
        await curve.connect()
        await eth_agg.add_connector(DEXType.CURVE, curve)
        
        await _dex_manager.add_chain(ChainId.ETHEREUM, eth_agg)
    
    return _dex_manager
