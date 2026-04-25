"""
Coinbase Pro LIVE API Integration
"""

from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
import hmac
import hashlib
import base64
import json
import logging
import os

logger = logging.getLogger(__name__)


class CoinbaseLive:
    """Production Coinbase Advanced Trade API Client"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, sandbox: bool = False):
        self.api_key = api_key or os.getenv("COINBASE_API_KEY")
        self.api_secret = api_secret or os.getenv("COINBASE_API_SECRET")
        self.base_url = "https://api.coinbase.com/api/v3/brokerage" if not sandbox else "https://api-public.sandbox.exchange.coinbase.com"
        self.sandbox = sandbox
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to Coinbase API"""
        self.session = aiohttp.ClientSession()
        try:
            accounts = await self.get_accounts()
            self.connected = True
            logger.info(f"Coinbase connected: {len(accounts)} accounts")
            return True
        except Exception as e:
            logger.error(f"Coinbase connection failed: {e}")
            return False
    
    def _get_headers(self, method: str, path: str, body: str = "") -> Dict:
        """Generate authentication headers"""
        timestamp = str(int(datetime.now().timestamp()))
        message = timestamp + method.upper() + path + body
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return {
            "accept": "application/json",
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": "",  # For advanced trade API
            "Content-Type": "application/json"
        }
    
    async def get_accounts(self) -> List[Dict]:
        """Get all accounts/wallets"""
        headers = self._get_headers("GET", "/api/v3/brokerage/accounts")
        async with self.session.get(f"{self.base_url}/accounts", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("accounts", [])
            return []
    
    async def get_ticker(self, product_id: str) -> Dict:
        """Get current price for crypto pair"""
        headers = self._get_headers("GET", f"/api/v3/brokerage/products/{product_id}")
        async with self.session.get(f"{self.base_url}/products/{product_id}", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "product_id": product_id,
                    "price": float(data.get("price", 0)),
                    "bid": float(data.get("bid", 0)),
                    "ask": float(data.get("ask", 0)),
                    "volume": float(data.get("volume_24h", 0)),
                    "source": "coinbase_live"
                }
            return {}
    
    async def place_order(self, product_id: str, side: str, size: float, order_type: str = "market", price: Optional[float] = None) -> Dict:
        """Place crypto order"""
        path = "/api/v3/brokerage/orders"
        payload = {
            "product_id": product_id,
            "side": side.lower(),
            "order_configuration": {
                "market_market_ioc" if order_type == "market" else "limit_limit_gtc": {
                    "quote_size": str(size) if side.lower() == "buy" else None,
                    "base_size": str(size) if side.lower() == "sell" else None,
                    "price": str(price) if price else None
                }
            }
        }
        
        body = json.dumps(payload)
        headers = self._get_headers("POST", path, body)
        
        async with self.session.post(f"{self.base_url}/orders", headers=headers, data=body) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "id": data.get("order_id"),
                    "product_id": product_id,
                    "side": side,
                    "size": size,
                    "type": order_type,
                    "status": data.get("status", "pending"),
                    "source": "coinbase_live"
                }
            return {"error": f"Order failed: {resp.status}"}
    
    async def get_order_history(self) -> List[Dict]:
        """Get filled orders"""
        headers = self._get_headers("GET", "/api/v3/brokerage/orders/historical/batch")
        async with self.session.get(f"{self.base_url}/orders/historical/batch", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("orders", [])
            return []
    
    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()
            self.connected = False
