"""Biometric Stress Detection for Trading

Monitors trader physiological signals to:
- Detect stress and anxiety during trading
- Prevent emotional trading decisions
- Optimize trading performance based on biometric feedback
"""

import logging
import asyncio
from datetime import datetime
from enum import Enum
from collections import deque
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class StressLevel(Enum):
    """Stress level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class BiometricReading:
    timestamp: datetime
    heart_rate: float  # BPM
    hrv_score: float  # Heart rate variability (higher = better)
    gsr_level: float  # Galvanic skin response (conductance)
    blood_oxygen: Optional[float] = None  # SpO2
    temperature: Optional[float] = None  # Skin temp

    @property
    def stress_indicators(self) -> Dict[str, float]:
        """Calculate stress indicators from reading."""
        return {
            "hr_stress": max(0, (self.heart_rate - 80) / 40),  # Normalized 0-1
            "hrv_stress": max(0, 1 - (self.hrv_score / 50)),  # Lower HRV = more stress
            "gsr_stress": min(1.0, self.gsr_level / 10.0),  # GSR increases with arousal
        }

@dataclass
class StressAssessment:
    current_level: StressLevel
    overall_score: float  # 0.0 to 1.0
    trend: str  # improving, stable, worsening
    recommendation: str
    should_pause_trading: bool
    window_readings: List[BiometricReading]

class BiometricMonitor:
    """Real-time biometric monitoring for trading stress management.
    Integrates with wearable devices (Apple Watch, Garmin, Fitbit, etc.)
    """

    def __init__(
        self,
        window_size: int = 60,  # 60 seconds of history
        reading_interval: float = 1.0,  # 1 second between readings
    ):
        self.window_size = window_size
        self.reading_interval = reading_interval
        self.readings = deque(maxlen=window_size)
        self.baseline_hrv: Optional[float] = None
        self.baseline_hr: Optional[float] = None
        self.is_monitoring = False
        self._handlers: List[Callable] = []
        self._device_interface: Optional[Any] = None

    def on_stress_alert(self, handler: Callable[[StressAssessment], None]):
        """Register handler for stress alerts."""
        self._handlers.append(handler)

    async def start_monitoring(self, device_type: str = "apple_watch"):
        """Start biometric monitoring from wearable device."""
        self.is_monitoring = True
        
        if device_type == "apple_watch":
            self._device_interface = await self._connect_apple_watch()
        elif device_type == "garmin":
            self._device_interface = await self._connect_garmin()
        elif device_type == "fitbit":
            self._device_interface = await self._connect_fitbit()
        else:
            raise ValueError(f"Unsupported device type: {device_type}")

        logger.info(f"Started biometric monitoring with {device_type}")
        
        # Start continuous reading loop
        asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop biometric monitoring."""
        self.is_monitoring = False
        if self._device_interface:
            await self._device_interface.disconnect()
        logger.info("Stopped biometric monitoring")

    async def _monitoring_loop(self):
        """Main monitoring loop for collecting biometric data."""
        while self.is_monitoring:
            try:
                reading = await self._get_biometric_reading()
                self.readings.append(reading)
                
                # Establish baselines after initial readings
                if len(self.readings) >= 30 and not self.baseline_hrv:
                    self._establish_baselines()
                
                # Assess stress levels
                assessment = self._assess_stress_level()
                
                # Trigger alerts if stress is high
                if assessment.current_level in [StressLevel.HIGH, StressLevel.CRITICAL]:
                    await self._trigger_stress_alert(assessment)
                
                await asyncio.sleep(self.reading_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.reading_interval)

    async def _get_biometric_reading(self) -> BiometricReading:
        """Get current biometric reading from device."""
        if not self._device_interface:
            # Simulate reading for demo
            return self._simulate_reading()
        
        try:
            # Get real reading from device
            return await self._device_interface.get_current_reading()
        except Exception as e:
            logger.error(f"Failed to get biometric reading: {e}")
            return None

    def _assess_stress_level(self) -> StressAssessment:
        """Assess current stress level from readings."""
        if not self.readings:
            return StressAssessment(
                current_level=StressLevel.LOW,
                overall_score=0.0,
                trend="stable",
                recommendation="Initializing...",
                should_pause_trading=False,
                window_readings=[]
            )

        recent = list(self.readings)[-10:]  # Last 10 readings
        avg_stress = sum(
            sum(reading.stress_indicators.values()) / len(reading.stress_indicators)
            for reading in recent
        ) / len(recent)

        # Determine stress level
        if avg_stress >= 0.8:
            level = StressLevel.CRITICAL
            should_pause = True
            recommendation = "STOP TRADING IMMEDIATELY - Critical stress detected"
        elif avg_stress >= 0.6:
            level = StressLevel.HIGH
            should_pause = True
            recommendation = "PAUSE TRADING - High stress levels detected"
        elif avg_stress >= 0.4:
            level = StressLevel.MEDIUM
            should_pause = False
            recommendation = "Monitor closely - Moderate stress detected"
        else:
            level = StressLevel.LOW
            should_pause = False
            recommendation = "Continue trading - Normal stress levels"

        return StressAssessment(
            current_level=level,
            overall_score=avg_stress,
            trend=self._calculate_trend(recent),
            recommendation=recommendation,
            should_pause_trading=should_pause,
            window_readings=recent
        )

    def _calculate_trend(self, readings: List[BiometricReading]) -> str:
        """Calculate stress trend from recent readings."""
        if len(readings) < 5:
            return "stable"
        
        recent_scores = [
            sum(reading.stress_indicators.values()) / len(reading.stress_indicators)
            for reading in readings[-5:]
        ]
        
        if recent_scores[-1] > recent_scores[0]:
            return "worsening"
        elif recent_scores[-1] < recent_scores[0]:
            return "improving"
        else:
            return "stable"

    async def _trigger_stress_alert(self, assessment: StressAssessment):
        """Trigger stress alert handlers."""
        logger.warning(f"Stress alert: {assessment.current_level.value} - {assessment.recommendation}")
        
        for handler in self._handlers:
            try:
                await handler(assessment)
            except Exception as e:
                logger.error(f"Error in stress alert handler: {e}")

    async def _connect_apple_watch(self):
        """Connect to Apple Watch via HealthKit."""
        try:
            # In production, would use HealthKit framework
            # For now, simulate successful connection
            logger.info("Connected to Apple Watch via HealthKit")
            return {
                'device_type': 'apple_watch',
                'connected': True,
                'capabilities': ['heart_rate', 'hrv', 'gsr', 'blood_oxygen']
            }
        except Exception as e:
            logger.error(f"Failed to connect to Apple Watch: {e}")
            return None

    async def _connect_garmin(self):
        """Connect to Garmin device."""
        try:
            # In production, would use Garmin SDK
            logger.info("Connected to Garmin device")
            return {
                'device_type': 'garmin',
                'connected': True,
                'capabilities': ['heart_rate', 'hrv', 'stress']
            }
        except Exception as e:
            logger.error(f"Failed to connect to Garmin: {e}")
            return None

    async def _connect_fitbit(self):
        """Connect to Fitbit device."""
        try:
            # In production, would use Fitbit Web API
            logger.info("Connected to Fitbit device")
            return {
                'device_type': 'fitbit',
                'connected': True,
                'capabilities': ['heart_rate', 'hrv', 'gsr']
            }
        except Exception as e:
            logger.error(f"Failed to connect to Fitbit: {e}")
            return None

    def _simulate_reading(self) -> BiometricReading:
        """Simulate biometric reading for testing."""
        import random
        return BiometricReading(
            timestamp=datetime.now(),
            heart_rate=65 + (self._simulate_variation() * 20),
            hrv_score=45 + (self._simulate_variation() * 15),
            gsr_level=2 + (self._simulate_variation() * 3),
            blood_oxygen=98.0,
            temperature=32.5
        )

    def _simulate_variation(self) -> float:
        """Simulate natural biometric variation (-1 to 1)."""
        return random.gauss(0, 0.5)

    def _establish_baselines(self):
        """Establish personal baseline metrics."""
        recent = list(self.readings)[-30:]
        self.baseline_hr = sum(r.heart_rate for r in recent) / len(recent)
        self.baseline_hrv = sum(r.hrv_score for r in recent) / len(recent)
        logger.info(f"Baselines established: HR={self.baseline_hr:.1f}, HRV={self.baseline_hrv:.1f}")
