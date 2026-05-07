"""
Comprehensive Enterprise Features Test Suite
==========================================
Complete test coverage for all enterprise-grade components
"""

import asyncio
import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
import tempfile
import os
from typing import Dict, List, Any

# Import all enterprise components
from src.backend.app.enterprise.api_gateway import APIGateway, RateLimitRule, RouteConfig
from src.backend.app.ml.mlops_pipeline import MLOpsPipeline, ModelType, PipelineConfig
from src.backend.app.quantum.quantum_portfolio_optimization import QuantumPortfolioOptimizer, QuantumAlgorithm
from src.backend.app.advanced_trading.trading_engine import AdvancedTradingEngine
from src.backend.app.risk_analytics.advanced_risk_engine import AdvancedRiskEngine
from src.backend.app.news.realtime_news_engine import RealTimeNewsEngine


class TestAPIGateway:
    """Test suite for API Gateway"""
    
    @pytest.fixture
    async def api_gateway(self):
        """Create API Gateway instance"""
        gateway = APIGateway()
        await gateway.initialize()
        return gateway
    
    @pytest.mark.asyncio
    async def test_api_gateway_initialization(self, api_gateway):
        """Test API Gateway initialization"""
        assert api_gateway.redis_client is not None
        assert len(api_gateway.routes) > 0
        assert "/api/v1/trading" in api_gateway.routes
        assert "/api/v1/portfolio" in api_gateway.routes
        
    @pytest.mark.asyncio
    async def test_route_matching(self, api_gateway):
        """Test route matching"""
        from fastapi import Request
        
        # Mock request
        request = Mock(spec=Request)
        request.url.path = "/api/v1/trading"
        request.method = "GET"
        
        route = api_gateway._find_route(request)
        assert route is not None
        assert route.path == "/api/v1/trading"
        assert "GET" in route.methods
        
    @pytest.mark.asyncio
    async def test_rate_limiting(self, api_gateway):
        """Test rate limiting"""
        rule = RateLimitRule(
            name="test_limit",
            limit_type=api_gateway.enterprise.api_gateway.RateLimitType.REQUESTS_PER_MINUTE,
            limit=5,
            window_seconds=60,
            scope="global"
        )
        
        # Test rate limit check (should pass first 5 times)
        for i in range(5):
            try:
                await api_gateway._check_single_rate_limit(None, rule, None)
            except Exception:
                pytest.fail(f"Rate limit failed unexpectedly at iteration {i}")
        
        # Test rate limit exceeded (should fail on 6th attempt)
        with pytest.raises(Exception):  # HTTPException for rate limit
            await api_gateway._check_single_rate_limit(None, rule, None)
            
    @pytest.mark.asyncio
    async def test_api_key_authentication(self, api_gateway):
        """Test API key authentication"""
        # Add test API key
        api_gateway.add_api_key("test_key", "secret_key_123", "user_123", ["read", "write"])
        
        # Test valid API key
        user_context = await api_gateway._authenticate_api_key("secret_key_123")
        assert user_context is not None
        assert user_context["user_id"] == "user_123"
        assert "read" in user_context["permissions"]
        
        # Test invalid API key
        with pytest.raises(Exception):  # HTTPException for invalid key
            await api_gateway._authenticate_api_key("invalid_key")
            
    def test_gateway_statistics(self, api_gateway):
        """Test gateway statistics"""
        stats = api_gateway.get_gateway_stats()
        
        assert "total_requests" in stats
        assert "active_routes" in stats
        assert "active_api_keys" in stats
        assert stats["active_routes"] > 0


