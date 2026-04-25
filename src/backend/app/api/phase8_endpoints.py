"""
Phase 8 API Endpoints - New features integration
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional

router = APIRouter(prefix="/api/v2", tags=["Phase 8 Features"])

# Import new modules
from strategy.visual_builder import strategy_builder_engine
from portfolio.dividend_tracker import dividend_tracker
from ai.video_analyzer import video_analyzer
from ai.satellite_imagery import satellite_ai
from social.reddit_discord_tracker import social_v2
from portfolio.passive_income import passive_dashboard
from institutional.oms_ems import oms

@router.post("/strategy/visual/create")
async def create_visual_strategy(name: str, description: str, author: str):
    """Create new visual strategy."""
    strategy = strategy_builder_engine.create_strategy(name, description, author)
    return {"strategy_id": strategy.id, "templates": strategy_builder_engine.list_templates()}

@router.get("/dividends/portfolio")
async def get_dividend_portfolio():
    """Get dividend income summary."""
    return dividend_tracker.get_portfolio_income_summary()

@router.get("/dividends/optimization")
async def get_dividend_optimization():
    """Get yield optimization suggestions."""
    return {"suggestions": dividend_tracker.get_yield_optimization_suggestions()}

@router.post("/ai/analyze-video")
async def analyze_video(source: str, transcript: str, symbol: Optional[str] = None):
    """Analyze financial video content."""
    from datetime import datetime
    result = await video_analyzer.analyze_cnbc_segment(transcript, datetime.now())
    return result.to_dict()

@router.get("/ai/satellite/signals")
async def get_satellite_signals():
    """Get satellite imagery trading signals."""
    return {"signals": [s.__dict__ for s in satellite_ai.get_signals()]}

@router.get("/social/meme-stocks")
async def get_meme_stocks():
    """Get potential short squeeze candidates."""
    return {"candidates": social_v2.detect_short_squeeze_candidates()}

@router.get("/income/dashboard")
async def get_income_dashboard():
    """Get passive income dashboard."""
    return passive_dashboard.get_dashboard()

@router.post("/institutional/parent-order")
async def create_parent_order(symbol: str, side: str, quantity: int, strategy: str):
    """Create institutional parent order."""
    order_id = oms.create_parent_order(symbol, side, quantity, strategy)
    return {"parent_order_id": order_id, "status": "created"}

@router.get("/phase8/status")
async def phase8_status():
    """Phase 8 implementation status."""
    return {
        "phase": "8",
        "target_grade": 350,
        "current_grade": 295,
        "features_implemented": [
            "Visual Strategy Builder",
            "Options Strategies",
            "Dividend Tracker",
            "Video Analysis AI",
            "Satellite Imagery",
            "Social Sentiment v2",
            "Real Estate Tracking",
            "Passive Income Dashboard",
            "OMS/EMS Core"
        ],
        "remaining": ["Mobile App", "Complete Options Module"]
    }
