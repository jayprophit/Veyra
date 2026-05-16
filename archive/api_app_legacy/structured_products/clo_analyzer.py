"""CLO Analyzer - Collateralized Loan Obligation tranche analysis"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class LoanAsset:
    issuer: str
    face_value: float
    coupon_rate: float
    default_probability: float
    recovery_rate: float
    seniority: str  # Senior, Subordinated

@dataclass
class Tranche:
    name: str  # AAA, AA, A, BBB, BB, Equity
    attachment: float  # % of capital structure
    detachment: float
    coupon: float
    notional: float

class CLOAnalyzer:
    """Analyze CLO tranches and collateral performance"""
    
    def __init__(self, total_collateral: float = 500e6):
        self.total_collateral = total_collateral
        self.loans: List[LoanAsset] = []
        self.tranches: List[Tranche] = []
        self.cash_account = 0.0
    
    def add_loan(self, loan: LoanAsset):
        """Add loan to collateral pool"""
        self.loans.append(loan)
    
    def add_tranche(self, tranche: Tranche):
        """Add tranche to capital structure"""
        self.tranches.append(tranche)
    
    def calculate_collateral_metrics(self) -> Dict:
        """Calculate collateral pool metrics"""
        if not self.loans:
            return {"error": "No loans in collateral pool"}
        
        total_par = sum(l.face_value for l in self.loans)
        total_coupon = sum(l.face_value * l.coupon_rate for l in self.loans)
        avg_coupon = total_coupon / total_par if total_par > 0 else 0
        
        # Weighted average default probability
        total_risk = sum(l.face_value * l.default_probability for l in self.loans)
        wasp = total_risk / total_par if total_par > 0 else 0
        
        # Weighted average recovery
        total_recovery = sum(l.face_value * l.recovery_rate for l in self.loans)
        warr = total_recovery / total_par if total_par > 0 else 0
        
        # Expected loss
        expected_loss = sum(
            l.face_value * l.default_probability * (1 - l.recovery_rate)
            for l in self.loans
        )
        expected_loss_pct = (expected_loss / total_par) * 100 if total_par > 0 else 0
        
        # Senior vs subordinated split
        senior_par = sum(l.face_value for l in self.loans if l.seniority == "Senior")
        sub_par = sum(l.face_value for l in self.loans if l.seniority == "Subordinated")
        
        return {
            "total_collateral": total_par,
            "num_loans": len(self.loans),
            "avg_loan_size": total_par / len(self.loans) if self.loans else 0,
            "weighted_avg_coupon": round(avg_coupon * 100, 3),
            "wasp": round(wasp * 100, 3),  # Weighted avg default prob
            "warr": round(warr * 100, 1),  # Weighted avg recovery
            "expected_loss_pct": round(expected_loss_pct, 3),
            "senior_pct": round((senior_par / total_par) * 100, 1) if total_par > 0 else 0,
            "subordinated_pct": round((sub_par / total_par) * 100, 1) if total_par > 0 else 0,
            "diversity_score": min(len(set(l.issuer for l in self.loans)), 35)  # Max 35
        }
    
    def calculate_tranche_coverage(self) -> Dict:
        """Calculate overcollateralization and interest coverage"""
        collateral_metrics = self.calculate_collateral_metrics()
        if "error" in collateral_metrics:
            return collateral_metrics
        
        total_par = collateral_metrics["total_collateral"]
        total_coupon = sum(l.face_value * l.coupon_rate for l in self.loans)
        
        # Total tranche notional
        total_tranche_par = sum(t.notional for t in self.tranches)
        
        # Overcollateralization ratio
        oc_ratio = (total_par / total_tranche_par) if total_tranche_par > 0 else 0
        
        # Calculate interest coverage for each tranche
        tranche_results = []
        running_notional = 0
        
        for tranche in self.tranches:
            running_notional += tranche.notional
            
            # Par coverage for this tranche
            par_coverage = (total_par - running_notional + tranche.notional) / tranche.notional if tranche.notional > 0 else 0
            
            # Interest coverage (simplified)
            tranche_coupon_payment = tranche.notional * tranche.coupon
            ic_ratio = total_coupon / tranche_coupon_payment if tranche_coupon_payment > 0 else 0
            
            tranche_results.append({
                "tranche": tranche.name,
                "attachment_pct": round(tranche.attachment * 100, 1),
                "detachment_pct": round(tranche.detachment * 100, 1),
                "notional": tranche.notional,
                "coupon": round(tranche.coupon * 100, 3),
                "oc_ratio": round(par_coverage, 3),
                "ic_ratio": round(ic_ratio, 2),
                "status": "PASS" if par_coverage > 1.05 and ic_ratio > 1.2 else "WARNING"
            })
        
        return {
            "total_collateral": total_par,
            "total_tranches": total_tranche_par,
            "overall_oc_ratio": round(oc_ratio, 3),
            "tranches": tranche_results,
            "structure_health": "HEALTHY" if oc_ratio > 1.1 else "STRESSED" if oc_ratio > 1.05 else "DISTRESSED"
        }
    
    def stress_test_defaults(self, default_rate: float) -> Dict:
        """Stress test with elevated default rate"""
        total_par = sum(l.face_value for l in self.loans)
        
        # Apply defaults
        defaulted_amount = total_par * default_rate
        recovery = sum(
            l.face_value * default_rate * l.recovery_rate
            for l in self.loans
        ) / len(self.loans) if self.loans else 0
        
        loss_amount = defaulted_amount - recovery
        remaining_collateral = total_par - loss_amount
        
        # Calculate tranche impacts
        tranche_impacts = []
        cumulative_loss = 0
        
        for tranche in self.tranches:
            tranche_start = tranche.attachment * self.total_collateral
            tranche_end = tranche.detachment * self.total_collateral
            
            # Check if loss penetrates this tranche
            if loss_amount > tranche_start:
                loss_in_tranche = min(loss_amount - tranche_start, tranche_end - tranche_start)
                loss_pct = (loss_in_tranche / tranche.notional) * 100 if tranche.notional > 0 else 0
                
                status = "IMPAIRED" if loss_pct > 0 else "WHOLE"
                principal_write_down = loss_in_tranche
            else:
                loss_pct = 0
                status = "WHOLE"
                principal_write_down = 0
            
            tranche_impacts.append({
                "tranche": tranche.name,
                "original_notional": tranche.notional,
                "principal_write_down": round(principal_write_down, 0),
                "loss_pct": round(loss_pct, 2),
                "status": status,
                "remaining_principal": round(tranche.notional - principal_write_down, 0)
            })
        
        return {
            "stress_default_rate": round(default_rate * 100, 1),
            "total_par": total_par,
            "loss_amount": round(loss_amount, 0),
            "loss_pct": round((loss_amount / total_par) * 100, 2),
            "remaining_collateral": round(remaining_collateral, 0),
            "tranche_impacts": tranche_impacts,
            "first_loss_tranche": next((t["tranche"] for t in tranche_impacts if t["loss_pct"] > 0), "None")
        }
    
    def calculate_yields(self, reinvestment_rate: float = 0.08) -> Dict:
        """Calculate expected yields by tranche"""
        # Simplified IRR calculation
        collateral_metrics = self.calculate_collateral_metrics()
        avg_coupon = collateral_metrics.get("weighted_avg_coupon", 8.0) / 100
        
        # Reinvestment income
        reinvestment_income = self.total_collateral * reinvestment_rate * 0.10  # 10% reinvested
        
        total_income = (self.total_collateral * avg_coupon) + reinvestment_income
        
        # Waterfall distribution (simplified)
        tranche_yields = []
        remaining_income = total_income
        
        for tranche in self.tranches:
            # Senior tranches get their coupon first
            tranche_coupon_income = tranche.notional * tranche.coupon
            
            if remaining_income >= tranche_coupon_income:
                received = tranche_coupon_income
                remaining_income -= tranche_coupon_income
            else:
                received = remaining_income
                remaining_income = 0
            
            # IRR approximation
            yield_pct = (received / tranche.notional) * 100 if tranche.notional > 0 else 0
            
            tranche_yields.append({
                "tranche": tranche.name,
                "coupon": round(tranche.coupon * 100, 3),
                "expected_yield": round(yield_pct, 3),
                "spread": round((yield_pct - tranche.coupon * 100), 3),
                "risk_adjusted_yield": round(yield_pct * (1 - self._tranche_risk_factor(tranche.name)), 3)
            })
        
        return {
            "collateral_yield": round(avg_coupon * 100, 3),
            "reinvestment_rate": round(reinvestment_rate * 100, 2),
            "tranche_yields": tranche_yields,
            "excess_spread": round((remaining_income / self.total_collateral) * 100, 3) if self.total_collateral > 0 else 0
        }
    
    def _tranche_risk_factor(self, tranche_name: str) -> float:
        """Risk factor for yield adjustment"""
        factors = {
            "AAA": 0.01,
            "AA": 0.02,
            "A": 0.03,
            "BBB": 0.05,
            "BB": 0.10,
            "B": 0.15,
            "Equity": 0.25
        }
        return factors.get(tranche_name, 0.10)
    
    def get_clo_summary(self) -> Dict:
        """Get comprehensive CLO summary"""
        collateral = self.calculate_collateral_metrics()
        coverage = self.calculate_tranche_coverage()
        yields = self.calculate_yields()
        
        # Stress scenarios
        stress_5 = self.stress_test_defaults(0.05)
        stress_10 = self.stress_test_defaults(0.10)
        
        return {
            "collateral": collateral,
            "capital_structure": coverage,
            "yields": yields,
            "stress_scenarios": {
                "5pct_defaults": stress_5,
                "10pct_defaults": stress_10
            },
            "rating": self._assign_clo_rating(stress_5, stress_10)
        }
    
    def _assign_clo_rating(self, stress_5: Dict, stress_10: Dict) -> str:
        """Assign overall CLO health rating"""
        loss_5 = stress_5.get("loss_pct", 0)
        loss_10 = stress_10.get("loss_pct", 0)
        first_loss_5 = stress_5.get("first_loss_tranche", "Equity")
        first_loss_10 = stress_10.get("first_loss_tranche", "Equity")
        
        if loss_10 < 5 and first_loss_10 == "Equity":
            return "INVESTMENT_GRADE"
        elif loss_5 < 3 and first_loss_5 in ["Equity", "B"]:
            return "SPECULATIVE_GRADE"
        else:
            return "DISTRESSED"
