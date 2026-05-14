"""
Behavioral Analytics System
=============================
Track trader psychology and behavioral patterns
Detect overtrading, FOMO, revenge trading, loss aversion
Gamification, streaks, achievements
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BehaviorPattern(Enum):
    OVERTRADING = "overtrading"
    FOMO = "fomo"  # Fear of missing out
    REVENGE_TRADING = "revenge_trading"
    LOSS_AVERSION = "loss_aversion"
    OVERCONFIDENCE = "overconfidence"
    ANALYSIS_PARALYSIS = "analysis_paralysis"
    PREMATURE_EXIT = "premature_exit"


@dataclass
class BehaviorAlert:
    pattern: str
    severity: str  # 'low', 'medium', 'high'
    description: str
    recommendation: str
    timestamp: datetime


@dataclass
class Achievement:
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_date: Optional[datetime]
    progress: float  # 0-100


class BehavioralAnalytics:
    """
    Analyze trader behavior and psychology
    
    Features:
    - Behavioral pattern detection
    - Trading psychology scoring
    - Gamification and achievements
    - Improvement recommendations
    """
    
    def __init__(self, trader_id: str = "default"):
        self.trader_id = trader_id
        self.trades_history: List[Dict] = []
        self.alerts: List[BehaviorAlert] = []
        self.achievements: Dict[str, Achievement] = self._init_achievements()
        self.streaks = {
            'winning_days': 0,
            'positive_expectancy': 0,
            'no_overtrading': 0,
            'discipline': 0
        }
    
    def _init_achievements(self) -> Dict[str, Achievement]:
        """Initialize achievement system"""
        return {
            'first_profit': Achievement(
                'First Blood', 'Make your first profitable trade', '🎯', 
                False, None, 0
            ),
            'first_100': Achievement(
                'Centurion', 'Make $100 in a single trade', '💯',
                False, None, 0
            ),
            'first_1000': Achievement(
                'Grand Slam', 'Make $1,000 in a single trade', '🚀',
                False, None, 0
            ),
            'winning_streak_5': Achievement(
                'On Fire', '5 consecutive winning trades', '🔥',
                False, None, 0
            ),
            'winning_streak_10': Achievement(
                'Legendary', '10 consecutive winning trades', '👑',
                False, None, 0
            ),
            'sharpe_above_2': Achievement(
                'Sharpe Shooter', 'Achieve Sharpe ratio > 2.0', '🎯',
                False, None, 0
            ),
            'diversified': Achievement(
                'Diversification King', 'Trade 10+ different assets', '🌍',
                False, None, 0
            ),
            'risk_manager': Achievement(
                'Risk Manager', '100 trades with positive expectancy', '🛡️',
                False, None, 0
            ),
            'patient_trader': Achievement(
                'Zen Master', 'Hold winning trade for > 30 days', '🧘',
                False, None, 0
            ),
            'tax_optimizer': Achievement(
                'Tax Ninja', 'Save $1,000+ with tax-loss harvesting', '🥷',
                False, None, 0
            ),
            '100_trades': Achievement(
                'Century', 'Complete 100 trades', '⚡',
                False, None, 0
            ),
            '500_trades': Achievement(
                'Veteran', 'Complete 500 trades', '🎖️',
                False, None, 0
            ),
            'profit_10k': Achievement(
                'Ten Thousand Club', 'Cumulative profit $10,000', '💰',
                False, None, 0
            ),
            'profit_100k': Achievement(
                'Six Figures', 'Cumulative profit $100,000', '🏆',
                False, None, 0
            ),
            'market_crash_survivor': Achievement(
                'Survivor', 'Profit during a market crash', '🦾',
                False, None, 0
            ),
            'short_squeeze_winner': Achievement(
                'Squeeze Player', 'Profit from a short squeeze', '🩳',
                False, None, 0
            ),
        }
    
    def add_trade(self, trade: Dict):
        """Add trade to history and check for patterns"""
        self.trades_history.append({
            **trade,
            'timestamp': datetime.now()
        })
        
        # Update achievements
        self._check_achievements()
        
        # Check for behavioral issues
        self._detect_patterns()
    
    def _detect_patterns(self):
        """Detect behavioral patterns in trading"""
        if len(self.trades_history) < 5:
            return
        
        recent = self.trades_history[-20:]
        
        # 1. Overtrading Detection
        trades_today = len([t for t in recent 
                           if t['timestamp'].date() == datetime.now().date()])
        if trades_today > 10:
            self.alerts.append(BehaviorAlert(
                pattern=BehaviorPattern.OVERTRADING.value,
                severity='high',
                description=f'{trades_today} trades today. Normal is 2-3.',
                recommendation='Take a break. Set max 5 trades/day rule.',
                timestamp=datetime.now()
            ))
        
        # 2. Revenge Trading (trading immediately after loss)
        if len(recent) >= 2:
            last_trade = recent[-1]
            prev_trade = recent[-2]
            
            if (prev_trade.get('pnl', 0) < 0 and 
                (last_trade['timestamp'] - prev_trade['timestamp']) < timedelta(minutes=5)):
                self.alerts.append(BehaviorAlert(
                    pattern=BehaviorPattern.REVENGE_TRADING.value,
                    severity='high',
                    description='Trade entered <5 min after loss. Emotional decision.',
                    recommendation='Wait 1 hour after loss before next trade.',
                    timestamp=datetime.now()
                ))
        
        # 3. FOMO Detection (chasing after big moves)
        if len(recent) >= 1:
            last_trade = recent[-1]
            if last_trade.get('entry_reason') == 'chase':
                self.alerts.append(BehaviorAlert(
                    pattern=BehaviorPattern.FOMO.value,
                    severity='medium',
                    description='Chasing momentum without plan.',
                    recommendation='Set entry criteria. No FOMO trades.',
                    timestamp=datetime.now()
                ))
        
        # 4. Loss Aversion (holding losers too long)
        open_losses = [t for t in self.trades_history 
                      if t.get('status') == 'open' and t.get('unrealized_pnl', 0) < -0.05]
        if len(open_losses) > 0:
            for trade in open_losses:
                days_held = (datetime.now() - trade['timestamp']).days
                if days_held > 5:
                    self.alerts.append(BehaviorAlert(
                        pattern=BehaviorPattern.LOSS_AVERSION.value,
                        severity='medium',
                        description=f'Holding {trade["ticker"]} loss for {days_held} days.',
                        recommendation='Cut losses at -5%. Use stop losses.',
                        timestamp=datetime.now()
                    ))
        
        # 5. Overconfidence (position sizing too large)
        recent_sizes = [t.get('position_size', 0) for t in recent[-5:]]
        avg_size = np.mean(recent_sizes)
        if avg_size > 50000:  # $50k+ positions
            self.alerts.append(BehaviorAlert(
                pattern=BehaviorPattern.OVERCONFIDENCE.value,
                severity='medium',
                description=f'Large positions: ${avg_size:,.0f} average.',
                recommendation='Reduce to <5% portfolio per trade.',
                timestamp=datetime.now()
            ))
        
        # Keep only last 10 alerts
        self.alerts = self.alerts[-10:]
    
    def _check_achievements(self):
        """Check and update achievements"""
        if not self.trades_history:
            return
        
        # First profit
        profits = [t for t in self.trades_history if t.get('pnl', 0) > 0]
        if profits and not self.achievements['first_profit'].unlocked:
            self._unlock_achievement('first_profit')
        
        # $100 profit
        if any(t.get('pnl', 0) >= 100 for t in profits):
            if not self.achievements['first_100'].unlocked:
                self._unlock_achievement('first_100')
        
        # $1000 profit
        if any(t.get('pnl', 0) >= 1000 for t in profits):
            if not self.achievements['first_1000'].unlocked:
                self._unlock_achievement('first_1000')
        
        # Winning streak
        closed_trades = [t for t in self.trades_history if t.get('status') == 'closed']
        wins = [t for t in closed_trades if t.get('pnl', 0) > 0]
        
        if len(wins) >= 5 and not self.achievements['winning_streak_5'].unlocked:
            self._unlock_achievement('winning_streak_5')
        
        if len(wins) >= 10 and not self.achievements['winning_streak_10'].unlocked:
            self._unlock_achievement('winning_streak_10')
        
        # Trade count achievements
        if len(closed_trades) >= 100 and not self.achievements['100_trades'].unlocked:
            self._unlock_achievement('100_trades')
        
        if len(closed_trades) >= 500 and not self.achievements['500_trades'].unlocked:
            self._unlock_achievement('500_trades')
        
        # Total profit
        total_profit = sum(t.get('pnl', 0) for t in profits)
        if total_profit >= 10000 and not self.achievements['profit_10k'].unlocked:
            self._unlock_achievement('profit_10k')
        
        if total_profit >= 100000 and not self.achievements['profit_100k'].unlocked:
            self._unlock_achievement('profit_100k')
        
        # Diversification
        tickers = set(t.get('ticker') for t in self.trades_history)
        if len(tickers) >= 10 and not self.achievements['diversified'].unlocked:
            self._unlock_achievement('diversified')
    
    def _unlock_achievement(self, achievement_id: str):
        """Unlock an achievement"""
        achievement = self.achievements[achievement_id]
        achievement.unlocked = True
        achievement.unlocked_date = datetime.now()
        achievement.progress = 100
        logger.info(f"Achievement unlocked: {achievement.name}")
    
    def get_behavioral_score(self) -> Dict:
        """Calculate overall behavioral health score"""
        if not self.trades_history:
            return {'score': 50, 'status': 'insufficient_data'}
        
        # Calculate components
        scores = {
            'discipline': 100 - min(len(self.alerts) * 10, 50),  # Fewer alerts = better
            'consistency': self._calculate_consistency(),
            'risk_management': self._calculate_risk_score(),
            'emotional_control': self._calculate_emotional_score(),
            'learning': self._calculate_learning_score()
        }
        
        # Weighted average
        weights = {
            'discipline': 0.25,
            'consistency': 0.20,
            'risk_management': 0.25,
            'emotional_control': 0.20,
            'learning': 0.10
        }
        
        overall = sum(scores[k] * weights[k] for k in scores)
        
        return {
            'overall_score': round(overall, 1),
            'component_scores': scores,
            'status': self._score_to_status(overall),
            'top_strength': max(scores, key=scores.get),
            'improvement_area': min(scores, key=scores.get)
        }
    
    def _calculate_consistency(self) -> float:
        """Calculate trading consistency score"""
        if len(self.trades_history) < 10:
            return 50
        
        # Win rate consistency
        closed = [t for t in self.trades_history if t.get('status') == 'closed']
        if not closed:
            return 50
        
        wins = len([t for t in closed if t.get('pnl', 0) > 0])
        win_rate = wins / len(closed)
        
        # Ideal is 50-60% win rate
        if 0.45 <= win_rate <= 0.65:
            return 90
        elif 0.35 <= win_rate <= 0.75:
            return 70
        else:
            return 50
    
    def _calculate_risk_score(self) -> float:
        """Calculate risk management score"""
        # Check if using stops
        stops_used = len([t for t in self.trades_history if t.get('stop_loss')])
        total = len(self.trades_history)
        
        if total == 0:
            return 50
        
        stop_rate = stops_used / total
        return min(50 + stop_rate * 50, 100)
    
    def _calculate_emotional_score(self) -> float:
        """Calculate emotional control score"""
        # Based on behavioral alerts
        recent_alerts = len([a for a in self.alerts 
                           if (datetime.now() - a.timestamp) < timedelta(days=7)])
        
        return max(100 - recent_alerts * 15, 20)
    
    def _calculate_learning_score(self) -> float:
        """Calculate learning/adaptation score"""
        unlocked = len([a for a in self.achievements.values() if a.unlocked])
        total = len(self.achievements)
        
        return (unlocked / total) * 100
    
    def _score_to_status(self, score: float) -> str:
        """Convert score to status"""
        if score >= 85:
            return 'EXCELLENT - Disciplined Trader'
        elif score >= 70:
            return 'GOOD - Solid Foundation'
        elif score >= 55:
            return 'AVERAGE - Room for Improvement'
        else:
            return 'NEEDS WORK - High Risk Behaviors'
    
    def get_summary(self) -> Dict:
        """Get comprehensive behavioral analytics summary"""
        return {
            'behavioral_score': self.get_behavioral_score(),
            'recent_alerts': [
                {
                    'pattern': a.pattern,
                    'severity': a.severity,
                    'description': a.description,
                    'recommendation': a.recommendation,
                    'time': a.timestamp.strftime('%Y-%m-%d %H:%M')
                }
                for a in self.alerts[-5:]
            ],
            'achievements': {
                'unlocked': len([a for a in self.achievements.values() if a.unlocked]),
                'total': len(self.achievements),
                'recent_unlocks': [
                    {'name': a.name, 'icon': a.icon, 'date': a.unlocked_date.strftime('%Y-%m-%d')}
                    for a in self.achievements.values()
                    if a.unlocked and a.unlocked_date and 
                    (datetime.now() - a.unlocked_date) < timedelta(days=30)
                ]
            },
            'streaks': self.streaks,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recs = []
        
        score = self.get_behavioral_score()
        
        if score['component_scores']['risk_management'] < 70:
            recs.append("Use stop losses on every trade. Risk no more than 1% per trade.")
        
        if score['component_scores']['emotional_control'] < 70:
            recs.append("Take 24-hour break after 3 consecutive losses. Keep trading journal.")
        
        if score['component_scores']['discipline'] < 70:
            recs.append("Create and follow a trading plan. Review before every trade.")
        
        if not recs:
            recs.append("Great job! Keep following your trading plan and risk rules.")
        
        return recs


# Usage
def get_behavioral_summary(trades: List[Dict]) -> Dict:
    """Quick behavioral analysis"""
    analyzer = BehavioralAnalytics()
    
    for trade in trades:
        analyzer.add_trade(trade)
    
    return analyzer.get_summary()


def check_trader_health(trades: List[Dict]) -> Dict:
    """Check trader behavioral health"""
    analyzer = BehavioralAnalytics()
    
    for trade in trades:
        analyzer.add_trade(trade)
    
    return analyzer.get_behavioral_score()