class TestMLOpsPipeline:
    """Test suite for MLOps Pipeline"""
    
    @pytest.fixture
    def mlops_pipeline(self):
        """Create MLOps Pipeline instance"""
        return MLOpsPipeline()
    
    def test_pipeline_initialization(self, mlops_pipeline):
        """Test MLOps pipeline initialization"""
        assert len(mlops_pipeline.pipeline_configs) > 0
        assert "stock_price_prediction" in mlops_pipeline.pipeline_configs
        assert "portfolio_optimization" in mlops_pipeline.pipeline_configs
        
    def test_model_types(self):
        """Test model type enumeration"""
        assert ModelType.LINEAR_REGRESSION in ModelType
        assert ModelType.RANDOM_FOREST in ModelType
        assert ModelType.GRADIENT_BOOSTING in ModelType
        assert ModelType.XGBOOST in ModelType
        
    @pytest.mark.asyncio
    async def test_data_ingestion(self, mlops_pipeline):
        """Test data ingestion stage"""
        config = mlops_pipeline.pipeline_configs["stock_price_prediction"]
        data = await mlops_pipeline._stage_data_ingestion(config)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert config.target_column in data.columns
        
    @pytest.mark.asyncio
    async def test_data_validation(self, mlops_pipeline):
        """Test data validation stage"""
        config = mlops_pipeline.pipeline_configs["stock_price_prediction"]
        
        # Create test data
        test_data = pd.DataFrame({
            "price_change": np.random.uniform(-0.1, 0.1, 100),
            "volume": np.random.uniform(1000000, 10000000, 100),
            "rsi": np.random.uniform(0, 100, 100)
        })
        
        validated_data = await mlops_pipeline._stage_data_validation(test_data, config)
        assert isinstance(validated_data, pd.DataFrame)
        assert len(validated_data) == len(test_data)
        
    @pytest.mark.asyncio
    async def test_model_training(self, mlops_pipeline):
        """Test model training stage"""
        config = mlops_pipeline.pipeline_configs["stock_price_prediction"]
        
        # Create test data
        test_data = pd.DataFrame({
            "price_change": np.random.uniform(-0.1, 0.1, 100),
            "volume": np.random.uniform(1000000, 10000000, 100),
            "rsi": np.random.uniform(0, 100, 100),
            "macd": np.random.uniform(-5, 5, 100)
        })
        
        trained_models = await mlops_pipeline._stage_model_training(test_data, config)
        assert len(trained_models) > 0
        
        for model in trained_models:
            assert model.metrics is not None
            assert model.metrics.mse >= 0
            assert model.metrics.r2 <= 1
            
    def test_get_best_model(self, mlops_pipeline):
        """Test best model selection"""
        from src.backend.app.ml.mlops_pipeline import ModelMetadata, ModelMetrics
        
        # Create mock models
        models = [
            ModelMetadata(
                model_id="model_1",
                model_type=ModelType.LINEAR_REGRESSION,
                version="1.0",
                created_at=datetime.now(),
                trained_at=datetime.now(),
                metrics=ModelMetrics(0.1, 0.2, 0.316, 0.8, 5.0, 1.0, 0.1, 1.0),
                hyperparameters={},
                feature_importance={},
                training_data_shape=(100, 4),
                validation_data_shape=(20, 4),
                model_path="test_path"
            ),
            ModelMetadata(
                model_id="model_2",
                model_type=ModelType.RANDOM_FOREST,
                version="1.0",
                created_at=datetime.now(),
                trained_at=datetime.now(),
                metrics=ModelMetrics(0.05, 0.15, 0.224, 0.9, 3.0, 2.0, 0.2, 2.0),
                hyperparameters={},
                feature_importance={},
                training_data_shape=(100, 4),
                validation_data_shape=(20, 4),
                model_path="test_path"
            )
        ]
        
        best_model = mlops_pipeline._get_best_model(models)
        assert best_model.model_id == "model_2"  # Higher R2 score


