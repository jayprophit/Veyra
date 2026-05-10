"""
Financial Master Widget Framework
Inspired by FactSet Widgets - Free open-source alternative
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class WidgetType(Enum):
    MARKET_DATA = "market_data"
    PORTFOLIO_ANALYTICS = "portfolio_analytics"
    NEWS = "news"
    COMPANY_DATA = "company_data"
    FUND_DATA = "fund_data"
    ETF_DATA = "etf_data"
    CHART = "chart"
    TABLE = "table"
    ALERT = "alert"

class WidgetSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    FULL = "full"

@dataclass
class WidgetConfig:
    widget_id: str
    widget_type: WidgetType
    title: str
    size: WidgetSize
    position: Dict[str, int] = field(default_factory=dict)
    data_config: Dict[str, Any] = field(default_factory=dict)
    style_config: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 300  # seconds
    auto_refresh: bool = True

@dataclass
class WidgetData:
    widget_id: str
    data: Dict[str, Any]
    timestamp: datetime
    last_updated: datetime
    status: str = "success"
    error_message: Optional[str] = None

class BaseWidget(ABC):
    """Base class for all financial widgets"""
    
    def __init__(self, config: WidgetConfig, data_manager=None):
        self.config = config
        self.data_manager = data_manager
        self.cache = {}
        self.cache_ttl = config.refresh_interval
        self.last_refresh = None
        
    @abstractmethod
    async def fetch_data(self) -> WidgetData:
        """Fetch widget data from data sources"""
        pass
    
    @abstractmethod
    def render_html(self) -> str:
        """Render widget as HTML"""
        pass
    
    @abstractmethod
    def render_json(self) -> Dict[str, Any]:
        """Render widget data as JSON"""
        pass
    
    async def get_data(self, force_refresh: bool = False) -> WidgetData:
        """Get widget data with caching"""
        now = datetime.now()
        
        # Check cache
        if not force_refresh and self.last_refresh and (now - self.last_refresh).seconds < self.cache_ttl:
            if self.config.widget_id in self.cache:
                return self.cache[self.config.widget_id]
        
        # Fetch fresh data
        try:
            data = await self.fetch_data()
            self.cache[self.config.widget_id] = data
            self.last_refresh = now
            return data
        except Exception as e:
            logger.error(f"Error fetching data for widget {self.config.widget_id}: {e}")
            return WidgetData(
                widget_id=self.config.widget_id,
                data={},
                timestamp=now,
                last_updated=now,
                status="error",
                error_message=str(e)
            )

class WidgetManager:
    """Manages all widgets in the system"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self.widgets = {}
        self.widget_templates = {}
        self.widget_catalog = []
        
    def register_widget(self, widget: BaseWidget):
        """Register a widget instance"""
        self.widgets[widget.config.widget_id] = widget
        
    def register_template(self, widget_type: WidgetType, template_class):
        """Register a widget template class"""
        self.widget_templates[widget_type] = template_class
        
    def create_widget(self, config: WidgetConfig) -> BaseWidget:
        """Create a widget instance from config"""
        template_class = self.widget_templates.get(config.widget_type)
        if not template_class:
            raise ValueError(f"Unknown widget type: {config.widget_type}")
        
        widget = template_class(config, self.data_manager)
        self.register_widget(widget)
        return widget
        
    async def get_widget_data(self, widget_id: str, force_refresh: bool = False) -> WidgetData:
        """Get data for a specific widget"""
        widget = self.widgets.get(widget_id)
        if not widget:
            raise ValueError(f"Widget not found: {widget_id}")
        
        return await widget.get_data(force_refresh)
        
    async def refresh_all_widgets(self) -> Dict[str, WidgetData]:
        """Refresh all widgets"""
        results = {}
        
        for widget_id, widget in self.widgets.items():
            try:
                data = await widget.get_data(force_refresh=True)
                results[widget_id] = data
            except Exception as e:
                logger.error(f"Error refreshing widget {widget_id}: {e}")
                results[widget_id] = WidgetData(
                    widget_id=widget_id,
                    data={},
                    timestamp=datetime.now(),
                    last_updated=datetime.now(),
                    status="error",
                    error_message=str(e)
                )
        
        return results
        
    def get_widget_catalog(self) -> List[Dict[str, Any]]:
        """Get catalog of available widget types"""
        catalog = []
        
        for widget_type in WidgetType:
            catalog.append({
                "type": widget_type.value,
                "name": widget_type.value.replace("_", " ").title(),
                "description": self._get_widget_description(widget_type),
                "example_config": self._get_example_config(widget_type),
                "data_sources": self._get_data_sources(widget_type)
            })
        
        return catalog
        
    def _get_widget_description(self, widget_type: WidgetType) -> str:
        """Get description for widget type"""
        descriptions = {
            WidgetType.MARKET_DATA: "Real-time market data including prices, volumes, and indices",
            WidgetType.PORTFOLIO_ANALYTICS: "Portfolio performance, attribution, and risk analytics",
            WidgetType.NEWS: "Real-time financial news and market updates",
            WidgetType.COMPANY_DATA: "Company fundamentals, financials, and analyst estimates",
            WidgetType.FUND_DATA: "Mutual fund data including performance and holdings",
            WidgetType.ETF_DATA: "ETF data including holdings, expenses, and performance",
            WidgetType.CHART: "Interactive charts for financial data visualization",
            WidgetType.TABLE: "Data tables with sorting, filtering, and export capabilities",
            WidgetType.ALERT: "Price alerts and market notifications"
        }
        return descriptions.get(widget_type, "Financial data widget")
        
    def _get_example_config(self, widget_type: WidgetType) -> Dict[str, Any]:
        """Get example configuration for widget type"""
        configs = {
            WidgetType.MARKET_DATA: {
                "symbols": ["AAPL", "MSFT", "GOOGL"],
                "data_points": ["price", "change", "volume"],
                "show_chart": True
            },
            WidgetType.PORTFOLIO_ANALYTICS: {
                "portfolio_id": "portfolio_123",
                "benchmark": "SPY",
                "show_attribution": True
            },
            WidgetType.NEWS: {
                "symbols": ["AAPL", "MSFT"],
                "sources": ["reuters", "bloomberg"],
                "limit": 10
            },
            WidgetType.COMPANY_DATA: {
                "symbol": "AAPL",
                "sections": ["overview", "financials", "estimates"]
            },
            WidgetType.FUND_DATA: {
                "fund_id": "VFIAX",
                "sections": ["performance", "holdings", "expenses"]
            },
            WidgetType.ETF_DATA: {
                "etf_id": "SPY",
                "sections": ["holdings", "performance", "expenses"]
            },
            WidgetType.CHART: {
                "type": "line",
                "data_source": "market_data",
                "symbols": ["AAPL"],
                "period": "1M"
            },
            WidgetType.TABLE: {
                "data_source": "portfolio_holdings",
                "columns": ["symbol", "weight", "value", "change"],
                "sortable": True
            },
            WidgetType.ALERT: {
                "symbols": ["AAPL"],
                "conditions": ["price_above_150", "volume_spike"],
                "notification_method": "email"
            }
        }
        return configs.get(widget_type, {})
        
    def _get_data_sources(self, widget_type: WidgetType) -> List[str]:
        """Get data sources for widget type"""
        sources = {
            WidgetType.MARKET_DATA: ["OpenBB", "Yahoo Finance", "Alpha Vantage"],
            WidgetType.PORTFOLIO_ANALYTICS: ["Portfolio Database", "OpenBB", "Finance Toolkit"],
            WidgetType.NEWS: ["News API", "OpenBB", "RSS Feeds"],
            WidgetType.COMPANY_DATA: ["EDGAR", "OpenBB", "Finance Toolkit"],
            WidgetType.FUND_DATA: ["Morningstar API", "Fund Database", "OpenBB"],
            WidgetType.ETF_DATA: ["ETF Database", "Yahoo Finance", "OpenBB"],
            WidgetType.CHART: ["Market Data APIs", "Portfolio Data"],
            WidgetType.TABLE: ["Portfolio Database", "Market Data"],
            WidgetType.ALERT: ["Market Data APIs", "Notification Service"]
        }
        return sources.get(widget_type, ["Free Data Sources"])

# Factory function
def get_widget_manager(data_manager=None) -> WidgetManager:
    """Factory function to get widget manager"""
    return WidgetManager(data_manager)
