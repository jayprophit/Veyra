"""Triangular Arbitrage - Cross-currency arbitrage"""
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class TriangularOpportunity:
    path: List[str]  # e.g., ["USD", "EUR", "GBP", "USD"]
    profit_pct: float
    steps: List[Dict]
    required_capital: float

class TriangularArbitrage:
    """Find triangular arbitrage opportunities in forex/crypto"""
    
    def __init__(self):
        self.rates: Dict[str, float] = {}  # e.g., "EURUSD": 1.0850
    
    def add_rate(self, pair: str, rate: float):
        """Add exchange rate"""
        self.rates[pair] = rate
        # Add inverse
        base, quote = self._parse_pair(pair)
        inverse_pair = f"{quote}{base}"
        self.rates[inverse_pair] = 1 / rate
    
    def _parse_pair(self, pair: str) -> Tuple[str, str]:
        """Parse currency pair"""
        if len(pair) == 6:
            return pair[:3], pair[3:]
        elif "_" in pair:
            return pair.split("_")
        return pair[:3], pair[3:]
    
    def find_triangular_opportunities(self, base_currency: str = "USD") -> List[TriangularOpportunity]:
        """Find triangular arbitrage starting from base currency"""
        opportunities = []
        
        # Get all currencies
        currencies = set()
        for pair in self.rates:
            base, quote = self._parse_pair(pair)
            currencies.add(base)
            currencies.add(quote)
        
        currencies = list(currencies)
        
        # Check all possible triangles: A -> B -> C -> A
        for i, b in enumerate(currencies):
            if b == base_currency:
                continue
            for c in currencies[i+1:]:
                if c == base_currency:
                    continue
                
                # Check path: base -> b -> c -> base
                opp = self._check_triangle(base_currency, b, c)
                if opp and opp.profit_pct > 0.01:  # 0.01% profit
                    opportunities.append(opp)
        
        return sorted(opportunities, key=lambda x: x.profit_pct, reverse=True)
    
    def _check_triangle(self, a: str, b: str, c: str) -> TriangularOpportunity:
        """Check if A -> B -> C -> A is profitable"""
        # Find rates
        rate_ab = self._get_rate(a, b)
        rate_bc = self._get_rate(b, c)
        rate_ca = self._get_rate(c, a)
        
        if not all([rate_ab, rate_bc, rate_ca]):
            return None
        
        # Calculate: Start with 1 unit of A
        amount_b = 1 * rate_ab
        amount_c = amount_b * rate_bc
        amount_a_final = amount_c * rate_ca
        
        profit_pct = (amount_a_final - 1) * 100
        
        if profit_pct <= 0:
            return None
        
        return TriangularOpportunity(
            path=[a, b, c, a],
            profit_pct=round(profit_pct, 4),
            steps=[
                {"from": a, "to": b, "rate": rate_ab, "amount": 1},
                {"from": b, "to": c, "rate": rate_bc, "amount": amount_b},
                {"from": c, "to": a, "rate": rate_ca, "amount": amount_c}
            ],
            required_capital=1000  # Minimum to overcome fees
        )
    
    def _get_rate(self, from_curr: str, to_curr: str) -> float:
        """Get exchange rate between two currencies"""
        direct = f"{from_curr}{to_curr}"
        if direct in self.rates:
            return self.rates[direct]
        
        # Try via USD
        if from_curr != "USD" and to_curr != "USD":
            rate_from_usd = self._get_rate(from_curr, "USD")
            rate_to_usd = self._get_rate(to_curr, "USD")
            if rate_from_usd and rate_to_usd:
                return rate_to_usd / rate_from_usd
        
        return None
    
    def get_implied_rates(self) -> Dict[str, float]:
        """Calculate implied cross rates from USD pairs"""
        implied = {}
        
        usd_pairs = {k: v for k, v in self.rates.items() if "USD" in k}
        
        # Get all currencies with USD pairs
        currencies = set()
        for pair in usd_pairs:
            if pair.startswith("USD"):
                currencies.add(pair[3:])
            else:
                currencies.add(pair[:3])
        
        # Calculate implied crosses
        currencies = list(currencies)
        for i, c1 in enumerate(currencies):
            for c2 in currencies[i+1:]:
                # c1/USD and c2/USD -> c1/c2
                rate1 = self._get_rate(c1, "USD")
                rate2 = self._get_rate(c2, "USD")
                
                if rate1 and rate2:
                    implied[f"{c1}{c2}"] = rate1 / rate2
                    implied[f"{c2}{c1}"] = rate2 / rate1
        
        return implied
    
    def compare_implied_vs_actual(self) -> List[Dict]:
        """Compare implied rates with actual quoted rates"""
        implied = self.get_implied_rates()
        discrepancies = []
        
        for pair, implied_rate in implied.items():
            if pair in self.rates:
                actual_rate = self.rates[pair]
                diff_pct = abs(implied_rate - actual_rate) / actual_rate * 100
                
                if diff_pct > 0.1:  # 0.1% discrepancy
                    discrepancies.append({
                        "pair": pair,
                        "implied_rate": round(implied_rate, 6),
                        "actual_rate": round(actual_rate, 6),
                        "difference_pct": round(diff_pct, 3),
                        "opportunity": implied_rate > actual_rate
                    })
        
        return sorted(discrepancies, key=lambda x: x["difference_pct"], reverse=True)
    
    def calculate_required_speed(self, opportunity: TriangularOpportunity) -> Dict:
        """Calculate execution speed requirements"""
        # Higher profit = more time available
        profit_pct = opportunity.profit_pct
        
        if profit_pct > 0.5:
            time_window_ms = 5000  # 5 seconds
            urgency = "LOW"
        elif profit_pct > 0.2:
            time_window_ms = 2000  # 2 seconds
            urgency = "MEDIUM"
        else:
            time_window_ms = 500  # 500ms
            urgency = "CRITICAL"
        
        return {
            "profit_pct": profit_pct,
            "max_execution_time_ms": time_window_ms,
            "urgency": urgency,
            "recommended_setup": "API_TRADING" if urgency == "CRITICAL" else "MANUAL_OK",
            "slippage_tolerance": round(profit_pct / 3, 3)  # 1/3 of profit
        }
