"""Narrative Patterns - Story-based trading pattern recognition"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class NarrativeArc(Enum):
    RISE_FALL = "rise_and_fall"          # Hubris -> Nemesis
    UNDERDOG = "underdog"                # Overcoming odds
    REDEMPTION = "redemption"            # Fall then rise
    TRAGEDY = "tragedy"                  # Fatal flaw
    COMEDY = "comedy"                    # Resolution of confusion
    QUEST = "quest"                      # Journey to goal
    VOYAGE = "voyage"                    # Journey and return

class MarketPhase(Enum):
    SETUP = "setup"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"

@dataclass
class MarketNarrative:
    symbol: str
    arc: NarrativeArc
    current_phase: MarketPhase
    protagonist: str  # Bull or Bear
    supporting_chars: List[str]  # Other factors
    plot_twists: List[str]
    predicted_ending: str

class NarrativePatternTrader:
    """Trade based on narrative pattern recognition"""
    
    def __init__(self):
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load narrative patterns"""
        return {
            NarrativeArc.RISE_FALL: {
                "description": "Hero rises too high, then falls",
                "market_example": "Parabolic stock that crashes",
                "phases": ["SETUP", "RISING_ACTION", "CLIMAX", "TRAGEDY"],
                "trade_strategy": "Short at climax, cover at resolution",
                "examples": ["GME 2021", "TSLA 2020"],
                "indicators": ["Euphoria", "High volume", "Media saturation"]
            },
            NarrativeArc.UNDERDOG: {
                "description": "Underestimated protagonist wins",
                "market_example": "Hated stock that surprises",
                "phases": ["SETUP", "STRUGGLE", "TURNING_POINT", "VICTORY"],
                "trade_strategy": "Buy at struggle, sell at victory",
                "examples": ["AAPL 1997", "F 2020"],
                "indicators": ["High short interest", "Low sentiment", "Turnaround plan"]
            },
            NarrativeArc.REDEMPTION: {
                "description": "Fallen hero rises again",
                "market_example": "Bankrupt company that recovers",
                "phases": ["FALL", "ROCK_BOTTOM", "CLIMB", "REDEMPTION"],
                "trade_strategy": "Buy at rock bottom, sell at redemption",
                "examples": ["GM 2009", "AAL 2020"],
                "indicators": ["Bankruptcy/restructuring", "New management", "Cost cutting"]
            },
            NarrativeArc.TRAGEDY: {
                "description": "Fatal flaw destroys protagonist",
                "market_example": "Fraud or business failure",
                "phases": ["SUCCESS", "HUBRIS", "FATAL_ACT", "COLLAPSE"],
                "trade_strategy": "Sell at hubris, short at fatal act",
                "examples": ["ENRON", "LEHMAN", "FTX"],
                "indicators": ["Aggressive accounting", "High leverage", "Cult of personality"]
            },
            NarrativeArc.QUEST: {
                "description": "Journey to achieve goal",
                "market_example": "Growth stock pursuing TAM",
                "phases": ["CALL_TO_ADVENTURE", "OBSTACLES", "ORDEAL", "ACHIEVEMENT"],
                "trade_strategy": "Buy early, hold through obstacles, sell at achievement",
                "examples": ["AMZN 1997-2015", "NFLX streaming transition"],
                "indicators": ["Clear mission", "Recurring revenue", "Expanding market"]
            }
        }
    
    def analyze_stock_narrative(self, symbol: str, price_data: List[Dict], 
                              news_data: List[Dict]) -> MarketNarrative:
        """Analyze the narrative arc of a stock"""
        
        # Determine arc based on price pattern
        if len(price_data) < 20:
            return MarketNarrative(symbol, NarrativeArc.QUEST, MarketPhase.SETUP, 
                                 "Unknown", [], [], "Insufficient data")
        
        # Calculate price trajectory
        first_price = price_data[0]["close"]
        last_price = price_data[-1]["close"]
        peak = max([p["high"] for p in price_data])
        trough = min([p["low"] for p in price_data])
        
        # Determine arc
        if peak > first_price * 3 and last_price < peak * 0.6:
            arc = NarrativeArc.RISE_FALL
            phase = MarketPhase.FALLING_ACTION if last_price < peak * 0.7 else MarketPhase.CLIMAX
            protagonist = "Bulls (defeated)"
        elif first_price < last_price * 0.5 and last_price > first_price * 2:
            arc = NarrativeArc.UNDERDOG if first_price < first_price * 0.8 else NarrativeArc.REDEMPTION
            phase = MarketPhase.RISING_ACTION
            protagonist = "Bulls"
        elif last_price < first_price * 0.3:
            arc = NarrativeArc.TRAGEDY
            phase = MarketPhase.RESOLUTION
            protagonist = "Bears (victorious)"
        else:
            arc = NarrativeArc.QUEST
            phase = MarketPhase.SETUP if last_price < first_price * 1.1 else MarketPhase.RISING_ACTION
            protagonist = "Bulls"
        
        # Identify plot twists from news
        plot_twists = [n["headline"] for n in news_data[-5:]] if news_data else ["None detected"]
        
        # Predict ending
        predicted_ending = self._predict_ending(arc, phase, last_price, peak)
        
        return MarketNarrative(
            symbol=symbol,
            arc=arc,
            current_phase=phase,
            protagonist=protagonist,
            supporting_chars=["Volume", "Sentiment", "Options flow"],
            plot_twists=plot_twists,
            predicted_ending=predicted_ending
        )
    
    def _predict_ending(self, arc: NarrativeArc, phase: MarketPhase, 
                       current_price: float, peak_price: float) -> str:
        """Predict narrative ending"""
        endings = {
            (NarrativeArc.RISE_FALL, MarketPhase.CLIMAX): "Crash imminent - sell now",
            (NarrativeArc.RISE_FALL, MarketPhase.FALLING_ACTION): "Decline continues - avoid",
            (NarrativeArc.UNDERDOG, MarketPhase.RISING_ACTION): "Victory ahead - hold",
            (NarrativeArc.REDEMPTION, MarketPhase.RISING_ACTION): "Redemption arc - buy",
            (NarrativeArc.TRAGEDY, MarketPhase.RESOLUTION): "Chapter closed - move on",
            (NarrativeArc.QUEST, MarketPhase.SETUP): "Adventure beginning - research",
            (NarrativeArc.QUEST, MarketPhase.RISING_ACTION): "Quest continues - hold"
        }
        
        return endings.get((arc, phase), "Unknown - watch closely")
    
    def get_trading_strategy(self, narrative: MarketNarrative) -> Dict:
        """Get trading strategy based on narrative"""
        pattern = self.patterns.get(narrative.arc, {})
        
        return {
            "symbol": narrative.symbol,
            "narrative_arc": narrative.arc.value,
            "current_phase": narrative.current_phase.value,
            "strategy": pattern.get("trade_strategy", "No strategy available"),
            "indicators_to_watch": pattern.get("indicators", []),
            "predicted_resolution": narrative.predicted_ending,
            "position_recommendation": self._position_from_narrative(narrative),
            "timeframe": self._timeframe_from_arc(narrative.arc)
        }
    
    def _position_from_narrative(self, narrative: MarketNarrative) -> str:
        """Generate position recommendation"""
        recommendations = {
            (NarrativeArc.RISE_FALL, MarketPhase.CLIMAX): "SHORT or PUTS",
            (NarrativeArc.RISE_FALL, MarketPhase.FALLING_ACTION): "AVOID or SHORT",
            (NarrativeArc.UNDERDOG, MarketPhase.RISING_ACTION): "LONG",
            (NarrativeArc.REDEMPTION, MarketPhase.RISING_ACTION): "LONG",
            (NarrativeArc.TRAGEDY, MarketPhase.RESOLUTION): "AVOID",
            (NarrativeArc.QUEST, MarketPhase.SETUP): "RESEARCH",
            (NarrativeArc.QUEST, MarketPhase.RISING_ACTION): "LONG"
        }
        
        return recommendations.get((narrative.arc, narrative.current_phase), "NEUTRAL")
    
    def _timeframe_from_arc(self, arc: NarrativeArc) -> str:
        """Estimate timeframe based on narrative type"""
        timeframes = {
            NarrativeArc.RISE_FALL: "1-4 weeks (fast collapse)",
            NarrativeArc.UNDERDOG: "3-12 months (gradual rise)",
            NarrativeArc.REDEMPTION: "6-18 months (recovery)",
            NarrativeArc.TRAGEDY: "1-6 months (collapse)",
            NarrativeArc.QUEST: "1-5 years (journey)"
        }
        return timeframes.get(arc, "Unknown")
    
    def compare_narratives(self, symbol1: str, symbol2: str, 
                          data1: List[Dict], data2: List[Dict]) -> Dict:
        """Compare narratives of two stocks"""
        n1 = self.analyze_stock_narrative(symbol1, data1, [])
        n2 = self.analyze_stock_narrative(symbol2, data2, [])
        
        return {
            "symbol_1": {
                "symbol": symbol1,
                "arc": n1.arc.value,
                "phase": n1.current_phase.value,
                "protagonist": n1.protagonist
            },
            "symbol_2": {
                "symbol": symbol2,
                "arc": n2.arc.value,
                "phase": n2.current_phase.value,
                "protagonist": n2.protagonist
            },
            "similarity": "Same arc" if n1.arc == n2.arc else "Different stories",
            "pair_trade_opportunity": self._check_pair_trade(n1, n2)
        }
    
    def _check_pair_trade(self, n1: MarketNarrative, n2: MarketNarrative) -> Dict:
        """Check for pair trade opportunity"""
        # Opposite arcs can be pair traded
        if (n1.arc == NarrativeArc.RISE_FALL and n2.arc == NarrativeArc.UNDERDOG) or \
           (n1.arc == NarrativeArc.UNDERDOG and n2.arc == NarrativeArc.RISE_FALL):
            return {
                "opportunity": True,
                "strategy": "Long underdog, Short peak",
                "confidence": "MEDIUM"
            }
        return {"opportunity": False}
    
    def get_narrative_alerts(self, watchlist: List[str], 
                            data_map: Dict[str, List[Dict]]) -> List[Dict]:
        """Get alerts for narrative changes"""
        alerts = []
        
        for symbol in watchlist:
            if symbol not in data_map:
                continue
            
            narrative = self.analyze_stock_narrative(symbol, data_map[symbol], [])
            
            # Alert on climax phases (actionable)
            if narrative.current_phase in [MarketPhase.CLIMAX, MarketPhase.RESOLUTION]:
                alerts.append({
                    "symbol": symbol,
                    "alert_type": f"NARRATIVE_{narrative.current_phase.value}",
                    "arc": narrative.arc.value,
                    "action": self._position_from_narrative(narrative),
                    "urgency": "HIGH" if narrative.current_phase == MarketPhase.CLIMAX else "MEDIUM"
                })
        
        return sorted(alerts, key=lambda x: x["urgency"], reverse=True)
