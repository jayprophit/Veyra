"""Cognitive Bias Detector - Identify trading biases"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TradeDecision:
    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL, HOLD
    quantity: int
    price: float
    reasoning: str
    pnl: float = 0

class CognitiveBiasDetector:
    """Detect cognitive biases in trading behavior"""
    
    def __init__(self):
        self.bias_types = [
            "confirmation_bias",
            "recency_bias",
            "loss_aversion",
            "overconfidence",
            "anchoring",
            "herding",
            "sunk_cost",
            "availability_heuristic"
        ]
    
    def analyze_trade_history(self, trades: List[TradeDecision]) -> Dict:
        """Analyze trade history for biases"""
        biases = {}
        
        # Confirmation bias - seek confirming info after trade
        biases["confirmation_bias"] = self._detect_confirmation_bias(trades)
        
        # Recency bias - weight recent events more
        biases["recency_bias"] = self._detect_recency_bias(trades)
        
        # Loss aversion - hold losers too long
        biases["loss_aversion"] = self._detect_loss_aversion(trades)
        
        # Overconfidence - trade too frequently
        biases["overconfidence"] = self._detect_overconfidence(trades)
        
        # Herding - follow crowd
        biases["herding"] = self._detect_herding(trades)
        
        # Calculate overall bias score
        total_score = sum(b["score"] for b in biases.values())
        
        return {
            "biases_detected": biases,
            "overall_bias_risk": "HIGH" if total_score > 6 else "MEDIUM" if total_score > 3 else "LOW",
            "most_problematic": max(biases, key=lambda x: biases[x]["score"]),
            "recommendations": self._generate_recommendations(biases)
        }
    
    def _detect_confirmation_bias(self, trades: List[TradeDecision]) -> Dict:
        """Detect confirmation bias"""
        if len(trades) < 5:
            return {"score": 0, "evidence": "Insufficient data"}
        
        # Check if reasoning mentions only confirming evidence
        confirming_only = 0
        for trade in trades:
            reasoning = trade.reasoning.lower()
            # Look for one-sided reasoning
            if any(word in reasoning for word in ["obviously", "clearly", "definitely", "sure thing"]):
                confirming_only += 1
        
        score = min(3, confirming_only / len(trades) * 3)
        
        return {
            "score": round(score, 1),
            "evidence": f"{confirming_only} trades with absolute language",
            "example": "Using words like 'obviously' without considering counterarguments"
        }
    
    def _detect_recency_bias(self, trades: List[TradeDecision]) -> Dict:
        """Detect recency bias"""
        if len(trades) < 10:
            return {"score": 0, "evidence": "Insufficient data"}
        
        # Check if recent trades cluster around recent events
        recent_trades = sum(1 for t in trades if (datetime.utcnow() - t.timestamp).days < 7)
        older_trades = sum(1 for t in trades if (datetime.utcnow() - t.timestamp).days > 30)
        
        if recent_trades > older_trades * 2:
            score = 2.5
        elif recent_trades > older_trades:
            score = 1.5
        else:
            score = 0.5
        
        return {
            "score": score,
            "evidence": f"{recent_trades} recent trades vs {older_trades} older trades",
            "example": "Overweighting recent market events in decisions"
        }
    
    def _detect_loss_aversion(self, trades: List[TradeDecision]) -> Dict:
        """Detect loss aversion bias"""
        losing_trades = [t for t in trades if t.pnl < 0]
        winning_trades = [t for t in trades if t.pnl > 0]
        
        if not losing_trades or not winning_trades:
            return {"score": 0, "evidence": "No completed trades"}
        
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades)
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades)
        
        # Loss aversion: losses hurt ~2x more than equivalent gains feel good
        # Check if holding losers too long or taking winners too early
        loss_to_win_ratio = abs(avg_loss) / avg_win if avg_win > 0 else 0
        
        if loss_to_win_ratio > 2.5:
            score = 3
        elif loss_to_win_ratio > 1.5:
            score = 2
        else:
            score = 1
        
        return {
            "score": score,
            "evidence": f"Avg loss ${abs(avg_loss):.2f} vs avg win ${avg_win:.2f}",
            "example": "Holding losing positions too long, taking winners too early"
        }
    
    def _detect_overconfidence(self, trades: List[TradeDecision]) -> Dict:
        """Detect overconfidence bias"""
        if len(trades) < 10:
            return {"score": 0, "evidence": "Insufficient data"}
        
        # High frequency trading
        days_span = (trades[-1].timestamp - trades[0].timestamp).days
        trades_per_day = len(trades) / max(days_span, 1)
        
        # Large position sizes
        large_positions = sum(1 for t in trades if t.quantity > 1000)
        
        if trades_per_day > 2 and large_positions > len(trades) * 0.3:
            score = 3
        elif trades_per_day > 1:
            score = 2
        else:
            score = 1
        
        return {
            "score": score,
            "evidence": f"{trades_per_day:.1f} trades/day, {large_positions} large positions",
            "example": "Trading too frequently or with excessive size"
        }
    
    def _detect_herding(self, trades: List[TradeDecision]) -> Dict:
        """Detect herding behavior"""
        # Check if reasoning mentions following others
        herding_keywords = ["everyone is buying", "crowd", "following", "trending", "popular"]
        
        herding_count = sum(1 for t in trades if any(kw in t.reasoning.lower() for kw in herding_keywords))
        
        score = min(3, herding_count / max(len(trades), 1) * 6)
        
        return {
            "score": round(score, 1),
            "evidence": f"{herding_count} trades following crowd",
            "example": "Buying because 'everyone is buying'"
        }
    
    def _generate_recommendations(self, biases: Dict) -> List[str]:
        """Generate de-biasing recommendations"""
        recs = []
        
        if biases["confirmation_bias"]["score"] > 1.5:
            recs.append("Write down 3 reasons your trade could be wrong before entering")
        
        if biases["recency_bias"]["score"] > 1.5:
            recs.append("Review trades from 6+ months ago to get long-term perspective")
        
        if biases["loss_aversion"]["score"] > 1.5:
            recs.append("Set stop losses before entry and honor them mechanically")
        
        if biases["overconfidence"]["score"] > 1.5:
            recs.append("Reduce position sizes by 50% and trading frequency by half")
        
        if biases["herding"]["score"] > 1.5:
            recs.append("Do the opposite of what the crowd is doing (contrarian)")
        
        if not recs:
            recs.append("Bias levels acceptable - maintain current discipline")
        
        return recs
    
    def get_bias_report_card(self, trades: List[TradeDecision]) -> Dict:
        """Generate bias report card"""
        analysis = self.analyze_trade_history(trades)
        
        grades = {}
        for bias, data in analysis["biases_detected"].items():
            score = data["score"]
            if score < 1:
                grades[bias] = "A"
            elif score < 2:
                grades[bias] = "B"
            elif score < 2.5:
                grades[bias] = "C"
            else:
                grades[bias] = "D"
        
        return {
            "grades": grades,
            "overall_grade": "A" if analysis["overall_bias_risk"] == "LOW" else 
                           "B" if analysis["overall_bias_risk"] == "MEDIUM" else "C",
            "analysis": analysis,
            "improvement_areas": [b for b, g in grades.items() if g in ["C", "D"]]
        }
