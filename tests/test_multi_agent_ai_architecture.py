
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Adjust import paths based on the Veyra project structure
from src.backend.app.multi_agent_ai_architecture import (
    MultiAgentOrchestrator, AgentType, AgentDecision, SystemState, AIAccountant, AIAnalyst
)
from src.backend.app.ai.enhanced_autonomous_ai import EnhancedAutonomousAI

@pytest.fixture
def mock_enhanced_ai_module():
    """Fixture for a mocked EnhancedAutonomousAI instance."""
    mock_module = AsyncMock(spec=EnhancedAutonomousAI)
    # Configure mock responses for methods called by agents
    mock_module.assess_portfolio_risk.return_value = {
        "status": "success",
        "metrics": {"VaR_95": 0.01, "sharpe_ratio": 1.5, "recommended_rebalance": []}
    }
    mock_module.get_financial_forecast.return_value = {
        "status": "success",
        "model": "Prophet",
        "forecast": [
            {"ds": (datetime.now() + timedelta(days=1)).isoformat(), "yhat": 150.0, "yhat_lower": 145.0, "yhat_upper": 155.0}
        ]
    }
    mock_module.analyze_news_sentiment_advanced.return_value = [
        {"article_id": "mock1", "sentiment": "positive", "confidence": 0.9, "source": "finbert"}
    ]
    return mock_module

@pytest.fixture
def mock_system_state():
    """Fixture for a mock SystemState instance."""
    return SystemState(
        timestamp=datetime.now(),
        portfolio_value=100000.0,
        cash_position=10000.0,
        active_positions={
            "AAPL": {"quantity": 10, "current_price": 170.0, "cost_basis": 160.0, "type": "equity"},
            "MSFT": {"quantity": 5, "current_price": 300.0, "cost_basis": 290.0, "type": "equity"}
        },
        open_orders=[],
        pending_decisions=[],
        alerts=[],
        phase="Test",
        risk_metrics={},
        compliance_status={},
        last_audit=datetime.now()
    )

@pytest.mark.asyncio
async def test_orchestrator_initialization_with_enhanced_ai(mock_enhanced_ai_module):
    """Test that MultiAgentOrchestrator initializes EnhancedAutonomousAI and passes it to agents."""
    with patch(
        "Veyra.src.backend.app.multi_agent_ai_architecture.EnhancedAutonomousAI",
        return_value=mock_enhanced_ai_module
    ) as MockEnhancedAutonomousAI:
        orchestrator = MultiAgentOrchestrator(config={})
        MockEnhancedAutonomousAI.assert_called_once_with(config={})
        assert orchestrator.enhanced_ai_module == mock_enhanced_ai_module
        assert isinstance(orchestrator.agents[AgentType.ACCOUNTANT], AIAccountant)
        assert orchestrator.agents[AgentType.ACCOUNTANT].ai_module == mock_enhanced_ai_module
        assert isinstance(orchestrator.agents[AgentType.ANALYST], AIAnalyst)
        assert orchestrator.agents[AgentType.ANALYST].ai_module == mock_enhanced_ai_module

@pytest.mark.asyncio
async def test_ai_accountant_uses_enhanced_ai(mock_enhanced_ai_module, mock_system_state):
    """Test AIAccountant calls assess_portfolio_risk from EnhancedAutonomousAI."""
    accountant = AIAccountant(config={}, ai_module=mock_enhanced_ai_module)
    decisions = await accountant.analyze(mock_system_state)

    mock_enhanced_ai_module.assess_portfolio_risk.assert_called_once_with(
        {"portfolio": mock_system_state.active_positions}
    )
    # Verify a decision related to risk assessment is generated or influenced
    assert any("Risk Assessment" in d.title for d in decisions)

@pytest.mark.asyncio
async def test_ai_analyst_uses_enhanced_ai(mock_enhanced_ai_module, mock_system_state):
    """Test AIAnalyst calls financial forecasting and sentiment analysis from EnhancedAutonomousAI."""
    analyst = AIAnalyst(config={}, ai_module=mock_enhanced_ai_module)
    decisions = await analyst.analyze(mock_system_state)

    # Check if get_financial_forecast was called
    mock_enhanced_ai_module.get_financial_forecast.assert_called_once_with("AAPL") # Default target_symbol

    # Check if analyze_news_sentiment_advanced was called
    mock_enhanced_ai_module.analyze_news_sentiment_advanced.assert_called_once()
    args, _ = mock_enhanced_ai_module.analyze_news_sentiment_advanced.call_args
    assert len(args[0]) == 2 # Expecting 2 mock news articles

    # Verify decisions related to forecast and sentiment are generated
    assert any("Financial Forecast" in d.title for d in decisions)
    assert any("Sentiment Analysis" in d.title for d in decisions)

@pytest.mark.asyncio
async def test_ai_analyst_fallback_without_enhanced_ai(mock_system_state):
    """Test AIAnalyst falls back to default methods if EnhancedAutonomousAI is not provided."""
    analyst = AIAnalyst(config={})
    # Mock the internal methods that would be called in fallback mode
    analyst._identify_opportunities = AsyncMock(return_value=[])
    analyst._check_correlations = AsyncMock(return_value=None)
    analyst._analyze_sentiment = AsyncMock(return_value=None)
    analyst._check_macro_conditions = AsyncMock(return_value=None)

    decisions = await analyst.analyze(mock_system_state)

    analyst._identify_opportunities.assert_called_once()
    analyst._check_correlations.assert_called_once()
    analyst._analyze_sentiment.assert_called_once()
    analyst._check_macro_conditions.assert_called_once()
    assert not decisions # No new decisions from AI/ML if fallback is used

# You can add more tests here for specific scenarios or edge cases
