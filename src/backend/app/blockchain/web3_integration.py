"""
Web3 Integration Module
======================
Comprehensive Web3 integration for Veyra
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import aiohttp
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BINANCE_SMART_CHAIN = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"
    HARMONY = "harmony"


class WalletType(Enum):
    """Supported wallet types"""
    METAMASK = "metamask"
    WALLET_CONNECT = "walletconnect"
    COINBASE_WALLET = "coinbase"
    TRUST_WALLET = "trust"
    SAFE = "safe"
    LEDGER = "ledger"
    TREZOR = "trezor"


@dataclass
class WalletInfo:
    """Wallet information"""
    address: str
    wallet_type: WalletType
    chain_id: int
    balance_wei: int
    balance_eth: float
    nonce: int
    last_active: datetime
    is_connected: bool


@dataclass
class TransactionInfo:
    """Transaction information"""
    hash: str
    from_address: str
    to_address: str
    value_wei: int
    value_eth: float
    gas_price: int
    gas_limit: int
    gas_used: int
    block_number: int
    block_timestamp: datetime
    status: str
    data: str


@dataclass
class TokenInfo:
    """Token information"""
    address: str
    symbol: str
    name: str
    decimals: int
    total_supply: int
    holder_count: int
    price_usd: float
    market_cap: float
    volume_24h: float


class Web3Integration:
    """Comprehensive Web3 integration for Veyra"""
    
    def __init__(self):
        self.network_configs = {
            BlockchainNetwork.ETHEREUM: {
                "chain_id": 1,
                "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
                "explorer_url": "https://etherscan.io",
                "native_currency": "ETH",
                "block_time": 12
            },
            BlockchainNetwork.POLYGON: {
                "chain_id": 137,
                "rpc_url": "https://polygon-rpc.com",
                "explorer_url": "https://polygonscan.com",
                "native_currency": "MATIC",
                "block_time": 2
            },
            BlockchainNetwork.BINANCE_SMART_CHAIN: {
                "chain_id": 56,
                "rpc_url": "https://bsc-dataseed1.binance.org",
                "explorer_url": "https://bscscan.com",
                "native_currency": "BNB",
                "block_time": 3
            },
            BlockchainNetwork.ARBITRUM: {
                "chain_id": 42161,
                "rpc_url": "https://arb1.arbitrum.io/rpc",
                "explorer_url": "https://arbiscan.io",
                "native_currency": "ETH",
                "block_time": 0.5
            }
        }
        
        self.connected_wallets: Dict[str, WalletInfo] = {}
        self.supported_tokens: Dict[str, TokenInfo] = {}
        self.transaction_cache: Dict[str, TransactionInfo] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize Web3 integration"""
        self.session = aiohttp.ClientSession()
        await self._load_popular_tokens()
        logger.info("Web3 integration initialized")
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    async def _load_popular_tokens(self):
        """Load popular token information"""
        # Popular tokens on Ethereum
        popular_tokens = {
            "USDT": {
                "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "symbol": "USDT",
                "name": "Tether USD",
                "decimals": 6,
                "chain": BlockchainNetwork.ETHEREUM
            },
            "USDC": {
                "address": "0xA0b86a33E6441b8e8C7C7b0b0b0b0b0b0b0b0b0b",
                "symbol": "USDC",
                "name": "USD Coin",
                "decimals": 6,
                "chain": BlockchainNetwork.ETHEREUM
            },
            "DAI": {
                "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                "symbol": "DAI",
                "name": "Dai Stablecoin",
                "decimals": 18,
                "chain": BlockchainNetwork.ETHEREUM
            },
            "LINK": {
                "address": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
                "symbol": "LINK",
                "name": "ChainLink Token",
                "decimals": 18,
                "chain": BlockchainNetwork.ETHEREUM
            }
        }
        
        for symbol, token_data in popular_tokens.items():
            token_info = TokenInfo(
                address=token_data["address"],
                symbol=token_data["symbol"],
                name=token_data["name"],
                decimals=token_data["decimals"],
                total_supply=0,
                holder_count=0,
                price_usd=1.0 if symbol in ["USDT", "USDC", "DAI"] else 0.0,
                market_cap=0.0,
                volume_24h=0.0
            )
            self.supported_tokens[symbol] = token_info
            
    async def connect_wallet(self, address: str, wallet_type: WalletType, 
                           network: BlockchainNetwork) -> WalletInfo:
        """Connect a wallet"""
        try:
            # Get wallet balance and nonce
            balance_wei, nonce = await self._get_wallet_balance_and_nonce(address, network)
            
            wallet_info = WalletInfo(
                address=address.lower(),
                wallet_type=wallet_type,
                chain_id=self.network_configs[network]["chain_id"],
                balance_wei=balance_wei,
                balance_eth=self._wei_to_eth(balance_wei),
                nonce=nonce,
                last_active=datetime.now(),
                is_connected=True
            )
            
            self.connected_wallets[address.lower()] = wallet_info
            logger.info(f"Connected wallet {address} on {network.value}")
            
            return wallet_info
            
        except Exception as e:
            logger.error(f"Failed to connect wallet {address}: {e}")
            raise
            
    async def disconnect_wallet(self, address: str):
        """Disconnect a wallet"""
        address_lower = address.lower()
        if address_lower in self.connected_wallets:
            del self.connected_wallets[address_lower]
            logger.info(f"Disconnected wallet {address}")
            
    async def _get_wallet_balance_and_nonce(self, address: str, 
                                          network: BlockchainNetwork) -> tuple[int, int]:
        """Get wallet balance and nonce"""
        config = self.network_configs[network]
        
        # Get balance
        balance_data = await self._make_rpc_call(network, "eth_getBalance", [address, "latest"])
        balance_wei = int(balance_data, 16) if isinstance(balance_data, str) else balance_data
        
        # Get nonce
        nonce_data = await self._make_rpc_call(network, "eth_getTransactionCount", [address, "latest"])
        nonce = int(nonce_data, 16) if isinstance(nonce_data, str) else nonce_data
        
        return balance_wei, nonce
        
    async def _make_rpc_call(self, network: BlockchainNetwork, method: str, 
                           params: List[Any]) -> Any:
        """Make RPC call to blockchain"""
        config = self.network_configs[network]
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        async with self.session.post(config["rpc_url"], json=payload) as response:
            result = await response.json()
            if "error" in result:
                raise Exception(f"RPC error: {result['error']}")
            return result.get("result")
            
    def _wei_to_eth(self, wei: int) -> float:
        """Convert wei to ETH"""
        return Decimal(wei) / Decimal(10**18)
        
    def _eth_to_wei(self, eth: float) -> int:
        """Convert ETH to wei"""
        return int(Decimal(eth) * Decimal(10**18))
        
    async def get_transaction(self, tx_hash: str, 
                           network: BlockchainNetwork) -> Optional[TransactionInfo]:
        """Get transaction information"""
        if tx_hash in self.transaction_cache:
            return self.transaction_cache[tx_hash]
            
        try:
            tx_data = await self._make_rpc_call(network, "eth_getTransactionByHash", [tx_hash])
            receipt_data = await self._make_rpc_call(network, "eth_getTransactionReceipt", [tx_hash])
            
            if not tx_data:
                return None
                
            # Get block information
            block_data = await self._make_rpc_call(network, "eth_getBlockByHash", [tx_data["blockHash"], False])
            block_timestamp = datetime.fromtimestamp(int(block_data["timestamp"], 16))
            
            transaction = TransactionInfo(
                hash=tx_hash,
                from_address=tx_data["from"],
                to_address=tx_data.get("to", ""),
                value_wei=int(tx_data["value"], 16),
                value_eth=self._wei_to_eth(int(tx_data["value"], 16)),
                gas_price=int(tx_data["gasPrice"], 16),
                gas_limit=int(tx_data["gas"], 16),
                gas_used=int(receipt_data["gasUsed"], 16),
                block_number=int(tx_data["blockNumber"], 16),
                block_timestamp=block_timestamp,
                status="success" if receipt_data["status"] == "0x1" else "failed",
                data=tx_data.get("input", "")
            )
            
            self.transaction_cache[tx_hash] = transaction
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to get transaction {tx_hash}: {e}")
            return None
            
    async def get_wallet_transactions(self, address: str, 
                                   network: BlockchainNetwork,
                                   limit: int = 50) -> List[TransactionInfo]:
        """Get wallet transactions"""
        try:
            # Get latest block number
            latest_block = await self._make_rpc_call(network, "eth_blockNumber", [])
            latest_block_number = int(latest_block, 16)
            
            transactions = []
            
            # Scan recent blocks for transactions
            for block_num in range(latest_block_number, max(latest_block_number - 1000, 0), -1):
                if len(transactions) >= limit:
                    break
                    
                try:
                    block_data = await self._make_rpc_call(network, "eth_getBlockByNumber", 
                                                        [f"0x{block_num:x}", True])
                    
                    for tx in block_data.get("transactions", []):
                        if (tx["from"].lower() == address.lower() or 
                            tx.get("to", "").lower() == address.lower()):
                            
                            transaction = await self.get_transaction(tx["hash"], network)
                            if transaction:
                                transactions.append(transaction)
                                
                except Exception as e:
                    logger.error(f"Error scanning block {block_num}: {e}")
                    continue
                    
            return transactions[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get wallet transactions: {e}")
            return []
            
    async def get_token_balance(self, address: str, token_address: str,
                              network: BlockchainNetwork) -> float:
        """Get ERC-20 token balance"""
        try:
            # ERC-20 balanceOf function signature
            balance_of_signature = "0x70a08231"
            
            # Pad address to 32 bytes
            address_padded = address.lower().replace("0x", "").zfill(64)
            
            data = balance_of_signature + address_padded
            
            result = await self._make_rpc_call(network, "eth_call", [{
                "to": token_address,
                "data": data
            }, "latest"])
            
            balance_wei = int(result, 16)
            
            # Get token decimals (simplified - would need to query token contract)
            decimals = 18  # Default to 18 decimals
            
            return Decimal(balance_wei) / Decimal(10**decimals)
            
        except Exception as e:
            logger.error(f"Failed to get token balance: {e}")
            return 0.0
            
    async def send_transaction(self, from_address: str, to_address: str,
                             value_eth: float, network: BlockchainNetwork,
                             data: str = "") -> str:
        """Send transaction (simplified - would need actual signing)"""
        try:
            config = self.network_configs[network]
            
            # Get nonce
            nonce = await self._make_rpc_call(network, "eth_getTransactionCount", [from_address, "latest"])
            
            # Build transaction
            tx_data = {
                "from": from_address,
                "to": to_address,
                "value": f"0x{self._eth_to_wei(value_eth):x}",
                "gas": "0x5208",  # 21000 gas
                "gasPrice": f"0x{int(20e9):x}",  # 20 gwei
                "nonce": f"0x{nonce:x}",
                "data": data
            }
            
            # This would require actual signing with private key
            # For now, return a mock transaction hash
            mock_tx_hash = hashlib.sha256(f"{from_address}{to_address}{value_eth}{datetime.now()}".encode()).hexdigest()
            
            logger.info(f"Mock transaction sent: {mock_tx_hash}")
            return f"0x{mock_tx_hash}"
            
        except Exception as e:
            logger.error(f"Failed to send transaction: {e}")
            raise
            
    async def get_token_price(self, symbol: str) -> float:
        """Get token price from external API"""
        try:
            # This would integrate with CoinGecko or CoinMarketCap API
            # For now, return mock prices
            mock_prices = {
                "USDT": 1.0,
                "USDC": 1.0,
                "DAI": 1.0,
                "LINK": 15.0,
                "ETH": 2000.0,
                "BTC": 50000.0
            }
            
            return mock_prices.get(symbol.upper(), 0.0)
            
        except Exception as e:
            logger.error(f"Failed to get token price: {e}")
            return 0.0
            
    async def get_defi_positions(self, address: str) -> Dict[str, Any]:
        """Get DeFi positions for address"""
        try:
            # This would integrate with DeFi protocols like Aave, Compound, Uniswap
            # For now, return mock data
            return {
                "lending": {
                    "total_supplied": 1000.0,
                    "total_borrowed": 500.0,
                    "protocols": ["Aave", "Compound"]
                },
                "liquidity": {
                    "total_locked": 2000.0,
                    "pools": ["USDC-ETH", "DAI-USDT"]
                },
                "yield_farming": {
                    "total_staked": 500.0,
                    "pools": ["Curve", "Balancer"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get DeFi positions: {e}")
            return {}
            
    def get_connected_wallets(self) -> List[WalletInfo]:
        """Get all connected wallets"""
        return list(self.connected_wallets.values())
        
    def get_supported_tokens(self) -> List[TokenInfo]:
        """Get all supported tokens"""
        return list(self.supported_tokens.values())


# Global Web3 integration instance
_web3_integration = None

def get_web3_integration() -> Web3Integration:
    """Get the global Web3 integration instance"""
    global _web3_integration
    if _web3_integration is None:
        _web3_integration = Web3Integration()
    return _web3_integration
