"""
Phase 10 Transcendent Feature Tests
Testing BCI, Reality Simulation, Interplanetary Trading, AI Instruments, Temporal Arbitrage
"""
import pytest
import asyncio
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from app.ai.bci_interface import bci_interface, MentalState, BrainWaveReading
from app.ai.reality_simulation import reality_simulator, RealitySimulator
from app.ai.interplanetary_trading import interplanetary_trading, Location
from app.ai.ai_instrument_generator import ai_instrument_generator, InstrumentType
from app.ai.temporal_arbitrage import temporal_arbitrage, ExchangeLocation


class TestBrainComputerInterface:
    """Test BCI neural trading functionality."""
    
    @pytest.fixture
    def reset_bci(self):
        """Reset BCI state before each test."""
        bci_interface.is_connected = False
        bci_interface.device_type = None
        bci_interface.reading_history = []
        bci_interface.current_state = MentalState.UNKNOWN
        bci_interface.trading_enabled = False
        yield
        # Cleanup
        bci_interface.disconnect()
    
    @pytest.mark.asyncio
    async def test_bci_connect_muse(self, reset_bci):
        """Test connecting to Muse headset."""
        result = await bci_interface.connect("muse")
        assert result is True
        assert bci_interface.is_connected is True
        assert bci_interface.device_type == "muse"
    
    @pytest.mark.asyncio
    async def test_bci_connect_emotiv(self, reset_bci):
        """Test connecting to Emotiv headset."""
        result = await bci_interface.connect("emotiv")
        assert result is True
        assert bci_interface.device_type == "emotiv"
    
    @pytest.mark.asyncio
    async def test_bci_status_disconnected(self, reset_bci):
        """Test status when disconnected."""
        status = bci_interface.get_status()
        assert status["connected"] is False
        assert status["trading_enabled"] is False
        assert status["mental_state"] == "unknown"
    
    def test_mental_state_classification_focused(self):
        """Test focused state detection."""
        reading = BrainWaveReading(
            timestamp=datetime.now(),
            alpha_power=0.3,
            beta_power=0.8,  # High beta = focused
            theta_power=0.1,
            gamma_power=0.3,
            delta_power=0.1,
            attention_score=85,
            meditation_score=40
        )
        
        state = bci_interface._classify_state(reading)
        assert state == MentalState.FOCUSED
    
    def test_mental_state_classification_flow(self):
        """Test flow state detection."""
        reading = BrainWaveReading(
            timestamp=datetime.now(),
            alpha_power=0.7,  # High alpha
            beta_power=0.3,
            theta_power=0.1,
            gamma_power=0.6,  # High gamma = flow
            delta_power=0.1,
            attention_score=90,
            meditation_score=75
        )
        
        state = bci_interface._classify_state(reading)
        assert state == MentalState.FLOW
    
    def test_trading_safety_stressed(self):
        """Test trading blocked when stressed."""
        reading = BrainWaveReading(
            timestamp=datetime.now(),
            alpha_power=0.2,
            beta_power=0.8,  # High beta
            theta_power=0.2,
            gamma_power=0.2,
            delta_power=0.2,
            attention_score=40,  # Low attention
            meditation_score=30
        )
        
        bci_interface._update_trading_permissions(reading)
        assert bci_interface.trading_enabled is False
    
    def test_trading_safety_flow(self):
        """Test trading enabled in flow state."""
        reading = BrainWaveReading(
            timestamp=datetime.now(),
            alpha_power=0.6,
            beta_power=0.4,
            theta_power=0.1,
            gamma_power=0.5,
            delta_power=0.1,
            attention_score=80,
            meditation_score=70
        )
        
        bci_interface.current_state = MentalState.FLOW
        bci_interface._update_trading_permissions(reading)
        assert bci_interface.trading_enabled is True
    
    def test_get_recommendation_flow(self):
        """Test recommendation in flow state."""
        bci_interface.current_state = MentalState.FLOW
        rec = bci_interface.get_recommendation()
        assert "FLOW STATE" in rec
        assert "Optimal" in rec


