"""Energy Markets - Power, oil, gas, renewables trading"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class EnergyType(Enum):
    ELECTRICITY = "electricity"; CRUDE_OIL = "crude_oil"
    NATURAL_GAS = "natural_gas"; COAL = "coal"
    URANIUM = "uranium"; SOLAR = "solar"
    WIND = "wind"; HYDRO = "hydro"
    BIOFUEL = "biofuel"; HYDROGEN = "hydrogen"

@dataclass
class EnergyContract:
    contract_id: str; energy_type: EnergyType
    quantity_mwh: Decimal; price_per_mwh: Decimal
    delivery_start: datetime; delivery_end: datetime
    grid_zone: str; counterparty: str
    contract_value: Decimal = Decimal("0")

class EnergyMarkets:
    """Electricity and energy commodity trading"""
    
    def __init__(self):
        self.positions: Dict[str, EnergyContract] = {}
        self.grid_zones = self._init_grid_zones()
        
    def _init_grid_zones(self):
        return {
            "DE_NORTH": {"country": "Germany", "peak_demand_mw": 18000, "avg_price": Decimal("85")},
            "DE_SOUTH": {"country": "Germany", "peak_demand_mw": 22000, "avg_price": Decimal("95")},
            "UK_LONDON": {"country": "UK", "peak_demand_mw": 10000, "avg_price": Decimal("120")},
            "US_ERCOT": {"country": "USA", "peak_demand_mw": 78000, "avg_price": Decimal("45")},
            "US_PJM": {"country": "USA", "peak_demand_mw": 150000, "avg_price": Decimal("52")},
            "FR_PARIS": {"country": "France", "peak_demand_mw": 6500, "avg_price": Decimal("78")},
            "JP_TOKYO": {"country": "Japan", "peak_demand_mw": 60000, "avg_price": Decimal("135")},
            "AU_NEM": {"country": "Australia", "peak_demand_mw": 35000, "avg_price": Decimal("62")}
        }
    
    def get_grid_price(self, zone: str, hour: int = 12) -> Decimal:
        """Get electricity price for grid zone"""
        if zone not in self.grid_zones:
            return Decimal("100")
        
        base = self.grid_zones[zone]["avg_price"]
        
        # Time of day adjustment
        peak_hours = [17, 18, 19, 20]
        off_peak = [2, 3, 4, 5, 6]
        
        if hour in peak_hours:
            return base * Decimal("1.5")
        elif hour in off_peak:
            return base * Decimal("0.6")
        return base
    
    def find_spread_opportunities(self) -> List[Dict]:
        """Find grid price arbitrage opportunities"""
        opportunities = []
        
        zones = list(self.grid_zones.keys())
        for i, zone_a in enumerate(zones):
            for zone_b in zones[i+1:]:
                price_a = self.get_grid_price(zone_a)
                price_b = self.get_grid_price(zone_b)
                
                spread = abs(price_a - price_b)
                avg_price = (price_a + price_b) / 2
                spread_pct = (spread / avg_price) * 100
                
                if spread_pct > 15:  # 15% spread threshold
                    opportunities.append({
                        "buy_zone": zone_a if price_a < price_b else zone_b,
                        "sell_zone": zone_b if price_a < price_b else zone_a,
                        "buy_price": float(min(price_a, price_b)),
                        "sell_price": float(max(price_a, price_b)),
                        "spread_usd_mwh": float(spread),
                        "spread_pct": float(spread_pct),
                        "transmission_loss_pct": 8,
                        "net_profit_mwh": float(spread * Decimal("0.92")),
                        "strategy": "buy_low_sell_high"
                    })
        
        return sorted(opportunities, key=lambda x: x["spread_pct"], reverse=True)
    
    def trade_power(self, buy_zone: str, sell_zone: str, 
                   quantity_mwh: Decimal, duration_hours: int = 1) -> Dict:
        """Execute power arbitrage trade"""
        buy_price = self.get_grid_price(buy_zone)
        sell_price = self.get_grid_price(sell_zone)
        
        transmission_loss = Decimal("0.08")  # 8% loss
        effective_quantity = quantity_mwh * (Decimal("1") - transmission_loss)
        
        cost = buy_price * quantity_mwh
        revenue = sell_price * effective_quantity
        profit = revenue - cost
        
        contract_id = f"PWR_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "success": True, "contract_id": contract_id,
            "buy_zone": buy_zone, "sell_zone": sell_zone,
            "quantity_mwh": float(quantity_mwh),
            "effective_quantity_mwh": float(effective_quantity),
            "buy_price": float(buy_price), "sell_price": float(sell_price),
            "cost_usd": float(cost), "revenue_usd": float(revenue),
            "profit_usd": float(profit), "profit_margin_pct": float((profit/cost)*100)
        }
    
    def get_renewables_opportunities(self) -> List[Dict]:
        """Find renewable energy trading opportunities"""
        return [
            {
                "type": "solar_farm_flip",
                "location": "Texas, USA",
                "capacity_mw": 450,
                "purchase_price_m": 180,
                "projected_sale_price_m": 250,
                "hold_period_years": 3,
                "annual_cash_flow_m": 22,
                "irr_pct": 28
            },
            {
                "type": "wind_portfolio",
                "location": "Scotland, UK",
                "capacity_mw": 800,
                "purchase_price_m": 320,
                "projected_sale_price_m": 480,
                "hold_period_years": 5,
                "annual_cash_flow_m": 45,
                "irr_pct": 22
            },
            {
                "type": "hydro_project",
                "location": "Norway",
                "capacity_mw": 200,
                "purchase_price_m": 150,
                "projected_sale_price_m": 200,
                "hold_period_years": 4,
                "annual_cash_flow_m": 18,
                "irr_pct": 18
            }
        ]
    
    def calculate_capacity_value(self, zone: str, capacity_mw: int) -> Dict:
        """Calculate value of generation capacity in a zone"""
        if zone not in self.grid_zones:
            return {"error": "Unknown zone"}
        
        zone_data = self.grid_zones[zone]
        avg_price = zone_data["avg_price"]
        
        # Annual generation (assuming 85% capacity factor)
        annual_mwh = capacity_mw * 8760 * 0.85
        
        # Revenue at average price
        annual_revenue = Decimal(annual_mwh) * avg_price
        
        # Capacity payment (availability payment)
        capacity_payment = Decimal(capacity_mw) * Decimal("50000")  # $50k/MW/year
        
        total_annual = annual_revenue + capacity_payment
        
        # Asset value (8x annual revenue typical)
        asset_value = total_annual * Decimal("8")
        
        return {
            "zone": zone, "capacity_mw": capacity_mw,
            "annual_generation_mwh": annual_mwh,
            "avg_price_per_mwh": float(avg_price),
            "annual_energy_revenue": float(annual_revenue),
            "annual_capacity_payment": float(capacity_payment),
            "total_annual_revenue": float(total_annual),
            "estimated_asset_value": float(asset_value),
            "revenue_per_mw": float(total_annual / Decimal(capacity_mw))
        }
