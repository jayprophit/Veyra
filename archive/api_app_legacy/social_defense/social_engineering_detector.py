"""Social Engineering Detector - Detect manipulation campaigns"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class ManipulationType(Enum):
    BOT_CAMPAIGN = "bot_campaign"
    ASTROTURFING = "astroturfing"
    PUMP_GROUP = "pump_group"
    FAKE_NEWS = "fake_news"
    IMPERSONATION = "impersonation"
    SOCIAL_PROOF = "social_proof_manipulation"

@dataclass
class SocialPost:
    id: str
    author: str
    content: str
    timestamp: datetime
    platform: str
    engagement: int
    tickers: List[str]

class SocialEngineeringDetector:
    """Detect social engineering attacks on markets"""
    
    def __init__(self):
        self.suspicious_patterns = [
            "guaranteed profit", "100% sure", "can't lose", "insider info",
            "secret strategy", "limited spots", "dm for details", "pay to join"
        ]
        self.manipulation_history = []
    
    def analyze_post(self, post: SocialPost) -> Dict:
        """Analyze single post for manipulation signals"""
        content_lower = post.content.lower()
        
        # Check for manipulation keywords
        manipulation_score = sum(1 for p in self.suspicious_patterns if p in content_lower)
        
        # Check for urgency tactics
        urgency = content_lower.count("now") + content_lower.count("urgent") + content_lower.count("hurry")
        
        # Check for social proof manipulation
        social_proof = content_lower.count("everyone is buying") + content_lower.count("smart money")
        
        # Check for fake scarcity
        scarcity = content_lower.count("limited time") + content_lower.count("last chance")
        
        total_score = manipulation_score * 10 + urgency * 5 + social_proof * 8 + scarcity * 5
        
        return {
            "post_id": post.id,
            "author": post.author,
            "manipulation_score": min(100, total_score),
            "indicators": {
                "suspicious_language": manipulation_score > 0,
                "urgency_tactics": urgency > 2,
                "social_proof_manipulation": social_proof > 0,
                "artificial_scarcity": scarcity > 0
            },
            "risk_level": "HIGH" if total_score > 50 else "MEDIUM" if total_score > 20 else "LOW",
            "tickers_affected": post.tickers
        }
    
    def detect_pump_group(self, posts: List[SocialPost], timeframe_minutes: int = 30) -> Dict:
        """Detect coordinated pump group activity"""
        recent_posts = [
            p for p in posts 
            if (datetime.utcnow() - p.timestamp).total_seconds() / 60 < timeframe_minutes
        ]
        
        # Group by ticker
        ticker_posts = {}
        for post in recent_posts:
            for ticker in post.tickers:
                if ticker not in ticker_posts:
                    ticker_posts[ticker] = []
                ticker_posts[ticker].append(post)
        
        # Detect pump patterns
        pumps = []
        for ticker, t_posts in ticker_posts.items():
            if len(t_posts) < 5:  # Need at least 5 posts
                continue
            
            # Check for coordinated timing
            timestamps = sorted([p.timestamp for p in t_posts])
            time_spread = (timestamps[-1] - timestamps[0]).total_seconds() / 60
            
            # Check for similar language patterns
            contents = [p.content.lower() for p in t_posts]
            common_words = set(contents[0].split())
            for c in contents[1:]:
                common_words &= set(c.split())
            
            # If coordinated (close timing + similar language)
            if time_spread < 10 and len(common_words) > 5:
                pumps.append({
                    "ticker": ticker,
                    "post_count": len(t_posts),
                    "time_spread_minutes": round(time_spread, 1),
                    "coordination_score": "HIGH",
                    "likely_pump": True,
                    "recommendation": "AVOID - Coordinated pump detected"
                })
        
        return {
            "pump_groups_detected": len(pumps),
            "pumps": pumps,
            "overall_threat_level": "HIGH" if len(pumps) > 2 else "MEDIUM" if pumps else "LOW"
        }
    
    def detect_astroturfing(self, posts: List[SocialPost]) -> Dict:
        """Detect fake grassroots campaigns"""
        # Look for accounts with suspicious characteristics
        author_stats = {}
        for post in posts:
            if post.author not in author_stats:
                author_stats[post.author] = {
                    "posts": 0,
                    "tickers": set(),
                    "avg_engagement": []
                }
            author_stats[post.author]["posts"] += 1
            author_stats[post.author]["tickers"].update(post.tickers)
            author_stats[post.author]["avg_engagement"].append(post.engagement)
        
        suspicious_accounts = []
        for author, stats in author_stats.items():
            avg_eng = sum(stats["avg_engagement"]) / len(stats["avg_engagement"]) if stats["avg_engagement"] else 0
            
            # Red flags
            red_flags = 0
            if stats["posts"] > 10:  # Spamming
                red_flags += 1
            if len(stats["tickers"]) > 5:  # Many tickers
                red_flags += 1
            if avg_eng < 5:  # Low engagement (bots)
                red_flags += 1
            
            if red_flags >= 2:
                suspicious_accounts.append({
                    "author": author,
                    "red_flags": red_flags,
                    "posts": stats["posts"],
                    "tickers_promoted": list(stats["tickers"]),
                    "likely_bot": red_flags >= 3
                })
        
        return {
            "suspicious_accounts": len(suspicious_accounts),
            "accounts": suspicious_accounts,
            "astroturfing_detected": len(suspicious_accounts) > 3,
            "recommendation": "VERIFY sources" if suspicious_accounts else "Normal activity"
        }
    
    def generate_protection_strategy(self, manipulation_type: ManipulationType, 
                                    affected_tickers: List[str]) -> Dict:
        """Generate protection strategy"""
        strategies = {
            ManipulationType.BOT_CAMPAIGN: {
                "detection": "Monitor for repetitive identical posts",
                "protection": "Wait 24h before acting on social signals",
                "indicators": ["Same post multiple times", "New accounts", "No engagement"]
            },
            ManipulationType.PUMP_GROUP: {
                "detection": "Sudden coordinated ticker mentions",
                "protection": "Inverse trade - sell into pump",
                "indicators": ["DM to join groups", "Pay for signals", "Guaranteed returns"]
            },
            ManipulationType.FAKE_NEWS: {
                "detection": "Verify through multiple sources",
                "protection": "Cross-reference with SEC filings",
                "indicators": ["No source cited", "Sensational headline", "Urgency"]
            },
            ManipulationType.IMPERSONATION: {
                "detection": "Verify account handles carefully",
                "protection": "Only trust verified accounts",
                "indicators": ["Slight spelling variation", "New account", "Urgent request"]
            }
        }
        
        strategy = strategies.get(manipulation_type, {})
        
        return {
            "manipulation_type": manipulation_type.value,
            "affected_tickers": affected_tickers,
            "strategy": strategy,
            "alert_level": "CRITICAL" if len(affected_tickers) > 3 else "HIGH",
            "action": "VERIFY_ALL_SOURCES"
        }
