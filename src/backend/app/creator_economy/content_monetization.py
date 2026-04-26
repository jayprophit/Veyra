"""Content Monetization - Digital products, courses, ebooks, templates, downloads"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class ContentType(Enum):
    EBOOK = "ebook"; COURSE = "course"; TEMPLATE = "template"
    PRESET = "preset"; STOCK_MEDIA = "stock_media"; SOFTWARE = "software"
    MUSIC = "music"; PODCAST = "podcast"; NEWSLETTER = "newsletter"
    MEMBERSHIP = "membership"; COACHING = "coaching"; CONSULTING = "consulting"

class Platform(Enum):
    GUMROAD = "gumroad"; LEMONSQUEEZY = "lemonsqueezy"; PAYHIP = "payhip"
    TEACHABLE = "teachable"; THINKIFIC = "thinkific"; KAJABI = "kajabi"
    SKOOL = "skool"; CIRCLE = "circle"; DISCORD_PAID = "discord_paid"
    SUBSTACK = "substack"; BEEHIV = "beehiv"; CONVERTKIT = "convertkit"
    APP_SUMO = "app_sumo"; PRODUCT_HUNT = "product_hunt"

@dataclass
class DigitalProduct:
    name: str; content_type: ContentType
    price: Decimal; platform: Platform
    units_sold: int; creation_cost: Decimal
    monthly_maintenance: Decimal

class ContentMonetization:
    """Monetize digital content, courses, ebooks, templates"""
    
    def __init__(self):
        self.products: List[DigitalProduct] = []
        self.platform_fees = {
            Platform.GUMROAD: {"fee_pct": Decimal("0.10"), "processing": Decimal("0.029") + Decimal("0.30")},
            Platform.LEMONSQUEEZY: {"fee_pct": Decimal("0.05"), "processing": Decimal("0.029")},
            Platform.PAYHIP: {"fee_pct": Decimal("0.05"), "monthly": Decimal("0")},
            Platform.TEACHABLE: {"fee_pct": Decimal("0.05"), "monthly": Decimal("39.00")},
            Platform.THINKIFIC: {"fee_pct": Decimal("0.00"), "monthly": Decimal("36.00")},
            Platform.KAJABI: {"fee_pct": Decimal("0.00"), "monthly": Decimal("149.00")},
            Platform.SKOOL: {"fee_pct": Decimal("0.00"), "monthly": Decimal("99.00")},
            Platform.SUBSTACK: {"fee_pct": Decimal("0.10"), "processing": Decimal("0")}  # 10% of paid subs
        }
    
    def calculate_ebook_revenue(self, price: Decimal, 
                               monthly_sales: int,
                               word_count: int = 20000,
                               platform: Platform = Platform.GUMROAD) -> Dict:
        """Calculate e-book revenue and costs"""
        fees = self.platform_fees.get(platform, self.platform_fees[Platform.GUMROAD])
        
        # Revenue
        gross_revenue = price * Decimal(monthly_sales)
        platform_cut = gross_revenue * fees["fee_pct"]
        processing = gross_revenue * fees.get("processing", Decimal("0.029"))
        
        # Costs
        creation_hours = word_count / 500  # 500 words/hour average
        hourly_rate = Decimal("50.00")  # Writer rate
        creation_cost = Decimal(creation_hours) * hourly_rate
        
        # Cover design
        cover_cost = Decimal("100.00") if word_count > 10000 else Decimal("50.00")
        
        # Editing (if outsourced)
        editing_cost = Decimal(word_count / 1000 * 10)  # $10 per 1000 words
        
        total_creation_cost = creation_cost + cover_cost + editing_cost
        
        # Ongoing marketing (estimate 20% of revenue)
        marketing_cost = gross_revenue * Decimal("0.20")
        
        # Platform subscription
        monthly_subscription = fees.get("monthly", Decimal("0"))
        
        total_costs = platform_cut + processing + marketing_cost + monthly_subscription
        net_revenue = gross_revenue - total_costs
        
        # Breakeven
        breakeven_units = int(total_creation_cost / (price * (Decimal("1") - fees["fee_pct"] - Decimal("0.029"))))
        
        return {
            "content_type": "ebook",
            "price": float(price),
            "word_count": word_count,
            "monthly_sales": monthly_sales,
            "gross_revenue": float(gross_revenue),
            "platform_fees": float(platform_cut),
            "processing": float(processing),
            "marketing_cost": float(marketing_cost),
            "net_revenue": float(net_revenue),
            "creation_cost": float(total_creation_cost),
            "breakeven_units": breakeven_units,
            "profit_margin_pct": float(net_revenue / gross_revenue * 100) if gross_revenue > 0 else 0,
            "roi_after_1_year": float((net_revenue * 12 - total_creation_cost) / total_creation_cost * 100) if total_creation_cost > 0 else 0
        }
    
    def calculate_course_revenue(self, price: Decimal,
                                 monthly_enrollments: int,
                                 course_hours: int = 10,
                                 platform: Platform = Platform.TEACHABLE) -> Dict:
        """Calculate online course revenue"""
        fees = self.platform_fees.get(platform, self.platform_fees[Platform.TEACHABLE])
        
        gross_revenue = price * Decimal(monthly_enrollments)
        platform_cut = gross_revenue * fees["fee_pct"]
        processing = gross_revenue * Decimal("0.029")
        subscription = fees.get("monthly", Decimal("0"))
        
        # Course creation costs
        recording_setup = Decimal("500.00")  # One-time
        editing_hours = course_hours * 3  # 3x recording time
        editing_cost = Decimal(editing_hours) * Decimal("40.00")
        platform_setup = Decimal("20.00") * course_hours  # Materials, quizzes
        
        creation_cost = recording_setup + editing_cost + platform_setup
        
        # Monthly marketing (30% of revenue for courses)
        marketing = gross_revenue * Decimal("0.30")
        
        total_costs = platform_cut + processing + marketing + subscription
        net_revenue = gross_revenue - total_costs
        
        # LTV (courses have lower retention)
        avg_student_months = 1  # One-time purchase typically
        ltv = price
        
        return {
            "content_type": "course",
            "price": float(price),
            "course_hours": course_hours,
            "monthly_enrollments": monthly_enrollments,
            "gross_revenue": float(gross_revenue),
            "platform_fees": float(platform_cut),
            "marketing": float(marketing),
            "net_revenue": float(net_revenue),
            "creation_cost": float(creation_cost),
            "customer_ltv": float(ltv),
            "payback_months": int(creation_cost / net_revenue) if net_revenue > 0 else 0,
            "annual_roi_pct": float((net_revenue * 12 - creation_cost) / creation_cost * 100) if creation_cost > 0 else 0
        }
    
    def calculate_newsletter_revenue(self, subscriber_count: int,
                                    free_to_paid_ratio: float = 0.02,
                                    monthly_price: Decimal = Decimal("5.00"),
                                    platform: Platform = Platform.SUBSTACK) -> Dict:
        """Calculate paid newsletter revenue"""
        fees = self.platform_fees.get(platform, self.platform_fees[Platform.SUBSTACK])
        
        paid_subscribers = int(subscriber_count * free_to_paid_ratio)
        gross_revenue = Decimal(paid_subscribers) * monthly_price
        
        # Substack takes 10% of paid subscriptions
        platform_cut = gross_revenue * fees["fee_pct"]
        net_revenue = gross_revenue - platform_cut
        
        # Writing time cost (2 hours per newsletter, 4 per month)
        hours_per_month = 8
        writer_cost = Decimal(hours_per_month) * Decimal("75.00")  # Ghostwriter or opportunity cost
        
        # Growth/marketing
        growth_cost = gross_revenue * Decimal("0.15")
        
        profit = net_revenue - writer_cost - growth_cost
        
        # Ad revenue potential (if allowing sponsorships)
        sponsor_cpm = Decimal("50.00")  # $50 per 1000 opens
        open_rate = 0.50
        opens = subscriber_count * open_rate
        sponsor_revenue = Decimal(opens / 1000) * sponsor_cpm * 2  # 2 sponsors per month
        
        return {
            "total_subscribers": subscriber_count,
            "paid_subscribers": paid_subscribers,
            "free_to_paid_pct": free_to_paid_ratio * 100,
            "monthly_subscription": float(monthly_price),
            "gross_revenue": float(gross_revenue),
            "platform_cut": float(platform_cut),
            "net_from_subs": float(net_revenue),
            "sponsorship_revenue": float(sponsor_revenue),
            "total_monthly": float(net_revenue + sponsor_revenue),
            "profit_after_costs": float(profit),
            "revenue_per_subscriber": float(gross_revenue / subscriber_count) if subscriber_count > 0 else 0
        }
    
    def calculate_templates_presets(self, price: Decimal,
                                    monthly_sales: int,
                                    template_type: str = "notion") -> Dict:
        """Calculate revenue from templates, presets, digital downloads"""
        # Templates have zero marginal cost after creation
        
        platforms = {
            "notion": {"marketplace": "Gumroad/Etsy", "avg_price": 19.99, "commission": 0.05},
            "excel": {"marketplace": "Etsy", "avg_price": 9.99, "commission": 0.065},
            "canva": {"marketplace": "Canva/Etsy", "avg_price": 12.99, "commission": 0.30},
            "lightroom": {"marketplace": "Gumroad", "avg_price": 29.99, "commission": 0.10},
            "figma": {"marketplace": "Figma Community", "avg_price": 25.00, "commission": 0.00},
            "webflow": {"marketplace": "Webflow", "avg_price": 49.00, "commission": 0.20}
        }
        
        platform_info = platforms.get(template_type, platforms["notion"])
        
        gross = price * Decimal(monthly_sales)
        commission = gross * Decimal(platform_info["commission"])
        processing = gross * Decimal("0.029") + Decimal("0.30") * Decimal(monthly_sales)
        
        net = gross - commission - processing
        
        # Creation time estimate
        hours_to_create = {"notion": 8, "excel": 6, "canva": 4, 
                        "lightroom": 12, "figma": 16, "webflow": 40}.get(template_type, 8)
        creation_cost = Decimal(hours_to_create) * Decimal("50.00")
        
        return {
            "template_type": template_type,
            "price": float(price),
            "monthly_sales": monthly_sales,
            "marketplace": platform_info["marketplace"],
            "gross_revenue": float(gross),
            "commission": float(commission),
            "processing": float(processing),
            "net_revenue": float(net),
            "creation_cost": float(creation_cost),
            "hours_to_create": hours_to_create,
            "profit_margin_pct": float(net / gross * 100) if gross > 0 else 0,
            "is_passive": True
        }
    
    def membership_tier_optimization(self, member_count: int = 100) -> Dict:
        """Optimize membership tier pricing"""
        # Typical membership tiers
        tiers = [
            {"name": "Basic", "price": 5, "features": "Newsletter access", "allocation_pct": 0.60},
            {"name": "Pro", "price": 15, "features": "All content + community", "allocation_pct": 0.30},
            {"name": "VIP", "price": 50, "features": "1-on-1 access + perks", "allocation_pct": 0.10}
        ]
        
        results = []
        total_revenue = Decimal("0")
        
        for tier in tiers:
            tier_members = int(member_count * tier["allocation_pct"])
            tier_revenue = Decimal(tier_members) * Decimal(tier["price"])
            total_revenue += tier_revenue
            
            results.append({
                "tier": tier["name"],
                "price": tier["price"],
                "members": tier_members,
                "monthly_revenue": float(tier_revenue),
                "features": tier["features"]
            })
        
        # Platform fees (assume 10% for membership platforms)
        net_revenue = total_revenue * Decimal("0.90")
        
        return {
            "tiers": results,
            "total_members": member_count,
            "gross_monthly": float(total_revenue),
            "net_monthly": float(net_revenue),
            "arpau": float(total_revenue / member_count) if member_count > 0 else 0,  # Average revenue per active user
            "annual_run_rate": float(net_revenue * 12)
        }
    
    def compare_platforms(self, product_price: Decimal = Decimal("29.99"),
                         monthly_volume: int = 100) -> List[Dict]:
        """Compare all monetization platforms"""
        comparisons = []
        
        for platform in [Platform.GUMROAD, Platform.LEMONSQUEEZY, Platform.PAYHIP,
                        Platform.TEACHABLE, Platform.TEACHABLE]:
            fees = self.platform_fees.get(platform, {})
            gross = product_price * Decimal(monthly_volume)
            
            fee_pct = fees.get("fee_pct", Decimal("0.10"))
            processing = Decimal("0.029")
            monthly = fees.get("monthly", Decimal("0"))
            
            platform_cut = gross * fee_pct
            processing_cost = gross * processing
            
            total_fees = platform_cut + processing_cost + monthly
            net = gross - total_fees
            
            comparisons.append({
                "platform": platform.value,
                "gross_revenue": float(gross),
                "platform_fees": float(platform_cut),
                "processing": float(processing_cost),
                "subscription": float(monthly),
                "total_fees": float(total_fees),
                "net_revenue": float(net),
                "take_home_pct": float(net / gross * 100) if gross > 0 else 0,
                "best_for": self._get_platform_best_for(platform)
            })
        
        return sorted(comparisons, key=lambda x: x["net_revenue"], reverse=True)
    
    def _get_platform_best_for(self, platform: Platform) -> str:
        mapping = {
            Platform.GUMROAD: "Digital downloads, ebooks, simple setup",
            Platform.LEMONSQUEEZY: "SaaS, software, lower fees",
            Platform.PAYHIP: "Courses, memberships, no monthly fee",
            Platform.TEACHABLE: "Full-featured courses, marketing tools",
            Platform.THINKIFIC: "Course creators, zero transaction fees",
            Platform.KAJABI: "All-in-one, premium pricing",
            Platform.SKOOL: "Community + courses combined"
        }
        return mapping.get(platform, "General digital products")
    
    def bundle_strategy(self, products: List[Dict]) -> Dict:
        """Calculate bundle pricing strategy"""
        # Bundle psychology: 20-30% discount increases perceived value
        
        individual_prices = [p["price"] for p in products]
        total_individual = sum(individual_prices)
        
        # Offer 25% bundle discount
        bundle_discount = Decimal("0.25")
        bundle_price = Decimal(total_individual) * (Decimal("1") - bundle_discount)
        
        # Bundle typically increases conversion by 40%
        base_conversion = 0.02  # 2%
        bundle_conversion = base_conversion * 1.4
        
        # Estimate traffic needed
        monthly_bundle_sales = 50
        traffic_needed = int(monthly_bundle_sales / bundle_conversion)
        
        return {
            "products_in_bundle": len(products),
            "individual_total": float(total_individual),
            "bundle_price": float(bundle_price),
            "discount_pct": float(bundle_discount * 100),
            "customer_savings": float(total_individual - bundle_price),
            "estimated_conversion_rate": bundle_conversion,
            "monthly_sales_target": monthly_bundle_sales,
            "traffic_needed": traffic_needed,
            "monthly_revenue": float(bundle_price * Decimal(monthly_bundle_sales)),
            "strategy": "Position as 'starter pack' or 'complete toolkit'"
        }
