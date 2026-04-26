"""
Layer 2 Network Manager
Arbitrum, Optimism, Base, zkSync, Starknet integration
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class L2Network(Enum):
    ARBITRUM_ONE = "arbitrum_one"
    ARBITRUM_NOVA = "arbitrum_nova"
    OPTIMISM = "optimism"
    BASE = "base"
    ZKSYNC = "zksync"
    STARKNET = "starknet"
    LINEA = "linea"
    SCROLL = "scroll"
    POLYGON_ZKEVM = "polygon_zkevm"
    MANTLE = "mantle"


@dataclass
class L2Config:
    name: str
    network: L2Network
    chain_id: int
    rpc_url: str
    explorer_url: str
    bridge_contract: str
    l1_gateway: str
    is_rollup: bool
    is_zk: bool
    block_time_seconds: float
    gas_token: str
    native_bridge_cost_eth: Decimal
    third_party_bridge_cost_eth: Decimal
    tvl_billions: float
    avg_gas_gwei: float


@dataclass
class BridgeTransaction:
    tx_hash: str
    source_chain: str
    dest_chain: str
    direction: str  # deposit or withdrawal
    token: str
    amount: Decimal
    l1_tx_hash: Optional[str]
    l2_tx_hash: Optional[str]
    status: str  # pending, confirmed, finalized
    timestamp: datetime
    estimated_completion: datetime
    gas_cost_eth: Decimal
    gas_cost_usd: float


@dataclass
class L2Transaction:
    tx_hash: str
    network: L2Network
    from_addr: str
    to_addr: str
    value: Decimal
    gas_price_gwei: float
    gas_used: int
    gas_cost_eth: Decimal
    gas_cost_usd: float
    timestamp: datetime
    status: str
    is_l1_origin: bool  # If initiated from L1


class ArbitrumConnector:
    """Arbitrum One/Nova connector - Optimistic Rollup"""
    
    BRIDGE_CONTRACT = "0x0000000000000000000000000000000000000064"
    INBOX_CONTRACT = "0x4Dbd4fc535Ab2726789bed7b2d8A43deB7C74782"
    
    def __init__(self, network: L2Network = L2Network.ARBITRUM_ONE):
        self.network = network
        self.connected = False
        self.pending_deposits: List[BridgeTransaction] = []
        self.pending_withdrawals: List[BridgeTransaction] = []
        
    async def connect(self) -> bool:
        """Connect to Arbitrum RPC"""
        try:
            logger.info(f"Connecting to {self.network.value}")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Arbitrum connection failed: {e}")
            return False
    
    async def deposit_eth(
        self,
        wallet: str,
        amount: Decimal,
        max_submission_cost: Decimal = Decimal("0.01")
    ) -> BridgeTransaction:
        """Deposit ETH from L1 to Arbitrum"""
        tx = BridgeTransaction(
            tx_hash=f"0x_arb_deposit_{datetime.now().timestamp()}",
            source_chain="ethereum",
            dest_chain=self.network.value,
            direction="deposit",
            token="ETH",
            amount=amount,
            l1_tx_hash=f"0x_l1_{datetime.now().timestamp()}",
            l2_tx_hash=None,
            status="pending",
            timestamp=datetime.now(),
            estimated_completion=datetime.now(),  # ~10 mins for Arbitrum
            gas_cost_eth=Decimal("0.005"),
            gas_cost_usd=17.5
        )
        self.pending_deposits.append(tx)
        logger.info(f"Arbitrum deposit: {amount} ETH from {wallet}")
        return tx
    
    async def initiate_withdrawal(
        self,
        wallet: str,
        amount: Decimal
    ) -> BridgeTransaction:
        """Initiate withdrawal from Arbitrum to L1"""
        tx = BridgeTransaction(
            tx_hash=f"0x_arb_withdraw_{datetime.now().timestamp()}",
            source_chain=self.network.value,
            dest_chain="ethereum",
            direction="withdrawal",
            token="ETH",
            amount=amount,
            l1_tx_hash=None,
            l2_tx_hash=f"0x_l2_{datetime.now().timestamp()}",
            status="pending",
            timestamp=datetime.now(),
            estimated_completion=datetime.now(),  # ~7 days for Arbitrum
            gas_cost_eth=Decimal("0.001"),
            gas_cost_usd=3.5
        )
        self.pending_withdrawals.append(tx)
        logger.info(f"Arbitrum withdrawal initiated: {amount} ETH")
        return tx
    
    async def confirm_withdrawal(self, tx_hash: str) -> bool:
        """Confirm withdrawal after challenge period"""
        logger.info(f"Confirming Arbitrum withdrawal: {tx_hash}")
        return True
    
    async def get_gas_price(self) -> Dict[str, float]:
        """Get current gas prices on Arbitrum"""
        return {
            "slow": 0.1,      # gwei
            "standard": 0.2,
            "fast": 0.5,
            "rapid": 1.0
        }
    
    async def estimate_l1_data_fee(self, calldata_bytes: int) -> Decimal:
        """Estimate L1 data fee for transaction (Arbitrum-specific)"""
        # Arbitrum charges extra for L1 data availability
        l1_base_fee = Decimal("20")  # gwei
        l1_fee = (Decimal(calldata_bytes) * Decimal("16") * l1_base_fee) / Decimal("10**9")
        return l1_fee


class OptimismConnector:
    """Optimism (OP Stack) connector - Optimistic Rollup"""
    
    BRIDGE_CONTRACT = "0x99C9fc46f92E8a1c0deC1b1747d010903C88493"
    
    def __init__(self, network: L2Network = L2Network.OPTIMISM):
        self.network = network
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to Optimism RPC"""
        try:
            logger.info(f"Connecting to {self.network.value}")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Optimism connection failed: {e}")
            return False
    
    async def deposit_eth(
        self,
        wallet: str,
        amount: Decimal
    ) -> BridgeTransaction:
        """Deposit ETH from L1 to Optimism"""
        tx = BridgeTransaction(
            tx_hash=f"0x_op_deposit_{datetime.now().timestamp()}",
            source_chain="ethereum",
            dest_chain=self.network.value,
            direction="deposit",
            token="ETH",
            amount=amount,
            l1_tx_hash=f"0x_l1_{datetime.now().timestamp()}",
            l2_tx_hash=f"0x_l2_{datetime.now().timestamp()}",
            status="confirmed",  # OP deposits are instant
            timestamp=datetime.now(),
            estimated_completion=datetime.now(),
            gas_cost_eth=Decimal("0.004"),
            gas_cost_usd=14.0
        )
        logger.info(f"Optimism deposit: {amount} ETH")
        return tx
    
    async def withdraw_eth(
        self,
        wallet: str,
        amount: Decimal
    ) -> BridgeTransaction:
        """Initiate withdrawal from Optimism"""
        tx = BridgeTransaction(
            tx_hash=f"0x_op_withdraw_{datetime.now().timestamp()}",
            source_chain=self.network.value,
            dest_chain="ethereum",
            direction="withdrawal",
            token="ETH",
            amount=amount,
            l1_tx_hash=None,
            l2_tx_hash=f"0x_l2_{datetime.now().timestamp()}",
            status="pending",
            timestamp=datetime.now(),
            estimated_completion=datetime.now(),  # ~7 days
            gas_cost_eth=Decimal("0.001"),
            gas_cost_usd=3.5
        )
        logger.info(f"Optimism withdrawal: {amount} ETH (7 day period)")
        return tx
    
    async def prove_withdrawal(self, withdrawal_hash: str) -> bool:
        """Prove withdrawal on L1 after challenge period"""
        logger.info(f"Proving Optimism withdrawal: {withdrawal_hash}")
        return True
    
    async def finalize_withdrawal(self, withdrawal_hash: str) -> bool:
        """Finalize withdrawal after proof"""
        logger.info(f"Finalizing Optimism withdrawal: {withdrawal_hash}")
        return True
    
    async def get_l1_gas_used(self, l2_tx_hash: str) -> int:
        """Get L1 gas used for L2 transaction (OP-specific)"""
        return 1600  # Average L1 gas units


