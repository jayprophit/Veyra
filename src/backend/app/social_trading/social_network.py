"""
Social Trading Network
======================
Trader profiles, leaderboards, idea sharing, copy trading
Community features, following, comments, reputation system
"""
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PrivacyLevel(Enum):
    PUBLIC = "public"
    FOLLOWERS_ONLY = "followers_only"
    PRIVATE = "private"


@dataclass
class TraderProfile:
    """Trader public profile"""
    id: str
    username: str
    display_name: str
    bio: str
    avatar_url: str
    privacy_level: str
    created_at: datetime
    
    # Stats
    followers_count: int = 0
    following_count: int = 0
    total_trades: int = 0
    win_rate: float = 0.0
    avg_return: float = 0.0
    sharpe_ratio: float = 0.0
    rank: int = 0
    
    # Verification
    is_verified: bool = False
    is_pro_trader: bool = False


@dataclass
class TradeIdea:
    """Shared trading idea"""
    id: str
    author_id: str
    ticker: str
    direction: str  # 'long', 'short'
    thesis: str
    entry_price: Optional[float]
    target_price: Optional[float]
    stop_loss: Optional[float]
    timestamp: datetime
    privacy: str
    
    # Engagement
    likes: int = 0
    comments_count: int = 0
    shares: int = 0


@dataclass
class Comment:
    """Comment on trade idea"""
    id: str
    idea_id: str
    author_id: str
    content: str
    timestamp: datetime
    likes: int = 0


