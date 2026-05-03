"""Exchange Rate Management"""
from datetime import datetime, timedelta
from typing import Dict, Optional

class ExchangeRateManager:
    BASE_CURRENCY = "USD"
    CURRENCIES = {
        "USD": {"name": "US Dollar", "symbol": "$", "decimals": 2},
        "EUR": {"name": "Euro", "symbol": "€", "decimals": 2},
        "GBP": {"name": "British Pound", "symbol": "£", "decimals": 2},
        "JPY": {"name": "Japanese Yen", "symbol": "¥", "decimals": 0},
        "CAD": {"name": "Canadian Dollar", "symbol": "C$", "decimals": 2},
        "AUD": {"name": "Australian Dollar", "symbol": "A$", "decimals": 2},
    }
    
    def __init__(self):
        self._rates: Dict[str, float] = {}
        self._last_update: Optional[datetime] = None
        self._initialize_default_rates()
    
    def _initialize_default_rates(self):
        self._rates = {
            "USD": 1.0, "EUR": 0.85, "GBP": 0.73, "JPY": 110.0,
            "CAD": 1.25, "AUD": 1.35, "CHF": 0.92, "CNY": 6.45
        }
        self._last_update = datetime.now()
    
    def get_rate(self, currency: str) -> float:
        return self._rates.get(currency, 1.0)
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return amount
        from_rate = self.get_rate(from_currency)
        to_rate = self.get_rate(to_currency)
        usd_amount = amount / from_rate
        return usd_amount * to_rate
    
    def format_currency(self, amount: float, currency: str) -> str:
        info = self.CURRENCIES.get(currency, self.CURRENCIES["USD"])
        symbol = info["symbol"]
        decimals = info["decimals"]
        return f"{symbol}{amount:,.{decimals}f}"

class CurrencyConverter:
    def __init__(self):
        self.manager = ExchangeRateManager()
    
    def convert_transaction(self, amount: float, currency: str, base_currency: str = "USD") -> Dict:
        converted = self.manager.convert(amount, currency, base_currency)
        return {
            "original_amount": amount,
            "original_currency": currency,
            "converted_amount": round(converted, 2),
            "target_currency": base_currency,
            "exchange_rate": self.manager.get_rate(currency) / self.manager.get_rate(base_currency),
            "formatted": self.manager.format_currency(converted, base_currency)
        }
