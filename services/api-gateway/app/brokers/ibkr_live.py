"""
Interactive Brokers LIVE API Integration
=========================================
Real IBKR Client using REST API
"""

from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
import logging
import os

logger = logging.getLogger(__name__)


class InteractiveBrokersLive:
    """Production IBKR REST API Client"""
    
    def __init__(self, api_key: Optional[str] = None, paper: bool = True):
        self.api_key = api_key or os.getenv("IBKR_API_KEY")
        self.base_url = "https://api.ibkr.com/v1/api" if not paper else "https://api.ibkr.com/v1/api"
        self.paper = paper
        self.session: Optional[aiohttp.ClientSession] = None
        self.account: Optional[str] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to IBKR REST API"""
        self.session = aiohttp.ClientSession()
        
        # Get account list
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with self.session.get(f"{self.base_url}/portfolio/accounts", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.account = data[0].get("account") if data else None
                    self.connected = True
                    logger.info(f"IBKR connected: Account {self.account}")
                    return True
        except Exception as e:
            logger.error(f"IBKR connection failed: {e}")
            return False
        return False
    
    async def get_account_summary(self) -> Dict:
        """Get account details"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with self.session.get(f"{self.base_url}/portfolio/{self.account}/summary", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "account_id": self.account,
                    "net_liquidation": data.get("netliquidation", {}).get("amount", 0),
                    "cash": data.get("cashbalance", {}).get("amount", 0),
                    "buying_power": data.get("buyingpower", {}).get("amount", 0),
                    "mode": "paper" if self.paper else "live",
                    "timestamp": datetime.now().isoformat()
                }
            return {}
    
    async def get_positions(self) -> List[Dict]:
        """Get all positions"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with self.session.get(f"{self.base_url}/portfolio/{self.account}/positions", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return [
                    {
                        "symbol": pos.get("contractDesc"),
                        "quantity": pos.get("position", 0),
                        "avg_cost": pos.get("avgCost", 0),
                        "market_price": pos.get("mktPrice", 0),
                        "market_value": pos.get("mktValue", 0),
                        "unrealized_pnl": pos.get("unrealizedPnl", 0)
                    }
                    for pos in data
                ]
            return []
    
    async def place_order(self, symbol: str, action: str, quantity: float, order_type: str = "MKT", price: Optional[float] = None) -> Dict:
        """Place an order"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "conid": await self._get_conid(symbol),
            "orderType": order_type,
            "quantity": quantity,
            "side": action.lower(),
            "tif": "DAY"
        }
        
        if price and order_type in ["LMT", "STP_LMT"]:
            payload["price"] = price
        
        async with self.session.post(f"{self.base_url}/iserver/account/{self.account}/orders", headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "order_id": data.get("id"),
                    "status": data.get("status", "submitted"),
                    "symbol": symbol,
                    "action": action,
                    "quantity": quantity,
                    "order_type": order_type
                }
            return {"error": f"Order failed: {resp.status}"}
    
    async def _get_conid(self, symbol: str) -> int:
        """Get contract ID for symbol"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with self.session.get(f"{self.base_url}/iserver/secdef/search?symbol={symbol}&name=true", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data[0].get("conid") if data else 0
        return 0
    
    async def get_options_chain(self, symbol: str) -> List[Dict]:
        """Get options chain for symbol"""
        conid = await self._get_conid(symbol)
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with self.session.get(f"{self.base_url}/iserver/secdef/info?conid={conid}&sectype=OPT", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("contracts", [])
            return []
    
    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()
            self.connected = False
