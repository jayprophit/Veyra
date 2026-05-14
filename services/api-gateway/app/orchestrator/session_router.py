"""
24/7 Session-Aware Trading Router
==================================
Automatically routes strategies based on global trading sessions.

Implements DeepSeek requirement for time-zone aware 24/7 wealth generation.
"""

from enum import Enum
from datetime import datetime, timezone
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TradingSession(Enum):
    SYDNEY = "sydney"           # 21:00 - 06:00 UTC
    TOKYO = "tokyo"             # 00:00 - 09:00 UTC
    LONDON = "london"           # 07:00 - 16:00 UTC
    NEW_YORK = "new_york"       # 13:00 - 22:00 UTC
    OVERLAP_LN = "overlap_ln"   # 13:00 - 16:00 (London+NY)
    WEEKEND = "weekend"         # Friday 22:00 - Sunday 21:00


class SessionRouter:
    """
    Routes trading strategies based on which global markets are open.
    Ensures 24/7 wealth generation by switching between asset classes.
    """
    
    # Session configurations
    SESSION_CONFIG = {
        TradingSession.SYDNEY: {
            "hours": (21, 6),
            "markets": ["ASX", "NZX", "SGX"],
            "primary_assets": ["forex_aud_jpy", "forex_aud_usd", "gold", "crypto_perps"],
            "secondary_assets": ["defi_yield", "staking"],
            "liquidity": "medium",
            "volatility": "medium"
        },
        TradingSession.TOKYO: {
            "hours": (0, 9),
            "markets": ["TSE", "SSE", "HKEX"],
            "primary_assets": ["forex_usd_jpy", "forex_eur_jpy", "nikkei_futures", "crypto"],
            "secondary_assets": ["defi", "asia_stocks"],
            "liquidity": "high",
            "volatility": "high"
        },
        TradingSession.LONDON: {
            "hours": (7, 16),
            "markets": ["LSE", "Euronext", "Xetra"],
            "primary_assets": ["forex_eur_usd", "forex_gbp_usd", "ftse100", "dax", "gold"],
            "secondary_assets": ["crypto", "european_etfs"],
            "liquidity": "very_high",
            "volatility": "medium"
        },
        TradingSession.NEW_YORK: {
            "hours": (13, 22),
            "markets": ["NYSE", "NASDAQ", "CME", "CBOT"],
            "primary_assets": ["us_equities", "us_etfs", "sp500_futures", "nasdaq_futures", "forex_usd"],
            "secondary_assets": ["crypto", "commodities"],
            "liquidity": "very_high",
            "volatility": "high"
        },
        TradingSession.OVERLAP_LN: {
            "hours": (13, 16),
            "markets": ["LSE", "NYSE", "NASDAQ", "Euronext"],
            "primary_assets": ["all_forex_majors", "european_us_arbitrage", "crypto"],
            "secondary_assets": ["cross_market_arbitrage", "etfs"],
            "liquidity": "highest",
            "volatility": "highest"
        },
        TradingSession.WEEKEND: {
            "hours": None,  # Special handling
            "markets": ["crypto_24_7", "defi", "forex_sun_17"],
            "primary_assets": ["crypto_perps", "defi_yield", "staking", "lending"],
            "secondary_assets": ["e_commerce", "digital_products", "p2p_lending"],
            "liquidity": "low_medium",
            "volatility": "high"
        }
    }
    
    def __init__(self):
        self.current_session = None
        self.active_strategies = []
        self.portfolio_allocation = {}
        
    def get_current_session(self) -> TradingSession:
        """Determine current trading session based on UTC time"""
        now = datetime.now(timezone.utc)
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Weekend check: Friday 22:00 - Sunday 21:00
        if weekday == 4 and hour >= 22:  # Friday after 22:00
            return TradingSession.WEEKEND
        elif weekday == 5:  # Saturday
            return TradingSession.WEEKEND
        elif weekday == 6 and hour < 21:  # Sunday before 21:00
            return TradingSession.WEEKEND
        
        # Weekday sessions
        if 21 <= hour or hour < 6:
            return TradingSession.SYDNEY
        elif 0 <= hour < 9:
            return TradingSession.TOKYO
        elif 7 <= hour < 16:
            # Check for London-NY overlap (13:00-16:00)
            if 13 <= hour < 16:
                return TradingSession.OVERLAP_LN
            return TradingSession.LONDON
        elif 13 <= hour < 22:
            return TradingSession.NEW_YORK
        else:
            return TradingSession.WEEKEND
    
    def get_session_strategies(self, session: Optional[TradingSession] = None) -> List[str]:
        """Get recommended strategies for a trading session"""
        if session is None:
            session = self.get_current_session()
        
        config = self.SESSION_CONFIG.get(session, {})
        primary = config.get("primary_assets", [])
        secondary = config.get("secondary_assets", [])
        
        return {
            "session": session.value,
            "primary_strategies": primary,
            "secondary_strategies": secondary,
            "markets_open": config.get("markets", []),
            "liquidity": config.get("liquidity", "unknown"),
            "volatility": config.get("volatility", "unknown")
        }
    
    def get_portfolio_allocation(self, session: Optional[TradingSession] = None) -> Dict[str, float]:
        """Recommended portfolio allocation for current session"""
        if session is None:
            session = self.get_current_session()
        
        allocations = {
            TradingSession.SYDNEY: {
                "forex_aud": 0.30,
                "gold": 0.25,
                "crypto": 0.25,
                "defi_yield": 0.20
            },
            TradingSession.TOKYO: {
                "forex_jpy": 0.35,
                "nikkei": 0.25,
                "crypto": 0.25,
                "asia_equities": 0.15
            },
            TradingSession.LONDON: {
                "forex_eur_gbp": 0.35,
                "european_equities": 0.25,
                "gold": 0.20,
                "crypto": 0.20
            },
            TradingSession.NEW_YORK: {
                "us_equities": 0.40,
                "us_etfs": 0.20,
                "forex_usd": 0.20,
                "crypto": 0.20
            },
            TradingSession.OVERLAP_LN: {
                "forex_majors": 0.40,
                "cross_market_arb": 0.30,
                "crypto": 0.20,
                "etfs": 0.10
            },
            TradingSession.WEEKEND: {
                "crypto_perps": 0.40,
                "defi_yield": 0.30,
                "staking": 0.20,
                "p2p_lending": 0.10
            }
        }
        
        return allocations.get(session, allocations[TradingSession.WEEKEND])
    
    def should_trade_asset(self, asset_class: str) -> bool:
        """Check if an asset class should be traded now"""
        session = self.get_current_session()
        strategies = self.get_session_strategies(session)
        
        all_assets = strategies["primary_strategies"] + strategies["secondary_strategies"]
        return asset_class in all_assets
    
    def get_24_7_status(self) -> Dict:
        """Get complete 24/7 trading status"""
        current = self.get_current_session()
        strategies = self.get_session_strategies(current)
        allocation = self.get_portfolio_allocation(current)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_session": current.value,
            "utc_time": datetime.now(timezone.utc).strftime("%H:%M"),
            "strategies": strategies,
            "recommended_allocation": allocation,
            "next_session": self._get_next_session(current),
            "markets_open": strategies["markets_open"],
            "24_7_assets_available": ["crypto", "defi", "forex_sunday"]
        }
    
    def _get_next_session(self, current: TradingSession) -> str:
        """Get next trading session"""
        order = [
            TradingSession.SYDNEY,
            TradingSession.TOKYO,
            TradingSession.LONDON,
            TradingSession.OVERLAP_LN,
            TradingSession.NEW_YORK,
            TradingSession.WEEKEND
        ]
        
        try:
            idx = order.index(current)
            next_idx = (idx + 1) % len(order)
            return order[next_idx].value
        except ValueError:
            return TradingSession.SYDNEY.value
    
    def execute_session_strategy(self, portfolio: Dict[str, float]) -> Dict:
        """
        Automatically rebalance portfolio for current session.
        Returns rebalancing recommendations.
        """
        current = self.get_current_session()
        target_allocation = self.get_portfolio_allocation(current)
        
        recommendations = []
        
        for asset, target_pct in target_allocation.items():
            current_value = portfolio.get(asset, 0)
            total_portfolio = sum(portfolio.values())
            current_pct = current_value / total_portfolio if total_portfolio > 0 else 0
            
            diff = target_pct - current_pct
            if abs(diff) > 0.05:  # 5% threshold
                action = "BUY" if diff > 0 else "SELL"
                amount = abs(diff) * total_portfolio
                
                recommendations.append({
                    "asset": asset,
                    "action": action,
                    "amount": amount,
                    "reason": f"{current.value} session optimization"
                })
        
        return {
            "session": current.value,
            "recommendations": recommendations,
            "should_rebalance": len(recommendations) > 0
        }