class SocialTradingNetwork:
    """
    Social trading features
    
    Features:
    - Trader profiles and leaderboards
    - Trade idea sharing
    - Comments and discussions
    - Copy trading (future)
    - Reputation system
    """
    
    def __init__(self):
        self.profiles: Dict[str, TraderProfile] = {}
        self.ideas: Dict[str, TradeIdea] = {}
        self.comments: Dict[str, List[Comment]] = {}
        self.followers: Dict[str, List[str]] = {}  # user_id -> list of follower_ids
        self.leaderboard_cache: List[TraderProfile] = []
        self.leaderboard_last_updated: Optional[datetime] = None
    
    def create_profile(self, username: str, display_name: str,
                      bio: str = "", privacy: str = PrivacyLevel.PUBLIC.value) -> TraderProfile:
        """Create new trader profile"""
        profile = TraderProfile(
            id=str(uuid.uuid4()),
            username=username,
            display_name=display_name,
            bio=bio,
            avatar_url="",
            privacy_level=privacy,
            created_at=datetime.now()
        )
        
        self.profiles[profile.id] = profile
        self.followers[profile.id] = []
        
        return profile
    
    def update_stats(self, profile_id: str, stats: Dict):
        """Update trader statistics"""
        if profile_id in self.profiles:
            profile = self.profiles[profile_id]
            
            if 'total_trades' in stats:
                profile.total_trades = stats['total_trades']
            if 'win_rate' in stats:
                profile.win_rate = stats['win_rate']
            if 'avg_return' in stats:
                profile.avg_return = stats['avg_return']
            if 'sharpe_ratio' in stats:
                profile.sharpe_ratio = stats['sharpe_ratio']
    
    def follow_trader(self, follower_id: str, following_id: str) -> bool:
        """Follow a trader"""
        if following_id not in self.followers:
            self.followers[following_id] = []
        
        if follower_id not in self.followers[following_id]:
            self.followers[following_id].append(follower_id)
            
            # Update counts
            if following_id in self.profiles:
                self.profiles[following_id].followers_count = len(self.followers[following_id])
            if follower_id in self.profiles:
                self.profiles[follower_id].following_count += 1
            
            return True
        
        return False
    
    def unfollow_trader(self, follower_id: str, following_id: str) -> bool:
        """Unfollow a trader"""
        if following_id in self.followers:
            if follower_id in self.followers[following_id]:
                self.followers[following_id].remove(follower_id)
                
                if following_id in self.profiles:
                    self.profiles[following_id].followers_count = len(self.followers[following_id])
                if follower_id in self.profiles:
                    self.profiles[follower_id].following_count -= 1
                
                return True
        
        return False
    
    def share_idea(self, author_id: str, ticker: str, direction: str,
                   thesis: str, entry: float = None, target: float = None,
                   stop: float = None, privacy: str = PrivacyLevel.PUBLIC.value) -> TradeIdea:
        """Share a trade idea"""
        idea = TradeIdea(
            id=str(uuid.uuid4()),
            author_id=author_id,
            ticker=ticker,
            direction=direction,
            thesis=thesis,
            entry_price=entry,
            target_price=target,
            stop_loss=stop,
            timestamp=datetime.now(),
            privacy=privacy
        )
        
        self.ideas[idea.id] = idea
        self.comments[idea.id] = []
        
        return idea
    
    def get_feed(self, user_id: str, limit: int = 20) -> List[TradeIdea]:
        """Get personalized feed of trade ideas"""
        if user_id not in self.followers:
            return []
        
        # Get ideas from followed traders
        followed_ids = self.followers.get(user_id, [])
        
        feed_ideas = []
        for idea in self.ideas.values():
            if idea.author_id in followed_ids or idea.privacy == PrivacyLevel.PUBLIC.value:
                feed_ideas.append(idea)
        
        # Sort by timestamp (newest first)
        feed_ideas.sort(key=lambda x: x.timestamp, reverse=True)
        
        return feed_ideas[:limit]
    
    def get_leaderboard(self, category: str = 'sharpe', limit: int = 10) -> List[Dict]:
        """Get trader leaderboard"""
        # Recalculate if needed
        if (self.leaderboard_last_updated is None or 
            (datetime.now() - self.leaderboard_last_updated).hours > 1):
            self._recalculate_leaderboard()
        
        # Sort by category
        if category == 'sharpe':
            sorted_profiles = sorted(
                self.profiles.values(),
                key=lambda x: x.sharpe_ratio,
                reverse=True
            )
        elif category == 'win_rate':
            sorted_profiles = sorted(
                self.profiles.values(),
                key=lambda x: x.win_rate,
                reverse=True
            )
        elif category == 'followers':
            sorted_profiles = sorted(
                self.profiles.values(),
                key=lambda x: x.followers_count,
                reverse=True
            )
        else:
            sorted_profiles = list(self.profiles.values())
        
        # Return top N
        return [
            {
                'rank': i + 1,
                'username': p.username,
                'display_name': p.display_name,
                'win_rate': p.win_rate,
                'sharpe_ratio': p.sharpe_ratio,
                'followers': p.followers_count,
                'is_pro': p.is_pro_trader,
                'is_verified': p.is_verified
            }
            for i, p in enumerate(sorted_profiles[:limit])
        ]
    
    def _recalculate_leaderboard(self):
        """Recalculate leaderboard rankings"""
        for i, profile in enumerate(sorted(self.profiles.values(), 
                                          key=lambda x: x.sharpe_ratio, 
                                          reverse=True)):
            profile.rank = i + 1
        
        self.leaderboard_last_updated = datetime.now()
    
    def add_comment(self, idea_id: str, author_id: str, content: str) -> Comment:
        """Add comment to trade idea"""
        comment = Comment(
            id=str(uuid.uuid4()),
            idea_id=idea_id,
            author_id=author_id,
            content=content,
            timestamp=datetime.now()
        )
        
        if idea_id in self.comments:
            self.comments[idea_id].append(comment)
        
        # Update comment count on idea
        if idea_id in self.ideas:
            self.ideas[idea_id].comments_count = len(self.comments[idea_id])
        
        return comment
    
    def like_idea(self, idea_id: str, user_id: str) -> bool:
        """Like a trade idea"""
        if idea_id in self.ideas:
            self.ideas[idea_id].likes += 1
            return True
        return False
    
    def get_trader_profile(self, user_id: str) -> Optional[Dict]:
        """Get public trader profile"""
        if user_id not in self.profiles:
            return None
        
        profile = self.profiles[user_id]
        
        return {
            'id': profile.id,
            'username': profile.username,
            'display_name': profile.display_name,
            'bio': profile.bio,
            'followers': profile.followers_count,
            'following': profile.following_count,
            'total_trades': profile.total_trades,
            'win_rate': profile.win_rate,
            'sharpe_ratio': profile.sharpe_ratio,
            'rank': profile.rank,
            'is_pro': profile.is_pro_trader,
            'is_verified': profile.is_verified,
            'joined': profile.created_at.strftime('%Y-%m-%d')
        }
    
    def get_popular_ideas(self, limit: int = 10) -> List[Dict]:
        """Get most popular trade ideas"""
        # Sort by engagement (likes + comments)
        sorted_ideas = sorted(
            self.ideas.values(),
            key=lambda x: x.likes + x.comments_count * 2,
            reverse=True
        )
        
        return [
            {
                'id': idea.id,
                'ticker': idea.ticker,
                'direction': idea.direction,
                'thesis': idea.thesis[:100] + '...' if len(idea.thesis) > 100 else idea.thesis,
                'author': self.profiles.get(idea.author_id, TraderProfile(
                    '', 'unknown', 'Unknown', '', '', 'public', datetime.now()
                )).username,
                'likes': idea.likes,
                'comments': idea.comments_count,
                'timestamp': idea.timestamp.strftime('%Y-%m-%d %H:%M')
            }
            for idea in sorted_ideas[:limit]
        ]
    
    def get_network_stats(self) -> Dict:
        """Get social network statistics"""
        return {
            'total_users': len(self.profiles),
            'total_ideas_shared': len(self.ideas),
            'total_comments': sum(len(c) for c in self.comments.values()),
            'total_connections': sum(len(f) for f in self.followers.values()),
            'top_ticker_ideas': self._get_top_tickers(),
            'verified_traders': len([p for p in self.profiles.values() if p.is_verified]),
            'pro_traders': len([p for p in self.profiles.values() if p.is_pro_trader])
        }
    
    def _get_top_tickers(self) -> List[Dict]:
        """Get most discussed tickers"""
        ticker_count = {}
        
        for idea in self.ideas.values():
            ticker = idea.ticker
            if ticker not in ticker_count:
                ticker_count[ticker] = 0
            ticker_count[ticker] += 1
        
        # Sort and return top 5
        sorted_tickers = sorted(ticker_count.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'ticker': t, 'ideas_count': c}
            for t, c in sorted_tickers[:5]
        ]


# Usage
def create_social_profile(username: str, display_name: str) -> TraderProfile:
    """Create social trading profile"""
    network = SocialTradingNetwork()
    return network.create_profile(username, display_name)


def get_leaderboard_preview() -> List[Dict]:
    """Get leaderboard preview"""
    network = SocialTradingNetwork()
    
    # Add some demo profiles
    for i in range(5):
        profile = network.create_profile(f"trader_{i}", f"Trader {i}")
        network.update_stats(profile.id, {
            'win_rate': 0.55 + i * 0.05,
            'sharpe_ratio': 1.5 + i * 0.3,
            'total_trades': 100 + i * 50
        })
    
    return network.get_leaderboard('sharpe', 5)


def share_trading_idea(author_id: str, ticker: str, direction: str, 
                      thesis: str) -> TradeIdea:
    """Share a trading idea"""
    network = SocialTradingNetwork()
    return network.share_idea(author_id, ticker, direction, thesis)
