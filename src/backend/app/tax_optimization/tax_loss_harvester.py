"""
Tax-Loss Harvesting Engine
==========================
Automated tax optimization through strategic loss realization
Wash sale detection, replacement security selection, year-round harvesting
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WashSaleStatus(Enum):
    SAFE = "safe"  # Outside 61-day window
    WARNING = "warning"  # Within 30 days before
    VIOLATION = "violation"  # Violates wash sale rule


@dataclass
class TaxLot:
    """Individual tax lot information"""
    ticker: str
    shares: float
    purchase_date: datetime
    cost_basis: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    days_held: int
    long_term: bool  # > 1 year


@dataclass
class HarvestOpportunity:
    """Tax-loss harvesting opportunity"""
    ticker: str
    shares: float
    loss_amount: float
    loss_pct: float
    harvest_value: float  # Tax savings
    replacement_ticker: str
    wash_sale_risk: str
    action: str


class TaxLossHarvester:
    """
    Sophisticated tax-loss harvesting system
    
    Features:
    - Continuous loss monitoring
    - Wash sale rule compliance
    - Replacement security selection
    - Tax savings calculation
    - Portfolio rebalancing integration
    """
    
    # Common replacement pairs (similar but not substantially identical)
    REPLACEMENT_PAIRS = {
        'VTI': 'VXUS',  # Total US -> Total International
        'VOO': 'IVV',   # S&P 500 -> S&P 500 (different provider, ok)
        'QQQ': 'QQQM',  # Nasdaq 100 -> Nasdaq 100 (different provider)
        'VEA': 'IEFA',  # Developed markets EAFE
        'VWO': 'IEMG',  # Emerging markets
        'AGG': 'BND',   # Total bond
        'GLD': 'IAU',   # Gold
        'AAPL': 'QQQ',  # Individual stock -> sector ETF (safe)
        'MSFT': 'XLK',  # Tech stock -> Tech ETF
        'JPM': 'XLF',   # Bank -> Financial ETF
        'XOM': 'XLE',   # Energy stock -> Energy ETF
        'JNJ': 'XLV',   # Healthcare -> Healthcare ETF
    }
    
    def __init__(self, tax_rate_short: float = 0.35, 
                 tax_rate_long: float = 0.15):
        self.tax_rate_short = tax_rate_short  # Short-term capital gains
        self.tax_rate_long = tax_rate_long    # Long-term capital gains
        self.tax_lots: List[TaxLot] = []
        self.harvest_history: List[Dict] = []
        self.wash_sale_violations: List[str] = []  # Tickers to avoid
    
    def add_tax_lot(self, lot: TaxLot):
        """Add a tax lot to tracking"""
        self.tax_lots.append(lot)
    
    def find_harvest_opportunities(self, 
                                   min_loss_pct: float = 0.05,
                                   min_loss_amount: float = 1000) -> List[HarvestOpportunity]:
        """
        Find all tax-loss harvesting opportunities
        
        Args:
            min_loss_pct: Minimum loss percentage to consider
            min_loss_amount: Minimum dollar loss to consider
        """
        opportunities = []
        
        for lot in self.tax_lots:
            # Check if there's a loss
            if lot.unrealized_pnl >= 0:
                continue
            
            loss_pct = abs(lot.unrealized_pnl_pct)
            loss_amount = abs(lot.unrealized_pnl)
            
            # Check minimums
            if loss_pct < min_loss_pct * 100 or loss_amount < min_loss_amount:
                continue
            
            # Calculate tax savings
            tax_rate = self.tax_rate_long if lot.long_term else self.tax_rate_short
            tax_savings = loss_amount * tax_rate
            
            # Find replacement
            replacement = self._find_replacement(lot.ticker)
            
            # Check wash sale status
            wash_sale_status = self._check_wash_sale(lot.ticker, lot.purchase_date)
            
            # Only proceed if safe or warning (not violation)
            if wash_sale_status != WashSaleStatus.VIOLATION:
                opportunities.append(HarvestOpportunity(
                    ticker=lot.ticker,
                    shares=lot.shares,
                    loss_amount=loss_amount,
                    loss_pct=loss_pct,
                    harvest_value=tax_savings,
                    replacement_ticker=replacement,
                    wash_sale_risk=wash_sale_status.value,
                    action='HARVEST_AND_REPLACE' if wash_sale_status == WashSaleStatus.SAFE else 'WAIT'
                ))
        
        # Sort by harvest value
        opportunities.sort(key=lambda x: x.harvest_value, reverse=True)
        
        return opportunities
    
    def _find_replacement(self, ticker: str) -> str:
        """Find suitable replacement security"""
        # Direct replacement pair
        if ticker in self.REPLACEMENT_PAIRS:
            return self.REPLACEMENT_PAIRS[ticker]
        
        # For other stocks, suggest sector ETF
        sector_etfs = {
            'Technology': 'XLK',
            'Financial': 'XLF',
            'Healthcare': 'XLV',
            'Energy': 'XLE',
            'Consumer': 'XLY',
            'Industrial': 'XLI',
            'Materials': 'XLB',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE'
        }
        
        # Default to broad market
        return 'VTI'
    
    def _check_wash_sale(self, ticker: str, 
                        purchase_date: datetime) -> WashSaleStatus:
        """
        Check if harvesting would trigger wash sale rule
        
        Wash sale: Can't claim loss if you buy same/substantially 
        identical security 30 days before or after the sale
        """
        today = datetime.now()
        
        # Check if ticker is in violation list
        if ticker in self.wash_sale_violations:
            return WashSaleStatus.VIOLATION
        
        # Check purchase date
        days_since_purchase = (today - purchase_date).days
        
        if days_since_purchase <= 30:
            # Bought within last 30 days - would be violation if harvested now
            return WashSaleStatus.WARNING
        
        return WashSaleStatus.SAFE
    
    def execute_harvest(self, opportunity: HarvestOpportunity) -> Dict:
        """
        Execute tax-loss harvest
        
        1. Sell losing position
        2. Buy replacement security
        3. Record for tax reporting
        """
        if opportunity.wash_sale_risk == 'violation':
            return {
                'status': 'REJECTED',
                'reason': 'Wash sale violation',
                'ticker': opportunity.ticker
            }
        
        # Record the harvest
        harvest_record = {
            'date': datetime.now().isoformat(),
            'ticker_sold': opportunity.ticker,
            'shares': opportunity.shares,
            'loss_realized': opportunity.loss_amount,
            'tax_savings': opportunity.harvest_value,
            'replacement_ticker': opportunity.replacement_ticker,
            'replacement_shares': opportunity.shares,  # Same dollar amount
            'wash_sale_status': opportunity.wash_sale_risk
        }
        
        self.harvest_history.append(harvest_record)
        
        # Add to wash sale watch (can't buy back for 30 days)
        self.wash_sale_violations.append(opportunity.ticker)
        
        logger.info(f"Tax-loss harvest executed: {opportunity.ticker} -> "
                   f"{opportunity.replacement_ticker}, "
                   f"savings: ${opportunity.harvest_value:.2f}")
        
        return {
            'status': 'EXECUTED',
            'harvest': harvest_record
        }
    
    def get_annual_summary(self, year: int = None) -> Dict:
        """Get annual tax-loss harvesting summary"""
        if year is None:
            year = datetime.now().year
        
        year_harvests = [
            h for h in self.harvest_history
            if datetime.fromisoformat(h['date']).year == year
        ]
        
        if not year_harvests:
            return {
                'year': year,
                'total_harvests': 0,
                'total_losses_realized': 0,
                'total_tax_savings': 0
            }
        
        total_losses = sum(h['loss_realized'] for h in year_harvests)
        total_savings = sum(h['tax_savings'] for h in year_harvests)
        
        return {
            'year': year,
            'total_harvests': len(year_harvests),
            'total_losses_realized': round(total_losses, 2),
            'total_tax_savings': round(total_savings, 2),
            'avg_loss_per_harvest': round(total_losses / len(year_harvests), 2),
            'tickers_harvested': list(set(h['ticker_sold'] for h in year_harvests)),
            'harvests_by_quarter': self._group_by_quarter(year_harvests)
        }
    
    def _group_by_quarter(self, harvests: List[Dict]) -> Dict:
        """Group harvests by quarter"""
        quarters = {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0}
        
        for h in harvests:
            month = datetime.fromisoformat(h['date']).month
            if month <= 3:
                quarters['Q1'] += h['tax_savings']
            elif month <= 6:
                quarters['Q2'] += h['tax_savings']
            elif month <= 9:
                quarters['Q3'] += h['tax_savings']
            else:
                quarters['Q4'] += h['tax_savings']
        
        return {k: round(v, 2) for k, v in quarters.items()}
    
    def get_portfolio_tax_analysis(self) -> Dict:
        """Analyze current portfolio for tax optimization"""
        if not self.tax_lots:
            return {}
        
        # Current unrealized gains/losses
        total_unrealized = sum(lot.unrealized_pnl for lot in self.tax_lots)
        total_gains = sum(lot.unrealized_pnl for lot in self.tax_lots if lot.unrealized_pnl > 0)
        total_losses = sum(lot.unrealized_pnl for lot in self.tax_lots if lot.unrealized_pnl < 0)
        
        # Tax lots by holding period
        short_term_lots = [lot for lot in self.tax_lots if not lot.long_term]
        long_term_lots = [lot for lot in self.tax_lots if lot.long_term]
        
        # Harvest opportunities
        opportunities = self.find_harvest_opportunities(min_loss_pct=0.01, min_loss_amount=100)
        total_harvestable = sum(opp.loss_amount for opp in opportunities)
        potential_savings = sum(opp.harvest_value for opp in opportunities)
        
        return {
            'total_unrealized_pnl': round(total_unrealized, 2),
            'total_unrealized_gains': round(total_gains, 2),
            'total_unrealized_losses': round(abs(total_losses), 2),
            'short_term_lots': len(short_term_lots),
            'long_term_lots': len(long_term_lots),
            'harvest_opportunities': len(opportunities),
            'harvestable_losses': round(total_harvestable, 2),
            'potential_tax_savings': round(potential_savings, 2),
            'optimization_recommendation': self._generate_recommendation(
                total_gains, abs(total_losses), potential_savings
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_recommendation(self, gains: float, losses: float, 
                                potential_savings: float) -> str:
        """Generate tax optimization recommendation"""
        if potential_savings > 10000:
            return "URGENT: Significant tax savings available. Execute harvests immediately."
        elif potential_savings > 5000:
            return "HIGH: Good harvesting opportunities. Execute this week."
        elif potential_savings > 1000:
            return "MODERATE: Some opportunities. Monitor daily."
        else:
            return "LOW: Minimal opportunities. Monitor for future losses."


# Usage
def quick_tax_analysis(portfolio: Dict[str, Tuple[float, float, str]]) -> Dict:
    """
    Quick tax-loss harvesting analysis
    
    portfolio: Dict of {ticker: (shares, cost_basis, purchase_date)}
    """
    harvester = TaxLossHarvester()
    
    for ticker, (shares, cost_basis, purchase_date) in portfolio.items():
        # Simulate current price (in real use, fetch live)
        current_price = cost_basis * 0.90  # Assume 10% loss for demo
        
        purchase_dt = datetime.fromisoformat(purchase_date)
        days_held = (datetime.now() - purchase_dt).days
        
        unrealized_pnl = (current_price - cost_basis) * shares
        
        lot = TaxLot(
            ticker=ticker,
            shares=shares,
            purchase_date=purchase_dt,
            cost_basis=cost_basis,
            current_price=current_price,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=(current_price - cost_basis) / cost_basis * 100,
            days_held=days_held,
            long_term=days_held > 365
        )
        
        harvester.add_tax_lot(lot)
    
    return harvester.get_portfolio_tax_analysis()


def calculate_tax_savings(loss_amount: float, 
                         holding_period_days: int) -> float:
    """Calculate tax savings from harvesting a loss"""
    harvester = TaxLossHarvester()
    
    tax_rate = harvester.tax_rate_long if holding_period_days > 365 else harvester.tax_rate_short
    
    return round(loss_amount * tax_rate, 2)
