"""
Company Data Widgets - Inspired by FactSet Company Data Showcase
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

class CompanyOverviewWidget(BaseWidget):
    """Company overview widget showing key company information"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            symbol = self.config.data_config.get('symbol', 'AAPL')
            
            # Get company data from free data sources
            data_manager = get_free_data_sources_manager()
            
            # Get company info
            company_info = await data_manager.get_company_data(symbol)
            
            # Get market data
            market_data = await data_manager.get_real_time_quotes([symbol])
            
            # Get financial analysis
            financial_analysis = await data_manager.get_financial_analysis(symbol)
            
            # Get SEC filings
            filings = await data_manager.get_sec_filings(symbol, filing_type='10-K', count=5)
            
            company_overview_data = {
                'symbol': symbol,
                'company_info': {
                    'name': company_info.company_name if company_info else symbol,
                    'sector': company_info.sector if company_info else 'Unknown',
                    'industry': company_info.industry if company_info else 'Unknown',
                    'market_cap': company_info.market_cap if company_info else 0,
                    'employees': company_info.fundamentals.get('employees', 0) if company_info else 0,
                    'country': company_info.fundamentals.get('country', 'Unknown') if company_info else 'Unknown',
                    'currency': company_info.fundamentals.get('currency', 'USD') if company_info else 'USD'
                },
                'market_data': {
                    'current_price': market_data[0].price if market_data else 0,
                    'change': market_data[0].additional_data.get('change', 0) if market_data else 0,
                    'change_percent': market_data[0].additional_data.get('change_percent', 0) if market_data else 0,
                    'volume': market_data[0].volume if market_data else 0,
                    'high': market_data[0].additional_data.get('high', 0) if market_data else 0,
                    'low': market_data[0].additional_data.get('low', 0) if market_data else 0,
                    'timestamp': market_data[0].timestamp.isoformat() if market_data else datetime.now().isoformat()
                },
                'key_metrics': self._extract_key_metrics(financial_analysis),
                'recent_filings': [
                    {
                        'type': filing.filing_type,
                        'date': filing.filing_date,
                        'description': filing.description,
                        'url': filing.document_url
                    } for filing in filings[:3]
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=company_overview_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching company overview data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="company-overview-widget" id="{self.config.widget_id}">
            <h3>Company Overview</h3>
            <div class="company-header">
                <!-- Company header info will be rendered here -->
            </div>
            <div class="key-metrics">
                <!-- Key metrics will be rendered here -->
            </div>
            <div class="market-data">
                <!-- Market data will be rendered here -->
            </div>
            <div class="recent-filings">
                <!-- Recent filings will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'company_overview',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    def _extract_key_metrics(self, financial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from financial analysis"""
        metrics = {}
        
        if 'ratios' in financial_analysis:
            for ratio in financial_analysis['ratios']:
                if ratio['ratio_name'] in ['P/E Ratio', 'P/B Ratio', 'Dividend Yield', 'ROE', 'ROA']:
                    metrics[ratio['ratio_name']] = ratio['value']
        
        if 'valuations' in financial_analysis:
            for valuation in financial_analysis['valuations']:
                if valuation['metric'] in ['Market Cap', 'Enterprise Value']:
                    metrics[valuation['metric']] = valuation['value']
        
        return metrics

class FinancialStatementsWidget(BaseWidget):
    """Financial statements widget showing income statement, balance sheet, and cash flow"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            symbol = self.config.data_config.get('symbol', 'AAPL')
            statement_type = self.config.data_config.get('statement_type', 'income')
            period = self.config.data_config.get('period', 'annual')
            
            # Get financial statements from free data sources
            data_manager = get_free_data_sources_manager()
            
            # Get financial statements
            statements = await data_manager.get_financial_statements(symbol, statement_type, period)
            
            # Calculate derived metrics
            derived_metrics = self._calculate_derived_metrics(statements, statement_type)
            
            # Get historical comparison
            historical_comparison = await self._get_historical_comparison(symbol, statement_type, period)
            
            financial_statements_data = {
                'symbol': symbol,
                'statement_type': statement_type,
                'period': period,
                'statements': statements,
                'derived_metrics': derived_metrics,
                'historical_comparison': historical_comparison,
                'analysis': self._analyze_statements(statements, statement_type),
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=financial_statements_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching financial statements data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="financial-statements-widget" id="{self.config.widget_id}">
            <h3>Financial Statements</h3>
            <div class="statement-selector">
                <!-- Statement type selector will be rendered here -->
            </div>
            <div class="statement-table">
                <!-- Financial statements table will be rendered here -->
            </div>
            <div class="derived-metrics">
                <!-- Derived metrics will be rendered here -->
            </div>
            <div class="historical-comparison">
                <!-- Historical comparison chart will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'financial_statements',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    def _calculate_derived_metrics(self, statements: List[Dict[str, Any]], statement_type: str) -> Dict[str, Any]:
        """Calculate derived financial metrics"""
        if not statements:
            return {}
        
        latest_statement = statements[0] if statements else {}
        
        if statement_type == 'income':
            return {
                'gross_margin': (latest_statement.get('gross_profit', 0) / latest_statement.get('revenue', 1)) * 100,
                'operating_margin': (latest_statement.get('operating_income', 0) / latest_statement.get('revenue', 1)) * 100,
                'net_margin': (latest_statement.get('net_income', 0) / latest_statement.get('revenue', 1)) * 100,
                'ebitda_margin': (latest_statement.get('ebitda', 0) / latest_statement.get('revenue', 1)) * 100
            }
        elif statement_type == 'balance':
            return {
                'debt_to_equity': latest_statement.get('total_debt', 0) / latest_statement.get('shareholders_equity', 1),
                'current_ratio': latest_statement.get('current_assets', 0) / latest_statement.get('current_liabilities', 1),
                'quick_ratio': (latest_statement.get('current_assets', 0) - latest_statement.get('inventory', 0)) / latest_statement.get('current_liabilities', 1),
                'asset_turnover': latest_statement.get('revenue', 0) / latest_statement.get('total_assets', 1)
            }
        elif statement_type == 'cash_flow':
            return {
                'operating_cash_flow_ratio': latest_statement.get('operating_cash_flow', 0) / latest_statement.get('net_income', 1),
                'free_cash_flow': latest_statement.get('operating_cash_flow', 0) - latest_statement.get('capital_expenditures', 0),
                'cash_flow_margin': (latest_statement.get('operating_cash_flow', 0) / latest_statement.get('revenue', 1)) * 100
            }
        
        return {}
    
    async def _get_historical_comparison(self, symbol: str, statement_type: str, period: str) -> List[Dict[str, Any]]:
        """Get historical comparison data"""
        # Mock historical data (in production, fetch actual historical statements)
        years = ['2023', '2022', '2021', '2020', '2019']
        historical_data = []
        
        for year in years:
            # Mock data for demonstration
            if statement_type == 'income':
                historical_data.append({
                    'year': year,
                    'revenue': np.random.uniform(1e10, 5e11),
                    'net_income': np.random.uniform(1e9, 5e10),
                    'gross_profit': np.random.uniform(5e9, 2.5e11)
                })
            elif statement_type == 'balance':
                historical_data.append({
                    'year': year,
                    'total_assets': np.random.uniform(2e11, 3e12),
                    'total_debt': np.random.uniform(1e10, 1e11),
                    'shareholders_equity': np.random.uniform(5e10, 2e11)
                })
            elif statement_type == 'cash_flow':
                historical_data.append({
                    'year': year,
                    'operating_cash_flow': np.random.uniform(1e10, 1e11),
                    'capital_expenditures': np.random.uniform(1e9, 1e10),
                    'free_cash_flow': np.random.uniform(5e9, 9e10)
                })
        
        return historical_data
    
    def _analyze_statements(self, statements: List[Dict[str, Any]], statement_type: str) -> Dict[str, Any]:
        """Analyze financial statements"""
        if not statements:
            return {}
        
        latest_statement = statements[0]
        
        if statement_type == 'income':
            return {
                'revenue_growth': 'Positive trend observed over 3 years',
                'profitability': 'Strong margins compared to industry average',
                'efficiency': 'Operating efficiency improving YoY'
            }
        elif statement_type == 'balance':
            return {
                'financial_health': 'Strong balance sheet with moderate leverage',
                'liquidity': 'Good liquidity position with adequate current ratio',
                'capital_structure': 'Well-balanced capital structure'
            }
        elif statement_type == 'cash_flow':
            return {
                'cash_generation': 'Strong operating cash flow generation',
                'investment': 'Consistent capital expenditure for growth',
                'financial_flexibility': 'Good free cash flow for dividends and buybacks'
            }
        
        return {}

class AnalystEstimatesWidget(BaseWidget):
    """Analyst estimates widget showing consensus estimates and forecasts"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            symbol = self.config.data_config.get('symbol', 'AAPL')
            
            # Get analyst estimates (mock implementation)
            estimates_data = await self._get_analyst_estimates(symbol)
            
            # Get price targets
            price_targets = await self._get_price_targets(symbol)
            
            # Get earnings estimates
            earnings_estimates = await self._get_earnings_estimates(symbol)
            
            # Get recommendations
            recommendations = await self._get_analyst_recommendations(symbol)
            
            analyst_estimates_data = {
                'symbol': symbol,
                'consensus_estimates': estimates_data,
                'price_targets': price_targets,
                'earnings_estimates': earnings_estimates,
                'recommendations': recommendations,
                'analyst_coverage': self._get_analyst_coverage(symbol),
                'estimate_accuracy': self._get_estimate_accuracy(symbol),
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=analyst_estimates_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching analyst estimates data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="analyst-estimates-widget" id="{self.config.widget_id}">
            <h3>Analyst Estimates</h3>
            <div class="consensus-estimates">
                <!-- Consensus estimates will be rendered here -->
            </div>
            <div class="price-targets">
                <!-- Price targets will be rendered here -->
            </div>
            <div class="earnings-estimates">
                <!-- Earnings estimates will be rendered here -->
            </div>
            <div class="recommendations">
                <!-- Analyst recommendations will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'analyst_estimates',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _get_analyst_estimates(self, symbol: str) -> Dict[str, Any]:
        """Get consensus analyst estimates"""
        # Mock analyst estimates
        return {
            'revenue_estimate': {
                'current_year': np.random.uniform(1e11, 5e11),
                'next_year': np.random.uniform(1.2e11, 6e11),
                'growth_rate': np.random.uniform(0.05, 0.15)
            },
            'eps_estimate': {
                'current_year': np.random.uniform(5, 15),
                'next_year': np.random.uniform(6, 18),
                'growth_rate': np.random.uniform(0.08, 0.20)
            },
            'ebitda_estimate': {
                'current_year': np.random.uniform(2e10, 1e11),
                'next_year': np.random.uniform(2.5e10, 1.2e11),
                'margin': np.random.uniform(0.15, 0.35)
            }
        }
    
    async def _get_price_targets(self, symbol: str) -> Dict[str, Any]:
        """Get analyst price targets"""
        # Mock price targets
        price_targets = []
        
        for i in range(10):  # 10 analysts
            target_price = np.random.uniform(100, 300)
            price_targets.append({
                'analyst': f'Analyst {i+1}',
                'firm': f'Firm {chr(65+i)}',
                'price_target': target_price,
                'rating': np.random.choice(['Buy', 'Hold', 'Sell']),
                'date': (datetime.now() - timedelta(days=np.random.randint(1, 30))).isoformat()
            })
        
        # Calculate consensus
        consensus_price = np.mean([pt['price_target'] for pt in price_targets])
        
        return {
            'price_targets': price_targets,
            'consensus_target': consensus_price,
            'high_target': max([pt['price_target'] for pt in price_targets]),
            'low_target': min([pt['price_target'] for pt in price_targets]),
            'price_target_distribution': {
                'buy': len([pt for pt in price_targets if pt['rating'] == 'Buy']),
                'hold': len([pt for pt in price_targets if pt['rating'] == 'Hold']),
                'sell': len([pt for pt in price_targets if pt['rating'] == 'Sell'])
            }
        }
    
    async def _get_earnings_estimates(self, symbol: str) -> Dict[str, Any]:
        """Get earnings estimates"""
        # Mock earnings estimates
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        current_year = datetime.now().year
        
        earnings_data = {
            'current_year': {},
            'next_year': {},
            'long_term_growth': np.random.uniform(0.08, 0.15)
        }
        
        for quarter in quarters:
            earnings_data['current_year'][quarter] = {
                'eps_estimate': np.random.uniform(1, 5),
                'revenue_estimate': np.random.uniform(2e10, 8e10),
                'actual_eps': np.random.uniform(0.8, 5.2),  # Some actual vs estimate
                'surprise_percent': np.random.uniform(-0.1, 0.1)
            }
            
            earnings_data['next_year'][quarter] = {
                'eps_estimate': np.random.uniform(1.2, 6),
                'revenue_estimate': np.random.uniform(2.5e10, 1e11)
            }
        
        return earnings_data
    
    async def _get_analyst_recommendations(self, symbol: str) -> Dict[str, Any]:
        """Get analyst recommendations"""
        # Mock recommendations
        recommendations = {
            'buy': np.random.randint(15, 25),
            'hold': np.random.randint(8, 15),
            'sell': np.random.randint(2, 8),
            'total': 35,
            'consensus': 'Buy',
            'price_target_12m': np.random.uniform(150, 250),
            'recommendation_trend': 'Stable',
            'last_updated': (datetime.now() - timedelta(days=7)).isoformat()
        }
        
        # Calculate consensus
        total = recommendations['total']
        if recommendations['buy'] / total > 0.5:
            recommendations['consensus'] = 'Buy'
        elif recommendations['sell'] / total > 0.3:
            recommendations['consensus'] = 'Sell'
        else:
            recommendations['consensus'] = 'Hold'
        
        return recommendations
    
    def _get_analyst_coverage(self, symbol: str) -> Dict[str, Any]:
        """Get analyst coverage information"""
        return {
            'total_analysts': np.random.randint(20, 40),
            'covering_firms': np.random.randint(15, 30),
            'coverage_quality': 'High',
            'last_update': (datetime.now() - timedelta(days=3)).isoformat(),
            'coverage_trend': 'Increasing'
        }
    
    def _get_estimate_accuracy(self, symbol: str) -> Dict[str, Any]:
        """Get estimate accuracy metrics"""
        return {
            'eps_accuracy': np.random.uniform(0.85, 0.95),
            'revenue_accuracy': np.random.uniform(0.80, 0.92),
            'price_target_accuracy': np.random.uniform(0.75, 0.90),
            'overall_rating': 'Excellent',
            'tracking_period': '12 months'
        }

class CompanyFilingsWidget(BaseWidget):
    """Company filings widget showing SEC filings and regulatory documents"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            symbol = self.config.data_config.get('symbol', 'AAPL')
            filing_type = self.config.data_config.get('filing_type', '10-K')
            count = self.config.data_config.get('count', 10)
            
            # Get SEC filings
            data_manager = get_free_data_sources_manager()
            
            # Get company info to get CIK
            company_info = await data_manager.get_company_data(symbol)
            
            # Get filings
            filings = await data_manager.get_sec_filings(symbol, filing_type, count)
            
            # Get filing analysis
            filing_analysis = self._analyze_filings(filings)
            
            # Get filing calendar
            filing_calendar = await self._get_filing_calendar(symbol)
            
            company_filings_data = {
                'symbol': symbol,
                'company_name': company_info.company_name if company_info else symbol,
                'cik': company_info.fundamentals.get('cik', 'Unknown') if company_info else 'Unknown',
                'filings': [
                    {
                        'filing_type': filing.filing_type,
                        'filing_date': filing.filing_date,
                        'accession_number': filing.accession_number,
                        'document_url': filing.document_url,
                        'description': filing.description,
                        'file_size': np.random.randint(100000, 5000000)  # Mock file size
                    } for filing in filings
                ],
                'filing_analysis': filing_analysis,
                'filing_calendar': filing_calendar,
                'next_expected_filings': self._get_next_expected_filings(symbol),
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=company_filings_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching company filings data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="company-filings-widget" id="{self.config.widget_id}">
            <h3>Company Filings</h3>
            <div class="filing-filters">
                <!-- Filing filters will be rendered here -->
            </div>
            <div class="filings-list">
                <!-- Filings list will be rendered here -->
            </div>
            <div class="filing-calendar">
                <!-- Filing calendar will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'company_filings',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    def _analyze_filings(self, filings: List) -> Dict[str, Any]:
        """Analyze filing patterns"""
        if not filings:
            return {}
        
        # Count filing types
        filing_types = {}
        for filing in filings:
            filing_type = filing.filing_type
            filing_types[filing_type] = filing_types.get(filing_type, 0) + 1
        
        # Calculate filing frequency
        latest_filing = filings[0] if filings else None
        filing_frequency = 'Regular'
        
        if latest_filing:
            filing_date = datetime.fromisoformat(latest_filing.filing_date.replace('Z', '+00:00'))
            days_since_last = (datetime.now() - filing_date).days
            
            if days_since_last > 400:
                filing_frequency = 'Delayed'
            elif days_since_last < 300:
                filing_frequency = 'Frequent'
        
        return {
            'total_filings': len(filings),
            'filing_types': filing_types,
            'filing_frequency': filing_frequency,
            'most_common_type': max(filing_types.items(), key=lambda x: x[1])[0] if filing_types else None,
            'compliance_status': 'Good'
        }
    
    async def _get_filing_calendar(self, symbol: str) -> List[Dict[str, Any]]:
        """Get upcoming filing calendar"""
        # Mock filing calendar
        calendar = []
        
        # Common filing types and their typical due dates
        filing_schedule = [
            {'type': '10-Q', 'quarter': 'Q1', 'due_date': '2024-05-15', 'status': 'Expected'},
            {'type': '10-Q', 'quarter': 'Q2', 'due_date': '2024-08-15', 'status': 'Expected'},
            {'type': '10-Q', 'quarter': 'Q3', 'due_date': '2024-11-15', 'status': 'Expected'},
            {'type': '10-K', 'quarter': 'Annual', 'due_date': '2025-03-01', 'status': 'Expected'},
            {'type': '8-K', 'quarter': 'Current', 'due_date': 'As needed', 'status': 'Event-driven'}
        ]
        
        for filing in filing_schedule:
            calendar.append({
                'filing_type': filing['type'],
                'description': f"{filing['type']} - {filing['quarter']}",
                'due_date': filing['due_date'],
                'status': filing['status'],
                'importance': 'High' if filing['type'] in ['10-K', '10-Q'] else 'Medium'
            })
        
        return calendar
    
    def _get_next_expected_filings(self, symbol: str) -> List[Dict[str, Any]]:
        """Get next expected filings"""
        next_filings = [
            {
                'type': '10-Q',
                'quarter': 'Q1 2024',
                'expected_date': '2024-05-15',
                'importance': 'High',
                'days_until': 30
            },
            {
                'type': '10-K',
                'quarter': 'Annual 2024',
                'expected_date': '2025-03-01',
                'importance': 'Very High',
                'days_until': 300
            }
        ]
        
        return next_filings

# Register company data widget templates
def register_company_data_widgets(widget_manager):
    """Register all company data widget templates"""
    
    widget_manager.register_template(WidgetType.COMPANY_DATA, CompanyOverviewWidget)
    widget_manager.register_template(WidgetType.COMPANY_DATA, FinancialStatementsWidget)
    widget_manager.register_template(WidgetType.COMPANY_DATA, AnalystEstimatesWidget)
    widget_manager.register_template(WidgetType.COMPANY_DATA, CompanyFilingsWidget)
