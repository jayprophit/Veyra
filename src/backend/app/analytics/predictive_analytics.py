"""Predictive Analytics for User Behavior and Trading."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class UserBehaviorPrediction:
    user_id: str
    predicted_actions: List[str]
    churn_risk: float
    engagement_score: float
    next_trade_probability: float
    recommendations: List[str]
    confidence: float

class PredictiveAnalytics:
    """ML-powered predictions for user behavior and trading."""
    
    def __init__(self):
        self.user_history: Dict[str, List[Dict]] = defaultdict(list)
        self.models = {}
    
    async def predict_user_behavior(self, user_id: str) -> UserBehaviorPrediction:
        """Predict user behavior based on historical data."""
        history = self.user_history.get(user_id, [])
        
        if not history:
            return UserBehaviorPrediction(
                user_id=user_id,
                predicted_actions=["explore_platform"],
                churn_risk=0.0,
                engagement_score=0.5,
                next_trade_probability=0.3,
                recommendations=["Complete onboarding", "Try paper trading"],
                confidence=0.5
            )
        
        # Analyze patterns
        actions = [h.get('action') for h in history]
        action_freq = pd.Series(actions).value_counts()
        
        # Calculate metrics
        total_actions = len(history)
        recent_actions = [h for h in history if h.get('timestamp', datetime.now()) > datetime.now() - timedelta(days=7)]
        engagement = len(recent_actions) / 7 if recent_actions else 0
        
        # Predict next actions
        likely_actions = action_freq.head(3).index.tolist() if len(action_freq) > 0 else ["trade"]
        
        # Churn risk (no activity in 14 days)
        last_activity = max([h.get('timestamp', datetime.now()) for h in history])
        days_inactive = (datetime.now() - last_activity).days
        churn_risk = min(days_inactive / 30, 1.0) if days_inactive > 7 else 0.0
        
        # Trade probability based on pattern
        trade_count = sum(1 for a in actions if 'trade' in str(a).lower())
        trade_prob = min(trade_count / total_actions * 2, 1.0) if total_actions > 0 else 0.3
        
        # Generate recommendations
        recommendations = []
        if churn_risk > 0.5:
            recommendations.append("Send re-engagement notification")
        if trade_prob < 0.3:
            recommendations.append("Suggest educational content")
        if engagement < 0.5:
            recommendations.append("Recommend daily market updates")
        
        return UserBehaviorPrediction(
            user_id=user_id,
            predicted_actions=likely_actions,
            churn_risk=churn_risk,
            engagement_score=engagement,
            next_trade_probability=trade_prob,
            recommendations=recommendations,
            confidence=0.7
        )
    
    async def predict_market_sentiment(self, symbol: str, historical_data: List[Dict]) -> Dict[str, Any]:
        """Predict market sentiment for a symbol."""
        if not historical_data:
            return {'sentiment': 'neutral', 'confidence': 0.5, 'trend': 'sideways'}
        
        # Simple trend analysis
        prices = [d.get('price', 0) for d in historical_data if 'price' in d]
        if len(prices) < 2:
            return {'sentiment': 'neutral', 'confidence': 0.5, 'trend': 'sideways'}
        
        returns = np.diff(prices) / prices[:-1]
        avg_return = np.mean(returns)
        volatility = np.std(returns)
        
        if avg_return > 0.01:
            sentiment = 'bullish'
        elif avg_return < -0.01:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'
        
        trend = 'up' if avg_return > 0 else 'down' if avg_return < 0 else 'sideways'
        
        return {
            'symbol': symbol,
            'sentiment': sentiment,
            'confidence': 1 - min(volatility * 10, 1.0),
            'trend': trend,
            'predicted_return_24h': float(avg_return),
            'volatility': float(volatility)
        }
    
    async def segment_users(self, user_data: List[Dict]) -> Dict[str, List[str]]:
        """Segment users by behavior patterns."""
        segments = {
            'active_traders': [],
            'hodlers': [],
            'learners': [],
            'churned': [],
            'new_users': []
        }
        
        for user in user_data:
            user_id = user.get('user_id')
            activity_count = user.get('activity_count', 0)
            days_since_join = user.get('days_since_join', 0)
            last_active = user.get('days_since_active', 0)
            
            if last_active > 30:
                segments['churned'].append(user_id)
            elif days_since_join < 7:
                segments['new_users'].append(user_id)
            elif activity_count > 50:
                segments['active_traders'].append(user_id)
            elif activity_count > 10:
                segments['learners'].append(user_id)
            else:
                segments['hodlers'].append(user_id)
        
        return segments
    
    def record_user_action(self, user_id: str, action: str, metadata: dict = None):
        """Record user action for analysis."""
        self.user_history[user_id].append({
            'action': action,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        })
        # Trim old history
        cutoff = datetime.now() - timedelta(days=90)
        self.user_history[user_id] = [
            h for h in self.user_history[user_id] 
            if h.get('timestamp', datetime.now()) > cutoff
        ]

predictive_analytics = PredictiveAnalytics()