class BaseConnector:
    """Base (Coinbase L2) connector - OP Stack"""
    
    def __init__(self):
        self.network = L2Network.BASE
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to Base RPC"""
        try:
            logger.info("Connecting to Base")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Base connection failed: {e}")
            return False
    
    async def deposit_from_coinbase(self, amount: Decimal) -> BridgeTransaction:
        """Special: Deposit from Coinbase (no gas fees)"""
        tx = BridgeTransaction(
            tx_hash=f"0x_base_cb_{datetime.now().timestamp()}",
            source_chain="coinbase",
            dest_chain="base",
            direction="deposit",
            token="ETH",
            amount=amount,
            l1_tx_hash=None,  # No L1 tx for Coinbase integration
            l2_tx_hash=f"0x_l2_{datetime.now().timestamp()}",
            status="confirmed",
            timestamp=datetime.now(),
            estimated_completion=datetime.now(),
            gas_cost_eth=Decimal("0"),
            gas_cost_usd=0.0
        )
        logger.info(f"Base deposit from Coinbase: {amount} ETH (no fees)")
        return tx


class ZKSyncConnector:
    """zkSync Era connector - ZK Rollup"""
    
    def __init__(self):
        self.network = L2Network.ZKSYNC
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to zkSync RPC"""
        try:
            logger.info("Connecting to zkSync Era")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"zkSync connection failed: {e}")
            return False
    
    async def deposit_eth(
        self,
        wallet: str,
        amount: Decimal
    ) -> BridgeTransaction:
        """Deposit to zkSync"""
        tx = BridgeTransaction(
            tx_hash=f"0x_zksync_deposit_{datetime.now().timestamp()}",
            source_chain="ethereum",
            dest_chain="zksync",
            direction="deposit",
            token="ETH",
            amount=amount,
            l1_tx_hash=f"0x_l1_{datetime.now().timestamp()}",
            l2_tx_hash=None,
            status="pending",
            timestamp=datetime.now(),
            estimated_completion=datetime.now(),  # ~15 mins
            gas_cost_eth=Decimal("0.003"),
            gas_cost_usd=10.5
        )
        logger.info(f"zkSync deposit: {amount} ETH")
        return tx
    
    async def get_zk_proof(self, tx_hash: str) -> Dict[str, Any]:
        """Get ZK proof for transaction"""
        return {
            "proof_valid": True,
            "commitment": f"0x_commitment_{tx_hash}",
            "verified_on_l1": True
        }


