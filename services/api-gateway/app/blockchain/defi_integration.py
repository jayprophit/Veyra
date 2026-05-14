"""
DeFi Integration Module
======================
Comprehensive DeFi protocol integration for Veyra
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import aiohttp
import hashlib

logger = logging.getLogger(__name__)


class DeFiProtocol(Enum):
    """Supported DeFi protocols"""
    AAVE = "aave"
    COMPOUND = "compound"
    UNISWAP = "uniswap"
    SUSHISWAP = "sushiswap"
    CURVE = "curve"
    BALANCER = "balancer"
    YEARN = "yearn"
    MAKERDAO = "makerdao"
    SYNTHETIX = "synthetix"
    ONEINCH = "1inch"


class PoolType(Enum):
    """Types of DeFi pools"""
    LENDING = "lending"
    LIQUIDITY = "liquidity"
    YIELD_FARMING = "yield_farming"
    STAKING = "staking"
    BRIDGE = "bridge"


@dataclass
class DeFiPosition:
    """DeFi position information"""
    protocol: DeFiProtocol
    pool_address: str
    token_address: str
    token_symbol: str
    amount: Decimal
    value_usd: Decimal
    apy: float
    rewards: List[Dict[str, Any]]
    created_at: datetime
    last_updated: datetime


@dataclass
class LiquidityPool:
    """Liquidity pool information"""
    protocol: DeFiProtocol
    address: str
    token0_address: str
    token1_address: str
    token0_symbol: str
    token1_symbol: str
    reserve0: Decimal
    reserve1: Decimal
    total_supply: Decimal
    apr: float
    volume_24h: Decimal
    fee: float


@dataclass
class LendingPool:
    """Lending pool information"""
    protocol: DeFiProtocol
    asset_address: str
    asset_symbol: str
    total_liquidity: Decimal
    total_borrows: Decimal
    supply_apy: float
    borrow_apy: float
    utilization_rate: float
    collateral_factor: float


class DeFiIntegration:
    """Comprehensive DeFi integration for Veyra"""
    
    def __init__(self):
        self.protocol_configs = {
            DeFiProtocol.AAVE: {
                "base_url": "https://api.aave.com/v2",
                "graph_url": "https://api.thegraph.com/subgraphs/name/aave/protocol-v2",
                "pools": ["USDC", "USDT", "DAI", "WBTC", "WETH"]
            },
            DeFiProtocol.COMPOUND: {
                "base_url": "https://api.compound.finance/api/v2",
                "graph_url": "https://api.thegraph.com/subgraphs/name/compound-finance/compound-v2",
                "pools": ["USDC", "USDT", "DAI", "WBTC", "ETH"]
            },
            DeFiProtocol.UNISWAP: {
                "base_url": "https://api.uniswap.org/v1",
                "graph_url": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2",
                "pools": ["USDC-ETH", "DAI-ETH", "WBTC-ETH"]
            }
        }
        
        self.user_positions: Dict[str, List[DeFiPosition]] = {}
        self.liquidity_pools: Dict[str, LiquidityPool] = {}
        self.lending_pools: Dict[str, LendingPool] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize DeFi integration"""
        self.session = aiohttp.ClientSession()
        await self._load_popular_pools()
        logger.info("DeFi integration initialized")
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    async def _load_popular_pools(self):
        """Load popular DeFi pools"""
        # Mock data for popular pools
        popular_liquidity_pools = [
            {
                "protocol": DeFiProtocol.UNISWAP,
                "address": "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",
                "token0_address": "0xa0b86a33e6441b8e8c7c7b0b0b0b0b0b0b0b0b0b",
                "token1_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                "token0_symbol": "USDC",
                "token1_symbol": "WETH",
                "reserve0": Decimal("1000000"),
                "reserve1": Decimal("500"),
                "total_supply": Decimal("1000000"),
                "apr": 0.05,
                "volume_24h": Decimal("100000"),
                "fee": 0.003
            },
            {
                "protocol": DeFiProtocol.SUSHISWAP,
                "address": "0x397ff1542f962076d0bfe58ea045ffa2d347aca0",
                "token0_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
                "token1_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                "token0_symbol": "USDT",
                "token1_symbol": "WETH",
                "reserve0": Decimal("500000"),
                "reserve1": Decimal("250"),
                "total_supply": Decimal("500000"),
                "apr": 0.08,
                "volume_24h": Decimal("80000"),
                "fee": 0.003
            }
        ]
        
        for pool_data in popular_liquidity_pools:
            pool = LiquidityPool(**pool_data)
            self.liquidity_pools[pool.address] = pool
            
        # Mock lending pools
        popular_lending_pools = [
            {
                "protocol": DeFiProtocol.AAVE,
                "asset_address": "0xa0b86a33e6441b8e8c7c7b0b0b0b0b0b0b0b0b0b",
                "asset_symbol": "USDC",
                "total_liquidity": Decimal("100000000"),
                "total_borrows": Decimal("50000000"),
                "supply_apy": 0.04,
                "borrow_apy": 0.06,
                "utilization_rate": 0.5,
                "collateral_factor": 0.8
            },
            {
                "protocol": DeFiProtocol.COMPOUND,
                "asset_address": "0x6b175474e89094c44da98b954eedeac495271d0f",
                "asset_symbol": "DAI",
                "total_liquidity": Decimal("50000000"),
                "total_borrows": Decimal("30000000"),
                "supply_apy": 0.03,
                "borrow_apy": 0.05,
                "utilization_rate": 0.6,
                "collateral_factor": 0.75
            }
        ]
        
        for pool_data in popular_lending_pools:
            pool = LendingPool(**pool_data)
            self.lending_pools[pool.asset_address] = pool
            
    async def get_user_positions(self, address: str) -> List[DeFiPosition]:
        """Get user's DeFi positions"""
        if address.lower() not in self.user_positions:
            # Mock user positions
            mock_positions = [
                DeFiPosition(
                    protocol=DeFiProtocol.AAVE,
                    pool_address="0x8dff5e27ea6b7ac08ebfdf9eb090f32ee91430c6",
                    token_address="0xa0b86a33e6441b8e8c7c7b0b0b0b0b0b0b0b0b0b",
                    token_symbol="USDC",
                    amount=Decimal("1000"),
                    value_usd=Decimal("1000"),
                    apy=0.04,
                    rewards=[{"token": "AAVE", "amount": "10"}],
                    created_at=datetime.now() - timedelta(days=30),
                    last_updated=datetime.now()
                ),
                DeFiPosition(
                    protocol=DeFiProtocol.UNISWAP,
                    pool_address="0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",
                    token_address="0xa0b86a33e6441b8e8c7c7b0b0b0b0b0b0b0b0b0b",
                    token_symbol="USDC",
                    amount=Decimal("500"),
                    value_usd=Decimal("500"),
                    apy=0.05,
                    rewards=[{"token": "UNI", "amount": "5"}],
                    created_at=datetime.now() - timedelta(days=15),
                    last_updated=datetime.now()
                )
            ]
            self.user_positions[address.lower()] = mock_positions
            
        return self.user_positions[address.lower()]
        
    async def get_liquidity_pools(self, protocol: Optional[DeFiProtocol] = None) -> List[LiquidityPool]:
        """Get liquidity pools"""
        pools = list(self.liquidity_pools.values())
        
        if protocol:
            pools = [pool for pool in pools if pool.protocol == protocol]
            
        return pools
        
    async def get_lending_pools(self, protocol: Optional[DeFiProtocol] = None) -> List[LendingPool]:
        """Get lending pools"""
        pools = list(self.lending_pools.values())
        
        if protocol:
            pools = [pool for pool in pools if pool.protocol == protocol]
            
        return pools
        
    async def add_liquidity(self, address: str, pool_address: str,
                           token0_amount: Decimal, token1_amount: Decimal) -> str:
        """Add liquidity to a pool"""
        try:
            pool = self.liquidity_pools.get(pool_address)
            if not pool:
                raise ValueError("Pool not found")
                
            # Mock liquidity addition
            lp_tokens = min(token0_amount, token1_amount)
            
            # Update user position or create new one
            user_positions = await self.get_user_positions(address)
            
            position = DeFiPosition(
                protocol=pool.protocol,
                pool_address=pool_address,
                token_address=pool.token0_address,
                token_symbol=pool.token0_symbol,
                amount=lp_tokens,
                value_usd=lp_tokens * 2,  # Simplified valuation
                apy=pool.apr,
                rewards=[],
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            user_positions.append(position)
            self.user_positions[address.lower()] = user_positions
            
            # Generate mock transaction hash
            tx_hash = hashlib.sha256(f"{address}{pool_address}{lp_tokens}{datetime.now()}".encode()).hexdigest()
            
            logger.info(f"Added liquidity to pool {pool_address}: {lp_tokens}")
            return f"0x{tx_hash}"
            
        except Exception as e:
            logger.error(f"Failed to add liquidity: {e}")
            raise
            
    async def supply_to_lending_pool(self, address: str, pool_address: str,
                                   amount: Decimal) -> str:
        """Supply assets to lending pool"""
        try:
            pool = self.lending_pools.get(pool_address)
            if not pool:
                raise ValueError("Lending pool not found")
                
            # Mock supply
            # Update user position or create new one
            user_positions = await self.get_user_positions(address)
            
            position = DeFiPosition(
                protocol=pool.protocol,
                pool_address=pool_address,
                token_address=pool.asset_address,
                token_symbol=pool.asset_symbol,
                amount=amount,
                value_usd=amount,
                apy=pool.supply_apy,
                rewards=[{"token": "aToken", "amount": str(amount)}],
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            user_positions.append(position)
            self.user_positions[address.lower()] = user_positions
            
            # Generate mock transaction hash
            tx_hash = hashlib.sha256(f"{address}{pool_address}{amount}{datetime.now()}".encode()).hexdigest()
            
            logger.info(f"Supplied {amount} to lending pool {pool_address}")
            return f"0x{tx_hash}"
            
        except Exception as e:
            logger.error(f"Failed to supply to lending pool: {e}")
            raise
            
    async def get_yield_farming_opportunities(self) -> List[Dict[str, Any]]:
        """Get yield farming opportunities"""
        opportunities = []
        
        for pool in self.liquidity_pools.values():
            if pool.apr > 0.05:  # Only show high APY pools
                opportunities.append({
                    "protocol": pool.protocol.value,
                    "pool_address": pool.address,
                    "token_pair": f"{pool.token0_symbol}/{pool.token1_symbol}",
                    "apr": pool.apr,
                    "tvl": pool.reserve0 + pool.reserve1,
                    "volume_24h": pool.volume_24h,
                    "type": "liquidity"
                })
                
        for pool in self.lending_pools.values():
            if pool.supply_apy > 0.03:  # Only show high APY pools
                opportunities.append({
                    "protocol": pool.protocol.value,
                    "pool_address": pool.asset_address,
                    "token": pool.asset_symbol,
                    "apr": pool.supply_apy,
                    "tvl": pool.total_liquidity,
                    "utilization": pool.utilization_rate,
                    "type": "lending"
                })
                
        # Sort by APY descending
        opportunities.sort(key=lambda x: x["apr"], reverse=True)
        
        return opportunities
        
    async def calculate_impermanent_loss(self, pool_address: str,
                                      initial_amount0: Decimal, initial_amount1: Decimal,
                                      current_amount0: Decimal, current_amount1: Decimal) -> Decimal:
        """Calculate impermanent loss"""
        try:
            pool = self.liquidity_pools.get(pool_address)
            if not pool:
                return Decimal("0")
                
            # Calculate initial value
            initial_price = initial_amount1 / initial_amount0 if initial_amount0 > 0 else Decimal("0")
            initial_value = initial_amount0 + (initial_amount0 * initial_price)
            
            # Calculate current value
            current_price = current_amount1 / current_amount0 if current_amount0 > 0 else Decimal("0")
            current_value = current_amount0 + (current_amount0 * current_price)
            
            # Calculate impermanent loss
            if current_price > 0:
                hodl_value = initial_amount0 + (initial_amount1 * (current_price / initial_price))
                impermanent_loss = (current_value - hodl_value) / hodl_value
                return impermanent_loss * 100  # Return as percentage
                
            return Decimal("0")
            
        except Exception as e:
            logger.error(f"Failed to calculate impermanent loss: {e}")
            return Decimal("0")
            
    async def get_defi_summary(self, address: str) -> Dict[str, Any]:
        """Get comprehensive DeFi summary for user"""
        positions = await self.get_user_positions(address)
        
        total_value = sum(pos.value_usd for pos in positions)
        total_apy = sum(pos.apy * pos.value_usd for pos in positions) / total_value if total_value > 0 else 0
        
        protocol_breakdown = {}
        for pos in positions:
            protocol = pos.protocol.value
            if protocol not in protocol_breakdown:
                protocol_breakdown[protocol] = {"value": 0, "apy": 0, "count": 0}
            protocol_breakdown[protocol]["value"] += pos.value_usd
            protocol_breakdown[protocol]["count"] += 1
            
        return {
            "total_value_usd": total_value,
            "weighted_apy": total_apy,
            "position_count": len(positions),
            "protocol_breakdown": protocol_breakdown,
            "positions": [asdict(pos) for pos in positions]
        }


# Global DeFi integration instance
_defi_integration = None

def get_defi_integration() -> DeFiIntegration:
    """Get the global DeFi integration instance"""
    global _defi_integration
    if _defi_integration is None:
        _defi_integration = DeFiIntegration()
    return _defi_integration