class TwentyFourSevenEngine:
    """
    Main 24/7 Wealth Generation Engine
    Ensures capital is always deployed in optimal markets.
    """
    
    def __init__(self):
        self.router = SessionRouter()
        self.running = False
        self.daily_pnl = 0.0
        self.total_trades = 0
    
    def start(self):
        """Start 24/7 trading engine"""
        self.running = True
        logger.info("24/7 Trading Engine STARTED")
        
        status = self.router.get_24_7_status()
        logger.info(f"Current session: {status['current_session']}")
        logger.info(f"Markets open: {', '.join(status['markets_open'])}")
        logger.info(f"Active strategies: {status['strategies']['primary_strategies']}")
    
    def stop(self):
        """Stop engine"""
        self.running = False
        logger.info("24/7 Trading Engine STOPPED")
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            "running": self.running,
            "current_session": self.router.get_current_session().value,
            "daily_pnl": self.daily_pnl,
            "total_trades": self.total_trades,
            "next_allocation_update": "Auto-rebalance hourly"
        }
    
    def hourly_rebalance_check(self, portfolio: Dict[str, float]) -> Optional[Dict]:
        """Check if portfolio needs rebalancing for new session"""
        if not self.running:
            return None
        
        return self.router.execute_session_strategy(portfolio)


# Quick usage
if __name__ == "__main__":
    engine = TwentyFourSevenEngine()
    engine.start()
    
    # Example portfolio
    portfolio = {
        "us_equities": 5000,
        "crypto": 3000,
        "forex": 2000
    }
    
    # Check for rebalancing
    rebalance = engine.hourly_rebalance_check(portfolio)
    if rebalance and rebalance["should_rebalance"]:
        print(f"Rebalance needed for {rebalance['session']}")
        for rec in rebalance["recommendations"]:
            print(f"  {rec['action']} ${rec['amount']:.2f} of {rec['asset']}")
