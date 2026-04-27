"""Yield Hunter - Find optimal dividend income opportunities"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DividendStock:
    symbol: str
    name: str
    sector: str
    price: float
    dividend_yield: float
    annual_dividend: float
    payout_ratio: float
    years_of_growth: int
    dividend_growth_5y: float
    free_cash_flow: float
    debt_to_equity: float
    ex_dividend_date: datetime

class YieldHunter:
    """Find and analyze dividend income opportunities"""
    
    def __init__(self):
        self.stocks: List[DividendStock] = []
    
    def add_stock(self, stock: DividendStock):
        """Add dividend stock to tracker"""
        self.stocks.append(stock)
    
    def calculate_yield_quality_score(self, stock: DividendStock) -> Dict:
        """Calculate quality score for dividend stock (0-100)"""
        score = 50  # Base score
        
        # Yield attractiveness (max 20 points)
        if 0.03 <= stock.dividend_yield <= 0.06:
            score += 20  # Sweet spot
        elif 0.02 <= stock.dividend_yield < 0.03:
            score += 10
        elif stock.dividend_yield > 0.08:
            score -= 10  # Too high, suspicious
        
        # Payout ratio safety (max 20 points)
        if stock.payout_ratio <= 0.50:
            score += 20
        elif stock.payout_ratio <= 0.60:
            score += 15
        elif stock.payout_ratio <= 0.75:
            score += 5
        else:
            score -= 15
        
        # Growth track record (max 15 points)
        if stock.years_of_growth >= 25:
            score += 15  # Aristocrat
        elif stock.years_of_growth >= 10:
            score += 10
        elif stock.years_of_growth >= 5:
            score += 5
        
        # Growth rate (max 10 points)
        if stock.dividend_growth_5y > 0.07:
            score += 10
        elif stock.dividend_growth_5y > 0.05:
            score += 7
        elif stock.dividend_growth_5y > 0.03:
            score += 3
        
        # Financial health (max 15 points)
        if stock.debt_to_equity < 0.5:
            score += 15
        elif stock.debt_to_equity < 1.0:
            score += 10
        elif stock.debt_to_equity < 1.5:
            score += 5
        else:
            score -= 5
        
        # FCF coverage (max 10 points)
        if stock.free_cash_flow > stock.annual_dividend * 1.5:
            score += 10
        elif stock.free_cash_flow > stock.annual_dividend:
            score += 5
        
        final_score = max(0, min(100, score))
        
        return {
            "symbol": stock.symbol,
            "name": stock.name,
            "quality_score": round(final_score, 1),
            "yield_grade": "A" if final_score >= 80 else "B" if final_score >= 65 else "C" if final_score >= 50 else "D",
            "dividend_safety": "EXCELLENT" if stock.payout_ratio < 0.50 and stock.years_of_growth > 10 else "GOOD" if stock.payout_ratio < 0.65 else "FAIR" if stock.payout_ratio < 0.80 else "RISKY",
            "attributes": {
                "yield": round(stock.dividend_yield * 100, 2),
                "payout_ratio": round(stock.payout_ratio * 100, 1),
                "years_of_growth": stock.years_of_growth,
                "growth_rate_5y": round(stock.dividend_growth_5y * 100, 1),
                "debt_to_equity": round(stock.debt_to_equity, 2)
            }
        }
    
    def screen_dividend_stocks(self, min_yield: float = 0.025, 
                               max_payout: float = 0.75,
                               min_years_growth: int = 5) -> List[Dict]:
        """Screen stocks based on dividend criteria"""
        results = []
        
        for stock in self.stocks:
            if stock.dividend_yield < min_yield:
                continue
            if stock.payout_ratio > max_payout:
                continue
            if stock.years_of_growth < min_years_growth:
                continue
            
            quality = self.calculate_yield_quality_score(stock)
            results.append({
                "symbol": stock.symbol,
                "name": stock.name,
                "sector": stock.sector,
                **quality,
                "annual_income_per_10k": round(10000 * stock.dividend_yield, 2)
            })
        
        return sorted(results, key=lambda x: x["quality_score"], reverse=True)
    
    def get_upcoming_ex_dividends(self, days_ahead: int = 30) -> List[Dict]:
        """Get stocks with upcoming ex-dividend dates"""
        cutoff = datetime.utcnow().timestamp() + (days_ahead * 86400)
        
        upcoming = []
        for stock in self.stocks:
            if stock.ex_dividend_date.timestamp() < cutoff:
                days_until = (stock.ex_dividend_date - datetime.utcnow()).days
                
                upcoming.append({
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "ex_dividend_date": stock.ex_dividend_date.strftime("%Y-%m-%d"),
                    "days_until": days_until,
                    "dividend_per_share": round(stock.annual_dividend / 4, 2),  # Assuming quarterly
                    "yield": round(stock.dividend_yield * 100, 2),
                    "action": "BUY_BEFORE" if days_until > 0 else "TOO_LATE"
                })
        
        return sorted(upcoming, key=lambda x: x["days_until"])
    
    def build_income_portfolio(self, capital: float, 
                               target_yield: float = 0.04) -> Dict:
        """Build diversified dividend income portfolio"""
        # Get quality dividend stocks
        candidates = self.screen_dividend_stocks(min_yield=0.03, max_payout=0.70)
        
        if not candidates:
            return {"error": "No suitable dividend stocks found"}
        
        # Select top 10 diversified by sector
        selected = []
        sectors_used = set()
        
        for stock in candidates:
            if stock["sector"] not in sectors_used or len(sectors_used) >= 5:
                selected.append(stock)
                sectors_used.add(stock["sector"])
            
            if len(selected) >= 10:
                break
        
        # Equal weight allocation
        allocation_per_stock = capital / len(selected)
        
        portfolio = []
        total_annual_income = 0
        
        for stock in selected:
            annual_income = allocation_per_stock * stock["attributes"]["yield"] / 100
            total_annual_income += annual_income
            
            portfolio.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "allocation": round(allocation_per_stock, 2),
                "yield": stock["attributes"]["yield"],
                "annual_income": round(annual_income, 2),
                "quality_grade": stock["yield_grade"]
            })
        
        portfolio_yield = (total_annual_income / capital) * 100 if capital > 0 else 0
        
        return {
            "total_capital": round(capital, 2),
            "target_yield": round(target_yield * 100, 2),
            "actual_portfolio_yield": round(portfolio_yield, 2),
            "number_of_positions": len(portfolio),
            "annual_income_projection": round(total_annual_income, 2),
            "monthly_income_estimate": round(total_annual_income / 12, 2),
            "holdings": portfolio,
            "diversification": {
                "sectors": len(sectors_used),
                "avg_quality": sum(ord(s["quality_grade"]) for s in portfolio) / len(portfolio)
            }
        }
