"""
Comprehensive Wealth API Endpoints
ALL asset types, ALL income types, ALL jurisdictions
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import date

from ..personal.wealth_tracker import (
    get_wealth_tracker,
    AssetClass,
    IncomeType,
    WealthHolding,
    IncomeStream
)

router = APIRouter(prefix="/wealth", tags=["Comprehensive Wealth"])

# ==================== REQUEST MODELS ====================

class AddHoldingRequest(BaseModel):
    asset_class: str
    name: str
    jurisdiction: str = "uk"
    acquisition_cost: Decimal
    current_value: Decimal


class AddIncomeRequest(BaseModel):
    income_type: str
    source: str
    amount_monthly: Decimal
    is_passive: bool = False
    jurisdiction: str = "uk"


# ==================== ASSET CLASS ENDPOINTS ====================

@router.get("/asset-classes")
async def get_all_asset_classes():
    """Get ALL asset classes supported"""
    return {
        "traditional_financial": [
            {"id": "cash", "name": "Cash & Equivalents", "liquidity": "high"},
            {"id": "stocks", "name": "Stocks & Shares", "liquidity": "high"},
            {"id": "bonds", "name": "Bonds", "liquidity": "medium"},
            {"id": "etf", "name": "ETFs", "liquidity": "high"}
        ],
        "real_assets": [
            {"id": "real_estate", "name": "Real Estate", "liquidity": "low"},
            {"id": "precious_metals", "name": "Gold/Silver", "liquidity": "medium"}
        ],
        "alternative": [
            {"id": "art", "name": "Art", "liquidity": "low"},
            {"id": "wine", "name": "Wine & Whisky", "liquidity": "low"},
            {"id": "classic_cars", "name": "Classic Cars", "liquidity": "low"},
            {"id": "watches", "name": "Luxury Watches", "liquidity": "medium"}
        ],
        "digital": [
            {"id": "crypto", "name": "Cryptocurrency", "liquidity": "medium"},
            {"id": "nft", "name": "NFTs", "liquidity": "low"}
        ],
        "private_markets": [
            {"id": "private_equity", "name": "Private Equity", "liquidity": "illiquid"},
            {"id": "venture_capital", "name": "Venture Capital", "liquidity": "illiquid"},
            {"id": "hedge_funds", "name": "Hedge Funds", "liquidity": "illiquid"}
        ],
        "other": [
            {"id": "p2p_lending", "name": "P2P Lending", "liquidity": "low"},
            {"id": "business", "name": "Business Equity", "liquidity": "illiquid"},
            {"id": "pension", "name": "Pension Assets", "liquidity": "locked"},
            {"id": "commodities", "name": "Commodities", "liquidity": "medium"},
            {"id": "forex", "name": "Forex", "liquidity": "high"},
            {"id": "derivatives", "name": "Derivatives", "liquidity": "medium"},
            {"id": "intellectual_property", "name": "Intellectual Property", "liquidity": "illiquid"}
        ]
    }


@router.get("/income-types")
async def get_all_income_types():
    """Get ALL income types supported"""
    return {
        "employment": [
            {"id": "salary", "name": "Salary", "passive": False},
            {"id": "bonus", "name": "Bonus", "passive": False}
        ],
        "self_employment": [
            {"id": "freelance", "name": "Freelance Income", "passive": False},
            {"id": "consulting", "name": "Consulting", "passive": False},
            {"id": "business_profit", "name": "Business Profit", "passive": False}
        ],
        "investment_passive": [
            {"id": "dividends", "name": "Dividends", "passive": True},
            {"id": "interest", "name": "Interest", "passive": True},
            {"id": "rent", "name": "Rental Income", "passive": True},
            {"id": "capital_gains", "name": "Capital Gains", "passive": True}
        ],
        "alternative_passive": [
            {"id": "royalties", "name": "Royalties", "passive": True},
            {"id": "crypto_staking", "name": "Crypto Staking", "passive": True},
            {"id": "defi_yield", "name": "DeFi Yield", "passive": True},
            {"id": "p2p_interest", "name": "P2P Interest", "passive": True}
        ],
        "retirement": [
            {"id": "pension", "name": "Pension Income", "passive": True}
        ]
    }


# ==================== HOLDINGS ====================

@router.post("/holding/add")
async def add_holding(req: AddHoldingRequest):
    """Add any type of wealth holding"""
    manager = get_wealth_tracker()
    
    try:
        asset_class = AssetClass(req.asset_class)
    except ValueError:
        valid = [a.value for a in AssetClass]
        raise HTTPException(400, f"Invalid asset class. Valid: {valid}")
    
    holding = WealthHolding(
        holding_id="",
        asset_class=asset_class,
        name=req.name,
        jurisdiction=req.jurisdiction,
        acquisition_cost=req.acquisition_cost,
        current_value=req.current_value,
        unrealized_gain_loss=req.current_value - req.acquisition_cost
    )
    
    holding_id = manager.add_holding(holding)
    
    return {
        "holding_id": holding_id,
        "asset_class": req.asset_class,
        "name": req.name,
        "jurisdiction": req.jurisdiction,
        "unrealized_gain_loss": float(holding.unrealized_gain_loss)
    }


@router.get("/holdings/list")
async def list_holdings(
    asset_class: Optional[str] = None,
    jurisdiction: Optional[str] = None
):
    """List all holdings with filters"""
    manager = get_wealth_tracker()
    
    holdings = list(manager.holdings.values())
    
    if asset_class:
        holdings = [h for h in holdings if h.asset_class.value == asset_class]
    if jurisdiction:
        holdings = [h for h in holdings if h.jurisdiction == jurisdiction]
    
    return {
        "count": len(holdings),
        "holdings": [
            {
                "id": h.holding_id,
                "asset_class": h.asset_class.value,
                "name": h.name,
                "jurisdiction": h.jurisdiction,
                "acquisition_cost": float(h.acquisition_cost),
                "current_value": float(h.current_value),
                "unrealized_gain_loss": float(h.unrealized_gain_loss),
                "income_ytd": float(h.income_generated_ytd),
                "is_active": h.is_active
            }
            for h in holdings
        ]
    }


@router.get("/holdings/summary")
async def get_holdings_summary():
    """Get wealth summary by asset class and jurisdiction"""
    manager = get_wealth_tracker()
    return manager.get_total_wealth()


# ==================== INCOME ====================

@router.post("/income/add-stream")
async def add_income_stream(req: AddIncomeRequest):
    """Add income stream"""
    manager = get_wealth_tracker()
    
    try:
        income_type = IncomeType(req.income_type)
    except ValueError:
        valid = [i.value for i in IncomeType]
        raise HTTPException(400, f"Invalid income type. Valid: {valid}")
    
    stream = IncomeStream(
        stream_id="",
        income_type=income_type,
        source=req.source,
        amount_monthly=req.amount_monthly,
        is_passive=req.is_passive,
        jurisdiction=req.jurisdiction
    )
    
    stream_id = manager.add_income_stream(stream)
    
    return {
        "stream_id": stream_id,
        "income_type": req.income_type,
        "source": req.source,
        "monthly_amount": float(req.amount_monthly),
        "annual_amount": float(req.amount_monthly * 12),
        "is_passive": req.is_passive
    }


@router.get("/income/passive")
async def get_passive_income_summary():
    """Get all passive income summary"""
    manager = get_wealth_tracker()
    return manager.get_passive_income()


@router.get("/income/streams")
async def list_income_streams(
    income_type: Optional[str] = None,
    passive_only: bool = False
):
    """List income streams"""
    manager = get_wealth_tracker()
    
    streams = list(manager.income_streams.values())
    
    if income_type:
        streams = [s for s in streams if s.income_type.value == income_type]
    if passive_only:
        streams = [s for s in streams if s.is_passive]
    
    return {
        "count": len(streams),
        "total_monthly": float(sum(s.amount_monthly for s in streams)),
        "total_annual": float(sum(s.amount_monthly * 12 for s in streams)),
        "streams": [
            {
                "id": s.stream_id,
                "type": s.income_type.value,
                "source": s.source,
                "monthly": float(s.amount_monthly),
                "annual": float(s.amount_monthly * 12),
                "is_passive": s.is_passive,
                "jurisdiction": s.jurisdiction,
                "ytd": float(s.ytd_total)
            }
            for s in streams
        ]
    }


# ==================== COMPREHENSIVE SUMMARY ====================

@router.get("/total")
async def get_total_wealth():
    """Get complete wealth summary"""
    manager = get_wealth_tracker()
    
    wealth = manager.get_total_wealth()
    passive = manager.get_passive_income()
    international = manager.get_international_summary()
    
    total_value = wealth["total_wealth"]
    annual_passive = passive["annual_passive"]
    
    # Calculate FI metrics
    fi_number = total_value * 0.04  # 4% rule
    passive_coverage = (annual_passive / fi_number * 100) if fi_number > 0 else 0
    
    return {
        "total_wealth_gbp": total_value,
        "by_asset_class": wealth["by_asset_class"],
        "by_jurisdiction": wealth["by_jurisdiction"],
        "passive_income": {
            "monthly": passive["monthly_passive"],
            "annual": annual_passive,
            "breakdown": passive["breakdown"]
        },
        "international": international,
        "fi_metrics": {
            "fi_number_4pct_rule": fi_number,
            "annual_passive": annual_passive,
            "passive_coverage_pct": passive_coverage,
            "years_to_fi_estimate": None  # Would need expense data
        },
        "diversification": {
            "asset_classes": len(wealth["by_asset_class"]),
            "jurisdictions": len(wealth["by_jurisdiction"]),
            "foreign_exposure_pct": (international["foreign_holdings_value"] / total_value * 100) if total_value > 0 else 0
        }
    }


@router.get("/opportunities")
async def get_investment_opportunities(
    asset_class: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    passive_income_focus: bool = False
):
    """Get investment opportunities by criteria"""
    # This would integrate with market data APIs
    # For now, return structure
    
    opportunities = []
    
    # Example opportunities by category
    if not asset_class or asset_class == "crypto":
        opportunities.append({
            "asset_class": "crypto",
            "name": "Ethereum Staking",
            "type": "passive_yield",
            "expected_yield": 4.5,
            "risk_level": "high",
            "jurisdiction": "international",
            "description": "Stake ETH for ~4.5% APR",
            "passive": True
        })
    
    if not asset_class or asset_class == "real_estate":
        opportunities.append({
            "asset_class": "real_estate",
            "name": "REITs",
            "type": "dividend_income",
            "expected_yield": 5.0,
            "risk_level": "medium",
            "jurisdiction": "uk",
            "description": "Real Estate Investment Trusts",
            "passive": True
        })
    
    if not asset_class or asset_class == "stocks":
        opportunities.append({
            "asset_class": "stocks",
            "name": "Dividend Aristocrats",
            "type": "dividend_growth",
            "expected_yield": 3.0,
            "risk_level": "medium",
            "jurisdiction": "usa",
            "description": "S&P 500 companies with 25+ years of dividend increases",
            "passive": True
        })
    
    if passive_income_focus:
        opportunities = [o for o in opportunities if o.get("passive")]
    
    if jurisdiction:
        opportunities = [o for o in opportunities if o.get("jurisdiction") == jurisdiction]
    
    return {
        "count": len(opportunities),
        "filters": {
            "asset_class": asset_class,
            "jurisdiction": jurisdiction,
            "passive_only": passive_income_focus
        },
        "opportunities": opportunities
    }


@router.get("/international/summary")
async def get_international_wealth_summary():
    """Get international wealth and income summary"""
    manager = get_wealth_tracker()
    return manager.get_international_summary()
