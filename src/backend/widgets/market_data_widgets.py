"""
Market Data Widgets - Inspired by FactSet Market Data Demo Portal
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

class MarketOverviewWidget(BaseWidget):
    """Market overview widget showing major indices and market sentiment"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            data_manager = get_free_data_sources_manager()
            
            # Get major indices
            indices = ['^GSPC', '^DJI', '^IXIC', '^RUT']  # S&P 500, Dow, NASDAQ, Russell 2000
            index_data = await data_manager.get_real_time_quotes(indices)
            
            # Get market overview data
            market_data = {
                'indices': [],
                'market_sentiment': self._calculate_market_sentiment(index_data),
                'sector_performance': await self._get_sector_performance(),
                'market_movers': await self._get_market_movers(),
                'economic_indicators': await self._get_economic_indicators()
            }
            
            for quote in index_data:
                market_data['indices'].append({
                    'symbol': quote.symbol,
                    'name': self._get_index_name(quote.symbol),
                    'price': quote.price,
                    'change': quote.additional_data.get('change', 0),
                    'change_percent': quote.additional_data.get('change_percent', 0),
                    'volume': quote.volume
                })
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=market_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching market overview data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="market-overview-widget" id="{self.config.widget_id}">
            <h3>Market Overview</h3>
            <div class="indices-grid">
                <!-- Indices will be rendered here -->
            </div>
            <div class="market-sentiment">
                <h4>Market Sentiment</h4>
                <div class="sentiment-indicator"></div>
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'market_overview',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    def _get_index_name(self, symbol: str) -> str:
        names = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            '^RUT': 'Russell 2000'
        }
        return names.get(symbol, symbol)
    
    def _calculate_market_sentiment(self, index_data) -> str:
        if not index_data:
            return "neutral"
        
        positive_count = sum(1 for quote in index_data 
                           if quote.additional_data.get('change_percent', 0) > 0)
        total_count = len(index_data)
        
        if positive_count / total_count > 0.6:
            return "bullish"
        elif positive_count / total_count < 0.4:
            return "bearish"
        else:
            return "neutral"
    
    async def _get_sector_performance(self) -> Dict[str, float]:
        # Mock sector performance
        sectors = ['Technology', 'Healthcare', 'Financial', 'Energy', 'Consumer']
        return {sector: np.random.uniform(-0.03, 0.05) for sector in sectors}
    
    async def _get_market_movers(self) -> Dict[str, List[Dict[str, Any]]]:
        # Mock market movers
        gainers = [
            {'symbol': 'AAPL', 'price': 150.25, 'change_percent': 3.2},
            {'symbol': 'MSFT', 'price': 280.50, 'change_percent': 2.8}
        ]
        losers = [
            {'symbol': 'TSLA', 'price': 180.75, 'change_percent': -2.1},
            {'symbol': 'NVDA', 'price': 420.30, 'change_percent': -1.8}
        ]
        
        return {'gainers': gainers, 'losers': losers}
    
    async def _get_economic_indicators(self) -> Dict[str, Any]:
        # Mock economic indicators
        return {
            'interest_rate': 0.045,
            'inflation_rate': 0.032,
            'gdp_growth': 0.025,
            'unemployment_rate': 0.038
        }