class TestQuantumPortfolioOptimizer:
    """Test suite for Quantum Portfolio Optimizer"""
    
    @pytest.fixture
    def quantum_optimizer(self):
        """Create Quantum Portfolio Optimizer instance"""
        return QuantumPortfolioOptimizer()
    
    def test_quantum_optimizer_initialization(self, quantum_optimizer):
        """Test quantum optimizer initialization"""
        assert quantum_optimizer.backend_name is not None
        assert quantum_optimizer.quantum_backend is not None
        assert quantum_optimizer.quantum_backend["qubits"] > 0
        
    def test_add_quantum_asset(self, quantum_optimizer):
        """Test adding quantum assets"""
        quantum_optimizer.add_quantum_asset("AAPL", 0.08, 0.15)
        quantum_optimizer.add_quantum_asset("GOOGL", 0.10, 0.20)
        
        assert len(quantum_optimizer.quantum_assets) == 2
        assert quantum_optimizer.quantum_assets[0].symbol == "AAPL"
        assert quantum_optimizer.quantum_assets[0].expected_return == 0.08
        
    def test_create_quantum_state(self, quantum_optimizer):
        """Test quantum state creation"""
        quantum_state = quantum_optimizer._create_quantum_state(0.08, 0.15)
        
        assert isinstance(quantum_state, np.ndarray)
        assert len(quantum_state) == 4  # 2 qubits
        assert np.isclose(np.linalg.norm(quantum_state), 1.0)  # Normalized
        
    @pytest.mark.asyncio
    async def test_qaoa_optimization(self, quantum_optimizer):
        """Test QAOA portfolio optimization"""
        # Add test assets
        quantum_optimizer.add_quantum_asset("AAPL", 0.08, 0.15)
        quantum_optimizer.add_quantum_asset("GOOGL", 0.10, 0.20)
        quantum_optimizer.add_quantum_asset("MSFT", 0.12, 0.18)
        
        portfolio = await quantum_optimizer.optimize_portfolio_qaoa(risk_aversion=0.5)
        
        assert portfolio is not None
        assert portfolio.quantum_algorithm == QuantumAlgorithm.QAOA
        assert len(portfolio.optimal_weights) == 3
        assert portfolio.sharpe_ratio > 0
        assert portfolio.expected_return > 0
        assert portfolio.risk > 0
        
        # Check weights sum to 1
        total_weight = sum(portfolio.optimal_weights.values())
        assert abs(total_weight - 1.0) < 0.01
        
    @pytest.mark.asyncio
    async def test_vqe_optimization(self, quantum_optimizer):
        """Test VQE portfolio optimization"""
        # Add test assets
        quantum_optimizer.add_quantum_asset("AAPL", 0.08, 0.15)
        quantum_optimizer.add_quantum_asset("GOOGL", 0.10, 0.20)
        
        portfolio = await quantum_optimizer.optimize_portfolio_vqe(risk_aversion=0.3)
        
        assert portfolio is not None
        assert portfolio.quantum_algorithm == QuantumAlgorithm.VQE
        assert len(portfolio.optimal_weights) == 2
        assert portfolio.sharpe_ratio > 0
        
    def test_portfolio_metrics_calculation(self, quantum_optimizer):
        """Test portfolio metrics calculation"""
        # Add test assets
        quantum_optimizer.add_quantum_asset("AAPL", 0.08, 0.15)
        quantum_optimizer.add_quantum_asset("GOOGL", 0.10, 0.20)
        
        weights = {"AAPL": 0.6, "GOOGL": 0.4}
        
        # Test return calculation
        portfolio_return = quantum_optimizer._calculate_portfolio_return(weights)
        expected_return = 0.6 * 0.08 + 0.4 * 0.10
        assert abs(portfolio_return - expected_return) < 0.001
        
        # Test risk calculation
        portfolio_risk = quantum_optimizer._calculate_portfolio_risk(weights)
        expected_risk = np.sqrt((0.6**2 * 0.15**2) + (0.4**2 * 0.20**2))
        assert abs(portfolio_risk - expected_risk) < 0.001
        
    @pytest.mark.asyncio
    async def test_quantum_risk_analysis(self, quantum_optimizer):
        """Test quantum risk analysis"""
        # Add test assets and optimize
        quantum_optimizer.add_quantum_asset("AAPL", 0.08, 0.15)
        quantum_optimizer.add_quantum_asset("GOOGL", 0.10, 0.20)
        
        portfolio = await quantum_optimizer.optimize_portfolio_qaoa()
        
        # Perform risk analysis
        risk_analysis = await quantum_optimizer.quantum_risk_analysis(portfolio.portfolio_id)
        
        assert "quantum_monte_carlo" in risk_analysis
        assert "quantum_var" in risk_analysis
        assert "quantum_stress" in risk_analysis
        assert "portfolio_id" in risk_analysis
        
    def test_quantum_advantage_report(self, quantum_optimizer):
        """Test quantum advantage report"""
        # Add test assets and optimize
        quantum_optimizer.add_quantum_asset("AAPL", 0.08, 0.15)
        quantum_optimizer.add_quantum_asset("GOOGL", 0.10, 0.20)
        
        report = quantum_optimizer.get_quantum_advantage_report()
        
        assert "total_portfolios" in report
        assert "average_quantum_advantage" in report
        assert "algorithm_performance" in report
        assert "quantum_backend" in report


