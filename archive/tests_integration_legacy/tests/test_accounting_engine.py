"""
Test suite for accounting engine AI categorization
Tests transaction categorization, ML model training, and confidence scoring
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from app.accounting_engine.ai_categorization import (
    AICategorization,
    CategorizationRule,
    CategorizationResult,
    SimpleMLCategorizer
)


class TestAICategorization:
    """Test AI-powered transaction categorization"""
    
    @pytest.fixture
    def categorizer(self):
        """Create test categorizer instance"""
        return AICategorization()
    
    def test_initialization(self, categorizer):
        """Test categorizer initialization"""
        assert categorizer._rules == {}
        assert categorizer._ml_model is not None
        assert categorizer._corrections == []
        assert categorizer._category_stats is not None
    
    def test_add_rule(self, categorizer):
        """Test adding categorization rules"""
        rule = CategorizationRule(
            id="test_rule_1",
            pattern="starbucks|coffee",
            account_code="5400",
            category="Office Supplies",
            confidence=0.9,
            is_regex=True
        )
        
        categorizer.add_rule(rule)
        
        assert "test_rule_1" in categorizer._rules
        assert categorizer._rules["test_rule_1"].pattern == "starbucks|coffee"
    
    def test_categorize_transaction(self, categorizer):
        """Test transaction categorization"""
        # Test with existing rule
        result = categorizer.categorize_transaction(
            description="Starbucks Coffee Purchase",
            amount=4.50,
            date=datetime.now()
        )
        
        assert result is not None
        assert result.account_code == "5400"
        assert result.category == "Office Supplies"
        assert result.confidence >= 0.8
        assert result.method in ["rule", "ml", "default"]
    
    def test_ml_categorization(self, categorizer):
        """Test ML-based categorization"""
        # Train the ML model with sample data
        training_data = [
            {"description": "Uber Ride", "amount": 25.50, "category": "Transportation"},
            {"description": "Restaurant Bill", "amount": 45.00, "category": "Dining"},
            {"description": "Office Supplies", "amount": 15.75, "category": "Office Supplies"},
            {"description": "Software License", "amount": 99.00, "category": "Software"},
            {"description": "Electric Bill", "amount": 120.00, "category": "Utilities"}
        ]
        
        categorizer._ml_model.train(training_data)
        
        # Test categorization
        result = categorizer.categorize_transaction(
            description="Lyft Ride",
            amount=18.25,
            date=datetime.now()
        )
        
        assert result is not None
        assert result.method == "ml"
        assert result.confidence > 0.0
    
    def test_confidence_scoring(self, categorizer):
        """Test confidence scoring for categorization"""
        # High confidence match
        result1 = categorizer.categorize_transaction(
            description="Starbucks Coffee",
            amount=4.50,
            date=datetime.now()
        )
        
        # Low confidence match
        result2 = categorizer.categorize_transaction(
            description="Unknown Purchase",
            amount=100.00,
            date=datetime.now()
        )
        
        assert result1.confidence > result2.confidence
    
    def test_correction_feedback(self, categorizer):
        """Test learning from user corrections"""
        # Initial categorization
        result = categorizer.categorize_transaction(
            description="Amazon Purchase",
            amount=25.00,
            date=datetime.now()
        )
        
        # User correction
        categorizer.record_correction(
            description="Amazon Purchase",
            amount=25.00,
            predicted_category=result.category,
            correct_category="Software"
        )
        
        # Verify correction recorded
        assert len(categorizer._corrections) == 1
        assert categorizer._corrections[0]["correct_category"] == "Software"
    
    def test_category_statistics(self, categorizer):
        """Test category statistics tracking"""
        # Add some test data
        test_transactions = [
            ("Office Supplies", True, 0.9),
            ("Office Supplies", True, 0.8),
            ("Office Supplies", False, 0.7),
            ("Dining", True, 0.95),
            ("Dining", False, 0.6)
        ]
        
        for category, correct, confidence in test_transactions:
            categorizer._update_category_stats(category, correct, confidence)
        
        stats = categorizer.get_category_statistics()
        
        assert "Office Supplies" in stats
        assert stats["Office Supplies"]["total"] == 3
        assert stats["Office Supplies"]["correct"] == 2
        assert stats["Office Supplies"]["accuracy"] == pytest.approx(0.67, rel=1e-2)


class TestSimpleMLCategorizer:
    """Test simple ML categorizer implementation"""
    
    @pytest.fixture
    def ml_model(self):
        """Create test ML model"""
        return SimpleMLCategorizer()
    
    def test_feature_extraction(self, ml_model):
        """Test feature extraction from transaction descriptions"""
        features = ml_model._extract_features("Starbucks Coffee $4.50", 4.50)
        
        assert "amount" in features
        assert "description_length" in features
        assert "has_digits" in features
        assert "word_count" in features
        assert features["amount"] == 4.50
        assert features["description_length"] == 19
    
    def test_pattern_training(self, ml_model):
        """Test pattern training from historical data"""
        training_data = [
            {"description": "Uber Ride", "amount": 25.50, "category": "Transportation"},
            {"description": "Taxi Ride", "amount": 18.75, "category": "Transportation"},
            {"description": "Bus Ticket", "amount": 12.00, "category": "Transportation"},
            {"description": "Restaurant Bill", "amount": 45.00, "category": "Dining"},
            {"description": "Food Delivery", "amount": 32.50, "category": "Dining"}
        ]
        
        ml_model.train(training_data)
        
        # Verify patterns learned
        assert len(ml_model._category_patterns) > 0
        assert "Transportation" in ml_model._category_patterns
        assert "Dining" in ml_model._category_patterns
    
    def test_prediction_accuracy(self, ml_model):
        """Test prediction accuracy"""
        # Train model
        training_data = [
            {"description": "Starbucks Coffee", "amount": 4.50, "category": "Coffee"},
            {"description": "Coffee Shop", "amount": 6.25, "category": "Coffee"},
            {"description": "Espresso Stand", "amount": 3.75, "category": "Coffee"}
        ]
        ml_model.train(training_data)
        
        # Test predictions
        test_cases = [
            ("Starbucks Latte", "Coffee"),
            ("Coffee House", "Coffee"),
            ("Tea Shop", "Coffee")  # Should be lower confidence
        ]
        
        correct_predictions = 0
        for description, expected_category in test_cases:
            account_code, predicted_category, confidence = ml_model.predict(description, 10.0)
            
            if predicted_category == expected_category:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(test_cases)
        assert accuracy >= 0.5  # At least 50% accuracy
    
    def test_confidence_calculation(self, ml_model):
        """Test confidence score calculation"""
        # Train with known patterns
        training_data = [
            {"description": "Office Supplies Store", "amount": 25.00, "category": "Office Supplies"},
            {"description": "Office Depot", "amount": 45.50, "category": "Office Supplies"}
        ]
        ml_model.train(training_data)
        
        # Test exact match (high confidence)
        account_code, category, confidence = ml_model.predict("Office Supplies Store", 30.00)
        assert confidence >= 0.8
        
        # Test partial match (medium confidence)
        account_code, category, confidence = ml_model.predict("Office Shop", 20.00)
        assert confidence >= 0.3
        
        # Test no match (low confidence)
        account_code, category, confidence = ml_model.predict("Random Purchase", 50.00)
        assert confidence < 0.2
    
    def test_model_updates(self, ml_model):
        """Test model updates from corrections"""
        # Initial training
        initial_data = [
            {"description": "Gas Station", "amount": 40.00, "category": "Fuel"}
        ]
        ml_model.train(initial_data)
        
        # Add correction
        ml_model.update_from_correction("Gas Station", 40.00, "Transportation")
        
        # Verify model updated
        assert len(ml_model._training_data) == 2
        assert ml_model._training_data[1]["category"] == "Transportation"


class TestCategorizationPerformance:
    """Test categorization performance metrics"""
    
    @pytest.fixture
    def categorizer(self):
        """Create test categorizer with sample data"""
        cat = AICategorization()
        
        # Add sample rules
        cat.add_rule(CategorizationRule(
            id="rule1", pattern="coffee|starbucks", 
            account_code="5400", category="Coffee", confidence=0.9
        ))
        cat.add_rule(CategorizationRule(
            id="rule2", pattern="gas|fuel", 
            account_code="5300", category="Fuel", confidence=0.95
        ))
        
        return cat
    
    def test_batch_categorization(self, categorizer):
        """Test batch categorization of multiple transactions"""
        transactions = [
            {"description": "Starbucks Coffee", "amount": 4.50},
            {"description": "Shell Gas", "amount": 45.00},
            {"description": "Office Supplies", "amount": 25.75},
            {"description": "Unknown Item", "amount": 15.00}
        ]
        
        results = categorizer.categorize_batch(transactions)
        
        assert len(results) == 4
        assert all(r is not None for r in results)
        assert results[0].category == "Coffee"
        assert results[1].category == "Fuel"
        assert results[2].category == "Office Supplies"
    
    def test_performance_metrics(self, categorizer):
        """Test categorization performance metrics"""
        # Add test corrections
        categorizer.record_correction("Test Desc", 10.00, "Wrong Category", "Correct Category")
        categorizer.record_correction("Test Desc 2", 20.00, "Wrong Category", "Correct Category")
        categorizer.record_correction("Test Desc 3", 15.00, "Correct Category", "Correct Category")
        
        metrics = categorizer.get_performance_metrics()
        
        assert "total_transactions" in metrics
        assert "accuracy" in metrics
        assert "corrections_count" in metrics
        assert metrics["corrections_count"] == 3
    
    def test_export_import_rules(self, categorizer):
        """Test exporting and importing categorization rules"""
        # Export rules
        rules_data = categorizer.export_rules()
        
        assert isinstance(rules_data, dict)
        assert len(rules_data) > 0
        
        # Create new categorizer and import rules
        new_categorizer = AICategorization()
        new_categorizer.import_rules(rules_data)
        
        # Verify rules imported
        assert len(new_categorizer._rules) == len(categorizer._rules)


if __name__ == "__main__":
    pytest.main([__file__])
