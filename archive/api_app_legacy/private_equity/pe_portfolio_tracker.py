"""
Private Equity Portfolio Tracker
================================
Track PE fund investments, commitments, distributions
J-curve analysis, TVPI, DPI, RVPI calculations
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum


class FundStage(Enum):
    COMMITTED = "committed"
    INVESTED = "invested"
    HARVESTING = "harvesting"
    LIQUIDATED = "liquidated"


@dataclass
class PEFund:
    name: str
    vintage_year: int
    strategy: str  # 'buyout', 'growth', 'vc', 'special_situations'
    commitment: float
    invested: float
    distributions: float
    nav: float  # Current NAV
    
    def tvpi(self) -> float:
        """Total Value to Paid-In multiple"""
        return (self.distributions + self.nav) / self.invested if self.invested > 0 else 0
    
    def dpi(self) -> float:
        """Distributions to Paid-In (realized return)"""
        return self.distributions / self.invested if self.invested > 0 else 0
    
    def rvpi(self) -> float:
        """Residual Value to Paid-In (unrealized return)"""
        return self.nav / self.invested if self.invested > 0 else 0


class PEPortfolioTracker:
    """Track private equity fund portfolio performance"""
    
    def __init__(self):
        self.funds: List[PEFund] = []
    
    def add_fund(self, fund: PEFund):
        """Add PE fund to portfolio"""
        self.funds.append(fund)
    
    def get_portfolio_metrics(self) -> Dict:
        """Calculate aggregate PE portfolio metrics"""
        if not self.funds:
            return {'error': 'No funds in portfolio'}
        
        total_commitment = sum(f.commitment for f in self.funds)
        total_invested = sum(f.invested for f in self.funds)
        total_distributions = sum(f.distributions for f in self.funds)
        total_nav = sum(f.nav for f in self.funds)
        
        # Portfolio-level multiples
        portfolio_tvpi = (total_distributions + total_nav) / total_invested if total_invested > 0 else 0
        portfolio_dpi = total_distributions / total_invested if total_invested > 0 else 0
        portfolio_rvpi = total_nav / total_invested if total_invested > 0 else 0
        
        # Deployment
        deployment_pct = (total_invested / total_commitment) * 100 if total_commitment > 0 else 0
        
        return {
            'fund_count': len(self.funds),
            'total_commitment': round(total_commitment, 0),
            'total_invested': round(total_invested, 0),
            'total_distributions': round(total_distributions, 0),
            'total_nav': round(total_nav, 0),
            'portfolio_tvpi': round(portfolio_tvpi, 2),
            'portfolio_dpi': round(portfolio_dpi, 2),
            'portfolio_rvpi': round(portfolio_rvpi, 2),
            'deployment_pct': round(deployment_pct, 1),
            'unfunded_commitments': round(total_commitment - total_invested, 0),
            'by_strategy': self._group_by_strategy(),
            'by_vintage': self._group_by_vintage()
        }
    
    def _group_by_strategy(self) -> Dict:
        """Group funds by strategy"""
        strategies = {}
        for fund in self.funds:
            if fund.strategy not in strategies:
                strategies[fund.strategy] = {'funds': 0, 'commitment': 0, 'tvpi': []}
            strategies[fund.strategy]['funds'] += 1
            strategies[fund.strategy]['commitment'] += fund.commitment
            strategies[fund.strategy]['tvpi'].append(fund.tvpi())
        
        # Calculate averages
        for s in strategies:
            tvpi_list = strategies[s]['tvpi']
            strategies[s]['avg_tvpi'] = round(sum(tvpi_list) / len(tvpi_list), 2) if tvpi_list else 0
            strategies[s]['commitment'] = round(strategies[s]['commitment'], 0)
            del strategies[s]['tvpi']
        
        return strategies
    
    def _group_by_vintage(self) -> Dict:
        """Group funds by vintage year"""
        vintages = {}
        for fund in self.funds:
            vintage = fund.vintage_year
            if vintage not in vintages:
                vintages[vintage] = {'funds': 0, 'tvpi_sum': 0}
            vintages[vintage]['funds'] += 1
            vintages[vintage]['tvpi_sum'] += fund.tvpi()
        
        # Calculate averages
        return {
            str(v): {
                'funds': data['funds'],
                'avg_tvpi': round(data['tvpi_sum'] / data['funds'], 2)
            }
            for v, data in vintages.items()
        }
    
    def get_fund_comparison(self, fund_name: str) -> Dict:
        """Compare specific fund to portfolio and benchmarks"""
        fund = next((f for f in self.funds if f.name == fund_name), None)
        if not fund:
            return {'error': 'Fund not found'}
        
        portfolio_metrics = self.get_portfolio_metrics()
        
        return {
            'fund_name': fund_name,
            'vintage': fund.vintage_year,
            'strategy': fund.strategy,
            'fund_tvpi': round(fund.tvpi(), 2),
            'fund_dpi': round(fund.dpi(), 2),
            'fund_rvpi': round(fund.rvpi(), 2),
            'vs_portfolio_tvpi': round(fund.tvpi() - portfolio_metrics.get('portfolio_tvpi', 0), 2),
            'vintage_rank': self._get_vintage_rank(fund),
            'stage': self._determine_stage(fund)
        }
    
    def _get_vintage_rank(self, target_fund: PEFund) -> str:
        """Rank fund within its vintage"""
        same_vintage = [f for f in self.funds if f.vintage_year == target_fund.vintage_year]
        if len(same_vintage) <= 1:
            return 'N/A'
        
        sorted_funds = sorted(same_vintage, key=lambda x: x.tvpi(), reverse=True)
        rank = next(i for i, f in enumerate(sorted_funds, 1) if f.name == target_fund.name)
        
        return f'{rank} of {len(same_vintage)}'
    
    def _determine_stage(self, fund: PEFund) -> str:
        """Determine fund lifecycle stage"""
        age_years = datetime.now().year - fund.vintage_year
        
        if age_years < 3:
            return FundStage.COMMITTED.value
        elif fund.dpi < 0.5 and age_years < 7:
            return FundStage.INVESTED.value
        elif fund.dpi >= 0.5 or fund.nav < fund.invested * 0.3:
            return FundStage.HARVESTING.value
        else:
            return FundStage.INVESTED.value


# Usage
def analyze_pe_portfolio(funds: List[Dict]) -> Dict:
    """Quick PE portfolio analysis"""
    tracker = PEPortfolioTracker()
    
    for f in funds:
        fund = PEFund(
            name=f['name'],
            vintage_year=f['vintage_year'],
            strategy=f['strategy'],
            commitment=f['commitment'],
            invested=f['invested'],
            distributions=f['distributions'],
            nav=f['nav']
        )
        tracker.add_fund(fund)
    
    return tracker.get_portfolio_metrics()


def compare_pe_fund(fund_name: str, portfolio_funds: List[Dict]) -> Dict:
    """Compare specific PE fund performance"""
    tracker = PEPortfolioTracker()
    
    for f in portfolio_funds:
        fund = PEFund(
            name=f['name'],
            vintage_year=f['vintage_year'],
            strategy=f['strategy'],
            commitment=f['commitment'],
            invested=f['invested'],
            distributions=f['distributions'],
            nav=f['nav']
        )
        tracker.add_fund(fund)
    
    return tracker.get_fund_comparison(fund_name)