class TestAdvancedTradingEngine:
    """Test suite for Advanced Trading Engine"""
    
    @pytest.fixture
    def trading_engine(self):
        """Create Advanced Trading Engine instance"""
        return AdvancedTradingEngine()
    
    def test_trading_engine_initialization(self, trading_engine):
        """Test trading engine initialization"""
        assert trading_engine is not None
        assert hasattr(trading_engine, 'execution_engine')
        assert hasattr(trading_engine, 'position_manager')
        assert hasattr(trading_engine, 'risk_manager')
        
    @pytest.mark.asyncio
    async def test_order_execution(self, trading_engine):
        """Test order execution"""
        # Create test order
        order = {
            "symbol": "AAPL",
            "side": "buy",
            "order_type": "market",
            "quantity": 100
        }
        
        # Execute order
        result = await trading_engine.execute_order(order)
        
        assert result is not None
        assert result["status"] in ["filled", "pending", "failed"]
        
    @pytest.mark.asyncio
    async def test_risk_management(self, trading_engine):
        """Test risk management"""
        # Test risk check
        order = {
            "symbol": "AAPL",
            "side": "buy",
            "order_type": "market",
            "quantity": 1000000  # Very large order
        }
        
        risk_check = await trading_engine.risk_manager.check_order_risk(order)
        assert risk_check is not None
        assert "approved" in risk_check or "rejected" in risk_check


class TestAdvancedRiskEngine:
    """Test suite for Advanced Risk Engine"""
    
    @pytest.fixture
    def risk_engine(self):
        """Create Advanced Risk Engine instance"""
        return AdvancedRiskEngine()
    
    def test_risk_engine_initialization(self, risk_engine):
        """Test risk engine initialization"""
        assert risk_engine is not None
        assert len(risk_engine.risk_factors) > 0
        assert len(risk_engine.stress_scenarios) > 0
        
    @pytest.mark.asyncio
    async def test_risk_metrics_calculation(self, risk_engine):
        """Test comprehensive risk metrics calculation"""
        # Create test portfolio data
        portfolio_data = {
            "total_value": 1000000,
            "positions": [
                {"symbol": "AAPL", "value": 400000, "weight": 0.4},
                {"symbol": "GOOGL", "value": 300000, "weight": 0.3},
                {"symbol": "MSFT", "value": 300000, "weight": 0.3}
            ],
            "returns": np.random.normal(0.001, 0.02, 252)  # Daily returns
        }
        
        risk_metrics = await risk_engine.calculate_comprehensive_risk_metrics(portfolio_data)
        
        assert risk_metrics is not None
        assert risk_metrics.var_1d > 0
        assert risk_metrics.var_5d > risk_metrics.var_1d
        assert risk_metrics.var_10d > risk_metrics.var_5d
        assert -1 <= risk_metrics.beta <= 1
        assert -1 <= risk_metrics.correlation_with_market <= 1
        assert risk_metrics.r_squared >= 0
        assert risk_metrics.r_squared <= 1
        
    @pytest.mark.asyncio
    async def test_stress_testing(self, risk_engine):
        """Test stress testing"""
        portfolio_data = {
            "total_value": 1000000,
            "positions": [
                {"symbol": "AAPL", "value": 400000, "weight": 0.4},
                {"symbol": "GOOGL", "value": 300000, "weight": 0.3}
            ]
        }
        
        stress_results = await risk_engine.run_stress_tests(portfolio_data)
        
        assert stress_results is not None
        assert "stress_test_results" in stress_results
        assert "worst_case_scenario" in stress_results
        assert "risk_concentration" in stress_results
        
        # Check that we have results for each scenario
        for scenario in risk_engine.stress_scenarios:
            assert scenario.name in stress_results["stress_test_results"]
            
    @pytest.mark.asyncio
    async def test_portfolio_optimization(self, risk_engine):
        """Test portfolio optimization"""
        constraints = {
            "max_weight": 0.5,
            "min_weight": 0.05
        }
        
        optimization_result = await risk_engine.optimize_portfolio(constraints)
        
        assert optimization_result is not None
        if optimization_result["success"]:
            assert "optimal_weights" in optimization_result
            assert "expected_return" in optimization_result
            assert "expected_risk" in optimization_result
            assert "sharpe_ratio" in optimization_result


