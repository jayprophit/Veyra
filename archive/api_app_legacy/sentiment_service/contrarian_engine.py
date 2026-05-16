"""
Contrarian Engine - Financial Wisdom Integration
Combines Fear & Greed Index with insights from classic financial literature:
- Rich Dad Poor Dad (Kiyosaki) - Asset mindset, cashflow quadrant
- The Millionaire Next Door - Frugality, wealth building habits
- Think and Grow Rich (Hill) - Desire, persistence, success philosophy
- The Psychology of Money (Housel) - Behavioral finance, emotions
- The Wealthy Barber - Automatic systems, long-term planning
- The Simple Path to Wealth - Index investing, financial independence
- The Automatic Millionaire - Automation, compound growth
- The Intelligent Investor (Graham) - Margin of safety, Mr. Market

Features:
- Fear & Greed Index with extreme sentiment detection
- Short squeeze alerts (crowd psychology)
- Insider buying signals (smart money vs dumb money)
- Behavioral bias detection (greed, fear, FOMO, panic)
- Contrarian opportunity scoring
- Asset vs Liability mindset analysis
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class FearGreedLevel(Enum):
    """Fear & Greed Index levels with Buffett wisdom"""
    EXTREME_FEAR = 0  # "Be greedy when others are fearful"
    FEAR = 25
    NEUTRAL = 50
    GREED = 75
    EXTREME_GREED = 100  # "Be fearful when others are greedy"


class ContrarianSignal(Enum):
    """Types of contrarian signals"""
    EXTREME_FEAR_OPPORTUNITY = "extreme_fear_opportunity"  # Buy signal
    EXTREME_GREED_WARNING = "extreme_greed_warning"  # Sell signal
    SHORT_SQUEEZE_POTENTIAL = "short_squeeze_potential"
    INSIDER_BUYING = "insider_buying"
    MARGIN_OF_SAFETY = "margin_of_safety"  # Graham
    SMART_MONEY_FLOW = "smart_money_flow"
    DUMB_MONEY_EXODUS = "dumb_money_exodus"
    ASSET_ACCUMULATION = "asset_accumulation"  # Kiyosaki
    AUTOMATED_WEALTH = "automated_wealth"  # Bach


@dataclass
class FinancialWisdomInsight:
    """Insight from financial literature"""
    source: str  # Book/Author
    principle: str
    application: str
    current_relevance: float  # 0-1 score
    action_recommendation: str


@dataclass
class ContrarianOpportunity:
    """Contrarian trading opportunity"""
    ticker: str
    signal_type: ContrarianSignal
    fear_greed_score: float
    confidence: float
    wisdom_insights: List[FinancialWisdomInsight]
    metrics: Dict[str, float]
    recommended_action: str
    urgency: str  # low, medium, high, extreme
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            'ticker': self.ticker,
            'signal_type': self.signal_type.value,
            'fear_greed_score': self.fear_greed_score,
            'confidence': self.confidence,
            'wisdom_insights': [
                {
                    'source': w.source,
                    'principle': w.principle,
                    'application': w.application,
                    'relevance': w.current_relevance
                }
                for w in self.wisdom_insights
            ],
            'metrics': self.metrics,
            'recommended_action': self.recommended_action,
            'urgency': self.urgency,
            'timestamp': self.timestamp.isoformat()
        }


class ContrarianEngine:
    """
    Advanced contrarian analysis engine combining:
    - Market sentiment extremes (Fear & Greed)
    - Behavioral finance principles (Psychology of Money)
    - Smart money tracking (insiders, institutions)
    - Asset accumulation strategies (Rich Dad, Simple Path)
    - Long-term wealth building (Automatic Millionaire, Wealthy Barber)
    """
    
    # Financial wisdom from classic books
    WISDOM_LIBRARY = {
        'buffett': {
            'quotes': [
                "Be fearful when others are greedy",
                "Be greedy when others are fearful",
                "Price is what you pay, value is what you get"
            ],
            'triggers': {
                'extreme_fear': 'BUY_OPPORTUNITY',
                'extreme_greed': 'SELL_WARNING'
            }
        },
        'kiyosaki_rich_dad': {
            'quotes': [
                "The rich buy assets, the poor buy liabilities",
                "It's not how much money you make, it's how much you keep",
                "Make money work for you, not you work for money"
            ],
            'principles': {
                'asset_vs_liability': 'Focus on income-generating assets',
                'cashflow_quadrant': 'Move from E/S to B/I quadrants',
                'financial_literacy': 'Understand money before seeking it'
            },
            'triggers': {
                'dividend_opportunity': 'ASSET_ACCUMULATION',
                'cashflow_positive': 'QUADRANT_ADVANCEMENT',
                'passive_income': 'AUTOMATED_WEALTH'
            }
        },
        'millionaire_next_door': {
            'quotes': [
                "Wealth is what you accumulate, not what you spend",
                "Live below your means",
                "Time and energy are finite resources"
            ],
            'principles': {
                'frugality': 'Spend less than you earn consistently',
                'accumulation': 'Build net worth through disciplined investing',
                'avoid_lifestyle_inflation': 'Keep expenses flat as income rises'
            },
            'triggers': {
                'high_valuation': 'FRUGALITY_OPPORTUNITY',
                'market_crash': 'ACCUMULATION_PHASE',
                'inflation_fear': 'LIFESTYLE_PROTECTION'
            }
        },
        'think_grow_rich': {
            'quotes': [
                "Whatever the mind can conceive and believe, it can achieve",
                "Desire is the starting point of all achievement",
                "Persistence is to success what carbon is to steel"
            ],
            'principles': {
                'definite_purpose': 'Have a clear financial goal',
                'persistence': 'Stay invested through volatility',
                'mastermind': 'Surround yourself with smart investors'
            },
            'triggers': {
                'market_crash': 'PERSISTENCE_TEST',
                'goal_opportunity': 'DEFINITE_PURPOSE',
                'mentor_signal': 'MASTERMIND_FOLLOW'
            }
        },
        'psychology_of_money': {
            'quotes': [
                "Wealth is the car you didn't buy",
                "Saving is the gap between your ego and your income",
                "No one is as impressed with your possessions as you are"
            ],
            'principles': {
                'behavioral_awareness': 'Recognize emotional decision-making',
                'tail_risk': 'Protect against extreme negative events',
                'compounding': 'Time is the most powerful wealth factor',
                'survival_bias': "Do not chase hot performance"
            },
            'triggers': {
                'fomo_moment': 'BEHAVIORAL_ALERT',
                'panic_selling': 'EMOTIONAL_OPPORTUNITY',
                'tail_event': 'RISK_PROTECTION',
                'long_horizon': 'COMPOUNDING_ADVANTAGE'
            }
        },
        'wealthy_barber': {
            'quotes': [
                "Pay yourself first",
                "Automate your financial life",
                "The magic of compound interest is real"
            ],
            'principles': {
                'automatic_saving': '10% minimum automatic savings',
                'dollar_cost_averaging': 'Consistent investing regardless of market',
                'emergency_fund': '3-6 months expenses in safe account'
            },
            'triggers': {
                'payday': 'AUTOMATIC_INVESTMENT',
                'volatility_spike': 'DCA_OPPORTUNITY',
                'crash_event': 'EMERGENCY_FUND_TEST'
            }
        },
        'simple_path_wealth': {
            'quotes': [
                "Don't just do something, stand there",
                "The stock market is a tool for transferring wealth to the patient",
                "VTSAX and chill"
            ],
            'principles': {
                'index_investing': 'Broad market exposure, low costs',
                'financial_independence': 'FIRE principles for early retirement',
                'ignore_noise': "Do not react to market news",
                'stay_the_course': 'Consistency beats timing'
            },
            'triggers': {
                'market_news': 'IGNORE_NOISE',
                'temptation_to_trade': 'STAY_THE_COURSE',
                'fear_event': 'IGNORE_AND_INVEST',
                'greed_event': 'STICK_TO_PLAN'
            }
        },
        'automatic_millionaire': {
            'quotes': [
                "The latte factor - small expenses add up",
                "Pay yourself first, automatically",
                "Set it and forget it"
            ],
            'principles': {
                'automation': 'Automate all wealth building',
                'latte_factor': 'Small daily savings compound to millions',
                'systematic_investing': 'Remove decision fatigue'
            },
            'triggers': {
                'manual_trading_urge': 'AUTOMATE_INSTEAD',
                'spending_temptation': 'LATTE_FACTOR_CHECK',
                'payday': 'AUTOMATIC_TRANSFER'
            }
        },
        'intelligent_investor': {
            'quotes': [
                "Mr. Market is your servant, not your guide",
                "Margin of safety is the central concept of investing",
                "The stock market is a voting machine in the short term, a weighing machine in the long"
            ],
            'principles': {
                'mr_market': "Use market irrationality, do not follow it",
                'margin_of_safety': 'Buy with significant downside protection',
                'value_investing': 'Price vs intrinsic value focus',
                'defensive_investing': 'Safety of principal + adequate return'
            },
            'triggers': {
                'market_mania': 'MR_MARKET_SERVANT',
                'high_valuation': 'MARGIN_OF_SAFETY_LOW',
                'crash_opportunity': 'MARGIN_OF_SAFETY_HIGH',
                'defensive_moment': 'DEFENSIVE_POSITIONING'
            }
        }
    }
    
    def __init__(self):
        self.fear_greed_history: List[Dict] = []
        self.max_history = 1000
        self.current_scores: Dict[str, float] = {}
        self.opportunity_cache: List[ContrarianOpportunity] = []
        
    def calculate_fear_greed_index(self, market_data: Dict) -> Dict[str, Any]:
        """
        Calculate Fear & Greed Index (0-100 scale)
        Based on CNN Money's methodology
        """
        # Market momentum (S&P 500 vs 125-day average)
        momentum_score = self._calculate_momentum(market_data)
        
        # Stock price strength (number of stocks at 52-week highs vs lows)
        strength_score = self._calculate_strength(market_data)
        
        # Stock price breadth (volume of advancing vs declining stocks)
        breadth_score = self._calculate_breadth(market_data)
        
        # Put/call ratio (options market fear indicator)
        put_call_score = self._calculate_put_call_ratio(market_data)
        
        # Junk bond demand (spread between investment grade and junk)
        junk_bond_score = self._calculate_junk_bond_demand(market_data)
        
        # Market volatility (VIX index)
        vix_score = self._calculate_vix_score(market_data)
        
        # Safe haven demand (treasury vs stock performance)
        safe_haven_score = self._calculate_safe_haven(market_data)
        
        # Average all scores
        total_score = (
            momentum_score + strength_score + breadth_score +
            put_call_score + junk_bond_score + vix_score + safe_haven_score
        ) / 7
        
        index_level = self._get_fear_greed_level(total_score)
        
        result = {
            'index_value': round(total_score, 1),
            'level': index_level.name,
            'description': self._get_level_description(index_level),
            'components': {
                'market_momentum': round(momentum_score, 1),
                'price_strength': round(strength_score, 1),
                'price_breadth': round(breadth_score, 1),
                'put_call_ratio': round(put_call_score, 1),
                'junk_bond_demand': round(junk_bond_score, 1),
                'market_volatility': round(vix_score, 1),
                'safe_haven_demand': round(safe_haven_score, 1)
            },
            'timestamp': datetime.now().isoformat(),
            'recommendation': self._get_contrarian_recommendation(index_level),
            'wisdom_applied': self._apply_wisdom_to_index(index_level)
        }
        
        self.fear_greed_history.append(result)
        if len(self.fear_greed_history) > self.max_history:
            self.fear_greed_history.pop(0)
        
        return result
    
    def _calculate_momentum(self, data: Dict) -> float:
        """S&P 500 vs 125-day moving average"""
        sp500_current = data.get('sp500_current', 4500)
        sp500_125d_avg = data.get('sp500_125d_avg', 4400)
        
        momentum = (sp500_current / sp500_125d_avg - 1) * 100
        # Normalize to 0-100 scale
        # >10% above avg = extreme greed (100), >10% below = extreme fear (0)
        return max(0, min(100, 50 + momentum * 5))
    
    def _calculate_strength(self, data: Dict) -> float:
        """Number of stocks at 52-week highs vs lows"""
        highs = data.get('new_52w_highs', 50)
        lows = data.get('new_52w_lows', 50)
        total = highs + lows if (highs + lows) > 0 else 1
        
        ratio = highs / total
        return ratio * 100
    
    def _calculate_breadth(self, data: Dict) -> float:
        """Volume of advancing vs declining stocks"""
        advancing_volume = data.get('advancing_volume', 1000)
        declining_volume = data.get('declining_volume', 1000)
        total = advancing_volume + declining_volume
        
        if total == 0:
            return 50
        
        return (advancing_volume / total) * 100
    
    def _calculate_put_call_ratio(self, data: Dict) -> float:
        """Options market fear indicator (inverted - high puts = fear)"""
        put_volume = data.get('put_volume', 100)
        call_volume = data.get('call_volume', 100)
        
        if call_volume == 0:
            return 50
        
        put_call_ratio = put_volume / call_volume
        # Invert: high put/call = fear (low score), low = greed (high score)
        # 1.0 ratio = neutral (50), >1.5 = extreme fear (0), <0.5 = extreme greed (100)
        return max(0, min(100, 100 - (put_call_ratio - 0.5) * 100))
    
    def _calculate_junk_bond_demand(self, data: Dict) -> float:
        """Spread between junk and investment grade bonds"""
        junk_yield = data.get('junk_bond_yield', 6.0)
        investment_yield = data.get('investment_grade_yield', 3.0)
        
        spread = junk_yield - investment_yield
        # Narrow spread (<3%) = greed (100), wide (>8%) = fear (0)
        return max(0, min(100, 100 - (spread - 3) * 20))
    
    def _calculate_vix_score(self, data: Dict) -> float:
        """Market volatility - inverted VIX"""
        vix = data.get('vix', 20)
        # VIX 20 = neutral, VIX 10 = extreme greed (100), VIX 40 = extreme fear (0)
        return max(0, min(100, 100 - (vix - 10) * 3.33))
    
    def _calculate_safe_haven(self, data: Dict) -> float:
        """Safe haven demand (bonds vs stocks)"""
        bond_return = data.get('treasury_20y_return_20d', 0)
        stock_return = data.get('sp500_return_20d', 0)
        
        # If bonds outperforming stocks = fear
        difference = stock_return - bond_return
        # Stocks beating bonds by >5% = greed (100), bonds beating by >5% = fear (0)
        return max(0, min(100, 50 + difference * 10))
    
    def _get_fear_greed_level(self, score: float) -> FearGreedLevel:
        """Determine fear/greed level from score"""
        if score < 20:
            return FearGreedLevel.EXTREME_FEAR
        elif score < 40:
            return FearGreedLevel.FEAR
        elif score < 60:
            return FearGreedLevel.NEUTRAL
        elif score < 80:
            return FearGreedLevel.GREED
        else:
            return FearGreedLevel.EXTREME_GREED
    
    def _get_level_description(self, level: FearGreedLevel) -> str:
        """Get human-readable description"""
        descriptions = {
            FearGreedLevel.EXTREME_FEAR: "Extreme Fear - Maximum buying opportunity",
            FearGreedLevel.FEAR: "Fear - Good buying opportunity",
            FearGreedLevel.NEUTRAL: "Neutral - Hold positions",
            FearGreedLevel.GREED: "Greed - Consider taking profits",
            FearGreedLevel.EXTREME_GREED: "Extreme Greed - Maximum caution"
        }
        return descriptions.get(level, "Unknown")
    
    def _get_contrarian_recommendation(self, level: FearGreedLevel) -> Dict:
        """Generate contrarian recommendation based on index level"""
        if level == FearGreedLevel.EXTREME_FEAR:
            return {
                'action': 'ACCUMULATE',
                'urgency': 'HIGH',
                'message': 'Be greedy when others are fearful - Time to buy quality assets',
                'position_size': 'full_risk_on',
                'cash_level': '10-20%'
            }
        elif level == FearGreedLevel.FEAR:
            return {
                'action': 'ACCUMULATE_SELECTIVELY',
                'urgency': 'MEDIUM',
                'message': 'Fear presents opportunities - Buy quality at discount',
                'position_size': 'moderate_risk_on',
                'cash_level': '20-30%'
            }
        elif level == FearGreedLevel.NEUTRAL:
            return {
                'action': 'HOLD',
                'urgency': 'LOW',
                'message': 'Stay the course - No action needed',
                'position_size': 'maintain_current',
                'cash_level': '30-40%'
            }
        elif level == FearGreedLevel.GREED:
            return {
                'action': 'TAKE_PROFITS',
                'urgency': 'MEDIUM',
                'message': 'Consider taking some profits off the table',
                'position_size': 'reduce_exposure',
                'cash_level': '40-50%'
            }
        else:  # EXTREME_GREED
            return {
                'action': 'DEFENSIVE',
                'urgency': 'HIGH',
                'message': 'Be fearful when others are greedy - Time for caution',
                'position_size': 'defensive',
                'cash_level': '50-70%'
            }
    
    def _apply_wisdom_to_index(self, level: FearGreedLevel) -> List[FinancialWisdomInsight]:
        """Apply financial wisdom literature to current index level"""
        insights = []
        
        if level in [FearGreedLevel.EXTREME_FEAR, FearGreedLevel.FEAR]:
            # Buffett - Buy when fearful
            insights.append(FinancialWisdomInsight(
                source="Warren Buffett",
                principle="Be greedy when others are fearful",
                application="Extreme fear creates maximum buying opportunities for patient investors",
                current_relevance=0.95,
                action_recommendation="Accumulate quality assets at distressed prices"
            ))
            
            # Psychology of Money - Behavioral opportunity
            insights.append(FinancialWisdomInsight(
                source="The Psychology of Money (Morgan Housel)",
                principle="Panic selling creates emotional opportunities",
                application="When others panic sell due to fear, rational investors buy",
                current_relevance=0.90,
                action_recommendation="Resist fear, focus on long-term fundamentals"
            ))
            
            # Think and Grow Rich - Persistence
            insights.append(FinancialWisdomInsight(
                source="Think and Grow Rich (Napoleon Hill)",
                principle="Persistence is to success what carbon is to steel",
                application="Market crashes test persistence - stay invested through volatility",
                current_relevance=0.85,
                action_recommendation="Stay the course, accumulate, persist"
            ))
            
            # Intelligent Investor - Mr. Market
            insights.append(FinancialWisdomInsight(
                source="The Intelligent Investor (Benjamin Graham)",
                principle="Mr. Market is your servant, not your guide",
                application="Mr. Market is offering bargain prices due to his depression",
                current_relevance=0.95,
                action_recommendation="Take advantage of Mr. Market's pessimism"
            ))
            
            # Simple Path to Wealth - Ignore and invest
            insights.append(FinancialWisdomInsight(
                source="The Simple Path to Wealth (JL Collins)",
                principle="Don't just do something, stand there",
                application="Or better yet, keep buying regularly through the crash",
                current_relevance=0.80,
                action_recommendation="Automate investments, ignore the noise"
            ))
        
        elif level in [FearGreedLevel.GREED, FearGreedLevel.EXTREME_GREED]:
            # Buffett - Fearful when others greedy
            insights.append(FinancialWisdomInsight(
                source="Warren Buffett",
                principle="Be fearful when others are greedy",
                application="Extreme greed signals market tops - time to be cautious",
                current_relevance=0.95,
                action_recommendation="Take profits, raise cash, wait for better prices"
            ))
            
            # Psychology of Money - FOMO alert
            insights.append(FinancialWisdomInsight(
                source="The Psychology of Money (Morgan Housel)",
                principle="No one is as impressed with your possessions as you are",
                application="FOMO buying at peaks destroys wealth - resist the urge",
                current_relevance=0.90,
                action_recommendation="Ignore FOMO, stick to your plan"
            ))
            
            # Rich Dad Poor Dad - Asset vs liability
            insights.append(FinancialWisdomInsight(
                source="Rich Dad Poor Dad (Robert Kiyosaki)",
                principle="The rich buy assets, the poor buy liabilities",
                application="At extreme prices, stocks become liabilities, not assets",
                current_relevance=0.85,
                action_recommendation="Wait for prices to return to asset territory"
            ))
            
            # Intelligent Investor - Margin of safety
            insights.append(FinancialWisdomInsight(
                source="The Intelligent Investor (Benjamin Graham)",
                principle="Margin of safety is the central concept of investing",
                application="At these valuations, margin of safety is non-existent",
                current_relevance=0.95,
                action_recommendation="Do not invest without margin of safety"
            ))
            
            # Millionaire Next Door - Frugality
            insights.append(FinancialWisdomInsight(
                source="The Millionaire Next Door",
                principle="Wealth is what you accumulate, not what you spend",
                application="Paying high prices is spending, not accumulating",
                current_relevance=0.80,
                action_recommendation="Be frugal with your buying prices"
            ))
        
        return insights
    
    def detect_short_squeeze_potential(self, ticker_data: Dict) -> Dict:
        """
        Detect potential short squeeze opportunities
        High short interest + positive catalyst = squeeze potential
        """
        short_interest_ratio = ticker_data.get('short_interest_ratio', 0)
        days_to_cover = ticker_data.get('days_to_cover', 0)
        float_short_pct = ticker_data.get('float_short_pct', 0)
        avg_volume = ticker_data.get('avg_daily_volume', 0)
        recent_volume = ticker_data.get('recent_volume', 0)
        price_change_5d = ticker_data.get('price_change_5d', 0)
        
        # Squeeze score calculation
        squeeze_factors = {
            'high_short_interest': short_interest_ratio > 20,
            'high_days_to_cover': days_to_cover > 5,
            'low_float': float_short_pct > 30,
            'volume_spike': recent_volume > avg_volume * 2,
            'positive_momentum': price_change_5d > 10
        }
        
        squeeze_score = sum(squeeze_factors.values()) / len(squeeze_factors)
        
        if squeeze_score >= 0.7:
            potential = "HIGH"
        elif squeeze_score >= 0.4:
            potential = "MEDIUM"
        else:
            potential = "LOW"
        
        return {
            'ticker': ticker_data.get('ticker'),
            'squeeze_potential': potential,
            'squeeze_score': round(squeeze_score * 100, 1),
            'factors': squeeze_factors,
            'metrics': {
                'short_interest_ratio': short_interest_ratio,
                'days_to_cover': days_to_cover,
                'float_short_pct': float_short_pct,
                'volume_spike_ratio': recent_volume / avg_volume if avg_volume > 0 else 0,
                'price_change_5d_pct': price_change_5d
            },
            'wisdom_insights': [
                FinancialWisdomInsight(
                    source="Crowd Psychology / Behavioral Finance",
                    principle="Short squeezes happen when fear meets forced buying",
                    application="High short interest creates powder keg - any positive catalyst ignites squeeze",
                    current_relevance=squeeze_score,
                    action_recommendation="Monitor for squeeze potential, but don't chase" if squeeze_score > 0.7 else "Not ripe for squeeze yet"
                ).__dict__,
                FinancialWisdomInsight(
                    source="The Psychology of Money",
                    principle="Tail events happen more often than we think",
                    application="Short squeezes are tail events that can happen to any heavily shorted stock",
                    current_relevance=squeeze_score,
                    action_recommendation="Respect the power of crowd dynamics and forced covering"
                ).__dict__
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_insider_activity(self, insider_data: List[Dict]) -> Dict:
        """
        Analyze insider buying/selling patterns
        Smart money vs dumb money indicator
        """
        total_buys = sum(1 for d in insider_data if d.get('transaction_type') == 'buy')
        total_sells = sum(1 for d in insider_data if d.get('transaction_type') == 'sell')
        
        buy_volume = sum(d.get('shares', 0) for d in insider_data if d.get('transaction_type') == 'buy')
        sell_volume = sum(d.get('shares', 0) for d in insider_data if d.get('transaction_type') == 'sell')
        
        # Cluster buying (multiple insiders buying in short period)
        recent_buys = [d for d in insider_data 
                      if d.get('transaction_type') == 'buy' and 
                      d.get('days_ago', 999) <= 30]
        unique_buyers = len(set(d.get('insider_name') for d in recent_buys))
        
        cluster_buying = unique_buyers >= 3 and len(recent_buys) >= 5
        
        # Calculate sentiment
        if total_buys > total_sells * 2 and buy_volume > sell_volume * 1.5:
            sentiment = "VERY_BULLISH"
            signal = ContrarianSignal.INSIDER_BUYING
        elif total_buys > total_sells:
            sentiment = "BULLISH"
            signal = ContrarianSignal.INSIDER_BUYING
        elif total_sells > total_buys * 2:
            sentiment = "BEARISH"
            signal = ContrarianSignal.EXTREME_GREED_WARNING
        else:
            sentiment = "NEUTRAL"
            signal = None
        
        return {
            'total_transactions': len(insider_data),
            'buys': total_buys,
            'sells': total_sells,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'buy_sell_ratio': round(buy_volume / sell_volume, 2) if sell_volume > 0 else float('inf'),
            'cluster_buying_detected': cluster_buying,
            'unique_recent_buyers': unique_buyers,
            'sentiment': sentiment,
            'signal': signal.value if signal else None,
            'wisdom_insights': [
                FinancialWisdomInsight(
                    source="Smart Money Concept / Market Lore",
                    principle="Insiders sell for many reasons, but buy for only one - they think it will go up",
                    application="Cluster insider buying is one of the strongest bullish signals",
                    current_relevance=0.90 if cluster_buying else 0.70,
                    action_recommendation="Strong buy signal" if cluster_buying else "Consider accumulating"
                ).__dict__,
                FinancialWisdomInsight(
                    source="The Intelligent Investor",
                    principle="Follow those with skin in the game",
                    application="Insiders have the best information - their buying is valuable signal",
                    current_relevance=0.85,
                    action_recommendation="Use insider activity as confirming signal"
                ).__dict__
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_contrarian_opportunities(self, 
                                         market_data: Dict,
                                         tickers: List[str]) -> List[ContrarianOpportunity]:
        """
        Generate contrarian opportunities combining all signals
        """
        opportunities = []
        
        # Get current fear/greed
        fg_index = self.calculate_fear_greed_index(market_data)
        fg_score = fg_index['index_value']
        
        for ticker in tickers:
            opp = self._analyze_ticker_contrarian(
                ticker, market_data, fg_score, fg_index['level']
            )
            if opp and opp.confidence > 0.6:
                opportunities.append(opp)
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x.confidence, reverse=True)
        
        return opportunities
    
    def _analyze_ticker_contrarian(self, ticker: str, market_data: Dict,
                                   fg_score: float, fg_level: str) -> Optional[ContrarianOpportunity]:
        """Analyze a single ticker for contrarian opportunity"""
        # Get ticker-specific data
        ticker_data = market_data.get('tickers', {}).get(ticker, {})
        
        metrics = {
            'pe_ratio': ticker_data.get('pe_ratio', 20),
            'pb_ratio': ticker_data.get('pb_ratio', 2),
            'price_change_52w': ticker_data.get('price_change_52w', 0),
            'rsi_14': ticker_data.get('rsi_14', 50),
            'short_interest': ticker_data.get('short_interest_ratio', 0),
            'insider_buy_ratio': ticker_data.get('insider_buy_ratio', 1)
        }
        
        # Determine signal type
        if fg_score < 25:  # Extreme fear
            signal = ContrarianSignal.EXTREME_FEAR_OPPORTUNITY
            confidence = 0.85
            urgency = "high"
            action = "ACCUMULATE_HEAVILY"
        elif metrics['rsi_14'] < 30 and metrics['price_change_52w'] < -30:
            signal = ContrarianSignal.MARGIN_OF_SAFETY
            confidence = 0.80
            urgency = "medium"
            action = "ACCUMULATE_SELECTIVELY"
        elif metrics['short_interest'] > 20 and metrics['insider_buy_ratio'] > 2:
            signal = ContrarianSignal.SHORT_SQUEEZE_POTENTIAL
            confidence = 0.75
            urgency = "high"
            action = "WATCH_FOR_SQUEEZE"
        elif metrics['insider_buy_ratio'] > 3 and fg_score < 40:
            signal = ContrarianSignal.SMART_MONEY_FLOW
            confidence = 0.70
            urgency = "medium"
            action = "FOLLOW_SMART_MONEY"
        else:
            return None
        
        # Generate wisdom insights
        wisdom = self._generate_ticker_wisdom(ticker, signal, metrics)
        
        return ContrarianOpportunity(
            ticker=ticker,
            signal_type=signal,
            fear_greed_score=fg_score,
            confidence=confidence,
            wisdom_insights=wisdom,
            metrics=metrics,
            recommended_action=action,
            urgency=urgency,
            timestamp=datetime.now()
        )
    
    def _generate_ticker_wisdom(self, ticker: str, signal: ContrarianSignal,
                               metrics: Dict) -> List[FinancialWisdomInsight]:
        """Generate relevant wisdom insights for this opportunity"""
        insights = []
        
        # Always include Buffett
        insights.append(FinancialWisdomInsight(
            source="Warren Buffett",
            principle="Price is what you pay, value is what you get",
            application=f"{ticker} price may be disconnected from intrinsic value",
            current_relevance=0.90,
            action_recommendation="Focus on value, not price movement"
        ))
        
        if signal == ContrarianSignal.EXTREME_FEAR_OPPORTUNITY:
            insights.append(FinancialWisdomInsight(
                source="The Intelligent Investor",
                principle="Mr. Market offers bargain prices during his depressive episodes",
                application=f"Market fear has created discount on {ticker}",
                current_relevance=0.95,
                action_recommendation="Take Mr. Market's offer"
            ))
        
        elif signal == ContrarianSignal.MARGIN_OF_SAFETY:
            insights.append(FinancialWisdomInsight(
                source="The Intelligent Investor (Benjamin Graham)",
                principle="Margin of safety is the central concept of investing",
                application=f"{ticker} is down {metrics['price_change_52w']:.1f}%, creating safety margin",
                current_relevance=0.95,
                action_recommendation="Buy with confidence in margin of safety"
            ))
        
        elif signal == ContrarianSignal.SHORT_SQUEEZE_POTENTIAL:
            insights.append(FinancialWisdomInsight(
                source="Crowd Psychology / Market Microstructure",
                principle="High short interest creates forced buying on any positive catalyst",
                application=f"{ticker} has {metrics['short_interest']:.1f}% short interest + insider buying",
                current_relevance=0.90,
                action_recommendation="Squeeze potential is elevated"
            ))
        
        elif signal == ContrarianSignal.SMART_MONEY_FLOW:
            insights.append(FinancialWisdomInsight(
                source="Market Wisdom",
                principle="Insiders know the business best",
                application=f"{ticker} insiders buying {metrics['insider_buy_ratio']:.1f}x sells",
                current_relevance=0.85,
                action_recommendation="Follow smart money accumulation"
            ))
        
        # Add Kiyosaki wisdom about assets
        insights.append(FinancialWisdomInsight(
            source="Rich Dad Poor Dad (Robert Kiyosaki)",
            principle="The rich buy assets, the poor buy liabilities",
            application=f"Is {ticker} an asset (cashflow positive) or liability?",
            current_relevance=0.80,
            action_recommendation="Evaluate as asset class, not speculation"
        ))
        
        return insights
    
    def get_fear_greed_history(self, days: int = 30) -> List[Dict]:
        """Get historical fear/greed data"""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            h for h in self.fear_greed_history 
            if datetime.fromisoformat(h['timestamp']) > cutoff
        ]
