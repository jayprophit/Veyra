"""Liquidity Aggregation for Best Execution."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class LiquiditySource:
    exchange: str
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    latency_ms: float
    fees_maker: float
    fees_taker: float
    last_updated: datetime

@dataclass
class AggregatedQuote:
    symbol: str
    best_bid: float
    best_ask: float
    best_bid_exchange: str
    best_ask_exchange: str
    total_bid_liquidity: float
    total_ask_liquidity: float
    spread: float
    effective_price: float
    sources: List[LiquiditySource]

class LiquidityAggregator:
    """Aggregates liquidity from multiple exchanges for best execution."""
    
    def __init__(self):
        self.sources: Dict[str, List[LiquiditySource]] = {}
        self.exchange_weights: Dict[str, float] = {
            'binance': 0.3,
            'coinbase': 0.25,
            'kraken': 0.2,
            'ftx': 0.15,
            'other': 0.1
        }
        self.min_liquidity_threshold = 1000  # Minimum $1k liquidity
        self.max_latency_ms = 500
    
    async def add_source(self, symbol: str, source: LiquiditySource):
        """Add or update liquidity source."""
        if symbol not in self.sources:
            self.sources[symbol] = []
        
        # Update existing or add new
        existing = [s for s in self.sources[symbol] if s.exchange == source.exchange]
        if existing:
            self.sources[symbol].remove(existing[0])
        
        self.sources[symbol].append(source)
        
        # Remove stale sources
        self.sources[symbol] = [
            s for s in self.sources[symbol]
            if (datetime.now() - s.last_updated).seconds < 30
        ]
    
    async def get_best_quote(self, symbol: str, side: str, 
                            size: float) -> Optional[AggregatedQuote]:
        """Get best aggregated quote for a trade."""
        if symbol not in self.sources:
            return None
        
        sources = self.sources[symbol]
        
        if side == 'buy':
            # Sort by lowest ask
            sorted_sources = sorted(sources, key=lambda s: s.ask)
            best = sorted_sources[0] if sorted_sources else None
            
            if not best:
                return None
            
            # Calculate effective price across multiple exchanges if needed
            remaining_size = size
            total_cost = 0
            used_exchanges = []
            
            for src in sorted_sources:
                if remaining_size <= 0:
                    break
                
                available = src.ask_size
                take_size = min(remaining_size, available)
                
                # Add taker fee
                fee = src.ask * take_size * src.fees_taker
                total_cost += (src.ask * take_size) + fee
                remaining_size -= take_size
                used_exchanges.append(src.exchange)
            
            if remaining_size > 0:
                logger.warning(f"Insufficient liquidity for {symbol} {side} {size}")
            
            effective_price = total_cost / size if size > 0 else best.ask
            
            return AggregatedQuote(
                symbol=symbol,
                best_bid=max(s.bid for s in sources),
                best_ask=best.ask,
                best_bid_exchange=max(sources, key=lambda s: s.bid).exchange,
                best_ask_exchange=best.exchange,
                total_bid_liquidity=sum(s.bid_size for s in sources),
                total_ask_liquidity=sum(s.ask_size for s in sources),
                spread=best.ask - max(s.bid for s in sources),
                effective_price=effective_price,
                sources=sources
            )
        
        else:  # sell
            # Sort by highest bid
            sorted_sources = sorted(sources, key=lambda s: s.bid, reverse=True)
            best = sorted_sources[0] if sorted_sources else None
            
            if not best:
                return None
            
            remaining_size = size
            total_proceeds = 0
            
            for src in sorted_sources:
                if remaining_size <= 0:
                    break
                
                available = src.bid_size
                take_size = min(remaining_size, available)
                
                fee = src.bid * take_size * src.fees_taker
                total_proceeds += (src.bid * take_size) - fee
                remaining_size -= take_size
            
            effective_price = total_proceeds / size if size > 0 else best.bid
            
            return AggregatedQuote(
                symbol=symbol,
                best_bid=best.bid,
                best_ask=min(s.ask for s in sources),
                best_bid_exchange=best.exchange,
                best_ask_exchange=min(sources, key=lambda s: s.ask).exchange,
                total_bid_liquidity=sum(s.bid_size for s in sources),
                total_ask_liquidity=sum(s.ask_size for s in sources),
                spread=min(s.ask for s in sources) - best.bid,
                effective_price=effective_price,
                sources=sources
            )
    
    async def smart_routing(self, symbol: str, side: str, 
                           size: float) -> Dict[str, Any]:
        """Smart order routing across exchanges."""
        quote = await self.get_best_quote(symbol, side, size)
        
        if not quote:
            return {'error': 'No liquidity available'}
        
        # Build routing plan
        routes = []
        remaining = size
        
        sources = sorted(quote.sources, 
                        key=lambda s: s.ask if side == 'buy' else -s.bid)
        
        for src in sources:
            if remaining <= 0:
                break
            
            available = src.ask_size if side == 'buy' else src.bid_size
            route_size = min(remaining, available * 0.95)  # Leave some buffer
            
            price = src.ask if side == 'buy' else src.bid
            fee = price * route_size * src.fees_taker
            
            routes.append({
                'exchange': src.exchange,
                'size': route_size,
                'price': price,
                'fee': fee,
                'net_price': price + fee/route_size if side == 'buy' else price - fee/route_size
            })
            
            remaining -= route_size
        
        return {
            'symbol': symbol,
            'side': side,
            'total_size': size,
            'effective_price': quote.effective_price,
            'routes': routes,
            'route_count': len(routes),
            'savings_vs_single_exchange': self._calculate_savings(symbol, side, size, quote.effective_price)
        }
    
    def _calculate_savings(self, symbol: str, side: str, size: float, 
                          effective_price: float) -> float:
        """Calculate savings vs using single worst exchange."""
        if symbol not in self.sources:
            return 0.0
        
        sources = self.sources[symbol]
        
        if side == 'buy':
            worst_price = max(s.ask for s in sources)
        else:
            worst_price = min(s.bid for s in sources)
        
        savings = abs(worst_price - effective_price) * size
        return savings
    
    async def update_all_sources(self, market_data: Dict[str, List[Dict]]):
        """Batch update all liquidity sources."""
        for symbol, exchanges in market_data.items():
            for ex_data in exchanges:
                source = LiquiditySource(
                    exchange=ex_data['exchange'],
                    bid=ex_data['bid'],
                    ask=ex_data['ask'],
                    bid_size=ex_data['bid_size'],
                    ask_size=ex_data['ask_size'],
                    latency_ms=ex_data.get('latency', 100),
                    fees_maker=ex_data.get('fees_maker', 0.001),
                    fees_taker=ex_data.get('fees_taker', 0.002),
                    last_updated=datetime.now()
                )
                await self.add_source(symbol, source)

liquidity_aggregator = LiquidityAggregator()
