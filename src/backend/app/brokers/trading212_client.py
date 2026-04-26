"""
Trading212 API Integration
EU-based commission-free trading
Pie investing and auto-invest features
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
import aiohttp
import asyncio


class T212OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class T212TimeInForce(Enum):
    GTC = "GTC"  # Good till cancelled
    IOC = "IOC"  # Immediate or cancel


@dataclass
class Trading212Order:
    """Trading212 order request"""
    ticker: str
    quantity: Optional[Decimal] = None
    value: Optional[Decimal] = None  # Value in account currency
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_validity: T212TimeInForce = T212TimeInForce.GTC
    
    def to_dict(self) -> Dict[str, Any]:
        data = {}
        if self.quantity:
            data["quantity"] = str(self.quantity)
        if self.value:
            data["value"] = str(self.value)
        if self.limit_price:
            data["limitPrice"] = str(self.limit_price)
        if self.stop_price:
            data["stopPrice"] = str(self.stop_price)
        data["timeValidity"] = self.time_validity.value
        return data


@dataclass
class T212Pie:
    """Trading212 pie (portfolio bundle)"""
    id: str
    name: str
    goal: Optional[Decimal] = None
    cash_value: Decimal = Decimal("0")
    invested_value: Decimal = Decimal("0")
    result: Decimal = Decimal("0")
    result_percent: float = 0.0
    dividend_cash: Decimal = Decimal("0")
    instruments: List[Dict] = field(default_factory=list)
    settings: Dict = field(default_factory=dict)


class Trading212Client:
    """
    Trading212 API Client
    
    Features:
    - Commission-free trading (EU/UK)
    - Pie investing (portfolio bundles)
    - Auto-invest
    - Dividend reinvestment
    """
    
    DEMO_URL = "https://demo.trading212.com"
    LIVE_URL = "https://live.trading212.com"
    
    def __init__(self, api_key: str, demo: bool = True):
        self.api_key = api_key
        self.demo = demo
        self.base_url = self.DEMO_URL if demo else self.LIVE_URL
        
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the client session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_account_cash(self) -> Dict[str, Any]:
        """Get account cash details"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/account/cash",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def get_account_metadata(self) -> Dict[str, Any]:
        """Get account metadata (currency, status)"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/account/info",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def submit_order(
        self,
        ticker: str,
        side: str,  # buy or sell
        order: Trading212Order
    ) -> Dict[str, Any]:
        """Submit a new order"""
        session = await self._get_session()
        
        url = f"{self.base_url}/api/v0/equity/orders"
        
        data = order.to_dict()
        data["ticker"] = ticker
        
        async with session.post(
            url,
            headers=self.headers,
            json=data
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Order error: {error}")
    
    async def get_orders(
        self,
        cursor: Optional[str] = None,
        ticker: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get orders with pagination"""
        session = await self._get_session()
        
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if ticker:
            params["ticker"] = ticker
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/orders",
            headers=self.headers,
            params=params
        ) as response:
            if response.status == 200:
                return await response.json()
            return {"items": []}
    
    async def delete_order(self, order_id: str) -> bool:
        """Cancel an order"""
        session = await self._get_session()
        
        async with session.delete(
            f"{self.base_url}/api/v0/equity/orders/{order_id}",
            headers=self.headers
        ) as response:
            return response.status == 200
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/portfolio",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def get_position(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get specific position"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/portfolio/{ticker}",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            return None
    
    # Pie Management
    
    async def get_pies(self) -> List[T212Pie]:
        """Get all pies"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/pies",
            headers=self.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                pies = []
                for pie_data in data:
                    pies.append(T212Pie(
                        id=pie_data["id"],
                        name=pie_data["name"],
                        goal=Decimal(str(pie_data.get("goal", 0))) if pie_data.get("goal") else None,
                        cash_value=Decimal(str(pie_data.get("cashValue", 0))),
                        invested_value=Decimal(str(pie_data.get("investedValue", 0))),
                        result=Decimal(str(pie_data.get("result", 0))),
                        result_percent=float(pie_data.get("resultCoef", 0)),
                        dividend_cash=Decimal(str(pie_data.get("dividendCash", 0))),
                        instruments=pie_data.get("instruments", []),
                        settings=pie_data.get("settings", {})
                    ))
                return pies
            return []
    
    async def create_pie(
        self,
        name: str,
        instruments: List[Dict[str, Any]],  # [{"ticker": "AAPL", "quantity": 10, "weight": 50}]
        settings: Optional[Dict] = None,
        goal: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Create a new pie (portfolio bundle)
        
        Args:
            name: Pie name
            instruments: List of instruments with weights
            settings: Pie settings
            goal: Target value goal
        """
        session = await self._get_session()
        
        data = {
            "name": name,
            "instruments": instruments
        }
        
        if settings:
            data["settings"] = settings
        if goal:
            data["goal"] = str(goal)
        
        async with session.post(
            f"{self.base_url}/api/v0/equity/pies",
            headers=self.headers,
            json=data
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Create pie error: {error}")
    
    async def update_pie(
        self,
        pie_id: str,
        name: Optional[str] = None,
        instruments: Optional[List[Dict]] = None,
        settings: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update pie configuration"""
        session = await self._get_session()
        
        data = {}
        if name:
            data["name"] = name
        if instruments:
            data["instruments"] = instruments
        if settings:
            data["settings"] = settings
        
        async with session.post(
            f"{self.base_url}/api/v0/equity/pies/{pie_id}",
            headers=self.headers,
            json=data
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Update pie error: {error}")
    
    async def delete_pie(self, pie_id: str) -> bool:
        """Delete a pie"""
        session = await self._get_session()
        
        async with session.delete(
            f"{self.base_url}/api/v0/equity/pies/{pie_id}",
            headers=self.headers
        ) as response:
            return response.status == 200
    
    async def buy_pie(self, pie_id: str, amount: Decimal) -> Dict[str, Any]:
        """Buy into a pie with specific amount"""
        session = await self._get_session()
        
        async with session.post(
            f"{self.base_url}/api/v0/equity/pies/{pie_id}/buy",
            headers=self.headers,
            json={"value": str(amount)}
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Buy pie error: {error}")
    
    async def sell_pie(self, pie_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        Sell from a pie
        If amount not specified, sells entire pie
        """
        session = await self._get_session()
        
        data = {}
        if amount:
            data["value"] = str(amount)
        
        async with session.post(
            f"{self.base_url}/api/v0/equity/pies/{pie_id}/sell",
            headers=self.headers,
            json=data
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Sell pie error: {error}")
    
    async def get_pie_investments(self, pie_id: str) -> List[Dict[str, Any]]:
        """Get investment history for a pie"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/pies/{pie_id}/investments",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def get_historical_data(
        self,
        ticker: str,
        time_range: str = "day"  # day, week, month, year, max
    ) -> List[Dict[str, Any]]:
        """Get historical price data"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/pricing/{time_range}/tickers/{ticker}",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Get exchange rate between currencies"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v0/historical-currencies/{from_currency}/{to_currency}",
            headers=self.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return Decimal(str(data.get("rate", 1)))
            return Decimal("1")
    
    async def get_instruments(
        self,
        cursor: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search available instruments"""
        session = await self._get_session()
        
        params = {}
        if cursor:
            params["cursor"] = cursor
        if search:
            params["search"] = search
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/metadata/instruments",
            headers=self.headers,
            params=params
        ) as response:
            if response.status == 200:
                return await response.json()
            return {"items": []}
    
    async def get_instrument_details(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get detailed instrument info"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v0/equity/metadata/instruments/{ticker}",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            return None