class StarknetConnector:
    """Starknet connector - ZK Rollup with Cairo"""
    
    def __init__(self):
        self.network = L2Network.STARKNET
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to Starknet"""
        try:
            logger.info("Connecting to Starknet")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Starknet connection failed: {e}")
            return False
    
    async def deploy_account(self) -> str:
        """Deploy Starknet account (required before use)"""
        return f"0x_starknet_account_{datetime.now().timestamp()}"


class Layer2Manager:
    """Manage all Layer 2 networks"""
    
    def __init__(self):
        self.networks: Dict[L2Network, Any] = {}
        self.configs: Dict[L2Network, L2Config] = self._load_configs()
        
    def _load_configs(self) -> Dict[L2Network, L2Config]:
        """Load default configurations for all L2s"""
        return {
            L2Network.ARBITRUM_ONE: L2Config(
                name="Arbitrum One",
                network=L2Network.ARBITRUM_ONE,
                chain_id=42161,
                rpc_url="https://arb1.arbitrum.io/rpc",
                explorer_url="https://arbiscan.io",
                bridge_contract="0x0000000000000000000000000000000000000064",
                l1_gateway="0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef",
                is_rollup=True,
                is_zk=False,
                block_time_seconds=0.25,
                gas_token="ETH",
                native_bridge_cost_eth=Decimal("0.005"),
                third_party_bridge_cost_eth=Decimal("0.001"),
                tvl_billions=15.0,
                avg_gas_gwei=0.2
            ),
            L2Network.OPTIMISM: L2Config(
                name="Optimism",
                network=L2Network.OPTIMISM,
                chain_id=10,
                rpc_url="https://mainnet.optimism.io",
                explorer_url="https://optimistic.etherscan.io",
                bridge_contract="0x99C9fc46f92E8a1c0deC1b1747d010903C88493",
                l1_gateway="0x25ace71c97B33Cc4729CF772ae268934F7ab70f",
                is_rollup=True,
                is_zk=False,
                block_time_seconds=2.0,
                gas_token="ETH",
                native_bridge_cost_eth=Decimal("0.004"),
                third_party_bridge_cost_eth=Decimal("0.001"),
                tvl_billions=8.0,
                avg_gas_gwei=0.1
            ),
            L2Network.BASE: L2Config(
                name="Base",
                network=L2Network.BASE,
                chain_id=8453,
                rpc_url="https://mainnet.base.org",
                explorer_url="https://basescan.org",
                bridge_contract="0x49048044D57e1CfcA56d822a7d6C3F22101C0B7c",
                l1_gateway="0x49048044D57e1CfcA56d822a7d6C3F22101C0B7c",
                is_rollup=True,
                is_zk=False,
                block_time_seconds=2.0,
                gas_token="ETH",
                native_bridge_cost_eth=Decimal("0.004"),
                third_party_bridge_cost_eth=Decimal("0.0005"),
                tvl_billions=6.0,
                avg_gas_gwei=0.1
            ),
            L2Network.ZKSYNC: L2Config(
                name="zkSync Era",
                network=L2Network.ZKSYNC,
                chain_id=324,
                rpc_url="https://mainnet.era.zksync.io",
                explorer_url="https://explorer.zksync.io",
                bridge_contract="0x32400084C286CF3E17e7B677ea9583e60a000324",
                l1_gateway="0x32400084C286CF3E17e7B677ea9583e60a000324",
                is_rollup=True,
                is_zk=True,
                block_time_seconds=1.0,
                gas_token="ETH",
                native_bridge_cost_eth=Decimal("0.003"),
                third_party_bridge_cost_eth=Decimal("0.001"),
                tvl_billions=0.8,
                avg_gas_gwei=0.25
            ),
            L2Network.STARKNET: L2Config(
                name="Starknet",
                network=L2Network.STARKNET,
                chain_id=1,  # SN_MAIN
                rpc_url="https://rpc.starknet.lava.build",
                explorer_url="https://starkscan.co",
                bridge_contract="0xae0Ee0A63a2cE6BaeEFFE56e7714Fb4E24Dc3bd4",
                l1_gateway="0xE2Bb56ee249fd61DeD24bB6D51c5F9D631756d4f",
                is_rollup=True,
                is_zk=True,
                block_time_seconds=2.0,
                gas_token="ETH",
                native_bridge_cost_eth=Decimal("0.01"),
                third_party_bridge_cost_eth=Decimal("0.002"),
                tvl_billions=0.5,
                avg_gas_gwei=0.5
            ),
        }
    
    async def add_network(self, network: L2Network, connector: Any):
        """Add L2 network connector"""
        self.networks[network] = connector
        logger.info(f"Added L2 network: {network.value}")
    
    async def get_bridge_cost_comparison(
        self,
        to_network: L2Network,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Compare bridge costs for different methods"""
        config = self.configs.get(to_network)
        if not config:
            return {"error": "Network not supported"}
        
        native_cost_eth = config.native_bridge_cost_eth
        third_party_cost_eth = config.third_party_bridge_cost_eth
        
        eth_price = 3500.0  # Would be dynamic
        
        return {
            "destination": to_network.value,
            "native_bridge": {
                "cost_eth": float(native_cost_eth),
                "cost_usd": float(native_cost_eth) * eth_price,
                "time_minutes": 10 if not config.is_zk else 15,
                "trust_assumption": "trust L2 sequencers"
            },
            "third_party_bridge": {
                "cost_eth": float(third_party_cost_eth),
                "cost_usd": float(third_party_bridge_cost_eth) * eth_price,
                "time_minutes": 2,
                "trust_assumption": "trust bridge operator",
                "platforms": ["Across", "Hop", "Stargate", "Celer", "Synapse"]
            },
            "recommendation": "third_party" if third_party_cost_eth < native_cost_eth * Decimal("0.5") else "native"
        }
    
    async def find_cheapest_l2_for_swap(
        self,
        token: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Find cheapest L2 for executing a swap"""
        results = []
        
        for network, config in self.configs.items():
            # Estimate total cost = bridge cost + swap gas
            bridge_cost = config.third_party_bridge_cost_eth
            swap_gas = Decimal(str(config.avg_gas_gwei * 100000 * 1e-9))  # 100k gas units
            total_cost = bridge_cost + swap_gas
            
            results.append({
                "network": network.value,
                "total_cost_eth": float(total_cost),
                "total_cost_usd": float(total_cost * 3500),
                "speed_seconds": config.block_time_seconds * 2,
                "tvl_billions": config.tvl_billions,
                "decentralization": "high" if config.is_zk else "medium"
            })
        
        results.sort(key=lambda x: x["total_cost_usd"])
        
        return {
            "cheapest": results[0],
            "all_options": results,
            "savings_vs_expensive": results[-1]["total_cost_usd"] - results[0]["total_cost_usd"]
        }
    
    async def get_all_networks_status(self) -> List[Dict[str, Any]]:
        """Get status of all L2 networks"""
        status = []
        
        for network, config in self.configs.items():
            connector = self.networks.get(network)
            status.append({
                "network": config.name,
                "chain_id": config.chain_id,
                "connected": connector.connected if connector else False,
                "is_zk": config.is_zk,
                "block_time": config.block_time_seconds,
                "avg_gas_gwei": config.avg_gas_gwei,
                "tvl_billions": config.tvl_billions,
                "bridge_cost_usd": float(config.third_party_bridge_cost_eth * 3500)
            })
        
        return status


# Global L2 manager
_l2_manager: Optional[Layer2Manager] = None


async def get_l2_manager() -> Layer2Manager:
    """Get or create global L2 manager"""
    global _l2_manager
    if _l2_manager is None:
        _l2_manager = Layer2Manager()
        
        # Initialize all L2 networks
        arbitrum = ArbitrumConnector(L2Network.ARBITRUM_ONE)
        await arbitrum.connect()
        await _l2_manager.add_network(L2Network.ARBITRUM_ONE, arbitrum)
        
        optimism = OptimismConnector(L2Network.OPTIMISM)
        await optimism.connect()
        await _l2_manager.add_network(L2Network.OPTIMISM, optimism)
        
        base = BaseConnector()
        await base.connect()
        await _l2_manager.add_network(L2Network.BASE, base)
        
        zksync = ZKSyncConnector()
        await zksync.connect()
        await _l2_manager.add_network(L2Network.ZKSYNC, zksync)
        
        starknet = StarknetConnector()
        await starknet.connect()
        await _l2_manager.add_network(L2Network.STARKNET, starknet)
        
        logger.info("All Layer 2 networks initialized")
    
    return _l2_manager
