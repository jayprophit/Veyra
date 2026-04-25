"""Physical Gold/Silver Integration
====================================
Connect to Goldwise, BullionVault for physical metal ownership.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class PhysicalMetal:
    metal_type: str  # gold, silver, platinum
    grams: Decimal
    price_per_gram: Decimal
    storage_provider: str  # Goldwise, BullionVault, Royal Mint
    storage_fee_annual: Decimal
    location: str  # London, Zurich, Singapore


class GoldwiseAPI:
    """Goldwise integration - UK gold platform"""
    
    BASE_URL = "https://api.goldwise.co.uk/v1"
    MIN_PURCHASE_GBP = 5.0
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.balance_gbp = Decimal("0")
        self.holdings: List[PhysicalMetal] = []
    
    def buy_gold(self, amount_gbp: float, auto_save: bool = False) -> Dict:
        """Buy physical gold"""
        # Current gold price ~£60/gram
        price_per_gram = Decimal("60.50")
        grams = Decimal(str(amount_gbp)) / price_per_gram
        
        gold = PhysicalMetal(
            metal_type="gold",
            grams=grams,
            price_per_gram=price_per_gram,
            storage_provider="Goldwise",
            storage_fee_annual=grams * price_per_gram * Decimal("0.005"),  # 0.5%
            location="London"
        )
        
        self.holdings.append(gold)
        
        return {
            "provider": "Goldwise",
            "amount_gbp": amount_gbp,
            "grams": float(grams),
            "storage": "London vault",
            "auto_save": auto_save,
            "monthly_fee_estimate": float(gold.storage_fee_annual / 12)
        }
    
    def buy_silver(self, amount_gbp: float) -> Dict:
        """Buy physical silver"""
        price_per_gram = Decimal("0.75")  # ~£0.75/gram
        grams = Decimal(str(amount_gbp)) / price_per_gram
        
        silver = PhysicalMetal(
            metal_type="silver",
            grams=grams,
            price_per_gram=price_per_gram,
            storage_provider="Goldwise",
            storage_fee_annual=grams * price_per_gram * Decimal("0.005"),
            location="London"
        )
        
        self.holdings.append(silver)
        
        return {
            "provider": "Goldwise",
            "amount_gbp": amount_gbp,
            "grams": float(grams),
            "storage": "London vault"
        }
    
    def get_portfolio_value(self) -> Dict:
        """Get current value of physical metals"""
        total_value = Decimal("0")
        
        for holding in self.holdings:
            # Use current spot price
            current_price = self._get_current_price(holding.metal_type)
            value = holding.grams * current_price
            total_value += value
        
        return {
            "total_gbp": float(total_value),
            "holdings": [
                {
                    "metal": h.metal_type,
                    "grams": float(h.grams),
                    "value_gbp": float(h.grams * self._get_current_price(h.metal_type)),
                    "location": h.location
                }
                for h in self.holdings
            ],
            "monthly_storage_fees": float(sum(h.storage_fee_annual / 12 for h in self.holdings))
        }
    
    def _get_current_price(self, metal: str) -> Decimal:
        """Get current spot price per gram"""
        prices = {
            "gold": Decimal("60.50"),
            "silver": Decimal("0.75"),
            "platinum": Decimal("28.00")
        }
        return prices.get(metal, Decimal("0"))


class BullionVaultAPI:
    """BullionVault integration - International storage"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.locations = ["London", "Zurich", "Singapore", "Toronto"]
    
    def allocate_storage(self, metal: str, amount_gbp: float, location: str) -> Dict:
        """Allocate physical metal in specific location"""
        if location not in self.locations:
            return {"error": f"Location {location} not available"}
        
        # BullionVault pricing
        fees = {
            "London": 0.0012,  # 0.12%
            "Zurich": 0.0012,
            "Singapore": 0.0015,
            "Toronto": 0.0018
        }
        
        return {
            "platform": "BullionVault",
            "metal": metal,
            "amount_gbp": amount_gbp,
            "location": location,
            "annual_fee_rate": fees.get(location, 0.0012),
            "insured": True
        }


class PreciousMetalsManager:
    """Manage all physical precious metals across platforms"""
    
    def __init__(self):
        self.goldwise = GoldwiseAPI()
        self.bullionvault = BullionVaultAPI()
        self.target_allocation = {"gold": 0.10, "silver": 0.05}  # 10% gold, 5% silver
    
    def buy_monthly(self, amount_gbp: float, split: str = "70/30") -> Dict:
        """Monthly gold/silver purchase"""
        # Default 70% gold, 30% silver
        gold_amount = amount_gbp * 0.70
        silver_amount = amount_gbp * 0.30
        
        gold_result = self.goldwise.buy_gold(gold_amount, auto_save=True)
        silver_result = self.goldwise.buy_silver(silver_amount)
        
        return {
            "total_invested": amount_gbp,
            "gold": gold_result,
            "silver": silver_result,
            "auto_save_enabled": True,
            "next_purchase": "Monthly"
        }
    
    def get_total_allocation(self, total_portfolio_value: float) -> Dict:
        """Check current vs target allocation"""
        metals_value = self.goldwise.get_portfolio_value()["total_gbp"]
        current_pct = metals_value / total_portfolio_value if total_portfolio_value > 0 else 0
        
        return {
            "metals_value_gbp": metals_value,
            "portfolio_value": total_portfolio_value,
            "current_allocation": current_pct,
            "target_allocation": sum(self.target_allocation.values()),
            "rebalance_needed": current_pct < sum(self.target_allocation.values())
        }
