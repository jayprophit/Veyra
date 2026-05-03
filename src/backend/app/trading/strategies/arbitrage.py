"""
Cross-Exchange Arbitrage Strategy
Buy low on one exchange, sell high on another
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class ArbitrageOpportunity:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    profit_pct: float
    profit_amount: float
    timestamp: datetime

class ArbitrageStrategy:
    """
    Automated cross-exchange arbitrage trading
    """
    
    def __init__(self, min_profit_pct: float = 1.5, safety_margin: float = 2.5):
        self.min_profit_pct = min_profit_pct
        self.safety_margin = safety_margin  # Account for fees/slippage
        self.active = False
        self.exchanges: Dict[str, any] = {}  # Exchange connectors
        self.opportunities: List[ArbitrageOpportunity] = []
        self.trade_history: List[Dict] = []
    
    def add_exchange(self, name: str, connector):
        """Add an exchange connector"""
        self.exchanges[name] = connector
    
    async def scan_opportunities(self, symbols: List[str]) -> List[ArbitrageOpportunity]:
        """Scan for arbitrage opportunities across exchanges"""
        opportunities = []
        
        for symbol in symbols:
            # Get prices from all exchanges
            prices = {}
            for name, exchange in self.exchanges.items():
                try:
                    price = await exchange.get_price(symbol)
                    prices[name] = price
                except Exception as e:
                    print(f"Error getting price from {name}: {e}")
            
            # Find arbitrage opportunities
            if len(prices) >= 2:
                for buy_ex, buy_price in prices.items():
                    for sell_ex, sell_price in prices.items():
                        if buy_ex != sell_ex:
                            profit_pct = ((sell_price - buy_price) / buy_price) * 100
                            
                            if profit_pct > self.min_profit_pct + self.safety_margin:
                                opp = ArbitrageOpportunity(
                                    symbol=symbol,
                                    buy_exchange=buy_ex,
                                    sell_exchange=sell_ex,
                                    buy_price=buy_price,
                                    sell_price=sell_price,
                                    profit_pct=profit_pct,
                                    profit_amount=sell_price - buy_price,
                                    timestamp=datetime.now()
                                )
                                opportunities.append(opp)
        
        self.opportunities = sorted(opportunities, key=lambda x: x.profit_pct, reverse=True)
        return self.opportunities
    
    async def execute_arbitrage(self, opportunity: ArbitrageOpportunity, 
                                quantity: float) -> Optional[Dict]:
        """Execute an arbitrage trade"""
        try:
            # Step 1: Buy on lower-priced exchange
            buy_exchange = self.exchanges[opportunity.buy_exchange]
            buy_order = await buy_exchange.place_order(
                symbol=opportunity.symbol,
                side='buy',
                quantity=quantity,
                price=opportunity.buy_price
            )
            
            # Step 2: Sell on higher-priced exchange
            sell_exchange = self.exchanges[opportunity.sell_exchange]
            sell_order = await sell_exchange.place_order(
                symbol=opportunity.symbol,
                side='sell',
                quantity=quantity,
                price=opportunity.sell_price
            )
            
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'symbol': opportunity.symbol,
                'buy_exchange': opportunity.buy_exchange,
                'sell_exchange': opportunity.sell_exchange,
                'buy_price': opportunity.buy_price,
                'sell_price': opportunity.sell_price,
                'quantity': quantity,
                'profit': (opportunity.sell_price - opportunity.buy_price) * quantity,
                'profit_pct': opportunity.profit_pct,
                'buy_order_id': buy_order.get('id'),
                'sell_order_id': sell_order.get('id'),
                'status': 'completed'
            }
            
            self.trade_history.append(trade_record)
            return trade_record
            
        except Exception as e:
            print(f"Arbitrage execution failed: {e}")
            return None
    
    async def run_automatic(self, symbols: List[str], check_interval: int = 60):
        """Run automatic arbitrage detection and execution"""
        self.active = True
        
        while self.active:
            try:
                opportunities = await self.scan_opportunities(symbols)
                
                if opportunities:
                    best = opportunities[0]
                    print(f"Found arbitrage: {best.symbol} {best.profit_pct:.2f}% profit")
                    
                    # Execute if profit is significant
                    if best.profit_pct > self.min_profit_pct * 2:
                        await self.execute_arbitrage(best, quantity=1.0)
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"Error in arbitrage loop: {e}")
                await asyncio.sleep(check_interval)
    
    def stop(self):
        """Stop automatic trading"""
        self.active = False
    
    def get_statistics(self) -> Dict:
        """Get arbitrage trading statistics"""
        if not self.trade_history:
            return {"total_trades": 0, "total_profit": 0}
        
        total_profit = sum(t['profit'] for t in self.trade_history)
        profitable_trades = len([t for t in self.trade_history if t['profit'] > 0])
        
        return {
            "total_trades": len(self.trade_history),
            "profitable_trades": profitable_trades,
            "total_profit": round(total_profit, 2),
            "avg_profit_per_trade": round(total_profit / len(self.trade_history), 2),
            "success_rate": round((profitable_trades / len(self.trade_history)) * 100, 1)
        }
