"""
Auto Podcast Generator
Creates daily/weekly financial podcasts from market data automatically
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
import json

@dataclass
class PodcastEpisode:
    episode_id: str; title: str; description: str; duration_minutes: int
    topics: List[str]; tickers_mentioned: List[str]; audio_url: str
    publish_date: date; download_count: int = 0; rating: float = 0.0

class AutoPodcastGenerator:
    """AI-generated financial podcast system"""
    
    def __init__(self):
        self.episodes: List[PodcastEpisode] = []
        self.show_formats = {
            "market_minute": {"duration": 5, "frequency": "daily"},
            "weekly_wrap": {"duration": 30, "frequency": "weekly"},
            "deep_dive": {"duration": 60, "frequency": "bi-weekly"},
            "interview_series": {"duration": 45, "frequency": "weekly"}
        }
    
    def generate_episode(self, format_type: str = "market_minute",
                        market_data: Optional[Dict] = None) -> Dict:
        """Generate podcast episode from market data"""
        
        if not market_data:
            market_data = self._get_mock_market_data()
        
        # Generate content based on format
        format_info = self.show_formats.get(format_type, self.show_formats["market_minute"])
        
        # Create script
        script = self._generate_script(format_type, market_data)
        
        # Generate audio (mock - would use ElevenLabs, AWS Polly, etc.)
        episode_id = f"EP_{datetime.utcnow().strftime('%Y%m%d')}_{format_type}"
        
        episode = PodcastEpisode(
            episode_id=episode_id,
            title=script["title"],
            description=script["description"],
            duration_minutes=format_info["duration"],
            topics=script["topics"],
            tickers_mentioned=script["tickers"],
            audio_url=f"https://cdn.veyra.com/podcasts/{episode_id}.mp3",
            publish_date=date.today()
        )
        
        self.episodes.append(episode)
        
        return {
            "success": True, "episode_id": episode_id,
            "title": script["title"], "duration": format_info["duration"],
            "topics": script["topics"], "tickers": script["tickers"],
            "script_preview": script["content"][:200] + "...",
            "monetization_estimate_usd": format_info["duration"] * 0.5  # $0.50 per minute
        }
    
    def _get_mock_market_data(self) -> Dict:
        """Get market data for podcast content"""
        return {
            "sp500_change": 1.2, "nasdaq_change": 2.1, "top_movers": ["AAPL", "TSLA", "NVDA"],
            "earnings_today": ["MSFT", "GOOGL"], "crypto_change": {"BTC": 3.5, "ETH": 2.8},
            "economic_news": ["Fed meeting", "Jobs report", "Inflation data"]
        }
    
    def _generate_script(self, format_type: str, market_data: Dict) -> Dict:
        """Generate podcast script"""
        scripts = {
            "market_minute": {
                "title": f"Market Minute - {date.today().strftime('%B %d, %Y')}",
                "description": "Your daily 5-minute market briefing",
                "content": f"Good morning traders. S&P 500 up {market_data['sp500_change']}%. Top movers today are {', '.join(market_data['top_movers'][:3])}. Crypto showing strength with Bitcoin up {market_data['crypto_change']['BTC']}%.",
                "topics": ["market summary", "top movers", "crypto"],
                "tickers": market_data["top_movers"]
            },
            "weekly_wrap": {
                "title": f"Weekly Market Wrap - Week of {date.today().strftime('%B %d')}",
                "description": "Complete weekly market analysis and next week preview",
                "content": f"This week in markets: S&P gained {market_data['sp500_change']}%. Tech led with {market_data['nasdaq_change']}% gains. Earnings season continues with {len(market_data['earnings_today'])} major companies reporting.",
                "topics": ["weekly review", "sector performance", "earnings preview"],
                "tickers": market_data["earnings_today"] + market_data["top_movers"]
            }
        }
        return scripts.get(format_type, scripts["market_minute"])
    
    def get_feed(self, limit: int = 10) -> List[Dict]:
        """Get podcast RSS feed content"""
        return [{"id": e.episode_id, "title": e.title, "date": e.publish_date.isoformat(),
                 "duration": e.duration_minutes, "url": e.audio_url} for e in self.episodes[-limit:]]
    
    def estimate_revenue(self) -> Dict:
        """Estimate podcast revenue"""
        total_episodes = len(self.episodes)
        avg_duration = sum(e.duration_minutes for e in self.episodes) / total_episodes if total_episodes > 0 else 0
        
        # Revenue estimates
        ad_revenue = total_episodes * avg_duration * 0.25  # $0.25 per minute
        sponsorship = total_episodes * 50  # $50 per episode sponsor
        premium_subs = 1000 * 5  # 1000 subscribers at $5/month
        
        return {"monthly_ad_revenue_usd": float(ad_revenue), "monthly_sponsorship_usd": float(sponsorship),
                "monthly_premium_usd": float(premium_subs), "total_monthly_usd": float(ad_revenue + sponsorship + premium_subs)}
