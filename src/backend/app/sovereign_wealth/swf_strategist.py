"""SWF Strategist - Sovereign Wealth Fund investment strategies"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SWFProfile:
    name: str
    country: str
    total_aum: float
    fund_type: str  # Savings, Stabilization, Pension Reserve, Development
    source_of_funds: str  # Oil, Commodities, Non-Commodity, Pension
    liability_duration: int  # Years
    spending_rule: float  # Annual withdrawal rate

class SWFStrategist:
    """Design sovereign wealth fund strategies"""
    
    # SWF type benchmarks
    BENCHMARK_ALLOCATIONS = {
        "Savings": {
            "equities": 0.45,
            "fixed_income": 0.25,
            "alternatives": 0.25,
            "cash": 0.05
        },
        "Stabilization": {
            "equities": 0.20,
            "fixed_income": 0.50,
            "alternatives": 0.15,
            "cash": 0.15
        },
        "Pension_Reserve": {
            "equities": 0.35,
            "fixed_income": 0.35,
            "alternatives": 0.25,
            "cash": 0.05
        },
        "Development": {
            "equities": 0.30,
            "fixed_income": 0.20,
            "alternatives": 0.45,  # Higher alternatives for infrastructure
            "cash": 0.05
        }
    }
    
    def __init__(self):
        self.swfs: List[SWFProfile] = []
    
    def add_swf(self, swf: SWFProfile):
        """Add SWF to database"""
        self.swfs.append(swf)
    
    def recommend_allocation(self, swf: SWFProfile,
                            risk_tolerance: str = "Moderate") -> Dict:
        """Recommend strategic asset allocation"""
        
        # Get base allocation for fund type
        base = self.BENCHMARK_ALLOCATIONS.get(swf.fund_type, 
                                            self.BENCHMARK_ALLOCATIONS["Savings"])
        
        # Adjust for liability duration
        if swf.liability_duration > 30:
            # Long duration allows more equities
            equity_adjustment = 0.10
            fixed_adjustment = -0.10
        elif swf.liability_duration < 10:
            # Short duration needs more stability
            equity_adjustment = -0.10
            fixed_adjustment = 0.10
        else:
            equity_adjustment = 0
            fixed_adjustment = 0
        
        # Adjust for risk tolerance
        if risk_tolerance == "Aggressive":
            equity_adjustment += 0.10
            fixed_adjustment -= 0.05
        elif risk_tolerance == "Conservative":
            equity_adjustment -= 0.10
            fixed_adjustment += 0.10
        
        # Adjust for source of funds
        if swf.source_of_funds == "Oil":
            # Commodity correlation - reduce energy exposure within equities
            commodity_hedge_note = "Consider underweighting energy sector within equity allocation"
        elif swf.source_of_funds == "Commodities":
            commodity_hedge_note = "Consider commodity hedging or inflation-linked securities"
        else:
            commodity_hedge_note = "None"
        
        # Build final allocation
        equities = max(0.10, min(0.70, base["equities"] + equity_adjustment))
        fixed_income = max(0.10, min(0.60, base["fixed_income"] + fixed_adjustment))
        
        # Remaining to alternatives and cash
        remaining = 1.0 - equities - fixed_income
        alternatives = remaining * 0.80
        cash = remaining * 0.20
        
        # Geographic split for equities
        equity_geo = {
            "domestic": 0.15,
            "developed_intl": 0.45,
            "emerging": 0.30,
            "frontier": 0.10
        }
        
        return {
            "swf": swf.name,
            "fund_type": swf.fund_type,
            "strategic_allocation": {
                "equities": round(equities * 100, 1),
                "fixed_income": round(fixed_income * 100, 1),
                "alternatives": round(alternatives * 100, 1),
                "cash": round(cash * 100, 1)
            },
            "equity_breakdown": {k: round(v * 100, 1) for k, v in equity_geo.items()},
            "alternative_breakdown": {
                "infrastructure": 35,
                "private_equity": 30,
                "real_estate": 25,
                "hedge_funds": 10
            },
            "commodity_hedge": commodity_hedge_note,
            "rebalancing_band": "+/- 5%",
            "review_frequency": "Annual"
        }
    
    def spending_rule_analysis(self, swf: SWFProfile,
                              market_return_assumption: float = 0.06,
                              inflation_assumption: float = 0.025) -> Dict:
        """Analyze spending rule sustainability"""
        
        # Current spending rule
        current_spending = swf.total_aum * swf.spending_rule
        
        # Real return assumption
        real_return = market_return_assumption - inflation_assumption
        
        # Sustainable spending rate (perpetuity formula)
        # Spending rate = real return / (1 + real return)
        sustainable_rate = real_return / (1 + real_return) if (1 + real_return) > 0 else 0
        
        # Years until depletion at current rate (simplified)
        if swf.spending_rule > market_return_assumption:
            # Declining real value
            decline_rate = swf.spending_rule - market_return_assumption
            years_to_half = 0.50 / decline_rate if decline_rate > 0 else 1000
        else:
            years_to_half = "Infinite (growing real value)"
        
        # Intergenerational transfer analysis
        # Value for next generation
        if swf.liability_duration > 0:
            annual_growth = market_return_assumption - swf.spending_rule
            next_gen_value = swf.total_aum * ((1 + annual_growth) ** swf.liability_duration)
        else:
            next_gen_value = 0
        
        return {
            "current_spending_rule": round(swf.spending_rule * 100, 2),
            "annual_spending": round(current_spending, 0),
            "sustainable_spending_rate": round(sustainable_rate * 100, 2),
            "current_vs_sustainable": "ABOVE" if swf.spending_rule > sustainable_rate else "BELOW",
            "real_return_assumption": round(real_return * 100, 2),
            "years_to_half_value": years_to_half if isinstance(years_to_half, str) else round(years_to_half, 1),
            "intergenerational_transfer": {
                "years_ahead": swf.liability_duration,
                "projected_value": round(next_gen_value, 0),
                "real_value_change_pct": round(((next_gen_value / swf.total_aum) ** (1/swf.liability_duration) - 1) * 100, 2) if swf.liability_duration > 0 else 0
            },
            "recommendation": "REDUCE_SPENDING" if swf.spending_rule > sustainable_rate * 1.2 else "MAINTAIN" if swf.spending_rule > sustainable_rate else "CAN_INCREASE"
        }
    
    def analyze_concentration_risk(self, swf: SWFProfile,
                                   domestic_equity_pct: float = 0.15) -> Dict:
        """Analyze home country bias and concentration risk"""
        
        # Calculate domestic market value vs SWF ownership
        # Simplified: assume domestic equities are all in local market
        domestic_equity_value = swf.total_aum * 0.45 * domestic_equity_pct  # 45% equity allocation * 15% domestic
        
        # Concentration metrics
        total_domestic_exposure = domestic_equity_value  # Could add domestic bonds, real estate
        
        # Risk assessment
        if domestic_equity_pct > 0.30:
            risk_level = "HIGH"
            recommendation = "Significant reduction in domestic exposure recommended"
        elif domestic_equity_pct > 0.20:
            risk_level = "MODERATE"
            recommendation = "Consider gradual reduction in domestic bias"
        else:
            risk_level = "LOW"
            recommendation = "Domestic concentration within acceptable range"
        
        return {
            "domestic_equity_allocation": round(domestic_equity_pct * 100, 1),
            "domestic_equity_value": round(domestic_equity_value, 0),
            "concentration_risk": risk_level,
            "recommendation": recommendation,
            "diversification_benefit": "HIGH" if domestic_equity_pct < 0.15 else "MODERATE" if domestic_equity_pct < 0.25 else "LOW"
        }
    
    def generate_peer_comparison(self, swf: SWFProfile) -> Dict:
        """Compare against peer SWFs"""
        
        peers = [s for s in self.swfs if s.fund_type == swf.fund_type and s.name != swf.name]
        
        if not peers:
            return {"error": "No peers found"}
        
        # Calculate peer averages
        avg_aum = sum(p.total_aum for p in peers) / len(peers)
        avg_spending = sum(p.spending_rule for p in peers) / len(peers)
        avg_duration = sum(p.liability_duration for p in peers) / len(peers)
        
        return {
            "swf": swf.name,
            "peer_group": swf.fund_type,
            "num_peers": len(peers),
            "aum_comparison": {
                "swf_aum": round(swf.total_aum / 1e9, 1),
                "peer_average": round(avg_aum / 1e9, 1),
                "percentile": "ABOVE_AVERAGE" if swf.total_aum > avg_aum else "BELOW_AVERAGE"
            },
            "spending_rule_comparison": {
                "swf_rate": round(swf.spending_rule * 100, 2),
                "peer_average": round(avg_spending * 100, 2),
                "assessment": "CONSERVATIVE" if swf.spending_rule < avg_spending * 0.8 else "AGGRESSIVE" if swf.spending_rule > avg_spending * 1.2 else "IN_LINE"
            },
            "liability_duration": {
                "swf_duration": swf.liability_duration,
                "peer_average": round(avg_duration, 1),
                "horizon_classification": "LONG" if swf.liability_duration > avg_duration * 1.2 else "SHORT" if swf.liability_duration < avg_duration * 0.8 else "AVERAGE"
            }
        }
    
    def strategic_review(self, swf: SWFProfile) -> Dict:
        """Generate comprehensive strategic review"""
        
        allocation = self.recommend_allocation(swf)
        spending = self.spending_rule_analysis(swf)
        concentration = self.analyze_concentration_risk(swf)
        
        return {
            "swf_name": swf.name,
            "country": swf.country,
            "fund_type": swf.fund_type,
            "total_aum_billions": round(swf.total_aum / 1e9, 1),
            "strategic_allocation": allocation,
            "spending_analysis": spending,
            "concentration_risk": concentration,
            "key_recommendations": [
                "Review asset allocation annually" if True else "",
                "Reduce spending rule to sustainable level" if spending["recommendation"] == "REDUCE_SPENDING" else "",
                "Diversify away from domestic concentration" if concentration["concentration_risk"] in ["HIGH", "MODERATE"] else "",
                "Consider increasing alternatives allocation" if swf.fund_type == "Development" else ""
            ],
            "governance_recommendations": [
                "Establish independent investment committee",
                "Implement clear rebalancing policy",
                "Regular peer benchmarking",
                "Transparent reporting standards"
            ]
        }