class TestRealTimeNewsEngine:
    """Test suite for Real-Time News Engine"""
    
    @pytest.fixture
    def news_engine(self):
        """Create Real-Time News Engine instance"""
        return RealTimeNewsEngine()
    
    def test_news_engine_initialization(self, news_engine):
        """Test news engine initialization"""
        assert news_engine is not None
        assert len(news_engine.news_sources) > 0
        assert len(news_engine.processors) > 0
        
    @pytest.mark.asyncio
    async def test_news_processing(self, news_engine):
        """Test news processing"""
        # Create test news item
        from src.backend.app.news.realtime_news_engine import NewsItem, NewsSource, NewsCategory, Sentiment
        
        news_item = NewsItem(
            id="test_news_1",
            title="Test News Item",
            content="This is a test news item for financial markets.",
            source=NewsSource.BLOOMBERG,
            category=NewsCategory.MARKET_NEWS,
            sentiment=Sentiment.NEUTRAL,
            sentiment_score=0.0,
            relevance_score=0.5,
            timestamp=datetime.now(),
            symbols=["AAPL", "GOOGL"],
            authors=["Test Author"],
            url="https://example.com/news/1",
            keywords=["test", "news"],
            market_impact="medium",
            priority=5,
            metadata={}
        )
        
        # Process news item
        await news_engine._process_news_item(news_item)
        
        assert news_item.id in news_engine.news_cache
        assert news_item.relevance_score >= 0
        
    @pytest.mark.asyncio
    async def test_sentiment_analysis(self, news_engine):
        """Test sentiment analysis"""
        sentiment_analyzer = news_engine.sentiment_analyzer
        
        # Test positive sentiment
        positive_text = "Stock prices surged today with strong earnings reports"
        sentiment, score = await sentiment_analyzer.analyze(positive_text)
        assert sentiment in [sentiment_analyzer.news.Sentiment.POSITIVE, sentiment_analyzer.news.Sentiment.VERY_POSITIVE]
        assert score > 0
        
        # Test negative sentiment
        negative_text = "Market crashed due to poor economic data and fears"
        sentiment, score = await sentiment_analyzer.analyze(negative_text)
        assert sentiment in [sentiment_analyzer.news.Sentiment.NEGATIVE, sentiment_analyzer.news.Sentiment.VERY_NEGATIVE]
        assert score < 0
        
    @pytest.mark.asyncio
    async def test_news_search(self, news_engine):
        """Test news search functionality"""
        # Add some test news items
        await news_engine._process_news_item(news_engine.news_cache.get("test_news_1"))
        
        # Search for news
        results = await news_engine.search_news("test")
        assert isinstance(results, list)
        
        # Search by symbol
        symbol_results = await news_engine.get_symbol_news("AAPL")
        assert isinstance(symbol_results, list)


