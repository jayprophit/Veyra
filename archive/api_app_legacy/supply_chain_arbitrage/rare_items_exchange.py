"""Rare Items Exchange - Collectibles, art, vintage, memorabilia"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class ItemCategory(Enum):
    FINE_ART = "fine_art"; VINTAGE_CARS = "vintage_cars"
    WATCHES = "watches"; JEWELRY = "jewelry"
    WINE = "wine"; WHISKEY = "whiskey"
    MEMORABILIA = "memorabilia"; COMICS = "comics"
    TRADING_CARDS = "trading_cards"; COINS = "coins"
    STAMPS = "stamps"; ANTIQUES = "antiques"
    SNEAKERS = "sneakers"; HAND_BAGS = "hand_bags"
    NFTS = "nfts"; VIRTUAL_ITEMS = "virtual_items"

@dataclass
class RareItem:
    item_id: str; category: ItemCategory; name: str
    maker: str; year: int; condition: str
    purchase_price: Decimal; current_value: Decimal
    unrealized_pnl: Decimal = Decimal("0")
    authenticity_verified: bool = False

class RareItemsExchange:
    """Rare and collectible item trading platform"""
    
    def __init__(self):
        self.inventory: Dict[str, RareItem] = {}
        self.price_database = self._init_price_database()
        
    def _init_price_database(self):
        return {
            ItemCategory.FINE_ART: {
                "baseline_appreciation_pct": 8,
                "blue_chip_artists": ["Basquiat", "Koons", "Richter", "Banksy"],
                "avg_sale_price_k": 250
            },
            ItemCategory.VINTAGE_CARS: {
                "baseline_appreciation_pct": 12,
                "top_models": ["Ferrari 250 GTO", "Mercedes 300SL", "Ford GT40"],
                "avg_sale_price_k": 800
            },
            ItemCategory.WATCHES: {
                "baseline_appreciation_pct": 15,
                "top_brands": ["Patek Philippe", "Rolex", "Audemars Piguet", "Richard Mille"],
                "avg_sale_price_k": 45
            },
            ItemCategory.WINE: {
                "baseline_appreciation_pct": 10,
                "top_vintages": ["1945 Mouton", "1992 Screaming Eagle", "2000 Petrus"],
                "avg_sale_price_k": 25
            },
            ItemCategory.TRADING_CARDS: {
                "baseline_appreciation_pct": 25,
                "top_cards": ["1952 Mickey Mantle", "1986 Jordan Fleer", "2009 Trout"],
                "avg_sale_price_k": 150
            },
            ItemCategory.SNEAKERS: {
                "baseline_appreciation_pct": 20,
                "top_models": ["Nike Air Yeezy 2", "Jordan 1 Chicago", "Dunk SB Low"],
                "avg_sale_price_k": 8
            }
        }
    
    def find_opportunities(self) -> List[Dict]:
        """Find undervalued rare items"""
        opportunities = []
        
        # Watch arbitrage
        watch_opps = [
            {"model": "Rolex Daytona", "year": 2023, "buy_price": 25000, "market_price": 35000, "profit": 10000},
            {"model": "Patek 5711", "year": 2021, "buy_price": 95000, "market_price": 140000, "profit": 45000},
            {"model": "AP Royal Oak", "year": 2022, "buy_price": 55000, "market_price": 75000, "profit": 20000}
        ]
        
        for w in watch_opps:
            opportunities.append({
                "category": "watches",
                "item": w["model"],
                "buy_price": w["buy_price"],
                "market_price": w["market_price"],
                "profit_potential": w["profit"],
                "roi_pct": (w["profit"] / w["buy_price"]) * 100,
                "source": "Authorized dealer waitlist",
                "urgency": "high"
            })
        
        # Art opportunities
        art_opps = [
            {"artist": "Banksy", "piece": "Girl with Balloon", "edition": "signed", "buy_price": 50000, "market_price": 120000},
            {"artist": "KAWS", "piece": "Companion", "edition": "5/10", "buy_price": 15000, "market_price": 45000}
        ]
        
        for a in art_opps:
            opportunities.append({
                "category": "fine_art",
                "item": f"{a['artist']} - {a['piece']}",
                "buy_price": a["buy_price"],
                "market_price": a["market_price"],
                "profit_potential": a["market_price"] - a["buy_price"],
                "roi_pct": ((a["market_price"] - a["buy_price"]) / a["buy_price"]) * 100,
                "source": "Gallery primary",
                "urgency": "medium"
            })
        
        # Wine arbitrage
        wine_opps = [
            {"wine": "2010 Lafite Rothschild", "cases": 5, "buy_price_per_case": 8500, "market_price": 12000},
            {"wine": "2015 Screaming Eagle", "cases": 2, "buy_price_per_case": 32000, "market_price": 48000}
        ]
        
        for wine in wine_opps:
            opportunities.append({
                "category": "wine",
                "item": wine["wine"],
                "buy_price": wine["buy_price_per_case"] * wine["cases"],
                "market_price": wine["market_price"] * wine["cases"],
                "profit_potential": (wine["market_price"] - wine["buy_price_per_case"]) * wine["cases"],
                "roi_pct": ((wine["market_price"] - wine["buy_price_per_case"]) / wine["buy_price_per_case"]) * 100,
                "source": "Bordeaux en primeur",
                "urgency": "low"
            })
        
        return sorted(opportunities, key=lambda x: x["roi_pct"], reverse=True)
    
    def purchase_item(self, category: ItemCategory, name: str, maker: str,
                     year: int, condition: str, price: Decimal) -> Dict:
        """Purchase rare item for inventory"""
        item_id = f"{category.value}_{year}_{abs(hash(name)) % 100000:05d}"
        
        item = RareItem(
            item_id=item_id, category=category, name=name, maker=maker,
            year=year, condition=condition, purchase_price=price,
            current_value=price * Decimal("1.1"),  # 10% markup
            authenticity_verified=False
        )
        
        self.inventory[item_id] = item
        
        return {
            "success": True, "item_id": item_id,
            "category": category.value, "name": name,
            "purchase_price": float(price),
            "current_estimated_value": float(item.current_value),
            "portfolio_size": len(self.inventory)
        }
    
    def get_portfolio_summary(self) -> Dict:
        """Get rare items portfolio summary"""
        if not self.inventory:
            return {"total_items": 0, "total_value": 0, "by_category": {}}
        
        total_value = sum(i.current_value for i in self.inventory.values())
        total_cost = sum(i.purchase_price for i in self.inventory.values())
        
        by_category = {}
        for item in self.inventory.values():
            cat = item.category.value
            if cat not in by_category:
                by_category[cat] = {"count": 0, "value": 0, "cost": 0}
            by_category[cat]["count"] += 1
            by_category[cat]["value"] += float(item.current_value)
            by_category[cat]["cost"] += float(item.purchase_price)
        
        # Calculate ROI by category
        for cat in by_category:
            cost = by_category[cat]["cost"]
            value = by_category[cat]["value"]
            by_category[cat]["unrealized_pnl"] = value - cost
            by_category[cat]["roi_pct"] = ((value - cost) / cost * 100) if cost > 0 else 0
        
        return {
            "total_items": len(self.inventory),
            "total_cost_basis": float(total_cost),
            "total_current_value": float(total_value),
            "total_unrealized_pnl": float(total_value - total_cost),
            "portfolio_roi_pct": float((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
            "by_category": by_category
        }
    
    def fractionalize_item(self, item_id: str, shares: int) -> Dict:
        """Create fractional ownership of expensive item"""
        if item_id not in self.inventory:
            return {"success": False, "error": "Item not found"}
        
        item = self.inventory[item_id]
        value_per_share = item.current_value / Decimal(shares)
        
        return {
            "success": True, "item_id": item_id,
            "item_name": item.name, "total_value": float(item.current_value),
            "shares_created": shares,
            "value_per_share": float(value_per_share),
            "minimum_investment": float(value_per_share),
            "platform_fee_pct": 2.5
        }
