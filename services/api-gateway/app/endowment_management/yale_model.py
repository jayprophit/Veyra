"""Yale Model - Endowment Management model based on David Swensen's approach"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Endowment:
    name: str
    total_assets: float
    spending_rate: float
    inflation_cushion: float  # Years of spending covered
    historical_return: float

class YaleModel:
    """Implement the Yale Endowment Model (David Swensen approach)"""
    
    # Yale Model target allocation (as of recent years)
    YALE_TARGET_ALLOCATION = {
        "absolute_return": 0.235,      # 23.5% - Hedge funds, event-driven
        "private_equity": 0.155,     # 15.5% - Leveraged buyouts, venture capital
        "natural_resources": 0.085,  # 8.5% - Oil, gas, timber, commodities
        "real_estate": 0.095,        # 9.5% - Commercial real estate
        "domestic_equity": 0.035,    # 3.5% - US stocks (low allocation)
        "foreign_equity": 0.115,   # 11.5% - International developed
        "emerging_markets": 0.095, # 9.5% - Emerging market equity
        "fixed_income": 0.055,     # 5.5% - Bonds and cash (very low)
        "cash": 0.035               # 3.5% - Liquidity buffer
    }
    
    # Expected returns by asset class (long-term assumptions)
    EXPECTED_RETURNS = {
        "absolute_return": 0.06,
        "private_equity": 0.10,
        "natural_resources": 0.07,
        "real_estate": 0.065,
        "domestic_equity": 0.055,
        "foreign_equity": 0.06,
        "emerging_markets": 0.075,
        "fixed_income": 0.035,
        "cash": 0.02
    }
    
    # Expected volatility (standard deviation)
    EXPECTED_VOLATILITY = {
        "absolute_return": 0.12,
        "private_equity": 0.22,
        "natural_resources": 0.25,
        "real_estate": 0.18,
        "domestic_equity": 0.16,
        "foreign_equity": 0.18,
        "emerging_markets": 0.24,
        "fixed_income": 0.05,
        "cash": 0.01
    }
    
    def __init__(self):
        self.endowments: List[Endowment] = []
        self.custom_allocation: Dict = {}
    
    def add_endowment(self, endowment: Endowment):
        """Add endowment to tracking"""
        self.endowments.append(endowment)
    
    def get_yale_allocation(self) -> Dict:
        """Get the classic Yale Model allocation"""
        
        # Calculate weighted expected return
        weighted_return = sum(
            self.YALE_TARGET_ALLOCATION[asset] * self.EXPECTED_RETURNS[asset]
            for asset in self.YALE_TARGET_ALLOCATION
        )
        
        # Calculate portfolio volatility (simplified, assumes some correlation)
        # In reality, Yale benefits from low correlation between alts and public markets
        public_markets_vol = 0.15
        alternatives_vol = 0.18
        blended_vol = (0.40 * public_markets_vol + 0.60 * alternatives_vol) * 0.85  # Diversification benefit
        
        # Sharpe ratio approximation
        risk_free_rate = 0.025
        sharpe = (weighted_return - risk_free_rate) / blended_vol if blended_vol > 0 else 0
        
        return {
            "model": "Yale Endowment Model",
            "allocation": {k: round(v * 100, 1) for k, v in self.YALE_TARGET_ALLOCATION.items()},
            "asset_class_groupings": {
                "traditional_public_markets": round((0.035 + 0.115 + 0.095 + 0.055 + 0.035) * 100, 1),
                "alternative_investments": round((0.235 + 0.155 + 0.085 + 0.095) * 100, 1)
            },
            "expected_return": round(weighted_return * 100, 2),
            "expected_volatility": round(blended_vol * 100, 2),
            "sharpe_ratio_approx": round(sharpe, 2),
            "rebalancing_frequency": "Quarterly for public, Annual for private",
            "key_principles": [
                "Heavy allocation to alternative investments",
                "Equity-oriented (minimize bonds)",
                "Diversification across uncorrelated assets",
                "Active management in inefficient markets",
                "Passive/index in efficient markets",
                "Long time horizon allows illiquidity"
            ]
        }
    
    def customize_for_endowment(self, endowment: Endowment,
                               risk_tolerance: str = "High",
                               size_category: str = "Large") -> Dict:
        """Customize Yale Model for specific endowment"""
        
        # Start with Yale base
        allocation = dict(self.YALE_TARGET_ALLOCATION)
        
        # Adjust for endowment size
        if size_category == "Small":
            # Smaller endowments can't access top-tier alternatives
            # Reduce alternatives, increase public markets
            alt_reduction = 0.15
            allocation["absolute_return"] -= 0.075
            allocation["private_equity"] -= 0.05
            allocation["real_estate"] -= 0.025
            
            # Add to public markets
            allocation["domestic_equity"] += alt_reduction * 0.40
            allocation["foreign_equity"] += alt_reduction * 0.35
            allocation["fixed_income"] += alt_reduction * 0.25
        
        elif size_category == "Medium":
            # Medium can access some alts but not full Yale allocation
            alt_reduction = 0.10
            allocation["absolute_return"] -= 0.05
            allocation["private_equity"] -= 0.035
            allocation["real_estate"] -= 0.015
            
            allocation["domestic_equity"] += alt_reduction * 0.50
            allocation["foreign_equity"] += alt_reduction * 0.30
            allocation["fixed_income"] += alt_reduction * 0.20
        
        # Adjust for risk tolerance
        if risk_tolerance == "Low":
            # Reduce volatility assets
            allocation["emerging_markets"] -= 0.03
            allocation["private_equity"] -= 0.02
            allocation["fixed_income"] += 0.03
            allocation["cash"] += 0.02
        
        elif risk_tolerance == "Very High":
            # Even more aggressive than Yale
            allocation["private_equity"] += 0.03
            allocation["emerging_markets"] += 0.02
            allocation["fixed_income"] -= 0.03
            allocation["cash"] -= 0.02
        
        # Ensure all positive
        for asset in allocation:
            allocation[asset] = max(0.01, allocation[asset])
        
        # Normalize to 100%
        total = sum(allocation.values())
        allocation = {k: v/total for k, v in allocation.items()}
        
        # Calculate expected metrics
        expected_return = sum(
            allocation[asset] * self.EXPECTED_RETURNS[asset]
            for asset in allocation
        )
        
        # Estimate liquidity
        liquid_assets = allocation["domestic_equity"] + allocation["foreign_equity"] + allocation["emerging_markets"] + allocation["fixed_income"] + allocation["cash"]
        illiquid_assets = 1 - liquid_assets
        
        return {
            "endowment": endowment.name,
            "size_category": size_category,
            "risk_tolerance": risk_tolerance,
            "custom_allocation": {k: round(v * 100, 1) for k, v in allocation.items()},
            "expected_return": round(expected_return * 100, 2),
            "illiquidity_level": round(illiquid_assets * 100, 1),
            "liquidity_profile": "HIGH" if liquid_assets > 0.60 else "MODERATE" if liquid_assets > 0.40 else "LOW",
            "implementation_difficulty": "HIGH" if illiquid_assets > 0.50 else "MODERATE" if illiquid_assets > 0.30 else "LOW"
        }
    
    def analyze_spending_sustainability(self, endowment: Endowment) -> Dict:
        """Analyze if spending policy is sustainable with Yale model returns"""
        
        yale_metrics = self.get_yale_allocation()
        expected_return = yale_metrics["expected_return"] / 100
        
        # Real return (after inflation)
        inflation = 0.025
        real_return = expected_return - inflation
        
        # Current spending
        annual_spending = endowment.total_assets * endowment.spending_rate
        
        # Break-even analysis
        # For perpetual sustainability: spending rate < real return
        sustainable_spending = real_return
        
        # Years of cushion
        cushion_years = endowment.inflation_cushion
        
        # Risk assessment
        if endowment.spending_rate > real_return * 1.2:
            risk_level = "HIGH"
            outlook = "Declining real value over time"
        elif endowment.spending_rate > real_return:
            risk_level = "MODERATE"
            outlook = "Stable nominal, slight decline in real value"
        elif endowment.spending_rate > real_return * 0.8:
            risk_level = "LOW"
            outlook = "Stable real value"
        else:
            risk_level = "VERY_LOW"
            outlook = "Growing real value"
        
        return {
            "endowment": endowment.name,
            "current_spending_rate": round(endowment.spending_rate * 100, 2),
            "sustainable_spending_rate": round(sustainable_spending * 100, 2),
            "expected_real_return": round(real_return * 100, 2),
            "annual_spending": round(annual_spending, 0),
            "risk_level": risk_level,
            "long_term_outlook": outlook,
            "spending_flexibility": "HIGH" if cushion_years > 5 else "MODERATE" if cushion_years > 3 else "LOW"
        }
    
    def compare_to_traditional_endowment(self) -> Dict:
        """Compare Yale Model to traditional 60/40 endowment"""
        
        # Traditional 60/40 allocation
        traditional = {
            "domestic_equity": 0.40,
            "foreign_equity": 0.15,
            "fixed_income": 0.40,
            "cash": 0.05
        }
        
        trad_return = sum(
            traditional.get(asset, 0) * self.EXPECTED_RETURNS.get(asset, 0.04)
            for asset in traditional
        )
        
        yale_metrics = self.get_yale_allocation()
        yale_return = yale_metrics["expected_return"] / 100
        
        # Traditional volatility (higher correlation between stocks and bonds reduces diversification)
        trad_volatility = 0.12  # 60/40 has about 12% volatility
        yale_volatility = yale_metrics["expected_volatility"] / 100
        
        # Risk-adjusted returns (Sharpe)
        rf = 0.025
        trad_sharpe = (trad_return - rf) / trad_volatility
        yale_sharpe = (yale_return - rf) / yale_volatility
        
        return {
            "comparison": {
                "traditional_60_40": {
                    "allocation": {k: round(v * 100, 0) for k, v in traditional.items()},
                    "expected_return": round(trad_return * 100, 2),
                    "expected_volatility": round(trad_volatility * 100, 2),
                    "sharpe_ratio": round(trad_sharpe, 2)
                },
                "yale_model": {
                    "allocation": yale_metrics["allocation"],
                    "expected_return": yale_metrics["expected_return"],
                    "expected_volatility": yale_metrics["expected_volatility"],
                    "sharpe_ratio": round(yale_sharpe, 2)
                }
            },
            "yale_advantages": [
                f"Higher expected return: +{round((yale_return - trad_return) * 100, 2)}%",
                f"Better Sharpe ratio: +{round(yale_sharpe - trad_sharpe, 2)}",
                "Inflation protection through real assets",
                "Diversification from low-correlation alternatives"
            ],
            "yale_challenges": [
                "Higher illiquidity requires long time horizon",
                "Complex implementation and manager selection",
                "Higher fees from active alternative managers",
                "Access to top-tier managers limited for smaller endowments"
            ]
        }
    
    def manager_selection_framework(self, asset_class: str) -> Dict:
        """Provide framework for selecting managers in each asset class"""
        
        frameworks = {
            "absolute_return": {
                "selection_criteria": [
                    "Consistent alpha generation (3+ years)",
                    "Downside protection track record",
                    "Alignment of interests (co-investment)",
                    "Transparency and liquidity terms"
                ],
                "due_diligence_focus": "Strategy capacity and alpha sustainability",
                "fee_structure": "Performance-based with high watermark"
            },
            "private_equity": {
                "selection_criteria": [
                    "Historic IRR vs benchmark (vintage adjusted)",
                    "Team stability and succession planning",
                    "Industry expertise and network",
                    "Deal sourcing capabilities"
                ],
                "due_diligence_focus": "Track record across market cycles",
                "fee_structure": "2% management + 20% carry with hurdle"
            },
            "real_estate": {
                "selection_criteria": [
                    "Property-level returns and occupancy rates",
                    "Geographic and sector diversification",
                    "Development vs core allocation",
                    "ESG integration and sustainability"
                ],
                "due_diligence_focus": "Valuation methodology and cap rate assumptions",
                "fee_structure": "1-1.5% management + promote above preferred"
            },
            "natural_resources": {
                "selection_criteria": [
                    "Commodity price outlook alignment",
                    "Operational expertise in specific resource",
                    "Environmental and regulatory compliance",
                    "Exit strategy and timeline clarity"
                ],
                "due_diligence_focus": "Reserve estimates and commodity price sensitivity",
                "fee_structure": "1.5% management + 15-20% carry"
            }
        }
        
        return frameworks.get(asset_class, {
            "selection_criteria": ["Track record", "Team quality", "Alignment", "Fees"],
            "due_diligence_focus": "Standard due diligence process",
            "fee_structure": "Industry standard fees"
        })
