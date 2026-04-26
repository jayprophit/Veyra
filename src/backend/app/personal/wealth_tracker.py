"""
Comprehensive Wealth Tracker
Tracks ALL wealth types: traditional, alternative, digital, international
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from decimal import Decimal
from collections import defaultdict

class AssetClass(Enum):
    CASH = "cash"
    STOCKS = "stocks"
    BONDS = "bonds"
    ETF = "etf"
    REAL_ESTATE = "real_estate"
    PRECIOUS_METALS = "precious_metals"
    ART = "art"
    WINE = "wine"
    CLASSIC_CARS = "classic_cars"
    WATCHES = "watches"
    CRYPTO = "crypto"
    NFT = "nft"
    PRIVATE_EQUITY = "private_equity"
    VENTURE_CAPITAL = "venture_capital"
    HEDGE_FUNDS = "hedge_funds"
    P2P_LENDING = "p2p_lending"
    BUSINESS = "business"
    PENSION = "pension"
    COMMODITIES = "commodities"
    FOREX = "forex"
    DERIVATIVES = "derivatives"
    INTELLECTUAL_PROPERTY = "intellectual_property"

class IncomeType(Enum):
    SALARY = "salary"
    BONUS = "bonus"
    DIVIDENDS = "dividends"
    INTEREST = "interest"
    RENT = "rent"
    CAPITAL_GAINS = "capital_gains"
    ROYALTIES = "royalties"
    CRYPTO_STAKING = "crypto_staking"
    DEFI_YIELD = "defi_yield"
    P2P_INTEREST = "p2p_interest"
    BUSINESS_PROFIT = "business_profit"
    PENSION = "pension"
    FREELANCE = "freelance"
    CONSULTING = "consulting"

@dataclass
class WealthHolding:
    holding_id: str
    asset_class: AssetClass
    name: str
    jurisdiction: str
    acquisition_cost: Decimal
    current_value: Decimal
    unrealized_gain_loss: Decimal
    income_generated_ytd: Decimal = Decimal("0")
    is_active: bool = True

@dataclass
class IncomeStream:
    stream_id: str
    income_type: IncomeType
    source: str
    amount_monthly: Decimal
    is_passive: bool
    jurisdiction: str
    ytd_total: Decimal = Decimal("0")

class ComprehensiveWealthTracker:
    def __init__(self):
        self.holdings: Dict[str, WealthHolding] = {}
        self.income_streams: Dict[str, IncomeStream] = {}
    
    def add_holding(self, holding: WealthHolding) -> str:
        holding_id = f"w_{len(self.holdings) + 1}"
        holding.holding_id = holding_id
        self.holdings[holding_id] = holding
        return holding_id
    
    def add_income_stream(self, stream: IncomeStream) -> str:
        stream_id = f"i_{len(self.income_streams) + 1}"
        stream.stream_id = stream_id
        self.income_streams[stream_id] = stream
        return stream_id
    
    def get_total_wealth(self) -> Dict[str, Any]:
        total = sum(h.current_value for h in self.holdings.values() if h.is_active)
        by_class = defaultdict(lambda: Decimal("0"))
        by_jurisdiction = defaultdict(lambda: Decimal("0"))
        
        for h in self.holdings.values():
            if h.is_active:
                by_class[h.asset_class.value] += h.current_value
                by_jurisdiction[h.jurisdiction] += h.current_value
        
        return {
            "total_wealth": float(total),
            "by_asset_class": {k: float(v) for k, v in by_class.items()},
            "by_jurisdiction": {k: float(v) for k, v in by_jurisdiction.items()},
            "holding_count": len([h for h in self.holdings.values() if h.is_active])
        }
    
    def get_passive_income(self) -> Dict[str, Any]:
        passive_types = [IncomeType.DIVIDENDS, IncomeType.INTEREST, IncomeType.RENT,
                        IncomeType.ROYALTIES, IncomeType.CRYPTO_STAKING, IncomeType.DEFI_YIELD]
        
        monthly = Decimal("0")
        annual = Decimal("0")
        breakdown = defaultdict(lambda: Decimal("0"))
        
        for s in self.income_streams.values():
            if s.is_passive or s.income_type in passive_types:
                monthly += s.amount_monthly
                annual += s.amount_monthly * 12
                breakdown[s.income_type.value] += s.amount_monthly
        
        return {
            "monthly_passive": float(monthly),
            "annual_passive": float(annual),
            "breakdown": {k: float(v) for k, v in breakdown.items()}
        }
    
    def get_international_summary(self) -> Dict[str, Any]:
        foreign_holdings = [h for h in self.holdings.values() if h.jurisdiction != "uk" and h.is_active]
        foreign_income = [s for s in self.income_streams.values() if s.jurisdiction != "uk"]
        
        return {
            "foreign_holdings_count": len(foreign_holdings),
            "foreign_holdings_value": float(sum(h.current_value for h in foreign_holdings)),
            "foreign_income_streams": len(foreign_income),
            "foreign_monthly_income": float(sum(s.amount_monthly for s in foreign_income)),
            "jurisdictions": list(set(h.jurisdiction for h in foreign_holdings))
        }

_wealth_tracker: Optional[ComprehensiveWealthTracker] = None

def get_wealth_tracker() -> ComprehensiveWealthTracker:
    global _wealth_tracker
    if _wealth_tracker is None:
        _wealth_tracker = ComprehensiveWealthTracker()
    return _wealth_tracker
