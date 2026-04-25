"""Pionex Broker - 0.05% fees, built-in bots"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PionexOrder:
    symbol: str
    side: str
    qty: float
    price: Optional[float] = None

class PionexBroker:
    """Pionex: 0.05% fees, 16 free bots, perfect for small accounts"""
    
    BASE_URL = "https://api.pionex.com"
    FEE = 0.0005  # 0.05%
    
    def __init__(self, api_key: str = None, secret: str = None, paper: bool = True):
        self.api_key = api_key
        self.secret = secret
        self.paper = paper
        self.balance = {"USDT": 100.0}
        self.orders: List[Dict] = []
    
    def get_info(self) -> Dict:
        return {
            "exchange": "Pionex",
            "fee": "0.05%",
            "paper_mode": self.paper,
            "balance": self.balance
        }
    
    def place_order(self, order: PionexOrder) -> Dict:
        if self.paper:
            fee = order.qty * (order.price or 100) * self.FEE
            self.orders.append({
                "symbol": order.symbol,
                "side": order.side,
                "qty": order.qty,
                "fee": fee
            })
            return {"status": "filled", "fee": fee}
        return {"status": "live_order_placed"}
