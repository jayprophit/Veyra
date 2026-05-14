"""Returns Calculator - Calculate TWR, MWR, and other return metrics"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import math

@dataclass
class CashFlow:
    date: datetime
    amount: float  # Positive = inflow, Negative = outflow

@dataclass
class PeriodReturn:
    start_date: datetime
    end_date: datetime
    start_value: float
    end_value: float
    cash_flows: List[CashFlow]

class ReturnsCalculator:
    """Calculate various return metrics"""
    
    def calculate_twr(self, periods: List[PeriodReturn]) -> Dict:
        """Calculate Time-Weighted Return (TWR)"""
        if not periods:
            return {"error": "No periods provided"}
        
        # Calculate sub-period returns
        sub_period_returns = []
        
        for period in periods:
            # Adjust for cash flows
            adjusted_start = period.start_value
            adjusted_end = period.end_value
            
            # Adjust start for inflows (add back)
            # Adjust end for outflows (add back)
            for cf in period.cash_flows:
                if cf.amount > 0:  # Inflow
                    adjusted_end -= cf.amount
                else:  # Outflow
                    adjusted_start -= abs(cf.amount)
            
            if adjusted_start == 0:
                sub_return = 0
            else:
                sub_return = (adjusted_end - adjusted_start) / adjusted_start
            
            sub_period_returns.append(sub_return)
        
        # Chain-link the returns
        twr = 1.0
        for ret in sub_period_returns:
            twr *= (1 + ret)
        
        twr -= 1  # Convert to percentage return
        
        # Annualize if multiple years
        total_days = sum((p.end_date - p.start_date).days for p in periods)
        years = total_days / 365.25
        
        if years > 1:
            annualized_twr = (1 + twr) ** (1 / years) - 1
        else:
            annualized_twr = twr
        
        return {
            "twr": round(twr * 100, 2),
            "annualized_twr": round(annualized_twr * 100, 2),
            "sub_period_count": len(sub_period_returns),
            "total_period_years": round(years, 2),
            "methodology": "Time-Weighted (eliminates cash flow impact)"
        }
    
    def calculate_mwr(self, periods: List[PeriodReturn]) -> Dict:
        """Calculate Money-Weighted Return (MWR) using IRR"""
        if not periods:
            return {"error": "No periods provided"}
        
        # Simplified MWR calculation (XIRR approximation)
        total_start = periods[0].start_value
        total_end = periods[-1].end_value
        
        # Sum all cash flows
        total_cf = sum(cf.amount for p in periods for cf in p.cash_flows)
        
        # Simple IRR approximation
        if total_start == 0:
            return {"error": "Cannot calculate MWR with zero start value"}
        
        total_days = sum((p.end_date - p.start_date).days for p in periods)
        years = total_days / 365.25
        
        # MWR ≈ (End Value - Start Value - Net Cash Flows) / Start Value
        mwr = (total_end - total_start - total_cf) / total_start
        
        if years > 0:
            annualized_mwr = (1 + mwr) ** (1 / years) - 1
        else:
            annualized_mwr = mwr
        
        return {
            "mwr": round(mwr * 100, 2),
            "annualized_mwr": round(annualized_mwr * 100, 2),
            "total_cash_flows": round(total_cf, 2),
            "methodology": "Money-Weighted (IRR - includes cash flow impact)"
        }
    
    def calculate_sharpe_ratio(self, returns: List[float], 
                               risk_free_rate: float = 0.03) -> Dict:
        """Calculate Sharpe ratio"""
        if not returns or len(returns) < 2:
            return {"error": "Insufficient return data"}
        
        avg_return = sum(returns) / len(returns)
        
        # Calculate standard deviation
        variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return {"error": "Zero volatility - cannot calculate Sharpe"}
        
        sharpe = (avg_return - risk_free_rate) / std_dev
        
        # Annualize (assuming monthly returns)
        annualized_sharpe = sharpe * math.sqrt(12)
        
        return {
            "periodic_sharpe": round(sharpe, 3),
            "annualized_sharpe": round(annualized_sharpe, 2),
            "average_return": round(avg_return * 100, 2),
            "volatility": round(std_dev * 100, 2),
            "risk_free_rate": round(risk_free_rate * 100, 2)
        }
    
    def calculate_sortino_ratio(self, returns: List[float],
                                risk_free_rate: float = 0.03,
                                target_return: float = 0) -> Dict:
        """Calculate Sortino ratio (downside risk only)"""
        if not returns or len(returns) < 2:
            return {"error": "Insufficient return data"}
        
        avg_return = sum(returns) / len(returns)
        
        # Calculate downside deviation (only negative returns vs target)
        downside_returns = [min(0, r - target_return) for r in returns]
        downside_variance = sum(r ** 2 for r in downside_returns) / len(returns)
        downside_deviation = math.sqrt(downside_variance)
        
        if downside_deviation == 0:
            return {"error": "Zero downside deviation"}
        
        sortino = (avg_return - risk_free_rate) / downside_deviation
        
        return {
            "sortino_ratio": round(sortino, 3),
            "average_return": round(avg_return * 100, 2),
            "downside_deviation": round(downside_deviation * 100, 2),
            "downside_returns_count": sum(1 for r in returns if r < target_return)
        }
    
    def calculate_calmar_ratio(self, returns: List[float],
                               max_drawdown: float) -> Dict:
        """Calculate Calmar ratio (return / max drawdown)"""
        if not returns:
            return {"error": "No return data"}
        
        if max_drawdown >= 0:
            return {"error": "Max drawdown must be negative"}
        
        annualized_return = sum(returns) / len(returns) * 12  # Assume monthly
        
        calmar = annualized_return / abs(max_drawdown)
        
        return {
            "calmar_ratio": round(calmar, 2),
            "annualized_return": round(annualized_return * 100, 2),
            "max_drawdown": round(max_drawdown * 100, 2),
            "interpretation": "EXCELLENT" if calmar > 3 else "GOOD" if calmar > 2 else "FAIR" if calmar > 1 else "POOR"
        }
    
    def calculate_max_drawdown(self, portfolio_values: List[float]) -> Dict:
        """Calculate maximum drawdown"""
        if not portfolio_values or len(portfolio_values) < 2:
            return {"error": "Insufficient data"}
        
        peak = portfolio_values[0]
        max_dd = 0
        peak_date_idx = 0
        trough_date_idx = 0
        
        for i, value in enumerate(portfolio_values):
            if value > peak:
                peak = value
                peak_date_idx = i
            
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
                trough_date_idx = i
        
        return {
            "max_drawdown": round(max_dd * 100, 2),
            "max_drawdown_pct": f"-{round(max_dd * 100, 2)}%",
            "recovery_needed": round((1 / (1 - max_dd) - 1) * 100, 1),
            "peak_to_trough_periods": trough_date_idx - peak_date_idx if max_dd > 0 else 0
        }
    
    def generate_performance_report(self, periods: List[PeriodReturn],
                                   benchmark_returns: List[float] = None) -> Dict:
        """Generate comprehensive performance report"""
        # Extract simple returns list
        returns = []
        for p in periods:
            if p.start_value > 0:
                ret = (p.end_value - p.start_value) / p.start_value
                returns.append(ret)
        
        # Calculate all metrics
        twr = self.calculate_twr(periods)
        mwr = self.calculate_mwr(periods)
        sharpe = self.calculate_sharpe_ratio(returns)
        sortino = self.calculate_sortino_ratio(returns)
        
        # Get portfolio values for drawdown
        values = [p.end_value for p in periods]
        max_dd = self.calculate_max_drawdown(values)
        
        # Calmar if we have max drawdown
        calmar = None
        if "error" not in max_dd:
            calmar = self.calculate_calmar_ratio(returns, max_dd["max_drawdown"] / 100)
        
        # Benchmark comparison
        alpha = 0
        beta = 1
        tracking_error = 0
        
        if benchmark_returns and len(benchmark_returns) == len(returns):
            # Calculate alpha and beta (simplified)
            bench_avg = sum(benchmark_returns) / len(benchmark_returns)
            port_avg = sum(returns) / len(returns)
            alpha = port_avg - bench_avg
            
            # Calculate tracking error
            diff_squared = sum((r - b) ** 2 for r, b in zip(returns, benchmark_returns))
            tracking_error = math.sqrt(diff_squared / len(returns))
        
        return {
            "summary": {
                "total_return_twr": twr.get("twr", 0),
                "total_return_mwr": mwr.get("mwr", 0),
                "annualized_return": twr.get("annualized_twr", 0),
                "volatility": sharpe.get("volatility", 0),
                "sharpe_ratio": sharpe.get("annualized_sharpe", 0),
                "sortino_ratio": sortino.get("sortino_ratio", 0),
                "max_drawdown": max_dd.get("max_drawdown", 0),
                "calmar_ratio": calmar.get("calmar_ratio", 0) if calmar else None
            },
            "benchmark_comparison": {
                "alpha": round(alpha * 100, 2),
                "beta": round(beta, 2),
                "tracking_error": round(tracking_error * 100, 2),
                "information_ratio": round(alpha / tracking_error, 2) if tracking_error > 0 else 0
            },
            "detailed": {
                "twr": twr,
                "mwr": mwr,
                "sharpe": sharpe,
                "sortino": sortino,
                "max_drawdown": max_dd,
                "calmar": calmar
            }
        }
