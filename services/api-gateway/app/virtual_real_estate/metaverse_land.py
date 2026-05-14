"""Metaverse Land - Virtual property valuation"""
from typing import Dict

class MetaverseLand:
    """Value metaverse land parcels"""
    
    METAVERSES = {
        "decentraland": {"floor_price": 3000, "daily_users": 8000},
        "sandbox": {"floor_price": 2500, "daily_users": 12000},
        "otherside": {"floor_price": 5000, "daily_users": 5000}
    }
    
    def value_parcel(self, metaverse: str, coords: tuple, size: int) -> Dict:
        """Value a land parcel"""
        data = self.METAVERSES.get(metaverse.lower(), {"floor_price": 1000})
        value = data["floor_price"] * size
        
        # Distance from center premium
        dist = (coords[0]**2 + coords[1]**2) ** 0.5
        if dist < 10:
            value *= 3
        elif dist < 50:
            value *= 1.5
        
        return {
            "metaverse": metaverse,
            "coordinates": coords,
            "size": size,
            "estimated_value": value,
            "currency": "USD"
        }
