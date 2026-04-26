"""E-Commerce Revenue Tracker - Amazon, eBay, Etsy, Shopify, Alibaba, etc."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class EcommercePlatform(Enum):
    AMAZON = "amazon"; EBAY = "ebay"; ETSY = "etsy"; SHOPIFY = "shopify"
    ALIBABA = "alibaba"; ALIEXPRESS = "aliexpress"; WALMART = "walmart"
    NEWEGG = "newegg"; RAKUTEN = "rakuten"; MERCARI = "mercari"
    POSHMARK = "poshmark"; STOCKX = "stockx"; GOAT = "goat"
    FACEBOOK_MARKETPLACE = "facebook_marketplace"; GOOGLE_SHOPPING = "google_shopping"

class ProductType(Enum):
    PHYSICAL = "physical"; DIGITAL = "digital"; DROPSHIPPED = "dropshipped"
    PRINT_ON_DEMAND = "print_on_demand"; HANDMADE = "handmade"; USED = "used"
    WHOLESALE = "wholesale"; BULK = "bulk"

@dataclass
class EcommerceSale:
    platform: EcommercePlatform; product_type: ProductType
    gross_revenue: Decimal; net_revenue: Decimal
    units_sold: int; date: date
    product_category: str

class EcommerceRevenueTracker:
    """Track revenue from all e-commerce platforms"""
    
    def __init__(self):
        self.sales_history: List[EcommerceSale] = []
        self.platform_fees = {
            EcommercePlatform.AMAZON: {
                "referral_fee_pct": Decimal("0.15"),  # 15% average
                "fba_fee_per_unit": Decimal("5.00"),
                "monthly_storage_per_unit": Decimal("0.75"),
                "fba_optional": True
            },
            EcommercePlatform.EBAY: {
                "insertion_fee": Decimal("0.35"),
                "final_value_fee_pct": Decimal("0.135"),  # 13.5%
                "store_subscription": Decimal("21.95"),  # monthly
                "promoted_listings_pct": Decimal("0.10")
            },
            EcommercePlatform.ETSY: {
                "listing_fee": Decimal("0.20"),
                "transaction_fee_pct": Decimal("0.065"),  # 6.5%
                "payment_processing_pct": Decimal("0.03"),
                "offsite_ads_pct": Decimal("0.15")  # if enabled
            },
            EcommercePlatform.SHOPIFY: {
                "subscription_tier": "basic",  # $29/month
                "subscription_cost": Decimal("29.00"),
                "transaction_fee_pct": Decimal("0.029"),
                "plus_processing": Decimal("0.30"),
                "payment_processing_pct": Decimal("0.029")
            },
            EcommercePlatform.ALIBABA: {
                "annual_fee": Decimal("3999.00"),
                "transaction_fee_pct": Decimal("0.02"),
                "payment_processing_pct": Decimal("0.029")
            },
            EcommercePlatform.ALIEXPRESS: {
                "commission_pct": Decimal("0.05"),  # 5-8%
                "payment_processing_pct": Decimal("0.029")
            },
            EcommercePlatform.WALMART: {
                "referral_fee_pct": Decimal("0.15"),
                "wfs_fee_per_unit": Decimal("3.45"),
                "monthly_subscription": Decimal("0.00")  # no monthly fee
            },
            EcommercePlatform.MERCARI: {
                "selling_fee_pct": Decimal("0.10"),
                "payment_processing_pct": Decimal("0.029") + Decimal("0.30")
            },
            EcommercePlatform.STOCKX: {
                "seller_fee_base_pct": Decimal("0.095"),  # 9.5%
                "payment_processing_pct": Decimal("0.03")
            }
        }
    
    def calculate_amazon_revenue(self, units_sold: int, price_per_unit: Decimal,
                                 product_category: str = "general",
                                 use_fba: bool = True,
                                 product_weight_lbs: float = 1.0) -> Dict:
        """Calculate Amazon FBA/FBM revenue"""
        fees = self.platform_fees[EcommercePlatform.AMAZON]
        
        # Category-specific referral fees
        referral_rates = {
            "electronics": Decimal("0.08"), "fashion": Decimal("0.17"),
            "home": Decimal("0.15"), "beauty": Decimal("0.15"),
            "books": Decimal("0.15"), "toys": Decimal("0.15"),
            "general": Decimal("0.15")
        }
        
        referral_rate = referral_rates.get(product_category, Decimal("0.15"))
        gross_revenue = Decimal(units_sold) * price_per_unit
        
        # Referral fee
        referral_fee = gross_revenue * referral_rate
        
        # FBA fees
        fba_cost = Decimal("0")
        if use_fba:
            # Simplified FBA calculation
            size_tier = "small_standard" if product_weight_lbs < 1 else "large_standard"
            base_fba = fees["fba_fee_per_unit"] if size_tier == "large_standard" else Decimal("3.22")
            weight_handling = Decimal(str(product_weight_lbs)) * Decimal("0.50")
            fba_per_unit = base_fba + weight_handling
            fba_cost = fba_per_unit * Decimal(units_sold)
            
            # Storage
            storage_cost = fees["monthly_storage_per_unit"] * Decimal(units_sold)
            fba_cost += storage_cost
        
        # Total fees
        total_fees = referral_fee + fba_cost
        net_revenue = gross_revenue - total_fees
        
        return {
            "platform": "amazon",
            "units_sold": units_sold,
            "price_per_unit": float(price_per_unit),
            "gross_revenue": float(gross_revenue),
            "referral_fee": float(referral_fee),
            "fba_cost": float(fba_cost),
            "total_fees": float(total_fees),
            "net_revenue": float(net_revenue),
            "take_home_pct": float(net_revenue / gross_revenue * 100) if gross_revenue > 0 else 0,
            "fulfillment_method": "FBA" if use_fba else "FBM",
            "per_unit_profit": float(net_revenue / Decimal(units_sold)) if units_sold > 0 else 0
        }
    
    def calculate_ebay_revenue(self, units_sold: int, price_per_unit: Decimal,
                             has_store: bool = True,
                             promoted_listings: bool = False) -> Dict:
        """Calculate eBay revenue"""
        fees = self.platform_fees[EcommercePlatform.EBAY]
        
        gross_revenue = Decimal(units_sold) * price_per_unit
        
        # Insertion fees (first 250 free with store)
        insertion_fees = Decimal("0") if has_store else fees["insertion_fee"] * max(0, units_sold - 50)
        
        # Final value fee (13.5% for most categories)
        final_value_fee = gross_revenue * fees["final_value_fee_pct"]
        
        # Store subscription (prorated per sale)
        store_cost = fees["store_subscription"] / 30 * Decimal(units_sold) if has_store else Decimal("0")
        
        # Promoted listings fee (if used)
        promoted_fee = gross_revenue * fees["promoted_listings_pct"] if promoted_listings else Decimal("0")
        
        total_fees = insertion_fees + final_value_fee + store_cost + promoted_fee
        
        # Payment processing (managed payments ~0.30 + 2.9%)
        processing = gross_revenue * Decimal("0.029") + Decimal("0.30") * Decimal(units_sold)
        
        total_fees += processing
        net_revenue = gross_revenue - total_fees
        
        return {
            "platform": "ebay",
            "gross_revenue": float(gross_revenue),
            "insertion_fees": float(insertion_fees),
            "final_value_fee": float(final_value_fee),
            "store_cost": float(store_cost),
            "promoted_listings_fee": float(promoted_fee),
            "payment_processing": float(processing),
            "total_fees": float(total_fees),
            "net_revenue": float(net_revenue),
            "take_home_pct": float(net_revenue / gross_revenue * 100) if gross_revenue > 0 else 0
        }
    
    def calculate_etsy_revenue(self, units_sold: int, price_per_unit: Decimal,
                             shipping_charged: Decimal = Decimal("5.00"),
                             offsite_ads: bool = True) -> Dict:
        """Calculate Etsy revenue for handmade/digital"""
        fees = self.platform_fees[EcommercePlatform.ETSY]
        
        gross_revenue = Decimal(units_sold) * (price_per_unit + shipping_charged)
        
        # Listing fees ($0.20 per item, renewed every 4 months)
        listing_fees = fees["listing_fee"] * Decimal(units_sold)
        
        # Transaction fee (6.5% on total including shipping)
        transaction_fee = gross_revenue * fees["transaction_fee_pct"]
        
        # Payment processing (3% + $0.25)
        processing = gross_revenue * fees["payment_processing_pct"] + Decimal("0.25") * Decimal(units_sold)
        
        # Offsite ads fee (15% if clicked and purchased within 30 days)
        offsite_fee = gross_revenue * fees["offsite_ads_pct"] if offsite_ads else Decimal("0")
        
        total_fees = listing_fees + transaction_fee + processing + offsite_fee
        net_revenue = gross_revenue - total_fees
        
        return {
            "platform": "etsy",
            "gross_revenue": float(gross_revenue),
            "listing_fees": float(listing_fees),
            "transaction_fee": float(transaction_fee),
            "payment_processing": float(processing),
            "offsite_ads_fee": float(offsite_fee),
            "total_fees": float(total_fees),
            "net_revenue": float(net_revenue),
            "take_home_pct": float(net_revenue / gross_revenue * 100) if gross_revenue > 0 else 0,
            "per_unit_cost": float(total_fees / Decimal(units_sold)) if units_sold > 0 else 0
        }
    
    def calculate_shopify_revenue(self, units_sold: int, price_per_unit: Decimal,
                                  ad_spend: Decimal = Decimal("0")) -> Dict:
        """Calculate Shopify revenue"""
        fees = self.platform_fees[EcommercePlatform.SHOPIFY]
        
        gross_revenue = Decimal(units_sold) * price_per_unit
        
        # Monthly subscription (assuming basic $29/mo, prorated per sale)
        subscription = fees["subscription_cost"] / 100  # Assuming 100 sales/month baseline
        
        # Shopify Payments processing (2.9% + $0.30)
        processing = gross_revenue * fees["payment_processing_pct"] + fees["plus_processing"] * Decimal(units_sold)
        
        total_fees = subscription + processing + ad_spend
        net_revenue = gross_revenue - total_fees
        
        return {
            "platform": "shopify",
            "gross_revenue": float(gross_revenue),
            "subscription_cost": float(subscription),
            "payment_processing": float(processing),
            "ad_spend": float(ad_spend),
            "total_fees": float(total_fees),
            "net_revenue": float(net_revenue),
            "roas": float(gross_revenue / ad_spend) if ad_spend > 0 else 0,
            "take_home_pct": float(net_revenue / gross_revenue * 100) if gross_revenue > 0 else 0
        }
    
    def digital_products_revenue(self, platform: str, units_sold: int,
                                 price_per_unit: Decimal,
                                 product_type: str = "ebook") -> Dict:
        """Calculate revenue for digital products (ebooks, courses, templates)"""
        digital_platforms = {
            "gumroad": {"fee_pct": Decimal("0.10"), "processing_pct": Decimal("0.029") + Decimal("0.30")},
            "teachable": {"fee_pct": Decimal("0.05"), "subscription": Decimal("39.00")},
            "udemy": {"fee_pct": Decimal("0.37"), "processing_pct": Decimal("0.03")},  # 37% revenue share
            "amazon_kdp": {"royalty_pct": Decimal("0.70") if price_per_unit > Decimal("2.99") else Decimal("0.35"),
                          "delivery_cost": Decimal("0.15")},  # per MB
            "etsy_digital": {"transaction_pct": Decimal("0.065"), "listing": Decimal("0.20"),
                           "processing_pct": Decimal("0.03")}
        }
        
        if platform not in digital_platforms:
            return {"error": "Platform not supported"}
        
        config = digital_platforms[platform]
        gross = Decimal(units_sold) * price_per_unit
        
        if platform == "amazon_kdp":
            royalty_rate = config["royalty_pct"]
            net = gross * royalty_rate - (config["delivery_cost"] * Decimal(units_sold))
        else:
            fee = gross * config.get("fee_pct", Decimal("0"))
            processing = gross * config.get("processing_pct", Decimal("0.03"))
            subscription = config.get("subscription", Decimal("0")) / 100  # Prorated
            net = gross - fee - processing - subscription
        
        return {
            "platform": platform,
            "product_type": product_type,
            "units_sold": units_sold,
            "price": float(price_per_unit),
            "gross_revenue": float(gross),
            "net_revenue": float(net),
            "take_home_pct": float(net / gross * 100) if gross > 0 else 0,
            "marginal_cost": 0,  # Digital has zero marginal cost
            "profit_margin_pct": 100 if net > 0 else 0
        }
    
    def arbitrage_opportunities(self, product_query: str) -> List[Dict]:
        """Find retail arbitrage opportunities across platforms"""
        # Mock arbitrage scanner
        opportunities = [
            {
                "product": "Wireless Headphones",
                "buy_platform": "alibaba",
                "buy_price": 12.50,
                "sell_platform": "amazon",
                "sell_price": 45.00,
                "estimated_fees": 15.00,
                "net_profit": 17.50,
                "roi_pct": 140,
                "confidence": "high"
            },
            {
                "product": "Phone Cases (Bulk 100)",
                "buy_platform": "aliexpress",
                "buy_price": 200.00,
                "sell_platform": "ebay",
                "sell_price": 500.00,
                "estimated_fees": 120.00,
                "net_profit": 180.00,
                "roi_pct": 90,
                "confidence": "medium"
            },
            {
                "product": "Vintage T-shirts",
                "buy_platform": "thrift_stores",
                "buy_price": 5.00,
                "sell_platform": "poshmark",
                "sell_price": 35.00,
                "estimated_fees": 10.00,
                "net_profit": 20.00,
                "roi_pct": 400,
                "confidence": "high"
            }
        ]
        
        return sorted(opportunities, key=lambda x: x["roi_pct"], reverse=True)
    
    def multi_platform_strategy(self, product_category: str,
                                monthly_volume: int,
                                avg_price: Decimal) -> Dict:
        """Recommend optimal multi-platform strategy"""
        strategies = []
        
        # Amazon strategy
        amazon_rev = self.calculate_amazon_revenue(
            monthly_volume // 2, avg_price, product_category
        )
        strategies.append({
            "platform": "amazon",
            "allocation_pct": 50,
            "projected_monthly": amazon_rev["net_revenue"],
            "strengths": ["Highest volume", "FBA convenience", "Prime customers"],
            "considerations": ["High fees", "Strict policies"]
        })
        
        # eBay strategy
        ebay_rev = self.calculate_ebay_revenue(
            monthly_volume // 4, avg_price, has_store=True
        )
        strategies.append({
            "platform": "ebay",
            "allocation_pct": 25,
            "projected_monthly": ebay_rev["net_revenue"],
            "strengths": ["Lower fees", "Auction option", "Used goods"],
            "considerations": ["Lower volume", "More work"]
        })
        
        # Walmart strategy (if approved)
        if product_category in ["home", "electronics", "beauty"]:
            strategies.append({
                "platform": "walmart",
                "allocation_pct": 25,
                "projected_monthly": float(Decimal(str(monthly_volume // 4)) * avg_price * Decimal("0.80")),
                "strengths": ["Growing marketplace", "No monthly fee", "Less competition"],
                "considerations": ["Approval required", "Lower traffic"]
            })
        
        total_projected = sum(s["projected_monthly"] for s in strategies)
        
        return {
            "product_category": product_category,
            "total_monthly_volume": monthly_volume,
            "avg_price": float(avg_price),
            "platform_allocation": strategies,
            "total_projected_monthly": total_projected,
            "risk_level": "medium",
            "recommendation": "Start with Amazon FBA, expand to eBay and Walmart"
        }
