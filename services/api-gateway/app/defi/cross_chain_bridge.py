"""
Cross-Chain Bridge Aggregator
Across, Stargate, Hop, Synapse, LI.FI, Wormhole integration
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BridgeType(Enum):
    ACROSS = "across"
    STARGATE = "stargate"
    HOP = "hop"
    SYNAPSE = "synapse"
    WORMHOLE = "wormhole"
    CELER = "celer"
    CONNEXT = "connext"
    LIFI = "lifi"  # Aggregator
    SOCKET = "socket"  # Aggregator
    LAYERZERO = "layerzero"


class BridgeRouteStatus(Enum):
    PENDING = "pending"
    IN_FLIGHT = "in_flight"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BridgeRoute:
    bridge: BridgeType
    source_chain: str
    dest_chain: str
    token: str
    amount: Decimal
    fee_amount: Decimal
    fee_percent: float
    gas_cost_eth: Decimal
    gas_cost_usd: float
    estimated_time_seconds: int
    min_amount: Decimal
    max_amount: Decimal
    route_id: str
    supported: bool


@dataclass
class BridgeTransaction:
    tx_hash: str
    bridge: BridgeType
    source_chain: str
    dest_chain: str
    token: str
    amount: Decimal
    fee_paid: Decimal
    gas_cost_eth: Decimal
    status: BridgeRouteStatus
    timestamp: datetime
    estimated_completion: datetime
    actual_completion: Optional[datetime]
    sender: str
    recipient: str
    ref_id: str  # Cross-reference between chains


class AcrossBridge:
    """Across Protocol - Fast L2 to L2 transfers via intents"""
    
    def __init__(self):
        self.name = "Across"
        self.supported_chains = [
            "ethereum", "arbitrum", "optimism", "base", 
            "polygon", "zkSync", "linea"
        ]
        self.fee_model = "lp_fees_plus_relayer"
        
    async def get_quote(
        self,
        source: str,
        dest: str,
        token: str,
        amount: Decimal
    ) -> Optional[BridgeRoute]:
        """Get Across bridge quote"""
        if source not in self.supported_chains or dest not in self.supported_chains:
            return None
        
        # Across fees: 0.04% - 0.12% depending on route
        fee_percent = 0.08
        fee_amount = amount * Decimal(str(fee_percent / 100))
        
        # Gas cost varies by destination
        gas_map = {
            "arbitrum": Decimal("0.0001"),
            "optimism": Decimal("0.00008"),
            "base": Decimal("0.00008"),
            "ethereum": Decimal("0.001")
        }
        
        return BridgeRoute(
            bridge=BridgeType.ACROSS,
            source_chain=source,
            dest_chain=dest,
            token=token,
            amount=amount,
            fee_amount=fee_amount,
            fee_percent=fee_percent,
            gas_cost_eth=gas_map.get(dest, Decimal("0.0001")),
            gas_cost_usd=0.3,
            estimated_time_seconds=20,  # Very fast
            min_amount=Decimal("0.001"),
            max_amount=Decimal("100000"),
            route_id=f"across_{source}_{dest}_{datetime.now().timestamp()}",
            supported=True
        )
    
    async def initiate_transfer(
        self,
        wallet: str,
        route: BridgeRoute
    ) -> BridgeTransaction:
        """Initiate Across bridge transfer"""
        tx = BridgeTransaction(
            tx_hash=f"0x_across_{datetime.now().timestamp()}",
            bridge=BridgeType.ACROSS,
            source_chain=route.source_chain,
            dest_chain=route.dest_chain,
            token=route.token,
            amount=route.amount,
            fee_paid=route.fee_amount,
            gas_cost_eth=route.gas_cost_eth,
            status=BridgeRouteStatus.IN_FLIGHT,
            timestamp=datetime.now(),
            estimated_completion=datetime.now(),  # ~20 seconds
            actual_completion=None,
            sender=wallet,
            recipient=wallet,
            ref_id=f"across_ref_{datetime.now().timestamp()}"
        )
        logger.info(f"Across transfer: {route.amount} {route.token} {route.source_chain} -> {route.dest_chain}")
        return tx


class StargateBridge:
    """Stargate - Omnichain liquidity transport via LayerZero"""
    
    def __init__(self):
        self.name = "Stargate"
        self.supported_chains = [
            "ethereum", "arbitrum", "optimism", "base",
            "bsc", "avalanche", "polygon", "metis"
        ]
        self.stg_token = "0x..."  # Stargate token for incentives
        
    async def get_quote(
        self,
        source: str,
        dest: str,
        token: str,
        amount: Decimal
    ) -> Optional[BridgeRoute]:
        """Get Stargate bridge quote"""
        # Stargate fees: 0.06% for stablecoins
        fee_percent = 0.06
        fee_amount = amount * Decimal(str(fee_percent / 100))
        
        # LayerZero messaging fee
        lz_fee = Decimal("0.0002")  # ETH
        
        return BridgeRoute(
            bridge=BridgeType.STARGATE,
            source_chain=source,
            dest_chain=dest,
            token=token,
            amount=amount,
            fee_amount=fee_amount,
            fee_percent=fee_percent,
            gas_cost_eth=lz_fee,
            gas_cost_usd=0.7,
            estimated_time_seconds=45,
            min_amount=Decimal("0.01"),
            max_amount=Decimal("1000000"),
            route_id=f"stargate_{source}_{dest}_{datetime.now().timestamp()}",
            supported=True
        )
    
    async def get_pool_liquidity(self, chain: str, token: str) -> Decimal:
        """Check Stargate pool liquidity on destination"""
        return Decimal("5000000")  # $5M default


class HopBridge:
    """Hop Protocol - Fast bridge with hTokens"""
    
    def __init__(self):
        self.name = "Hop"
        self.supported_chains = [
            "ethereum", "arbitrum", "optimism", "base", "polygon", "gnosis"
        ]
        self.htokens = ["hETH", "hUSDC", "hUSDT", "hDAI"]
        
    async def get_quote(
        self,
        source: str,
        dest: str,
        token: str,
        amount: Decimal
    ) -> Optional[BridgeRoute]:
        """Get Hop bridge quote"""
        # Hop fees: 0.04% - 0.3% depending on bonders
        fee_percent = 0.04
        
        # Special routes (L2 to L2 are cheapest)
        if source != "ethereum" and dest != "ethereum":
            fee_percent = 0.04  # L2-L2
        elif source == "ethereum":
            fee_percent = 0.1   # L1-L2
        else:
            fee_percent = 0.3   # L2-L1 (need to wait for challenge period)
        
        fee_amount = amount * Decimal(str(fee_percent / 100))
        
        gas_cost = Decimal("0.00015") if dest != "ethereum" else Decimal("0.001")
        
        return BridgeRoute(
            bridge=BridgeType.HOP,
            source_chain=source,
            dest_chain=dest,
            token=token,
            amount=amount,
            fee_amount=fee_amount,
            fee_percent=fee_percent,
            gas_cost_eth=gas_cost,
            gas_cost_usd=0.5,
            estimated_time_seconds=60,
            min_amount=Decimal("0.001"),
            max_amount=Decimal("500000"),
            route_id=f"hop_{source}_{dest}_{datetime.now().timestamp()}",
            supported=True
        )
    
    async def check_bonder_liquidity(self, dest_chain: str, token: str) -> Decimal:
        """Check bonder liquidity for fast transfer"""
        return Decimal("2000000")  # $2M available


class SynapseBridge:
    """Synapse - Cross-chain AMM and bridge"""
    
    def __init__(self):
        self.name = "Synapse"
        self.supported_chains = [
            "ethereum", "arbitrum", "optimism", "base",
            "bsc", "avalanche", "polygon", "fantom", "harmony"
        ]
        
    async def get_quote(
        self,
        source: str,
        dest: str,
        token: str,
        amount: Decimal
    ) -> Optional[BridgeRoute]:
        """Get Synapse bridge quote"""
        fee_percent = 0.1
        fee_amount = amount * Decimal(str(fee_percent / 100))
        
        return BridgeRoute(
            bridge=BridgeType.SYNAPSE,
            source_chain=source,
            dest_chain=dest,
            token=token,
            amount=amount,
            fee_amount=fee_amount,
            fee_percent=fee_percent,
            gas_cost_eth=Decimal("0.0003"),
            gas_cost_usd=1.0,
            estimated_time_seconds=120,
            min_amount=Decimal("0.01"),
            max_amount=Decimal("1000000"),
            route_id=f"synapse_{source}_{dest}_{datetime.now().timestamp()}",
            supported=True
        )


class LiFiAggregator:
    """LI.FI - Bridge and DEX aggregator"""
    
    def __init__(self):
        self.name = "LI.FI"
        self.sub_bridges = ["across", "stargate", "hop", "synapse", "cbridge", "amarok"]
        
    async def get_best_route(
        self,
        source: str,
        dest: str,
        token: str,
        amount: Decimal,
        prioritize_speed: bool = False,
        prioritize_cost: bool = True
    ) -> List[BridgeRoute]:
        """Get best routes aggregated from all bridges"""
        
        # Get quotes from all supported bridges
        bridges = [
            AcrossBridge(),
            StargateBridge(),
            HopBridge(),
            SynapseBridge()
        ]
        
        all_routes = []
        for bridge in bridges:
            try:
                route = await bridge.get_quote(source, dest, token, amount)
                if route:
                    all_routes.append(route)
            except Exception as e:
                logger.warning(f"Could not get quote from {bridge.name}: {e}")
        
        if not all_routes:
            return []
        
        # Sort by criteria
        if prioritize_cost:
            all_routes.sort(key=lambda r: r.fee_amount + r.gas_cost_eth)
        elif prioritize_speed:
            all_routes.sort(key=lambda r: r.estimated_time_seconds)
        
        return all_routes
    
    async def execute_best_route(
        self,
        wallet: str,
        source: str,
        dest: str,
        token: str,
        amount: Decimal
    ) -> Optional[BridgeTransaction]:
        """Find and execute best bridge route"""
        routes = await self.get_best_route(source, dest, token, amount)
        
        if not routes:
            return None
        
        best = routes[0]
        
        # Execute via the winning bridge
        bridge_map = {
            BridgeType.ACROSS: AcrossBridge(),
            BridgeType.STARGATE: StargateBridge(),
            BridgeType.HOP: HopBridge(),
            BridgeType.SYNAPSE: SynapseBridge()
        }
        
        executor = bridge_map.get(best.bridge)
        if not executor:
            return None
        
        tx = await executor.initiate_transfer(wallet, best)
        
        return tx


class CrossChainBridgeManager:
    """Manage all cross-chain bridge integrations"""
    
    def __init__(self):
        self.bridges: Dict[BridgeType, Any] = {}
        self.aggregator = LiFiAggregator()
        self.pending_transactions: Dict[str, BridgeTransaction] = {}
        
    async def add_bridge(self, bridge_type: BridgeType, connector: Any):
        """Add bridge connector"""
        self.bridges[bridge_type] = connector
        logger.info(f"Added bridge: {bridge_type.value}")
    
    async def get_all_quotes(
        self,
        source: str,
        dest: str,
        token: str,
        amount: Decimal
    ) -> List[BridgeRoute]:
        """Get quotes from all available bridges"""
        return await self.aggregator.get_best_route(source, dest, token, amount)
    
    async def compare_bridges(
        self,
        source: str,
        dest: str,
        token: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Detailed comparison of all bridge options"""
        routes = await self.get_all_quotes(source, dest, token, amount)
        
        if not routes:
            return {"error": "No routes available"}
        
        comparison = {
            "source": source,
            "destination": dest,
            "token": token,
            "amount": float(amount),
            "best_overall": {
                "bridge": routes[0].bridge.value,
                "total_cost_usd": float(routes[0].fee_amount * 3500 + routes[0].gas_cost_eth * 3500),
                "time_seconds": routes[0].estimated_time_seconds
            },
            "fastest": min(routes, key=lambda r: r.estimated_time_seconds).bridge.value,
            "cheapest": routes[0].bridge.value,
            "all_options": []
        }
        
        for route in routes:
            total_cost_usd = float(route.fee_amount * 3500 + route.gas_cost_eth * 3500)
            comparison["all_options"].append({
                "bridge": route.bridge.value,
                "fee_percent": route.fee_percent,
                "fee_usd": float(route.fee_amount * 3500),
                "gas_usd": route.gas_cost_usd,
                "total_cost_usd": total_cost_usd,
                "time_seconds": route.estimated_time_seconds,
                "max_amount": float(route.max_amount)
            })
        
        return comparison
    
    async def find_arbitrage_opportunity(
        self,
        token: str,
        amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """Find price differences across chains for arbitrage"""
        chains = ["ethereum", "arbitrum", "optimism", "base", "polygon"]
        
        prices = {}
        for source in chains:
            for dest in chains:
                if source == dest:
                    continue
                
                # This would query actual DEX prices on each chain
                price_on_source = 3500.0  # Mock ETH price
                price_on_dest = 3502.0
                
                if price_on_dest > price_on_source:
                    # Potential arbitrage
                    profit_before_fees = (price_on_dest - price_on_source) * float(amount)
                    
                    # Get bridge cost
                    routes = await self.get_all_quotes(source, dest, token, amount)
                    if routes:
                        bridge_cost = float(routes[0].fee_amount + routes[0].gas_cost_eth * 3500)
                        
                        if profit_before_fees > bridge_cost:
                            return {
                                "buy_on": source,
                                "sell_on": dest,
                                "price_diff_usd": price_on_dest - price_on_source,
                                "profit_potential_usd": profit_before_fees - bridge_cost,
                                "bridge_cost_usd": bridge_cost,
                                "best_bridge": routes[0].bridge.value
                            }
        
        return None
    
    async def execute_transfer(
        self,
        wallet: str,
        source: str,
        dest: str,
        token: str,
        amount: Decimal,
        preferred_bridge: Optional[BridgeType] = None
    ) -> Optional[BridgeTransaction]:
        """Execute cross-chain transfer"""
        
        if preferred_bridge:
            bridge = self.bridges.get(preferred_bridge)
            if bridge:
                route = await bridge.get_quote(source, dest, token, amount)
                if route:
                    tx = await bridge.initiate_transfer(wallet, route)
                    self.pending_transactions[tx.tx_hash] = tx
                    return tx
        
        # Use best route
        return await self.aggregator.execute_best_route(wallet, source, dest, token, amount)
    
    async def track_transaction(self, tx_hash: str) -> Optional[BridgeTransaction]:
        """Track pending bridge transaction"""
        tx = self.pending_transactions.get(tx_hash)
        if not tx:
            return None
        
        # In production, would poll API for status
        return tx
    
    async def get_transaction_history(
        self,
        wallet: str,
        bridge: Optional[BridgeType] = None
    ) -> List[BridgeTransaction]:
        """Get bridge transaction history for wallet"""
        # Filter by wallet and optionally bridge
        history = []
        for tx in self.pending_transactions.values():
            if tx.sender == wallet:
                if bridge is None or tx.bridge == bridge:
                    history.append(tx)
        
        return sorted(history, key=lambda x: x.timestamp, reverse=True)


# Global bridge manager
_bridge_manager: Optional[CrossChainBridgeManager] = None


async def get_bridge_manager() -> CrossChainBridgeManager:
    """Get or create global bridge manager"""
    global _bridge_manager
    if _bridge_manager is None:
        _bridge_manager = CrossChainBridgeManager()
        
        # Initialize all bridges
        await _bridge_manager.add_bridge(BridgeType.ACROSS, AcrossBridge())
        await _bridge_manager.add_bridge(BridgeType.STARGATE, StargateBridge())
        await _bridge_manager.add_bridge(BridgeType.HOP, HopBridge())
        await _bridge_manager.add_bridge(BridgeType.SYNAPSE, SynapseBridge())
        
        logger.info("Cross-chain bridge manager initialized")
    
    return _bridge_manager
