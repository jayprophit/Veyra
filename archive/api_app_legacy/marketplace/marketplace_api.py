"""
Strategy Marketplace API Routes
FastAPI endpoints for buying and selling strategies
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel

from .strategy_marketplace import StrategyMarketplace, ListingStatus

router = APIRouter(prefix="/marketplace", tags=["Strategy Marketplace"])

# Initialize marketplace
marketplace = StrategyMarketplace()


class CreateListingRequest(BaseModel):
    creator_id: str
    creator_name: str
    strategy_id: str
    name: str
    description: str
    price: float
    category: str


class UpdatePerformanceRequest(BaseModel):
    total_return: float = 0
    win_rate: float = 0
    profit_factor: float = 0
    sharpe_ratio: float = 0
    max_drawdown: float = 0
    total_trades: int = 0
    avg_trade_duration: str = ""
    backtest_period: str = ""


class PurchaseRequest(BaseModel):
    listing_id: str
    buyer_id: str


class ReviewRequest(BaseModel):
    listing_id: str
    user_id: str
    user_name: str
    rating: int
    title: str
    content: str


@router.get("/listings")
async def search_listings(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "popular",
    limit: int = 20
):
    """Search and filter marketplace listings"""
    return marketplace.search_listings(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by,
        limit=limit
    )


@router.get("/listings/{listing_id}")
async def get_listing(listing_id: str):
    """Get listing details"""
    listing = marketplace.get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post("/listings")
async def create_listing(request: CreateListingRequest):
    """Create a new marketplace listing"""
    listing = marketplace.create_listing(
        creator_id=request.creator_id,
        creator_name=request.creator_name,
        strategy_id=request.strategy_id,
        name=request.name,
        description=request.description,
        price=request.price,
        category=request.category
    )
    return listing.to_dict()


@router.post("/listings/{listing_id}/publish")
async def publish_listing(listing_id: str):
    """Publish listing to marketplace"""
    success = marketplace.publish_listing(listing_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to publish listing")
    return {'success': True}


@router.put("/listings/{listing_id}/performance")
async def update_performance(listing_id: str, request: UpdatePerformanceRequest):
    """Update listing performance metrics"""
    success = marketplace.update_listing_performance(listing_id, request.dict())
    if not success:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {'success': True}


@router.post("/purchase")
async def purchase_strategy(request: PurchaseRequest):
    """Purchase a strategy"""
    result = marketplace.purchase_strategy(
        listing_id=request.listing_id,
        buyer_id=request.buyer_id
    )
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result


@router.get("/users/{user_id}/library")
async def get_user_library(user_id: str):
    """Get user's purchased strategies"""
    return {'library': marketplace.get_user_library(user_id)}


@router.post("/reviews")
async def add_review(request: ReviewRequest):
    """Add a review to a listing"""
    review = marketplace.add_review(
        listing_id=request.listing_id,
        user_id=request.user_id,
        user_name=request.user_name,
        rating=request.rating,
        title=request.title,
        content=request.content
    )
    return review.to_dict()


@router.get("/listings/{listing_id}/reviews")
async def get_reviews(listing_id: str, limit: int = 10):
    """Get reviews for a listing"""
    return {'reviews': marketplace.get_reviews(listing_id, limit)}


@router.get("/creators/{creator_id}")
async def get_creator_profile(creator_id: str):
    """Get creator profile with their listings"""
    profile = marketplace.get_creator_profile(creator_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Creator not found")
    return profile


@router.get("/featured")
async def get_featured(limit: int = 6):
    """Get featured listings"""
    return {'listings': marketplace.get_featured_listings(limit)}


@router.get("/new-arrivals")
async def get_new_arrivals(limit: int = 6):
    """Get newest listings"""
    return {'listings': marketplace.get_new_arrivals(limit)}


@router.get("/top-rated")
async def get_top_rated(limit: int = 6):
    """Get top rated listings"""
    return {'listings': marketplace.get_top_rated(limit)}


@router.get("/categories")
async def get_categories():
    """Get all categories with listing counts"""
    return {'categories': marketplace.get_categories_with_counts()}
