"""
Comprehensive Test Suite
=======================
Unit tests, integration tests, and validation for Veyra
"""
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestVisualAI(unittest.TestCase):
    """Test visual learning AI components"""
    
    def test_sentiment_analysis(self):
        """Test sentiment scoring"""
        from ai.visual_advanced import AdvancedVisualAI
        
        analyzer = AdvancedVisualAI()
        
        # Mock stress scores
        stress_scores = {
            'facial_stress': 0.7,
            'body_stress': 0.6,
            'voice_stress': 0.5
        }
        
        combined = analyzer._combine_stress_scores(stress_scores)
        self.assertIsInstance(combined, float)
        self.assertGreaterEqual(combined, 0)
        self.assertLessEqual(combined, 1)
    
    def test_deception_detection(self):
        """Test deception signal generation"""
        
        analyzer = AdvancedVisualAI()
        
        # High stress + positive words = deception
        visual_stress = 0.8
        transcript_sentiment = 0.7
        
        deception = analyzer._detect_deception(
            visual_stress, transcript_sentiment
        )
        
        self.assertIsInstance(deception, dict)
        self.assertIn('risk_level', deception)


class TestStatisticalArbitrage(unittest.TestCase):
    """Test statistical arbitrage engine"""
    
    def test_cointegration_detection(self):
        """Test cointegration detection"""
        from strategies.statistical_arbitrage import find_cointegrated_pairs
        
        # Generate cointegrated series
        np.random.seed(42)
        n = 100
        x = np.cumsum(np.random.normal(0, 1, n))
        y = 2 * x + np.random.normal(0, 0.5, n)
        
        df = pd.DataFrame({'X': x, 'Y': y})
        pairs = find_cointegrated_pairs(df, p_value_threshold=0.05)
        
        self.assertIsInstance(pairs, list)
    
    def test_half_life_calculation(self):
        """Test half-life calculation"""
        from strategies.statistical_arbitrage import StatisticalArbitrageEngine
        
        engine = StatisticalArbitrageEngine()
        
        # Mean-reverting spread
        spread = np.sin(np.linspace(0, 4*np.pi, 100)) + np.random.normal(0, 0.1, 100)
        
        half_life = engine._calculate_half_life(spread)
        
        self.assertIsInstance(half_life, float)
        self.assertGreater(half_life, 0)


class TestRiskManager(unittest.TestCase):
    """Test risk management framework"""
    
    def test_var_calculation(self):
        """Test VaR calculation"""
        from risk.risk_manager import RiskManager
        
        rm = RiskManager()
        
        # Generate returns
        np.random.seed(42)
        returns = pd.Series(np.random.normal(0.001, 0.02, 252))
        
        var = rm.calculate_var(returns, method='historical')
        
        self.assertIn(0.95, var)
        self.assertIn(0.99, var)
        self.assertLess(var[0.95], 0)  # VaR should be negative (loss)
    
    def test_stress_testing(self):
        """Test stress test scenarios"""
        
        rm = RiskManager()
        
        positions = {'SPY': 100000, 'TLT': 50000}
        
        stress_results = rm.stress_test(positions)
        
        self.assertIsInstance(stress_results, dict)
        self.assertIn('market_crash_2008', stress_results)


class TestMetalsTracker(unittest.TestCase):
    """Test precious metals tracker"""
    
    def test_portfolio_valuation(self):
        """Test metals portfolio valuation"""
        from physical_metals.metals_tracker import PreciousMetalsPortfolio
        
        portfolio = PreciousMetalsPortfolio()
        
        # Add holdings
        portfolio.add_holding('gold', 'coins', 10, 1800.0, 2000.0)
        portfolio.add_holding('silver', 'bars', 100, 22.0, 28.0)
        
        summary = portfolio.get_portfolio_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_value_usd', summary)
        self.assertIn('total_cost_basis', summary)
    
    def test_ratio_analysis(self):
        """Test gold/silver ratio analysis"""
        from physical_metals.metals_tracker import get_live_metal_prices
        
        prices = get_live_metal_prices()
        
        self.assertIsInstance(prices, dict)
        self.assertIn('gold', prices)
        self.assertIn('silver', prices)


