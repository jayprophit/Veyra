"""Conspiracy Analyzer - Pattern detection for market manipulation theories"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class ConspiracyTheory(Enum):
    PLUNGE_PROTECTION = "plunge_protection_team"  # Fed intervention
    DARK_POOL_MANIPULATION = "dark_pool_manipulation"
    CITADEL_CONFLICT = "citadel_payment_for_order_flow"
    ALGO_MANIPULATION = "algorithmic_manipulation"
    INSIDER_NETWORK = "insider_trading_network"
    MEDIA_COORDINATION = "media_narrative_coordination"
    SHORT_LADDER = "short_ladder_attack"
    WASH_TRADING = "wash_trading_exchanges"
    PUMP_DUMP_RING = "pump_and_dump_ring"
    GOLD_REHYPOTHECATION = "basel_iii_gold"

@dataclass
class ConspiracyEvidence:
    theory: ConspiracyTheory
    evidence_score: float
    detected_patterns: List[str]
    confidence: str  # speculative, plausible, likely, confirmed
    data_sources: List[str]

class ConspiracyAnalyzer:
    """Analyze market data for patterns matching conspiracy theories"""
    
    def __init__(self):
        self.evidence_database: List[ConspiracyEvidence] = []
        self.theory_weights = {
            ConspiracyTheory.PLUNGE_PROTECTION: 0.3,
            ConspiracyTheory.DARK_POOL_MANIPULATION: 0.4,
            ConspiracyTheory.ALGO_MANIPULATION: 0.5,
            ConspiracyTheory.INSIDER_NETWORK: 0.2
        }
    
    def analyze_plunge_protection(self, market_data: List[Dict]) -> Dict:
        """Detect patterns suggesting PPT/Fed intervention"""
        if len(market_data) < 30:
            return {"analysis": "insufficient_data"}
        
        # Look for unnatural market recoveries
        recoveries = []
        for i in range(5, len(market_data)):
            # Check for sharp drop followed by immediate recovery
            drop = (market_data[i-4]["price"] - market_data[i]["price"]) / market_data[i-4]["price"]
            recovery = (market_data[i]["price"] - market_data[i-1]["price"]) / market_data[i-1]["price"]
            
            if drop > 0.02 and recovery > 0.015:  # 2% drop, 1.5% recovery
                recoveries.append({
                    "timestamp": market_data[i]["timestamp"],
                    "drop_pct": drop * 100,
                    "recovery_pct": recovery * 100,
                    "time_of_day": market_data[i].get("hour", 0)
                })
        
        # PPT typically acts during specific hours and at key levels
        ppt_indicators = {
            "recoveries_at_key_levels": sum(1 for r in recoveries if r["drop_pct"] > 2.5),
            "end_of_day_reversals": sum(1 for r in recoveries if r["time_of_day"] >= 15),
            "unnatural_v_shape": len(recoveries),
            "avg_recovery_time_minutes": 30  # Mock average
        }
        
        confidence = min(len(recoveries) * 0.1, 0.8)
        
        return {
            "theory": "Plunge Protection Team Intervention",
            "evidence_score": confidence,
            "indicators": ppt_indicators,
            "confidence_level": "speculative" if confidence < 0.3 else "plausible",
            "detected_events": recoveries[:5],
            "alternative_explanation": "Natural market dynamics, algorithmic trading",
            "trading_implication": "Buy dips during high volatility if pattern confirmed"
        }
    
    def analyze_dark_pool_manipulation(self, 
                                     dark_pool_volume: float,
                                     lit_exchange_volume: float,
                                     price_movement: float) -> Dict:
        """Analyze dark pool vs lit exchange activity"""
        total_volume = dark_pool_volume + lit_exchange_volume
        dark_pool_pct = dark_pool_volume / total_volume if total_volume > 0 else 0
        
        # High dark pool % with price movement = potential manipulation
        indicators = {
            "dark_pool_percentage": dark_pool_pct * 100,
            "volume_imbalance": abs(dark_pool_pct - 0.4),  # 40% is normal
            "price_movement_correlation": price_movement,
            "suspicious_activity": dark_pool_pct > 0.6 and abs(price_movement) > 0.02
        }
        
        # Large dark pool prints before price moves
        manipulation_score = 0
        if dark_pool_pct > 0.5:
            manipulation_score += 0.3
        if abs(price_movement) > 0.03:
            manipulation_score += 0.3
        if dark_pool_pct > 0.6:
            manipulation_score += 0.2
        
        return {
            "theory": "Dark Pool Manipulation",
            "evidence_score": manipulation_score,
            "confidence_level": "plausible" if manipulation_score > 0.5 else "speculative",
            "indicators": indicators,
            "interpretation": "Large institutions moving size off-exchange" if dark_pool_pct > 0.5 else "Normal market activity",
            "trading_implication": "Watch dark pool prints for directional signals" if manipulation_score > 0.4 else "No action needed"
        }
    
    def analyze_media_coordination(self, 
                                  news_headlines: List[str],
                                  sentiment_scores: List[float],
                                  publication_times: List[datetime]) -> Dict:
        """Detect synchronized media narratives"""
        if len(news_headlines) < 3:
            return {"analysis": "insufficient_data"}
        
        # Check for similar headlines
        from difflib import SequenceMatcher
        
        similarity_scores = []
        for i in range(len(news_headlines)):
            for j in range(i+1, len(news_headlines)):
                similarity = SequenceMatcher(None, news_headlines[i], news_headlines[j]).ratio()
                similarity_scores.append(similarity)
        
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
        
        # Check for synchronized timing
        time_diffs = []
        for i in range(1, len(publication_times)):
            diff = (publication_times[i] - publication_times[i-1]).total_seconds() / 60
            time_diffs.append(diff)
        
        # Multiple stories within minutes suggests coordination
        synchronized_timing = sum(1 for d in time_diffs if d < 10) / len(time_diffs) if time_diffs else 0
        
        coordination_score = (avg_similarity * 0.5) + (synchronized_timing * 0.5)
        
        return {
            "theory": "Media Narrative Coordination",
            "evidence_score": coordination_score,
            "confidence_level": "likely" if coordination_score > 0.7 else "plausible" if coordination_score > 0.5 else "speculative",
            "indicators": {
                "headline_similarity": avg_similarity,
                "synchronized_publications_pct": synchronized_timing * 100,
                "stories_within_10min": sum(1 for d in time_diffs if d < 10)
            },
            "trading_implication": "Fade the narrative" if coordination_score > 0.7 else "Trade the trend"
        }
    
    def analyze_short_ladder_attack(self, 
                                   price_data: List[float],
                                   volume_data: List[float],
                                   borrow_rate: float) -> Dict:
        """Detect coordinated short selling patterns"""
        if len(price_data) < 10:
            return {"analysis": "insufficient_data"}
        
        # Short ladder pattern: rapid price drops on moderate volume
        price_drops = []
        volume_ratios = []
        
        for i in range(1, len(price_data)):
            drop = (price_data[i-1] - price_data[i]) / price_data[i-1]
            price_drops.append(drop)
            
            if i < len(volume_data):
                vol_ratio = volume_data[i] / volume_data[i-1] if volume_data[i-1] > 0 else 1
                volume_ratios.append(vol_ratio)
        
        # Short ladder: price drops faster than volume would suggest
        ladder_indicators = 0
        for i in range(len(price_drops)):
            if price_drops[i] > 0.01:  # 1% drop
                if i < len(volume_ratios) and volume_ratios[i] < 1.5:  # Not huge volume
                    ladder_indicators += 1
        
        confidence = min(ladder_indicators / len(price_drops) * 2, 1.0) if price_drops else 0
        
        # High borrow rates suggest shorting pressure
        borrow_factor = min(borrow_rate / 0.30, 1.0) if borrow_rate else 0  # 30% is extreme
        
        final_score = (confidence * 0.6) + (borrow_factor * 0.4)
        
        return {
            "theory": "Short Ladder Attack",
            "evidence_score": final_score,
            "confidence_level": "likely" if final_score > 0.7 else "plausible" if final_score > 0.5 else "speculative",
            "indicators": {
                "rapid_price_drops": ladder_indicators,
                "borrow_rate": borrow_rate * 100 if borrow_rate else 0,
                "price_to_volume_ratio": confidence
            },
            "trading_implication": "Buy the dip if fundamentals intact" if final_score > 0.6 else "Short-term short, then reversal"
        }
    
    def gold_rehypothecation_analysis(self, 
                                    gold_price: float,
                                    gold_etf_holdings: float,
                                    physical_demand: float,
                                    basel_iii_date: date) -> Dict:
        """Analyze Basel III impact on gold rehypothecation"""
        today = date.today()
        days_to_basel = (basel_iii_date - today).days if basel_iii_date > today else 0
        
        # Calculate paper vs physical gold ratio
        estimated_paper_gold = gold_etf_holdings * 2.5  # Multiple claims on same gold
        physical_ratio = physical_demand / estimated_paper_gold if estimated_paper_gold > 0 else 0
        
        indicators = {
            "paper_to_physical_ratio": estimated_paper_gold / physical_demand if physical_demand > 0 else 0,
            "days_to_basel_iii": days_to_basel,
            "gold_price_momentum": gold_price,
            "physical_demand_surge": physical_ratio > 1.2
        }
        
        # Basel III makes gold a tier 1 asset, potentially increasing demand
        impact_score = 0.5
        if days_to_basel < 90:
            impact_score += 0.3
        if indicators["paper_to_physical_ratio"] > 100:
            impact_score += 0.2
        
        return {
            "theory": "Basel III Gold Rehypothecation Crisis",
            "evidence_score": impact_score,
            "confidence_level": "plausible" if impact_score > 0.6 else "speculative",
            "indicators": indicators,
            "prediction": "Gold price increase as banks must hold physical" if impact_score > 0.6 else "Gradual price adjustment",
            "trading_implication": "Long gold, long silver, avoid paper gold ETFs" if impact_score > 0.7 else "Monitor Basel implementation"
        }
    
    def get_all_analyses(self, market_snapshot: Dict) -> Dict:
        """Run all conspiracy theory analyses"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "market_conditions": market_snapshot,
            "analyses": [],
            "overall_market_manipulation_risk": 0.0,
            "highest_confidence_theory": None,
            "recommended_actions": []
        }
        
        # Run individual analyses
        if "market_data" in market_snapshot:
            ppt = self.analyze_plunge_protection(market_snapshot["market_data"])
            results["analyses"].append(ppt)
        
        if "dark_pool_data" in market_snapshot:
            dark_pool = self.analyze_dark_pool_manipulation(
                market_snapshot["dark_pool_data"]["volume"],
                market_snapshot["lit_volume"],
                market_snapshot["price_move"]
            )
            results["analyses"].append(dark_pool)
        
        # Calculate overall risk
        scores = [a.get("evidence_score", 0) for a in results["analyses"]]
        results["overall_market_manipulation_risk"] = max(scores) if scores else 0
        
        # Find highest confidence theory
        highest = max(results["analyses"], key=lambda x: x.get("evidence_score", 0), default={})
        results["highest_confidence_theory"] = highest.get("theory")
        
        # Generate recommendations
        if results["overall_market_manipulation_risk"] > 0.6:
            results["recommended_actions"].append("Increase caution - manipulation patterns detected")
            results["recommended_actions"].append("Use limit orders, avoid market orders")
            results["recommended_actions"].append("Consider defensive positions")
        
        return results
