"""
Fund Data Widgets - Inspired by FactSet Fund Data Showcase
Free open-source alternative using free data sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import numpy as np

from .widget_framework import BaseWidget, WidgetConfig, WidgetData, WidgetType
from ..integrations.free.free_data_sources import get_free_data_sources_manager

logger = logging.getLogger(__name__)

class FundOverviewWidget(BaseWidget):
    """Fund overview widget showing key fund information"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            fund_id = self.config.data_config.get('fund_id', 'VFIAX')
            fund_type = self.config.data_config.get('fund_type', 'mutual_fund')
            
            # Get fund data based on type
            if fund_type == 'mutual_fund':
                fund_data = await self._get_mutual_fund_data(fund_id)
            elif fund_type == 'etf':
                fund_data = await self._get_etf_data(fund_id)
            else:
                fund_data = await self._get_generic_fund_data(fund_id)
            
            # Get performance data
            performance_data = await self._get_fund_performance(fund_id, fund_type)
            
            # Get holdings data
            holdings_data = await self._get_fund_holdings(fund_id, fund_type)
            
            # Get expense data
            expense_data = await self._get_fund_expenses(fund_id, fund_type)
            
            fund_overview_data = {
                'fund_id': fund_id,
                'fund_type': fund_type,
                'basic_info': fund_data,
                'performance': performance_data,
                'holdings': holdings_data,
                'expenses': expense_data,
                'risk_metrics': await self._get_fund_risk_metrics(fund_id, fund_type),
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=fund_overview_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching fund overview data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="fund-overview-widget" id="{self.config.widget_id}">
            <h3>Fund Overview</h3>
            <div class="fund-header">
                <!-- Fund header info will be rendered here -->
            </div>
            <div class="performance-summary">
                <!-- Performance summary will be rendered here -->
            </div>
            <div class="holdings-breakdown">
                <!-- Holdings breakdown will be rendered here -->
            </div>
            <div class="expenses-ratios">
                <!-- Expenses and ratios will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'fund_overview',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _get_mutual_fund_data(self, fund_id: str) -> Dict[str, Any]:
        """Get mutual fund data"""
        # Mock mutual fund data (in production, integrate with fund APIs)
        mutual_funds = {
            'VFIAX': {
                'name': 'Vanguard 500 Index Fund Admiral Shares',
                'manager': 'Vanguard',
                'inception_date': '2000-09-22',
                'fund_family': 'Vanguard',
                'category': 'Large Blend',
                'investment_objective': 'Track the performance of the S&P 500 Index',
                'assets_under_management': np.random.uniform(100e9, 500e9),
                'minimum_investment': 3000,
                'expense_ratio': 0.0004,  # 0.04%
                'load': 'No Load'
            },
            'VTSAX': {
                'name': 'Vanguard Total Stock Market Index Fund Admiral Shares',
                'manager': 'Vanguard',
                'inception_date': '1992-04-27',
                'fund_family': 'Vanguard',
                'category': 'Large Blend',
                'investment_objective': 'Track the performance of the CRSP US Total Market Index',
                'assets_under_management': np.random.uniform(200e9, 800e9),
                'minimum_investment': 3000,
                'expense_ratio': 0.0005,  # 0.05%
                'load': 'No Load'
            },
            'VTIAX': {
                'name': 'Vanguard Total International Stock Index Fund Admiral Shares',
                'manager': 'Vanguard',
                'inception_date': '1996-04-29',
                'fund_family': 'Vanguard',
                'category': 'Foreign Large Blend',
                'investment_objective': 'Track the performance of the FTSE Global All Cap ex US Index',
                'assets_under_management': np.random.uniform(50e9, 200e9),
                'minimum_investment': 3000,
                'expense_ratio': 0.0008,  # 0.08%
                'load': 'No Load'
            }
        }
        
        return mutual_funds.get(fund_id, {
            'name': fund_id,
            'manager': 'Unknown',
            'inception_date': '2000-01-01',
            'fund_family': 'Unknown',
            'category': 'Unknown',
            'investment_objective': 'Unknown',
            'assets_under_management': 0,
            'minimum_investment': 1000,
            'expense_ratio': 0.001,
            'load': 'Unknown'
        })
    
    async def _get_etf_data(self, fund_id: str) -> Dict[str, Any]:
        """Get ETF data"""
        # Mock ETF data (in production, integrate with ETF APIs)
        etfs = {
            'SPY': {
                'name': 'SPDR S&P 500 ETF Trust',
                'manager': 'State Street Global Advisors',
                'inception_date': '1993-01-22',
                'fund_family': 'SPDR',
                'category': 'Large Blend',
                'investment_objective': 'Provide investment results that correspond to the price and yield performance of the S&P 500 Index',
                'assets_under_management': np.random.uniform(300e9, 500e9),
                'expense_ratio': 0.000945,  # 0.0945%
                'load': 'No Load',
                'tracking_error': np.random.uniform(0.001, 0.005)
            },
            'QQQ': {
                'name': 'Invesco QQQ Trust',
                'manager': 'Invesco',
                'inception_date': '1999-03-10',
                'fund_family': 'Invesco',
                'category': 'Large Growth',
                'investment_objective': 'Provide investment results that correspond to the price and yield performance of the NASDAQ-100 Index',
                'assets_under_management': np.random.uniform(150e9, 250e9),
                'expense_ratio': 0.0020,  # 0.20%
                'load': 'No Load',
                'tracking_error': np.random.uniform(0.002, 0.008)
            },
            'VTI': {
                'name': 'Vanguard Total Stock Market ETF',
                'manager': 'Vanguard',
                'inception_date': '2001-05-24',
                'fund_family': 'Vanguard',
                'category': 'Large Blend',
                'investment_objective': 'Track the performance of the CRSP US Total Market Index',
                'assets_under_management': np.random.uniform(200e9, 350e9),
                'expense_ratio': 0.0003,  # 0.03%
                'load': 'No Load',
                'tracking_error': np.random.uniform(0.001, 0.004)
            }
        }
        
        return etfs.get(fund_id, {
            'name': fund_id,
            'manager': 'Unknown',
            'inception_date': '2000-01-01',
            'fund_family': 'Unknown',
            'category': 'Unknown',
            'investment_objective': 'Unknown',
            'assets_under_management': 0,
            'expense_ratio': 0.001,
            'load': 'Unknown'
        })
    
    async def _get_generic_fund_data(self, fund_id: str) -> Dict[str, Any]:
        """Get generic fund data"""
        return {
            'name': f'{fund_id} Fund',
            'manager': 'Fund Manager',
            'inception_date': '2000-01-01',
            'fund_family': 'Fund Family',
            'category': 'Mixed',
            'investment_objective': 'Diversified investment strategy',
            'assets_under_management': np.random.uniform(50e9, 200e9),
            'minimum_investment': 1000,
            'expense_ratio': 0.001,
            'load': 'Unknown'
        }
    
    async def _get_fund_performance(self, fund_id: str, fund_type: str) -> Dict[str, Any]:
        """Get fund performance data"""
        # Mock performance data
        return {
            'ytd_return': np.random.uniform(-0.15, 0.25),
            'one_year_return': np.random.uniform(-0.20, 0.30),
            'three_year_return': np.random.uniform(-0.10, 0.40),
            'five_year_return': np.random.uniform(-0.05, 0.50),
            'ten_year_return': np.random.uniform(0.02, 0.12),
            'since_inception': np.random.uniform(0.05, 0.15),
            'annualized_return': np.random.uniform(0.05, 0.15),
            'volatility': np.random.uniform(0.10, 0.25),
            'sharpe_ratio': np.random.uniform(0.3, 1.5),
            'max_drawdown': np.random.uniform(0.05, 0.30),
            'beta': np.random.uniform(0.8, 1.2),
            'alpha': np.random.uniform(-0.02, 0.08),
            'standard_deviation': np.random.uniform(0.12, 0.20)
        }
    
    async def _get_fund_holdings(self, fund_id: str, fund_type: str) -> Dict[str, Any]:
        """Get fund holdings data"""
        # Mock holdings data
        top_holdings = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'weight': np.random.uniform(0.02, 0.08), 'shares': np.random.randint(1000000, 10000000)},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'weight': np.random.uniform(0.02, 0.08), 'shares': np.random.randint(500000, 5000000)},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'weight': np.random.uniform(0.01, 0.06), 'shares': np.random.randint(200000, 2000000)},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'weight': np.random.uniform(0.01, 0.06), 'shares': np.random.randint(300000, 3000000)},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'weight': np.random.uniform(0.01, 0.05), 'shares': np.random.randint(100000, 1000000)},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'weight': np.random.uniform(0.01, 0.05), 'shares': np.random.randint(200000, 2000000)},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'weight': np.random.uniform(0.01, 0.05), 'shares': np.random.randint(100000, 1000000)},
            {'symbol': 'JPM', 'name': 'JP Morgan Chase', 'weight': np.random.uniform(0.01, 0.04), 'shares': np.random.randint(500000, 5000000)},
            {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'weight': np.random.uniform(0.01, 0.04), 'shares': np.random.randint(200000, 2000000)},
            {'symbol': 'V', 'name': 'Visa Inc.', 'weight': np.random.uniform(0.01, 0.04), 'shares': np.random.randint(300000, 3000000)}
        ]
        
        # Calculate total holdings
        total_holdings = len(top_holdings)
        top_10_weight = sum(holding['weight'] for holding in top_holdings)
        
        return {
            'total_holdings': total_holdings,
            'top_10_holdings': top_holdings,
            'top_10_weight': top_10_weight,
            'sector_allocation': self._calculate_sector_allocation(top_holdings),
            'geographic_allocation': self._calculate_geographic_allocation(top_holdings),
            'turnover_rate': np.random.uniform(0.1, 0.8)  # Annual turnover rate
        }
    
    async def _get_fund_expenses(self, fund_id: str, fund_type: str) -> Dict[str, Any]:
        """Get fund expense data"""
        return {
            'expense_ratio': np.random.uniform(0.0003, 0.0025),  # 0.03% to 0.25%
            'management_fee': np.random.uniform(0.0005, 0.0015),
            '12b1_fee': np.random.uniform(0.0001, 0.0025),
            'other_expenses': np.random.uniform(0.0001, 0.001),
            'total_expense_ratio': np.random.uniform(0.0005, 0.003),
            'load_type': np.random.choice(['No Load', 'Front Load', 'Back Load']),
            'load_amount': np.random.uniform(0, 0.05) if np.random.random() > 0.7 else 0,
            'early_redemption_fee': np.random.uniform(0, 0.01) if np.random.random() > 0.8 else 0,
            'minimum_investment': np.random.uniform(100, 5000),
            'minimum_additional': np.random.uniform(50, 1000)
        }
    
    async def _get_fund_risk_metrics(self, fund_id: str, fund_type: str) -> Dict[str, Any]:
        """Get fund risk metrics"""
        return {
            'morningstar_rating': np.random.randint(1, 6),
            'risk_level': np.random.choice(['Low', 'Below Average', 'Average', 'Above Average', 'High']),
            'standard_deviation': np.random.uniform(0.10, 0.25),
            'beta': np.random.uniform(0.7, 1.3),
            'r_squared': np.random.uniform(0.85, 0.98),
            'value_at_risk_95': np.random.uniform(0.02, 0.08),
            'downside_capture': np.random.uniform(0.8, 1.2),
            'upside_capture': np.random.uniform(0.8, 1.2),
            'sortino_ratio': np.random.uniform(0.3, 1.2),
            'information_ratio': np.random.uniform(0.2, 0.8),
            'tracking_error': np.random.uniform(0.001, 0.008) if fund_type == 'etf' else 0
        }
    
    def _calculate_sector_allocation(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate sector allocation"""
        sector_allocation = {}
        
        for holding in holdings:
            sector = self._get_sector_for_symbol(holding['symbol'])
            weight = holding['weight']
            
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += weight
        
        return sector_allocation
    
    def _calculate_geographic_allocation(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate geographic allocation"""
        # Mock geographic allocation
        return {
            'United States': 0.75,
            'Europe': 0.15,
            'Asia': 0.07,
            'Other': 0.03
        }
    
    def _get_sector_for_symbol(self, symbol: str) -> str:
        """Get sector for symbol"""
        sector_mapping = {
            'AAPL': 'Technology',
            'MSFT': 'Technology',
            'GOOGL': 'Technology',
            'AMZN': 'Consumer Discretionary',
            'TSLA': 'Consumer Discretionary',
            'META': 'Technology',
            'NVDA': 'Technology',
            'JPM': 'Financial',
            'JNJ': 'Healthcare',
            'V': 'Financial',
            'PG': 'Consumer Staples',
            'UNH': 'Healthcare',
            'HD': 'Consumer Discretionary',
            'DIS': 'Communication Services',
            'MA': 'Financial'
        }
        
        return sector_mapping.get(symbol, 'Other')

class FundComparisonWidget(BaseWidget):
    """Fund comparison widget for comparing multiple funds"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            fund_ids = self.config.data_config.get('fund_ids', ['VFIAX', 'VTSAX', 'VTIAX'])
            comparison_metrics = self.config.data_config.get('metrics', ['performance', 'risk', 'expenses'])
            
            # Get data for all funds
            comparison_data = {
                'fund_ids': fund_ids,
                'funds': {},
                'comparison_metrics': comparison_metrics,
                'performance_comparison': {},
                'risk_comparison': {},
                'expense_comparison': {},
                'ranking': {},
                'recommendations': {},
                'last_updated': datetime.now().isoformat()
            }
            
            for fund_id in fund_ids:
                # Get fund data for each fund
                fund_data = await self._get_comprehensive_fund_data(fund_id)
                comparison_data['funds'][fund_id] = fund_data
            
            # Generate comparisons
            if 'performance' in comparison_metrics:
                comparison_data['performance_comparison'] = self._compare_performance(comparison_data['funds'])
            
            if 'risk' in comparison_metrics:
                comparison_data['risk_comparison'] = self._compare_risk(comparison_data['funds'])
            
            if 'expenses' in comparison_metrics:
                comparison_data['expense_comparison'] = self._compare_expenses(comparison_data['funds'])
            
            # Generate rankings
            comparison_data['ranking'] = self._rank_funds(comparison_data['funds'])
            
            # Generate recommendations
            comparison_data['recommendations'] = self._generate_comparison_recommendations(comparison_data['funds'])
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=comparison_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching fund comparison data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="fund-comparison-widget" id="{self.config.widget_id}">
            <h3>Fund Comparison</h3>
            <div class="comparison-metrics">
                <!-- Comparison metrics selector will be rendered here -->
            </div>
            <div class="comparison-table">
                <!-- Comparison table will be rendered here -->
            </div>
            <div class="comparison-charts">
                <!-- Comparison charts will be rendered here -->
            </div>
            <div class="recommendations">
                <!-- Recommendations will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'fund_comparison',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _get_comprehensive_fund_data(self, fund_id: str) -> Dict[str, Any]:
        """Get comprehensive fund data"""
        # Mock comprehensive fund data
        return {
            'basic_info': {
                'name': f'{fund_id} Fund',
                'manager': 'Fund Manager',
                'category': 'Mixed'
            },
            'performance': {
                'ytd_return': np.random.uniform(-0.15, 0.25),
                'one_year_return': np.random.uniform(-0.20, 0.30),
                'three_year_return': np.random.uniform(-0.10, 0.40),
                'five_year_return': np.random.uniform(-0.05, 0.50),
                'volatility': np.random.uniform(0.10, 0.25),
                'sharpe_ratio': np.random.uniform(0.3, 1.5)
            },
            'risk': {
                'morningstar_rating': np.random.randint(1, 6),
                'beta': np.random.uniform(0.7, 1.3),
                'standard_deviation': np.random.uniform(0.10, 0.25),
                'risk_level': np.random.choice(['Low', 'Average', 'High'])
            },
            'expenses': {
                'expense_ratio': np.random.uniform(0.0003, 0.0025),
                'load_type': 'No Load',
                'total_expense_ratio': np.random.uniform(0.0005, 0.003)
            },
            'holdings': {
                'total_holdings': np.random.randint(100, 500),
                'top_10_weight': np.random.uniform(0.3, 0.6),
                'turnover_rate': np.random.uniform(0.1, 0.8)
            }
        }
    
    def _compare_performance(self, funds: Dict[str, Any]) -> Dict[str, Any]:
        """Compare fund performance"""
        performance_comparison = {}
        
        for fund_id, fund_data in funds.items():
            performance = fund_data.get('performance', {})
            performance_comparison[fund_id] = {
                'ytd_return': performance.get('ytd_return', 0),
                'one_year_return': performance.get('one_year_return', 0),
                'three_year_return': performance.get('three_year_return', 0),
                'five_year_return': performance.get('five_year_return', 0),
                'volatility': performance.get('volatility', 0),
                'sharpe_ratio': performance.get('sharpe_ratio', 0)
            }
        
        return performance_comparison
    
    def _compare_risk(self, funds: Dict[str, Any]) -> Dict[str, Any]:
        """Compare fund risk metrics"""
        risk_comparison = {}
        
        for fund_id, fund_data in funds.items():
            risk = fund_data.get('risk', {})
            risk_comparison[fund_id] = {
                'morningstar_rating': risk.get('morningstar_rating', 3),
                'beta': risk.get('beta', 1.0),
                'standard_deviation': risk.get('standard_deviation', 0.15),
                'risk_level': risk.get('risk_level', 'Average')
            }
        
        return risk_comparison
    
    def _compare_expenses(self, funds: Dict[str, Any]) -> Dict[str, Any]:
        """Compare fund expenses"""
        expense_comparison = {}
        
        for fund_id, fund_data in funds.items():
            expenses = fund_data.get('expenses', {})
            expense_comparison[fund_id] = {
                'expense_ratio': expenses.get('expense_ratio', 0.001),
                'load_type': expenses.get('load_type', 'No Load'),
                'total_expense_ratio': expenses.get('total_expense_ratio', 0.0015)
            }
        
        return expense_comparison
    
    def _rank_funds(self, funds: Dict[str, Any]) -> Dict[str, List[str]]:
        """Rank funds by different criteria"""
        rankings = {}
        
        # Rank by performance
        performance_ranking = sorted(
            funds.items(),
            key=lambda x: x[1].get('performance', {}).get('sharpe_ratio', 0),
            reverse=True
        )
        rankings['performance'] = [fund[0] for fund in performance_ranking]
        
        # Rank by risk-adjusted returns
        risk_adjusted_ranking = sorted(
            funds.items(),
            key=lambda x: x[1].get('performance', {}).get('sharpe_ratio', 0) / (x[1].get('risk', {}).get('standard_deviation', 0.15)),
            reverse=True
        )
        rankings['risk_adjusted'] = [fund[0] for fund in risk_adjusted_ranking]
        
        # Rank by expenses (lower is better)
        expense_ranking = sorted(
            funds.items(),
            key=lambda x: x[1].get('expenses', {}).get('total_expense_ratio', 0.0015)
        )
        rankings['lowest_expenses'] = [fund[0] for fund in expense_ranking]
        
        return rankings
    
    def _generate_comparison_recommendations(self, funds: Dict[str, Any]) -> Dict[str, str]:
        """Generate comparison recommendations"""
        recommendations = {}
        
        for fund_id, fund_data in funds.items():
            performance = fund_data.get('performance', {})
            risk = fund_data.get('risk', {})
            expenses = fund_data.get('expenses', {})
            
            sharpe_ratio = performance.get('sharpe_ratio', 0)
            risk_level = risk.get('risk_level', 'Average')
            expense_ratio = expenses.get('expense_ratio', 0.001)
            
            if sharpe_ratio > 1.0 and risk_level == 'Low' and expense_ratio < 0.001:
                recommendations[fund_id] = 'Excellent choice - Great risk-adjusted returns with low expenses'
            elif sharpe_ratio > 0.5 and risk_level == 'Average' and expense_ratio < 0.002:
                recommendations[fund_id] = 'Good choice - Solid performance with reasonable expenses'
            elif expense_ratio > 0.002:
                recommendations[fund_id] = 'Consider lower expense alternatives'
            elif risk_level == 'High':
                recommendations[fund_id] = 'High risk fund - Consider your risk tolerance'
            else:
                recommendations[fund_id] = 'Moderate choice - Evaluate against your investment goals'
        
        return recommendations

class FundScreeningWidget(BaseWidget):
    """Fund screening widget for finding funds based on criteria"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            screening_criteria = self.config.data_config.get('criteria', {})
            limit = self.config.data_config.get('limit', 20)
            
            # Get screening results
            screening_results = await self._screen_funds(screening_criteria, limit)
            
            # Generate screening summary
            screening_summary = self._generate_screening_summary(screening_results, screening_criteria)
            
            # Get top recommendations
            top_recommendations = self._get_top_recommendations(screening_results)
            
            fund_screening_data = {
                'criteria': screening_criteria,
                'results': screening_results,
                'summary': screening_summary,
                'top_recommendations': top_recommendations,
                'total_results': len(screening_results),
                'screening_time': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=fund_screening_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching fund screening data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="fund-screening-widget" id="{self.config.widget_id}">
            <h3>Fund Screener</h3>
            <div class="screening-criteria">
                <!-- Screening criteria will be rendered here -->
            </div>
            <div class="screening-results">
                <!-- Screening results will be rendered here -->
            </div>
            <div class="recommendations">
                <!-- Top recommendations will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'fund_screening',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _screen_funds(self, criteria: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Screen funds based on criteria"""
        # Mock fund database
        fund_database = [
            {
                'id': 'VFIAX',
                'name': 'Vanguard 500 Index Fund Admiral Shares',
                'category': 'Large Blend',
                'manager': 'Vanguard',
                'expense_ratio': 0.0004,
                'load_type': 'No Load',
                'minimum_investment': 3000,
                'morningstar_rating': 5,
                'ytd_return': np.random.uniform(-0.15, 0.25),
                'three_year_return': np.random.uniform(-0.10, 0.40),
                'volatility': np.random.uniform(0.10, 0.25),
                'sharpe_ratio': np.random.uniform(0.3, 1.5),
                'beta': np.random.uniform(0.7, 1.3),
                'assets_under_management': np.random.uniform(100e9, 500e9)
            },
            {
                'id': 'VTSAX',
                'name': 'Vanguard Total Stock Market Index Fund Admiral Shares',
                'category': 'Large Blend',
                'manager': 'Vanguard',
                'expense_ratio': 0.0005,
                'load_type': 'No Load',
                'minimum_investment': 3000,
                'morningstar_rating': 4,
                'ytd_return': np.random.uniform(-0.15, 0.25),
                'three_year_return': np.random.uniform(-0.10, 0.40),
                'volatility': np.random.uniform(0.10, 0.25),
                'sharpe_ratio': np.random.uniform(0.3, 1.5),
                'beta': np.random.uniform(0.7, 1.3),
                'assets_under_management': np.random.uniform(200e9, 800e9)
            },
            {
                'id': 'VTIAX',
                'name': 'Vanguard Total International Stock Index Fund Admiral Shares',
                'category': 'Foreign Large Blend',
                'manager': 'Vanguard',
                'expense_ratio': 0.0008,
                'load_type': 'No Load',
                'minimum_investment': 3000,
                'morningstar_rating': 4,
                'ytd_return': np.random.uniform(-0.15, 0.25),
                'three_year_return': np.random.uniform(-0.10, 0.40),
                'volatility': np.random.uniform(0.10, 0.25),
                'sharpe_ratio': np.random.uniform(0.3, 1.5),
                'beta': np.random.uniform(0.7, 1.3),
                'assets_under_management': np.random.uniform(50e9, 200e9)
            },
            {
                'id': 'SPY',
                'name': 'SPDR S&P 500 ETF Trust',
                'category': 'Large Blend',
                'manager': 'State Street Global Advisors',
                'expense_ratio': 0.000945,
                'load_type': 'No Load',
                'minimum_investment': 0,
                'morningstar_rating': 4,
                'ytd_return': np.random.uniform(-0.15, 0.25),
                'three_year_return': np.random.uniform(-0.10, 0.40),
                'volatility': np.random.uniform(0.10, 0.25),
                'sharpe_ratio': np.random.uniform(0.3, 1.5),
                'beta': np.random.uniform(0.7, 1.3),
                'assets_under_management': np.random.uniform(300e9, 500e9)
            },
            {
                'id': 'QQQ',
                'name': 'Invesco QQQ Trust',
                'category': 'Large Growth',
                'manager': 'Invesco',
                'expense_ratio': 0.0020,
                'load_type': 'No Load',
                'minimum_investment': 0,
                'morningstar_rating': 4,
                'ytd_return': np.random.uniform(-0.15, 0.25),
                'three_year_return': np.random.uniform(-0.10, 0.40),
                'volatility': np.random.uniform(0.10, 0.25),
                'sharpe_ratio': np.random.uniform(0.3, 1.5),
                'beta': np.random.uniform(0.7, 1.3),
                'assets_under_management': np.random.uniform(150e9, 250e9)
            }
        ]
        
        # Apply screening criteria
        filtered_funds = []
        
        for fund in fund_database:
            if self._fund_meets_criteria(fund, criteria):
                filtered_funds.append(fund)
        
        # Sort by criteria priority (default: Sharpe ratio)
        sort_by = criteria.get('sort_by', 'sharpe_ratio')
        reverse_sort = criteria.get('sort_order', 'desc') == 'desc'
        
        if sort_by == 'sharpe_ratio':
            filtered_funds.sort(key=lambda x: x['sharpe_ratio'], reverse=reverse_sort)
        elif sort_by == 'expense_ratio':
            filtered_funds.sort(key=lambda x: x['expense_ratio'], reverse=not reverse_sort)
        elif sort_by == 'performance':
            filtered_funds.sort(key=lambda x: x['three_year_return'], reverse=reverse_sort)
        elif sort_by == 'morningstar_rating':
            filtered_funds.sort(key=lambda x: x['morningstar_rating'], reverse=reverse_sort)
        
        return filtered_funds[:limit]
    
    def _fund_meets_criteria(self, fund: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if fund meets screening criteria"""
        # Category filter
        if 'category' in criteria and fund['category'] not in criteria['category']:
            return False
        
        # Manager filter
        if 'manager' in criteria and fund['manager'] not in criteria['manager']:
            return False
        
        # Expense ratio filter
        if 'max_expense_ratio' in criteria and fund['expense_ratio'] > criteria['max_expense_ratio']:
            return False
        
        # Load type filter
        if 'load_type' in criteria and fund['load_type'] not in criteria['load_type']:
            return False
        
        # Minimum investment filter
        if 'max_minimum_investment' in criteria and fund['minimum_investment'] > criteria['max_minimum_investment']:
            return False
        
        # Morningstar rating filter
        if 'min_morningstar_rating' in criteria and fund['morningstar_rating'] < criteria['min_morningstar_rating']:
            return False
        
        # Performance filter
        if 'min_three_year_return' in criteria and fund['three_year_return'] < criteria['min_three_year_return']:
            return False
        
        # Volatility filter
        if 'max_volatility' in criteria and fund['volatility'] > criteria['max_volatility']:
            return False
        
        # Sharpe ratio filter
        if 'min_sharpe_ratio' in criteria and fund['sharpe_ratio'] < criteria['min_sharpe_ratio']:
            return False
        
        # Beta filter
        if 'max_beta' in criteria and fund['beta'] > criteria['max_beta']:
            return False
        
        return True
    
    def _generate_screening_summary(self, results: List[Dict[str, Any]], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Generate screening summary"""
        if not results:
            return {'total_results': 0, 'message': 'No funds match your criteria'}
        
        # Calculate summary statistics
        avg_expense_ratio = sum(fund['expense_ratio'] for fund in results) / len(results)
        avg_sharpe_ratio = sum(fund['sharpe_ratio'] for fund in results) / len(results)
        avg_morningstar_rating = sum(fund['morningstar_rating'] for fund in results) / len(results)
        
        return {
            'total_results': len(results),
            'criteria_applied': criteria,
            'average_metrics': {
                'expense_ratio': avg_expense_ratio,
                'sharpe_ratio': avg_sharpe_ratio,
                'morningstar_rating': avg_morningstar_rating
            },
            'category_distribution': self._get_category_distribution(results),
            'top_categories': self._get_top_categories(results)
        }
    
    def _get_top_recommendations(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top recommendations from screening results"""
        # Return top 5 funds with additional analysis
        top_funds = results[:5]
        
        recommendations = []
        for i, fund in enumerate(top_funds):
            recommendation = {
                'rank': i + 1,
                'fund_id': fund['id'],
                'name': fund['name'],
                'reason': self._get_recommendation_reason(fund),
                'score': self._calculate_fund_score(fund),
                'highlights': self._get_fund_highlights(fund)
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def _get_category_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get category distribution"""
        distribution = {}
        
        for fund in results:
            category = fund['category']
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution
    
    def _get_top_categories(self, results: List[Dict[str, Any]]) -> List[str]:
        """Get top categories"""
        distribution = self._get_category_distribution(results)
        sorted_categories = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        return [category[0] for category in sorted_categories[:5]]
    
    def _get_recommendation_reason(self, fund: Dict[str, Any]) -> str:
        """Get recommendation reason for fund"""
        reasons = []
        
        if fund['morningstar_rating'] >= 4:
            reasons.append('High Morningstar rating')
        
        if fund['sharpe_ratio'] > 1.0:
            reasons.append('Excellent risk-adjusted returns')
        
        if fund['expense_ratio'] < 0.001:
            reasons.append('Very low expenses')
        
        if fund['three_year_return'] > 0.15:
            reasons.append('Strong historical performance')
        
        if fund['volatility'] < 0.15:
            reasons.append('Low volatility')
        
        if not reasons:
            reasons.append('Meets your criteria')
        
        return ', '.join(reasons)
    
    def _calculate_fund_score(self, fund: Dict[str, Any]) -> float:
        """Calculate overall fund score"""
        score = 0
        
        # Morningstar rating (0-5 points)
        score += fund['morningstar_rating']
        
        # Sharpe ratio (0-2 points)
        score += min(fund['sharpe_ratio'] * 2, 2)
        
        # Expense ratio (0-1 point, lower is better)
        score += max(0, 1 - fund['expense_ratio'] * 500)
        
        # Performance (0-1 point)
        score += min(fund['three_year_return'] * 3, 1)
        
        return score
    
    def _get_fund_highlights(self, fund: Dict[str, Any]) -> List[str]:
        """Get fund highlights"""
        highlights = []
        
        if fund['morningstar_rating'] >= 5:
            highlights.append('Gold Morningstar Rating')
        
        if fund['expense_ratio'] < 0.0005:
            highlights.append('Ultra-Low Expenses')
        
        if fund['sharpe_ratio'] > 1.2:
            highlights.append('Excellent Risk-Adjusted Returns')
        
        if fund['assets_under_management'] > 500e9:
            highlights.append('Large AUM')
        
        if fund['load_type'] == 'No Load':
            highlights.append('No Load')
        
        if fund['beta'] < 0.8:
            highlights.append('Low Market Risk')
        
        return highlights

# Register fund data widget templates
def register_fund_data_widgets(widget_manager):
    """Register all fund data widget templates"""
    
    widget_manager.register_template(WidgetType.FUND_DATA, FundOverviewWidget)
    widget_manager.register_template(WidgetType.FUND_DATA, FundComparisonWidget)
    widget_manager.register_template(WidgetType.FUND_DATA, FundScreeningWidget)
