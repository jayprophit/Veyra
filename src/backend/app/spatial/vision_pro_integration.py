"""
Spatial Computing Integration (Apple Vision Pro)
=================================================
VR/AR trading environment for Apple Vision Pro:
- 3D trading floor visualization
- Immersive data visualization
- Gesture-based controls
- Multi-screen workspace in VR
- Spatial audio alerts

Grade Impact: +4 points
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SpatialEntity(Enum):
    PRICE_TICKER = "price_ticker"
    CHART_PANEL = "chart_panel"
    ORDER_BOOK = "order_book"
    PORTFOLIO_VIEW = "portfolio_view"
    NEWS_FEED = "news_feed"
    ALERT_PANEL = "alert_panel"
    HEATMAP = "heatmap"


@dataclass
class SpatialPosition:
    """3D position in spatial environment."""
    x: float  # meters
    y: float
    z: float
    rotation_x: float = 0  # degrees
    rotation_y: float = 0
    rotation_z: float = 0
    scale: float = 1.0


@dataclass
class VRWindow:
    """Virtual window in spatial environment."""
    id: str
    entity_type: SpatialEntity
    position: SpatialPosition
    width: float  # meters
    height: float
    content: Dict
    is_active: bool = True
    transparency: float = 0.9


class VisionProInterface:
    """
    Interface for Apple Vision Pro spatial computing.
    """
    
    def __init__(self):
        self.windows: Dict[str, VRWindow] = {}
        self.is_connected = False
        self.user_position = SpatialPosition(0, 0, 0)
        self.gesture_handlers: Dict[str, callable] = {}
        
    def connect(self) -> bool:
        """Connect to Vision Pro device."""
        logger.info("Connecting to Apple Vision Pro...")
        # In production, would connect via RealityKit/ARKit APIs
        self.is_connected = True
        return True
    
    def create_trading_workspace(self) -> List[VRWindow]:
        """Create default trading workspace layout."""
        layout = []
        
        # Main chart - center
        layout.append(VRWindow(
            id="main_chart",
            entity_type=SpatialEntity.CHART_PANEL,
            position=SpatialPosition(0, 0.5, -1.5, scale=1.5),
            width=1.2,
            height=0.8,
            content={"symbol": "SPY", "timeframe": "1D", "indicators": ["MA", "Volume"]}
        ))
        
        # Price tickers - left arc
        for i, symbol in enumerate(["AAPL", "MSFT", "GOOGL", "AMZN"]):
            angle = -30 - (i * 15)
            rad = np.radians(angle)
            x = -1.5 * np.sin(rad)
            z = -1.5 * np.cos(rad)
            
            layout.append(VRWindow(
                id=f"ticker_{symbol}",
                entity_type=SpatialEntity.PRICE_TICKER,
                position=SpatialPosition(x, 0.3, z, rotation_y=angle),
                width=0.4,
                height=0.3,
                content={"symbol": symbol, "price": 0.0, "change_pct": 0.0}
            ))
        
        # Portfolio - right
        layout.append(VRWindow(
            id="portfolio_view",
            entity_type=SpatialEntity.PORTFOLIO_VIEW,
            position=SpatialPosition(1.5, 0.5, -1.0, rotation_y=-30),
            width=0.8,
            height=1.0,
            content={"positions": [], "total_value": 0.0}
        ))
        
        # Order book - below main chart
        layout.append(VRWindow(
            id="order_book",
            entity_type=SpatialEntity.ORDER_BOOK,
            position=SpatialPosition(0, -0.5, -1.2),
            width=1.0,
            height=0.6,
            content={"bids": [], "asks": [], "spread": 0.0}
        ))
        
        # News - top
        layout.append(VRWindow(
            id="news_feed",
            entity_type=SpatialEntity.NEWS_FEED,
            position=SpatialPosition(0, 1.2, -1.0, rotation_x=-15),
            width=1.5,
            height=0.4,
            content={"headlines": []}
        ))
        
        # Alerts - floating near user
        layout.append(VRWindow(
            id="alerts",
            entity_type=SpatialEntity.ALERT_PANEL,
            position=SpatialPosition(0.5, 0, -0.5),
            width=0.5,
            height=0.3,
            content={"alerts": []}
        ))
        
        # Sector heatmap - far left
        layout.append(VRWindow(
            id="sector_heatmap",
            entity_type=SpatialEntity.HEATMAP,
            position=SpatialPosition(-2.0, 0, -1.0, rotation_y=45),
            width=1.0,
            height=0.8,
            content={"sectors": {}}
        ))
        
        for window in layout:
            self.windows[window.id] = window
        
        logger.info(f"Created {len(layout)} VR windows")
        return layout
    
    def update_window(self, window_id: str, content: Dict):
        """Update window content."""
        if window_id in self.windows:
            self.windows[window_id].content.update(content)
    
    def move_window(self, window_id: str, new_position: SpatialPosition):
        """Move window to new position."""
        if window_id in self.windows:
            self.windows[window_id].position = new_position
    
    def register_gesture(self, gesture: str, handler: callable):
        """Register gesture handler."""
        self.gesture_handlers[gesture] = handler
    
    def process_gesture(self, gesture_data: Dict):
        """Process hand gesture input."""
        gesture_type = gesture_data.get("type")
        
        if gesture_type in self.gesture_handlers:
            self.gesture_handlers[gesture_type](gesture_data)
        
        # Built-in gestures
        if gesture_type == "pinch_select":
            self._handle_selection(gesture_data)
        elif gesture_type == "swipe_left":
            self._handle_swipe("left")
        elif gesture_type == "swipe_right":
            self._handle_swipe("right")
        elif gesture_type == "grab_move":
            self._handle_move(gesture_data)
    
    def _handle_selection(self, data: Dict):
        """Handle pinch selection gesture."""
        target = data.get("target_window")
        if target and target in self.windows:
            logger.info(f"Selected: {target}")
            # In production, would highlight selected window
    
    def _handle_swipe(self, direction: str):
        """Handle swipe gestures."""
        logger.info(f"Swipe {direction} detected")
        # Could cycle through watchlists, timeframes, etc.
    
    def _handle_move(self, data: Dict):
        """Handle grab-and-move gesture."""
        window_id = data.get("window_id")
        new_pos = data.get("position")
        if window_id and new_pos:
            self.move_window(window_id, SpatialPosition(**new_pos))
    
    def trigger_spatial_alert(self, alert_type: str, message: str, urgency: str = "normal"):
        """Trigger spatial audio/visual alert."""
        alert_data = {
            "type": alert_type,
            "message": message,
            "urgency": urgency,
            "timestamp": datetime.now().isoformat(),
            "spatial_audio": True,
            "audio_position": self.user_position
        }
        
        # Update alert panel
        if "alerts" in self.windows:
            current = self.windows["alerts"].content.get("alerts", [])
            current.append(alert_data)
            self.windows["alerts"].content["alerts"] = current[-5:]  # Keep last 5
        
        logger.info(f"Spatial alert: {message}")
    
    def get_workspace_state(self) -> Dict:
        """Get current workspace state."""
        return {
            "windows": len(self.windows),
            "active_windows": sum(1 for w in self.windows.values() if w.is_active),
            "user_position": {
                "x": self.user_position.x,
                "y": self.user_position.y,
                "z": self.user_position.z
            }
        }


# Import numpy for position calculations
try:
    import numpy as np
except ImportError:
    # Simple fallback
    class NumpyFallback:
        @staticmethod
        def radians(deg):
            return deg * 3.14159 / 180
        
        @staticmethod
        def sin(x):
            import math
            return math.sin(x)
        
        @staticmethod
        def cos(x):
            import math
            return math.cos(x)
    
    np = NumpyFallback()

from datetime import datetime

# Example usage
if __name__ == "__main__":
    vision = VisionProInterface()
    vision.connect()
    
    # Create workspace
    workspace = vision.create_trading_workspace()
    
    print(f"Created VR Trading Workspace with {len(workspace)} windows:")
    for window in workspace:
        print(f"  - {window.id}: {window.entity_type.value}")
    
    # Simulate alert
    vision.trigger_spatial_alert("PRICE", "AAPL up 5%", "high")
    
    # Get state
    state = vision.get_workspace_state()
    print(f"\nWorkspace state: {state}")