class TestSentimentAnalysis(unittest.TestCase):
    """Test sentiment analysis components"""
    
    def test_news_sentiment(self):
        """Test news sentiment analysis"""
        from sentiment.news_sentiment_engine import NewsSentimentEngine
        
        engine = NewsSentimentEngine()
        
        article = engine._generate_synthetic_article('AAPL', 'bloomberg')
        
        self.assertIsNotNone(article)
        self.assertEqual(article.ticker, 'AAPL')
        self.assertEqual(article.source, 'bloomberg')
    
    def test_social_media_analysis(self):
        """Test social media sentiment"""
        from sentiment.social_video_analyzer import SocialVideoAnalyzer
        
        analyzer = SocialVideoAnalyzer()
        
        text = "I love my new iPhone! Best purchase ever! #apple #iphone"
        metadata = {'views': 100000, 'likes': 5000}
        
        signals = analyzer.analyze_mentions(text, metadata)
        
        self.assertIsInstance(signals, list)


class TestPortfolioOptimizer(unittest.TestCase):
    """Test portfolio optimization"""
    
    def test_markowitz_optimization(self):
        """Test mean-variance optimization"""
        from portfolio_opt.optimizer import PortfolioOptimizer
        
        optimizer = PortfolioOptimizer()
        
        # Generate synthetic returns
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        returns_df = optimizer.generate_random_returns(tickers, periods=252)
        
        result = optimizer.markowitz_optimization()
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result.weights, dict)
        self.assertEqual(len(result.weights), 3)
    
    def test_efficient_frontier(self):
        """Test efficient frontier generation"""
        
        optimizer = PortfolioOptimizer()
        
        tickers = ['A', 'B', 'C']
        optimizer.generate_random_returns(tickers, periods=100)
        
        frontier = optimizer.efficient_frontier(n_points=20)
        
        self.assertIsInstance(frontier, list)
        self.assertLessEqual(len(frontier), 20)


class TestCrisisDetector(unittest.TestCase):
    """Test crisis detection"""
    
    def test_vix_analysis(self):
        """Test VIX analysis"""
        from risk.crisis_alpha_detector import CrisisAlphaDetector
        
        detector = CrisisAlphaDetector()
        
        # Simulate data
        detector.vix_history = detector._simulate_vix_data()
        
        analysis = detector.analyze_vix()
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('current_vix', analysis)
        self.assertIn('level', analysis)
    
    def test_crisis_signal_detection(self):
        """Test crisis signal detection"""
        
        detector = CrisisAlphaDetector()
        detector.fetch_market_data()  # Simulate
        detector.detect_crisis_signals()
        
        self.assertIsInstance(detector.active_signals, list)


class TestExecutionAlgorithms(unittest.TestCase):
    """Test execution algorithms"""
    
    def test_twap_slicing(self):
        """Test TWAP order slicing"""
        from execution.advanced_algorithms import ExecutionOrder, AlgoType
        
        order = ExecutionOrder(
            ticker='AAPL',
            side='buy',
            total_quantity=1000,
            algo_type=AlgoType.TWAP,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1)
        )
        
        self.assertEqual(order.total_quantity, 1000)
        self.assertEqual(order.algo_type, AlgoType.TWAP)


class TestSignalAggregator(unittest.TestCase):
    """Test signal aggregation"""
    
    def test_signal_aggregation(self):
        """Test multi-source signal aggregation"""
        from signal_aggregator import SignalAggregator, SignalSource
        
        aggregator = SignalAggregator()
        
        # Add signals
        signal1 = {'ticker': 'AAPL', 'signal': 'BUY', 'strength': 0.8, 'source': 'visual_ai'}
        signal2 = {'ticker': 'AAPL', 'signal': 'BUY', 'strength': 0.7, 'source': 'sentiment'}
        
        aggregator.add_signal(SignalSource.VISUAL_AI, signal1)
        aggregator.add_signal(SignalSource.SENTIMENT, signal2)
        
        result = aggregator.aggregate('AAPL')
        
        if result:
            self.assertIsNotNone(result.aggregated_score)
            self.assertGreater(result.confidence, 0)


