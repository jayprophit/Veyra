"""Logistics Tracker - Real-time tracking, route optimization, cost reduction"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

@dataclass
class Shipment:
    shipment_id: str; origin: str; destination: str
    cargo_type: str; quantity: Decimal
    transport_mode: str; carrier: str
    status: str; eta: datetime
    tracking_events: List[Dict]

class LogisticsTracker:
    """Global logistics tracking and optimization"""
    
    def __init__(self):
        self.active_shipments: Dict[str, Shipment] = {}
        self.route_costs = self._init_route_costs()
        
    def _init_route_costs(self):
        return {
            "air": {"cost_per_kg_km": Decimal("0.004"), "speed_kmh": 900, "co2_g_per_kg_km": 500},
            "sea": {"cost_per_kg_km": Decimal("0.0001"), "speed_kmh": 40, "co2_g_per_kg_km": 15},
            "rail": {"cost_per_kg_km": Decimal("0.0003"), "speed_kmh": 80, "co2_g_per_kg_km": 25},
            "truck": {"cost_per_kg_km": Decimal("0.0006"), "speed_kmh": 80, "co2_g_per_kg_km": 60},
            "drone": {"cost_per_kg_km": Decimal("0.005"), "speed_kmh": 100, "co2_g_per_kg_km": 0}
        }
    
    def create_shipment(self, origin: str, destination: str, 
                       cargo_type: str, weight_kg: Decimal,
                       transport_mode: str = "sea") -> Dict:
        """Create new shipment tracking"""
        shipment_id = f"SHP_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate distance (simplified)
        distances = {
            ("Shanghai", "Rotterdam"): 18000,
            ("Los Angeles", "Shanghai"): 11000,
            ("Dubai", "Singapore"): 5800,
            ("New York", "London"): 5500,
            ("Santos", "Hamburg"): 9500
        }
        
        distance_km = distances.get((origin, destination), 10000)
        
        # Calculate costs and time
        route_data = self.route_costs.get(transport_mode, self.route_costs["sea"])
        transport_cost = route_data["cost_per_kg_km"] * weight_kg * Decimal(distance_km)
        duration_hours = Decimal(distance_km) / Decimal(route_data["speed_kmh"])
        
        shipment = Shipment(
            shipment_id=shipment_id,
            origin=origin,
            destination=destination,
            cargo_type=cargo_type,
            quantity=weight_kg,
            transport_mode=transport_mode,
            carrier=f"Carrier_{transport_mode.upper()}",
            status="in_transit",
            eta=datetime.utcnow() + timedelta(hours=float(duration_hours)),
            tracking_events=[{
                "timestamp": datetime.utcnow().isoformat(),
                "location": origin,
                "status": "departed"
            }]
        )
        
        self.active_shipments[shipment_id] = shipment
        
        return {
            "success": True,
            "shipment_id": shipment_id,
            "origin": origin,
            "destination": destination,
            "cargo": cargo_type,
            "weight_kg": float(weight_kg),
            "transport_mode": transport_mode,
            "distance_km": distance_km,
            "transport_cost": float(transport_cost),
            "estimated_duration_hours": float(duration_hours),
            "eta": shipment.eta.isoformat(),
            "co2_emissions_kg": float(route_data["co2_g_per_kg_km"] * weight_kg * Decimal(distance_km) / 1000)
        }
    
    def get_shipment_status(self, shipment_id: str) -> Dict:
        """Get current shipment status"""
        if shipment_id not in self.active_shipments:
            return {"error": "Shipment not found"}
        
        shipment = self.active_shipments[shipment_id]
        
        return {
            "shipment_id": shipment_id,
            "status": shipment.status,
            "current_location": shipment.tracking_events[-1]["location"],
            "origin": shipment.origin,
            "destination": shipment.destination,
            "eta": shipment.eta.isoformat(),
            "progress_pct": 65,  # Mock progress
            "tracking_history": shipment.tracking_events
        }
    
    def optimize_route(self, origin: str, destination: str,
                      weight_kg: Decimal, priority: str = "cost") -> Dict:
        """Find optimal transport route"""
        distances = {
            ("Shanghai", "Rotterdam"): 18000,
            ("Los Angeles", "Shanghai"): 11000,
            ("Dubai", "Singapore"): 5800
        }
        
        distance_km = distances.get((origin, destination), 10000)
        
        options = []
        for mode, data in self.route_costs.items():
            cost = data["cost_per_kg_km"] * weight_kg * Decimal(distance_km)
            duration = Decimal(distance_km) / Decimal(data["speed_kmh"])
            co2 = data["co2_g_per_kg_km"] * weight_kg * Decimal(distance_km) / 1000
            
            # Score based on priority
            if priority == "cost":
                score = 1 / float(cost)
            elif priority == "speed":
                score = 1 / float(duration)
            else:  # eco
                score = 1 / float(co2)
            
            options.append({
                "mode": mode,
                "cost_usd": float(cost),
                "duration_hours": float(duration),
                "co2_emissions_kg": float(co2),
                "score": score
            })
        
        # Sort by score
        options.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "origin": origin,
            "destination": destination,
            "cargo_weight_kg": float(weight_kg),
            "priority": priority,
            "recommended_mode": options[0]["mode"],
            "all_options": options,
            "savings_vs_worst_pct": ((options[-1]["cost_usd"] - options[0]["cost_usd"]) / options[-1]["cost_usd"]) * 100
        }
    
    def get_active_shipments(self) -> List[Dict]:
        """Get all active shipments"""
        return [{"id": s.shipment_id, "from": s.origin, "to": s.destination,
                "cargo": s.cargo_type, "status": s.status, "eta": s.eta.isoformat()}
               for s in self.active_shipments.values()]
    
    def calculate_total_exposure(self) -> Dict:
        """Calculate total logistics exposure"""
        total_cargo_value = sum(s.quantity * Decimal("100") for s in self.active_shipments.values())
        
        by_mode = {}
        for s in self.active_shipments.values():
            mode = s.transport_mode
            by_mode[mode] = by_mode.get(mode, {"count": 0, "weight": 0})
            by_mode[mode]["count"] += 1
            by_mode[mode]["weight"] += float(s.quantity)
        
        return {
            "active_shipments": len(self.active_shipments),
            "total_cargo_weight_kg": sum(float(s.quantity) for s in self.active_shipments.values()),
            "estimated_cargo_value": float(total_cargo_value),
            "by_transport_mode": by_mode,
            "at_risk_exposure": float(total_cargo_value * Decimal("0.15"))  # 15% risk assumption
        }