class AssetScreenerWidget(BaseWidget):
    """Asset screener widget for filtering and searching securities"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            data_manager = get_free_data_sources_manager()
            
            # Get screener criteria from config
            criteria = self.config.data_config.get('criteria', {})
            sectors = criteria.get('sectors', [])
            market_cap_range = criteria.get('market_cap_range', (0, float('inf')))
            pe_ratio_range = criteria.get('pe_ratio_range', (0, float('inf')))
            
            # Get screening results (mock implementation)
            screening_results = await self._perform_screening(
                sectors, market_cap_range, pe_ratio_range
            )
            
            screener_data = {
                'criteria': criteria,
                'results': screening_results,
                'total_results': len(screening_results),
                'screening_time': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=screener_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching screener data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="asset-screener-widget" id="{self.config.widget_id}">
            <h3>Asset Screener</h3>
            <div class="screener-filters">
                <!-- Filter controls will be rendered here -->
            </div>
            <div class="screener-results">
                <!-- Results will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'asset_screener',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _perform_screening(self, sectors: List[str], market_cap_range: tuple, pe_ratio_range: tuple) -> List[Dict[str, Any]]:
        # Mock screening results
        results = []
        
        # Generate mock securities that meet criteria
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'WMT']
        
        for symbol in symbols:
            # Mock data
            market_cap = np.random.uniform(1e10, 2e12)
            pe_ratio = np.random.uniform(10, 35)
            sector = np.random.choice(['Technology', 'Healthcare', 'Financial', 'Consumer', 'Energy'])
            
            # Check if meets criteria
            if (not sectors or sector in sectors) and \
               market_cap_range[0] <= market_cap <= market_cap_range[1] and \
               pe_ratio_range[0] <= pe_ratio <= pe_ratio_range[1]:
                
                results.append({
                    'symbol': symbol,
                    'name': f'{symbol} Corporation',
                    'sector': sector,
                    'market_cap': market_cap,
                    'pe_ratio': pe_ratio,
                    'price': np.random.uniform(50, 500),
                    'change_percent': np.random.uniform(-0.05, 0.05)
                })
        
        return results[:20]  # Limit to 20 results

class WatchlistWidget(BaseWidget):
    """Watchlist widget for tracking selected securities"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            data_manager = get_free_data_sources_manager()
            
            # Get watchlist symbols from config
            symbols = self.config.data_config.get('symbols', ['AAPL', 'MSFT', 'GOOGL'])
            
            # Get real-time quotes
            quotes = await data_manager.get_real_time_quotes(symbols)
            
            watchlist_data = {
                'symbols': [],
                'summary': self._calculate_watchlist_summary(quotes),
                'last_updated': datetime.now().isoformat()
            }
            
            for quote in quotes:
                watchlist_data['symbols'].append({
                    'symbol': quote.symbol,
                    'price': quote.price,
                    'change': quote.additional_data.get('change', 0),
                    'change_percent': quote.additional_data.get('change_percent', 0),
                    'volume': quote.volume,
                    'high': quote.additional_data.get('high', quote.price),
                    'low': quote.additional_data.get('low', quote.price)
                })
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=watchlist_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching watchlist data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="watchlist-widget" id="{self.config.widget_id}">
            <h3>Watchlist</h3>
            <div class="watchlist-summary">
                <!-- Summary will be rendered here -->
            </div>
            <div class="watchlist-table">
                <!-- Watchlist table will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'watchlist',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    def _calculate_watchlist_summary(self, quotes) -> Dict[str, Any]:
        if not quotes:
            return {}
        
        total_value = sum(quote.price for quote in quotes)
        positive_changes = sum(1 for quote in quotes 
                            if quote.additional_data.get('change_percent', 0) > 0)
        
        return {
            'total_symbols': len(quotes),
            'positive_changes': positive_changes,
            'negative_changes': len(quotes) - positive_changes,
            'average_change': np.mean([quote.additional_data.get('change_percent', 0) for quote in quotes]),
            'total_volume': sum(quote.volume for quote in quotes)
        }