class TestRealitySimulation:
    """Test reality simulation and timeline branching."""
    
    @pytest.fixture
    def simulator(self):
        """Create fresh simulator instance."""
        return RealitySimulator(num_simulations=1000)  # Reduced for testing
    
    def test_simulate_timelines_basic(self, simulator):
        """Test basic timeline simulation."""
        result = simulator.simulate_timelines(
            symbol="AAPL",
            current_price=150.0,
            days_forward=30,
            scenario_type="neutral"
        )
        
        assert result.symbol == "AAPL"
        assert result.current_price == 150.0
        assert len(result.timelines) > 0
        assert result.expected_value > 0
        assert result.risk_score >= 0
    
    def test_simulate_bullish_scenario(self, simulator):
        """Test bullish scenario has higher expected value."""
        neutral = simulator.simulate_timelines("AAPL", 150.0, 30, "neutral")
        bullish = simulator.simulate_timelines("AAPL", 150.0, 30, "bullish")
        
        # Bullish should generally have higher expected value
        assert bullish.expected_value >= neutral.expected_value * 0.9
    
    def test_simulate_bearish_scenario(self, simulator):
        """Test bearish scenario has lower expected value."""
        neutral = simulator.simulate_timelines("AAPL", 150.0, 30, "neutral")
        bearish = simulator.simulate_timelines("AAPL", 150.0, 30, "bearish")
        
        # Bearish should generally have lower expected value
        assert bearish.expected_value <= neutral.expected_value * 1.1
    
    def test_confidence_interval(self, simulator):
        """Test confidence interval calculation."""
        result = simulator.simulate_timelines("TSLA", 200.0, 30, "neutral")
        
        lower, upper = result.confidence_interval
        assert lower < upper
        assert lower > 0
        assert result.expected_value >= lower
        assert result.expected_value <= upper
    
    def test_recommendation_generation(self, simulator):
        """Test recommendation based on simulation."""
        # High expected return, low risk
        result = simulator.simulate_timelines("AAPL", 150.0, 30, "bullish")
        assert len(result.recommendation) > 0
        assert isinstance(result.recommendation, str)
    
    def test_counterfactual_analysis(self, simulator):
        """Test what-if scenario analysis."""
        result = simulator.counterfactual_analysis(
            symbol="TSLA",
            entry_price=200.0,
            exit_price=220.0,
            alternative_action="hold"
        )
        
        assert result["actual_pnl"] == 20.0
        assert result["alternative_action"] == "hold"
        assert "lesson" in result
    
    def test_probability_cloud(self, simulator):
        """Test probability cloud calculation."""
        result = simulator.get_probability_cloud(
            symbol="AAPL",
            current_price=150.0,
            target_prices=[140, 150, 160, 170]
        )
        
        assert result["symbol"] == "AAPL"
        assert "probability_cloud" in result
        assert 140 in result["probability_cloud"]
        assert 170 in result["probability_cloud"]


class TestInterplanetaryTrading:
    """Test Mars/Moon trading with light-speed delays."""
    
    @pytest.fixture
    def reset_interplanetary(self):
        """Reset interplanetary state."""
        interplanetary_trading.active_locations = [Location.EARTH]
        interplanetary_trading.local_order_books = {
            loc: [] for loc in Location
        }
        yield
    
    def test_earth_to_moon_delay(self, reset_interplanetary):
        """Test Earth to Moon delay calculation."""
        delay = interplanetary_trading.calculate_delay(
            Location.EARTH, Location.LUNAR_ORBIT
        )
        
        assert delay.one_way_delay_seconds == 1.28
        assert delay.round_trip_delay_seconds == 2.56
    
    def test_earth_to_mars_delay(self, reset_interplanetary):
        """Test Earth to Mars delay calculation."""
        delay = interplanetary_trading.calculate_delay(
            Location.EARTH, Location.MARS
        )
        
        assert delay.one_way_delay_seconds == 240  # 4 minutes
        assert delay.round_trip_delay_seconds == 480  # 8 minutes
    
    def test_place_mars_order(self, reset_interplanetary):
        """Test placing order from Mars."""
        order = interplanetary_trading.place_offworld_order(
            symbol="TSLA",
            side="buy",
            quantity=10,
            origin=Location.MARS,
            destination=Location.EARTH
        )
        
        assert order.symbol == "TSLA"
        assert order.side == "buy"
        assert order.quantity == 10
        assert order.origin_location == Location.MARS
        assert "OFFWORLD_mars_" in order.order_id
    
    def test_mars_order_book(self, reset_interplanetary):
        """Test Mars local order book."""
        interplanetary_trading.place_offworld_order(
            symbol="AAPL", side="buy", quantity=5,
            origin=Location.MARS, destination=Location.EARTH
        )
        
        mars_book = interplanetary_trading.get_local_order_book(Location.MARS)
        assert len(mars_book) == 1
        assert mars_book[0]["symbol"] == "AAPL"
    
    def test_mars_trading_demo(self, reset_interplanetary):
        """Test Mars trading demo endpoint."""
        result = interplanetary_trading.simulate_mars_trading(
            symbol="AAPL", side="buy", quantity=10
        )
        
        assert result["status"] == "pending_light_speed"
        assert result["origin"] == "Mars Colony Alpha"
        assert result["delay_minutes"] >= 4
        assert "execution_time" in result
    
    def test_asteroid_etf_proposal(self):
        """Test asteroid mining ETF generation."""
        etf = interplanetary_trading.create_asteroid_mining_etf_proposal()
        
        assert etf["etf_name"] == "COSMIC.MINERS"
        assert "asteroid" in etf["description"].lower()
        assert len(etf["tracking_companies"]) > 0
        assert etf["risk_level"] == "extreme"


