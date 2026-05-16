"""
Bot Manager API Routes
FastAPI endpoints for DCA, Grid, and TWAP bots
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel

from .bot_manager import BotManager

router = APIRouter(prefix="/bots", tags=["Trading Bots"])

# Initialize bot manager
bot_manager = BotManager()


class CreateDCABotRequest(BaseModel):
    user_id: str
    name: str
    symbol: str
    total_investment: float
    entry_price: float
    num_orders: int = 10
    price_drop_pct: float = 5.0
    take_profit_pct: float = 10.0


class CreateGridBotRequest(BaseModel):
    user_id: str
    name: str
    symbol: str
    total_investment: float
    lower_price: float
    upper_price: float
    num_grids: int = 10


class CreateTWAPBotRequest(BaseModel):
    user_id: str
    name: str
    symbol: str
    total_quantity: float
    side: str
    duration_minutes: int = 60
    num_slices: int = 12


@router.post("/dca")
async def create_dca_bot(request: CreateDCABotRequest):
    """Create a new DCA bot"""
    config = {
        'symbol': request.symbol,
        'total_investment': request.total_investment,
        'entry_price': request.entry_price,
        'num_orders': request.num_orders,
        'price_drop_pct': request.price_drop_pct,
        'take_profit_pct': request.take_profit_pct
    }
    bot = bot_manager.create_dca_bot(request.user_id, request.name, config)
    return bot.to_dict()


@router.post("/grid")
async def create_grid_bot(request: CreateGridBotRequest):
    """Create a new Grid Trading bot"""
    config = {
        'symbol': request.symbol,
        'total_investment': request.total_investment,
        'lower_price': request.lower_price,
        'upper_price': request.upper_price,
        'num_grids': request.num_grids
    }
    bot = bot_manager.create_grid_bot(request.user_id, request.name, config)
    return bot.to_dict()


@router.post("/twap")
async def create_twap_bot(request: CreateTWAPBotRequest):
    """Create a new TWAP execution bot"""
    config = {
        'symbol': request.symbol,
        'total_quantity': request.total_quantity,
        'side': request.side,
        'duration_minutes': request.duration_minutes,
        'num_slices': request.num_slices
    }
    bot = bot_manager.create_twap_bot(request.user_id, request.name, config)
    return bot.to_dict()


@router.get("/")
async def list_bots(user_id: str, bot_type: str = None, status: str = None):
    """List all bots for a user"""
    return {'bots': bot_manager.list_user_bots(user_id, bot_type, status)}


@router.get("/{bot_id}")
async def get_bot(bot_id: str):
    """Get bot details"""
    bot = bot_manager.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot


@router.post("/{bot_id}/start")
async def start_bot(bot_id: str):
    """Start a bot"""
    success = bot_manager.start_bot(bot_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start bot")
    return {'success': True, 'status': 'running'}


@router.post("/{bot_id}/pause")
async def pause_bot(bot_id: str):
    """Pause a bot"""
    success = bot_manager.pause_bot(bot_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to pause bot")
    return {'success': True, 'status': 'paused'}


@router.post("/{bot_id}/stop")
async def stop_bot(bot_id: str, close_positions: bool = False):
    """Stop a bot"""
    success = bot_manager.stop_bot(bot_id, close_positions)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop bot")
    return {'success': True, 'status': 'stopped'}


@router.get("/{bot_id}/stats")
async def get_bot_stats(bot_id: str):
    """Get bot statistics"""
    stats = bot_manager.get_bot_stats(bot_id)
    if 'error' in stats:
        raise HTTPException(status_code=404, detail=stats['error'])
    return stats


@router.post("/{bot_id}/duplicate")
async def duplicate_bot(bot_id: str, new_name: str):
    """Duplicate an existing bot"""
    new_bot = bot_manager.duplicate_bot(bot_id, new_name)
    if not new_bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return new_bot.to_dict()


@router.get("/{bot_id}/dca-levels")
async def get_dca_levels(bot_id: str):
    """Get DCA entry levels"""
    levels = bot_manager.calculate_dca_levels(bot_id)
    return {'levels': levels}


@router.get("/{bot_id}/grid-levels")
async def get_grid_levels(bot_id: str):
    """Get Grid levels"""
    levels = bot_manager.calculate_grid_levels(bot_id)
    return {'levels': levels}


@router.get("/summary/active")
async def get_active_bots_summary():
    """Get summary of active bots"""
    return bot_manager.get_active_bots_summary()
