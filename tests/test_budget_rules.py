"""
Unit Tests for Budget Rules Module
"""
import pytest
from decimal import Decimal
from datetime import date
from src.backend.app.personal.budget_rules import (
    BudgetRulesEngine, BudgetRuleType, get_budget_engine
)


class TestBudgetRulesEngine:
    """Test budget rules functionality"""
    
    @pytest.fixture
    def engine(self):
        return get_budget_engine()
    
    def test_get_all_rules(self, engine):
        """Test retrieving all budget rules"""
        rules = engine.get_all_rules()
        assert len(rules) == 10  # Should have 10 rules
        assert BudgetRuleType.FIFTY_THIRTY_TWENTY in rules
        assert BudgetRuleType.NINETY_TEN in rules
    
    def test_get_specific_rule(self, engine):
        """Test retrieving specific rule"""
        rule = engine.get_rule(BudgetRuleType.FIFTY_THIRTY_TWENTY)
        assert rule is not None
        assert rule.name == "50/30/20 Rule"
        assert rule.allocations == {"needs": 50.0, "wants": 30.0, "savings": 20.0}
        assert rule.savings_rate == 20.0
    
    def test_fifty_thirty_twenty_analysis(self, engine):
        """Test 50/30/20 rule analysis"""
        income = Decimal("3000")
        spending = {
            "needs": Decimal("1500"),  # 50%
            "wants": Decimal("900"),   # 30%
            "savings": Decimal("600")  # 20%
        }
        
        analysis = engine.analyze_against_rule(
            BudgetRuleType.FIFTY_THIRTY_TWENTY, income, spending
        )
        
        assert analysis.rule_type == BudgetRuleType.FIFTY_THIRTY_TWENTY
        assert analysis.income == income
        assert analysis.compliance_score == 100  # Perfect match
        assert len(analysis.on_track_categories) == 3
        assert len(analysis.off_track_categories) == 0
    
    def test_ninety_ten_analysis(self, engine):
        """Test 90/10 rule analysis"""
        income = Decimal("2000")
        spending = {
            "living": Decimal("1800"),    # 90%
            "investing": Decimal("200")   # 10%
        }
        
        analysis = engine.analyze_against_rule(
            BudgetRuleType.NINETY_TEN, income, spending
        )
        
        assert analysis.compliance_score == 100
        assert analysis.target_allocation["living"] == Decimal("1800")
        assert analysis.target_allocation["investing"] == Decimal("200")
    
    def test_overspending_detection(self, engine):
        """Test detection of overspending"""
        income = Decimal("3000")
        spending = {
            "needs": Decimal("1800"),    # 60% - over 50% target
            "wants": Decimal("900"),     # 30% - on target
            "savings": Decimal("300")    # 10% - under 20% target
        }
        
        analysis = engine.analyze_against_rule(
            BudgetRuleType.FIFTY_THIRTY_TWENTY, income, spending
        )
        
        # Should be off track for needs (60% vs 50% target)
        assert len(analysis.off_track_categories) >= 1
        
        # Check needs variance
        needs_variance = analysis.variance_percent.get("needs", 0)
        assert needs_variance > 0  # Positive means over budget
    
    def test_recommendations_generation(self, engine):
        """Test that recommendations are generated"""
        income = Decimal("3000")
        spending = {
            "needs": Decimal("2100"),    # 70% - way over
            "wants": Decimal("600"),     # 20% - under
            "savings": Decimal("300")    # 10% - way under
        }
        
        analysis = engine.analyze_against_rule(
            BudgetRuleType.FIFTY_THIRTY_TWENTY, income, spending
        )
        
        assert len(analysis.recommendations) > 0
        # Should have recommendation about high needs
        needs_recommendations = [r for r in analysis.recommendations if "needs" in r.lower()]
        assert len(needs_recommendations) > 0
    
    def test_compare_all_rules(self, engine):
        """Test comparing against all rules"""
        income = Decimal("2500")
        spending = {
            "needs": Decimal("1250"),
            "wants": Decimal("750"),
            "savings": Decimal("500")
        }
        
        comparison = engine.compare_all_rules(income, spending)
        
        assert "comparisons" in comparison
        assert len(comparison["comparisons"]) == 10  # All 10 rules
        assert "best_fit" in comparison
        assert comparison["income"] == 2500.0
    
    def test_recommend_rule_for_situation(self, engine):
        """Test rule recommendation based on profile"""
        recommendations = engine.recommend_rule(
            income=Decimal("1500"),
            age=25,
            has_debt=True,
            family_size=1,
            lifestyle="frugal",
            discipline_level="low"
        )
        
        assert len(recommendations) > 0
        top_pick = recommendations[0]
        assert "score" in top_pick
        assert "why" in top_pick
        assert len(top_pick["why"]) > 0
    
    def test_transition_plan(self, engine):
        """Test transition plan between rules"""
        income = Decimal("3000")
        spending = {
            "needs": Decimal("1500"),
            "wants": Decimal("900"),
            "savings": Decimal("600")
        }
        
        plan = engine.create_action_plan(
            BudgetRuleType.FIFTY_THIRTY_TWENTY,
            BudgetRuleType.NINETY_TEN,
            income, spending
        )
        
        assert plan["from_rule"] == "50/30/20 Rule"
        assert plan["to_rule"] == "90/10 Rule"
        assert "timeline" in plan
        assert "steps" in plan
        assert len(plan["steps"]) > 0
    
    def test_years_to_fi_calculation(self, engine):
        """Test financial independence projection"""
        income = Decimal("3000")
        spending = {
            "needs": Decimal("1200"),
            "wants": Decimal("600"),
            "savings": Decimal("1200")  # 40% savings rate
        }
        
        analysis = engine.analyze_against_rule(
            BudgetRuleType.FIFTY_THIRTY_TWENTY, income, spending
        )
        
        assert analysis.years_to_financial_independence is not None
        assert analysis.years_to_financial_independence > 0
        # With 40% savings rate, should be around 20-25 years
        assert analysis.years_to_financial_independence < 30
    
    def test_rule_flexibility_levels(self, engine):
        """Test that rules have different flexibility levels"""
        rule_50_30_20 = engine.get_rule(BudgetRuleType.FIFTY_THIRTY_TWENTY)
        rule_zero_based = engine.get_rule(BudgetRuleType.ZERO_BASED)
        
        assert rule_50_30_20.flexibility == "moderate"
        assert rule_zero_based.flexibility == "rigid"
    
    def test_invalid_rule_type(self, engine):
        """Test handling of invalid rule type"""
        with pytest.raises(KeyError):
            engine.get_rule("invalid_rule")


