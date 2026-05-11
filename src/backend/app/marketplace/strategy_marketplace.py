"""
Strategy Marketplace for Veyra
Buy, sell, and share trading strategies

Features:
- Strategy listings with performance metrics
- Purchase and licensing system
- Creator revenue sharing
- Rating and review system
- Strategy analytics
- Copy trading integration
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class ListingStatus(Enum):
    """Marketplace listing status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    PAUSED = "paused"
    SOLD_OUT = "sold_out"
    DELISTED = "delisted"


class LicenseType(Enum):
    """Strategy license types"""
    PERSONAL = "personal"  # Single user
    COMMERCIAL = "commercial"  # Multiple users/business
    WHITE_LABEL = "white_label"  # Rebrand and resell
    SUBSCRIPTION = "subscription"  # Monthly access


@dataclass
class StrategyListing:
    """A strategy listed on the marketplace"""
    id: str
    strategy_id: str
    creator_id: str
    creator_name: str
    
    # Listing details
    name: str
    description: str
    short_description: str
    category: str
    tags: List[str] = field(default_factory=list)
    
    # Pricing
    price: float
    original_price: Optional[float] = None  # For sales
    license_type: LicenseType = LicenseType.PERSONAL
    currency: str = "USD"
    
    # Performance metrics
    total_return: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    total_trades: int = 0
    avg_trade_duration: str = ""
    backtest_period: str = ""
    
    # Marketplace stats
    sales_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    views: int = 0
    favorites: int = 0
    
    # Status
    status: ListingStatus = ListingStatus.DRAFT
    created_at: datetime = None
    updated_at: datetime = None
    published_at: Optional[datetime] = None
    
    # Content
    preview_code: Optional[str] = None
    documentation: Optional[str] = None
    video_url: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    
    # Configuration
    supported_pairs: List[str] = field(default_factory=list)
    recommended_timeframes: List[str] = field(default_factory=list)
    min_capital: float = 0.0
    risk_level: str = "medium"  # low, medium, high
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'creator_id': self.creator_id,
            'creator_name': self.creator_name,
            'name': self.name,
            'description': self.description,
            'short_description': self.short_description,
            'category': self.category,
            'tags': self.tags,
            'price': self.price,
            'original_price': self.original_price,
            'license_type': self.license_type.value,
            'currency': self.currency,
            'performance': {
                'total_return': self.total_return,
                'win_rate': self.win_rate,
                'profit_factor': self.profit_factor,
                'sharpe_ratio': self.sharpe_ratio,
                'max_drawdown': self.max_drawdown,
                'total_trades': self.total_trades,
                'avg_trade_duration': self.avg_trade_duration,
                'backtest_period': self.backtest_period
            },
            'stats': {
                'sales': self.sales_count,
                'rating': self.rating,
                'reviews': self.review_count,
                'views': self.views,
                'favorites': self.favorites
            },
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'configuration': {
                'supported_pairs': self.supported_pairs,
                'timeframes': self.recommended_timeframes,
                'min_capital': self.min_capital,
                'risk_level': self.risk_level
            }
        }


@dataclass
class Review:
    """Strategy review/rating"""
    id: str
    listing_id: str
    user_id: str
    user_name: str
    rating: int  # 1-5
    title: str
    content: str
    created_at: datetime = None
    helpful_count: int = 0
    verified_purchase: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'helpful_count': self.helpful_count,
            'verified_purchase': self.verified_purchase
        }


@dataclass
class Purchase:
    """Strategy purchase record"""
    id: str
    listing_id: str
    buyer_id: str
    seller_id: str
    price_paid: float
    license_type: LicenseType
    status: str = "completed"  # pending, completed, refunded, disputed
    created_at: datetime = None
    strategy_access_key: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if not self.strategy_access_key:
            self.strategy_access_key = str(uuid.uuid4())


