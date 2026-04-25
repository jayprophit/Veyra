"""
Comprehensive Test Suite for New Modules
==========================================
Tests for all Phase 5, 6, 7 implementations and integrations.
"""

import pytest
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal

# Import modules to test
from src.backend.app.core.master_orchestrator import MasterOrchestrator, get_orchestrator
from src.backend.app.core.websocket_manager import WebSocketManager, get_websocket_manager
from src.backend.app.ai.earnings_analyzer import EarningsAnalyzer
from src.backend.app.ai.biometric_monitor import BiometricMonitor
from src.backend.app.ai.crisis_detector import CrisisAlphaDetector, CrisisType, SignalStrength
from src.backend.app.ai.pattern_recognition import PatternRecognitionEngine
from src.backend.app.execution.smart_router import SmartOrderRouter, Order, OrderType
from src.backend.app.market_data.level2_orderbook import Level2OrderBook
from src.backend.app.strategies.stat_arb_engine import StatisticalArbitrageEngine, CointegrationTester
from src.backend.app.portfolio.advanced_optimizer import AdvancedPortfolioOptimizer


# ============================================================================
# Master Orchestrator Tests
# ============================================================================

class TestMasterOrchestrator:
    """Test master orchestrator functionality."""
    
    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator fixture."""
        orch = MasterOrchestrator()
        yield orch
        await orch.stop()
    
    @pytest.mark.asyncio
    async def test_module_registration(self, orchestrator):
        """Test module registration."""
        orchestrator.register_module("test_module", "1.0.0", [], {"test": True})
        assert "test_module" in orchestrator.modules
        assert orchestrator.modules["test_module"].version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_event_bus_publish_subscribe(self, orchestrator):
        """Test event bus publish/subscribe."""
        received_events = []
        
        async def handler(event):
            received_events.append(event)
        
        orchestrator.event_bus.subscribe("test.event", handler)
        await orchestrator.event_bus.publish("test.event", {"data": "test"})
        
        await asyncio.sleep(0.1)
        assert len(received_events) == 1
        assert received_events[0]["data"] == "test"
    
    @pytest.mark.asyncio
    async def test_system_status(self, orchestrator):
        """Test system status retrieval."""
        orchestrator.register_module("mod1", "1.0.0")
        orchestrator.register_module("mod2", "1.0.0", ["mod1"])
        
        status = orchestrator.get_system_status()
        assert "modules" in status
        assert len(status["modules"]) == 2


# ============================================================================
# WebSocket Manager Tests
# ============================================================================

class TestWebSocketManager:
    """Test WebSocket manager functionality."""
    
    @pytest.fixture
    async def ws_manager(self):
        """Create WebSocket manager fixture."""
        manager = WebSocketManager()
        await manager.start()
        yield manager
        await manager.stop()
    
    @pytest.mark.asyncio
    async def test_connection_management(self, ws_manager):
        """Test connection registration."""
        messages = []
        
        async def mock_send(msg):
            messages.append(msg)
        
        conn = await ws_manager.connect("test-conn-1", mock_send)
        assert conn.id == "test-conn-1"
        assert "test-conn-1" in ws_manager.connections
    
    @pytest.mark.asyncio
    async def test_subscription_management(self, ws_manager):
        """Test stream subscription."""
        async def mock_send(msg):
            pass
        
        conn = await ws_manager.connect("test-conn-2", mock_send)
        await conn.subscribe("prices")
        
        assert "prices" in conn.subscriptions
        assert conn.is_subscribed("prices")
    
    @pytest.mark.asyncio
    async def test_broadcast(self, ws_manager):
        """Test message broadcasting."""
        received = []
        
        async def mock_send(msg):
            received.append(msg)
        
        conn = await ws_manager.connect("test-conn-3", mock_send)
        await conn.subscribe("prices")
        ws_manager.stream_handlers["prices"].append(conn)
        
        await ws_manager.broadcast("prices", {"symbol": "AAPL", "price": 150.0})
        
        await asyncio.sleep(0.1)
        assert len(received) == 1
        assert "AAPL" in received[0]


# ============================================================================
# AI Module Tests
# ============================================================================

class TestEarningsAnalyzer:
    """Test earnings analyzer functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create earnings analyzer fixture."""
        return EarningsAnalyzer(api_key="test-key")
    
    def test_sentiment_analysis(self, analyzer):
        """Test sentiment extraction."""
        transcript = """
        We had an excellent quarter with record revenue growth.
        However, supply chain challenges remain a concern.
        Management is confident about future prospects.
        """
        
        # Since we can't call actual API, test structure
        result = analyzer._extract_sentiment_simple(transcript)
        assert "positive_keywords" in result
        assert "negative_keywords" in result


class TestBiometricMonitor:
    """Test biometric monitor functionality."""
    
    @pytest.fixture
    def monitor(self):
        """Create biometric monitor fixture."""
        return BiometricMonitor()
    
    def test_stress_calculation(self, monitor):
        """Test stress level calculation."""
        # High stress scenario
        data = {
            "heart_rate": 110,
            "hrv": 25,
            "gsr": 8.5,
            "timestamp": datetime.now()
        }
        
        result = monitor.calculate_stress(data)
        assert result.stress_level in ["high", "extreme"]
        assert result.recommendation == "STOP_TRADING"
    
    def test_position_sizing(self, monitor):
        """Test position sizing adjustment."""
        monitor.stress_history = [0.8, 0.7, 0.75]  # High stress
        
        base_size = 1000
        adjusted = monitor.get_position_size_adjustment(base_size)
        assert adjusted < base_size


class TestCrisisDetector:
    """Test crisis alpha detector."""
    
    @pytest.fixture
    def detector(self):
        """Create crisis detector fixture."""
        return CrisisAlphaDetector()
    
    def test_vix_spike_detection(self, detector):
        """Test VIX spike detection."""
        signal = detector.analyze_vix(spot=35.0, term_1m=38.0, term_3m=32.0)
        
        assert signal is not None
        assert signal.crisis_type == CrisisType.VIX_SPIKE
        assert signal.strength in [SignalStrength.STRONG, SignalStrength.EXTREME]
        assert signal.confidence > 0.7
    
    def test_credit_spread_detection(self, detector):
        """Test credit spread stress detection."""
        signal = detector.analyze_credit_spreads(hy_spread=550)
        
        assert signal is not None
        assert signal.crisis_type == CrisisType.CREDIT_STRESS
        assert "500bps" in signal.contrarian_opportunity


class TestPatternRecognition:
    """Test pattern recognition engine."""
    
    @pytest.fixture
    def engine(self):
        """Create pattern engine fixture."""
        return PatternRecognitionEngine()
    
    def test_pattern_detection(self, engine):
        """Test pattern detection on sample data."""
        # Create sample price data with double top pattern
        dates = pd.date_range("2026-01-01", periods=60, freq="D")
        prices = [100] * 20 + [105] * 10 + [95] * 10 + [105] * 10 + [90] * 10
        
        df = pd.DataFrame({
            "open": prices,
            "high": [p + 1 for p in prices],
            "low": [p - 1 for p in prices],
            "close": prices,
            "volume": [1000000] * 60
        }, index=dates)
        
        patterns = engine.find_patterns(df)
        
        # Should detect some patterns
        assert isinstance(patterns, list)


# ============================================================================
# Execution Tests
# ============================================================================

class TestSmartOrderRouter:
    """Test smart order router."""
    
    @pytest.fixture
    def router(self):
        """Create router fixture."""
        return SmartOrderRouter()
    
    def test_order_routing_small(self, router):
        """Test routing for small order."""
        order = Order(symbol="AAPL", side="buy", quantity=100, order_type=OrderType.LIMIT, limit_price=150.0)
        
        decision = router.route_order(order)
        
        assert len(decision.venues) == 1  # Single venue for small orders
        assert decision.expected_cost > 0
    
    def test_order_routing_large(self, router):
        """Test routing for large order."""
        order = Order(symbol="AAPL", side="buy", quantity=10000, order_type=OrderType.LIMIT, limit_price=150.0)
        
        decision = router.route_order(order)
        
        assert len(decision.venues) >= 2  # Multiple venues for large orders
        assert "algorithmic" in decision.reasoning.lower() or "TWAP" in decision.reasoning
    
    def test_market_impact_calculation(self, router):
        """Test market impact estimation."""
        order = Order(symbol="AAPL", side="buy", quantity=5000, order_type=OrderType.MARKET)
        
        impact = router.calculate_market_impact(order)
        
        assert "impact_bps" in impact
        assert "recommendation" in impact


class TestLevel2OrderBook:
    """Test Level 2 order book."""
    
    @pytest.fixture
    def orderbook(self):
        """Create order book fixture."""
        return Level2OrderBook("AAPL", depth=5)
    
    def test_book_updates(self, orderbook):
        """Test bid/ask updates."""
        orderbook.update_bid(150.0, 1000, 5)
        orderbook.update_ask(150.05, 500, 3)
        
        book = orderbook.get_book()
        assert len(book.bids) == 1
        assert len(book.asks) == 1
        assert book.best_bid.price == 150.0
        assert book.best_ask.price == 150.05
    
    def test_vwap_calculation(self, orderbook):
        """Test VWAP calculation."""
        # Populate book
        for i in range(5):
            orderbook.update_bid(150.0 - i * 0.01, 1000 - i * 100, 5)
            orderbook.update_ask(150.05 + i * 0.01, 1000 - i * 100, 5)
        
        vwap_info = orderbook.calculate_vwap(2000)
        
        assert "vwap" in vwap_info
        assert "levels_consumed" in vwap_info


# ============================================================================
# Strategy Tests
# ============================================================================

class TestStatisticalArbitrage:
    """Test statistical arbitrage engine."""
    
    @pytest.fixture
    def engine(self):
        """Create stat arb engine fixture."""
        return StatisticalArbitrageEngine()
    
    def test_cointegration_detection(self, engine):
        """Test cointegration detection."""
        # Create cointegrated series
        dates = pd.date_range("2026-01-01", periods=100, freq="D")
        base = np.cumsum(np.random.randn(100) * 0.01)
        
        for i, date in enumerate(dates):
            engine.add_price_data("STOCK_A", 100 + base[i] + np.random.randn() * 0.5, date)
            engine.add_price_data("STOCK_B", 50 + 0.5 * base[i] + np.random.randn() * 0.3, date)
        
        pairs = engine.find_cointegrated_pairs(["STOCK_A", "STOCK_B"])
        
        assert len(pairs) > 0
    
    def test_z_score_calculation(self, engine):
        """Test z-score calculation."""
        dates = pd.date_range("2026-01-01", periods=50, freq="D")
        
        for i, date in enumerate(dates):
            engine.add_price_data("A", 100 + i * 0.1, date)
            engine.add_price_data("B", 50 + i * 0.05, date)
        
        engine.active_pairs["A_B"] = {"symbol_a": "A", "symbol_b": "B"}
        
        result = engine.calculate_z_score("A", "B")
        
        if result:
            z_score, hedge = result
            assert isinstance(z_score, float)
            assert isinstance(hedge, float)


# ============================================================================
# Portfolio Tests
# ============================================================================

class TestAdvancedPortfolioOptimizer:
    """Test portfolio optimizer."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer fixture."""
        return AdvancedPortfolioOptimizer()
    
    @pytest.fixture
    def sample_returns(self):
        """Create sample returns data."""
        np.random.seed(42)
        data = {}
        for i in range(5):
            data[f"ASSET_{i}"] = np.random.randn(252) * 0.02 + 0.0005
        return pd.DataFrame(data)
    
    def test_mean_variance_optimization(self, optimizer, sample_returns):
        """Test mean-variance optimization."""
        result = optimizer.optimize(sample_returns, method="mean_variance")
        
        assert len(result.weights) == 5
        assert abs(sum(result.weights.values()) - 1.0) < 0.01  # Sum to 1
        assert result.expected_return > 0
        assert result.sharpe_ratio is not None
    
    def test_risk_parity_optimization(self, optimizer, sample_returns):
        """Test risk parity optimization."""
        result = optimizer.optimize(sample_returns, method="risk_parity")
        
        assert len(result.weights) == 5
        assert result.method == "risk_parity"
    
    def test_compare_methods(self, optimizer, sample_returns):
        """Test method comparison."""
        results = optimizer.compare_methods(sample_returns)
        
        assert "mean_variance" in results or "risk_parity" in results


# ============================================================================
# Integration Tests
# ============================================================================

class TestSystemIntegration:
    """Test system-wide integration."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow."""
        # Initialize orchestrator
        orch = get_orchestrator()
        
        # Register modules
        orch.register_module("market_data", "1.0.0")
        orch.register_module("execution", "1.0.0", ["market_data"])
        orch.register_module("portfolio", "1.0.0", ["market_data"])
        
        # Start system
        await orch.start()
        
        # Verify status
        status = orch.get_system_status()
        assert status["running"] == True
        assert len(status["modules"]) == 3
        
        # Clean up
        await orch.stop()
    
    @pytest.mark.asyncio
    async def test_event_flow(self):
        """Test event flow between modules."""
        orch = get_orchestrator()
        
        events_received = []
        
        async def test_handler(event):
            events_received.append(event)
        
        orch.event_bus.subscribe("test.integration", test_handler)
        
        await orch.event_bus.publish("test.integration", {"test": True})
        
        await asyncio.sleep(0.1)
        
        assert len(events_received) == 1
        assert events_received[0]["test"] == True


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
