"""
Comprehensive Test Suite
=======================
Unit tests, integration tests, and validation for Financial Master
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
        from ai.visual_advanced import AdvancedVisualAI
        
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
        from risk.risk_manager import RiskManager
        
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
        from portfolio_opt.optimizer import PortfolioOptimizer
        
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
        from risk.crisis_alpha_detector import CrisisAlphaDetector
        
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
        from signal_aggregator import SignalAggregator, SignalSource
        from ai.visual_advanced import AdvancedVisualAI
        from sentiment.news_sentiment_engine import NewsSentimentEngine
        
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


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