@dataclass
class CreatorProfile:
    """Strategy creator profile"""
    user_id: str
    display_name: str
    bio: str
    avatar_url: Optional[str] = None
    
    # Stats
    total_listings: int = 0
    total_sales: int = 0
    total_revenue: float = 0.0
    average_rating: float = 0.0
    follower_count: int = 0
    
    # Verification
    verified: bool = False
    top_seller: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'stats': {
                'listings': self.total_listings,
                'sales': self.total_sales,
                'revenue': self.total_revenue,
                'rating': self.average_rating,
                'followers': self.follower_count
            },
            'badges': {
                'verified': self.verified,
                'top_seller': self.top_seller
            }
        }


class StrategyMarketplace:
    """
    Strategy Marketplace backend
    Handles listings, purchases, reviews, and creator management
    """
    
    # Revenue sharing config
    PLATFORM_FEE_PCT = 0.20  # 20% platform fee
    CREATOR_PCT = 0.80  # 80% to creator
    
    def __init__(self):
        self.listings: Dict[str, StrategyListing] = {}
        self.reviews: Dict[str, List[Review]] = {}  # listing_id -> reviews
        self.purchases: Dict[str, Purchase] = {}
        self.creators: Dict[str, CreatorProfile] = {}
        self.user_purchases: Dict[str, List[str]] = {}  # user_id -> purchase_ids
        
        # Categories
        self.categories = [
            "Trend Following",
            "Mean Reversion",
            "Momentum",
            "Breakout",
            "Scalping",
            "Swing Trading",
            "Day Trading",
            "Options",
            "Crypto",
            "Forex",
            "Stocks",
            "Multi-Asset"
        ]
    
    def create_listing(self, creator_id: str, creator_name: str, 
                      strategy_id: str, name: str, description: str,
                      price: float, category: str) -> StrategyListing:
        """Create a new marketplace listing"""
        
        listing = StrategyListing(
            id=str(uuid.uuid4()),
            strategy_id=strategy_id,
            creator_id=creator_id,
            creator_name=creator_name,
            name=name,
            description=description,
            short_description=description[:150] + "..." if len(description) > 150 else description,
            category=category,
            price=price,
            license_type=LicenseType.PERSONAL,
            status=ListingStatus.DRAFT
        )
        
        self.listings[listing.id] = listing
        
        # Update creator stats
        creator = self.creators.get(creator_id)
        if creator:
            creator.total_listings += 1
        else:
            self.creators[creator_id] = CreatorProfile(
                user_id=creator_id,
                display_name=creator_name,
                bio="",
                total_listings=1
            )
        
        logger.info(f"Created listing: {listing.id}")
        return listing
    
    def publish_listing(self, listing_id: str) -> bool:
        """Publish a listing to the marketplace"""
        listing = self.listings.get(listing_id)
        if not listing:
            return False
        
        # Validate listing has required fields
        if not listing.name or listing.price < 0:
            return False
        
        listing.status = ListingStatus.ACTIVE
        listing.published_at = datetime.now()
        listing.updated_at = datetime.now()
        
        logger.info(f"Published listing: {listing_id}")
        return True
    
    def update_listing_performance(self, listing_id: str, 
                                    performance: Dict[str, Any]) -> bool:
        """Update listing with backtest/live performance metrics"""
        listing = self.listings.get(listing_id)
        if not listing:
            return False
        
        listing.total_return = performance.get('total_return', 0)
        listing.win_rate = performance.get('win_rate', 0)
        listing.profit_factor = performance.get('profit_factor', 0)
        listing.sharpe_ratio = performance.get('sharpe_ratio', 0)
        listing.max_drawdown = performance.get('max_drawdown', 0)
        listing.total_trades = performance.get('total_trades', 0)
        listing.avg_trade_duration = performance.get('avg_trade_duration', '')
        listing.backtest_period = performance.get('backtest_period', '')
        listing.updated_at = datetime.now()
        
        return True
    
    def get_listing(self, listing_id: str, increment_view: bool = True) -> Optional[Dict]:
        """Get listing details"""
        listing = self.listings.get(listing_id)
        if not listing:
            return None
        
        if increment_view and listing.status == ListingStatus.ACTIVE:
            listing.views += 1
        
        return listing.to_dict()
    
    def search_listings(self, 
                       query: str = None,
                       category: str = None,
                       min_price: float = None,
                       max_price: float = None,
                       min_rating: float = None,
                       sort_by: str = "popular",
                       limit: int = 20) -> List[Dict]:
        """Search and filter marketplace listings"""
        
        results = list(self.listings.values())
        
        # Filter by status
        results = [l for l in results if l.status == ListingStatus.ACTIVE]
        
        # Text search
        if query:
            query_lower = query.lower()
            results = [
                l for l in results 
                if (query_lower in l.name.lower() or 
                    query_lower in l.description.lower() or
                    any(query_lower in tag.lower() for tag in l.tags))
            ]
        
        # Category filter
        if category:
            results = [l for l in results if l.category == category]
        
        # Price filter
        if min_price is not None:
            results = [l for l in results if l.price >= min_price]
        if max_price is not None:
            results = [l for l in results if l.price <= max_price]
        
        # Rating filter
        if min_rating is not None:
            results = [l for l in results if l.rating >= min_rating]
        
        # Sorting
        if sort_by == "price_low":
            results.sort(key=lambda l: l.price)
        elif sort_by == "price_high":
            results.sort(key=lambda l: l.price, reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda l: l.rating, reverse=True)
        elif sort_by == "newest":
            results.sort(key=lambda l: l.published_at or l.created_at, reverse=True)
        else:  # popular - by sales
            results.sort(key=lambda l: l.sales_count, reverse=True)
        
        return [l.to_dict() for l in results[:limit]]
    
    def purchase_strategy(self, listing_id: str, buyer_id: str) -> Dict:
        """Process strategy purchase"""
        listing = self.listings.get(listing_id)
        if not listing:
            return {'error': 'Listing not found'}
        
        if listing.status != ListingStatus.ACTIVE:
            return {'error': 'Listing not available'}
        
        # Check if already purchased
        user_purchases = self.user_purchases.get(buyer_id, [])
        for purchase_id in user_purchases:
            purchase = self.purchases.get(purchase_id)
            if purchase and purchase.listing_id == listing_id:
                return {'error': 'Already purchased'}
        
        # Create purchase record
        purchase = Purchase(
            id=str(uuid.uuid4()),
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=listing.creator_id,
            price_paid=listing.price,
            license_type=listing.license_type
        )
        
        self.purchases[purchase.id] = purchase
        
        # Track user purchase
        if buyer_id not in self.user_purchases:
            self.user_purchases[buyer_id] = []
        self.user_purchases[buyer_id].append(purchase.id)
        
        # Update listing stats
        listing.sales_count += 1
        
        # Update creator revenue
        creator = self.creators.get(listing.creator_id)
        if creator:
            creator.total_sales += 1
            creator.total_revenue += listing.price * self.CREATOR_PCT
        
        logger.info(f"Purchase completed: {purchase.id} for listing {listing_id}")
        
        return {
            'success': True,
            'purchase_id': purchase.id,
            'access_key': purchase.strategy_access_key,
            'download_url': f"/api/marketplace/strategies/{listing.strategy_id}/download?key={purchase.strategy_access_key}"
        }
    
    def add_review(self, listing_id: str, user_id: str, user_name: str,
                  rating: int, title: str, content: str) -> Review:
        """Add a review to a listing"""
        
        # Verify purchase
        user_purchases = self.user_purchases.get(user_id, [])
        verified = any(
            self.purchases.get(pid) and 
            self.purchases[pid].listing_id == listing_id
            for pid in user_purchases
        )
        
        review = Review(
            id=str(uuid.uuid4()),
            listing_id=listing_id,
            user_id=user_id,
            user_name=user_name,
            rating=max(1, min(5, rating)),  # Clamp to 1-5
            title=title,
            content=content,
            verified_purchase=verified
        )
        
        # Add to listing reviews
        if listing_id not in self.reviews:
            self.reviews[listing_id] = []
        self.reviews[listing_id].append(review)
        
        # Update listing rating
        listing = self.listings.get(listing_id)
        if listing:
            listing.review_count = len(self.reviews[listing_id])
            listing.rating = sum(r.rating for r in self.reviews[listing_id]) / listing.review_count
        
        logger.info(f"Added review: {review.id} for listing {listing_id}")
        return review
    
    def get_reviews(self, listing_id: str, limit: int = 10) -> List[Dict]:
        """Get reviews for a listing"""
        reviews = self.reviews.get(listing_id, [])
        # Sort by verified first, then by date
        reviews.sort(key=lambda r: (not r.verified_purchase, r.created_at), reverse=True)
        return [r.to_dict() for r in reviews[:limit]]
    
    def get_user_library(self, user_id: str) -> List[Dict]:
        """Get all strategies purchased by user"""
        purchase_ids = self.user_purchases.get(user_id, [])
        library = []
        
        for purchase_id in purchase_ids:
            purchase = self.purchases.get(purchase_id)
            if purchase:
                listing = self.listings.get(purchase.listing_id)
                if listing:
                    library.append({
                        'purchase_id': purchase.id,
                        'purchase_date': purchase.created_at.isoformat(),
                        'listing': listing.to_dict(),
                        'access_key': purchase.strategy_access_key
                    })
        
        return library
    
    def get_creator_profile(self, creator_id: str) -> Optional[Dict]:
        """Get creator profile with their listings"""
        creator = self.creators.get(creator_id)
        if not creator:
            return None
        
        # Get creator's listings
        creator_listings = [
            l.to_dict() for l in self.listings.values()
            if l.creator_id == creator_id and l.status == ListingStatus.ACTIVE
        ]
        
        profile = creator.to_dict()
        profile['listings'] = creator_listings
        
        return profile
    
    def get_featured_listings(self, limit: int = 6) -> List[Dict]:
        """Get featured/top listings"""
        active = [l for l in self.listings.values() if l.status == ListingStatus.ACTIVE]
        
        # Score listings by popularity + rating
        def score(l):
            return (l.sales_count * 2 + l.views * 0.01 + l.rating * 10 + l.favorites * 5)
        
        active.sort(key=score, reverse=True)
        
        return [l.to_dict() for l in active[:limit]]
    
    def get_new_arrivals(self, limit: int = 6) -> List[Dict]:
        """Get newest listings"""
        active = [l for l in self.listings.values() if l.status == ListingStatus.ACTIVE]
        active.sort(key=lambda l: l.published_at or l.created_at, reverse=True)
        return [l.to_dict() for l in active[:limit]]
    
    def get_top_rated(self, limit: int = 6) -> List[Dict]:
        """Get top rated listings"""
        active = [l for l in self.listings.values() 
                 if l.status == ListingStatus.ACTIVE and l.review_count >= 3]
        active.sort(key=lambda l: l.rating, reverse=True)
        return [l.to_dict() for l in active[:limit]]
    
    def get_categories_with_counts(self) -> List[Dict]:
        """Get categories with listing counts"""
        counts = {}
        for listing in self.listings.values():
            if listing.status == ListingStatus.ACTIVE:
                counts[listing.category] = counts.get(listing.category, 0) + 1
        
        return [
            {'name': cat, 'count': counts.get(cat, 0)}
            for cat in self.categories
        ]
    
    def toggle_favorite(self, listing_id: str, user_id: str) -> bool:
        """Toggle favorite status (simplified - would need user prefs storage)"""
        listing = self.listings.get(listing_id)
        if not listing:
            return False
        
        # In production, this would check if user already favorited
        listing.favorites += 1
        return True
