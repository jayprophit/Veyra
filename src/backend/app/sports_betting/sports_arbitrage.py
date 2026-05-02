"""
Sports Betting Arbitrage Finder
================================
Find arbitrage opportunities across sportsbooks
Line shopping, sure bets, positive expected value
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class BetType(Enum):
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"
    FUTURES = "futures"


@dataclass
class BettingLine:
    sportsbook: str
    event: str
    bet_type: str
    selection: str
    odds: float  # Decimal odds (European)
    stake_limit: float
    timestamp: datetime


class SportsArbitrageFinder:
    """
    Find sports betting arbitrage opportunities
    
    Arb occurs when sum of implied probabilities < 1
    """
    
    # Major sportsbooks
    SPORTSBOOKS = {
        'draftkings': {'juice': 0.045, 'limits': 10000},
        'fanduel': {'juice': 0.045, 'limits': 10000},
        'betmgm': {'juice': 0.05, 'limits': 5000},
        'caesars': {'juice': 0.05, 'limits': 5000},
        'pinnacle': {'juice': 0.02, 'limits': 50000},  # Sharp book
        'betfair': {'juice': 0.02, 'limits': 20000}  # Exchange
    }
    
    def find_arbitrage_2way(self, lines: List[BettingLine]) -> List[Dict]:
        """
        Find arbitrage on 2-way markets (moneyline, totals, spreads)
        
        Arb exists when: 1/odds_A + 1/odds_B < 1
        """
        opportunities = []
        
        # Group by event and bet type
        by_event = {}
        for line in lines:
            key = (line.event, line.bet_type)
            if key not in by_event:
                by_event[key] = []
            by_event[key].append(line)
        
        # Check each event for arb
        for (event, bet_type), event_lines in by_event.items():
            if len(event_lines) < 2:
                continue
            
            # Find best odds for each side
            sides = {}
            for line in event_lines:
                if line.selection not in sides:
                    sides[line.selection] = []
                sides[line.selection].append(line)
            
            if len(sides) != 2:
                continue  # Need exactly 2 sides
            
            side_names = list(sides.keys())
            
            # Get best odds for each side
            best_1 = max(sides[side_names[0]], key=lambda x: x.odds)
            best_2 = max(sides[side_names[1]], key=lambda x: x.odds)
            
            # Check for arb
            implied_prob = (1 / best_1.odds) + (1 / best_2.odds)
            
            if implied_prob < 1:
                # Arb found!
                profit_margin = (1 - implied_prob) * 100
                
                # Optimal stake allocation
                total_stake = min(best_1.stake_limit, best_2.stake_limit) * 0.5
                stake_1 = total_stake * (1 / best_1.odds) / implied_prob
                stake_2 = total_stake * (1 / best_2.odds) / implied_prob
                
                guaranteed_profit = total_stake * (1 - implied_prob)
                
                opportunities.append({
                    'event': event,
                    'bet_type': bet_type,
                    'side_a': {
                        'selection': side_names[0],
                        'sportsbook': best_1.sportsbook,
                        'odds': best_1.odds,
                        'stake': round(stake_1, 0)
                    },
                    'side_b': {
                        'selection': side_names[1],
                        'sportsbook': best_2.sportsbook,
                        'odds': best_2.odds,
                        'stake': round(stake_2, 0)
                    },
                    'total_stake': round(total_stake, 0),
                    'guaranteed_profit': round(guaranteed_profit, 0),
                    'profit_margin_pct': round(profit_margin, 2),
                    'roi_pct': round(profit_margin, 2)
                })
        
        # Sort by profit margin
        opportunities.sort(key=lambda x: x['profit_margin_pct'], reverse=True)
        
        return opportunities
    
    def calculate_implied_probability(self, odds_american: int) -> float:
        """Convert American odds to implied probability"""
        if odds_american > 0:
            return 100 / (odds_american + 100)
        else:
            return abs(odds_american) / (abs(odds_american) + 100)
    
    def find_positive_ev_bets(self, lines: List[BettingLine],
                             true_probabilities: Dict[str, float]) -> List[Dict]:
        """
        Find positive expected value bets
        
        Compare market odds to true probability
        """
        positive_ev = []
        
        for line in lines:
            event_key = f"{line.event}:{line.selection}"
            
            if event_key not in true_probabilities:
                continue
            
            true_prob = true_probabilities[event_key]
            market_prob = 1 / line.odds
            
            # Calculate EV
            ev = (true_prob * (line.odds - 1)) - (1 - true_prob)
            
            if ev > 0:
                positive_ev.append({
                    'event': line.event,
                    'selection': line.selection,
                    'sportsbook': line.sportsbook,
                    'odds': line.odds,
                    'market_implied_prob': round(market_prob, 3),
                    'true_probability': round(true_prob, 3),
                    'edge': round(true_prob - market_prob, 3),
                    'expected_value_pct': round(ev * 100, 2),
                    'kelly_fraction': round((true_prob * (line.odds - 1) - (1 - true_prob)) / (line.odds - 1), 3)
                })
        
        # Sort by EV
        positive_ev.sort(key=lambda x: x['expected_value_pct'], reverse=True)
        
        return positive_ev
    
    def get_arbitrage_summary(self, bankroll: float = 10000) -> Dict:
        """Get summary of arbitrage landscape"""
        
        # Typical arb opportunities available
        typical_opportunities = {
            'count_daily': 3,
            'avg_profit_margin': 0.015,  # 1.5%
            'avg_stake_required': 2000,
            'avg_profit_per_opportunity': 30
        }
        
        daily_potential = (
            typical_opportunities['count_daily'] * 
            typical_opportunities['avg_profit_per_opportunity']
        )
        
        monthly_potential = daily_potential * 30
        
        return {
            'arbitrage_type': 'RISK_FREE',
            'typical_opportunities_per_day': typical_opportunities['count_daily'],
            'avg_profit_margin': f"{typical_opportunities['avg_profit_margin']*100:.1f}%",
            'daily_profit_potential': daily_potential,
            'monthly_profit_potential': monthly_potential,
            'required_bankroll': typical_opportunities['avg_stake_required'] * 2,
            'risks': [
                'Line movement before all bets placed',
                'Bet limits prevent proper sizing',
                'Account limits/restrictions',
                'Human error in execution'
            ],
            'mitigation': [
                'Use fast line monitoring software',
                'Diversify across many sportsbooks',
                'Use friends/family accounts legally',
                'Double-check all bets immediately'
            ],
            'roi_estimate': f"{daily_potential / bankroll * 30 * 100:.1f}% monthly"
        }


# Usage
def find_sports_arbitrage(lines_data: List[Dict]) -> List[Dict]:
    """Quick sports arbitrage finder"""
    finder = SportsArbitrageFinder()
    
    lines = [
        BettingLine(
            sportsbook=l['book'],
            event=l['event'],
            bet_type=l['type'],
            selection=l['selection'],
            odds=l['odds'],
            stake_limit=l.get('limit', 1000),
            timestamp=datetime.now()
        )
        for l in lines_data
    ]
    
    return finder.find_arbitrage_2way(lines)


def get_positive_ev(lines_data: List[Dict], true_probs: Dict[str, float]) -> List[Dict]:
    """Find positive EV bets"""
    finder = SportsArbitrageFinder()
    
    lines = [
        BettingLine(
            sportsbook=l['book'],
            event=l['event'],
            bet_type=l['type'],
            selection=l['selection'],
            odds=l['odds'],
            stake_limit=l.get('limit', 1000),
            timestamp=datetime.now()
        )
        for l in lines_data
    ]
    
    return finder.find_positive_ev_bets(lines, true_probs)


def get_arb_summary() -> Dict:
    """Get arbitrage summary"""
    finder = SportsArbitrageFinder()
    return finder.get_arbitrage_summary()
