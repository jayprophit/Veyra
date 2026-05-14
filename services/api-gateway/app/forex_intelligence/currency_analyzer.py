"""Currency Analyzer - Forex pair analysis and strength metrics"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"
    AUD = "AUD"
    CAD = "CAD"
    NZD = "NZD"

@dataclass
class CurrencyData:
    currency: Currency
    interest_rate: float
    inflation_rate: float
    gdp_growth: float
    unemployment_rate: float
    trade_balance_pct_gdp: float
    current_account_pct_gdp: float
    central_bank_policy: str  # hawkish, dovish, neutral

class CurrencyAnalyzer:
    """Analyze currency strength and forex pairs"""
    
    def __init__(self):
        self.currencies: Dict[Currency, CurrencyData] = {}
        self.major_pairs = [
            (Currency.EUR, Currency.USD),
            (Currency.GBP, Currency.USD),
            (Currency.USD, Currency.JPY),
            (Currency.USD, Currency.CHF),
            (Currency.AUD, Currency.USD),
            (Currency.USD, Currency.CAD),
            (Currency.NZD, Currency.USD),
        ]
    
    def add_currency_data(self, data: CurrencyData):
        """Add currency economic data"""
        self.currencies[data.currency] = data
    
    def calculate_currency_strength(self, currency: Currency) -> Dict:
        """Calculate fundamental strength score for a currency"""
        if currency not in self.currencies:
            return {"error": "Currency data not available"}
        
        data = self.currencies[currency]
        score = 50  # Base score
        
        # Interest rate differential (max +/- 20 points)
        rate_score = min(20, max(-20, data.interest_rate * 10))
        score += rate_score
        
        # Inflation (moderate is good, too high or too low is bad)
        if 1.5 <= data.inflation_rate <= 2.5:
            score += 10
        elif data.inflation_rate > 4 or data.inflation_rate < 0:
            score -= 15
        
        # GDP growth (positive is good)
        if data.gdp_growth > 2:
            score += 10
        elif data.gdp_growth < 0:
            score -= 10
        
        # Unemployment (lower is better)
        if data.unemployment_rate < 4:
            score += 10
        elif data.unemployment_rate > 6:
            score -= 10
        
        # Trade balance surplus is positive
        if data.trade_balance_pct_gdp > 0:
            score += 5
        elif data.trade_balance_pct_gdp < -3:
            score -= 5
        
        # Central bank stance
        stance_bonus = {"hawkish": 5, "neutral": 0, "dovish": -5}
        score += stance_bonus.get(data.central_bank_policy, 0)
        
        return {
            "currency": currency.value,
            "strength_score": max(0, min(100, score)),
            "rating": "STRONG" if score > 70 else "MODERATE" if score > 50 else "WEAK",
            "components": {
                "interest_rate_impact": round(rate_score, 1),
                "inflation_status": "OPTIMAL" if 1.5 <= data.inflation_rate <= 2.5 else "CONCERN",
                "growth_momentum": "POSITIVE" if data.gdp_growth > 2 else "NEGATIVE" if data.gdp_growth < 0 else "STABLE",
                "central_bank_bias": data.central_bank_policy.upper()
            }
        }
    
    def analyze_currency_pair(self, base: Currency, quote: Currency) -> Dict:
        """Analyze a currency pair"""
        if base not in self.currencies or quote not in self.currencies:
            return {"error": "Insufficient data for pair analysis"}
        
        base_strength = self.calculate_currency_strength(base)
        quote_strength = self.calculate_currency_strength(quote)
        
        base_data = self.currencies[base]
        quote_data = self.currencies[quote]
        
        # Interest rate differential
        rate_diff = base_data.interest_rate - quote_data.interest_rate
        
        # Pair strength differential
        strength_diff = base_strength["strength_score"] - quote_strength["strength_score"]
        
        # Trend bias based on fundamentals
        if strength_diff > 15 and rate_diff > 0.5:
            bias = "BULLISH_BASE"
        elif strength_diff < -15 and rate_diff < -0.5:
            bias = "BULLISH_QUOTE"
        else:
            bias = "NEUTRAL_RANGE"
        
        pair_name = f"{base.value}{quote.value}"
        
        return {
            "pair": pair_name,
            "base_currency": base.value,
            "quote_currency": quote.value,
            "base_strength": base_strength["strength_score"],
            "quote_strength": quote_strength["strength_score"],
            "strength_differential": strength_diff,
            "interest_rate_differential": round(rate_diff * 100, 2),  # in bps
            "fundamental_bias": bias,
            "carry_attractive": rate_diff > 1.0,
            "volatility_estimate": "HIGH" if abs(strength_diff) < 10 else "MODERATE",
            "recommendation": "FAVOR_BASE" if bias == "BULLISH_BASE" else "FAVOR_QUOTE" if bias == "BULLISH_QUOTE" else "WAIT"
        }
    
    def rank_all_pairs(self) -> List[Dict]:
        """Rank all major pairs by opportunity"""
        pair_analysis = []
        
        for base, quote in self.major_pairs:
            analysis = self.analyze_currency_pair(base, quote)
            if "error" not in analysis:
                pair_analysis.append(analysis)
        
        # Sort by absolute strength differential (best opportunities first)
        pair_analysis.sort(key=lambda x: abs(x["strength_differential"]), reverse=True)
        
        return pair_analysis
    
    def get_divergence_opportunities(self) -> List[Dict]:
        """Find currencies with diverging fundamentals"""
        divergences = []
        
        # Compare all currency pairs
        currencies = list(self.currencies.keys())
        
        for i, curr1 in enumerate(currencies):
            for curr2 in currencies[i+1:]:
                data1 = self.currencies[curr1]
                data2 = self.currencies[curr2]
                
                # Check for policy divergence
                policy_diff = 0
                if data1.central_bank_policy == "hawkish" and data2.central_bank_policy == "dovish":
                    policy_diff = 2
                elif data1.central_bank_policy == "dovish" and data2.central_bank_policy == "hawkish":
                    policy_diff = -2
                
                # Check for growth divergence
                growth_diff = data1.gdp_growth - data2.gdp_growth
                
                # Check for rate divergence
                rate_diff = data1.interest_rate - data2.interest_rate
                
                # Score the divergence
                divergence_score = abs(policy_diff) + abs(growth_diff) + abs(rate_diff)
                
                if divergence_score > 2:
                    divergences.append({
                        "pair": f"{curr1.value}{curr2.value}",
                        "divergence_score": round(divergence_score, 2),
                        "policy_spread": policy_diff,
                        "growth_spread": round(growth_diff, 2),
                        "rate_spread": round(rate_diff * 100, 0),
                        "opportunity_type": "MONETARY_DIVERGENCE" if policy_diff != 0 else "GROWTH_DIVERGENCE",
                        "direction": f"{curr1.value}_STRENGTH" if policy_diff > 0 or growth_diff > 0 else f"{curr2.value}_STRENGTH"
                    })
        
        return sorted(divergences, key=lambda x: x["divergence_score"], reverse=True)