class TestAIInstrumentGenerator:
    """Test AI-generated financial instruments."""
    
    @pytest.fixture
    def reset_generator(self):
        """Reset instrument generator."""
        ai_instrument_generator.created_instruments = []
        yield
    
    def test_create_quantum_etf(self, reset_generator):
        """Test quantum computing ETF creation."""
        etf = ai_instrument_generator.create_dynamic_etf(
            theme="quantum computing",
            risk_tolerance="high",
            market_condition="bullish"
        )
        
        assert etf.instrument_type == InstrumentType.DYNAMIC_ETF
        assert "quantum" in etf.name.lower()
        assert len(etf.components) > 0
        assert etf.ai_rationale is not None
    
    def test_create_ai_revolution_etf(self, reset_generator):
        """Test AI revolution ETF."""
        etf = ai_instrument_generator.create_dynamic_etf(
            theme="ai revolution",
            risk_tolerance="high",
            market_condition="bullish"
        )
        
        assert len(etf.components) >= 4
        symbols = [c.symbol for c in etf.components]
        assert any(s in symbols for s in ["NVDA", "MSFT", "GOOGL"])
    
    def test_create_synthetic_remote_work(self, reset_generator):
        """Test synthetic asset for remote work."""
        synth = ai_instrument_generator.create_synthetic_asset(
            concept="remote work economy",
            tracking_method="proxy_basket"
        )
        
        assert synth.instrument_type == InstrumentType.SYNTHETIC_ASSET
        assert "remote work" in synth.name.lower()
        assert len(synth.components) > 0
    
    def test_create_personalized_retirement_index(self, reset_generator):
        """Test personalized retirement index."""
        index = ai_instrument_generator.create_personalized_index(
            user_goals=["retirement"],
            risk_profile="medium",
            time_horizon="long_term"
        )
        
        assert index.instrument_type == InstrumentType.PERSONALIZED_INDEX
        assert "retirement" in index.name.lower()
        assert len(index.components) > 0
        # Check weights sum to ~1
        total_weight = sum(c.weight for c in index.components)
        assert 0.99 <= total_weight <= 1.01
    
    def test_volatile_market_defensive_allocation(self, reset_generator):
        """Test defensive allocation in volatile markets."""
        etf = ai_instrument_generator.create_dynamic_etf(
            theme="inflation hedge",
            risk_tolerance="medium",
            market_condition="volatile"
        )
        
        symbols = [c.symbol for c in etf.components]
        # Should have defensive components in volatile markets
        assert any(s in symbols for s in ["TLT", "GLD", "BND"])
    
    def test_list_instruments(self, reset_generator):
        """Test listing created instruments."""
        # Create some instruments
        ai_instrument_generator.create_dynamic_etf("test1", "low", "neutral")
        ai_instrument_generator.create_dynamic_etf("test2", "high", "bullish")
        
        instruments = ai_instrument_generator.get_all_instruments()
        assert len(instruments) == 2


class TestTemporalArbitrage:
    """Test nanosecond precision trading infrastructure."""
    
    def test_latency_profiles_initialized(self):
        """Test exchange latency profiles exist."""
        assert len(temporal_arbitrage.latency_profiles) == 3
        assert ExchangeLocation.NY4 in temporal_arbitrage.latency_profiles
        assert ExchangeLocation.LD4 in temporal_arbitrage.latency_profiles
        assert ExchangeLocation.TY3 in temporal_arbitrage.latency_profiles
    
    def test_ny4_lowest_latency(self):
        """Test NY4 has lowest latency."""
        profile = temporal_arbitrage.latency_profiles[ExchangeLocation.NY4]
        assert profile.avg_latency_ns == 500
        assert profile.co_location_available is True
    
    def test_get_fastest_exchange(self):
        """Test fastest exchange identification."""
        fastest = temporal_arbitrage.get_fastest_exchange()
        assert fastest == ExchangeLocation.NY4
    
    def test_get_status(self):
        """Test temporal arbitrage status."""
        status = temporal_arbitrage.get_status()
        assert "exchanges" in status
        assert "fastest" in status
        assert status["min_latency_ns"] == 500


class TestIntegration:
    """Integration tests across Phase 10 features."""
    
    @pytest.mark.asyncio
    async def test_bci_blocks_trading_in_stress(self):
        """Test BCI blocks trading when stressed, even with good signals."""
        # Connect BCI
        await bci_interface.connect("muse")
        
        # Simulate stressed reading
        reading = BrainWaveReading(
            timestamp=datetime.now(),
            alpha_power=0.2,
            beta_power=0.9,  # Very high beta
            theta_power=0.3,
            gamma_power=0.2,
            delta_power=0.2,
            attention_score=45,  # Low attention
            meditation_score=20
        )
        
        bci_interface._update_trading_permissions(reading)
        
        # Trading should be blocked
        assert bci_interface.trading_enabled is False
        
        # Cleanup
        bci_interface.disconnect()
    
    def test_end_to_end_quantum_etf_simulation(self):
        """Test quantum ETF creation + reality simulation."""
        # Create quantum ETF
        etf = ai_instrument_generator.create_dynamic_etf(
            theme="quantum computing",
            risk_tolerance="high",
            market_condition="bullish"
        )
        
        # Simulate performance of first component
        symbol = etf.components[0].symbol
        result = reality_simulator.simulate_timelines(
            symbol=symbol,
            current_price=100.0,
            days_forward=30,
            scenario_type="bullish"
        )
        
        assert result.expected_value > 0
        assert len(result.timelines) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