class MarketDepthWidget(BaseWidget):
    """Market depth widget showing order book data"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            symbol = self.config.data_config.get('symbol', 'AAPL')
            
            # Mock market depth data
            depth_data = self._generate_market_depth(symbol)
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=depth_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching market depth data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="market-depth-widget" id="{self.config.widget_id}">
            <h3>Market Depth</h3>
            <div class="depth-chart">
                <!-- Depth chart will be rendered here -->
            </div>
            <div class="order-book">
                <!-- Order book will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'market_depth',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    def _generate_market_depth(self, symbol: str) -> Dict[str, Any]:
        # Generate mock order book data
        base_price = np.random.uniform(100, 200)
        
        bids = []
        asks = []
        
        # Generate bids (buy orders)
        for i in range(10):
            price = base_price - (i * 0.01)
            volume = np.random.randint(100, 10000)
            bids.append({'price': price, 'volume': volume, 'total': volume})
        
        # Generate asks (sell orders)
        for i in range(10):
            price = base_price + ((i + 1) * 0.01)
            volume = np.random.randint(100, 10000)
            asks.append({'price': price, 'volume': volume, 'total': volume})
        
        # Calculate cumulative totals
        for i in range(1, len(bids)):
            bids[i]['total'] += bids[i-1]['total']
        
        for i in range(1, len(asks)):
            asks[i]['total'] += asks[i-1]['total']
        
        return {
            'symbol': symbol,
            'current_price': base_price,
            'bids': bids,
            'asks': asks,
            'spread': asks[0]['price'] - bids[0]['price']
        }

class TechnicalAnalysisWidget(BaseWidget):
    """Technical analysis widget with indicators and charts"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            data_manager = get_free_data_sources_manager()
            
            symbol = self.config.data_config.get('symbol', 'AAPL')
            indicators = self.config.data_config.get('indicators', ['sma', 'rsi', 'macd'])
            
            # Get historical data for technical analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=60)
            
            historical_data = await data_manager.get_historical_data(symbol, start_date, end_date)
            
            # Calculate technical indicators
            technical_data = {
                'symbol': symbol,
                'price_data': historical_data[-20:],  # Last 20 days
                'indicators': self._calculate_indicators(historical_data, indicators),
                'signals': self._generate_trading_signals(historical_data, indicators),
                'analysis_time': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=technical_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching technical analysis data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="technical-analysis-widget" id="{self.config.widget_id}">
            <h3>Technical Analysis</h3>
            <div class="price-chart">
                <!-- Price chart with indicators will be rendered here -->
            </div>
            <div class="indicators-panel">
                <!-- Technical indicators will be rendered here -->
            </div>
            <div class="trading-signals">
                <!-- Trading signals will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'technical_analysis',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    def _calculate_indicators(self, historical_data: List[Dict[str, Any]], indicators: List[str]) -> Dict[str, Any]:
        if not historical_data:
            return {}
        
        prices = [data['close'] for data in historical_data]
        volumes = [data['volume'] for data in historical_data]
        
        indicator_data = {}
        
        if 'sma' in indicators:
            sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
            sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)
            indicator_data['sma'] = {'sma_20': sma_20, 'sma_50': sma_50}
        
        if 'rsi' in indicators:
            rsi = self._calculate_rsi(prices)
            indicator_data['rsi'] = {'current': rsi[-1] if rsi else 50, 'values': rsi}
        
        if 'macd' in indicators:
            macd_data = self._calculate_macd(prices)
            indicator_data['macd'] = macd_data
        
        if 'bollinger' in indicators:
            bb_data = self._calculate_bollinger_bands(prices)
            indicator_data['bollinger'] = bb_data
        
        return indicator_data
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        if len(prices) < period + 1:
            return [50] * len(prices)
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [max(delta, 0) for delta in deltas]
        losses = [abs(min(delta, 0)) for delta in deltas]
        
        rsi_values = []
        for i in range(period, len(gains)):
            avg_gain = np.mean(gains[i-period:i])
            avg_loss = np.mean(losses[i-period:i])
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values
    
    def _calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        if len(prices) < slow:
            return {'macd': [], 'signal': [], 'histogram': []}
        
        # Calculate EMAs
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        
        # Calculate MACD line
        macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(ema_slow))]
        
        # Calculate signal line
        signal_line = self._calculate_ema(macd_line, signal)
        
        # Calculate histogram
        histogram = [macd_line[i] - signal_line[i] for i in range(len(signal_line))]
        
        return {
            'macd': macd_line[-10:] if len(macd_line) >= 10 else macd_line,
            'signal': signal_line[-10:] if len(signal_line) >= 10 else signal_line,
            'histogram': histogram[-10:] if len(histogram) >= 10 else histogram
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        if len(prices) < period:
            return [np.mean(prices)] * len(prices)
        
        multiplier = 2 / (period + 1)
        ema = [prices[0]]
        
        for price in prices[1:]:
            ema.append((price * multiplier) + (ema[-1] * (1 - multiplier)))
        
        return ema
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, Any]:
        if len(prices) < period:
            return {'upper': [], 'middle': [], 'lower': []}
        
        upper = []
        middle = []
        lower = []
        
        for i in range(period, len(prices)):
            window = prices[i-period:i]
            sma = np.mean(window)
            std = np.std(window)
            
            upper.append(sma + (std * std_dev))
            middle.append(sma)
            lower.append(sma - (std * std_dev))
        
        return {
            'upper': upper[-10:] if len(upper) >= 10 else upper,
            'middle': middle[-10:] if len(middle) >= 10 else middle,
            'lower': lower[-10:] if len(lower) >= 10 else lower
        }
    
    def _generate_trading_signals(self, historical_data: List[Dict[str, Any]], indicators: List[str]) -> List[Dict[str, Any]]:
        signals = []
        
        if not historical_data:
            return signals
        
        current_price = historical_data[-1]['close']
        
        # Generate mock signals based on indicators
        if 'sma' in indicators:
            signals.append({
                'type': 'SMA Crossover',
                'action': 'BUY' if np.random.random() > 0.5 else 'SELL',
                'confidence': np.random.uniform(0.6, 0.9),
                'reason': 'Price crossed SMA'
            })
        
        if 'rsi' in indicators:
            rsi = np.random.uniform(20, 80)
            if rsi < 30:
                signals.append({
                    'type': 'RSI Oversold',
                    'action': 'BUY',
                    'confidence': 0.8,
                    'reason': f'RSI at {rsi:.1f} (oversold)'
                })
            elif rsi > 70:
                signals.append({
                    'type': 'RSI Overbought',
                    'action': 'SELL',
                    'confidence': 0.8,
                    'reason': f'RSI at {rsi:.1f} (overbought)'
                })
        
        return signals

# Register widget templates
def register_market_data_widgets(widget_manager):
    """Register all market data widget templates"""
    
    widget_manager.register_template(WidgetType.MARKET_DATA, MarketOverviewWidget)
    widget_manager.register_template(WidgetType.MARKET_DATA, AssetScreenerWidget)
    widget_manager.register_template(WidgetType.MARKET_DATA, WatchlistWidget)
    widget_manager.register_template(WidgetType.MARKET_DATA, MarketDepthWidget)
    widget_manager.register_template(WidgetType.MARKET_DATA, TechnicalAnalysisWidget)
