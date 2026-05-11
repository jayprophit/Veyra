"""
Demo Portals for Veyra Widgets
FactSet-inspired demo portals using free data sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import uuid

from .widget_framework import get_widget_manager, WidgetConfig, WidgetType, WidgetSize
from .market_data_widgets import register_market_data_widgets
from .portfolio_analytics_widgets import register_portfolio_analytics_widgets
from .news_widgets import register_news_widgets
from .company_data_widgets import register_company_data_widgets
from .fund_data_widgets import register_fund_data_widgets

logger = logging.getLogger(__name__)

class DemoPortalManager:
    """Manager for creating and managing demo portals"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self.widget_manager = get_widget_manager(data_manager)
        self.register_all_widgets()
        self.portals = {}
        
        logger.info("Demo Portal Manager initialized")
    
    def register_all_widgets(self):
        """Register all widget types"""
        register_market_data_widgets(self.widget_manager)
        register_portfolio_analytics_widgets(self.widget_manager)
        register_news_widgets(self.widget_manager)
        register_company_data_widgets(self.widget_manager)
        register_fund_data_widgets(self.widget_manager)
    
    async def create_market_data_demo_portal(self) -> Dict[str, Any]:
        """Create Market Data Demo Portal"""
        portal_id = f"market_data_demo_{uuid.uuid4().hex[:8]}"
        
        # Define widgets for market data portal
        widgets_config = [
            {
                'widget_id': 'market_overview',
                'widget_type': WidgetType.MARKET_DATA,
                'title': 'Market Overview',
                'size': WidgetSize.LARGE,
                'position': {'x': 0, 'y': 0, 'width': 12, 'height': 4},
                'data_config': {
                    'indices': ['^GSPC', '^DJI', '^IXIC', '^RUT']
                }
            },
            {
                'widget_id': 'asset_screener',
                'widget_type': WidgetType.MARKET_DATA,
                'title': 'Asset Screener',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'criteria': {
                        'sectors': ['Technology', 'Healthcare'],
                        'market_cap_range': (1e9, 100e9),
                        'pe_ratio_range': (10, 30)
                    }
                }
            },
            {
                'widget_id': 'watchlist',
                'widget_type': WidgetType.MARKET_DATA,
                'title': 'Watchlist',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 6, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
                }
            },
            {
                'widget_id': 'market_depth',
                'widget_type': WidgetType.MARKET_DATA,
                'title': 'Market Depth',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 7, 'width': 6, 'height': 3},
                'data_config': {
                    'symbol': 'AAPL'
                }
            },
            {
                'widget_id': 'technical_analysis',
                'widget_type': WidgetType.MARKET_DATA,
                'title': 'Technical Analysis',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 6, 'y': 7, 'width': 6, 'height': 3},
                'data_config': {
                    'symbol': 'AAPL',
                    'indicators': ['sma', 'rsi', 'macd', 'bollinger']
                }
            }
        ]
        
        # Create widgets
        widgets = []
        for widget_config in widgets_config:
            config = WidgetConfig(
                widget_id=widget_config['widget_id'],
                widget_type=widget_config['widget_type'],
                title=widget_config['title'],
                size=widget_config['size'],
                position=widget_config['position'],
                data_config=widget_config['data_config']
            )
            
            widget = self.widget_manager.create_widget(config)
            widgets.append(widget)
        
        # Fetch widget data
        widget_data = {}
        for widget in widgets:
            try:
                data = await widget.get_data()
                widget_data[widget.config.widget_id] = data
            except Exception as e:
                logger.error(f"Error fetching data for widget {widget.config.widget_id}: {e}")
                widget_data[widget.config.widget_id] = {
                    'data': {},
                    'status': 'error',
                    'error_message': str(e)
                }
        
        portal = {
            'portal_id': portal_id,
            'portal_name': 'Market Data Demo Portal',
            'portal_type': 'market_data',
            'description': 'Comprehensive market data portal with real-time quotes, screening, and technical analysis',
            'widgets': widgets_config,
            'widget_data': widget_data,
            'layout': {
                'type': 'grid',
                'columns': 12,
                'row_height': 60
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        self.portals[portal_id] = portal
        return portal
    
    async def create_portfolio_analytics_demo_portal(self) -> Dict[str, Any]:
        """Create Portfolio Analytics Demo Portal"""
        portal_id = f"portfolio_analytics_demo_{uuid.uuid4().hex[:8]}"
        
        # Define widgets for portfolio analytics portal
        widgets_config = [
            {
                'widget_id': 'portfolio_performance',
                'widget_type': WidgetType.PORTFOLIO_ANALYTICS,
                'title': 'Portfolio Performance',
                'size': WidgetSize.LARGE,
                'position': {'x': 0, 'y': 0, 'width': 12, 'height': 4},
                'data_config': {
                    'portfolio_id': 'demo_portfolio_1',
                    'benchmark': 'SPY'
                }
            },
            {
                'widget_id': 'holdings_breakdown',
                'widget_type': WidgetType.PORTFOLIO_ANALYTICS,
                'title': 'Holdings Breakdown',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'portfolio_id': 'demo_portfolio_1'
                }
            },
            {
                'widget_id': 'risk_analysis',
                'widget_type': WidgetType.PORTFOLIO_ANALYTICS,
                'title': 'Risk Analysis',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 6, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'portfolio_id': 'demo_portfolio_1'
                }
            },
            {
                'widget_id': 'attribution_analysis',
                'widget_type': WidgetType.PORTFOLIO_ANALYTICS,
                'title': 'Attribution Analysis',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 7, 'width': 6, 'height': 3},
                'data_config': {
                    'portfolio_id': 'demo_portfolio_1',
                    'benchmark': 'SPY'
                }
            },
            {
                'widget_id': 'comparison',
                'widget_type': WidgetType.PORTFOLIO_ANALYTICS,
                'title': 'Portfolio Comparison',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 6, 'y': 7, 'width': 6, 'height': 3},
                'data_config': {
                    'portfolio_ids': ['demo_portfolio_1', 'demo_portfolio_2'],
                    'benchmark': 'SPY'
                }
            }
        ]
        
        # Create widgets and fetch data
        widgets = []
        widget_data = {}
        
        for widget_config in widgets_config:
            config = WidgetConfig(
                widget_id=widget_config['widget_id'],
                widget_type=widget_config['widget_type'],
                title=widget_config['title'],
                size=widget_config['size'],
                position=widget_config['position'],
                data_config=widget_config['data_config']
            )
            
            widget = self.widget_manager.create_widget(config)
            widgets.append(widget)
            
            try:
                data = await widget.get_data()
                widget_data[widget.config.widget_id] = data
            except Exception as e:
                logger.error(f"Error fetching data for widget {widget.config.widget_id}: {e}")
                widget_data[widget.config.widget_id] = {
                    'data': {},
                    'status': 'error',
                    'error_message': str(e)
                }
        
        portal = {
            'portal_id': portal_id,
            'portal_name': 'Portfolio Analytics Demo Portal',
            'portal_type': 'portfolio_analytics',
            'description': 'Industry-leading portfolio analysis tools with performance, risk, and attribution analytics',
            'widgets': widgets_config,
            'widget_data': widget_data,
            'layout': {
                'type': 'grid',
                'columns': 12,
                'row_height': 60
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        self.portals[portal_id] = portal
        return portal
    
    async def create_news_demo_portal(self) -> Dict[str, Any]:
        """Create News Demo Portal"""
        portal_id = f"news_demo_{uuid.uuid4().hex[:8]}"
        
        # Define widgets for news portal
        widgets_config = [
            {
                'widget_id': 'market_news',
                'widget_type': WidgetType.NEWS,
                'title': 'Market News',
                'size': WidgetSize.LARGE,
                'position': {'x': 0, 'y': 0, 'width': 12, 'height': 4},
                'data_config': {
                    'sources': ['reuters', 'bloomberg', 'marketwatch'],
                    'limit': 15
                }
            },
            {
                'widget_id': 'company_news',
                'widget_type': WidgetType.NEWS,
                'title': 'Company News',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'symbols': ['AAPL', 'MSFT', 'GOOGL'],
                    'limit': 5
                }
            },
            {
                'widget_id': 'news_alerts',
                'widget_type': WidgetType.NEWS,
                'title': 'News Alerts',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 6, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'keywords': ['earnings', 'merger', 'acquisition', 'dividend'],
                    'alert_threshold': 0.7
                }
            }
        ]
        
        # Create widgets and fetch data
        widgets = []
        widget_data = {}
        
        for widget_config in widgets_config:
            config = WidgetConfig(
                widget_id=widget_config['widget_id'],
                widget_type=widget_config['widget_type'],
                title=widget_config['title'],
                size=widget_config['size'],
                position=widget_config['position'],
                data_config=widget_config['data_config']
            )
            
            widget = self.widget_manager.create_widget(config)
            widgets.append(widget)
            
            try:
                data = await widget.get_data()
                widget_data[widget.config.widget_id] = data
            except Exception as e:
                logger.error(f"Error fetching data for widget {widget.config.widget_id}: {e}")
                widget_data[widget.config.widget_id] = {
                    'data': {},
                    'status': 'error',
                    'error_message': str(e)
                }
        
        portal = {
            'portal_id': portal_id,
            'portal_name': 'News Demo Portal',
            'portal_type': 'news',
            'description': 'Real-time news and market updates from multiple sources',
            'widgets': widgets_config,
            'widget_data': widget_data,
            'layout': {
                'type': 'grid',
                'columns': 12,
                'row_height': 60
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        self.portals[portal_id] = portal
        return portal
    
    async def create_company_data_demo_portal(self) -> Dict[str, Any]:
        """Create Company Data Demo Portal"""
        portal_id = f"company_data_demo_{uuid.uuid4().hex[:8]}"
        
        # Define widgets for company data portal
        widgets_config = [
            {
                'widget_id': 'company_overview',
                'widget_type': WidgetType.COMPANY_DATA,
                'title': 'Company Overview',
                'size': WidgetSize.LARGE,
                'position': {'x': 0, 'y': 0, 'width': 12, 'height': 4},
                'data_config': {
                    'symbol': 'AAPL'
                }
            },
            {
                'widget_id': 'financial_statements',
                'widget_type': WidgetType.COMPANY_DATA,
                'title': 'Financial Statements',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'symbol': 'AAPL',
                    'statement_type': 'income',
                    'period': 'annual'
                }
            },
            {
                'widget_id': 'analyst_estimates',
                'widget_type': WidgetType.COMPANY_DATA,
                'title': 'Analyst Estimates',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 6, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'symbol': 'AAPL'
                }
            },
            {
                'widget_id': 'company_filings',
                'widget_type': WidgetType.COMPANY_DATA,
                'title': 'SEC Filings',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 7, 'width': 6, 'height': 3},
                'data_config': {
                    'symbol': 'AAPL',
                    'filing_type': '10-K',
                    'count': 5
                }
            }
        ]
        
        # Create widgets and fetch data
        widgets = []
        widget_data = {}
        
        for widget_config in widgets_config:
            config = WidgetConfig(
                widget_id=widget_config['widget_id'],
                widget_type=widget_config['widget_type'],
                title=widget_config['title'],
                size=widget_config['size'],
                position=widget_config['position'],
                data_config=widget_config['data_config']
            )
            
            widget = self.widget_manager.create_widget(config)
            widgets.append(widget)
            
            try:
                data = await widget.get_data()
                widget_data[widget.config.widget_id] = data
            except Exception as e:
                logger.error(f"Error fetching data for widget {widget.config.widget_id}: {e}")
                widget_data[widget.config.widget_id] = {
                    'data': {},
                    'status': 'error',
                    'error_message': str(e)
                }
        
        portal = {
            'portal_id': portal_id,
            'portal_name': 'Company Data Demo Portal',
            'portal_type': 'company_data',
            'description': 'Comprehensive company data including fundamentals, estimates, and SEC filings',
            'widgets': widgets_config,
            'widget_data': widget_data,
            'layout': {
                'type': 'grid',
                'columns': 12,
                'row_height': 60
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        self.portals[portal_id] = portal
        return portal
    
    async def create_fund_data_demo_portal(self) -> Dict[str, Any]:
        """Create Fund Data Demo Portal"""
        portal_id = f"fund_data_demo_{uuid.uuid4().hex[:8]}"
        
        # Define widgets for fund data portal
        widgets_config = [
            {
                'widget_id': 'fund_overview',
                'widget_type': WidgetType.FUND_DATA,
                'title': 'Fund Overview',
                'size': WidgetSize.LARGE,
                'position': {'x': 0, 'y': 0, 'width': 12, 'height': 4},
                'data_config': {
                    'fund_id': 'VFIAX',
                    'fund_type': 'mutual_fund'
                }
            },
            {
                'widget_id': 'fund_comparison',
                'widget_type': WidgetType.FUND_DATA,
                'title': 'Fund Comparison',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'fund_ids': ['VFIAX', 'VTSAX', 'VTIAX'],
                    'metrics': ['performance', 'risk', 'expenses']
                }
            },
            {
                'widget_id': 'fund_screening',
                'widget_type': WidgetType.FUND_DATA,
                'title': 'Fund Screener',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 6, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'criteria': {
                        'max_expense_ratio': 0.001,
                        'min_morningstar_rating': 4,
                        'category': ['Large Blend']
                    },
                    'limit': 20
                }
            }
        ]
        
        # Create widgets and fetch data
        widgets = []
        widget_data = {}
        
        for widget_config in widgets_config:
            config = WidgetConfig(
                widget_id=widget_config['widget_id'],
                widget_type=widget_config['widget_type'],
                title=widget_config['title'],
                size=widget_config['size'],
                position=widget_config['position'],
                data_config=widget_config['data_config']
            )
            
            widget = self.widget_manager.create_widget(config)
            widgets.append(widget)
            
            try:
                data = await widget.get_data()
                widget_data[widget.config.widget_id] = data
            except Exception as e:
                logger.error(f"Error fetching data for widget {widget.config.widget_id}: {e}")
                widget_data[widget.config.widget_id] = {
                    'data': {},
                    'status': 'error',
                    'error_message': str(e)
                }
        
        portal = {
            'portal_id': portal_id,
            'portal_name': 'Fund Data Demo Portal',
            'portal_type': 'fund_data',
            'description': 'Mutual fund and ETF data with performance, risk, and screening tools',
            'widgets': widgets_config,
            'widget_data': widget_data,
            'layout': {
                'type': 'grid',
                'columns': 12,
                'row_height': 60
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        self.portals[portal_id] = portal
        return portal
    
    async def create_comprehensive_demo_portal(self) -> Dict[str, Any]:
        """Create Comprehensive Demo Portal with all widget types"""
        portal_id = f"comprehensive_demo_{uuid.uuid4().hex[:8]}"
        
        # Define widgets for comprehensive portal
        widgets_config = [
            # Market Data Section
            {
                'widget_id': 'market_overview',
                'widget_type': WidgetType.MARKET_DATA,
                'title': 'Market Overview',
                'size': WidgetSize.LARGE,
                'position': {'x': 0, 'y': 0, 'width': 12, 'height': 4},
                'data_config': {
                    'indices': ['^GSPC', '^DJI', '^IXIC']
                }
            },
            {
                'widget_id': 'watchlist',
                'widget_type': WidgetType.MARKET_DATA,
                'title': 'Watchlist',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'symbols': ['AAPL', 'MSFT', 'GOOGL']
                }
            },
            {
                'widget_id': 'market_news',
                'widget_type': WidgetType.NEWS,
                'title': 'Latest News',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 6, 'y': 4, 'width': 6, 'height': 3},
                'data_config': {
                    'sources': ['reuters', 'marketwatch'],
                    'limit': 8
                }
            },
            # Portfolio Analytics Section
            {
                'widget_id': 'portfolio_performance',
                'widget_type': WidgetType.PORTFOLIO_ANALYTICS,
                'title': 'Portfolio Performance',
                'size': WidgetSize.LARGE,
                'position': {'x': 0, 'y': 7, 'width': 12, 'height': 4},
                'data_config': {
                    'portfolio_id': 'demo_portfolio',
                    'benchmark': 'SPY'
                }
            },
            {
                'widget_id': 'holdings_breakdown',
                'widget_type': WidgetType.PORTFOLIO_ANALYTICS,
                'title': 'Holdings',
                'size': WidgetSize.SMALL,
                'position': {'x': 0, 'y': 11, 'width': 4, 'height': 2},
                'data_config': {
                    'portfolio_id': 'demo_portfolio'
                }
            },
            {
                'widget_id': 'risk_analysis',
                'widget_type': WidgetType.PORTFOLIO_ANALYTICS,
                'title': 'Risk Analysis',
                'size': WidgetSize.SMALL,
                'position': {'x': 4, 'y': 11, 'width': 4, 'height': 2},
                'data_config': {
                    'portfolio_id': 'demo_portfolio'
                }
            },
            {
                'widget_id': 'company_overview',
                'widget_type': WidgetType.COMPANY_DATA,
                'title': 'Company Spotlight',
                'size': WidgetSize.SMALL,
                'position': {'x': 8, 'y': 11, 'width': 4, 'height': 2},
                'data_config': {
                    'symbol': 'AAPL'
                }
            },
            # Fund Data Section
            {
                'widget_id': 'fund_overview',
                'widget_type': WidgetType.FUND_DATA,
                'title': 'Featured Fund',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 0, 'y': 13, 'width': 6, 'height': 3},
                'data_config': {
                    'fund_id': 'VFIAX',
                    'fund_type': 'mutual_fund'
                }
            },
            {
                'widget_id': 'fund_screening',
                'widget_type': WidgetType.FUND_DATA,
                'title': 'Fund Ideas',
                'size': WidgetSize.MEDIUM,
                'position': {'x': 6, 'y': 13, 'width': 6, 'height': 3},
                'data_config': {
                    'criteria': {
                        'max_expense_ratio': 0.001,
                        'min_morningstar_rating': 4
                    },
                    'limit': 5
                }
            }
        ]
        
        # Create widgets and fetch data
        widgets = []
        widget_data = {}
        
        for widget_config in widgets_config:
            config = WidgetConfig(
                widget_id=widget_config['widget_id'],
                widget_type=widget_config['widget_type'],
                title=widget_config['title'],
                size=widget_config['size'],
                position=widget_config['position'],
                data_config=widget_config['data_config']
            )
            
            widget = self.widget_manager.create_widget(config)
            widgets.append(widget)
            
            try:
                data = await widget.get_data()
                widget_data[widget.config.widget_id] = data
            except Exception as e:
                logger.error(f"Error fetching data for widget {widget.config.widget_id}: {e}")
                widget_data[widget.config.widget_id] = {
                    'data': {},
                    'status': 'error',
                    'error_message': str(e)
                }
        
        portal = {
            'portal_id': portal_id,
            'portal_name': 'Comprehensive Demo Portal',
            'portal_type': 'comprehensive',
            'description': 'Complete financial dashboard showcasing all widget types and capabilities',
            'widgets': widgets_config,
            'widget_data': widget_data,
            'layout': {
                'type': 'grid',
                'columns': 12,
                'row_height': 60
            },
            'sections': [
                {
                    'name': 'Market Overview',
                    'widgets': ['market_overview', 'watchlist', 'market_news']
                },
                {
                    'name': 'Portfolio Analytics',
                    'widgets': ['portfolio_performance', 'holdings_breakdown', 'risk_analysis']
                },
                {
                    'name': 'Company & Fund Data',
                    'widgets': ['company_overview', 'fund_overview', 'fund_screening']
                }
            ],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        self.portals[portal_id] = portal
        return portal
    
    def get_portal_catalog(self) -> Dict[str, Any]:
        """Get catalog of available demo portals"""
        return {
            'portals': [
                {
                    'id': 'market_data_demo',
                    'name': 'Market Data Demo Portal',
                    'type': 'market_data',
                    'description': 'Real-time market data, screening, and technical analysis',
                    'widgets_count': 5,
                    'features': [
                        'Real-time market indices',
                        'Asset screening tools',
                        'Custom watchlists',
                        'Market depth analysis',
                        'Technical indicators'
                    ]
                },
                {
                    'id': 'portfolio_analytics_demo',
                    'name': 'Portfolio Analytics Demo Portal',
                    'type': 'portfolio_analytics',
                    'description': 'Industry-leading portfolio analysis tools',
                    'widgets_count': 5,
                    'features': [
                        'Performance analytics',
                        'Risk assessment',
                        'Holdings breakdown',
                        'Attribution analysis',
                        'Portfolio comparison'
                    ]
                },
                {
                    'id': 'news_demo',
                    'name': 'News Demo Portal',
                    'type': 'news',
                    'description': 'Real-time news and market updates',
                    'widgets_count': 3,
                    'features': [
                        'Market news aggregation',
                        'Company-specific news',
                        'Breaking news alerts',
                        'Sentiment analysis',
                        'Trending topics'
                    ]
                },
                {
                    'id': 'company_data_demo',
                    'name': 'Company Data Demo Portal',
                    'type': 'company_data',
                    'description': 'Comprehensive company fundamentals and analysis',
                    'widgets_count': 4,
                    'features': [
                        'Company overview',
                        'Financial statements',
                        'Analyst estimates',
                        'SEC filings',
                        'Key metrics'
                    ]
                },
                {
                    'id': 'fund_data_demo',
                    'name': 'Fund Data Demo Portal',
                    'type': 'fund_data',
                    'description': 'Mutual fund and ETF analysis tools',
                    'widgets_count': 3,
                    'features': [
                        'Fund overview',
                        'Performance comparison',
                        'Fund screening',
                        'Expense analysis',
                        'Risk metrics'
                    ]
                },
                {
                    'id': 'comprehensive_demo',
                    'name': 'Comprehensive Demo Portal',
                    'type': 'comprehensive',
                    'description': 'Complete financial dashboard with all features',
                    'widgets_count': 10,
                    'features': [
                        'All widget types',
                        'Integrated workflows',
                        'Cross-widget data sharing',
                        'Advanced visualizations',
                        'Real-time updates'
                    ]
                }
            ],
            'total_portals': 6,
            'total_widget_types': 5,
            'last_updated': datetime.now().isoformat()
        }
    
    async def get_portal(self, portal_id: str) -> Optional[Dict[str, Any]]:
        """Get specific portal by ID"""
        if portal_id not in self.portals:
            return None
        
        portal = self.portals[portal_id]
        
        # Refresh widget data
        for widget_id in portal['widget_data']:
            try:
                widget = self.widget_manager.widgets.get(widget_id)
                if widget:
                    data = await widget.get_data(force_refresh=True)
                    portal['widget_data'][widget_id] = data
            except Exception as e:
                logger.error(f"Error refreshing widget {widget_id}: {e}")
        
        portal['last_updated'] = datetime.now().isoformat()
        return portal
    
    async def refresh_portal(self, portal_id: str) -> Optional[Dict[str, Any]]:
        """Refresh all widgets in a portal"""
        return await self.get_portal(portal_id)

# Factory function
def get_demo_portal_manager(data_manager=None) -> DemoPortalManager:
    """Factory function to get demo portal manager"""
    return DemoPortalManager(data_manager)
