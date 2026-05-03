"""
MetaTrader Integration API Routes
FastAPI endpoints for MT4/MT5 connection
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel

from .metatrader_integration import MetaTraderIntegration

router = APIRouter(prefix="/metatrader", tags=["MetaTrader Integration"])

# Initialize MT integration
mt_integration = MetaTraderIntegration()


class AddAccountRequest(BaseModel):
    user_id: str
    name: str
    version: int  # 4 or 5
    account_type: str  # demo or live
    host: str = "localhost"
    port: int = 15555


class ConfigureEARequest(BaseModel):
    account_id: str
    name: str
    magic_number: int
    strategy_type: str = ""
    timeframe: str = "H1"
    symbols: List[str] = []
    risk_per_trade_pct: float = 1.0
    max_daily_trades: int = 10
    use_trailing_stop: bool = False


class SignalRequest(BaseModel):
    account_id: str
    action: str
    symbol: str
    volume: float
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    magic_number: int = 0
    comment: str = ""
    ea_name: str = ""


@router.post("/accounts")
async def add_account(request: AddAccountRequest):
    """Add MetaTrader account"""
    account = mt_integration.add_account(
        user_id=request.user_id,
        name=request.name,
        version=request.version,
        account_type=request.account_type,
        host=request.host,
        port=request.port
    )
    return account.to_dict()


@router.get("/accounts")
async def list_accounts(user_id: str):
    """List user's MetaTrader accounts"""
    return {'accounts': mt_integration.list_user_accounts(user_id)}


@router.get("/accounts/{account_id}")
async def get_account(account_id: str):
    """Get account details"""
    account = mt_integration.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.get("/accounts/{account_id}/summary")
async def get_account_summary(account_id: str):
    """Get account summary with positions and signals"""
    return mt_integration.get_account_summary(account_id)


@router.post("/accounts/{account_id}/update-status")
async def update_connection_status(account_id: str, status: str, error: str = None):
    """Update account connection status"""
    success = mt_integration.update_connection_status(account_id, status, error)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {'success': True}


@router.post("/accounts/{account_id}/update-info")
async def update_account_info(account_id: str, info: Dict):
    """Update account information from MT"""
    success = mt_integration.update_account_info(account_id, info)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {'success': True}


@router.post("/accounts/{account_id}/update-positions")
async def update_positions(account_id: str, positions: List[Dict]):
    """Update positions from MT"""
    success = mt_integration.update_positions(account_id, positions)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {'success': True}


@router.get("/accounts/{account_id}/positions")
async def get_positions(account_id: str):
    """Get current positions"""
    return {'positions': mt_integration.get_positions(account_id)}


@router.get("/accounts/{account_id}/orders")
async def get_pending_orders(account_id: str):
    """Get pending orders"""
    return {'orders': mt_integration.get_pending_orders(account_id)}


@router.post("/eas")
async def configure_ea(request: ConfigureEARequest):
    """Configure Expert Advisor"""
    ea = mt_integration.configure_ea(
        account_id=request.account_id,
        name=request.name,
        magic_number=request.magic_number,
        config={
            'strategy_type': request.strategy_type,
            'timeframe': request.timeframe,
            'symbols': request.symbols,
            'risk_per_trade_pct': request.risk_per_trade_pct,
            'max_daily_trades': request.max_daily_trades,
            'use_trailing_stop': request.use_trailing_stop
        }
    )
    return ea.to_dict()


@router.get("/accounts/{account_id}/eas")
async def list_eas(account_id: str):
    """List EAs for an account"""
    return {'eas': mt_integration.list_account_eas(account_id)}


@router.get("/eas/{ea_id}")
async def get_ea_config(ea_id: str):
    """Get EA configuration"""
    ea = mt_integration.get_ea_config(ea_id)
    if not ea:
        raise HTTPException(status_code=404, detail="EA not found")
    return ea


@router.get("/eas/{ea_id}/code")
async def generate_ea_code(ea_id: str):
    """Generate MQL4/5 code for EA"""
    code = mt_integration.generate_mt_code(ea_id)
    if not code:
        raise HTTPException(status_code=404, detail="EA not found")
    return {'code': code}


@router.post("/signals")
async def receive_signal(request: SignalRequest):
    """Receive trade signal from MT EA"""
    signal = mt_integration.receive_signal(
        account_id=request.account_id,
        signal_data=request.dict()
    )
    return signal.to_dict()


@router.get("/accounts/{account_id}/signals")
async def get_signals(account_id: str, unprocessed_only: bool = False, limit: int = 100):
    """Get signals for an account"""
    return {'signals': mt_integration.get_signals(account_id, unprocessed_only, limit)}


@router.post("/signals/{signal_id}/process")
async def process_signal(signal_id: str, result: str):
    """Mark signal as processed"""
    success = mt_integration.process_signal(signal_id, result)
    if not success:
        raise HTTPException(status_code=404, detail="Signal not found")
    return {'success': True}
