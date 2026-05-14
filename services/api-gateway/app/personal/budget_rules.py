"""
Budget Rules & Strategies
Multiple budgeting frameworks with analysis and recommendations
50/30/20, 90/10, 60/20/20, 70/20/10, Zero-Based, Envelope, Pay Yourself First
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class BudgetRuleType(Enum):
    FIFTY_THIRTY_TWENTY = "50_30_20"  # 50 needs, 30 wants, 20 savings
    NINETY_TEN = "90_10"  # 90 living, 10 investing
    SIXTY_TWENTY_TWENTY = "60_20_20"  # 60 living, 20 savings, 20 fun
    SEVENTY_TWENTY_TEN = "70_20_10"  # 70 living, 20 savings, 10 debt/giving
    EIGHTY_TWENTY = "80_20"  # 80 living, 20 savings
    PAY_YOURSELF_FIRST = "pay_yourself_first"  # Save then spend
    ZERO_BASED = "zero_based"  # Every pound has a job
    ENVELOPE = "envelope"  # Cash allocation
    FIFTEEN_PERCENT_RETIREMENT = "15_percent_retirement"
    ONE_PERCENT_RULE = "1_percent_rule"  # Invest 1% more each year


@dataclass
class BudgetRule:
    rule_type: BudgetRuleType
    name: str
    description: str
    allocations: Dict[str, float]  # Category -> percentage
    ideal_for: List[str]  # Income levels, lifestyles
    difficulty: str  # easy, medium, hard
    savings_rate: float
    flexibility: str  # rigid, moderate, flexible
    pros: List[str]
    cons: List[str]


@dataclass
class BudgetAnalysis:
    rule_type: BudgetRuleType
    income: Decimal
    actual_spending: Dict[str, Decimal]
    target_allocation: Dict[str, Decimal]
    variance: Dict[str, Decimal]  # Actual - Target
    variance_percent: Dict[str, float]
    compliance_score: int  # 0-100
    on_track_categories: List[str]
    off_track_categories: List[Dict[str, Any]]
    recommendations: List[str]
    projected_savings_annual: Decimal
    years_to_financial_independence: Optional[int]


class BudgetRulesEngine:
    """Analyze spending against multiple budget frameworks"""
    
    # Define all budget rules
    RULES = {
        BudgetRuleType.FIFTY_THIRTY_TWENTY: BudgetRule(
            rule_type=BudgetRuleType.FIFTY_THIRTY_TWENTY,
            name="50/30/20 Rule",
            description="Classic budgeting framework from Elizabeth Warren",
            allocations={"needs": 50.0, "wants": 30.0, "savings": 20.0},
            ideal_for=["beginners", "middle_income", "balanced_approach"],
            difficulty="easy",
            savings_rate=20.0,
            flexibility="moderate",
            pros=["Simple to understand", "Balanced lifestyle", "Sustainable long-term"],
            cons=["May not save enough for early FI", "High cost-of-living areas struggle"]
        ),
        
        BudgetRuleType.NINETY_TEN: BudgetRule(
            rule_type=BudgetRuleType.NINETY_TEN,
            name="90/10 Rule",
            description="Keep living expenses at 90%, invest 10% minimum",
            allocations={"living": 90.0, "investing": 10.0},
            ideal_for=["low_income", "debt_payoff", "simplicity"],
            difficulty="easy",
            savings_rate=10.0,
            flexibility="flexible",
            pros=["Very simple", "Minimum viable investing", "Easy to start"],
            cons=["Low savings rate", "Slow wealth building", "Not for FI goals"]
        ),
        
        BudgetRuleType.SIXTY_TWENTY_TWENTY: BudgetRule(
            rule_type=BudgetRuleType.SIXTY_TWENTY_TWENTY,
            name="60/20/20 Rule",
            description="Equal weight to savings and fun, controlled living expenses",
            allocations={"living": 60.0, "savings": 20.0, "fun": 20.0},
            ideal_for=["young_professionals", "single", "urban"],
            difficulty="medium",
            savings_rate=20.0,
            flexibility="moderate",
            pros=["Balances fun and future", "Good for single earners", "Prevents burnout"],
            cons=["60% living may be tight for families", "Fun spending can creep"]
        ),
        
        BudgetRuleType.SEVENTY_TWENTY_TEN: BudgetRule(
            rule_type=BudgetRuleType.SEVENTY_TWENTY_TEN,
            name="70/20/10 Rule",
            description="Focus on living comfortably while saving and giving/paying debt",
            allocations={"living": 70.0, "savings": 20.0, "debt_giving": 10.0},
            ideal_for=["families", "debt_payoff", "charitable_givers"],
            difficulty="medium",
            savings_rate=20.0,
            flexibility="moderate",
            pros=["Family-friendly", "Debt payoff focused", "Allows giving"],
            cons=["Lower savings than aggressive methods", "10% debt may not be enough"]
        ),
        
        BudgetRuleType.EIGHTY_TWENTY: BudgetRule(
            rule_type=BudgetRuleType.EIGHTY_TWENTY,
            name="80/20 Rule",
            description="Pareto principle for budgeting - keep it simple",
            allocations={"everything": 80.0, "savings": 20.0},
            ideal_for=["high_income", "busy_professionals", "minimalists"],
            difficulty="easy",
            savings_rate=20.0,
            flexibility="flexible",
            pros=["Extremely simple", "No category tracking needed", "High flexibility"],
            cons=["Lacks spending visibility", "May miss optimization opportunities"]
        ),
        
        BudgetRuleType.PAY_YOURSELF_FIRST: BudgetRule(
            rule_type=BudgetRuleType.PAY_YOURSELF_FIRST,
            name="Pay Yourself First",
            description="Save/invest before any spending",
            allocations={"savings_first": 20.0, "everything_else": 80.0},
            ideal_for=["low_discipline", "automated_savers", "all_income_levels"],
            difficulty="easy",
            savings_rate=20.0,
            flexibility="flexible",
            pros=["Guarantees savings", "Removes temptation", "Psychologically effective"],
            cons=["May lead to overdraft if not careful", "Rest is unmonitored"]
        ),
        
        BudgetRuleType.ZERO_BASED: BudgetRule(
            rule_type=BudgetRuleType.ZERO_BASED,
            name="Zero-Based Budgeting",
            description="Every pound has a specific job - income minus outgoings equals zero",
            allocations={"detailed": 100.0},
            ideal_for=["detail_oriented", "irregular_income", "debt_payoff"],
            difficulty="hard",
            savings_rate=25.0,  # Variable
            flexibility="rigid",
            pros=["Maximum control", "Every penny tracked", "Great for irregular income"],
            cons=["Time intensive", "Requires discipline", "Can be stressful"]
        ),
        
        BudgetRuleType.ENVELOPE: BudgetRule(
            rule_type=BudgetRuleType.ENVELOPE,
            name="Envelope System",
            description="Cash-based physical allocation to spending categories",
            allocations={"cash_categories": 100.0},
            ideal_for=["overspenders", "cash_preferrers", "visual_learners"],
            difficulty="medium",
            savings_rate=15.0,  # Variable
            flexibility="rigid",
            pros=["Physical limits spending", "Tangible", "No overspending possible"],
            cons=["Cash inconvenience", "No rewards/cashback", "Security risk"]
        ),
        
        BudgetRuleType.FIFTEEN_PERCENT_RETIREMENT: BudgetRule(
            rule_type=BudgetRuleType.FIFTEEN_PERCENT_RETIREMENT,
            name="15% Retirement Rule",
            description="Minimum 15% to retirement accounts, rest is flexible",
            allocations={"retirement": 15.0, "everything_else": 85.0},
            ideal_for=["retirement_focused", "middle_age", "stable_income"],
            difficulty="easy",
            savings_rate=15.0,
            flexibility="flexible",
            pros=["Retirement secure", "Fidelity recommended", "Rest is flexible"],
            cons=["Only 15% may not be enough for early retirement", "Ignores other goals"]
        ),
        
        BudgetRuleType.ONE_PERCENT_RULE: BudgetRule(
            rule_type=BudgetRuleType.ONE_PERCENT_RULE,
            name="1% Rule",
            description="Increase savings rate by 1% each year",
            allocations={"savings_annual_increase": 1.0},
            ideal_for=["gradual_improvers", "lifestyle_creep_prevention", "all_levels"],
            difficulty="easy",
            savings_rate=15.0,  # Starting point, grows
            flexibility="flexible",
            pros=["Painless progression", "Compound effect", "Sustainable"],
            cons=["Slow initially", "Requires annual review", "May need bigger jumps"]
        )
    }
    
    @classmethod
    def get_all_rules(cls) -> Dict[BudgetRuleType, BudgetRule]:
        """Get all available budget rules"""
        return cls.RULES
    
    @classmethod
    def get_rule(cls, rule_type: BudgetRuleType) -> Optional[BudgetRule]:
        """Get specific budget rule"""
        return cls.RULES.get(rule_type)
    
    @classmethod
    def recommend_rule(
        cls,
        income: Decimal,
        age: int,
        has_debt: bool,
        family_size: int,
        lifestyle: str,
        discipline_level: str
    ) -> List[Dict[str, Any]]:
        """Recommend best budget rules for situation"""
        recommendations = []
        
        for rule in cls.RULES.values():
            score = 0
            reasons = []
            
            # Income level matching
            if income < Decimal("2000") and rule.savings_rate <= 15:
                score += 2
                reasons.append("Appropriate for lower income")
            elif income > Decimal("4000") and rule.savings_rate >= 20:
                score += 2
                reasons.append("Can afford higher savings rate")
            
            # Age matching
            if age < 30 and rule.rule_type in [
                BudgetRuleType.SIXTY_TWENTY_TWENTY,
                BudgetRuleType.ONE_PERCENT_RULE
            ]:
                score += 2
                reasons.append("Good for building habits while young")
            elif age > 50 and rule.rule_type == BudgetRuleType.FIFTEEN_PERCENT_RETIREMENT:
                score += 3
                reasons.append("Critical for retirement catch-up")
            
            # Debt situation
            if has_debt and rule.rule_type in [
                BudgetRuleType.SEVENTY_TWENTY_TEN,
                BudgetRuleType.ZERO_BASED
            ]:
                score += 3
                reasons.append("Includes debt payoff allocation")
            
            # Family size
            if family_size > 2 and rule.rule_type in [
                BudgetRuleType.FIFTY_THIRTY_TWENTY,
                BudgetRuleType.SEVENTY_TWENTY_TEN
            ]:
                score += 2
                reasons.append("Family-friendly structure")
            elif family_size == 1 and rule.rule_type == BudgetRuleType.SIXTY_TWENTY_TWENTY:
                score += 2
                reasons.append("Optimized for single earners")
            
            # Discipline level
            if discipline_level == "low" and rule.difficulty == "easy":
                score += 2
                reasons.append("Easy to maintain")
            elif discipline_level == "high" and rule.difficulty == "hard":
                score += 1
                reasons.append("Matches your discipline level")
            
            # Lifestyle
            if lifestyle == "frugal" and rule.savings_rate >= 20:
                score += 2
                reasons.append("Matches frugal lifestyle")
            elif lifestyle == "balanced" and rule.flexibility == "moderate":
                score += 2
                reasons.append("Balanced flexibility")
            elif lifestyle == "luxury" and rule.savings_rate <= 15:
                score -= 1  # Penalty
            
            recommendations.append({
                "rule": rule.name,
                "type": rule.rule_type.value,
                "score": score,
                "savings_rate": rule.savings_rate,
                "difficulty": rule.difficulty,
                "why": reasons,
                "pros": rule.pros,
                "cons": rule.cons
            })
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:5]  # Top 5
    
    @classmethod
    def analyze_against_rule(
        cls,
        rule_type: BudgetRuleType,
        income: Decimal,
        spending: Dict[str, Decimal]
    ) -> BudgetAnalysis:
        """Analyze actual spending against a budget rule"""
        rule = cls.RULES[rule_type]
        
        # Map spending to rule categories
        category_mapping = cls._map_to_rule_categories(spending, rule_type)
        
        # Calculate targets
        targets = {}
        variances = {}
        variance_pcts = {}
        
        for category, pct in rule.allocations.items():
            target = income * Decimal(str(pct / 100))
            targets[category] = target
            
            actual = category_mapping.get(category, Decimal("0"))
            variance = actual - target
            variances[category] = variance
            
            variance_pct = float(variance / target * 100) if target > 0 else 0
            variance_pcts[category] = variance_pct
        
        # Calculate compliance
        on_track = []
        off_track = []
        
        for category, variance_pct in variance_pcts.items():
            if abs(variance_pct) <= 10:  # Within 10%
                on_track.append(category)
            else:
                off_track.append({
                    "category": category,
                    "variance_percent": round(variance_pct, 1),
                    "direction": "over" if variance_pct > 0 else "under",
                    "severity": "high" if abs(variance_pct) > 25 else "medium"
                })
        
        compliance_score = int(len(on_track) / len(rule.allocations) * 100) if rule.allocations else 0
        
        # Generate recommendations
        recommendations = cls._generate_recommendations(
            rule_type, variances, variance_pcts, spending, income
        )
        
        # Project annual savings
        actual_savings = spending.get("savings", Decimal("0")) + spending.get("investments", Decimal("0"))
        projected_annual = actual_savings * 12
        
        # Estimate years to FI (simplified 4% rule)
        years_to_fi = None
        if actual_savings > 0:
            savings_rate = float(actual_savings / income)
            if savings_rate > 0:
                # Simplified: Years = 25 / savings_rate (very rough)
                years_to_fi = int(25 / savings_rate)
        
        return BudgetAnalysis(
            rule_type=rule_type,
            income=income,
            actual_spending=category_mapping,
            target_allocation=targets,
            variance=variances,
            variance_percent=variance_pcts,
            compliance_score=compliance_score,
            on_track_categories=on_track,
            off_track_categories=off_track,
            recommendations=recommendations,
            projected_savings_annual=projected_annual,
            years_to_financial_independence=years_to_fi
        )
    
    @classmethod
    def _map_to_rule_categories(
        cls,
        spending: Dict[str, Decimal],
        rule_type: BudgetRuleType
    ) -> Dict[str, Decimal]:
        """Map detailed spending to rule categories"""
        # Define mappings
        mappings = {
            BudgetRuleType.FIFTY_THIRTY_TWENTY: {
                "needs": ["housing", "utilities", "food", "transport", "insurance", "health", "debt_payments"],
                "wants": ["dining_out", "entertainment", "shopping", "travel", "personal_care", "gifts_donations", "education", "subscriptions"],
                "savings": ["investments", "savings", "emergency_fund"]
            },
            BudgetRuleType.NINETY_TEN: {
                "living": ["housing", "utilities", "food", "transport", "insurance", "health", "dining_out", "entertainment", "shopping", "personal_care", "subscriptions", "phone_internet"],
                "investing": ["investments", "savings", "pension"]
            },
            BudgetRuleType.SIXTY_TWENTY_TWENTY: {
                "living": ["housing", "utilities", "food", "transport", "insurance", "health", "phone_internet"],
                "savings": ["investments", "savings", "pension", "emergency_fund"],
                "fun": ["dining_out", "entertainment", "shopping", "travel", "personal_care", "subscriptions"]
            },
            BudgetRuleType.SEVENTY_TWENTY_TEN: {
                "living": ["housing", "utilities", "food", "transport", "insurance", "health", "subscriptions", "phone_internet", "personal_care"],
                "savings": ["investments", "savings", "pension"],
                "debt_giving": ["debt_payments", "gifts_donations", "charity"]
            },
            BudgetRuleType.EIGHTY_TWENTY: {
                "everything": list(spending.keys()),
                "savings": ["investments", "savings", "pension"]
            }
        }
        
        mapping = mappings.get(rule_type, {})
        result = {cat: Decimal("0") for cat in mapping.keys()}
        
        for rule_cat, detail_cats in mapping.items():
            for detail_cat in detail_cats:
                if detail_cat in spending:
                    result[rule_cat] += spending[detail_cat]
        
        return result
    
    @classmethod
    def _generate_recommendations(
        cls,
        rule_type: BudgetRuleType,
        variances: Dict[str, Decimal],
        variance_pcts: Dict[str, float],
        spending: Dict[str, Decimal],
        income: Decimal
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Check for overspending
        for category, variance_pct in variance_pcts.items():
            if variance_pct > 25:
                recommendations.append(
                    f"{category.upper()}: You're spending {variance_pct:.0f}% more than target. "
                    f"Consider reducing this category to align with the {rule_type.value} rule."
                )
            elif variance_pct < -20:
                recommendations.append(
                    f"{category.upper()}: You're underspending by {abs(variance_pct):.0f}%. "
                    f"Good discipline, but ensure you're not sacrificing necessities."
                )
        
        # Rule-specific recommendations
        if rule_type == BudgetRuleType.FIFTY_THIRTY_TWENTY:
            needs_pct = variance_pcts.get("needs", 0)
            if needs_pct > 10:
                recommendations.append(
                    "Your essential expenses are high. Consider: downsizing housing, "
                    "refinancing debt, or increasing income to improve the 50% target."
                )
            savings_pct = variance_pcts.get("savings", 0)
            if savings_pct < -10:
                recommendations.append(
                    "Increase savings to 20% by automating transfers on payday. "
                    "Pay yourself first before discretionary spending."
                )
        
        elif rule_type == BudgetRuleType.NINETY_TEN:
            if variance_pcts.get("investing", 0) < -50:
                recommendations.append(
                    "Critical: You're investing less than 5%. Minimum target is 10%. "
                    "Start with £10/week auto-invest to build the habit."
                )
        
        elif rule_type == BudgetRuleType.PAY_YOURSELF_FIRST:
            recommendations.append(
                "Set up automatic transfer to savings on payday. "
                "Treat savings like a non-negotiable bill."
            )
        
        # Add generic recommendations if list is short
        if len(recommendations) < 2:
            recommendations.extend([
                "Review subscriptions monthly - cancel unused services.",
                "Use cashback cards for all purchases to maximize returns.",
                "Meal plan weekly to reduce food waste and dining out costs."
            ])
        
        return recommendations[:5]  # Top 5
    
    @classmethod
    def compare_all_rules(
        cls,
        income: Decimal,
        spending: Dict[str, Decimal]
    ) -> Dict[str, Any]:
        """Compare spending against all budget rules"""
        comparisons = []
        
        for rule_type in cls.RULES.keys():
            analysis = cls.analyze_against_rule(rule_type, income, spending)
            
            comparisons.append({
                "rule": cls.RULES[rule_type].name,
                "type": rule_type.value,
                "compliance_score": analysis.compliance_score,
                "projected_annual_savings": float(analysis.projected_savings_annual),
                "years_to_fi": analysis.years_to_financial_independence,
                "on_track": len(analysis.on_track_categories),
                "off_track": len(analysis.off_track_categories),
                "recommendation_count": len(analysis.recommendations)
            })
        
        # Sort by compliance score
        comparisons.sort(key=lambda x: x["compliance_score"], reverse=True)
        
        return {
            "income": float(income),
            "total_monthly_spending": float(sum(spending.values())),
            "comparisons": comparisons,
            "best_fit": comparisons[0] if comparisons else None,
            "needs_attention": [c for c in comparisons if c["compliance_score"] < 50]
        }
    
    @classmethod
    def create_action_plan(
        cls,
        current_rule: BudgetRuleType,
        target_rule: BudgetRuleType,
        income: Decimal,
        current_spending: Dict[str, Decimal]
    ) -> Dict[str, Any]:
        """Create transition plan between budget rules"""
        current = cls.RULES[current_rule]
        target = cls.RULES[target_rule]
        
        # Calculate required changes
        changes = []
        
        for category, target_pct in target.allocations.items():
            target_amount = income * Decimal(str(target_pct / 100))
            current_amount = current_spending.get(category, Decimal("0"))
            difference = target_amount - current_amount
            
            changes.append({
                "category": category,
                "current": float(current_amount),
                "target": float(target_amount),
                "difference": float(difference),
                "change_needed": "increase" if difference > 0 else "decrease",
                "percent_change": float(difference / current_amount * 100) if current_amount > 0 else 0
            })
        
        # Sort by magnitude of change
        changes.sort(key=lambda x: abs(x["difference"]), reverse=True)
        
        # Determine timeline
        difficulty = target.difficulty
        if difficulty == "easy":
            timeline = "1-2 months"
        elif difficulty == "medium":
            timeline = "2-4 months"
        else:
            timeline = "4-6 months"
        
        return {
            "from_rule": current.name,
            "to_rule": target.name,
            "timeline": timeline,
            "required_changes": changes[:3],  # Top 3
            "total_monthly_shift": float(sum(abs(c["difference"]) for c in changes)),
            "steps": [
                f"Week 1-2: Set up tracking for {target.name} categories",
                f"Week 3-4: Reduce spending in {changes[0]['category'] if changes else 'highest'} category",
                f"Month 2: Automate savings/investments for new allocation",
                f"Month 3: Full transition and review"
            ],
            "difficulty": difficulty,
            "success_probability": "high" if current.difficulty == target.difficulty else "medium"
        }


# Global engine instance
_budget_engine: Optional[BudgetRulesEngine] = None


def get_budget_engine() -> BudgetRulesEngine:
    """Get or create budget rules engine"""
    global _budget_engine
    if _budget_engine is None:
        _budget_engine = BudgetRulesEngine()
    return _budget_engine
