"""Alpaca Broker Integration - Production Ready"""
import os
import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AlpacaOrder:
    symbol: str
    qty: float
    side: str  # 'buy' or 'sell'
    type: str = 'market'  # 'market', 'limit', 'stop', 'stop_limit'
    time_in_force: str = 'day'
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None

class AlpacaBroker:
    """Production-ready Alpaca API integration."""
    
    def __init__(self, api_key: str = None, secret_key: str = None, paper: bool = True):
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        self.paper = paper
        
        self.base_url = (
            'https://paper-api.alpaca.markets' if paper 
            else 'https://api.alpaca.markets'
        )
        self.data_url = 'https://data.alpaca.markets'
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API keys required. Set ALPACA_API_KEY and ALPACA_SECRET_KEY env vars.")
    
    def _get_headers(self) -> Dict:
        return {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key
        }
    
    async def get_account(self) -> Dict:
        """Get account information."""
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.get(f"{self.base_url}/v2/account") as resp:
                if resp.status == 200:
                    return await resp.json()
                raise Exception(f"Failed to get account: {resp.status}")
    
    async def place_order(self, order: AlpacaOrder) -> Dict:
        """Place an order."""
        payload = {
            'symbol': order.symbol,
            'qty': order.qty,
            'side': order.side,
            'type': order.type,
            'time_in_force': order.time_in_force
        }
        if order.limit_price:
            payload['limit_price'] = order.limit_price
        if order.stop_price:
            payload['stop_price'] = order.stop_price
        
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.post(
                f"{self.base_url}/v2/orders",
                json=payload
            ) as resp:
                if resp.status in [200, 201]:
                    return await resp.json()
                error = await resp.text()
                raise Exception(f"Order failed: {error}")
    
    async def get_positions(self) -> List[Dict]:
        """Get current positions."""
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.get(f"{self.base_url}/v2/positions") as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
    
    async def get_orders(self, status: str = 'all') -> List[Dict]:
        """Get orders."""
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.get(
                f"{self.base_url}/v2/orders",
                params={'status': status}
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.delete(
                f"{self.base_url}/v2/orders/{order_id}"
            ) as resp:
                return resp.status == 200
    
    async def get_asset(self, symbol: str) -> Dict:
        """Get asset information."""
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.get(
                f"{self.base_url}/v2/assets/{symbol}"
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                raise Exception(f"Asset not found: {symbol}")
    
    async def get_bars(self, symbol: str, timeframe: str = '1Day', limit: int = 100) -> List[Dict]:
        """Get price bars."""
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.get(
                f"{self.data_url}/v2/stocks/{symbol}/bars",
                params={'timeframe': timeframe, 'limit': limit}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('bars', [])
                return []

# Usage example:
# broker = AlpacaBroker(paper=True)
# account = await broker.get_account()
# order = await broker.place_order(AlpacaOrder('AAPL', 10, 'buy'))
