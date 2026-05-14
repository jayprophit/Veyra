"""Social Media Video Analyzer - Compact Version"""
import re
from typing import Dict, List
from collections import Counter

class SocialVideoAnalyzer:
    """Extract trading signals from TikTok/YouTube videos"""
    
    BRAND_MAP = {
        'apple': 'AAPL', 'iphone': 'AAPL', 'tesla': 'TSLA', 'nvidia': 'NVDA',
        'amazon': 'AMZN', 'netflix': 'NFLX', 'target': 'TGT', 'walmart': 'WMT',
        'nike': 'NKE', 'robinhood': 'HOOD', 'gamestop': 'GME', 'amc': 'AMC'
    }
    
    def analyze_mentions(self, text: str, metadata: Dict) -> List[Dict]:
        """Analyze video text for brand mentions and sentiment"""
        text = text.lower()
        signals = []
        
        for brand, ticker in self.BRAND_MAP.items():
            if brand in text:
                # Simple sentiment
                pos = sum(1 for w in ['love', 'great', 'best', 'buy'] if w in text)
                neg = sum(1 for w in ['hate', 'bad', 'worst', 'avoid'] if w in text)
                
                sentiment = (pos - neg) / 10
                views = metadata.get('views', 0)
                
                signals.append({
                    'ticker': ticker,
                    'brand': brand,
                    'sentiment': round(sentiment, 2),
                    'views': views,
                    'signal': 'BULLISH' if sentiment > 0.3 else 'BEARISH' if sentiment < -0.3 else 'NEUTRAL',
                    'strength': min(abs(sentiment) * (views / 100000), 1.0)
                })
        
        return signals
    
    def get_trending(self, videos: List[Dict]) -> List[Dict]:
        """Get trending stocks from video batch"""
        all_signals = []
        for video in videos:
            text = f"{video.get('caption', '')} {video.get('transcription', '')}"
            all_signals.extend(self.analyze_mentions(text, video))
        
        # Aggregate by ticker
        by_ticker = {}
        for sig in all_signals:
            t = sig['ticker']
            if t not in by_ticker:
                by_ticker[t] = []
            by_ticker[t].append(sig)
        
        trending = []
        for ticker, sigs in by_ticker.items():
            trending.append({
                'ticker': ticker,
                'mentions': len(sigs),
                'avg_sentiment': round(sum(s['sentiment'] for s in sigs) / len(sigs), 2),
                'total_views': sum(s['views'] for s in sigs),
                'score': sum(s['strength'] for s in sigs)
            })
        
        return sorted(trending, key=lambda x: x['score'], reverse=True)[:20]
