"""
Copy Trading System API Routes
FastAPI endpoints for social copy trading
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel

from .copy_trading import CopyTradingSystem

router = APIRouter(prefix="/copy-trading", tags=["Copy Trading"])

# Initialize system
copy_system = CopyTradingSystem()


class RegisterTraderRequest(BaseModel):
    user_id: str
    display_name: str
    bio: str
    strategy_description: str = ""


class StartCopyingRequest(BaseModel):
    copier_id: str
    trader_id: str
    allocation: float
    risk_settings: Optional[Dict] = None


class UpdateCopySettingsRequest(BaseModel):
    copier_id: str
    trader_id: str
    settings: Dict


class CreateSignalRequest(BaseModel):
    trader_id: str
    symbol: str
    side: str
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size_pct: float = 5.0
    rationale: str = ""
    confidence: str = "medium"


@router.get("/traders")
async def discover_traders(
    sort_by: str = "performance",
    min_return_30d: Optional[float] = None,
    max_risk: Optional[str] = None,
    trading_style: Optional[str] = None,
    verified_only: bool = False,
    limit: int = 20
):
    """Discover top traders to copy"""
    return copy_system.discover_traders(
        sort_by=sort_by,
        min_return_30d=min_return_30d,
        max_risk=max_risk,
        trading_style=trading_style,
        verified_only=verified_only,
        limit=limit
    )


@router.get("/traders/{trader_id}")
async def get_trader(trader_id: str):
    """Get trader profile"""
    trader = copy_system.get_trader(trader_id)
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    return trader


@router.post("/traders/register")
async def register_trader(request: RegisterTraderRequest):
    """Register as a trader"""
    trader = copy_system.register_trader(
        user_id=request.user_id,
        display_name=request.display_name,
        bio=request.bio,
        strategy_description=request.strategy_description
    )
    return trader.to_dict()


@router.get("/traders/{trader_id}/dashboard")
async def get_trader_dashboard(trader_id: str):
    """Get trader's copy trading dashboard"""
    return copy_system.get_trader_dashboard(trader_id)


@router.post("/copy/start")
async def start_copying(request: StartCopyingRequest):
    """Start copying a trader"""
    result = copy_system.start_copying(
        copier_id=request.copier_id,
        trader_id=request.trader_id,
        allocation=request.allocation,
        risk_settings=request.risk_settings
    )
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result


@router.post("/copy/{copier_id}/stop/{trader_id}")
async def stop_copying(copier_id: str, trader_id: str):
    """Stop copying a trader"""
    success = copy_system.stop_copying(copier_id, trader_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop copying")
    return {'success': True}


@router.post("/copy/{copier_id}/pause/{trader_id}")
async def pause_copying(copier_id: str, trader_id: str):
    """Pause copying (keep existing positions)"""
    success = copy_system.pause_copying(copier_id, trader_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to pause copying")
    return {'success': True}


@router.post("/copy/{copier_id}/resume/{trader_id}")
async def resume_copying(copier_id: str, trader_id: str):
    """Resume paused copying"""
    success = copy_system.resume_copying(copier_id, trader_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to resume copying")
    return {'success': True}


@router.put("/copy/settings")
async def update_copy_settings(request: UpdateCopySettingsRequest):
    """Update copy relationship settings"""
    success = copy_system.update_copy_settings(
        copier_id=request.copier_id,
        trader_id=request.trader_id,
        settings=request.settings
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update settings")
    return {'success': True}


@router.get("/copiers/{copier_id}/dashboard")
async def get_copier_dashboard(copier_id: str):
    """Get copier's copy trading dashboard"""
    return copy_system.get_copier_dashboard(copier_id)


@router.post("/traders/{trader_id}/signals")
async def create_trade_signal(trader_id: str, request: CreateSignalRequest):
    """Trader creates a new trade signal"""
    signal = copy_system.create_trade_signal(
        trader_id=trader_id,
        signal=request.dict()
    )
    return signal.to_dict()


@router.get("/leaderboard")
async def get_leaderboard(period: str = "30d", limit: int = 10):
    """Get top traders leaderboard"""
    return {'leaderboard': copy_system.get_leaderboard(period, limit)}
