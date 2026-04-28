"""Life Actuary - Life insurance actuarial calculations and reserving"""
from typing import Dict, List
from dataclasses import dataclass
from math import exp

@dataclass
class LifePolicy:
    policy_id: str
    face_amount: float
    issue_age: int
    current_age: int
    premium: float
    policy_type: str  # Term, Whole, Universal, Variable
    term_years: int = 0  # For term policies
    cash_value: float = 0.0
    mortality_table: str = "2017CSO"

class LifeActuary:
    """Actuarial calculations for life insurance"""
    
    # Simplified mortality rates (2017 CSO table - age-specific)
    CSO_RATES = {
        20: 0.0005, 25: 0.0006, 30: 0.0008, 35: 0.0010,
        40: 0.0015, 45: 0.0025, 50: 0.0040, 55: 0.0070,
        60: 0.0120, 65: 0.0200, 70: 0.0350, 75: 0.0600,
        80: 0.1000, 85: 0.1600, 90: 0.2500
    }
    
    def __init__(self, interest_rate: float = 0.04):
        self.interest_rate = interest_rate
        self.policies: List[LifePolicy] = []
    
    def add_policy(self, policy: LifePolicy):
        """Add policy to portfolio"""
        self.policies.append(policy)
    
    def get_mortality_rate(self, age: int) -> float:
        """Get mortality rate for age (interpolated)"""
        ages = sorted(self.CSO_RATES.keys())
        
        if age <= ages[0]:
            return self.CSO_RATES[ages[0]]
        if age >= ages[-1]:
            return self.CSO_RATES[ages[-1]]
        
        # Find nearest ages
        for i in range(len(ages) - 1):
            if ages[i] <= age <= ages[i + 1]:
                # Linear interpolation
                rate_low = self.CSO_RATES[ages[i]]
                rate_high = self.CSO_RATES[ages[i + 1]]
                weight = (age - ages[i]) / (ages[i + 1] - ages[i])
                return rate_low + (rate_high - rate_low) * weight
        
        return 0.01
    
    def calculate_npx(self, age: int, n: int) -> float:
        """Calculate n-year survival probability"""
        survival_prob = 1.0
        for year in range(n):
            current_age = age + year
            mortality = self.get_mortality_rate(current_age)
            survival_prob *= (1 - mortality)
        return survival_prob
    
    def calculate_term_premium(self, face_amount: float, issue_age: int,
                               term_years: int, premium_mode: str = "annual") -> Dict:
        """Calculate term life insurance premium"""
        # Net single premium for term insurance
        net_single_premium = 0.0
        
        for year in range(term_years):
            current_age = issue_age + year
            mortality = self.get_mortality_rate(current_age)
            survival_to_year = self.calculate_npx(issue_age, year)
            
            # Discount factor
            v = 1 / (1 + self.interest_rate)
            discount = v ** (year + 0.5)  # Mid-year
            
            net_single_premium += face_amount * mortality * survival_to_year * discount
        
        # Annuity due for premium payment period
        annuity_factor = 0.0
        for year in range(min(term_years, 20)):  # Premiums for 20 years max
            survival = self.calculate_npx(issue_age, year)
            v = 1 / (1 + self.interest_rate)
            annuity_factor += survival * (v ** year)
        
        # Net annual premium
        net_annual_premium = net_single_premium / annuity_factor if annuity_factor > 0 else 0
        
        # Gross premium with loadings (25% expense loading)
        gross_premium = net_annual_premium * 1.25
        
        # Mode adjustment
        mode_factors = {"annual": 1.0, "semi": 0.51, "quarterly": 0.26, "monthly": 0.09}
        mode_factor = mode_factors.get(premium_mode, 1.0)
        
        adjusted_premium = gross_premium * mode_factor
        
        return {
            "face_amount": face_amount,
            "issue_age": issue_age,
            "term_years": term_years,
            "net_single_premium": round(net_single_premium, 2),
            "net_annual_premium": round(net_annual_premium, 2),
            "gross_annual_premium": round(gross_premium, 2),
            "premium_mode": premium_mode,
            "adjusted_premium": round(adjusted_premium, 2),
            "expense_loading_pct": 25.0
        }
    
    def calculate_policy_reserve(self, policy: LifePolicy, duration: int) -> Dict:
        """Calculate policy reserve at given duration"""
        if policy.policy_type == "Term":
            # Net premium reserve
            remaining_term = max(0, policy.term_years - duration)
            
            if remaining_term == 0:
                return {"reserve": 0.0, "method": "Term Expired"}
            
            # Calculate present value of future benefits
            pv_benefits = 0.0
            current_age = policy.issue_age + duration
            
            for year in range(remaining_term):
                mortality = self.get_mortality_rate(current_age + year)
                survival = self.calculate_npx(current_age, year)
                v = 1 / (1 + self.interest_rate)
                discount = v ** (year + 0.5)
                
                pv_benefits += policy.face_amount * mortality * survival * discount
            
            # Calculate present value of future premiums
            pv_premiums = 0.0
            original_net_premium = policy.premium * 0.8  # Estimate net portion
            
            for year in range(min(remaining_term, 20 - duration)):
                survival = self.calculate_npx(current_age, year)
                v = 1 / (1 + self.interest_rate)
                pv_premiums += original_net_premium * survival * (v ** year)
            
            reserve = pv_benefits - pv_premiums
            
        elif policy.policy_type in ["Whole", "Universal"]:
            # Cash value based reserve
            reserve = max(policy.cash_value, policy.face_amount * 0.02)  # Minimum reserve
        else:
            reserve = 0.0
        
        return {
            "policy_id": policy.policy_id,
            "duration": duration,
            "reserve": round(reserve, 2),
            "reserve_pct_of_face": round((reserve / policy.face_amount) * 100, 3),
            "method": "Net Premium" if policy.policy_type == "Term" else "Cash Value",
            "current_age": policy.issue_age + duration
        }
    
    def calculate_surrender_value(self, policy: LifePolicy, duration: int) -> Dict:
        """Calculate surrender value"""
        reserve = self.calculate_policy_reserve(policy, duration)
        gross_reserve = reserve["reserve"]
        
        # Surrender charges (declining scale)
        if duration <= 3:
            surrender_charge_rate = 0.10
        elif duration <= 5:
            surrender_charge_rate = 0.05
        elif duration <= 10:
            surrender_charge_rate = 0.02
        else:
            surrender_charge_rate = 0.0
        
        surrender_charge = gross_reserve * surrender_charge_rate
        surrender_value = max(0, gross_reserve - surrender_charge)
        
        # For whole/universal, consider cash value
        if policy.policy_type in ["Whole", "Universal"]:
            surrender_value = max(surrender_value, policy.cash_value * 0.95)
        
        return {
            "gross_reserve": round(gross_reserve, 2),
            "surrender_charge": round(surrender_charge, 2),
            "surrender_charge_pct": round(surrender_charge_rate * 100, 1),
            "surrender_value": round(surrender_value, 2),
            "cash_surrender_value_pct": round((surrender_value / policy.face_amount) * 100, 3)
        }
    
    def portfolio_analysis(self) -> Dict:
        """Analyze entire policy portfolio"""
        if not self.policies:
            return {"error": "No policies in portfolio"}
        
        total_face = sum(p.face_amount for p in self.policies)
        total_premium = sum(p.premium for p in self.policies)
        total_reserve = 0.0
        
        # Calculate average age
        avg_age = sum(p.current_age for p in self.policies) / len(self.policies)
        
        # Risk concentration
        age_distribution = {}
        for p in self.policies:
            age_bucket = (p.current_age // 10) * 10
            age_distribution[age_bucket] = age_distribution.get(age_bucket, 0) + p.face_amount
        
        # Expected mortality cost
        expected_mortality_cost = sum(
            p.face_amount * self.get_mortality_rate(p.current_age)
            for p in self.policies
        )
        
        # Reserve calculation for each policy
        for policy in self.policies:
            duration = policy.current_age - policy.issue_age
            reserve = self.calculate_policy_reserve(policy, duration)
            total_reserve += reserve["reserve"]
        
        # Loss ratio estimate
        expected_claims = expected_mortality_cost
        earned_premium = total_premium * 0.9  # Assume 10% unearned
        loss_ratio = (expected_claims / earned_premium) * 100 if earned_premium > 0 else 0
        
        return {
            "total_policies": len(self.policies),
            "total_face_amount": round(total_face, 0),
            "total_annual_premium": round(total_premium, 0),
            "total_reserves": round(total_reserve, 0),
            "average_age": round(avg_age, 1),
            "expected_mortality_cost": round(expected_mortality_cost, 0),
            "estimated_loss_ratio": round(loss_ratio, 2),
            "risk_based_capital_ratio": round((total_reserve / total_face) * 100, 2),
            "age_distribution": {f"{k}s": round(v/1e6, 1) for k, v in age_distribution.items()},
            "portfolio_health": "HEALTHY" if loss_ratio < 60 else "MODERATE" if loss_ratio < 80 else "STRESSED"
        }
    
    def reinsurance_optimization(self, retention_limit: float = 1e6) -> Dict:
        """Optimize reinsurance structure"""
        if not self.policies:
            return {"error": "No policies"}
        
        # Categorize policies by size
        retained_policies = []
        ceded_policies = []
        
        for p in self.policies:
            if p.face_amount <= retention_limit:
                retained_policies.append(p)
            else:
                ceded_policies.append(p)
        
        # Calculate reinsurance premium (cost)
        ceded_face = sum(p.face_amount for p in ceded_policies)
        reinsurance_rate = 0.015  # 1.5% of face
        reinsurance_premium = ceded_face * reinsurance_rate
        
        # Risk reduction benefit
        total_mortality_cost = sum(
            p.face_amount * self.get_mortality_rate(p.current_age)
            for p in self.policies
        )
        
        ceded_mortality_cost = sum(
            p.face_amount * self.get_mortality_rate(p.current_age)
            for p in ceded_policies
        )
        
        risk_reduction = (ceded_mortality_cost / total_mortality_cost * 100) if total_mortality_cost > 0 else 0
        
        return {
            "retention_limit": retention_limit,
            "retained_policies": len(retained_policies),
            "ceded_policies": len(ceded_policies),
            "retained_face": round(sum(p.face_amount for p in retained_policies), 0),
            "ceded_face": round(ceded_face, 0),
            "reinsurance_premium": round(reinsurance_premium, 0),
            "mortality_risk_reduction_pct": round(risk_reduction, 2),
            "net_cost_benefit": "POSITIVE" if risk_reduction > 15 else "NEUTRAL" if risk_reduction > 5 else "NEGATIVE"
        }
