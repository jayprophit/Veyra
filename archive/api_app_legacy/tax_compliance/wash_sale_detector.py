"""Wash Sale Detector - Detect and prevent wash sale violations"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Trade:
    symbol: str
    quantity: int
    price: float
    side: str  # BUY or SELL
    date: datetime
    account: str

class WashSaleDetector:
    """Detect wash sale violations and track disallowed losses"""
    
    def __init__(self):
        self.wash_sale_window = 30  # days before and after
        self.trade_history: List[Trade] = []
        self.disallowed_losses: Dict[str, float] = {}  # Symbol -> disallowed amount
        self.substitute_securities = self._load_substitute_map()
    
    def _load_substitute_map(self) -> Dict[str, List[str]]:
        """Load map of substantially identical securities"""
        return {
            # ETFs tracking same index
            "SPY": ["VOO", "IVV", "SPYX"],  # S&P 500
            "QQQ": ["TQQQ", "SQQQ", "QQQM"],  # Nasdaq 100
            "IWM": ["TNA", "TZA", "VTWO"],  # Russell 2000
            # Sector ETFs
            "XLK": ["VGT", "FTEC", "TECL"],  # Technology
            "XLF": ["VFH", "KRE", "FAS"],   # Financials
            # Individual stocks and their substitutes
            "AAPL": ["QQQ", "VGT"],  # Not substantially identical but similar exposure
            "GOOGL": ["QQQ", "FNGU"],
        }
    
    def add_trade(self, trade: Trade):
        """Add trade to history"""
        self.trade_history.append(trade)
    
    def check_wash_sale(self, trade: Trade) -> Dict:
        """Check if trade triggers wash sale rule"""
        if trade.side != "SELL":
            return {"wash_sale": False}  # Only sales can trigger wash sale
        
        # Check for loss on this sale
        realized_loss = self._calculate_realized_loss(trade)
        if realized_loss <= 0:
            return {"wash_sale": False}  # No loss, no wash sale concern
        
        # Look for repurchase within 30 days before or after
        window_start = trade.date - timedelta(days=self.wash_sale_window)
        window_end = trade.date + timedelta(days=self.wash_sale_window)
        
        repurchases = self._find_repurchases(trade.symbol, trade.account, 
                                            window_start, window_end, 
                                            exclude_date=trade.date)
        
        if not repurchases:
            return {"wash_sale": False}
        
        # Wash sale detected
        disallowed_amount = min(realized_loss, 
                               sum(r.quantity * r.price for r in repurchases))
        
        # Track disallowed loss
        self.disallowed_losses[trade.symbol] = self.disallowed_losses.get(trade.symbol, 0) + disallowed_amount
        
        # Adjust cost basis of repurchased shares
        basis_adjustment = self._calculate_basis_adjustment(trade, repurchases, disallowed_amount)
        
        return {
            "wash_sale": True,
            "severity": "HIGH",
            "realized_loss": round(realized_loss, 2),
            "disallowed_loss": round(disallowed_amount, 2),
            "repurchase_dates": [r.date.strftime("%Y-%m-%d") for r in repurchases],
            "basis_adjustment": round(basis_adjustment, 2),
            "recommendation": "HOLD_REPLACEMENT_FOR_30_DAYS"
        }
    
    def _calculate_realized_loss(self, trade: Trade) -> float:
        """Calculate realized loss from sale"""
        # Find matching buys (FIFO assumption)
        matching_buys = [
            t for t in self.trade_history
            if t.symbol == trade.symbol 
            and t.side == "BUY"
            and t.date < trade.date
        ]
        
        if not matching_buys:
            return 0
        
        # Calculate average cost basis
        total_cost = sum(t.price * t.quantity for t in matching_buys)
        total_shares = sum(t.quantity for t in matching_buys)
        avg_cost = total_cost / total_shares if total_shares > 0 else 0
        
        realized_loss = (avg_cost - trade.price) * trade.quantity
        return max(0, realized_loss)
    
    def _find_repurchases(self, symbol: str, account: str, 
                         start: datetime, end: datetime,
                         exclude_date: datetime) -> List[Trade]:
        """Find repurchases of same or substantially identical security"""
        
        # Check exact symbol match
        matches = [t for t in self.trade_history
                  if t.symbol == symbol
                  and t.side == "BUY"
                  and start <= t.date <= end
                  and t.date != exclude_date
                  and t.account == account]
        
        # Check substitute securities
        substitutes = self.substitute_securities.get(symbol, [])
        for sub in substitutes:
            sub_matches = [t for t in self.trade_history
                        if t.symbol == sub
                        and t.side == "BUY"
                        and start <= t.date <= end
                        and t.account == account]
            matches.extend(sub_matches)
        
        return matches
    
    def _calculate_basis_adjustment(self, sale: Trade, 
                                   repurchases: List[Trade], 
                                   disallowed_amount: float) -> float:
        """Calculate new cost basis for repurchased shares"""
        if not repurchases:
            return 0
        
        total_repurchase_shares = sum(r.quantity for r in repurchases)
        if total_repurchase_shares == 0:
            return 0
        
        # Disallowed loss is added to basis of replacement shares
        adjustment_per_share = disallowed_amount / total_repurchase_shares
        
        return adjustment_per_share
    
    def get_account_summary(self, account: str) -> Dict:
        """Get wash sale summary for account"""
        account_trades = [t for t in self.trade_history if t.account == account]
        
        sales = [t for t in account_trades if t.side == "SELL"]
        
        wash_sale_count = 0
        total_disallowed = 0
        affected_symbols = set()
        
        for sale in sales:
            result = self.check_wash_sale(sale)
            if result.get("wash_sale"):
                wash_sale_count += 1
                total_disallowed += result.get("disallowed_loss", 0)
                affected_symbols.add(sale.symbol)
        
        return {
            "account": account,
            "total_trades": len(account_trades),
            "wash_sale_violations": wash_sale_count,
            "total_disallowed_losses": round(total_disallowed, 2),
            "affected_symbols": list(affected_symbols),
            "compliance_status": "CLEAN" if wash_sale_count == 0 else "VIOLATIONS_FOUND",
            "recommended_actions": [
                f"Monitor {sym} for 30-day holding period" 
                for sym in affected_symbols
            ] if affected_symbols else ["No action required"]
        }
    
    def check_portfolio_compliance(self, positions: Dict[str, int]) -> Dict:
        """Check if current positions would trigger wash sale on future sales"""
        at_risk_positions = []
        
        for symbol, quantity in positions.items():
            # Check if we have recent sales of this symbol
            recent_sales = [
                t for t in self.trade_history
                if t.symbol == symbol
                and t.side == "SELL"
                and (datetime.utcnow() - t.date).days < self.wash_sale_window
            ]
            
            if recent_sales:
                days_until_safe = self.wash_sale_window - (datetime.utcnow() - recent_sales[-1].date).days
                
                at_risk_positions.append({
                    "symbol": symbol,
                    "recent_sale_date": recent_sales[-1].date.strftime("%Y-%m-%d"),
                    "days_until_safe": days_until_safe,
                    "risk_level": "HIGH" if days_until_safe > 15 else "MEDIUM"
                })
        
        return {
            "positions_at_risk": len(at_risk_positions),
            "at_risk_details": at_risk_positions,
            "compliance_warning": len(at_risk_positions) > 0,
            "safe_to_trade_list": [
                sym for sym in positions.keys() 
                if sym not in [p["symbol"] for p in at_risk_positions]
            ]
        }
