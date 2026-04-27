"""Crypto Arbitrage Scanner - Cross-exchange price discrepancies"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CryptoQuote:
    symbol: str  # BTCUSD, ETHUSD, etc
    exchange: str
    bid: float
    ask: float
    timestamp: datetime

class CryptoArbitrageScanner:
    """Scan for crypto arbitrage across exchanges"""
    
    def __init__(self):
        self.exchanges = ["Binance", "Coinbase", "Kraken", "Bitfinex", "KuCoin", "Bybit", "OKX"]
        self.major_cryptos = ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX"]
        self.stablecoins = ["USDT", "USDC", "BUSD", "DAI"]
        self.min_profit_pct = 0.05  # 0.05% minimum
        self.quotes: Dict[str, List[CryptoQuote]] = {}
    
    def add_quote(self, quote: CryptoQuote):
        """Add crypto quote from exchange"""
        key = f"{quote.symbol}_{quote.exchange}"
        if quote.symbol not in self.quotes:
            self.quotes[quote.symbol] = []
        self.quotes[quote.symbol].append(quote)
    
    def find_spot_arbitrage(self, symbol: str) -> List[Dict]:
        """Find spot arbitrage opportunities"""
        if symbol not in self.quotes:
            return []
        
        quotes = self.quotes[symbol]
        if len(quotes) < 2:
            return []
        
        opportunities = []
        
        # Check all exchange pairs
        for i, q1 in enumerate(quotes):
            for q2 in quotes[i+1:]:
                # Buy on q2 (lower ask), sell on q1 (higher bid)
                if q1.bid > q2.ask:
                    gross_profit = q1.bid - q2.ask
                    profit_pct = gross_profit / q2.ask * 100
                    
                    # Account for fees (0.1% typical)
                    fee_cost = q2.ask * 0.001 + q1.bid * 0.001
                    net_profit = gross_profit - fee_cost
                    net_profit_pct = net_profit / q2.ask * 100
                    
                    if net_profit_pct > self.min_profit_pct:
                        opportunities.append({
                            "symbol": symbol,
                            "type": "SPOT_ARBITRAGE",
                            "buy_exchange": q2.exchange,
                            "buy_price": q2.ask,
                            "sell_exchange": q1.exchange,
                            "sell_price": q1.bid,
                            "gross_profit_pct": round(profit_pct, 3),
                            "net_profit_pct": round(net_profit_pct, 3),
                            "profit_per_unit": round(net_profit, 4),
                            "confidence": "HIGH" if net_profit_pct > 0.2 else "MEDIUM",
                            "speed_required": "FAST" if net_profit_pct < 0.1 else "NORMAL"
                        })
        
        return sorted(opportunities, key=lambda x: x["net_profit_pct"], reverse=True)
    
    def find_stablecoin_arbitrage(self) -> List[Dict]:
        """Find stablecoin peg arbitrage"""
        opportunities = []
        
        for stable in self.stablecoins:
            symbol = f"{stable}USD"
            if symbol not in self.quotes:
                continue
            
            quotes = self.quotes[symbol]
            
            for q in quotes:
                # Check if deviated from $1.00 peg
                mid_price = (q.bid + q.ask) / 2
                deviation = abs(mid_price - 1.0)
                
                if deviation > 0.002:  # 0.2% deviation
                    direction = "PREMIUM" if mid_price > 1.0 else "DISCOUNT"
                    
                    opportunities.append({
                        "stablecoin": stable,
                        "exchange": q.exchange,
                        "price": round(mid_price, 4),
                        "deviation_from_peg": round(deviation * 100, 2),
                        "direction": direction,
                        "trade": f"SELL_{stable}" if direction == "PREMIUM" else f"BUY_{stable}",
                        "expected_return": round(deviation * 100 - 0.1, 2),  # minus fees
                        "risk": "LOW" if stable in ["USDC", "DAI"] else "MEDIUM"
                    })
        
        return sorted(opportunities, key=lambda x: x["deviation_from_peg"], reverse=True)
    
    def calculate_funding_arbitrage(self, 
                                  perp_funding_rates: Dict[str, float],
                                  spot_prices: Dict[str, float]) -> List[Dict]:
        """Calculate funding rate arbitrage (perp vs spot)"""
        opportunities = []
        
        for symbol in perp_funding_rates:
            funding = perp_funding_rates[symbol]
            
            # High positive funding = short perp, long spot
            # High negative funding = long perp, short spot
            
            if abs(funding) > 0.0001:  # > 0.01% per 8 hours
                annualized = funding * 3 * 365  # 3 periods per day
                
                direction = "SHORT_PERP_LONG_SPOT" if funding > 0 else "LONG_PERP_SHORT_SPOT"
                
                opportunities.append({
                    "symbol": symbol,
                    "type": "FUNDING_ARBITRAGE",
                    "direction": direction,
                    "funding_rate_8h": round(funding * 100, 4),
                    "annualized_return": round(annualized * 100, 2),
                    "risk_level": "LOW" if abs(annualized) > 0.15 else "MEDIUM",
                    "complexity": "MEDIUM",
                    "capital_required": "HIGH"  # Requires both spot and perp positions
                })
        
        return sorted(opportunities, key=lambda x: abs(x["annualized_return"]), reverse=True)
    
    def get_exchange_spread_comparison(self, symbol: str) -> Dict:
        """Compare spreads across exchanges"""
        if symbol not in self.quotes:
            return {"error": "No data"}
        
        quotes = self.quotes[symbol]
        
        spread_data = []
        for q in quotes:
            spread = q.ask - q.bid
            spread_pct = spread / ((q.bid + q.ask) / 2) * 100
            
            spread_data.append({
                "exchange": q.exchange,
                "bid": q.bid,
                "ask": q.ask,
                "spread": round(spread, 4),
                "spread_pct": round(spread_pct, 3)
            })
        
        spread_data.sort(key=lambda x: x["spread_pct"])
        
        return {
            "symbol": symbol,
            "best_liquidity": spread_data[0]["exchange"],
            "tightest_spread": spread_data[0]["spread_pct"],
            "widest_spread": spread_data[-1]["spread_pct"],
            "spread_comparison": spread_data
        }
    
    def scan_all_opportunities(self) -> Dict:
        """Scan all crypto for arbitrage"""
        all_spot = []
        stable = []
        
        for crypto in self.major_cryptos:
            symbol = f"{crypto}USD"
            all_spot.extend(self.find_spot_arbitrage(symbol))
        
        stable = self.find_stablecoin_arbitrage()
        
        return {
            "spot_arbitrage": all_spot[:10],
            "stablecoin_arbitrage": stable[:5],
            "total_opportunities": len(all_spot) + len(stable),
            "highest_profit": max(
                [x["net_profit_pct"] for x in all_spot] + [0]
            ),
            "last_scan": datetime.utcnow().isoformat()
        }