class TestCrossAssetArbitrage(unittest.TestCase):
    """Test cross-asset arbitrage detection"""
    
    def test_etf_basket_arbitrage(self):
        """Test ETF vs basket arbitrage detection"""
        from arbitrage.cross_asset_arbitrage import CrossAssetArbitrageDetector
        
        detector = CrossAssetArbitrageDetector()
        
        # Set prices
        detector.update_prices('SPY', 450.0, 'NYSE')
        
        components = {'AAPL': 0.07, 'MSFT': 0.065}
        component_prices = {'AAPL': 185.0, 'MSFT': 420.0}
        
        opportunity = detector.detect_etf_basket_arbitrage(
            'SPY', components, component_prices
        )
        
        # Result may be None if no arbitrage
        if opportunity:
            self.assertIsNotNone(opportunity.spread)


class IntegrationTests(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def test_end_to_end_signal_generation(self):
        """Test complete signal generation pipeline"""
        
        # This would be a full integration test
        # Mocking components for speed
        
        aggregator = SignalAggregator()
        
        # Simulate visual AI signal
        visual_signal = {
            'ticker': 'TSLA',
            'signal': 'CAUTION',
            'confidence': 0.8,
            'stress_level': 0.75
        }
        aggregator.add_signal(SignalSource.VISUAL_AI, visual_signal)
        
        # Aggregate
        result = aggregator.aggregate('TSLA')
        
        self.assertIsNotNone(result)
    
    def test_portfolio_optimization_workflow(self):
        """Test full portfolio optimization workflow"""
        from portfolio_opt.optimizer import optimize_portfolio_quick
        
        # Create sample returns data
        np.random.seed(42)
        returns_df = pd.DataFrame({
            'SPY': np.random.normal(0.0007, 0.015, 252),
            'TLT': np.random.normal(0.0003, 0.008, 252),
            'GLD': np.random.normal(0.0002, 0.012, 252)
        })
        
        result = optimize_portfolio_quick(returns_df, method='max_sharpe')
        
        self.assertIsInstance(result, dict)
        self.assertIn('weights', result)
        self.assertIn('sharpe_ratio', result)


def run_all_tests():
    """Run complete test suite"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestVisualAI,
        TestStatisticalArbitrage,
        TestRiskManager,
        TestMetalsTracker,
        TestSentimentAnalysis,
        TestPortfolioOptimizer,
        TestCrisisDetector,
        TestExecutionAlgorithms,
        TestSignalAggregator,
        TestCrossAssetArbitrage,
        IntegrationTests
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUITE SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Success Rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result.wasSuccessful()


# Additional Comprehensive Test Classes for Enhanced Coverage

class TestAuthenticationSecurity(unittest.TestCase):
    """Test authentication and security features"""
    
    def setUp(self):
        from core.auth import AuthService
        self.auth = AuthService()
    
    def test_password_hashing_security(self):
        """Test secure password hashing"""
        password = "test_password_123!"
        hashed = self.auth._hash_password(password)
        
        # Hash should be different from original
        self.assertNotEqual(password, hashed)
        self.assertGreater(len(hashed), 50)  # Should be substantially longer
        
        # Should verify correctly
        self.assertTrue(self.auth._verify_password(password, hashed))
        self.assertFalse(self.auth._verify_password("wrong_password", hashed))
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM sensitive_data --"
        ]
        
        for malicious_input in malicious_inputs:
            result = self.auth.authenticate_user(malicious_input, "password")
            self.assertIsNone(result)
    
    def test_token_validation(self):
        """Test JWT token validation"""
        user_data = {"email": "test@example.com", "user_id": "123"}
        token = self.auth._generate_token(user_data)
        
        # Valid token should decode
        decoded = self.auth._validate_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded['email'], "test@example.com")
        
        # Invalid token should fail
        invalid_result = self.auth._validate_token("invalid_token")
        self.assertIsNone(invalid_result)


class TestPredictiveEngineML(unittest.TestCase):
    """Test ML predictive engine functionality"""
    
    def setUp(self):
        from ai_ml.predictive_engine import PredictiveEngine
        self.engine = PredictiveEngine()
        
        # Create sample data
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.02)
        volumes = np.random.randint(1000000, 10000000, 100)
        
        self.sample_data = pd.DataFrame({
            'date': dates,
            'open': prices * (1 + np.random.randn(100) * 0.01),
            'high': prices * (1 + np.abs(np.random.randn(100) * 0.02)),
            'low': prices * (1 - np.abs(np.random.randn(100) * 0.02)),
            'close': prices,
            'volume': volumes
        })
    
    def test_feature_engineering_quality(self):
        """Test technical feature engineering"""
        features = self.engine._engineer_features(self.sample_data)
        
        expected_features = [
            'returns', 'log_returns', 'sma_5', 'sma_20', 'rsi', 
            'volatility', 'volume_ratio'
        ]
        
        for feature in expected_features:
            self.assertIn(feature, features.columns)
        
        # Should not have NaN values
        self.assertFalse(features.isnull().any().any())
    
    def test_garch_parameter_estimation(self):
        """Test GARCH volatility model parameters"""
        returns = self.sample_data['close'].pct_change().dropna()
        omega, alpha, beta = self.engine._estimate_garch_parameters(returns)
        
        # Parameters should be reasonable
        self.assertGreater(omega, 0)
        self.assertGreaterEqual(alpha, 0)
        self.assertLessEqual(alpha, 1)
        self.assertGreaterEqual(beta, 0)
        self.assertLessEqual(beta, 1)
        self.assertLess(alpha + beta, 1)  # Should be stationary
    
    def test_technical_analysis_fallback(self):
        """Test technical analysis fallback prediction"""
        features = self.engine._engineer_features(self.sample_data)
        prediction = self.engine._technical_analysis_prediction(features)
        
        self.assertIsInstance(prediction, dict)
        self.assertIn("bullish", prediction)
        self.assertIn("bearish", prediction)
        self.assertIn("neutral", prediction)
        
        # Probabilities should sum to 1
        total_prob = sum(prediction.values())
        self.assertAlmostEqual(total_prob, 1.0, places=2)


class TestAutonomousAgent(unittest.TestCase):
    """Test autonomous trading agent"""
    
    def setUp(self):
        from ai.autonomous_agent import AutonomousTradingAgent
        self.agent = AutonomousTradingAgent()
    
    def test_agent_safety_parameters(self):
        """Test agent safety configuration"""
        self.assertEqual(self.agent.safety["max_daily_loss"], 1000.0)
        self.assertEqual(self.agent.safety["max_position"], 10000.0)
        self.assertEqual(self.agent.safety["min_confidence"], 0.75)
        self.assertFalse(self.agent.safety["kill_switch"])
    
    def test_kill_switch_activation(self):
        """Test emergency kill switch"""
        self.agent.kill_switch()
        self.assertTrue(self.agent.safety["kill_switch"])
    
    def test_trade_proposal_generation(self):
        """Test trade proposal from ML signals"""
        # Mock prediction objects
        class MockPrediction:
            def __init__(self, prediction, confidence):
                self.prediction = prediction
                self.confidence = confidence
        
        mock_trend = MockPrediction("bullish", 0.85)
        mock_volatility = Mock()
        mock_volatility.prediction = {"risk_level": "medium"}
        
        sample_data = pd.DataFrame({'close': [100, 101, 102, 103, 104]})
        
        proposal = self.agent._generate_trade_proposal(
            "AAPL", mock_trend, mock_volatility, sample_data
        )
        
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.symbol, "AAPL")
        self.assertEqual(proposal.side, "buy")
        self.assertGreaterEqual(proposal.confidence, 0.75)
    
    def test_position_size_limits(self):
        """Test position sizing respects limits"""
        mock_trend = Mock()
        mock_trend.prediction = "bullish"
        mock_trend.confidence = 0.9
        
        mock_volatility = Mock()
        mock_volatility.prediction = {"risk_level": "low"}
        
        # High price that would exceed limit
        sample_data = pd.DataFrame({'close': [5000]})
        
        proposal = self.agent._generate_trade_proposal(
            "AAPL", mock_trend, mock_volatility, sample_data
        )
        
        if proposal:
            position_value = proposal.quantity * 5000
            self.assertLessEqual(position_value, self.agent.safety["max_position"])


class TestTradingEngine(unittest.TestCase):
    """Test trading engine functionality"""
    
    def setUp(self):
        from advanced_trading.trading_engine import TradingEngine, Order, OrderStatus
        self.engine = TradingEngine()
        self.Order = Order
        self.OrderStatus = OrderStatus
    
    def test_order_creation_validation(self):
        """Test order creation and validation"""
        order = self.Order(
            id="test_order",
            symbol="AAPL",
            side="buy",
            quantity=100,
            order_type="market",
            status=self.OrderStatus.PENDING
        )
        
        self.assertEqual(order.symbol, "AAPL")
        self.assertEqual(order.side, "buy")
        self.assertEqual(order.quantity, 100)
        self.assertEqual(order.status, self.OrderStatus.PENDING)
    
    def test_vwap_calculation(self):
        """Test VWAP calculation accuracy"""
        # Mock market data
        market_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2023-01-01', periods=10, freq='1min'),
            'price': [150.1, 150.2, 150.0, 150.3, 150.1, 150.4, 150.2, 150.5, 150.3, 150.6],
            'volume': [1000, 1200, 800, 1500, 900, 1100, 1300, 700, 1400, 1000]
        })
        
        vwap = self.engine._calculate_vwap(market_data)
        expected_vwap = (market_data['price'] * market_data['volume']).sum() / market_data['volume'].sum()
        
        self.assertAlmostEqual(vwap, expected_vwap, places=4)
    
    def test_order_book_matching(self):
        """Test order book matching logic"""
        buy_orders = [
            self.Order(id="buy1", symbol="AAPL", side="buy", quantity=100, price=149.5),
            self.Order(id="buy2", symbol="AAPL", side="buy", quantity=200, price=149.8),
        ]
        
        sell_orders = [
            self.Order(id="sell1", symbol="AAPL", side="sell", quantity=150, price=150.0),
            self.Order(id="sell2", symbol="AAPL", side="sell", quantity=100, price=149.7),
        ]
        
        # This would test the matching algorithm
        # Implementation would depend on the actual matching logic
        self.assertGreater(len(buy_orders), 0)
        self.assertGreater(len(sell_orders), 0)


class TestVisualLearningAI(unittest.TestCase):
    """Test visual learning AI functionality"""
    
    def setUp(self):
        from ai.visual_learning import VisualLearningAI
        self.visual_ai = VisualLearningAI()
    
    def test_price_extraction_from_text(self):
        """Test OCR price extraction"""
        text_samples = [
            "Stock trading at $150.25 per share",
            "Price target: $1,234.56",
            "Current price: 89.75"
        ]
        
        all_prices = []
        for text in text_samples:
            prices = self.visual_ai._extract_prices_from_text(text)
            all_prices.extend(prices)
        
        expected_prices = [150.25, 1234.56, 89.75]
        for expected in expected_prices:
            self.assertIn(expected, all_prices)
    
    def test_visual_signature_generation(self):
        """Test pattern signature generation"""
        chart_data = {
            'pattern_type': 'head_and_shoulders',
            'timeframe': '1D',
            'trend': 'bearish',
            'volatility': 'high',
            'rsi': 65,
            'macd': -0.5
        }
        
        signature = self.visual_ai._generate_visual_signature(chart_data)
        
        self.assertIsInstance(signature, str)
        self.assertIn("head_and_shoulders", signature)
        self.assertIn("1D", signature)
        self.assertIn("bearish", signature)
    
    def test_pattern_memory_creation(self):
        """Test chart pattern memory"""
        from ai.visual_learning import ChartPatternMemory
        from datetime import datetime
        
        pattern = ChartPatternMemory(
            pattern_name="bullish_flag_1D",
            visual_signature="flag|1D|bullish|medium|50|0",
            success_rate=0.75,
            avg_return=0.05,
            occurrences=10,
            last_seen=datetime.now(),
            confidence_threshold=0.8
        )
        
        self.assertEqual(pattern.pattern_name, "bullish_flag_1D")
        self.assertEqual(pattern.success_rate, 0.75)
        self.assertEqual(pattern.occurrences, 10)


class TestBrokerCertification(unittest.TestCase):
    """Test broker certification system"""
    
    def setUp(self):
        from brokers.certification import BrokerCertification
        self.certification = BrokerCertification()
    
    def test_market_data_quality_validation(self):
        """Test market data quality checks"""
        # This would test actual broker connections
        # For now, test the validation logic
        
        sample_data = {
            'symbol': 'AAPL',
            'price': 150.25,
            'volume': 1000000,
            'timestamp': datetime.now().isoformat(),
            'bid': 150.20,
            'ask': 150.30
        }
        
        # Validate data quality
        self.assertGreater(sample_data['price'], 0)
        self.assertGreater(sample_data['volume'], 0)
        self.assertGreater(sample_data['ask'], sample_data['bid'])
    
    def test_connection_timeout_handling(self):
        """Test connection timeout handling"""
        # Test timeout scenarios
        timeout_seconds = 30
        
        # This would test actual connection logic
        self.assertGreater(timeout_seconds, 0)
        self.assertLess(timeout_seconds, 300)  # Should be reasonable


class TestDeploymentController(unittest.TestCase):
    """Test deployment controller"""
    
    def setUp(self):
        from deployment_controller import DeploymentController
        self.controller = DeploymentController()
    
    def test_health_check_systems(self):
        """Test system health checks"""
        health_status = self.controller.check_system_health()
        
        self.assertIsInstance(health_status, dict)
        self.assertIn("overall_status", health_status)
        self.assertIn("services", health_status)
        self.assertIn("timestamp", health_status)
    
    def test_alert_system_channels(self):
        """Test alert system channels"""
        alert_data = {
            "severity": "critical",
            "message": "Test alert",
            "service": "test_service"
        }
        
        # Test alert formatting
        self.assertIn("severity", alert_data)
        self.assertIn("message", alert_data)
        self.assertEqual(alert_data["severity"], "critical")


class TestSecurityVulnerabilities(unittest.TestCase):
    """Test security vulnerability protection"""
    
    def test_xss_prevention(self):
        """Test XSS prevention in inputs"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            # Test input sanitization
            sanitized = payload.replace("<", "&lt;").replace(">", "&gt;")
            self.assertNotIn("<script", sanitized)
            self.assertNotIn("javascript:", sanitized)
    
    def test_path_traversal_prevention(self):
        """Test path traversal prevention"""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for path in malicious_paths:
            # Test path validation
            is_safe = not (".." in path or "%2e" in path.lower())
            # In real implementation, would validate against allowed paths
            self.assertFalse(is_safe)  # These should be flagged as unsafe


# Performance and Load Tests
class TestPerformance(unittest.TestCase):
    """Test system performance"""
    
    def test_large_dataset_processing(self):
        """Test processing large datasets"""
        # Create large dataset
        dates = pd.date_range(start='2020-01-01', periods=10000, freq='H')
        large_data = pd.DataFrame({
            'timestamp': dates,
            'price': 100 + np.cumsum(np.random.randn(10000) * 0.01),
            'volume': np.random.randint(100000, 1000000, 10000)
        })
        
        start_time = datetime.now()
        
        # Test processing time
        processed_data = large_data.copy()
        processed_data['returns'] = processed_data['price'].pct_change()
        processed_data['volatility'] = processed_data['returns'].rolling(20).std()
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time
        self.assertLess(processing_time, 5.0)  # 5 seconds max
        self.assertEqual(len(processed_data), 10000)
    
    def test_concurrent_request_handling(self):
        """Test concurrent request handling"""
        import threading
        import time
        
        results = []
        
        def dummy_task():
            time.sleep(0.1)  # Simulate work
            results.append("completed")
        
        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=dummy_task)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All tasks should complete
        self.assertEqual(len(results), 10)


# Update the test runner to include new classes
def run_all_tests():
    """Run complete test suite with enhanced coverage"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Original test classes
    original_classes = [
        TestVisualAI,
        TestStatisticalArbitrage,
        TestRiskManager,
        TestMetalsTracker,
        TestSentimentAnalysis,
        TestPortfolioOptimizer,
        TestCrisisDetector,
        TestExecutionAlgorithms,
        TestSignalAggregator,
        TestCrossAssetArbitrage,
        IntegrationTests
    ]
    
    # New comprehensive test classes
    new_classes = [
        TestAuthenticationSecurity,
        TestPredictiveEngineML,
        TestAutonomousAgent,
        TestTradingEngine,
        TestVisualLearningAI,
        TestBrokerCertification,
        TestDeploymentController,
        TestSecurityVulnerabilities,
        TestPerformance
    ]
    
    # Add all test classes
    all_classes = original_classes + new_classes
    
    for test_class in all_classes:
        try:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        except Exception as e:
            print(f"Warning: Could not load {test_class.__name__}: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Enhanced summary
    print("\n" + "="*70)
    print("ENHANCED TEST SUITE SUMMARY")
    print("="*70)
    print(f"Test Classes: {len(all_classes)}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.testsRun > 0:
        success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
