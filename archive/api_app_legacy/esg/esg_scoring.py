"""
ESG (Environmental, Social, Governance) Scoring System
======================================================
Comprehensive ESG analysis and scoring for sustainable investing
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ESGScore:
    """ESG scoring data"""
    ticker: str
    environmental: float  # 0-10
    social: float  # 0-10
    governance: float  # 0-10
    overall: float  # 0-10
    carbon_intensity: float  # tons CO2 / $1M revenue
    controversy_score: int  # 0-5 (5 = severe)
    last_updated: datetime


class ESGScoringSystem:
    """
    ESG scoring and analysis system
    
    Scores companies on:
    - Environmental: Carbon emissions, resource use, pollution
    - Social: Labor practices, diversity, community impact
    - Governance: Board structure, ethics, transparency
    """
    
    # Sample ESG data for major companies
    ESG_DATABASE = {
        'AAPL': ESGScore('AAPL', 7.5, 6.8, 7.2, 7.2, 45.3, 1, datetime.now()),
        'MSFT': ESGScore('MSFT', 8.2, 7.5, 8.0, 7.9, 32.1, 0, datetime.now()),
        'GOOGL': ESGScore('GOOGL', 7.8, 6.5, 6.8, 7.0, 48.7, 2, datetime.now()),
        'TSLA': ESGScore('TSLA', 8.5, 5.5, 6.0, 6.7, 12.3, 2, datetime.now()),
        'AMZN': ESGScore('AMZN', 6.5, 5.8, 6.5, 6.3, 67.8, 2, datetime.now()),
        'JPM': ESGScore('JPM', 6.0, 6.5, 7.0, 6.5, 12.1, 1, datetime.now()),
        'XOM': ESGScore('XOM', 3.5, 5.0, 6.0, 4.8, 485.2, 3, datetime.now()),
        'CVX': ESGScore('CVX', 4.0, 5.5, 6.5, 5.3, 356.7, 2, datetime.now()),
        'NEE': ESGScore('NEE', 8.0, 6.5, 7.0, 7.2, 28.4, 0, datetime.now()),
        'ENPH': ESGScore('ENPH', 9.0, 7.0, 7.5, 7.8, 8.2, 0, datetime.now()),
    }
    
    def __init__(self):
        self.scores = self.ESG_DATABASE.copy()
    
    def get_score(self, ticker: str) -> Optional[ESGScore]:
        """Get ESG score for a company"""
        return self.scores.get(ticker)
    
    def get_esg_rating(self, score: float) -> str:
        """Convert numeric score to rating"""
        if score >= 8.0:
            return 'AAA'
        elif score >= 7.0:
            return 'AA'
        elif score >= 6.0:
            return 'A'
        elif score >= 5.0:
            return 'BBB'
        elif score >= 4.0:
            return 'BB'
        elif score >= 3.0:
            return 'B'
        elif score >= 2.0:
            return 'CCC'
        else:
            return 'CC'
    
    def screen_portfolio(self, tickers: List[str], 
                       min_score: float = 6.0,
                       max_carbon: float = 100.0) -> Dict:
        """Screen portfolio for ESG compliance"""
        results = {
            'passed': [],
            'failed': [],
            'excluded': []
        }
        
        for ticker in tickers:
            score = self.scores.get(ticker)
            
            if not score:
                results['excluded'].append({
                    'ticker': ticker,
                    'reason': 'No ESG data available'
                })
                continue
            
            if score.overall >= min_score and score.carbon_intensity <= max_carbon:
                results['passed'].append({
                    'ticker': ticker,
                    'esg_score': score.overall,
                    'rating': self.get_esg_rating(score.overall),
                    'carbon_intensity': score.carbon_intensity
                })
            else:
                reasons = []
                if score.overall < min_score:
                    reasons.append(f"ESG score {score.overall} < {min_score}")
                if score.carbon_intensity > max_carbon:
                    reasons.append(f"Carbon intensity {score.carbon_intensity} > {max_carbon}")
                
                results['failed'].append({
                    'ticker': ticker,
                    'esg_score': score.overall,
                    'carbon_intensity': score.carbon_intensity,
                    'reasons': reasons
                })
        
        return results
    
    def get_sector_leaders(self, sector: str) -> List[ESGScore]:
        """Get ESG leaders by sector"""
        sector_map = {
            'technology': ['AAPL', 'MSFT', 'GOOGL'],
            'energy': ['XOM', 'CVX', 'NEE'],
            'financials': ['JPM'],
            'consumer': ['AMZN', 'TSLA'],
            'solar': ['ENPH']
        }
        
        tickers = sector_map.get(sector.lower(), [])
        scores = [self.scores.get(t) for t in tickers if t in self.scores]
        
        return sorted(scores, key=lambda x: x.overall if x else 0, reverse=True)
    
    def calculate_portfolio_esg(self, holdings: Dict[str, float]) -> Dict:
        """Calculate weighted ESG score for portfolio"""
        total_value = sum(holdings.values())
        
        if total_value == 0:
            return {'error': 'No holdings'}
        
        weighted_scores = {
            'environmental': 0,
            'social': 0,
            'governance': 0,
            'overall': 0,
            'carbon_intensity': 0
        }
        
        for ticker, value in holdings.items():
            weight = value / total_value
            score = self.scores.get(ticker)
            
            if score:
                weighted_scores['environmental'] += score.environmental * weight
                weighted_scores['social'] += score.social * weight
                weighted_scores['governance'] += score.governance * weight
                weighted_scores['overall'] += score.overall * weight
                weighted_scores['carbon_intensity'] += score.carbon_intensity * weight
        
        return {
            'portfolio_esg_score': round(weighted_scores['overall'], 2),
            'portfolio_rating': self.get_esg_rating(weighted_scores['overall']),
            'breakdown': {
                'environmental': round(weighted_scores['environmental'], 2),
                'social': round(weighted_scores['social'], 2),
                'governance': round(weighted_scores['governance'], 2)
            },
            'carbon_intensity': round(weighted_scores['carbon_intensity'], 2),
            ' holdings_analyzed': len([t for t in holdings if t in self.scores]),
            'holdings_missing_data': len([t for t in holdings if t not in self.scores])
        }
    
    def get_esg_themes(self) -> Dict[str, List[str]]:
        """Get stocks by ESG theme"""
        return {
            'clean_energy': ['TSLA', 'ENPH', 'NEE'],
            'carbon_intensive': ['XOM', 'CVX'],
            'tech_leaders': ['MSFT', 'AAPL'],
            'social_leaders': ['MSFT', 'JPM'],
            'governance_leaders': ['MSFT', 'AAPL']
        }
    
    def generate_esg_report(self, portfolio: Dict[str, float]) -> Dict:
        """Generate comprehensive ESG report"""
        portfolio_esg = self.calculate_portfolio_esg(portfolio)
        
        # Identify best and worst performers
        scores = []
        for ticker in portfolio.keys():
            score = self.scores.get(ticker)
            if score:
                scores.append((ticker, score))
        
        scores.sort(key=lambda x: x[1].overall, reverse=True)
        
        best = scores[:3] if scores else []
        worst = scores[-3:] if scores else []
        
        return {
            'portfolio_summary': portfolio_esg,
            'best_esg_performers': [
                {'ticker': t, 'score': s.overall, 'rating': self.get_esg_rating(s.overall)}
                for t, s in best
            ],
            'needs_improvement': [
                {'ticker': t, 'score': s.overall, 'rating': self.get_esg_rating(s.overall)}
                for t, s in worst
            ],
            'recommendations': self._generate_recommendations(portfolio, portfolio_esg),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, portfolio: Dict[str, float], 
                                 esg_summary: Dict) -> List[str]:
        """Generate ESG improvement recommendations"""
        recommendations = []
        
        score = esg_summary.get('portfolio_esg_score', 0)
        
        if score < 6.0:
            recommendations.append(
                "Portfolio ESG score below threshold. Consider increasing allocation to ESG leaders like MSFT, NEE, ENPH"
            )
        
        carbon = esg_summary.get('carbon_intensity', 0)
        if carbon > 100:
            recommendations.append(
                f"High carbon intensity ({carbon:.1f}). Consider divesting from fossil fuel companies"
            )
        
        # Check for controversy
        for ticker in portfolio.keys():
            score = self.scores.get(ticker)
            if score and score.controversy_score >= 3:
                recommendations.append(
                    f"{ticker} has ESG controversies (score: {score.controversy_score}). Consider reducing exposure"
                )
        
        if not recommendations:
            recommendations.append("Portfolio has strong ESG profile. Maintain current allocations.")
        
        return recommendations


# Usage
def get_esg_score(ticker: str) -> Dict:
    """Quick ESG score lookup"""
    system = ESGScoringSystem()
    score = system.get_score(ticker)
    
    if score:
        return {
            'ticker': score.ticker,
            'environmental': score.environmental,
            'social': score.social,
            'governance': score.governance,
            'overall': score.overall,
            'rating': system.get_esg_rating(score.overall),
            'carbon_intensity': score.carbon_intensity,
            'controversy': score.controversy_score
        }
    return {'error': 'No ESG data available'}


def screen_esg_portfolio(holdings: Dict[str, float]) -> Dict:
    """Screen portfolio for ESG compliance"""
    system = ESGScoringSystem()
    return system.screen_portfolio(list(holdings.keys()))
