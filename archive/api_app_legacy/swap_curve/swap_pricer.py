"""Swap Pricer - Price interest rate swaps and analyze swap curves"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SwapRate:
    tenor: str  # 1Y, 2Y, 5Y, 10Y, etc.
    maturity_years: float
    rate: float  # Swap rate (fixed leg)

class SwapPricer:
    """Price interest rate swaps and analyze curve"""
    
    def __init__(self, currency: str = "USD"):
        self.currency = currency
        self.curve_points: List[SwapRate] = []
        self.discount_factors: Dict[float, float] = {}
    
    def add_curve_point(self, rate: SwapRate):
        """Add swap rate to curve"""
        self.curve_points.append(rate)
        self.curve_points.sort(key=lambda x: x.maturity_years)
    
    def calculate_forward_rate(self, start_year: float, end_year: float) -> Dict:
        """Calculate forward rate between two points"""
        # Find rates for start and end
        start_rate = None
        end_rate = None
        
        for point in self.curve_points:
            if abs(point.maturity_years - start_year) < 0.1:
                start_rate = point.rate
            if abs(point.maturity_years - end_year) < 0.1:
                end_rate = point.rate
        
        if start_rate is None or end_rate is None:
            return {"error": "Curve points not available"}
        
        # Simplified forward rate calculation
        # (1 + r2)^t2 = (1 + r1)^t1 * (1 + f)^(t2-t1)
        t1 = start_year
        t2 = end_year
        r1 = start_rate
        r2 = end_rate
        
        if t2 <= t1:
            return {"error": "Invalid tenor range"}
        
        # Solve for forward rate f
        try:
            forward = ((1 + r2) ** t2 / (1 + r1) ** t1) ** (1 / (t2 - t1)) - 1
        except:
            forward = 0
        
        return {
            "start_tenor": f"{int(start_year)}Y",
            "end_tenor": f"{int(end_year)}Y",
            "forward_rate": round(forward * 100, 3),
            "spot_start": round(start_rate * 100, 3),
            "spot_end": round(end_rate * 100, 3),
            "implied_direction": "RISING" if forward > r2 else "FALLING"
        }
    
    def calculate_swap_pv01(self, notional: float, maturity_years: float) -> Dict:
        """Calculate PV01 (value of 1bp change)"""
        # Simplified PV01: Notional * maturity * 0.0001
        pv01 = notional * maturity_years * 0.0001
        
        return {
            "notional": notional,
            "maturity_years": maturity_years,
            "pv01": round(pv01, 2),
            "interpretation": f"1bp rate change = ${pv01:,.0f} P&L"
        }
    
    def analyze_curve_shape(self) -> Dict:
        """Analyze swap curve shape"""
        if len(self.curve_points) < 2:
            return {"error": "Insufficient curve points"}
        
        rates = [p.rate for p in self.curve_points]
        tenors = [p.maturity_years for p in self.curve_points]
        
        # Calculate slopes
        short_end = rates[0]  # 1-2Y
        long_end = rates[-1]  # 30Y
        
        curve_slope = long_end - short_end
        
        # Find inflection points
        max_rate = max(rates)
        min_rate = min(rates)
        
        # Determine curve shape
        if curve_slope > 0.01:
            shape = "STEEP"
        elif curve_slope < -0.01:
            shape = "INVERTED"
        elif max_rate - min_rate < 0.005:
            shape = "FLAT"
        else:
            shape = "HUMPED"
        
        # Calculate butterfly spread (2s-5s-10s)
        rate_2y = next((r for r in self.curve_points if r.maturity_years == 2), None)
        rate_5y = next((r for r in self.curve_points if r.maturity_years == 5), None)
        rate_10y = next((r for r in self.curve_points if r.maturity_years == 10), None)
        
        butterfly = None
        if rate_2y and rate_5y and rate_10y:
            butterfly = 2 * rate_5y.rate - rate_2y.rate - rate_10y.rate
        
        return {
            "shape": shape,
            "short_end_rate": round(short_end * 100, 3),
            "long_end_rate": round(long_end * 100, 3),
            "slope_bps": round(curve_slope * 10000, 1),
            "curve_range_bps": round((max_rate - min_rate) * 10000, 1),
            "butterfly_spread": round(butterfly * 10000, 1) if butterfly else None,
            "trading_implication": self._curve_trading_implication(shape)
        }
    
    def _curve_trading_implication(self, shape: str) -> str:
        """Generate trading implication from curve shape"""
        implications = {
            "STEEP": "Expecting rate hikes - consider payer swaps or steepeners",
            "INVERTED": "Expecting rate cuts - consider receiver swaps or flatteners",
            "FLAT": "Neutral environment - range-bound strategies appropriate",
            "HUMPED": "Mid-curve dislocation - butterfly trades attractive"
        }
        return implications.get(shape, "Neutral")
    
    def calculate_carry_roll(self, swap_rate: float, maturity: float) -> Dict:
        """Calculate carry and roll-down for a swap position"""
        # Find next shorter maturity rate
        shorter = None
        for point in self.curve_points:
            if point.maturity_years < maturity:
                shorter = point
        
        if not shorter:
            return {"error": "Cannot calculate roll"}
        
        # Roll-down: as swap ages, it rolls down the curve
        # Assuming linear interpolation between points
        roll_down = (swap_rate - shorter.rate) / (maturity - shorter.maturity_years)
        
        # Carry = swap rate - funding rate (simplified as short rate)
        funding_rate = self.curve_points[0].rate if self.curve_points else 0.03
        carry = swap_rate - funding_rate
        
        total_return = carry + roll_down
        
        return {
            "swap_rate": round(swap_rate * 100, 3),
            "funding_rate": round(funding_rate * 100, 3),
            "carry_bps": round(carry * 10000, 1),
            "roll_down_bps": round(roll_down * 10000, 1),
            "total_expected_return_bps": round(total_return * 10000, 1),
            "annualized_carry": round(carry * 100, 3),
            "strategy": "RECEIVER" if total_return > 0 else "PAYER"
        }
    
    def get_curve_summary(self) -> Dict:
        """Get comprehensive curve summary"""
        shape = self.analyze_curve_shape()
        
        # Key rates
        key_tenors = [2, 5, 10, 30]
        key_rates = {}
        
        for tenor in key_tenors:
            rate = next((r for r in self.curve_points if abs(r.maturity_years - tenor) < 0.5), None)
            if rate:
                key_rates[f"{tenor}Y"] = round(rate.rate * 100, 3)
        
        # Spreads
        spread_2s10s = None
        spread_5s30s = None
        
        rate_2y = next((r for r in self.curve_points if abs(r.maturity_years - 2) < 0.5), None)
        rate_5y = next((r for r in self.curve_points if abs(r.maturity_years - 5) < 0.5), None)
        rate_10y = next((r for r in self.curve_points if abs(r.maturity_years - 10) < 0.5), None)
        rate_30y = next((r for r in self.curve_points if abs(r.maturity_years - 30) < 0.5), None)
        
        if rate_2y and rate_10y:
            spread_2s10s = round((rate_10y.rate - rate_2y.rate) * 10000, 1)
        if rate_5y and rate_30y:
            spread_5s30s = round((rate_30y.rate - rate_5y.rate) * 10000, 1)
        
        return {
            "currency": self.currency,
            "curve_shape": shape.get("shape", "UNKNOWN"),
            "key_rates": key_rates,
            "spreads": {
                "2s10s_bps": spread_2s10s,
                "5s30s_bps": spread_5s30s
            },
            "trading_implication": shape.get("trading_implication", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
