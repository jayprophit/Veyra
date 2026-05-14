"""Whale Tracker - Track large crypto wallet movements"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class WhaleAlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class WhaleTransaction:
    tx_hash: str
    from_address: str
    to_address: str
    amount: float
    token: str
    timestamp: datetime
    usd_value: float
    is_exchange_from: bool
    is_exchange_to: bool

class WhaleTracker:
    """Track and analyze large cryptocurrency transactions"""
    
    def __init__(self):
        self.whale_thresholds = {
            "BTC": 100,      # 100+ BTC
            "ETH": 1000,     # 1000+ ETH
            "USDT": 1000000, # $1M+ USDT
            "USDC": 1000000, # $1M+ USDC
        }
        self.known_exchanges = {
            "Binance": ["0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"],
            "Coinbase": ["0x71660c4005ba85c37ccec55d991c6a548ff96d37"],
            "Kraken": ["0x267be1c1d684f78cb4f27a976185c6b5d9c4b0d3"]
        }
        self.transactions: List[WhaleTransaction] = []
        self.whale_wallets: Dict[str, Dict] = {}
    
    def add_transaction(self, tx: WhaleTransaction):
        """Add transaction to tracker"""
        self.transactions.append(tx)
        
        # Update whale wallet balances
        self._update_wallet_stats(tx)
    
    def _update_wallet_stats(self, tx: WhaleTransaction):
        """Update statistics for whale wallets"""
        # From address
        if tx.from_address not in self.whale_wallets:
            self.whale_wallets[tx.from_address] = {
                "total_out": 0,
                "total_in": 0,
                "tx_count": 0,
                "tokens": set()
            }
        
        self.whale_wallets[tx.from_address]["total_out"] += tx.usd_value
        self.whale_wallets[tx.from_address]["tx_count"] += 1
        self.whale_wallets[tx.from_address]["tokens"].add(tx.token)
        
        # To address
        if tx.to_address not in self.whale_wallets:
            self.whale_wallets[tx.to_address] = {
                "total_out": 0,
                "total_in": 0,
                "tx_count": 0,
                "tokens": set()
            }
        
        self.whale_wallets[tx.to_address]["total_in"] += tx.usd_value
        self.whale_wallets[tx.to_address]["tx_count"] += 1
        self.whale_wallets[tx.to_address]["tokens"].add(tx.token)
    
    def detect_whale_activity(self, hours: int = 24) -> Dict:
        """Detect whale activity in time window"""
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        
        recent_txs = [
            tx for tx in self.transactions
            if tx.timestamp.timestamp() > cutoff
        ]
        
        if not recent_txs:
            return {"message": "No whale activity detected"}
        
        # Analyze flows
        exchange_outflow = sum(tx.usd_value for tx in recent_txs 
                              if tx.is_exchange_from and not tx.is_exchange_to)
        exchange_inflow = sum(tx.usd_value for tx in recent_txs 
                             if tx.is_exchange_to and not tx.is_exchange_from)
        
        net_exchange_flow = exchange_inflow - exchange_outflow
        
        # Largest transactions
        sorted_txs = sorted(recent_txs, key=lambda x: x.usd_value, reverse=True)
        
        # Alert level
        total_volume = sum(tx.usd_value for tx in recent_txs)
        alert_level = self._determine_alert_level(total_volume, net_exchange_flow)
        
        return {
            "time_window_hours": hours,
            "whale_transactions": len(recent_txs),
            "total_volume_usd": round(total_volume, 2),
            "exchange_outflow_usd": round(exchange_outflow, 2),
            "exchange_inflow_usd": round(exchange_inflow, 2),
            "net_exchange_flow": round(net_exchange_flow, 2),
            "interpretation": "ACCUMULATION" if net_exchange_flow < -1e6 else "DISTRIBUTION" if net_exchange_flow > 1e6 else "NEUTRAL",
            "alert_level": alert_level.value,
            "largest_transactions": [
                {
                    "tx_hash": tx.tx_hash[:10] + "...",
                    "amount": tx.amount,
                    "token": tx.token,
                    "usd_value": round(tx.usd_value, 2),
                    "type": "EXCHANGE_WITHDRAWAL" if tx.is_exchange_from else "EXCHANGE_DEPOSIT" if tx.is_exchange_to else "WALLET_TRANSFER"
                }
                for tx in sorted_txs[:5]
            ]
        }
    
    def _determine_alert_level(self, volume: float, net_flow: float) -> WhaleAlertLevel:
        """Determine alert level based on activity"""
        if volume > 100_000_000 or abs(net_flow) > 50_000_000:
            return WhaleAlertLevel.CRITICAL
        elif volume > 50_000_000 or abs(net_flow) > 20_000_000:
            return WhaleAlertLevel.HIGH
        elif volume > 10_000_000 or abs(net_flow) > 5_000_000:
            return WhaleAlertLevel.MEDIUM
        return WhaleAlertLevel.LOW
    
    def track_wallet(self, address: str, label: str = None) -> Dict:
        """Track specific whale wallet"""
        if address not in self.whale_wallets:
            return {"error": "Wallet not found in transaction history"}
        
        stats = self.whale_wallets[address]
        
        # Get recent transactions for this wallet
        wallet_txs = [
            tx for tx in self.transactions
            if tx.from_address == address or tx.to_address == address
        ]
        
        recent_txs = sorted(wallet_txs, key=lambda x: x.timestamp, reverse=True)[:10]
        
        # Calculate balance change
        balance_change = stats["total_in"] - stats["total_out"]
        
        return {
            "address": address[:10] + "..." + address[-8:] if len(address) > 20 else address,
            "label": label,
            "total_volume_in": round(stats["total_in"], 2),
            "total_volume_out": round(stats["total_out"], 2),
            "net_position_change": round(balance_change, 2),
            "transaction_count": stats["tx_count"],
            "tokens_involved": list(stats["tokens"]),
            "wallet_type": self._classify_wallet(stats, recent_txs),
            "recent_activity": [
                {
                    "type": "IN" if tx.to_address == address else "OUT",
                    "token": tx.token,
                    "amount": tx.amount,
                    "usd_value": round(tx.usd_value, 2),
                    "time": tx.timestamp.strftime("%Y-%m-%d %H:%M")
                }
                for tx in recent_txs[:5]
            ]
        }
    
    def _classify_wallet(self, stats: Dict, recent_txs: List[WhaleTransaction]) -> str:
        """Classify wallet behavior"""
        if stats["total_out"] > stats["total_in"] * 2:
            return "DISTRIBUTOR"
        elif stats["total_in"] > stats["total_out"] * 2:
            return "ACCUMULATOR"
        elif stats["tx_count"] > 50:
            return "ACTIVE_TRADER"
        return "HOLDER"
    
    def get_exchange_flows(self) -> Dict:
        """Analyze exchange deposit/withdrawal patterns"""
        exchange_stats = {}
        
        for name, addresses in self.known_exchanges.items():
            deposits = sum(tx.usd_value for tx in self.transactions 
                         if tx.to_address in addresses)
            withdrawals = sum(tx.usd_value for tx in self.transactions 
                            if tx.from_address in addresses)
            
            exchange_stats[name] = {
                "deposits_usd": round(deposits, 2),
                "withdrawals_usd": round(withdrawals, 2),
                "net_flow": round(deposits - withdrawals, 2),
                "direction": "INFLOW" if deposits > withdrawals else "OUTFLOW"
            }
        
        # Determine market sentiment based on exchange flows
        total_withdrawals = sum(s["withdrawals_usd"] for s in exchange_stats.values())
        total_deposits = sum(s["deposits_usd"] for s in exchange_stats.values())
        
        return {
            "exchange_breakdown": exchange_stats,
            "total_deposits": round(total_deposits, 2),
            "total_withdrawals": round(total_withdrawals, 2),
            "net_exchange_flow": round(total_deposits - total_withdrawals, 2),
            "market_sentiment": "BULLISH" if total_withdrawals > total_deposits else "BEARISH" if total_deposits > total_withdrawals else "NEUTRAL",
            "interpretation": "Whales withdrawing to cold storage (accumulation)" if total_withdrawals > total_deposits else "Whales depositing to exchanges (selling pressure)"
        }
    
    def alert_subscription(self, min_usd_threshold: float = 1000000,
                          tokens: List[str] = None) -> Dict:
        """Set up whale alert subscription"""
        return {
            "subscription_config": {
                "min_usd_threshold": min_usd_threshold,
                "tokens_tracked": tokens or ["BTC", "ETH", "USDT", "USDC"],
                "alert_channels": ["webhook", "email", "sms"],
                "alert_levels": {
                    "medium": min_usd_threshold,
                    "high": min_usd_threshold * 5,
                    "critical": min_usd_threshold * 10
                }
            },
            "active": True,
            "last_alert": None,
            "alerts_today": 0
        }
