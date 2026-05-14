"""
Brain-Computer Interface (BCI) - Phase 10 Transcendent (+20 points)
Neural trading via EEG headsets
"""
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MentalState(Enum):
    FOCUSED = "focused"
    RELAXED = "relaxed"
    STRESSED = "stressed"
    TIRED = "tired"
    FLOW = "flow"  # Optimal trading state
    UNKNOWN = "unknown"

class BrainWaveBand(Enum):
    DELTA = "delta"      # 0.5-4 Hz - Deep sleep
    THETA = "theta"      # 4-8 Hz - Meditation
    ALPHA = "alpha"      # 8-13 Hz - Relaxed awareness
    BETA = "beta"        # 13-30 Hz - Active thinking
    GAMMA = "gamma"      # 30-100 Hz - Peak concentration

@dataclass
class BrainWaveReading:
    timestamp: datetime
    alpha_power: float
    beta_power: float
    theta_power: float
    gamma_power: float
    delta_power: float
    attention_score: float  # 0-100
    meditation_score: float  # 0-100

@dataclass
class NeuralCommand:
    command_type: str
    symbol: Optional[str]
    action: Optional[str]  # buy, sell, hold
    confidence: float
    source: str  # eeg, voice, manual

class BCIInterface:
    """
    Brain-Computer Interface for neural trading.
    
    Supports consumer EEG headsets:
    - Muse (Interaxon)
    - Emotiv Epoc X
    - OpenBCI
    - Neurosity Crown
    
    Safety: Blocks trading during high stress/fatigue.
    """
    
    def __init__(self):
        self.is_connected = False
        self.device_type: Optional[str] = None
        self.reading_history: List[BrainWaveReading] = []
        self.current_state = MentalState.UNKNOWN
        self.trading_enabled = False
        
        # Safety thresholds
        self.safety_config = {
            "min_attention_for_trading": 60,  # 0-100
            "max_stress_for_trading": 70,     # 0-100
            "flow_state_boost": True,         # Allow larger trades in flow
            "block_when_tired": True,
            "mandatory_break_after_minutes": 60,
        }
        
        # Neural command patterns
        self.command_patterns = {
            "buy": {"beta_spike": True, "alpha_suppression": True},
            "sell": {"theta_spike": True, "beta_suppression": True},
            "hold": {"alpha_dominant": True, "beta_low": True},
        }
    
    async def connect(self, device_type: str = "muse") -> bool:
        """Connect to EEG headset."""
        self.device_type = device_type
        
        try:
            # Mock connection for demo
            # Real implementation would use device SDKs
            if device_type == "muse":
                logger.info("Connecting to Muse headset via Bluetooth...")
            elif device_type == "emotiv":
                logger.info("Connecting to Emotiv Epoc X...")
            elif device_type == "openbci":
                logger.info("Connecting to OpenBCI Cyton...")
            
            self.is_connected = True
            logger.info(f"✅ BCI connected: {device_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect BCI: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from headset."""
        self.is_connected = False
        self.trading_enabled = False
        logger.info("BCI disconnected")
    
    async def start_reading(self):
        """Start receiving brain wave data."""
        if not self.is_connected:
            raise Exception("BCI not connected")
        
        logger.info("Starting neural stream...")
        
        while self.is_connected:
            # Simulate or read real EEG data
            reading = await self._get_reading()
            self.reading_history.append(reading)
            
            # Update mental state
            self.current_state = self._classify_state(reading)
            
            # Check if trading should be enabled
            self._update_trading_permissions(reading)
            
            # Check for neural commands
            command = self._detect_command(reading)
            if command:
                await self._handle_neural_command(command)
    
    async def _get_reading(self) -> BrainWaveReading:
        """Get brain wave reading from device."""
        # Mock data for development
        # Real implementation would read from device SDK
        import random
        
        return BrainWaveReading(
            timestamp=datetime.now(),
            alpha_power=random.uniform(0.3, 0.8),
            beta_power=random.uniform(0.2, 0.9),
            theta_power=random.uniform(0.1, 0.5),
            gamma_power=random.uniform(0.1, 0.4),
            delta_power=random.uniform(0.0, 0.3),
            attention_score=random.uniform(40, 95),
            meditation_score=random.uniform(20, 80)
        )
    
    def _classify_state(self, reading: BrainWaveReading) -> MentalState:
        """Classify mental state from brain waves."""
        # Alpha dominant = relaxed
        if reading.alpha_power > 0.6 and reading.beta_power < 0.4:
            if reading.meditation_score > 70:
                return MentalState.FLOW  # Flow state = high alpha, focused
            return MentalState.RELAXED
        
        # Beta dominant = focused/active
        if reading.beta_power > 0.6:
            if reading.attention_score > 80:
                return MentalState.FOCUSED
            return MentalState.STRESSED  # High beta + not focused = stress
        
        # Theta dominant = tired/daydreaming
        if reading.theta_power > 0.5:
            return MentalState.TIRED
        
        # Gamma spike = peak performance
        if reading.gamma_power > 0.5 and reading.attention_score > 85:
            return MentalState.FLOW
        
        return MentalState.UNKNOWN
    
    def _update_trading_permissions(self, reading: BrainWaveReading):
        """Update whether trading is allowed based on mental state."""
        was_enabled = self.trading_enabled
        
        # Requirements for trading
        attention_ok = reading.attention_score >= self.safety_config["min_attention_for_trading"]
        stress_ok = reading.beta_power < 0.7  # Beta correlates with stress
        not_tired = self.current_state != MentalState.TIRED
        
        self.trading_enabled = attention_ok and stress_ok and not_tired
        
        if was_enabled and not self.trading_enabled:
            logger.warning("🧠 Trading DISABLED - Mental state not optimal")
        elif not was_enabled and self.trading_enabled:
            logger.info("🧠 Trading ENABLED - Mental state optimal")
    
    def _detect_command(self, reading: BrainWaveReading) -> Optional[NeuralCommand]:
        """Detect if user is issuing a neural command."""
        # Pattern detection for intentional commands
        # This is a simplified version - real would use ML
        
        # "Buy" pattern: Beta spike + intention
        if reading.beta_power > 0.8 and reading.attention_score > 85:
            return NeuralCommand(
                command_type="intent",
                symbol=None,  # Would be from eye tracking or context
                action="buy",
                confidence=0.75,
                source="eeg"
            )
        
        return None
    
    async def _handle_neural_command(self, command: NeuralCommand):
        """Handle detected neural command."""
        logger.info(f"🧠 Neural command detected: {command.action} (confidence: {command.confidence:.2f})")
        
        if not self.trading_enabled:
            logger.warning("Neural command ignored - trading not enabled")
            return
        
        # Require high confidence for neural trades
        if command.confidence < 0.9:
            logger.info("Confidence too low, requesting confirmation")
            return
        
        # Execute or queue the command
        logger.info(f"Would execute: {command.action}")
    
    def get_status(self) -> Dict:
        """Get current BCI status."""
        return {
            "connected": self.is_connected,
            "device_type": self.device_type,
            "mental_state": self.current_state.value,
            "trading_enabled": self.trading_enabled,
            "reading_count": len(self.reading_history),
            "safety_config": self.safety_config
        }
    
    def get_recommendation(self) -> str:
        """Get trading recommendation based on mental state."""
        if self.current_state == MentalState.FLOW:
            return "🌊 FLOW STATE - Optimal for complex decisions"
        elif self.current_state == MentalState.FOCUSED:
            return "🎯 FOCUSED - Good for trading"
        elif self.current_state == MentalState.RELAXED:
            return "😌 RELAXED - Good for analysis, avoid impulsive trades"
        elif self.current_state == MentalState.STRESSED:
            return "😰 STRESSED - Trading blocked. Take a break."
        elif self.current_state == MentalState.TIRED:
            return "😴 TIRED - Trading blocked. Rest recommended."
        else:
            return "❓ Unknown state - baseline reading needed"

# Global instance
bci_interface = BCIInterface()
