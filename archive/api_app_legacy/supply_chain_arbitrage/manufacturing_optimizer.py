"""Manufacturing Optimizer - Factory arbitrage, production cost optimization"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class ManufacturingType(Enum):
    ELECTRONICS = "electronics"; TEXTILES = "textiles"
    AUTOMOTIVE = "automotive"; PHARMA = "pharma"
    FOOD_PROCESSING = "food_processing"; STEEL = "steel"
    CHEMICALS = "chemicals"; PLASTICS = "plastics"

@dataclass
class ManufacturingContract:
    contract_id: str; product_type: str
    quantity: Decimal; unit_cost: Decimal
    factory_location: str; delivery_date: date
    profit_margin: Decimal = Decimal("0")

class ManufacturingOptimizer:
    """Manufacturing cost arbitrage and optimization"""
    
    def __init__(self):
        self.active_contracts: Dict[str, ManufacturingContract] = {}
        self.factory_network = self._init_factory_network()
        
    def _init_factory_network(self):
        return {
            "shenzhen_electronics": {
                "location": "Shenzhen, China",
                "type": ManufacturingType.ELECTRONICS,
                "labor_cost_per_hour": Decimal("4.50"),
                "capacity_units_per_day": 50000,
                "quality_rating": 8.5,
                "shipping_cost_to_us": Decimal("2.50"),
                "min_order": 1000
            },
            "vietnam_textiles": {
                "location": "Ho Chi Minh, Vietnam",
                "type": ManufacturingType.TEXTILES,
                "labor_cost_per_hour": Decimal("2.80"),
                "capacity_units_per_day": 100000,
                "quality_rating": 7.5,
                "shipping_cost_to_us": Decimal("3.20"),
                "min_order": 5000
            },
            "bangladesh_garments": {
                "location": "Dhaka, Bangladesh",
                "type": ManufacturingType.TEXTILES,
                "labor_cost_per_hour": Decimal("1.50"),
                "capacity_units_per_day": 200000,
                "quality_rating": 6.5,
                "shipping_cost_to_us": Decimal("3.80"),
                "min_order": 10000
            },
            "mexico_automotive": {
                "location": "Monterrey, Mexico",
                "type": ManufacturingType.AUTOMOTIVE,
                "labor_cost_per_hour": Decimal("6.50"),
                "capacity_units_per_day": 5000,
                "quality_rating": 8.0,
                "shipping_cost_to_us": Decimal("0.50"),
                "min_order": 500
            },
            "india_pharma": {
                "location": "Hyderabad, India",
                "type": ManufacturingType.PHARMA,
                "labor_cost_per_hour": Decimal("3.00"),
                "capacity_units_per_day": 1000000,
                "quality_rating": 9.0,
                "shipping_cost_to_us": Decimal("1.80"),
                "min_order": 50000
            },
            "germany_steel": {
                "location": "Duisburg, Germany",
                "type": ManufacturingType.STEEL,
                "labor_cost_per_hour": Decimal("28.00"),
                "capacity_units_per_day": 10000,
                "quality_rating": 9.5,
                "shipping_cost_to_us": Decimal("8.00"),
                "min_order": 100
            },
            "usa_food": {
                "location": "Omaha, USA",
                "type": ManufacturingType.FOOD_PROCESSING,
                "labor_cost_per_hour": Decimal("18.00"),
                "capacity_units_per_day": 500000,
                "quality_rating": 9.0,
                "shipping_cost_to_us": Decimal("0.20"),
                "min_order": 10000
            }
        }
    
    def calculate_production_cost(self, factory_id: str, 
                                product_specs: Dict) -> Dict:
        """Calculate total production cost at a factory"""
        if factory_id not in self.factory_network:
            return {"error": "Factory not found"}
        
        factory = self.factory_network[factory_id]
        quantity = product_specs.get("quantity", 1000)
        
        # Calculate costs
        labor_hours_per_unit = product_specs.get("labor_hours", 0.5)
        labor_cost = factory["labor_cost_per_hour"] * Decimal(labor_hours_per_unit) * Decimal(quantity)
        
        material_cost_per_unit = product_specs.get("material_cost", 5.00)
        material_cost = Decimal(material_cost_per_unit) * Decimal(quantity)
        
        overhead_per_unit = product_specs.get("overhead", 1.00)
        overhead = Decimal(overhead_per_unit) * Decimal(quantity)
        
        shipping = factory["shipping_cost_to_us"] * Decimal(quantity)
        
        total_cost = labor_cost + material_cost + overhead + shipping
        cost_per_unit = total_cost / Decimal(quantity)
        
        # Retail price calculation
        retail_price_per_unit = cost_per_unit * Decimal("2.5")  # 150% markup
        
        return {
            "factory": factory_id,
            "location": factory["location"],
            "quantity": quantity,
            "labor_cost": float(labor_cost),
            "material_cost": float(material_cost),
            "overhead": float(overhead),
            "shipping": float(shipping),
            "total_cost": float(total_cost),
            "cost_per_unit": float(cost_per_unit),
            "retail_price_per_unit": float(retail_price_per_unit),
            "profit_per_unit": float(retail_price_per_unit - cost_per_unit),
            "total_potential_profit": float((retail_price_per_unit - cost_per_unit) * Decimal(quantity)),
            "quality_rating": factory["quality_rating"]
        }
    
    def find_arbitrage_opportunities(self, product_specs: Dict) -> List[Dict]:
        """Find best manufacturing locations for product"""
        opportunities = []
        
        for factory_id in self.factory_network:
            cost_data = self.calculate_production_cost(factory_id, product_specs)
            
            if "error" not in cost_data:
                opportunities.append({
                    "factory_id": factory_id,
                    "location": cost_data["location"],
                    "cost_per_unit": cost_data["cost_per_unit"],
                    "total_cost": cost_data["total_cost"],
                    "potential_profit": cost_data["total_potential_profit"],
                    "quality_rating": cost_data["quality_rating"],
                    "shipping_cost": cost_data["shipping"]
                })
        
        return sorted(opportunities, key=lambda x: x["cost_per_unit"])
    
    def create_contract(self, factory_id: str, product_type: str,
                       quantity: Decimal, specs: Dict) -> Dict:
        """Create manufacturing contract"""
        cost_data = self.calculate_production_cost(factory_id, {
            "quantity": int(quantity),
            "labor_hours": specs.get("labor_hours", 0.5),
            "material_cost": specs.get("material_cost", 5.00)
        })
        
        if "error" in cost_data:
            return cost_data
        
        contract_id = f"MFG_{factory_id}_{date.today().isoformat()}"
        
        contract = ManufacturingContract(
            contract_id=contract_id,
            product_type=product_type,
            quantity=quantity,
            unit_cost=Decimal(str(cost_data["cost_per_unit"])),
            factory_location=cost_data["location"],
            delivery_date=date.today(),
            profit_margin=Decimal(str(cost_data["profit_per_unit"]))
        )
        
        self.active_contracts[contract_id] = contract
        
        return {
            "success": True,
            "contract_id": contract_id,
            "factory": factory_id,
            "product": product_type,
            "quantity": float(quantity),
            "unit_cost": cost_data["cost_per_unit"],
            "total_cost": cost_data["total_cost"],
            "expected_profit": cost_data["total_potential_profit"],
            "delivery_estimate_weeks": 12
        }
    
    def get_margin_optimization(self) -> List[Dict]:
        """Get margin optimization strategies"""
        return [
            {
                "strategy": "nearshoring",
                "current": "China factory",
                "proposed": "Mexico factory",
                "shipping_savings_pct": 80,
                "labor_cost_increase_pct": 45,
                "net_margin_improvement_pct": 12,
                "payback_period_months": 8
            },
            {
                "strategy": "automation",
                "investment": 500000,
                "labor_reduction_pct": 60,
                "productivity_gain_pct": 35,
                "annual_savings": 350000,
                "roi_pct": 70,
                "payback_months": 17
            },
            {
                "strategy": "bulk_material_purchasing",
                "investment": 200000,
                "material_cost_reduction_pct": 15,
                "annual_savings": 180000,
                "roi_pct": 90,
                "payback_months": 13
            }
        ]