class TestBudgetRuleDetails:
    """Test individual budget rule configurations"""
    
    @pytest.fixture
    def engine(self):
        return get_budget_engine()
    
    def test_50_30_20_has_correct_allocations(self, engine):
        """Verify 50/30/20 allocations"""
        rule = engine.get_rule(BudgetRuleType.FIFTY_THIRTY_TWENTY)
        assert rule.allocations["needs"] == 50.0
        assert rule.allocations["wants"] == 30.0
        assert rule.allocations["savings"] == 20.0
        assert sum(rule.allocations.values()) == 100.0
    
    def test_90_10_has_correct_allocations(self, engine):
        """Verify 90/10 allocations"""
        rule = engine.get_rule(BudgetRuleType.NINETY_TEN)
        assert rule.allocations["living"] == 90.0
        assert rule.allocations["investing"] == 10.0
        assert sum(rule.allocations.values()) == 100.0
    
    def test_60_20_20_has_correct_allocations(self, engine):
        """Verify 60/20/20 allocations"""
        rule = engine.get_rule(BudgetRuleType.SIXTY_TWENTY_TWENTY)
        assert rule.allocations["living"] == 60.0
        assert rule.allocations["savings"] == 20.0
        assert rule.allocations["fun"] == 20.0
        assert sum(rule.allocations.values()) == 100.0
    
    def test_all_rules_sum_to_100_percent(self, engine):
        """Verify all rule allocations sum to 100%"""
        for rule_type, rule in engine.get_all_rules().items():
            if rule_type != BudgetRuleType.ONE_PERCENT_RULE:  # Special case
                total = sum(rule.allocations.values())
                assert total == 100.0, f"{rule.name} allocations sum to {total}, not 100"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
