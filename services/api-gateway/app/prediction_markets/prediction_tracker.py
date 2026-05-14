"""
Prediction Markets Tracker
==========================
Track prediction markets for market intelligence
Polymarket, Kalshi, election betting, event derivatives
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MarketCategory(Enum):
    POLITICS = "politics"
    ECONOMICS = "economics"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    CRYPTO = "crypto"
    SCIENCE = "science"


@dataclass
class PredictionMarket:
    market_id: str
    question: str
    category: str
    probability_yes: float  # 0-1
    volume_usd: float
    liquidity: float
    close_date: datetime
    resolution_source: str
    fees_pct: float


class PredictionMarketsTracker:
    """
    Track prediction markets for alternative data and sentiment
    
    Sources: Polymarket, Kalshi, PredictIt (RIP), crypto prediction markets
    """
    
    # Market platforms
    PLATFORMS = {
        'polymarket': {
            'blockchain': 'Polygon',
            'fees': 0.02,
            'max_payout': 1000000,
            'categories': ['politics', 'crypto', 'sports', 'entertainment']
        },
        'kalshi': {
            'regulated': True,
            'fees': 0.00,  # No trading fees, spread only
            'max_payout': 25000,
            'categories': ['economics', 'politics', 'weather', 'sports']
        }
    }
    
    # Economic prediction markets of interest
    ECONOMIC_MARKETS = {
        'fed_rate_decision': {
            'question': 'Will Fed raise rates at next meeting?',
            'typical_volume': '$2M',
            'signal_value': 'HIGH - Institutional interest'
        },
        'cpi_release': {
            'question': 'Will CPI YoY be above 3%?',
            'typical_volume': '$500K',
            'signal_value': 'MEDIUM - Inflation expectations'
        },
        'recession_2024': {
            'question': 'Will US enter recession in 2024?',
            'typical_volume': '$5M',
            'signal_value': 'HIGH - Macro indicator'
        },
        'btc_price': {
            'question': 'Will BTC be above $100K by EOY?',
            'typical_volume': '$10M',
            'signal_value': 'MEDIUM - Crypto sentiment'
        }
    }
    
    def analyze_market_sentiment(self, markets: List[PredictionMarket]) -> Dict:
        """Analyze prediction market sentiment by category"""
        
        by_category = {}
        
        for market in markets:
            cat = market.category
            if cat not in by_category:
                by_category[cat] = {
                    'markets': [],
                    'avg_probability': 0,
                    'total_volume': 0
                }
            
            by_category[cat]['markets'].append(market)
            by_category[cat]['total_volume'] += market.volume_usd
        
        # Calculate averages
        for cat in by_category:
            markets = by_category[cat]['markets']
            avg_prob = sum(m.probability_yes for m in markets) / len(markets)
            by_category[cat]['avg_probability'] = round(avg_prob, 3)
            by_category[cat]['market_count'] = len(markets)
        
        return {
            'by_category': by_category,
            'total_volume': sum(m.volume_usd for m in markets),
            'most_active_category': max(by_category.items(), 
                                       key=lambda x: x[1]['total_volume'])[0],
            'timestamp': datetime.now().isoformat()
        }
    
    def find_divergence_trades(self, prediction_markets: List[PredictionMarket],
                               traditional_odds: Dict[str, float]) -> List[Dict]:
        """
        Find arbitrage between prediction markets and traditional odds
        
        prediction_markets: List of markets with current probabilities
        traditional_odds: Dict of {market_id: implied_probability}
        """
        opportunities = []
        
        for market in prediction_markets:
            market_id = market.market_id
            
            if market_id not in traditional_odds:
                continue
            
            pred_prob = market.probability_yes
            trad_prob = traditional_odds[market_id]
            
            # Check for divergence > 5%
            divergence = abs(pred_prob - trad_prob)
            
            if divergence > 0.05:
                # Determine which side is mispriced
                if pred_prob > trad_prob:
                    signal = 'PREDICTION_MARKET_OVERVALUES'
                    trade = 'SELL on prediction market, BUY traditional'
                else:
                    signal = 'TRADITIONAL_OVERVALUES'
                    trade = 'BUY on prediction market, SELL traditional'
                
                opportunities.append({
                    'market': market.question,
                    'prediction_market_prob': round(pred_prob, 3),
                    'traditional_prob': round(trad_prob, 3),
                    'divergence': round(divergence, 3),
                    'signal': signal,
                    'trade_recommendation': trade,
                    'edge_pct': round(divergence * 100, 1)
                })
        
        # Sort by divergence
        opportunities.sort(key=lambda x: x['divergence'], reverse=True)
        
        return opportunities
    
    def calculate_kelly_bet(self, market: PredictionMarket,
                           your_probability: float,
                           bankroll: float) -> Dict:
        """
        Calculate optimal Kelly criterion bet size
        
        Kelly = (bp - q) / b
        where b = odds - 1, p = probability of win, q = probability of loss
        """
        
        market_prob = market.probability_yes
        market_odds = 1 / market_prob  # Decimal odds
        
        # Kelly calculation
        b = market_odds - 1
        p = your_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        
        # Conservative half-Kelly
        half_kelly = kelly_fraction / 2
        
        # Quarter-Kelly (very conservative)
        quarter_kelly = kelly_fraction / 4
        
        # Bet amounts
        kelly_bet = bankroll * max(0, kelly_fraction)
        half_kelly_bet = bankroll * max(0, half_kelly)
        quarter_kelly_bet = bankroll * max(0, quarter_kelly)
        
        # Expected value
        ev = (your_probability * market_odds - 1) * 100  # as percentage
        
        return {
            'market': market.question,
            'market_implied_prob': round(market_prob, 3),
            'your_probability': round(your_probability, 3),
            'edge': round(your_probability - market_prob, 3),
            'kelly_fraction': round(max(0, kelly_fraction), 3),
            'kelly_bet_size': round(kelly_bet, 0),
            'half_kelly_bet': round(half_kelly_bet, 0),
            'quarter_kelly_bet': round(quarter_kelly_bet, 0),
            'expected_value_pct': round(ev, 1),
            'viable_trade': your_probability > market_prob + 0.05
        }
    
    def get_market_overview(self) -> Dict:
        """Get prediction market ecosystem overview"""
        return {
            'leading_platforms': [
                {'name': 'Polymarket', 'volume': '$100M+ monthly', 'focus': 'Global events'},
                {'name': 'Kalshi', 'volume': '$10M+ monthly', 'focus': 'US regulated'},
                {'name': 'Crypto markets', 'volume': '$50M+ monthly', 'focus': 'DeFi native'}
            ],
            'trading_strategies': {
                'information_arbitrage': 'Use private information/insights',
                'statistical_arbitrage': 'Find mispriced probabilities',
                'news_trading': 'React quickly to breaking events',
                'market_making': 'Provide liquidity, capture spread'
            },
            'risks': [
                'Resolution source risk (who decides outcome?)',
                'Smart contract risk (for crypto markets)',
                'Liquidity risk (wide spreads on small markets)',
                'Regulatory risk (PredictIt shutdown example)'
            ],
            'alpha_sources': [
                'Insider knowledge of events',
                'Superior polling analysis',
                'Better understanding of base rates',
                'Faster news reaction'
            ]
        }


# Usage
def analyze_prediction_sentiment(markets: List[Dict]) -> Dict:
    """Quick prediction market sentiment analysis"""
    tracker = PredictionMarketsTracker()
    
    market_objects = [
        PredictionMarket(
            market_id=m['id'],
            question=m['question'],
            category=m['category'],
            probability_yes=m['probability'],
            volume_usd=m['volume'],
            liquidity=m.get('liquidity', 10000),
            close_date=m.get('close_date', datetime.now()),
            resolution_source=m.get('source', 'Official data'),
            fees_pct=m.get('fees', 0.02)
        )
        for m in markets
    ]
    
    return tracker.analyze_market_sentiment(market_objects)


def find_prediction_arbitrage(prediction_probs: Dict[str, float],
                              traditional_probs: Dict[str, float]) -> List[Dict]:
    """Find arbitrage opportunities"""
    tracker = PredictionMarketsTracker()
    
    markets = [
        PredictionMarket(
            market_id=k,
            question=k,
            category='politics',
            probability_yes=v,
            volume_usd=1000000,
            liquidity=500000,
            close_date=datetime.now(),
            resolution_source='Official',
            fees_pct=0.02
        )
        for k, v in prediction_probs.items()
    ]
    
    return tracker.find_divergence_trades(markets, traditional_probs)


def get_optimal_bet(market_prob: float, your_prob: float, bankroll: float) -> Dict:
    """Calculate Kelly-optimal bet"""
    tracker = PredictionMarketsTracker()
    
    market = PredictionMarket(
        market_id='demo',
        question='Demo Market',
        category='politics',
        probability_yes=market_prob,
        volume_usd=1000000,
        liquidity=500000,
        close_date=datetime.now(),
        resolution_source='Official',
        fees_pct=0.02
    )
    
    return tracker.calculate_kelly_bet(market, your_prob, bankroll)
