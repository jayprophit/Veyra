"""Yield Optimizer - Find optimal DeFi yield opportunities"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class YieldOpportunity:
    protocol: str
    pool_name: str
    apy: float
    tvl: float  # Total Value Locked
    risk_score: int  # 1-10
    token_pair: List[str]
    impermanent_loss_30d: float
    rewards_token: str

class YieldOptimizer:
    """Optimize yield farming across DeFi protocols"""
    
    def __init__(self):
        self.opportunities: List[YieldOpportunity] = []
        self.protocols_tracked = [
            "Aave", "Compound", "Uniswap", "Curve", "Convex",
            "Yearn", "Balancer", "SushiSwap", "Lido", "RocketPool"
        ]
    
    def add_opportunity(self, opp: YieldOpportunity):
        """Add yield opportunity to tracker"""
        self.opportunities.append(opp)
    
    def calculate_risk_adjusted_yield(self, opp: YieldOpportunity) -> Dict:
        """Calculate risk-adjusted yield (Sharpe-like metric for DeFi)"""
        # Base APY
        base_apy = opp.apy
        
        # Risk penalties
        il_penalty = opp.impermanent_loss_30d * 0.5  # Half weight to IL
        risk_penalty = (opp.risk_score - 1) * 0.02  # 2% per risk point above 1
        
        # TVL size bonus (larger = safer)
        tvl_bonus = min(0.02, opp.tvl / 1e9 * 0.01)  # Max 2% bonus
        
        risk_adjusted = base_apy - il_penalty - risk_penalty + tvl_bonus
        
        return {
            "protocol": opp.protocol,
            "pool": opp.pool_name,
            "nominal_apy": round(opp.apy * 100, 2),
            "risk_adjusted_apy": round(risk_adjusted * 100, 2),
            "il_penalty": round(il_penalty * 100, 2),
            "risk_penalty": round(risk_penalty * 100, 2),
            "tvl_bonus": round(tvl_bonus * 100, 2),
            "risk_score": opp.risk_score,
            "tvl_millions": round(opp.tvl / 1e6, 2)
        }
    
    def find_best_opportunities(self, risk_tolerance: str = "medium",
                                min_tvl: float = 1e6) -> List[Dict]:
        """Find best yield opportunities based on risk tolerance"""
        # Filter by TVL
        filtered = [o for o in self.opportunities if o.tvl >= min_tvl]
        
        # Risk tolerance mapping
        max_risk = {"conservative": 3, "medium": 6, "aggressive": 10}
        allowed_risk = max_risk.get(risk_tolerance, 6)
        
        filtered = [o for o in filtered if o.risk_score <= allowed_risk]
        
        # Calculate risk-adjusted yields
        scored = []
        for opp in filtered:
            analysis = self.calculate_risk_adjusted_yield(opp)
            scored.append((opp, analysis["risk_adjusted_apy"]))
        
        # Sort by risk-adjusted yield
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [self.calculate_risk_adjusted_yield(opp) for opp, _ in scored[:10]]
    
    def compare_to_traditional(self, defi_apy: float) -> Dict:
        """Compare DeFi yields to traditional finance"""
        traditional_rates = {
            "savings_account": 0.005,  # 0.5%
            "1_year_cd": 0.055,      # 5.5%
            "money_market": 0.045,   # 4.5%
            "corporate_bonds": 0.06  # 6%
        }
        
        comparisons = {}
        for product, rate in traditional_rates.items():
            premium = ((defi_apy / rate) - 1) * 100 if rate > 0 else 0
            comparisons[product] = {
                "traditional_rate": round(rate * 100, 2),
                "defi_premium_pct": round(premium, 1),
                "multiple": round(defi_apy / rate, 1) if rate > 0 else 0
            }
        
        return {
            "defi_apy": round(defi_apy * 100, 2),
            "comparisons": comparisons,
            "outperforms_traditional": defi_apy > max(traditional_rates.values())
        }
    
    def get_diversified_yield_portfolio(self, capital: float) -> Dict:
        """Create diversified yield farming portfolio"""
        # Split across risk levels
        allocations = {
            "low_risk": capital * 0.40,   # Stable coins, blue-chip protocols
            "medium_risk": capital * 0.35,  # Established pairs
            "high_yield": capital * 0.25    # Higher risk, higher reward
        }
        
        portfolio = []
        
        for risk_level, amount in allocations.items():
            max_risk = 3 if risk_level == "low_risk" else 6 if risk_level == "medium_risk" else 10
            opps = [o for o in self.opportunities if o.risk_score <= max_risk]
            
            if opps:
                # Pick best from this risk category
                best = max(opps, key=lambda x: x.apy)
                analysis = self.calculate_risk_adjusted_yield(best)
                
                portfolio.append({
                    "allocation": risk_level,
                    "amount": round(amount, 2),
                    "protocol": best.protocol,
                    "pool": best.pool_name,
                    "expected_apy": analysis["nominal_apy"],
                    "annual_yield_usd": round(amount * best.apy, 2)
                })
        
        total_expected = sum(p["annual_yield_usd"] for p in portfolio)
        weighted_apy = (total_expected / capital * 100) if capital > 0 else 0
        
        return {
            "total_capital": round(capital, 2),
            "allocations": portfolio,
            "expected_total_yield_usd": round(total_expected, 2),
            "portfolio_apy": round(weighted_apy, 2),
            "monthly_yield_estimate": round(total_expected / 12, 2)
        }
    
    def monitor_impermanent_loss(self, position: YieldOpportunity,
                                 entry_prices: Dict[str, float],
                                 current_prices: Dict[str, float]) -> Dict:
        """Calculate impermanent loss for LP position"""
        if len(position.token_pair) != 2:
            return {"error": "Only valid for 2-token pools"}
        
        token_a, token_b = position.token_pair
        
        if token_a not in entry_prices or token_b not in entry_prices:
            return {"error": "Missing price data"}
        
        # Price ratios
        entry_ratio = entry_prices[token_a] / entry_prices[token_b]
        current_ratio = current_prices[token_a] / current_prices[token_b]
        
        # Price change
        price_change = current_ratio / entry_ratio
        
        # Impermanent loss formula: 2*sqrt(price_ratio) / (1 + price_ratio) - 1
        il = 2 * (price_change ** 0.5) / (1 + price_change) - 1
        
        return {
            "pool": position.pool_name,
            "token_pair": position.token_pair,
            "entry_ratio": round(entry_ratio, 4),
            "current_ratio": round(current_ratio, 4),
            "price_change_pct": round((price_change - 1) * 100, 2),
            "impermanent_loss_pct": round(abs(il) * 100, 2),
            "holding_vs_lp_value_diff": round(il * 100, 2),
            "recommendation": "REBALANCE" if abs(il) > 0.05 else "HOLD"
        }
