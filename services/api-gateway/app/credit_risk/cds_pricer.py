"""CDS Pricer - Price Credit Default Swaps and analyze credit risk"""
from typing import Dict, List
from dataclasses import dataclass
import math

@dataclass
class CDSContract:
    reference_entity: str
    notional: float
    spread_bps: float  # CDS spread in basis points
    maturity_years: float
    recovery_rate: float  # Expected recovery rate (0-1)
    coupon_frequency: int = 4  # Quarterly payments

class CDSPricer:
    """Price Credit Default Swaps and analyze credit risk"""
    
    def __init__(self, risk_free_rate: float = 0.05):
        self.risk_free_rate = risk_free_rate
        self.cds_contracts: List[CDSContract] = []
    
    def add_contract(self, contract: CDSContract):
        """Add CDS contract"""
        self.cds_contracts.append(contract)
    
    def calculate_default_probability(self, spread_bps: float, 
                                       maturity: float,
                                       recovery_rate: float = 0.4) -> Dict:
        """Calculate implied default probability from CDS spread"""
        # Simplified hazard rate model
        # Spread ≈ (1 - RR) × Hazard Rate
        # Hazard Rate = -ln(1 - PD) / T
        
        spread_decimal = spread_bps / 10000
        hazard_rate = spread_decimal / (1 - recovery_rate)
        
        # Calculate cumulative default probability
        # PD = 1 - exp(-hazard_rate × T)
        pd = 1 - math.exp(-hazard_rate * maturity)
        
        # Annual default probability
        annual_pd = 1 - math.exp(-hazard_rate)
        
        return {
            "cds_spread_bps": spread_bps,
            "maturity_years": maturity,
            "recovery_rate": recovery_rate,
            "hazard_rate": round(hazard_rate * 100, 3),
            "cumulative_default_probability": round(pd * 100, 2),
            "annual_default_probability": round(annual_pd * 100, 3),
            "survival_probability": round((1 - pd) * 100, 2),
            "risk_rating": self._get_risk_rating(pd)
        }
    
    def _get_risk_rating(self, pd: float) -> str:
        """Map default probability to risk rating"""
        if pd < 0.01:
            return "AAA/AA"
        elif pd < 0.03:
            return "A"
        elif pd < 0.07:
            return "BBB"
        elif pd < 0.15:
            return "BB"
        elif pd < 0.25:
            return "B"
        elif pd < 0.50:
            return "CCC/CC"
        else:
            return "D (Distressed)"
    
    def price_cds_premium(self, contract: CDSContract) -> Dict:
        """Calculate CDS premium leg and upfront"""
        notional = contract.notional
        spread_bps = contract.spread_bps
        maturity = contract.maturity_years
        recovery = contract.recovery_rate
        
        # Annual premium payment
        annual_premium = notional * (spread_bps / 10000)
        
        # Total expected premium payments (simplified, ignoring discounting)
        total_premium = annual_premium * maturity
        
        # Expected loss (protection leg)
        default_prob = self.calculate_default_probability(
            spread_bps, maturity, recovery
        )
        pd = default_prob["cumulative_default_probability"] / 100
        expected_loss = notional * pd * (1 - recovery)
        
        # CDS price (upfront payment)
        # Positive = protection buyer pays upfront
        # Negative = protection seller pays upfront
        cds_price = expected_loss - total_premium
        
        # Duration approximation
        duration = maturity * (1 - pd * 0.5)  # Rough approximation
        
        return {
            "reference_entity": contract.reference_entity,
            "notional": notional,
            "annual_premium": round(annual_premium, 2),
            "total_premium": round(total_premium, 2),
            "expected_loss": round(expected_loss, 2),
            "cds_price": round(cds_price, 2),
            "upfront_payment": "BUYER_PAYS" if cds_price > 0 else "SELLER_PAYS",
            "duration_years": round(duration, 2),
            "default_probability": default_prob
        }
    
    def calculate_cds_pnl(self, contract: CDSContract, 
                          current_spread_bps: float) -> Dict:
        """Calculate mark-to-market P&L for CDS position"""
        entry_spread = contract.spread_bps
        notional = contract.notional
        maturity = contract.maturity_years
        remaining_maturity = maturity  # Simplified
        
        # Spread widening = gain for protection buyer
        spread_change = current_spread_bps - entry_spread
        
        # Simplified P&L: DV01 × spread change
        # DV01 ≈ Notional × Duration × 0.0001
        dv01 = notional * remaining_maturity * 0.0001
        pnl = dv01 * spread_change
        
        # Percentage return
        initial_investment = notional * (entry_spread / 10000) * remaining_maturity
        pct_return = (pnl / initial_investment * 100) if initial_investment > 0 else 0
        
        return {
            "entry_spread_bps": entry_spread,
            "current_spread_bps": current_spread_bps,
            "spread_change_bps": round(spread_change, 2),
            "dv01": round(dv01, 2),
            "pnl": round(pnl, 2),
            "return_pct": round(pct_return, 2),
            "position": "PROTECTION_BUYER" if pnl > 0 else "PROTECTION_SELLER",
            "unrealized_pnl": round(pnl, 2)
        }
    
    def analyze_credit_curve(self, spreads_by_tenor: Dict[str, float],
                             recovery_rate: float = 0.4) -> Dict:
        """Analyze CDS term structure"""
        tenors = [(k, float(k.replace('Y', ''))) for k in spreads_by_tenor.keys()]
        tenors.sort(key=lambda x: x[1])
        
        default_probs = []
        for tenor_str, maturity in tenors:
            spread = spreads_by_tenor[tenor_str]
            pd_data = self.calculate_default_probability(spread, maturity, recovery_rate)
            default_probs.append({
                "tenor": tenor_str,
                "spread_bps": spread,
                **pd_data
            })
        
        # Curve shape analysis
        if len(default_probs) >= 2:
            short_spread = default_probs[0]["cds_spread_bps"]
            long_spread = default_probs[-1]["cds_spread_bps"]
            curve_slope = long_spread - short_spread
            
            if curve_slope > 50:
                curve_shape = "UPWARD_SLOPING (Normal)"
            elif curve_slope < -20:
                curve_shape = "INVERTED (Distress Warning)"
            else:
                curve_shape = "FLAT"
        else:
            curve_shape = "INSUFFICIENT_DATA"
            curve_slope = 0
        
        return {
            "curve_shape": curve_shape,
            "slope_bps": round(curve_slope, 1),
            "default_probabilities": default_probs,
            "implied_rating": default_probs[0].get("risk_rating", "N/A") if default_probs else "N/A",
            "stress_scenario": self._calculate_stress_scenario(default_probs)
        }
    
    def _calculate_stress_scenario(self, default_probs: List[Dict]) -> Dict:
        """Calculate stress scenario impact"""
        if not default_probs:
            return {}
        
        # Assume spreads widen by 200 bps in stress
        stress_spread_increase = 200
        
        stressed_pds = []
        for dp in default_probs:
            stressed_spread = dp["cds_spread_bps"] + stress_spread_increase
            maturity = dp["maturity_years"]
            recovery = dp["recovery_rate"]
            
            stressed = self.calculate_default_probability(
                stressed_spread, maturity, recovery
            )
            stressed_pds.append(stressed)
        
        return {
            "stress_spread_shock_bps": stress_spread_increase,
            "stressed_default_probs": stressed_pds,
            "credit_migration_risk": "HIGH" if stressed_pds[0]["cumulative_default_probability"] > 30 else "MODERATE"
        }
    
    def calculate_basket_cds(self, entities: List[str], 
                            spreads: List[float],
                            notional: float,
                            correlation: float = 0.3) -> Dict:
        """Price basket CDS (CDX/IG type)"""
        num_entities = len(entities)
        
        # Equal weighted basket
        avg_spread = sum(spreads) / num_entities if num_entities > 0 else 0
        
        # Correlation adjustment to spread
        # Higher correlation = higher basket spread
        correlation_adjustment = 1 + (correlation * 0.5)
        basket_spread = avg_spread * correlation_adjustment
        
        # Expected number of defaults
        avg_pd = sum(self.calculate_default_probability(s, 5)["annual_default_probability"] 
                     for s in spreads) / num_entities / 100
        
        # With correlation, probability of multiple defaults increases
        expected_defaults = num_entities * avg_pd * (1 + correlation)
        
        return {
            "num_entities": num_entities,
            "basket_spread_bps": round(basket_spread, 2),
            "avg_entity_spread": round(avg_spread, 2),
            "correlation_assumption": correlation,
            "expected_defaults": round(expected_defaults, 2),
            "diversification_score": round((1 - correlation) * 100, 1),
            "index_equivalent": self._get_index_equivalent(basket_spread)
        }
    
    def _get_index_equivalent(self, spread_bps: float) -> str:
        """Map spread to index equivalent"""
        if spread_bps < 60:
            return "CDX.IG (Investment Grade)"
        elif spread_bps < 150:
            return "CDX.IG High Vol"
        elif spread_bps < 300:
            return "CDX.HY (High Yield)"
        else:
            return "Distressed Index"
