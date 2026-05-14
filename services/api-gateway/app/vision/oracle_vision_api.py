"""
Oracle Vision API - Unified interface for all visual AI modules
"""

from typing import Dict, List, Any
from .chart_vision import ChartVision, ChartPattern
from .tube_trader import TubeTrader
from .stream_sight import StreamSight
from .satellite_sight import SatelliteSight
from .social_scope import SocialScope


class OracleVisionAPI:
    """
    Unified API for Oracle Vision System
    Provides access to all 5 vision modules:
    - ChartVision: Pattern detection from charts
    - TubeTrader: YouTube content analysis
    - StreamSight: Live stream monitoring
    - SatelliteSight: Alternative data from satellite imagery
    - SocialScope: Social media visual sentiment
    """
    
    def __init__(self):
        self.chart_vision = ChartVision()
        self.tube_trader = TubeTrader()
        self.stream_sight = StreamSight()
        self.satellite_sight = SatelliteSight()
        self.social_scope = SocialScope()
    
    async def analyze_chart(self, symbol: str, ohlcv_data: Any) -> List[ChartPattern]:
        """Analyze chart data for patterns"""
        return self.chart_vision.analyze_chart(symbol, ohlcv_data)
    
    async def analyze_youtube_video(self, video_url: str) -> Dict[str, Any]:
        """Extract trading insights from YouTube video"""
        return await self.tube_trader.analyze_video(video_url)
    
    async def monitor_stream(self, stream_url: str) -> Dict[str, Any]:
        """Real-time analysis of financial livestream"""
        return await self.stream_sight.analyze_stream(stream_url)
    
    async def analyze_satellite_data(self, location: str, data_type: str) -> Dict[str, Any]:
        """Analyze satellite imagery for trading signals"""
        return await self.satellite_sight.analyze_location(location, data_type)
    
    async def analyze_social_media(self, platform: str, query: str) -> Dict[str, Any]:
        """Analyze social media visual content"""
        return await self.social_scope.analyze_content(platform, query)
    
    async def get_comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive visual analysis for a symbol
        Combines all 5 modules for complete picture
        """
        return {
            "symbol": symbol,
            "chart_patterns": [],  # Would be populated with actual analysis
            "youtube_sentiment": {},
            "stream_mentions": {},
            "satellite_signals": {},
            "social_sentiment": {},
            "combined_signal": "neutral",
            "confidence": 0.0,
            "timestamp": "2026-01-01T00:00:00Z"
        }
