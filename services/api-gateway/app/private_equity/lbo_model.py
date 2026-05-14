"""LBO Model - Leveraged Buyout financial modeling"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class LBOTarget:
    company_name: str
    revenue: float
    ebitda: float
    ebitda_margin: float
    debt: float
    cash: float
    enterprise_value: float
    industry: str
    growth_rate: float

class LBOModel:
    """LBO financial model for private equity"""
    
    def __init__(self):
        self.target: LBOTarget = None
        self.entry_assumptions: Dict = {}
        self.debt_schedule: List[Dict] = []
    
    def set_target(self, target: LBOTarget):
        """Set acquisition target"""
        self.target = target
    
    def calculate_entry_multiples(self) -> Dict:
        """Calculate entry valuation multiples"""
        if not self.target:
            return {"error": "No target set"}
        
        ev = self.target.enterprise_value
        ebitda = self.target.ebitda
        revenue = self.target.revenue
        
        # Calculate multiples
        ev_ebitda = ev / ebitda if ebitda > 0 else 0
        ev_revenue = ev / revenue if revenue > 0 else 0
        
        # Equity value
        equity_value = ev - self.target.debt + self.target.cash
        
        # Industry benchmarks (simplified)
        industry_medians = {
            "Technology": {"ev_ebitda": 12, "ev_revenue": 4},
            "Healthcare": {"ev_ebitda": 10, "ev_revenue": 3},
            "Industrials": {"ev_ebitda": 8, "ev_revenue": 1.5},
            "Consumer": {"ev_ebitda": 9, "ev_revenue": 2},
            "Energy": {"ev_ebitda": 6, "ev_revenue": 2},
            "Financials": {"ev_ebitda": 10, "ev_revenue": 3}
        }
        
        median = industry_medians.get(self.target.industry, {"ev_ebitda": 8, "ev_revenue": 2})
        
        return {
            "company": self.target.company_name,
            "enterprise_value": round(ev, 0),
            "equity_value": round(equity_value, 0),
            "ev_ebitda": round(ev_ebitda, 1),
            "ev_revenue": round(ev_revenue, 2),
            "industry_median_ebitda": median["ev_ebitda"],
            "premium_to_median": round(((ev_ebitda / median["ev_ebitda"]) - 1) * 100, 1) if median["ev_ebitda"] > 0 else 0,
            "valuation_assessment": "PREMIUM" if ev_ebitda > median["ev_ebitda"] * 1.1 else "FAIR" if ev_ebitda > median["ev_ebitda"] * 0.9 else "DISCOUNT"
        }
    
    def build_lbo_structure(self, purchase_price: float,
                          senior_debt_multiple: float = 3.0,
                          sub_debt_multiple: float = 1.0,
                          equity_contribution_pct: float = 0.40) -> Dict:
        """Build LBO capital structure"""
        
        # Total debt capacity
        senior_debt = self.target.ebitda * senior_debt_multiple
        subordinated_debt = self.target.ebitda * sub_debt_multiple
        total_debt = senior_debt + subordinated_debt
        
        # Required equity
        total_sources = purchase_price
        equity_required = total_sources - total_debt
        
        # Check if structure works
        actual_equity_pct = equity_required / purchase_price if purchase_price > 0 else 0
        
        # If equity % is too low, reduce debt
        if actual_equity_pct < equity_contribution_pct:
            max_debt = purchase_price * (1 - equity_contribution_pct)
            senior_debt = max_debt * 0.75
            subordinated_debt = max_debt * 0.25
            total_debt = senior_debt + subordinated_debt
            equity_required = purchase_price - total_debt
            actual_equity_pct = equity_required / purchase_price
        
        return {
            "purchase_price": round(purchase_price, 0),
            "sources": {
                "senior_debt": round(senior_debt, 0),
                "subordinated_debt": round(subordinated_debt, 0),
                "equity": round(equity_required, 0),
                "total_sources": round(purchase_price, 0)
            },
            "capital_structure": {
                "senior_debt_pct": round((senior_debt / purchase_price) * 100, 1),
                "sub_debt_pct": round((subordinated_debt / purchase_price) * 100, 1),
                "equity_pct": round((equity_required / purchase_price) * 100, 1)
            },
            "leverage_metrics": {
                "total_leverage": round(total_debt / self.target.ebitda, 1) if self.target.ebitda > 0 else 0,
                "senior_leverage": round(senior_debt / self.target.ebitda, 1) if self.target.ebitda > 0 else 0,
                "interest_coverage": round(self.target.ebitda / (senior_debt * 0.06 + subordinated_debt * 0.10), 1) if (senior_debt + subordinated_debt) > 0 else 0
            },
            "fees": {
                "advisory_fees": round(purchase_price * 0.015, 0),  # 1.5%
                "financing_fees": round(total_debt * 0.02, 0),  # 2%
                "total_fees": round(purchase_price * 0.015 + total_debt * 0.02, 0)
            }
        }
    
    def project_financials(self, holding_period: int = 5,
                          revenue_cagr: float = 0.05,
                          margin_expansion: float = 0.02,
                          capex_pct: float = 0.03) -> List[Dict]:
        """Project financials over holding period"""
        if not self.target:
            return []
        
        projections = []
        
        revenue = self.target.revenue
        ebitda_margin = self.target.ebitda_margin
        
        for year in range(holding_period + 1):
            ebitda = revenue * ebitda_margin
            depreciation = revenue * 0.02  # Simplified
            ebit = ebitda - depreciation
            
            # Interest expense (simplified, declining as debt pays down)
            interest = revenue * 0.03 * (1 - year * 0.1)  # Declining interest
            
            ebt = ebit - interest
            taxes = max(0, ebt * 0.25)
            net_income = ebt - taxes
            
            # Free cash flow
            capex = revenue * capex_pct
            working_capital = revenue * 0.02
            fcf = ebitda - capex - working_capital - taxes
            
            projections.append({
                "year": year,
                "revenue": round(revenue, 0),
                "ebitda": round(ebitda, 0),
                "ebitda_margin": round(ebitda_margin * 100, 1),
                "ebit": round(ebit, 0),
                "interest": round(interest, 0),
                "net_income": round(net_income, 0),
                "capex": round(capex, 0),
                "free_cash_flow": round(fcf, 0)
            })
            
            # Grow for next year
            revenue *= (1 + revenue_cagr)
            ebitda_margin = min(0.35, ebitda_margin + (margin_expansion / holding_period))
        
        return projections
    
    def calculate_irr(self, entry_equity: float,
                     exit_equity: float,
                     holding_period: int = 5,
                     dividends: float = 0) -> Dict:
        """Calculate levered IRR"""
        
        # Total cash flows
        total_cash_received = exit_equity + dividends
        
        # IRR calculation
        # exit = entry * (1 + irr)^period
        # irr = (exit/entry)^(1/period) - 1
        
        if entry_equity <= 0:
            return {"error": "Invalid entry equity"}
        
        multiple = total_cash_received / entry_equity
        irr = (multiple ** (1/holding_period)) - 1 if holding_period > 0 else 0
        
        # Money multiple
        money_multiple = multiple
        
        return {
            "entry_equity": round(entry_equity, 0),
            "exit_equity": round(exit_equity, 0),
            "dividends": round(dividends, 0),
            "total_cash": round(total_cash_received, 0),
            "money_multiple": round(money_multiple, 2),
            "gross_irr": round(irr * 100, 2),
            "net_irr": round((irr - 0.02) * 100, 2),  # Assume 2% fees/drag
            "performance_rating": "EXCELLENT" if irr > 0.25 else "GOOD" if irr > 0.15 else "ACCEPTABLE" if irr > 0.08 else "POOR"
        }
    
    def sensitivity_analysis(self, entry_ev_ebitda: float,
                            exit_ev_ebitda_range: List[float],
                            ebitda_growth_range: List[float]) -> Dict:
        """Run sensitivity analysis on key assumptions"""
        
        results = []
        
        base_entry_ev = entry_ev_ebitda * self.target.ebitda
        lbo_structure = self.build_lbo_structure(base_entry_ev)
        entry_equity = lbo_structure["sources"]["equity"]
        
        for exit_multiple in exit_ev_ebitda_range:
            row = {"exit_multiple": exit_multiple}
            
            for growth_rate in ebitda_growth_range:
                # Project EBITDA with this growth rate
                final_ebitda = self.target.ebitda * ((1 + growth_rate) ** 5)
                exit_ev = final_ebitda * exit_multiple
                
                # Assume debt paid down 50%
                remaining_debt = lbo_structure["sources"]["total_sources"] - lbo_structure["sources"]["equity"]
                remaining_debt *= 0.5  # 50% paid down
                
                exit_equity = exit_ev - remaining_debt
                
                # Calculate IRR
                irr_result = self.calculate_irr(entry_equity, exit_equity, 5)
                row[f"growth_{int(growth_rate*100)}"] = round(irr_result["gross_irr"], 1)
            
            results.append(row)
        
        return {
            "entry_multiple": entry_ev_ebitda,
            "entry_equity": round(entry_equity, 0),
            "sensitivity_matrix": results,
            "base_case_irr": results[len(results)//2][f"growth_{int(ebitda_growth_range[len(ebitda_growth_range)//2]*100)}"] if results else 0
        }
    
    def generate_investment_memo(self, lbo_structure: Dict,
                                projections: List[Dict],
                                irr_analysis: Dict) -> Dict:
        """Generate investment committee memo summary"""
        
        return {
            "executive_summary": {
                "target": self.target.company_name if self.target else "Unknown",
                "investment_thesis": f"Buy {self.target.industry if self.target else 'company'} leader at {lbo_structure.get('capital_structure', {}).get('equity_pct', 0)}% equity",
                "equity_investment": lbo_structure.get("sources", {}).get("equity", 0),
                "expected_irr": irr_analysis.get("gross_irr", 0),
                "money_multiple": irr_analysis.get("money_multiple", 0)
            },
            "market_opportunity": {
                "industry": self.target.industry if self.target else "Unknown",
                "market_size": "$XX billion",  # Would need external data
                "growth_rate": f"{self.target.growth_rate * 100 if self.target else 0}%"
            },
            "financial_overview": {
                "revenue": self.target.revenue if self.target else 0,
                "ebitda": self.target.ebitda if self.target else 0,
                "margin": f"{self.target.ebitda_margin * 100 if self.target else 0}%"
            },
            "capital_structure": lbo_structure.get("capital_structure", {}),
            "projected_returns": {
                "5_year_revenue": projections[-1]["revenue"] if projections else 0,
                "5_year_ebitda": projections[-1]["ebitda"] if projections else 0,
                "exit_ev": projections[-1]["ebitda"] * 8 if projections else 0,  # 8x exit multiple
                "gross_irr": irr_analysis.get("gross_irr", 0),
                "net_irr": irr_analysis.get("net_irr", 0)
            },
            "risk_factors": [
                "Leverage risk - high debt levels",
                "Market risk - exit multiple compression",
                "Operational risk - execution of growth plan",
                "Macro risk - economic downturn impact"
            ],
            "recommendation": "PROCEED" if irr_analysis.get("gross_irr", 0) > 20 else "CONDITIONAL" if irr_analysis.get("gross_irr", 0) > 15 else "REJECT"
        }
