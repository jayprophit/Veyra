"""
Fiat Currency Exchange / FX Providers
Forex.com, OANDA, XE, Wise, Revolut
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import asyncio
import aiohttp


class TransferType(Enum):
    SPOT = "spot"  # Immediate transfer
    FORWARD = "forward"  # Future date
    LIMIT = "limit"  # Target rate
    RECURRING = "recurring"  # Scheduled transfers


class TransferPurpose(Enum):
    PERSONAL = "personal"
    BUSINESS = "business"
    INVESTMENT = "investment"
    REMITTANCE = "remittance"
    TRADE = "trade"


@dataclass
class FXQuote:
    """FX exchange quote"""
    from_currency: str
    to_currency: str
    amount: Decimal
    
    # Rates
    mid_market_rate: Decimal
    customer_rate: Decimal
    spread: Decimal
    
    # Fees
    transfer_fee: Decimal
    total_cost: Decimal
    
    # Timing
    delivery_estimate: datetime
    rate_guaranteed_until: datetime


@dataclass
class Transfer:
    """Fiat currency transfer"""
    transfer_id: str
    from_currency: str
    to_currency: str
    amount_sent: Decimal
    amount_received: Decimal
    exchange_rate: Decimal
    fee: Decimal
    
    # Status
    status: str  # pending, processing, completed, failed, cancelled
    
    # Parties
    sender_account: str
    recipient_account: str
    
    # Timing
    created_at: datetime
    completed_at: Optional[datetime] = None
    estimated_delivery: Optional[datetime] = None


class FXProvider:
    """Base class for FX/fiat providers"""
    
    def __init__(self, name: str, api_key: str):
        self.name = name
        self.api_key = api_key
        self.base_url = ""
    
    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        raise NotImplementedError
    
    async def create_transfer(
        self,
        from_currency: str,
        to_currency: str,
        amount: Decimal,
        recipient: Dict[str, Any]
    ) -> Transfer:
        raise NotImplementedError


class WiseClient(FXProvider):
    """Wise (formerly TransferWise) API"""
    
    BASE_URL = "https://api.transferwise.com"
    
    def __init__(self, api_key: str):
        super().__init__("Wise", api_key)
        self.base_url = self.BASE_URL
        self.profile_id = None
    
    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Get exchange rate from Wise"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            url = f"{self.base_url}/v1/rates?source={from_currency}&target={to_currency}"
            
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                
                if isinstance(data, list) and len(data) > 0:
                    rate_data = data[0]
                    return {
                        "provider": "Wise",
                        "from": from_currency,
                        "to": to_currency,
                        "rate": rate_data.get("rate"),
                        "timestamp": rate_data.get("time")
                    }
                
                return {"error": "Rate not available"}
    
    async def create_quote(
        self,
        from_currency: str,
        to_currency: str,
        amount: Decimal,
        amount_type: str = "source"  # source or target
    ) -> Dict[str, Any]:
        """Create transfer quote"""
        if not self.profile_id:
            # Get personal profile
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                async with session.get(
                    f"{self.base_url}/v2/profiles",
                    headers=headers
                ) as resp:
                    profiles = await resp.json()
                    if profiles:
                        self.profile_id = profiles[0].get("id")
        
        body = {
            "profile": self.profile_id,
            "sourceCurrency": from_currency,
            "targetCurrency": to_currency,
            "targetAmount" if amount_type == "target" else "sourceAmount": float(amount)
        }
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            async with session.post(
                f"{self.base_url}/v3/profiles/{self.profile_id}/quotes",
                headers=headers,
                json=body
            ) as resp:
                return await resp.json()


class OandaClient(FXProvider):
    """OANDA Forex API"""
    
    BASE_URL = "https://api-fxpractice.oanda.com"  # Practice account
    
    def __init__(self, api_key: str, account_id: str):
        super().__init__("OANDA", api_key)
        self.base_url = self.BASE_URL
        self.account_id = account_id
    
    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Get exchange rate from OANDA"""
        pair = f"{from_currency}_{to_currency}"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept-Datetime-Format": "RFC3339"
            }
            
            async with session.get(
                f"{self.base_url}/v3/instruments/{pair}/pricing",
                headers=headers
            ) as resp:
                data = await resp.json()
                prices = data.get("prices", [])
                
                if prices:
                    price = prices[0]
                    return {
                        "provider": "OANDA",
                        "from": from_currency,
                        "to": to_currency,
                        "bid": price.get("bid"),
                        "ask": price.get("ask"),
                        "spread": price.get("closeoutAsk", 0) - price.get("closeoutBid", 0)
                    }
                
                return {"error": "Rate not available"}


