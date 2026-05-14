"""Form 4 Analyzer - Analyze insider trading filings"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TransactionType(Enum):
    PURCHASE = "P"
    SALE = "S"
    EXERCISE = "E"
    GRANT = "G"

class InsiderRole(Enum):
    CEO = "Chief Executive Officer"
    CFO = "Chief Financial Officer"
    COO = "Chief Operating Officer"
    DIRECTOR = "Director"
    VP = "Vice President"
    TEN_PERCENT = "10% Owner"
    GENERAL_COUNSEL = "General Counsel"

@dataclass
class Form4Filing:
    symbol: str
    insider_name: str
    insider_role: InsiderRole
    transaction_type: TransactionType
    transaction_date: datetime
    shares: int
    price: float
    shares_owned_after: int
    is_direct: bool  # Direct ownership vs indirect

class Form4Analyzer:
    """Analyze SEC Form 4 insider filings"""
    
    def __init__(self):
        self.filings: List[Form4Filing] = []
        self.role_weights = {
            InsiderRole.CEO: 5,
            InsiderRole.CFO: 4,
            InsiderRole.COO: 4,
            InsiderRole.TEN_PERCENT: 4,
            InsiderRole.DIRECTOR: 3,
            InsiderRole.VP: 2,
            InsiderRole.GENERAL_COUNSEL: 2
        }
    
    def add_filing(self, filing: Form4Filing):
        """Add Form 4 filing to database"""
        self.filings.append(filing)
    
    def analyze_insider_sentiment(self, symbol: str, 
                                  days: int = 90) -> Dict:
        """Analyze insider sentiment for a stock"""
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        
        symbol_filings = [
            f for f in self.filings
            if f.symbol == symbol and f.transaction_date.timestamp() > cutoff
        ]
        
        if not symbol_filings:
            return {"error": "No recent filings found"}
        
        # Aggregate buys and sells
        total_buy_shares = 0
        total_sell_shares = 0
        total_buy_value = 0
        total_sell_value = 0
        
        weighted_buys = 0
        weighted_sells = 0
        
        for f in symbol_filings:
            weight = self.role_weights.get(f.insider_role, 1)
            
            if f.transaction_type == TransactionType.PURCHASE:
                total_buy_shares += f.shares
                total_buy_value += f.shares * f.price
                weighted_buys += f.shares * weight
            elif f.transaction_type == TransactionType.SALE:
                total_sell_shares += f.shares
                total_sell_value += f.shares * f.price
                weighted_sells += f.shares * weight
        
        # Calculate sentiment score (-100 to +100)
        total_volume = weighted_buys + weighted_sells
        if total_volume == 0:
            sentiment_score = 0
        else:
            sentiment_score = ((weighted_buys - weighted_sells) / total_volume) * 100
        
        # Cluster analysis - are multiple insiders acting?
        unique_buyers = len(set(f.insider_name for f in symbol_filings 
                               if f.transaction_type == TransactionType.PURCHASE))
        unique_sellers = len(set(f.insider_name for f in symbol_filings 
                                if f.transaction_type == TransactionType.SALE))
        
        return {
            "symbol": symbol,
            "period_days": days,
            "total_filings": len(symbol_filings),
            "buy_volume_shares": total_buy_shares,
            "sell_volume_shares": total_sell_shares,
            "buy_value": round(total_buy_value, 2),
            "sell_value": round(total_sell_value, 2),
            "sentiment_score": round(sentiment_score, 1),
            "sentiment_label": self._get_sentiment_label(sentiment_score),
            "unique_buyers": unique_buyers,
            "unique_sellers": unique_sellers,
            "cluster_signal": "STRONG" if unique_buyers >= 3 else "MODERATE" if unique_buyers >= 2 else "SINGLE",
            "signal_strength": abs(sentiment_score) / 100
        }
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert score to sentiment label"""
        if score > 50:
            return "VERY_BULLISH"
        elif score > 20:
            return "BULLISH"
        elif score < -50:
            return "VERY_BEARISH"
        elif score < -20:
            return "BEARISH"
        return "NEUTRAL"
    
    def detect_cluster_buying(self, symbol: str, days: int = 30) -> Dict:
        """Detect cluster buying patterns"""
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        
        recent_filings = [
            f for f in self.filings
            if f.symbol == symbol 
            and f.transaction_date.timestamp() > cutoff
            and f.transaction_type == TransactionType.PURCHASE
        ]
        
        if len(recent_filings) < 2:
            return {"cluster_detected": False}
        
        # Group by date windows
        by_week = {}
        for f in recent_filings:
            week_key = f.transaction_date.strftime("%Y-W%U")
            if week_key not in by_week:
                by_week[week_key] = []
            by_week[week_key].append(f)
        
        # Find clusters
        clusters = []
        for week, filings in by_week.items():
            if len(filings) >= 2:
                total_shares = sum(f.shares for f in filings)
                total_value = sum(f.shares * f.price for f in filings)
                unique_insiders = len(set(f.insider_name for f in filings))
                
                clusters.append({
                    "week": week,
                    "insider_count": unique_insiders,
                    "total_shares": total_shares,
                    "total_value": round(total_value, 2),
                    "avg_price": round(total_value / total_shares, 2) if total_shares > 0 else 0
                })
        
        best_cluster = max(clusters, key=lambda x: x["total_value"]) if clusters else None
        
        return {
            "cluster_detected": len(clusters) > 0,
            "clusters_found": len(clusters),
            "best_cluster": best_cluster,
            "interpretation": "Multiple insiders buying - bullish signal" if best_cluster and best_cluster["insider_count"] >= 3 else "Some insider interest" if clusters else "No cluster activity"
        }
    
    def find_unusual_activity(self, min_transaction_value: float = 100000) -> List[Dict]:
        """Find unusually large insider transactions"""
        unusual = []
        
        for f in self.filings:
            value = f.shares * f.price
            if value >= min_transaction_value:
                unusual.append({
                    "symbol": f.symbol,
                    "insider": f.insider_name,
                    "role": f.insider_role.value,
                    "type": "BUY" if f.transaction_type == TransactionType.PURCHASE else "SELL",
                    "shares": f.shares,
                    "value": round(value, 2),
                    "date": f.transaction_date.strftime("%Y-%m-%d"),
                    "significance": "MAJOR" if value > 1000000 else "SIGNIFICANT"
                })
        
        return sorted(unusual, key=lambda x: x["value"], reverse=True)[:20]
    
    def track_c_level_activity(self, symbol: str = None) -> Dict:
        """Track C-suite executive transactions"""
        c_level_roles = [InsiderRole.CEO, InsiderRole.CFO, InsiderRole.COO]
        
        c_level_filings = [
            f for f in self.filings
            if f.insider_role in c_level_roles
            and (symbol is None or f.symbol == symbol)
        ]
        
        buys = [f for f in c_level_filings if f.transaction_type == TransactionType.PURCHASE]
        sells = [f for f in c_level_filings if f.transaction_type == TransactionType.SALE]
        
        total_buy = sum(f.shares * f.price for f in buys)
        total_sell = sum(f.shares * f.price for f in sells)
        
        return {
            "scope": symbol if symbol else "ALL_SYMBOLS",
            "c_level_buys": len(buys),
            "c_level_sells": len(sells),
            "buy_value": round(total_buy, 2),
            "sell_value": round(total_sell, 2),
            "net_activity": round(total_buy - total_sell, 2),
            "sentiment": "ACCUMULATING" if total_buy > total_sell * 2 else "DISTRIBUTING" if total_sell > total_buy * 2 else "NEUTRAL",
            "recent_c_level_transactions": [
                {
                    "symbol": f.symbol,
                    "executive": f.insider_name,
                    "role": f.insider_role.value,
                    "action": "BOUGHT" if f.transaction_type == TransactionType.PURCHASE else "SOLD",
                    "value": round(f.shares * f.price, 2),
                    "date": f.transaction_date.strftime("%Y-%m-%d")
                }
                for f in sorted(c_level_filings, key=lambda x: x.transaction_date, reverse=True)[:10]
            ]
        }
    
    def generate_insider_report(self, symbol: str) -> Dict:
        """Generate comprehensive insider activity report"""
        sentiment = self.analyze_insider_sentiment(symbol, days=90)
        cluster = self.detect_cluster_buying(symbol, days=30)
        c_level = self.track_c_level_activity(symbol)
        
        # Overall signal
        signals = []
        if sentiment.get("sentiment_label") in ["BULLISH", "VERY_BULLISH"]:
            signals.append("Positive insider sentiment")
        if cluster.get("cluster_detected"):
            signals.append("Cluster buying detected")
        if c_level.get("sentiment") == "ACCUMULATING":
            signals.append("C-level accumulation")
        
        signal_count = len(signals)
        
        return {
            "symbol": symbol,
            "summary": {
                "insider_sentiment": sentiment.get("sentiment_label", "UNKNOWN"),
                "cluster_activity": "YES" if cluster.get("cluster_detected") else "NO",
                "c_level_stance": c_level.get("sentiment", "UNKNOWN"),
                "total_buy_value": sentiment.get("buy_value", 0),
                "total_sell_value": sentiment.get("sell_value", 0)
            },
            "signals": signals,
            "overall_rating": "STRONG_BUY" if signal_count >= 3 else "BUY" if signal_count >= 2 else "NEUTRAL" if signal_count >= 1 else "NO_SIGNAL",
            "detailed_analysis": {
                "sentiment_analysis": sentiment,
                "cluster_analysis": cluster,
                "c_level_activity": c_level
            }
        }