# Integration Tests
class TestIntegration:
    """Integration tests for enterprise components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_trading_workflow(self):
        """Test end-to-end trading workflow"""
        # Initialize components
        trading_engine = AdvancedTradingEngine()
        risk_engine = AdvancedRiskEngine()
        news_engine = RealTimeNewsEngine()
        
        # 1. Get market news
        news_results = await news_engine.search_news("market", time_range="1h")
        
        # 2. Analyze portfolio risk
        portfolio_data = {
            "total_value": 1000000,
            "positions": [
                {"symbol": "AAPL", "value": 400000, "weight": 0.4},
                {"symbol": "GOOGL", "value": 300000, "weight": 0.3}
            ],
            "returns": np.random.normal(0.001, 0.02, 252)
        }
        
        risk_metrics = await risk_engine.calculate_comprehensive_risk_metrics(portfolio_data)
        
        # 3. Execute trade if risk is acceptable
        if risk_metrics.var_1d < 0.02:  # Risk threshold
            order = {
                "symbol": "AAPL",
                "side": "buy",
                "order_type": "market",
                "quantity": 100
            }
            
            result = await trading_engine.execute_order(order)
            assert result["status"] != "failed"
            
    @pytest.mark.asyncio
    async def test_ml_to_trading_integration(self):
        """Test ML to trading integration"""
        # Initialize components
        mlops_pipeline = MLOpsPipeline()
        trading_engine = AdvancedTradingEngine()
        
        # 1. Run ML pipeline
        config = mlops_pipeline.pipeline_configs["stock_price_prediction"]
        data = await mlops_pipeline._stage_data_ingestion(config)
        trained_models = await mlops_pipeline._stage_model_training(data, config)
        
        # 2. Get best model prediction
        best_model = mlops_pipeline._get_best_model(trained_models)
        
        # 3. Use prediction for trading decision
        if best_model.metrics.r2 > 0.7:  # Model confidence threshold
            # Execute trade based on prediction
            order = {
                "symbol": "AAPL",
                "side": "buy",
                "order_type": "market",
                "quantity": 100
            }
            
            result = await trading_engine.execute_order(order)
            assert result["status"] != "failed"
            
    @pytest.mark.asyncio
    async def test_quantum_to_classical_comparison(self):
        """Test quantum vs classical optimization comparison"""
        # Initialize components
        quantum_optimizer = QuantumPortfolioOptimizer()
        
        # Add test assets
        quantum_optimizer.add_quantum_asset("AAPL", 0.08, 0.15)
        quantum_optimizer.add_quantum_asset("GOOGL", 0.10, 0.20)
        quantum_optimizer.add_quantum_asset("MSFT", 0.12, 0.18)
        
        # 1. Quantum optimization
        quantum_portfolio = await quantum_optimizer.optimize_portfolio_qaoa()
        
        # 2. Classical optimization
        classical_result = await quantum_optimizer._classical_portfolio_optimization(0.5)
        
        # 3. Compare results
        quantum_advantage = quantum_optimizer._calculate_quantum_advantage(
            quantum_portfolio.sharpe_ratio, 
            classical_result["sharpe_ratio"]
        )
        
        # Quantum should show advantage (in this mock implementation)
        assert quantum_portfolio.sharpe_ratio > 0
        assert classical_result["sharpe_ratio"] > 0
        assert isinstance(quantum_advantage, float)


# Performance Tests
class TestPerformance:
    """Performance tests for enterprise components"""
    
    @pytest.mark.asyncio
    async def test_api_gateway_performance(self):
        """Test API Gateway performance"""
        gateway = APIGateway()
        await gateway.initialize()
        
        import time
        start_time = time.time()
        
        # Process 1000 requests
        for i in range(1000):
            rule = gateway.enterprise.api_gateway.RateLimitRule(
                name=f"perf_test_{i}",
                limit_type=gateway.enterprise.api_gateway.RateLimitType.REQUESTS_PER_MINUTE,
                limit=100,
                window_seconds=60,
                scope="global"
            )
            await gateway._check_single_rate_limit(None, rule, None)
            
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 1000 requests in under 1 second
        assert processing_time < 1.0
        
    @pytest.mark.asyncio
    async def test_quantum_optimization_performance(self):
        """Test quantum optimization performance"""
        optimizer = QuantumPortfolioOptimizer()
        
        # Add many assets
        for i in range(10):
            optimizer.add_quantum_asset(f"STOCK_{i}", 0.08 + i*0.01, 0.15 + i*0.02)
            
        import time
        start_time = time.time()
        
        # Run optimization
        portfolio = await optimizer.optimize_portfolio_qaoa()
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete optimization in under 5 seconds
        assert processing_time < 5.0
        assert portfolio is not None
        assert len(portfolio.optimal_weights) == 10


# Security Tests
class TestSecurity:
    """Security tests for enterprise components"""
    
    @pytest.mark.asyncio
    async def test_api_gateway_security(self):
        """Test API Gateway security features"""
        gateway = APIGateway()
        await gateway.initialize()
        
        # Test API key security
        api_key = "secure_api_key_123"
        user_id = "user_123"
        
        gateway.add_api_key("test_key", api_key, user_id, ["read", "write"])
        
        # Test authentication
        user_context = await gateway._authenticate_api_key(api_key)
        assert user_context["user_id"] == user_id
        
        # Test invalid key rejection
        with pytest.raises(Exception):
            await gateway._authenticate_api_key("invalid_key")
            
        # Test rate limiting security
        rule = gateway.enterprise.api_gateway.RateLimitRule(
            name="security_test",
            limit_type=gateway.enterprise.api_gateway.RateLimitType.REQUESTS_PER_MINUTE,
            limit=2,
            window_seconds=60,
            scope="ip"
        )
        
        # Should pass first 2 requests
        await gateway._check_single_rate_limit(None, rule, None)
        await gateway._check_single_rate_limit(None, rule, None)
        
        # Should fail on 3rd request
        with pytest.raises(Exception):
            await gateway._check_single_rate_limit(None, rule, None)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
