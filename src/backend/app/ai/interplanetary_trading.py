"""
Interplanetary Trading Infrastructure - Phase 10 Transcendent (+15 points)
Mars delay compensation, space-based settlement, off-world markets
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class Location(Enum):
    EARTH = "earth"
    LUNAR_ORBIT = "lunar_orbit"
    MARS = "mars"
    MARS_ORBIT = "mars_orbit"
    ASTEROID_BELT = "asteroid_belt"
    SPACE_STATION = "space_station"

@dataclass
class DelayCalculation:
    from_location: Location
    to_location: Location
    one_way_delay_seconds: float
    round_trip_delay_seconds: float
    light_speed_distance_au: float

@dataclass
class OffWorldOrder:
    order_id: str
    symbol: str
    side: str
    quantity: int
    origin_location: Location
    destination_location: Location
    local_timestamp: datetime
    earth_timestamp: datetime
    expected_execution_earth_time: datetime
    quantum_entangled: bool  # Theoretical instant communication

class InterplanetaryTrading:
    """
    Trading infrastructure for off-world colonies.
    
    Handles light-speed delays between Earth, Moon, Mars, and beyond.
    Prepares for the coming space economy.
    
    Inspired by: The Expanse, SpaceX Mars colony plans
    """
    
    # Light speed delay from Earth (seconds)
    DELAY_TABLE = {
        Location.EARTH: 0,
        Location.LUNAR_ORBIT: 1.28,  # 1.28 seconds to Moon
        Location.MARS: 240,  # 4-24 minutes (varies by position)
        Location.MARS_ORBIT: 240,
        Location.ASTEROID_BELT: 1200,  # ~20 minutes
        Location.SPACE_STATION: 0.001,  # ISS ~400km
    }
    
    def __init__(self):
        self.active_locations: List[Location] = [Location.EARTH]
        self.local_order_books: Dict[Location, List[OffWorldOrder]] = {
            loc: [] for loc in Location
        }
        self.pending_sync_orders: List[OffWorldOrder] = []
        self.blockchain_settlement_enabled = True
    
    def calculate_delay(
        self,
        from_loc: Location,
        to_loc: Location
    ) -> DelayCalculation:
        """Calculate light-speed delay between locations."""
        delay_from = self.DELAY_TABLE[from_loc]
        delay_to = self.DELAY_TABLE[to_loc]
        
        # Rough approximation - actual varies by orbital positions
        one_way = abs(delay_to - delay_from)
        
        # Distance in AU (Earth to Sun = 1 AU)
        au_distance = one_way / 500  # Very rough conversion
        
        return DelayCalculation(
            from_location=from_loc,
            to_location=to_loc,
            one_way_delay_seconds=one_way,
            round_trip_delay_seconds=one_way * 2,
            light_speed_distance_au=au_distance
        )
    
    def place_offworld_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        origin: Location,
        destination: Location
    ) -> OffWorldOrder:
        """
        Place an order from an off-world location.
        
        Accounts for light-speed delays in execution.
        """
        delay_calc = self.calculate_delay(origin, Location.EARTH)
        
        now_earth = datetime.utcnow()
        now_local = now_earth  # Would adjust for local timekeeping
        
        # Orders execute after round-trip delay
        execution_time = now_earth + timedelta(
            seconds=delay_calc.round_trip_delay_seconds
        )
        
        order = OffWorldOrder(
            order_id=f"OFFWORLD_{origin.value}_{now_earth.timestamp()}",
            symbol=symbol,
            side=side,
            quantity=quantity,
            origin_location=origin,
            destination_location=destination,
            local_timestamp=now_local,
            earth_timestamp=now_earth,
            expected_execution_earth_time=execution_time,
            quantum_entangled=False  # Future feature
        )
        
        self.local_order_books[origin].append(order)
        
        logger.info(
            f"🚀 Off-world order placed: {side} {quantity} {symbol} "
            f"from {origin.value} (delay: {delay_calc.round_trip_delay_seconds:.1f}s)"
        )
        
        return order
    
    def get_local_order_book(self, location: Location) -> List[Dict]:
        """Get the local order book for a specific location."""
        orders = self.local_order_books[location]
        return [{
            "order_id": o.order_id,
            "symbol": o.symbol,
            "side": o.side,
            "quantity": o.quantity,
            "earth_time": o.earth_timestamp.isoformat(),
            "execution_time": o.expected_execution_earth_time.isoformat(),
            "delay_seconds": (o.expected_execution_earth_time - o.earth_timestamp).total_seconds()
        } for o in orders]
    
    def simulate_mars_trading(self, symbol: str, side: str, quantity: int) -> Dict:
        """
        Simulate placing a trade from Mars.
        
        Mars is 4-24 minutes away at light speed.
        """
        order = self.place_offworld_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            origin=Location.MARS,
            destination=Location.EARTH
        )
        
        delay = self.calculate_delay(Location.MARS, Location.EARTH)
        
        return {
            "status": "pending_light_speed",
            "order_id": order.order_id,
            "location": "Mars Colony Alpha",
            "earth_execution_time": order.expected_execution_earth_time.isoformat(),
            "delay_minutes": delay.round_trip_delay_seconds / 60,
            "message": f"Order will execute on Earth in {delay.round_trip_delay_seconds/60:.1f} minutes",
            "local_order_book_size": len(self.local_order_books[Location.MARS]),
            "blockchain_settlement": self.blockchain_settlement_enabled
        }
    
    def get_offworld_market_status(self) -> Dict:
        """Get status of all off-world trading locations."""
        return {
            "active_locations": [loc.value for loc in self.active_locations],
            "location_status": {
                loc.value: {
                    "delay_from_earth_seconds": self.DELAY_TABLE[loc],
                    "local_orders_pending": len(self.local_order_books[loc]),
                    "operational": loc in self.active_locations
                }
                for loc in Location
            },
            "earth_sync_status": "real_time",
            "mars_sync_status": "4_24_minute_delay",
            "quantum_entanglement_ready": False,  # Future technology
            "space_weather_status": self._get_space_weather()
        }
    
    def _get_space_weather(self) -> Dict:
        """Get current space weather conditions affecting communication."""
        # Solar flares, radiation storms can affect Earth-Mars comms
        return {
            "solar_flare_activity": "low",
            "radiation_storm_level": 0,
            "coronal_mass_ejection": False,
            "communication_impact": "none"
        }
    
    def create_asteroid_mining_etf_proposal(self) -> Dict:
        """
        Propose an ETF tracking asteroid mining companies.
        
        The future of space resource extraction.
        """
        companies = [
            "Planetary Resources (fictional)",
            "Deep Space Industries (fictional)",
            "SpaceX (Starlink funding)",
            "Blue Origin (lunar resources)",
            "NASA contractors"
        ]
        
        return {
            "etf_name": "COSMIC.MINERS",
            "description": "Asteroid Mining and Space Resources ETF",
            "tracking_companies": companies,
            "expense_ratio": 0.75,  # Higher for frontier tech
            "risk_level": "extreme",
            "projected_launch": "2035",
            "investment_thesis": "First trillionaires will be asteroid miners"
        }

# Global instance
interplanetary_trading = InterplanetaryTrading()
