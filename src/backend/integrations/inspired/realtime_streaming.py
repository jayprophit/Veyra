"""
Real-time Streaming Data Module - Inspired by FactSet Recipes
Free open-source alternative using free data sources and streaming technologies
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import json
import websockets
import numpy as np
from collections import defaultdict, deque

from ..free.free_data_sources import get_free_data_sources_manager

logger = logging.getLogger(__name__)

@dataclass
class StreamingData:
    symbol: str
    data_type: str
    timestamp: datetime
    value: float
    metadata: Dict[str, Any]

@dataclass
class StreamSubscription:
    subscription_id: str
    symbols: List[str]
    data_types: List[str]
    callback: Callable
    active: bool
    created_at: datetime

@dataclass
class DerivedAnalytics:
    symbol: str
    indicator_name: str
    value: float
    calculation_time: datetime
    input_data: Dict[str, Any]

class RealtimeStreamingModule:
    """Real-time streaming data module inspired by FactSet recipes"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.data_manager = get_free_data_sources_manager(config.get('data_sources', {}))
        self.subscriptions = {}
        self.data_streams = defaultdict(deque)
        self.derived_analytics = defaultdict(deque)
        self.websocket_clients = set()
        self.cache = {}
        self.cache_ttl = 60  # 1 minute cache
        
        # Streaming configuration
        self.stream_interval = config.get('stream_interval', 1)  # seconds
        self.max_queue_size = config.get('max_queue_size', 1000)
        self.enable_derived_analytics = config.get('enable_derived_analytics', True)
        
        logger.info("Real-time Streaming Module initialized")
    
    async def start_streaming_service(self, port: int = 8765):
        """
        Inspired by: "Stream Pricing Data from Global Exchanges to Web Applications at Scale"
        Start the streaming service for real-time data
        """
        try:
            # Start WebSocket server
            server = await websockets.serve(
                self._handle_websocket_connection,
                "localhost",
                port
            )
            
            logger.info(f"Streaming service started on port {port}")
            
            # Start data streaming tasks
            streaming_tasks = [
                asyncio.create_task(self._stream_market_data()),
                asyncio.create_task(self._stream_derived_analytics()),
                asyncio.create_task(self._cleanup_old_data())
            ]
            
            return server, streaming_tasks
            
        except Exception as e:
            logger.error(f"Error starting streaming service: {e}")
            raise
    
    async def create_stream_subscription(self, symbols: List[str], data_types: List[str], 
                                       callback: Callable = None) -> str:
        """
        Create a subscription for real-time data streaming
        """
        try:
            subscription_id = f"SUB_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.subscriptions)}"
            
            subscription = StreamSubscription(
                subscription_id=subscription_id,
                symbols=symbols,
                data_types=data_types,
                callback=callback,
                active=True,
                created_at=datetime.now()
            )
            
            self.subscriptions[subscription_id] = subscription
            
            logger.info(f"Created subscription {subscription_id} for {len(symbols)} symbols")
            
            return subscription_id
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise
    
    async def cancel_subscription(self, subscription_id: str):
        """Cancel a streaming subscription"""
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].active = False
            del self.subscriptions[subscription_id]
            logger.info(f"Cancelled subscription {subscription_id}")
    
    async def compute_custom_derived_analytics(self, symbol: str, analytics_config: Dict[str, Any]) -> DerivedAnalytics:
        """
        Inspired by: "Compute Custom Derived Pricing Analytics on Streaming Data"
        Compute custom derived analytics on streaming data
        """
        try:
            indicator_name = analytics_config.get('indicator_name', 'custom_indicator')
            calculation_method = analytics_config.get('method', 'simple_moving_average')
            parameters = analytics_config.get('parameters', {})
            
            # Get recent data for calculation
            recent_data = list(self.data_streams[symbol])[-parameters.get('lookback_period', 20):]
            
            if not recent_data:
                raise ValueError(f"No recent data available for {symbol}")
            
            # Calculate derived analytics based on method
            if calculation_method == 'simple_moving_average':
                value = self._calculate_sma(recent_data, parameters.get('period', 10))
            elif calculation_method == 'exponential_moving_average':
                value = self._calculate_ema(recent_data, parameters.get('period', 10))
            elif calculation_method == 'relative_strength_index':
                value = self._calculate_rsi(recent_data, parameters.get('period', 14))
            elif calculation_method == 'bollinger_bands':
                value = self._calculate_bollinger_position(recent_data, parameters.get('period', 20))
            elif calculation_method == 'custom_formula':
                value = self._calculate_custom_formula(recent_data, parameters.get('formula', 'price * 1.01'))
            else:
                value = np.mean([data.value for data in recent_data])
            
            derived_analytics = DerivedAnalytics(
                symbol=symbol,
                indicator_name=indicator_name,
                value=value,
                calculation_time=datetime.now(),
                input_data={'recent_data_count': len(recent_data), 'parameters': parameters}
            )
            
            # Store derived analytics
            self.derived_analytics[symbol].append(derived_analytics)
            
            # Limit queue size
            if len(self.derived_analytics[symbol]) > self.max_queue_size:
                self.derived_analytics[symbol].popleft()
            
            # Broadcast to subscribers
            await self._broadcast_derived_analytics(derived_analytics)
            
            return derived_analytics
            
        except Exception as e:
            logger.error(f"Error computing derived analytics for {symbol}: {e}")
            raise
    
    async def create_high_velocity_streaming_app(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspired by: "Best Practices to Build Performant Streaming Web Applications using a FactSet JavaScript SDK"
        Create high-velocity streaming application
        """
        try:
            app_id = app_config.get('app_id', f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            symbols = app_config.get('symbols', ['AAPL', 'MSFT', 'GOOGL'])
            data_types = app_config.get('data_types', ['price', 'volume'])
            max_subscribers = app_config.get('max_subscribers', 100)
            
            streaming_app = {
                'app_id': app_id,
                'created_at': datetime.now().isoformat(),
                'configuration': {
                    'symbols': symbols,
                    'data_types': data_types,
                    'max_subscribers': max_subscribers,
                    'stream_interval': self.stream_interval,
                    'compression': app_config.get('compression', 'gzip'),
                    'buffer_size': app_config.get('buffer_size', 1024)
                },
                'performance_metrics': {
                    'messages_per_second': 0,
                    'latency_ms': 0,
                    'active_subscribers': 0,
                    'data_rate_mb_per_second': 0
                },
                'endpoints': {
                    'websocket': f"ws://localhost:8765/stream/{app_id}",
                    'rest_api': f"http://localhost:8000/api/streaming/{app_id}",
                    'status': f"http://localhost:8000/api/streaming/{app_id}/status"
                }
            }
            
            # Create subscription for this app
            await self.create_stream_subscription(
                symbols=symbols,
                data_types=data_types,
                callback=lambda data: self._handle_app_streaming_data(app_id, data)
            )
            
            return streaming_app
            
        except Exception as e:
            logger.error(f"Error creating high-velocity streaming app: {e}")
            raise
    
    async def deliver_intelligence_to_channels(self, intelligence_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspired by: "Deliver Intelligence to All Channels with a Simple Streaming Architecture"
        Deliver intelligence to multiple communication channels
        """
        try:
            delivery_id = f"INTELLIGENCE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            channels = intelligence_config.get('channels', ['websocket', 'webhook', 'email'])
            intelligence_data = intelligence_config.get('data', {})
            
            delivery_results = {
                'delivery_id': delivery_id,
                'initiated_at': datetime.now().isoformat(),
                'channels': {},
                'success_count': 0,
                'failure_count': 0
            }
            
            # Deliver to each channel
            for channel in channels:
                try:
                    if channel == 'websocket':
                        result = await self._deliver_to_websocket_channel(intelligence_data)
                    elif channel == 'webhook':
                        result = await self._deliver_to_webhook_channel(intelligence_data)
                    elif channel == 'email':
                        result = await self._deliver_to_email_channel(intelligence_data)
                    elif channel == 'slack':
                        result = await self._deliver_to_slack_channel(intelligence_data)
                    else:
                        result = {'success': False, 'error': f'Unknown channel: {channel}'}
                    
                    delivery_results['channels'][channel] = result
                    if result.get('success', False):
                        delivery_results['success_count'] += 1
                    else:
                        delivery_results['failure_count'] += 1
                        
                except Exception as e:
                    logger.error(f"Error delivering to {channel}: {e}")
                    delivery_results['channels'][channel] = {'success': False, 'error': str(e)}
                    delivery_results['failure_count'] += 1
            
            delivery_results['completed_at'] = datetime.now().isoformat()
            delivery_results['success_rate'] = delivery_results['success_count'] / len(channels)
            
            return delivery_results
            
        except Exception as e:
            logger.error(f"Error delivering intelligence to channels: {e}")
            raise
    
    async def get_streaming_status(self) -> Dict[str, Any]:
        """Get current streaming status"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'active_subscriptions': len([s for s in self.subscriptions.values() if s.active]),
                'websocket_clients': len(self.websocket_clients),
                'data_streams': {
                    symbol: len(stream) for symbol, stream in self.data_streams.items()
                },
                'derived_analytics': {
                    symbol: len(analytics) for symbol, analytics in self.derived_analytics.items()
                },
                'performance_metrics': {
                    'total_data_points': sum(len(stream) for stream in self.data_streams.values()),
                    'total_analytics': sum(len(analytics) for analytics in self.derived_analytics.values()),
                    'memory_usage_mb': self._estimate_memory_usage()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting streaming status: {e}")
            raise
    
    # Private methods
    async def _handle_websocket_connection(self, websocket, path):
        """Handle WebSocket connections"""
        try:
            self.websocket_clients.add(websocket)
            logger.info(f"WebSocket client connected: {websocket.remote_address}")
            
            # Send initial status
            await websocket.send(json.dumps({
                'type': 'status',
                'data': await self.get_streaming_status()
            }))
            
            # Keep connection alive and handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_websocket_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket client disconnected: {websocket.remote_address}")
        finally:
            self.websocket_clients.discard(websocket)
    
    async def _handle_websocket_message(self, websocket, data: Dict[str, Any]):
        """Handle WebSocket messages"""
        message_type = data.get('type')
        
        if message_type == 'subscribe':
            symbols = data.get('symbols', [])
            data_types = data.get('data_types', ['price'])
            
            subscription_id = await self.create_stream_subscription(
                symbols=symbols,
                data_types=data_types,
                callback=lambda stream_data: self._send_to_websocket(websocket, stream_data)
            )
            
            await websocket.send(json.dumps({
                'type': 'subscription_created',
                'subscription_id': subscription_id
            }))
            
        elif message_type == 'unsubscribe':
            subscription_id = data.get('subscription_id')
            await self.cancel_subscription(subscription_id)
            
        elif message_type == 'get_status':
            status = await self.get_streaming_status()
            await websocket.send(json.dumps({
                'type': 'status',
                'data': status
            }))
    
    async def _send_to_websocket(self, websocket, data: StreamingData):
        """Send data to specific WebSocket client"""
        try:
            message = {
                'type': 'stream_data',
                'data': {
                    'symbol': data.symbol,
                    'data_type': data.data_type,
                    'timestamp': data.timestamp.isoformat(),
                    'value': data.value,
                    'metadata': data.metadata
                }
            }
            
            await websocket.send(json.dumps(message))
            
        except websockets.exceptions.ConnectionClosed:
            self.websocket_clients.discard(websocket)
        except Exception as e:
            logger.error(f"Error sending to WebSocket: {e}")
    
    async def _stream_market_data(self):
        """Stream market data to subscribers"""
        while True:
            try:
                # Get active subscriptions
                active_subscriptions = [s for s in self.subscriptions.values() if s.active]
                
                if not active_subscriptions:
                    await asyncio.sleep(self.stream_interval)
                    continue
                
                # Collect all unique symbols from active subscriptions
                all_symbols = set()
                for sub in active_subscriptions:
                    all_symbols.update(sub.symbols)
                
                # Get market data for all symbols
                if all_symbols:
                    market_data = await self.data_manager.get_real_time_quotes(list(all_symbols))
                    
                    # Process each symbol's data
                    for quote in market_data:
                        # Store in data stream
                        streaming_data = StreamingData(
                            symbol=quote.symbol,
                            data_type='price',
                            timestamp=quote.timestamp,
                            value=quote.price,
                            metadata={
                                'volume': quote.volume,
                                'high': quote.additional_data.get('high'),
                                'low': quote.additional_data.get('low'),
                                'change': quote.additional_data.get('change'),
                                'change_percent': quote.additional_data.get('change_percent')
                            }
                        )
                        
                        self.data_streams[quote.symbol].append(streaming_data)
                        
                        # Limit queue size
                        if len(self.data_streams[quote.symbol]) > self.max_queue_size:
                            self.data_streams[quote.symbol].popleft()
                        
                        # Send to subscribers
                        await self._broadcast_to_subscribers(streaming_data)
                
                await asyncio.sleep(self.stream_interval)
                
            except Exception as e:
                logger.error(f"Error in market data streaming: {e}")
                await asyncio.sleep(self.stream_interval)
    
    async def _stream_derived_analytics(self):
        """Stream derived analytics to subscribers"""
        if not self.enable_derived_analytics:
            return
        
        while True:
            try:
                # Get symbols with recent data
                symbols_with_data = [
                    symbol for symbol, stream in self.data_streams.items()
                    if len(stream) >= 20  # Need enough data for calculations
                ]
                
                for symbol in symbols_with_data:
                    try:
                        # Calculate various derived analytics
                        analytics_configs = [
                            {'indicator_name': 'SMA_10', 'method': 'simple_moving_average', 'parameters': {'period': 10}},
                            {'indicator_name': 'RSI_14', 'method': 'relative_strength_index', 'parameters': {'period': 14}},
                            {'indicator_name': 'EMA_10', 'method': 'exponential_moving_average', 'parameters': {'period': 10}}
                        ]
                        
                        for config in analytics_configs:
                            await self.compute_custom_derived_analytics(symbol, config)
                            
                    except Exception as e:
                        logger.warning(f"Error computing analytics for {symbol}: {e}")
                
                await asyncio.sleep(self.stream_interval * 5)  # Less frequent than market data
                
            except Exception as e:
                logger.error(f"Error in derived analytics streaming: {e}")
                await asyncio.sleep(self.stream_interval * 5)
    
    async def _cleanup_old_data(self):
        """Clean up old data to prevent memory issues"""
        while True:
            try:
                cutoff_time = datetime.now() - timedelta(hours=1)
                
                # Clean up data streams
                for symbol in list(self.data_streams.keys()):
                    self.data_streams[symbol] = deque(
                        (data for data in self.data_streams[symbol] if data.timestamp > cutoff_time),
                        maxlen=self.max_queue_size
                    )
                
                # Clean up derived analytics
                for symbol in list(self.derived_analytics.keys()):
                    self.derived_analytics[symbol] = deque(
                        (analytics for analytics in self.derived_analytics[symbol] 
                         if analytics.calculation_time > cutoff_time),
                        maxlen=self.max_queue_size
                    )
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in data cleanup: {e}")
                await asyncio.sleep(300)
    
    async def _broadcast_to_subscribers(self, data: StreamingData):
        """Broadcast data to relevant subscribers"""
        for subscription in self.subscriptions.values():
            if not subscription.active:
                continue
            
            # Check if subscription is interested in this data
            if data.symbol in subscription.symbols and data.data_type in subscription.data_types:
                if subscription.callback:
                    try:
                        await subscription.callback(data)
                    except Exception as e:
                        logger.error(f"Error in subscription callback: {e}")
    
    async def _broadcast_derived_analytics(self, analytics: DerivedAnalytics):
        """Broadcast derived analytics to subscribers"""
        for subscription in self.subscriptions.values():
            if not subscription.active:
                continue
            
            # Check if subscription is interested in this symbol
            if analytics.symbol in subscription.symbols and 'analytics' in subscription.data_types:
                if subscription.callback:
                    try:
                        # Convert to StreamingData format
                        stream_data = StreamingData(
                            symbol=analytics.symbol,
                            data_type='analytics',
                            timestamp=analytics.calculation_time,
                            value=analytics.value,
                            metadata={
                                'indicator_name': analytics.indicator_name,
                                'input_data': analytics.input_data
                            }
                        )
                        await subscription.callback(stream_data)
                    except Exception as e:
                        logger.error(f"Error in analytics callback: {e}")
    
    def _calculate_sma(self, data: List[StreamingData], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(data) < period:
            return np.mean([d.value for d in data])
        
        recent_data = data[-period:]
        return np.mean([d.value for d in recent_data])
    
    def _calculate_ema(self, data: List[StreamingData], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return np.mean([d.value for d in data])
        
        values = [d.value for d in data[-period:]]
        alpha = 2 / (period + 1)
        ema = values[0]
        
        for value in values[1:]:
            ema = alpha * value + (1 - alpha) * ema
        
        return ema
    
    def _calculate_rsi(self, data: List[StreamingData], period: int) -> float:
        """Calculate Relative Strength Index"""
        if len(data) < period + 1:
            return 50  # Neutral
        
        values = [d.value for d in data[-(period + 1):]]
        gains = []
        losses = []
        
        for i in range(1, len(values)):
            change = values[i] - values[i-1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_bollinger_position(self, data: List[StreamingData], period: int) -> float:
        """Calculate position within Bollinger Bands"""
        if len(data) < period:
            return 0.5  # Middle
        
        values = [d.value for d in data[-period:]]
        sma = np.mean(values)
        std = np.std(values)
        
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        
        current_price = values[-1]
        
        if upper_band == lower_band:
            return 0.5
        
        position = (current_price - lower_band) / (upper_band - lower_band)
        return max(0, min(1, position))
    
    def _calculate_custom_formula(self, data: List[StreamingData], formula: str) -> float:
        """Calculate custom formula (simplified)"""
        if not data:
            return 0
        
        price = data[-1].value
        
        # Simple formula evaluation (in production, use proper expression parser)
        if 'price' in formula:
            try:
                # Very basic formula evaluation
                result = eval(formula.replace('price', str(price)))
                return result
            except:
                return price
        
        return price
    
    async def _handle_app_streaming_data(self, app_id: str, data: StreamingData):
        """Handle streaming data for specific app"""
        # Broadcast to WebSocket clients subscribed to this app
        message = {
            'type': 'app_data',
            'app_id': app_id,
            'data': {
                'symbol': data.symbol,
                'data_type': data.data_type,
                'timestamp': data.timestamp.isoformat(),
                'value': data.value,
                'metadata': data.metadata
            }
        }
        
        # Send to all connected WebSocket clients
        if self.websocket_clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.websocket_clients],
                return_exceptions=True
            )
    
    async def _deliver_to_websocket_channel(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver intelligence to WebSocket channel"""
        try:
            message = {
                'type': 'intelligence',
                'data': intelligence_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to all WebSocket clients
            if self.websocket_clients:
                await asyncio.gather(
                    *[client.send(json.dumps(message)) for client in self.websocket_clients],
                    return_exceptions=True
                )
            
            return {'success': True, 'delivered_to': len(self.websocket_clients)}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _deliver_to_webhook_channel(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver intelligence to webhook channel"""
        try:
            # Mock webhook delivery
            webhook_url = self.config.get('webhook_url', 'https://example.com/webhook')
            
            # In production, use actual HTTP request
            logger.info(f"Would deliver to webhook: {webhook_url}")
            
            return {'success': True, 'webhook_url': webhook_url}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _deliver_to_email_channel(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver intelligence to email channel"""
        try:
            # Mock email delivery
            email_recipients = self.config.get('email_recipients', ['admin@example.com'])
            
            # In production, use actual email service
            logger.info(f"Would deliver to email: {email_recipients}")
            
            return {'success': True, 'recipients': email_recipients}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _deliver_to_slack_channel(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver intelligence to Slack channel"""
        try:
            # Mock Slack delivery
            slack_webhook = self.config.get('slack_webhook', 'https://hooks.slack.com/services/...')
            
            # In production, use actual Slack API
            logger.info(f"Would deliver to Slack: {slack_webhook}")
            
            return {'success': True, 'slack_webhook': slack_webhook}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        total_data_points = sum(len(stream) for stream in self.data_streams.values())
        total_analytics = sum(len(analytics) for analytics in self.derived_analytics.values())
        
        # Rough estimation: 100 bytes per data point
        estimated_bytes = (total_data_points + total_analytics) * 100
        estimated_mb = estimated_bytes / (1024 * 1024)
        
        return estimated_mb

# Factory function
def get_realtime_streaming_module(config: Dict[str, Any] = None) -> RealtimeStreamingModule:
    """Factory function to get realtime streaming module"""
    return RealtimeStreamingModule(config)