class ForexDotComClient(FXProvider):
    """Forex.com API"""
    
    def __init__(self, api_key: str, username: str):
        super().__init__("Forex.com", api_key)
        self.username = username
        self.session_token = None
    
    async def authenticate(self):
        """Authenticate with Forex.com"""
        # In production: OAuth or session-based auth
        self.session_token = "mock_token"
    
    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Get FX rate"""
        return {
            "provider": "Forex.com",
            "from": from_currency,
            "to": to_currency,
            "rate": 1.0850,  # Mock
            "spread": 0.0002
        }


class FiatExchangeManager:
    """
    Unified Manager for Fiat Currency Exchanges
    
    Routes transfers through best provider based on:
    - Exchange rate
    - Fees
    - Speed
    - Reliability
    """
    
    PROVIDERS = {
        "wise": WiseClient,
        "oanda": OandaClient,
        "forex_dot_com": ForexDotComClient
    }
    
    def __init__(self):
        self.clients: Dict[str, FXProvider] = {}
        self.transfer_history: List[Transfer] = []
    
    async def add_provider(
        self,
        provider_name: str,
        credentials: Dict[str, str]
    ) -> FXProvider:
        """Add FX provider"""
        client_class = self.PROVIDERS.get(provider_name)
        if not client_class:
            raise ValueError(f"Provider {provider_name} not supported")
        
        if provider_name == "wise":
            client = client_class(credentials["api_key"])
        elif provider_name == "oanda":
            client = client_class(
                credentials["api_key"],
                credentials["account_id"]
            )
        elif provider_name == "forex_dot_com":
            client = client_class(
                credentials["api_key"],
                credentials["username"]
            )
        
        self.clients[provider_name] = client
        return client
    
    async def get_best_rate(
        self,
        from_currency: str,
        to_currency: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Compare rates across all providers
        
        Returns cheapest option including all fees
        """
        quotes = []
        
        for name, client in self.clients.items():
            try:
                rate_data = await client.get_rate(from_currency, to_currency, amount)
                
                if "error" not in rate_data:
                    # Calculate total cost
                    rate = Decimal(str(rate_data.get("rate", 0)))
                    
                    # Estimate fees (varies by provider)
                    if name == "wise":
                        fee = amount * Decimal("0.005")  # ~0.5% + small fixed
                    elif name == "oanda":
                        fee = amount * Decimal("0.002")  # Spread
                    else:
                        fee = amount * Decimal("0.01")  # 1%
                    
                    received = (amount - fee) * rate
                    
                    quotes.append({
                        "provider": name,
                        "rate": float(rate),
                        "fee": float(fee),
                        "amount_received": float(received),
                        "total_cost": float(fee + (amount - (amount * rate))),
                        "speed": "1-2 days"
                    })
                    
            except Exception as e:
                print(f"Error getting rate from {name}: {e}")
        
        if not quotes:
            return {"error": "No rates available"}
        
        # Sort by best received amount
        best = max(quotes, key=lambda x: x["amount_received"])
        
        return {
            "from": from_currency,
            "to": to_currency,
            "amount": float(amount),
            "best_provider": best["provider"],
            "best_quote": best,
            "all_quotes": quotes,
            "savings": float(best["amount_received"] - min(q["amount_received"] for q in quotes))
        }
    
    async def create_transfer(
        self,
        from_currency: str,
        to_currency: str,
        amount: Decimal,
        recipient: Dict[str, Any],
        provider_preference: Optional[str] = None,
        transfer_type: TransferType = TransferType.SPOT
    ) -> Transfer:
        """
        Create fiat transfer
        
        Routes to best or preferred provider
        """
        # Get best rate
        if not provider_preference:
            best = await self.get_best_rate(from_currency, to_currency, amount)
            provider_preference = best.get("best_provider")
        
        client = self.clients.get(provider_preference)
        if not client:
            raise ValueError(f"Provider {provider_preference} not configured")
        
        # Create transfer
        transfer = Transfer(
            transfer_id=f"FX_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            from_currency=from_currency,
            to_currency=to_currency,
            amount_sent=amount,
            amount_received=Decimal("0"),  # Will be updated
            exchange_rate=Decimal("0"),
            fee=Decimal("0"),
            status="pending",
            sender_account="",
            recipient_account=recipient.get("account_number", ""),
            created_at=datetime.utcnow(),
            estimated_delivery=datetime.utcnow() + timedelta(days=2)
        )
        
        self.transfer_history.append(transfer)
        
        return transfer
    
    async def get_transfer_history(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None
    ) -> List[Transfer]:
        """Get transfer history with filters"""
        transfers = self.transfer_history
        
        if start_date:
            transfers = [t for t in transfers if t.created_at.date() >= start_date]
        
        if end_date:
            transfers = [t for t in transfers if t.created_at.date() <= end_date]
        
        if status:
            transfers = [t for t in transfers if t.status == status]
        
        return sorted(transfers, key=lambda x: x.created_at, reverse=True)
    
    async def get_supported_currencies(self) -> List[Dict[str, Any]]:
        """Get list of supported currencies"""
        currencies = [
            {"code": "USD", "name": "US Dollar", "countries": ["United States"], "popular": True},
            {"code": "EUR", "name": "Euro", "countries": ["European Union"], "popular": True},
            {"code": "GBP", "name": "British Pound", "countries": ["United Kingdom"], "popular": True},
            {"code": "JPY", "name": "Japanese Yen", "countries": ["Japan"], "popular": True},
            {"code": "CAD", "name": "Canadian Dollar", "countries": ["Canada"], "popular": True},
            {"code": "AUD", "name": "Australian Dollar", "countries": ["Australia"], "popular": True},
            {"code": "CHF", "name": "Swiss Franc", "countries": ["Switzerland"], "popular": True},
            {"code": "CNY", "name": "Chinese Yuan", "countries": ["China"], "popular": True},
            {"code": "SGD", "name": "Singapore Dollar", "countries": ["Singapore"], "popular": False},
            {"code": "HKD", "name": "Hong Kong Dollar", "countries": ["Hong Kong"], "popular": False},
            {"code": "NZD", "name": "New Zealand Dollar", "countries": ["New Zealand"], "popular": False},
            {"code": "SEK", "name": "Swedish Krona", "countries": ["Sweden"], "popular": False},
            {"code": "NOK", "name": "Norwegian Krone", "countries": ["Norway"], "popular": False},
            {"code": "MXN", "name": "Mexican Peso", "countries": ["Mexico"], "popular": False},
            {"code": "BRL", "name": "Brazilian Real", "countries": ["Brazil"], "popular": False}
        ]
        
        return currencies
    
    async def calculate_historical_savings(
        self,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Calculate savings vs traditional banks
        
        Wise/OANDA typically 5-8x cheaper than banks
        """
        # Get transfers from last N months
        cutoff = datetime.utcnow() - timedelta(days=30*months)
        transfers = [t for t in self.transfer_history if t.created_at > cutoff]
        
        total_sent = sum(t.amount_sent for t in transfers)
        total_fees = sum(t.fee for t in transfers)
        
        # Bank fees typically 3-5% for international transfers
        bank_fees_estimate = total_sent * Decimal("0.035")
        
        savings = bank_fees_estimate - total_fees
        
        return {
            "period_months": months,
            "total_transfers": len(transfers),
            "total_sent": float(total_sent),
            "fees_paid": float(total_fees),
            "bank_fees_estimate": float(bank_fees_estimate),
            "savings_vs_banks": float(savings),
            "savings_percentage": float((savings / bank_fees_estimate) * 100) if bank_fees_estimate > 0 else 0
        }
