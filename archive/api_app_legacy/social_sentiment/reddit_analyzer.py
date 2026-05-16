"""Reddit Analyzer - WSB and subreddit sentiment"""
from typing import Dict, List

class RedditAnalyzer:
    """Analyze Reddit sentiment for stocks and crypto"""
    
    MEME_STOCKS = ["GME", "AMC", "BB", "NOK", "BBBY", "PLTR", "TSLA"]
    
    def wsb_sentiment(self, mentions: int, upvote_ratio: float,
                     awards: int, sentiment_keywords: List[str]) -> Dict:
        """WallStreetBets sentiment score"""
        # Base hype score
        base_hype = min(mentions / 100, 10)
        
        # Engagement quality
        engagement = upvote_ratio * (1 + awards * 0.1)
        
        # Sentiment analysis from keywords
        bullish = sum(1 for k in sentiment_keywords if k in ["moon", "rocket", "buy", "calls", "tendies"])
        bearish = sum(1 for k in sentiment_keywords if k in ["crash", "dump", "sell", "puts", "bagholder"])
        
        sentiment_score = (bullish - bearish) / max(len(sentiment_keywords), 1)
        
        # Composite WSB score
        wsb_score = base_hype * engagement * (1 + sentiment_score)
        
        return {
            "wsb_hype_score": round(min(wsb_score, 100), 1),
            "sentiment": "extremely_bullish" if sentiment_score > 0.5 else "bullish" if sentiment_score > 0 else "bearish" if sentiment_score < -0.3 else "neutral",
            "mention_velocity": mentions,
            "upvote_quality": round(upvote_ratio * 100, 1),
            "meme_stock_status": "confirmed" if mentions > 1000 else "emerging" if mentions > 100 else "none"
        }
    
    def subreddit_correlation(self, ticker: str, subreddit_mentions: Dict[str, int]) -> Dict:
        """Analyze mentions across subreddits"""
        total_mentions = sum(subreddit_mentions.values())
        
        # Subreddit weights for reliability
        weights = {
            "wallstreetbets": 1.0, "stocks": 0.8, "investing": 0.9,
            "cryptocurrency": 0.7, "pennystocks": 0.5, "options": 0.8
        }
        
        weighted_score = sum(subreddit_mentions.get(k, 0) * weights.get(k, 0.5) 
                           for k in subreddit_mentions.keys())
        
        return {
            "ticker": ticker,
            "total_mentions": total_mentions,
            "weighted_sentiment_score": round(weighted_score, 0),
            "primary_source": max(subreddit_mentions.items(), key=lambda x: x[1])[0] if subreddit_mentions else "none",
            "cross_subreddit_buzz": len([v for v in subreddit_mentions.values() if v > 10])
        }
    
    def yolo_detection(self, position_size: float, account_value: float,
                      instrument: str) -> Dict:
        """Detect YOLO trades"""
        yolo_ratio = position_size / account_value if account_value > 0 else 0
        
        # YOLO classification
        if yolo_ratio > 0.9:
            yolo_level = "all_in"
            warning = "MAXIMUM RISK"
        elif yolo_ratio > 0.5:
            yolo_level = "aggressive"
            warning = "HIGH RISK"
        elif yolo_ratio > 0.25:
            yolo_level = "moderate"
            warning = "ELEVATED RISK"
        else:
            yolo_level = "conservative"
            warning = "STANDARD"
        
        return {
            "yolo_ratio": round(yolo_ratio * 100, 1),
            "yolo_classification": yolo_level,
            "risk_warning": warning,
            "position_size": position_size,
            "instrument_risk": "extreme" if instrument in ["options", "futures"] else "high"
        }
    
    def dd_quality_score(self, word_count: int, has_financials: bool,
                        has_charts: int, sources_cited: int) -> Dict:
        """Score due diligence post quality"""
        # Base score from length
        length_score = min(word_count / 500, 5)
        
        # Quality bonuses
        financial_bonus = 2 if has_financials else 0
        chart_bonus = min(has_charts * 0.5, 2)
        source_bonus = min(sources_cited * 0.5, 2)
        
        total = length_score + financial_bonus + chart_bonus + source_bonus
        
        return {
            "dd_quality_score": round(min(total, 10), 1),
            "reliability": "high" if total > 7 else "medium" if total > 4 else "low",
            "length_contribution": round(length_score, 1),
            "financial_analysis": has_financials,
            "charts_included": has_charts,
            "sources_count": sources_cited
        }
