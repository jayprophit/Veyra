"""
Financial Master Widgets Framework
FactSet-inspired widgets using free data sources
"""

from .widget_framework import (
    WidgetManager,
    BaseWidget,
    WidgetConfig,
    WidgetData,
    WidgetType,
    WidgetSize,
    get_widget_manager
)

from .market_data_widgets import register_market_data_widgets
from .portfolio_analytics_widgets import register_portfolio_analytics_widgets
from .news_widgets import register_news_widgets
from .company_data_widgets import register_company_data_widgets
from .fund_data_widgets import register_fund_data_widgets

__all__ = [
    'WidgetManager',
    'BaseWidget',
    'WidgetConfig',
    'WidgetData',
    'WidgetType',
    'WidgetSize',
    'get_widget_manager',
    'register_market_data_widgets',
    'register_portfolio_analytics_widgets',
    'register_news_widgets',
    'register_company_data_widgets',
    'register_fund_data_widgets'
]
