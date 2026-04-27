"""Financial Ratio Analyzer - Calculate and analyze financial ratios"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class FinancialData:
    revenue: float
    net_income: float
    total_assets: float
    total_debt: float
    shareholders_equity: float
    current_assets: float
    current_liabilities: float
    operating_cash_flow: float
    shares_outstanding: float
    stock_price: float

class FinancialRatioAnalyzer:
    """Calculate key financial ratios for stock analysis"""
    
    def __init__(self):
        self.sector_benchmarks = {
            "technology": {"pe": 25, "pb": 5, "debt_equity": 0.5},
            "financials": {"pe": 12, "pb": 1, "debt_equity": 2.0},
            "healthcare": {"pe": 20, "pb": 4, "debt_equity": 0.6},
            "consumer": {"pe": 18, "pb": 3, "debt_equity": 0.8},
            "energy": {"pe": 15, "pb": 1.5, "debt_equity": 0.7},
            "industrials": {"pe": 16, "pb": 2.5, "debt_equity": 0.9}
        }
    
    def calculate_profitability_ratios(self, data: FinancialData) -> Dict:
        """Calculate profitability ratios"""
        ratios = {}
        
        # Net Profit Margin
        ratios["net_profit_margin"] = round(
            (data.net_income / data.revenue) * 100, 2
        ) if data.revenue > 0 else 0
        
        # Return on Assets (ROA)
        ratios["roa"] = round(
            (data.net_income / data.total_assets) * 100, 2
        ) if data.total_assets > 0 else 0
        
        # Return on Equity (ROE)
        ratios["roe"] = round(
            (data.net_income / data.shareholders_equity) * 100, 2
        ) if data.shareholders_equity > 0 else 0
        
        # Return on Invested Capital (ROIC)
        invested_capital = data.total_assets - data.current_liabilities
        ratios["roic"] = round(
            (data.net_income / invested_capital) * 100, 2
        ) if invested_capital > 0 else 0
        
        return ratios
    
    def calculate_leverage_ratios(self, data: FinancialData) -> Dict:
        """Calculate leverage ratios"""
        ratios = {}
        
        # Debt-to-Equity
        ratios["debt_to_equity"] = round(
            data.total_debt / data.shareholders_equity, 2
        ) if data.shareholders_equity > 0 else 0
        
        # Debt-to-Assets
        ratios["debt_to_assets"] = round(
            data.total_debt / data.total_assets, 2
        ) if data.total_assets > 0 else 0
        
        # Equity Multiplier
        ratios["equity_multiplier"] = round(
            data.total_assets / data.shareholders_equity, 2
        ) if data.shareholders_equity > 0 else 0
        
        # Interest Coverage (simulated)
        ebit = data.net_income * 1.3  # Approximation
        interest_expense = data.total_debt * 0.05  # 5% rate assumption
        ratios["interest_coverage"] = round(
            ebit / interest_expense, 2
        ) if interest_expense > 0 else 0
        
        return ratios
    
    def calculate_liquidity_ratios(self, data: FinancialData) -> Dict:
        """Calculate liquidity ratios"""
        ratios = {}
        
        # Current Ratio
        ratios["current_ratio"] = round(
            data.current_assets / data.current_liabilities, 2
        ) if data.current_liabilities > 0 else 0
        
        # Quick Ratio (excludes inventory)
        quick_assets = data.current_assets * 0.7  # Approximation
        ratios["quick_ratio"] = round(
            quick_assets / data.current_liabilities, 2
        ) if data.current_liabilities > 0 else 0
        
        # Cash Ratio (simulated)
        cash = data.current_assets * 0.3
        ratios["cash_ratio"] = round(
            cash / data.current_liabilities, 2
        ) if data.current_liabilities > 0 else 0
        
        return ratios
    
    def calculate_efficiency_ratios(self, data: FinancialData) -> Dict:
        """Calculate efficiency ratios"""
        ratios = {}
        
        # Asset Turnover
        ratios["asset_turnover"] = round(
            data.revenue / data.total_assets, 2
        ) if data.total_assets > 0 else 0
        
        # Cash Conversion Cycle components (simplified)
        ratios["receivables_turnover"] = round(
            data.revenue / (data.current_assets * 0.3), 2
        ) if data.current_assets > 0 else 0
        
        # Operating Cash Flow Ratio
        ratios["ocf_ratio"] = round(
            data.operating_cash_flow / data.current_liabilities, 2
        ) if data.current_liabilities > 0 else 0
        
        return ratios
    
    def calculate_valuation_ratios(self, data: FinancialData) -> Dict:
        """Calculate market valuation ratios"""
        ratios = {}
        
        market_cap = data.stock_price * data.shares_outstanding
        
        # P/E Ratio
        eps = data.net_income / data.shares_outstanding if data.shares_outstanding > 0 else 0
        ratios["pe_ratio"] = round(
            data.stock_price / eps, 2
        ) if eps > 0 else 0
        
        # P/B Ratio
        book_value_per_share = data.shareholders_equity / data.shares_outstanding if data.shares_outstanding > 0 else 0
        ratios["pb_ratio"] = round(
            data.stock_price / book_value_per_share, 2
        ) if book_value_per_share > 0 else 0
        
        # P/S Ratio
        revenue_per_share = data.revenue / data.shares_outstanding if data.shares_outstanding > 0 else 0
        ratios["ps_ratio"] = round(
            data.stock_price / revenue_per_share, 2
        ) if revenue_per_share > 0 else 0
        
        # EV/EBITDA (simplified)
        ev = market_cap + data.total_debt
        ebitda = data.net_income * 1.5  # Rough approximation
        ratios["ev_ebitda"] = round(
            ev / ebitda, 2
        ) if ebitda > 0 else 0
        
        # Dividend yield (if applicable)
        ratios["fcf_yield"] = round(
            (data.operating_cash_flow / market_cap) * 100, 2
        ) if market_cap > 0 else 0
        
        return ratios
    
    def compare_to_sector(self, ratios: Dict, sector: str) -> Dict:
        """Compare ratios to sector benchmarks"""
        if sector not in self.sector_benchmarks:
            return {"error": "Sector not found"}
        
        benchmarks = self.sector_benchmarks[sector]
        comparison = {}
        
        # P/E comparison
        if "pe_ratio" in ratios:
            pe = ratios["pe_ratio"]
            bench_pe = benchmarks["pe"]
            comparison["pe_vs_sector"] = round((pe / bench_pe - 1) * 100, 1)
            comparison["pe_valuation"] = "EXPENSIVE" if pe > bench_pe * 1.2 else "CHEAP" if pe < bench_pe * 0.8 else "FAIR"
        
        # P/B comparison
        if "pb_ratio" in ratios:
            pb = ratios["pb_ratio"]
            bench_pb = benchmarks["pb"]
            comparison["pb_vs_sector"] = round((pb / bench_pb - 1) * 100, 1)
        
        # Debt comparison
        if "debt_to_equity" in ratios:
            de = ratios["debt_to_equity"]
            bench_de = benchmarks["debt_equity"]
            comparison["leverage_vs_sector"] = round((de / bench_de - 1) * 100, 1)
            comparison["leverage_assessment"] = "HIGH" if de > bench_de * 1.5 else "LOW" if de < bench_de * 0.5 else "NORMAL"
        
        return comparison
    
    def get_comprehensive_analysis(self, data: FinancialData, 
                                 sector: str) -> Dict:
        """Get comprehensive ratio analysis"""
        all_ratios = {}
        all_ratios.update(self.calculate_profitability_ratios(data))
        all_ratios.update(self.calculate_leverage_ratios(data))
        all_ratios.update(self.calculate_liquidity_ratios(data))
        all_ratios.update(self.calculate_efficiency_ratios(data))
        all_ratios.update(self.calculate_valuation_ratios(data))
        
        comparison = self.compare_to_sector(all_ratios, sector)
        
        # Overall health score
        health_score = self._calculate_health_score(all_ratios)
        
        return {
            "financial_ratios": all_ratios,
            "sector_comparison": comparison,
            "health_score": health_score,
            "health_grade": self._get_health_grade(health_score),
            "strengths": self._identify_strengths(all_ratios),
            "weaknesses": self._identify_weaknesses(all_ratios),
            "investment_quality": self._assess_quality(all_ratios, comparison)
        }
    
    def _calculate_health_score(self, ratios: Dict) -> int:
        """Calculate overall health score 0-100"""
        score = 50  # Base score
        
        # Profitability (+20 max)
        if ratios.get("roe", 0) > 15:
            score += 10
        if ratios.get("net_profit_margin", 0) > 10:
            score += 10
        
        # Leverage (+20 max)
        if ratios.get("debt_to_equity", 1) < 0.5:
            score += 10
        if ratios.get("current_ratio", 1) > 1.5:
            score += 10
        
        # Efficiency (+10 max)
        if ratios.get("roic", 0) > 10:
            score += 10
        
        return min(100, score)
    
    def _get_health_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 80:
            return "A"
        elif score >= 65:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 35:
            return "D"
        return "F"
    
    def _identify_strengths(self, ratios: Dict) -> List[str]:
        """Identify financial strengths"""
        strengths = []
        
        if ratios.get("roe", 0) > 15:
            strengths.append("High Return on Equity")
        if ratios.get("debt_to_equity", 1) < 0.3:
            strengths.append("Low Debt Levels")
        if ratios.get("current_ratio", 0) > 2:
            strengths.append("Strong Liquidity Position")
        if ratios.get("net_profit_margin", 0) > 15:
            strengths.append("Excellent Profitability")
        if ratios.get("pe_ratio", 100) < 15:
            strengths.append("Attractive Valuation")
        
        return strengths
    
    def _identify_weaknesses(self, ratios: Dict) -> List[str]:
        """Identify financial weaknesses"""
        weaknesses = []
        
        if ratios.get("debt_to_equity", 0) > 1.5:
            weaknesses.append("High Leverage")
        if ratios.get("current_ratio", 10) < 1:
            weaknesses.append("Liquidity Concerns")
        if ratios.get("roe", 100) < 5:
            weaknesses.append("Low Profitability")
        if ratios.get("pe_ratio", 0) > 40:
            weaknesses.append("Expensive Valuation")
        if ratios.get("net_profit_margin", 100) < 3:
            weaknesses.append("Thin Margins")
        
        return weaknesses
    
    def _assess_quality(self, ratios: Dict, comparison: Dict) -> str:
        """Assess overall investment quality"""
        quality_score = 0
        
        # Valuation
        if ratios.get("pe_ratio", 100) < 20:
            quality_score += 1
        
        # Profitability
        if ratios.get("roe", 0) > 10:
            quality_score += 1
        
        # Financial health
        if ratios.get("debt_to_equity", 10) < 1:
            quality_score += 1
        
        if quality_score >= 3:
            return "HIGH_QUALITY"
        elif quality_score >= 2:
            return "MEDIUM_QUALITY"
        return "SPECULATIVE"
