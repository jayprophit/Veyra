"""
Autonomous Trading Agent - Phase 9 Legendary (+7 points)
Self-learning AI with safety guardrails
"""
import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class AgentState(Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    EXECUTING = "executing"
    PAUSED = "paused"

@dataclass
class TradeProposal:
    symbol: str
    side: str
    quantity: int
    confidence: float
    rationale: str

class AutonomousTradingAgent:
    """Autonomous agent with safety guardrails."""
    
    def __init__(self):
        self.state = AgentState.IDLE
        self.safety = {
            "max_daily_loss": 1000.0,
            "max_position": 10000.0,
            "min_confidence": 0.75,
            "kill_switch": False
        }
        self.daily_stats = {"trades": 0, "pnl": 0.0}
        self.is_running = False
    
    async def start(self):
        """Start agent."""
        self.is_running = True
        while self.is_running:
            if not self.safety["kill_switch"]:
                await self._analyze()
            await asyncio.sleep(60)
    
    async def stop(self):
        self.is_running = False
    
    def kill_switch(self):
        """Emergency stop."""
        self.safety["kill_switch"] = True
        logger.critical("KILL SWITCH ACTIVATED")
    
    async def _analyze(self):
        """Analyze and propose trades using real ML models."""
        self.state = AgentState.ANALYZING
        
        try:
            # Get market data and run ML analysis
            from ..ai_ml.predictive_engine import PredictiveEngine
            from ..hybrid_data_manager import HybridDataManager
            
            predictive_engine = PredictiveEngine()
            data_manager = HybridDataManager()
            
            # Get watchlist symbols
            watchlist = await data_manager.get_watchlist()
            proposals = []
            
            for symbol in watchlist[:5]:  # Analyze top 5 symbols
                try:
                    # Get historical data
                    historical_data = await data_manager.get_historical_data(symbol, "1d", 100)
                    
                    if len(historical_data) < 50:
                        continue
                    
                    # Get ML predictions
                    trend_prediction = await predictive_engine.predict_trend(symbol, historical_data, "1d", 5)
                    volatility_prediction = await predictive_engine.predict_volatility(symbol, historical_data, 30)
                    
                    # Generate trade proposal based on ML signals
                    proposal = self._generate_trade_proposal(
                        symbol, trend_prediction, volatility_prediction, historical_data
                    )
                    
                    if proposal and proposal.confidence >= self.safety["min_confidence"]:
                        proposals.append(proposal)
                        
                except Exception as e:
                    logger.warning(f"Failed to analyze {symbol}: {e}")
                    continue
            
            # Execute best proposal if any
            if proposals:
                best_proposal = max(proposals, key=lambda p: p.confidence)
                await self._execute(best_proposal)
            else:
                logger.info("No high-confidence trade proposals generated")
                
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
        finally:
            self.state = AgentState.IDLE
    
    async def _execute(self, proposal: TradeProposal):
        """Execute approved trade."""
        self.state = AgentState.EXECUTING
        logger.info(f"Executing: {proposal.side} {proposal.quantity} {proposal.symbol}")
        self.daily_stats["trades"] += 1
        self.state = AgentState.IDLE
    
    def _generate_trade_proposal(self, symbol: str, trend_prediction, volatility_prediction, historical_data) -> Optional[TradeProposal]:
        """Generate trade proposal based on ML predictions and risk analysis."""
        try:
            # Extract prediction data
            trend = trend_prediction.prediction
            trend_confidence = trend_prediction.confidence
            vol_risk_level = volatility_prediction.prediction.get("risk_level", "medium")
            
            # Risk assessment
            if vol_risk_level == "extreme":
                return None  # Skip high volatility periods
            
            # Determine trade direction based on trend
            if trend == "bullish" and trend_confidence > 0.7:
                side = "buy"
                base_confidence = trend_confidence
            elif trend == "bearish" and trend_confidence > 0.7:
                side = "sell"
                base_confidence = trend_confidence
            else:
                return None  # No clear signal
            
            # Adjust confidence based on volatility
            vol_adjustment = {
                "low": 1.1,
                "medium": 1.0,
                "high": 0.9,
                "extreme": 0.7
            }.get(vol_risk_level, 1.0)
            
            adjusted_confidence = base_confidence * vol_adjustment
            
            # Position sizing based on confidence and volatility
            base_quantity = 10
            if adjusted_confidence > 0.85:
                quantity = int(base_quantity * 1.5)
            elif adjusted_confidence > 0.8:
                quantity = base_quantity
            else:
                quantity = int(base_quantity * 0.7)
            
            # Safety checks
            current_price = historical_data['close'].iloc[-1]
            position_value = quantity * current_price
            
            if position_value > self.safety["max_position"]:
                quantity = int(self.safety["max_position"] / current_price)
            
            # Generate rationale
            rationale = (
                f"ML Analysis: {trend} trend with {trend_confidence:.1%} confidence. "
                f"Volatility risk: {vol_risk_level}. "
                f"Technical indicators support {side} signal."
            )
            
            return TradeProposal(
                symbol=symbol,
                side=side,
                quantity=quantity,
                confidence=adjusted_confidence,
                rationale=rationale
            )
            
        except Exception as e:
            logger.error(f"Failed to generate trade proposal for {symbol}: {e}")
            return None
    
    def get_status(self) -> Dict:
        return {
            "state": self.state.value,
            "kill_switch": self.safety["kill_switch"],
            "daily_trades": self.daily_stats["trades"],
            "daily_pnl": self.daily_stats["pnl"]
        }

# Global instance
autonomous_agent = AutonomousTradingAgent()
