"""Carry Strategy - Implement carry trades across asset classes"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class AssetClass(Enum):
    FX = "fx"
    RATES = "rates"
    CREDIT = "credit"
    COMMODITIES = "commodities"

@dataclass
class CarryInstrument:
    symbol: str
    asset_class: AssetClass
    yield_rate: float  # Annualized yield/carry
    funding_rate: float  # Cost of carry
    volatility: float
    liquidity_score: int  # 0-100

class CarryStrategy:
    """Identify and analyze carry trade opportunities"""
    
    def __init__(self):
        self.instruments: List[CarryInstrument] = []
        self.risk_free_rate = 0.05
    
    def add_instrument(self, instrument: CarryInstrument):
        """Add instrument to universe"""
        self.instruments.append(instrument)
    
    def calculate_carry(self, instrument: CarryInstrument) -> Dict:
        """Calculate carry metrics for an instrument"""
        # Gross carry
        gross_carry = instrument.yield_rate - instrument.funding_rate
        
        # Sharpe of carry (carry per unit of risk)
        if instrument.volatility > 0:
            carry_sharpe = gross_carry / instrument.volatility
        else:
            carry_sharpe = 0
        
        # Real carry (excess over risk-free)
        real_carry = gross_carry - self.risk_free_rate
        
        # Liquidity adjustment
        liquidity_factor = min(1.0, instrument.liquidity_score / 50)
        adjusted_carry = real_carry * liquidity_factor
        
        return {
            "symbol": instrument.symbol,
            "asset_class": instrument.asset_class.value,
            "gross_carry": round(gross_carry * 100, 2),
            "real_carry": round(real_carry * 100, 2),
            "adjusted_carry": round(adjusted_carry * 100, 2),
            "carry_sharpe": round(carry_sharpe, 2),
            "annualized_return": round(gross_carry * 100, 2),
            "risk_adjusted_rating": "HIGH" if carry_sharpe > 1.0 else "MODERATE" if carry_sharpe > 0.5 else "LOW",
            "recommendation": "LONG_CARRY" if real_carry > 0.02 else "AVOID" if real_carry < 0 else "NEUTRAL"
        }
    
    def find_best_carry_trades(self, asset_class: AssetClass = None, 
                                min_carry: float = 0.01) -> List[Dict]:
        """Find best carry opportunities"""
        opportunities = []
        
        for inst in self.instruments:
            if asset_class and inst.asset_class != asset_class:
                continue
            
            carry_data = self.calculate_carry(inst)
            
            if carry_data["real_carry"] >= min_carry * 100:  # Convert to bps
                opportunities.append(carry_data)
        
        # Sort by carry Sharpe
        opportunities.sort(key=lambda x: x["carry_sharpe"], reverse=True)
        
        return opportunities
    
    def build_carry_portfolio(self, capital: float, 
                              max_positions: int = 5,
                              diversification: bool = True) -> Dict:
        """Build diversified carry portfolio"""
        # Get all opportunities
        opportunities = self.find_best_carry_trades(min_carry=0.005)
        
        if not opportunities:
            return {"error": "No viable carry trades found"}
        
        selected = []
        asset_classes_used = set()
        
        for opp in opportunities:
            if len(selected) >= max_positions:
                break
            
            if diversification:
                # Check asset class diversification
                asset_class = opp["asset_class"]
                if asset_class in asset_classes_used and len(asset_classes_used) >= 3:
                    continue
                asset_classes_used.add(asset_class)
            
            selected.append(opp)
        
        # Equal weight allocation
        allocation_per_trade = capital / len(selected) if selected else 0
        
        portfolio = []
        total_expected_carry = 0
        
        for trade in selected:
            allocation = allocation_per_trade
            expected_return = trade["annualized_return"]
            dollar_return = allocation * (expected_return / 100)
            total_expected_carry += dollar_return
            
            portfolio.append({
                "symbol": trade["symbol"],
                "asset_class": trade["asset_class"],
                "allocation": round(allocation, 2),
                "expected_carry": trade["annualized_return"],
                "carry_sharpe": trade["carry_sharpe"],
                "risk_rating": trade["risk_adjusted_rating"]
            })
        
        portfolio_yield = (total_expected_carry / capital * 100) if capital > 0 else 0
        
        return {
            "total_capital": round(capital, 2),
            "number_of_positions": len(portfolio),
            "expected_portfolio_carry": round(portfolio_yield, 2),
            "expected_dollar_return": round(total_expected_carry, 2),
            "diversification_score": len(asset_classes_used),
            "positions": portfolio,
            "rebalancing_frequency": "MONTHLY",
            "risk_warning": "CARRY_TRADES_SUBJECT_TO_CRASH_RISK"
        }
    
    def analyze_carry_crash_risk(self, portfolio: List[Dict]) -> Dict:
        """Analyze tail risk for carry portfolio"""
        # Estimate crash risk based on historical carry trade crashes
        avg_sharpe = sum(p["carry_sharpe"] for p in portfolio) / len(portfolio) if portfolio else 0
        
        # Higher Sharpe = lower crash risk (paradox of carry)
        crash_probability = max(0.05, 0.30 - (avg_sharpe * 0.10))
        
        # Estimated drawdown in crash scenario
        expected_crash_drawdown = min(-0.50, -0.20 - (avg_sharpe * 0.10))
        
        return {
            "crash_probability_annual": round(crash_probability * 100, 1),
            "expected_crash_drawdown": round(expected_crash_drawdown * 100, 1),
            "tail_risk_rating": "HIGH" if crash_probability > 0.20 else "MODERATE" if crash_probability > 0.10 else "LOW",
            "hedging_recommendation": "BUY_VOLATILITY_HEDGE" if crash_probability > 0.15 else "MONITOR",
            "position_size_adjustment": 0.7 if crash_probability > 0.20 else 1.0
        }
    
    def get_carry_dashboard(self) -> Dict:
        """Get comprehensive carry opportunity dashboard"""
        # Analyze by asset class
        by_asset_class = {ac: [] for ac in AssetClass}
        
        for inst in self.instruments:
            carry_data = self.calculate_carry(inst)
            by_asset_class[inst.asset_class].append(carry_data)
        
        # Sort each by carry Sharpe
        for ac in by_asset_class:
            by_asset_class[ac].sort(key=lambda x: x["carry_sharpe"], reverse=True)
        
        # Best opportunities overall
        all_opps = []
        for ac_list in by_asset_class.values():
            all_opps.extend(ac_list)
        all_opps.sort(key=lambda x: x["carry_sharpe"], reverse=True)
        
        return {
            "top_opportunities_overall": all_opps[:10],
            "by_asset_class": {
                ac.value: {
                    "best": data[:3] if data else [],
                    "count": len(data),
                    "avg_carry": round(sum(d["real_carry"] for d in data) / len(data), 2) if data else 0
                }
                for ac, data in by_asset_class.items()
            },
            "market_environment": "FAVORABLE" if len([o for o in all_opps if o["real_carry"] > 2]) > 5 else "CHALLENGING",
            "timestamp": "2024-01-15T00:00:00Z"
        }
