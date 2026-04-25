"""Dividend Tracker - DRIP, dividend calendar, yield analysis"""

from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class DividendEvent:
    symbol: str
    ex_dividend_date: date
    payment_date: date
    amount_per_share: float
    dividend_type: str  # "cash", "stock_split", "special"
    currency: str = "USD"

@dataclass
class DRIPSettings:
    enabled: bool
    reinvest_all: bool = True
    symbols_to_reinvest: List[str] = None
    minimum_amount: float = 0.0
    fractional_shares: bool = True

class DividendTracker:
    """SSS-Grade dividend tracking and DRIP management"""
    
    def __init__(self, db_manager=None, broker_client=None):
        self.db = db_manager
        self.broker = broker_client
        self.dividend_calendar = {}
    
    def track_position_dividends(
        self,
        user_id: str,
        symbol: str,
        shares: float,
        drip_settings: DRIPSettings
    ) -> Dict:
        """Track upcoming dividends for a position"""
        
        # Get next dividend
        next_div = self._get_next_dividend(symbol)
        if not next_div:
            return {"symbol": symbol, "upcoming": None}
        
        estimated_dividend = shares * next_div.amount_per_share
        
        return {
            "symbol": symbol,
            "shares": shares,
            "upcoming": {
                "ex_dividend_date": next_div.ex_dividend_date.isoformat(),
                "payment_date": next_div.payment_date.isoformat(),
                "amount_per_share": next_div.amount_per_share,
                "estimated_total": estimated_dividend
            },
            "drip_enabled": drip_settings.enabled,
            "projected_shares": self._calculate_drip_shares(
                estimated_dividend,
                symbol,
                drip_settings
            ) if drip_settings.enabled else 0
        }
    
    def _get_next_dividend(self, symbol: str) -> Optional[DividendEvent]:
        """Fetch next dividend from data source"""
        # Would integrate with dividend API (IEX, Alpha Vantage, etc.)
        # Placeholder implementation
        return DividendEvent(
            symbol=symbol,
            ex_dividend_date=date.today(),
            payment_date=date.today(),
            amount_per_share=0.50,
            dividend_type="cash"
        )
    
    def _calculate_drip_shares(
        self,
        dividend_amount: float,
        symbol: str,
        settings: DRIPSettings
    ) -> float:
        """Calculate shares to purchase via DRIP"""
        if dividend_amount < settings.minimum_amount:
            return 0.0
        
        # Get current price
        current_price = self._get_price(symbol)
        if not current_price or current_price <= 0:
            return 0.0
        
        shares = dividend_amount / current_price
        
        if not settings.fractional_shares:
            shares = int(shares)
        
        return shares
    
    def _get_price(self, symbol: str) -> Optional[float]:
        """Get current stock price"""
        # Would integrate with price feed
        return 100.0  # Placeholder
    
    def get_dividend_calendar(
        self,
        user_id: str,
        month: int,
        year: int
    ) -> Dict:
        """Get dividend calendar for user"""
        if not self.db:
            return {"month": month, "year": year, "events": []}
        
        positions = self.db.get_user_positions(user_id)
        
        events = []
        for pos in positions:
            divs = self._get_dividends_for_month(
                pos["symbol"],
                month,
                year,
                pos["shares"]
            )
            events.extend(divs)
        
        # Group by date
        by_date = defaultdict(list)
        for event in events:
            by_date[event["date"]].append(event)
        
        total_estimated = sum(
            e["estimated_amount"] for e in events
        )
        
        return {
            "month": month,
            "year": year,
            "total_positions": len(positions),
            "total_estimated_dividends": round(total_estimated, 2),
            "calendar": dict(by_date)
        }
    
    def _get_dividends_for_month(
        self,
        symbol: str,
        month: int,
        year: int,
        shares: float
    ) -> List[Dict]:
        """Get dividends for symbol in month"""
        # Would query dividend database/API
        return [{
            "symbol": symbol,
            "date": f"{year}-{month:02d}-15",
            "amount_per_share": 0.50,
            "estimated_amount": round(shares * 0.50, 2)
        }]
    
    def calculate_dividend_yield(
        self,
        user_id: str
    ) -> Dict:
        """Calculate portfolio dividend yield"""
        if not self.db:
            return {}
        
        positions = self.db.get_user_positions(user_id)
        
        total_value = 0.0
        total_annual_dividends = 0.0
        by_symbol = {}
        
        for pos in positions:
            symbol = pos["symbol"]
            shares = pos.get("shares", 0)
            price = self._get_price(symbol) or 0
            value = shares * price
            
            # Get annual dividend rate
            annual_div_rate = self._get_annual_dividend_rate(symbol)
            annual_dividends = shares * annual_div_rate
            
            total_value += value
            total_annual_dividends += annual_dividends
            
            by_symbol[symbol] = {
                "shares": shares,
                "value": round(value, 2),
                "annual_dividend": round(annual_dividends, 2),
                "yield_pct": round(annual_div_rate / price * 100, 2) if price > 0 else 0
            }
        
        portfolio_yield = (
            total_annual_dividends / total_value * 100
            if total_value > 0 else 0
        )
        
        return {
            "portfolio_value": round(total_value, 2),
            "annual_dividend_income": round(total_annual_dividends, 2),
            "portfolio_yield_pct": round(portfolio_yield, 2),
            "monthly_average": round(total_annual_dividends / 12, 2),
            "by_symbol": by_symbol
        }
    
    def _get_annual_dividend_rate(self, symbol: str) -> float:
        """Get annual dividend per share"""
        # Would query dividend history
        return 2.00  # Placeholder
    
    def execute_drip(
        self,
        user_id: str,
        dividend_payment: Dict,
        settings: DRIPSettings
    ) -> Dict:
        """Execute DRIP purchase"""
        symbol = dividend_payment["symbol"]
        amount = dividend_payment["amount"]
        
        if not settings.enabled:
            return {"status": "disabled", "symbol": symbol}
        
        if settings.symbols_to_reinvest and symbol not in settings.symbols_to_reinvest:
            return {"status": "skipped", "symbol": symbol, "reason": "not in reinvest list"}
        
        if amount < settings.minimum_amount:
            return {"status": "skipped", "symbol": symbol, "reason": "below minimum"}
        
        shares = self._calculate_drip_shares(amount, symbol, settings)
        
        if shares <= 0:
            return {"status": "skipped", "symbol": symbol, "reason": "insufficient for 1 share"}
        
        # Execute purchase
        if self.broker:
            try:
                order = self.broker.place_order(
                    symbol=symbol,
                    side="BUY",
                    quantity=shares,
                    order_type="MARKET"
                )
                
                return {
                    "status": "executed",
                    "symbol": symbol,
                    "shares_purchased": shares,
                    "dividend_amount": amount,
                    "order_id": order.get("id")
                }
            except Exception as e:
                return {"status": "failed", "symbol": symbol, "error": str(e)}
        
        return {
            "status": "simulated",
            "symbol": symbol,
            "shares_purchased": shares,
            "dividend_amount": amount
        }

print("Dividend Tracker loaded - SSS-grade DRIP and dividend analysis")
