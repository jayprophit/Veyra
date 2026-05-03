"""Trading Journal for Performance Analysis."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class JournalEntry:
    entry_id: str
    user_id: str
    trade_id: str
    symbol: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    side: str
    entry_date: datetime
    exit_date: Optional[datetime]
    pnl: Optional[float]
    strategy_used: str
    emotions: str
    lessons: str
    tags: List[str]
    screenshot_url: Optional[str]
    market_conditions: str
    notes: str

class TradingJournal:
    """AI-enhanced trading journal for continuous improvement."""
    
    def __init__(self):
        self.entries: Dict[str, JournalEntry] = {}
        self.user_entries: Dict[str, List[str]] = defaultdict(list)
        self.strategy_performance: Dict[str, Dict] = defaultdict(lambda: {
            'trades': 0, 'wins': 0, 'losses': 0, 'total_pnl': 0
        })
        self.entry_counter = 0
    
    def _generate_id(self) -> str:
        self.entry_counter += 1
        return f"journal_{self.entry_counter}_{datetime.now().strftime('%H%M%S')}"
    
    async def create_entry(self, user_id: str, trade_data: Dict, 
                          reflection: Dict) -> JournalEntry:
        """Create a new journal entry."""
        entry_id = self._generate_id()
        
        entry = JournalEntry(
            entry_id=entry_id,
            user_id=user_id,
            trade_id=trade_data['trade_id'],
            symbol=trade_data['symbol'],
            entry_price=trade_data['entry_price'],
            exit_price=trade_data.get('exit_price'),
            quantity=trade_data['quantity'],
            side=trade_data['side'],
            entry_date=trade_data['entry_date'],
            exit_date=trade_data.get('exit_date'),
            pnl=trade_data.get('pnl'),
            strategy_used=reflection.get('strategy', 'unknown'),
            emotions=reflection.get('emotions', 'neutral'),
            lessons=reflection.get('lessons', ''),
            tags=reflection.get('tags', []),
            screenshot_url=reflection.get('screenshot'),
            market_conditions=reflection.get('market_conditions', ''),
            notes=reflection.get('notes', '')
        )
        
        self.entries[entry_id] = entry
        self.user_entries[user_id].append(entry_id)
        
        # Update strategy performance
        strat = entry.strategy_used
        self.strategy_performance[strat]['trades'] += 1
        if entry.pnl and entry.pnl > 0:
            self.strategy_performance[strat]['wins'] += 1
        elif entry.pnl and entry.pnl < 0:
            self.strategy_performance[strat]['losses'] += 1
        self.strategy_performance[strat]['total_pnl'] += (entry.pnl or 0)
        
        logger.info(f"Journal entry created: {entry_id}")
        return entry
    
    async def get_entries(self, user_id: str, 
                         filters: Optional[Dict] = None) -> List[Dict]:
        """Get journal entries with filtering."""
        entry_ids = self.user_entries.get(user_id, [])
        entries = [self.entries[eid] for eid in entry_ids if eid in self.entries]
        
        if filters:
            if 'symbol' in filters:
                entries = [e for e in entries if e.symbol == filters['symbol']]
            if 'strategy' in filters:
                entries = [e for e in entries if e.strategy_used == filters['strategy']]
            if 'start_date' in filters:
                entries = [e for e in entries if e.entry_date >= filters['start_date']]
            if 'end_date' in filters:
                entries = [e for e in entries if e.entry_date <= filters['end_date']]
            if 'tag' in filters:
                entries = [e for e in entries if filters['tag'] in e.tags]
        
        return [{
            'entry_id': e.entry_id,
            'trade_id': e.trade_id,
            'symbol': e.symbol,
            'side': e.side,
            'pnl': e.pnl,
            'strategy': e.strategy_used,
            'emotions': e.emotions,
            'lessons': e.lessons,
            'tags': e.tags,
            'entry_date': e.entry_date.isoformat(),
            'exit_date': e.exit_date.isoformat() if e.exit_date else None
        } for e in entries]
    
    async def get_performance_stats(self, user_id: str) -> Dict[str, Any]:
        """Get trading performance statistics."""
        entries = [self.entries[eid] for eid in self.user_entries.get(user_id, [])
                   if eid in self.entries]
        
        if not entries:
            return {'total_trades': 0}
        
        trades_with_pnl = [e for e in entries if e.pnl is not None]
        
        wins = sum(1 for e in trades_with_pnl if e.pnl > 0)
        losses = sum(1 for e in trades_with_pnl if e.pnl < 0)
        total = len(trades_with_pnl)
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        total_pnl = sum(e.pnl for e in trades_with_pnl)
        
        winning_trades = [e.pnl for e in trades_with_pnl if e.pnl > 0]
        losing_trades = [e.pnl for e in trades_with_pnl if e.pnl < 0]
        
        avg_win = sum(winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(losing_trades) / len(losing_trades) if losing_trades else 0
        
        profit_factor = abs(sum(winning_trades) / sum(losing_trades)) if losing_trades and sum(losing_trades) != 0 else float('inf')
        
        # By strategy
        by_strategy = {}
        for e in entries:
            strat = e.strategy_used
            if strat not in by_strategy:
                by_strategy[strat] = {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0}
            by_strategy[strat]['trades'] += 1
            if e.pnl:
                by_strategy[strat]['pnl'] += e.pnl
                if e.pnl > 0:
                    by_strategy[strat]['wins'] += 1
                else:
                    by_strategy[strat]['losses'] += 1
        
        return {
            'user_id': user_id,
            'total_trades': len(entries),
            'trades_with_pnl': total,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'wins': wins,
            'losses': losses,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'by_strategy': by_strategy,
            'common_emotions': self._get_common_emotions(entries),
            'common_lessons': self._get_common_lessons(entries)
        }
    
    def _get_common_emotions(self, entries: List[JournalEntry]) -> Dict[str, int]:
        """Analyze emotional patterns."""
        emotions = defaultdict(int)
        for e in entries:
            emotions[e.emotions] += 1
        return dict(emotions)
    
    def _get_common_lessons(self, entries: List[JournalEntry]) -> List[str]:
        """Extract recurring lessons."""
        lessons = [e.lessons for e in entries if e.lessons]
        # Simple frequency analysis
        from collections import Counter
        words = ' '.join(lessons).lower().split()
        return [word for word, count in Counter(words).most_common(10) if len(word) > 3]
    
    async def generate_insights(self, user_id: str) -> List[str]:
        """Generate AI insights from trading patterns."""
        stats = await self.get_performance_stats(user_id)
        insights = []
        
        if stats['win_rate'] < 50:
            insights.append("Consider reviewing your entry criteria - win rate is below 50%")
        
        if stats.get('profit_factor', 0) < 1.5:
            insights.append("Your profit factor is low. Focus on cutting losses faster.")
        
        # Strategy insights
        for strategy, data in stats.get('by_strategy', {}).items():
            if data['trades'] > 5 and data['pnl'] < 0:
                insights.append(f"Strategy '{strategy}' is underperforming. Consider optimization.")
            if data['trades'] > 5 and data['pnl'] > 0:
                win_rate_strat = data['wins'] / data['trades'] * 100
                if win_rate_strat > 60:
                    insights.append(f"Strategy '{strategy}' shows strong performance ({win_rate_strat:.1f}% win rate)")
        
        return insights

trading_journal = TradingJournal()
