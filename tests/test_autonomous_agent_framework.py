"""
Test suite for autonomous agent framework
Tests agent functionality, decision making, and execution cycles
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from app.autonomous_agent_framework import (
    AgentOrchestrator, 
    BaseAgent,
    MarketDataCollectorAgent,
    TaxOptimizerAgent,
    RiskManagerAgent,
    PortfolioRebalancerAgent,
    RetirementPlannerAgent,
    WithdrawalStrategistAgent,
    SentimentAnalyzerAgent,
    create_default_agents
)


class TestAgentOrchestrator:
    """Test the main agent orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create test orchestrator instance"""
        return AgentOrchestrator()
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator.agents == {}
        assert orchestrator.approval_gate is not None
        assert orchestrator.config is not None
        assert orchestrator.running == False
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, orchestrator):
        """Test agent registration"""
        mock_agent = Mock(spec=BaseAgent)
        mock_agent.name = "TestAgent"
        mock_agent.get_interval_seconds.return_value = 60
        
        agent_id = orchestrator.register_agent(mock_agent)
        
        assert agent_id is not None
        assert agent_id in orchestrator.agents
        assert orchestrator.agents[agent_id] == mock_agent
    
    @pytest.mark.asyncio
    async def test_agent_decision_approval(self, orchestrator):
        """Test agent decision approval process"""
        mock_agent = Mock(spec=BaseAgent)
        mock_agent.name = "TestAgent"
        
        agent_id = orchestrator.register_agent(mock_agent)
        
        # Test auto-approval for low-risk decisions
        decision = orchestrator.approval_gate.create_decision(
            agent_name="TestAgent",
            action_type="READ",
            risk_level="LOW",
            description="Test low-risk action",
            details={},
            confidence=0.9
        )
        
        result = orchestrator.approve_decision(decision["decision_id"], "test_user")
        assert result == True
        
        # Verify decision status updated
        updated_decision = orchestrator.approval_gate.get_decision(decision["decision_id"])
        assert updated_decision["status"] == "approved"


class TestMarketDataCollectorAgent:
    """Test market data collection agent"""
    
    @pytest.fixture
    def agent(self):
        """Create test agent instance"""
        mock_approval_gate = Mock()
        mock_llm_manager = Mock()
        return MarketDataCollectorAgent(mock_approval_gate, mock_llm_manager)
    
    @pytest.mark.asyncio
    async def test_market_data_collection_cycle(self, agent):
        """Test market data collection execution cycle"""
        # Mock approval gate to auto-approve
        agent.approval_gate.auto_approve_below = 10000
        agent.approval_gate.create_decision = Mock(return_value={
            "decision_id": "test_decision_123",
            "status": "auto_approved"
        })
        
        # Execute agent cycle
        await agent.execute_cycle()
        
        # Verify agent ran
        assert agent.run_count > 0
        assert agent.last_run is not None
    
    def test_get_interval_seconds(self, agent):
        """Test agent interval configuration"""
        interval = agent.get_interval_seconds()
        assert interval == 60  # Should run every minute


class TestTaxOptimizerAgent:
    """Test tax optimization agent"""
    
    @pytest.fixture
    def agent(self):
        """Create test agent instance"""
        mock_approval_gate = Mock()
        mock_llm_manager = Mock()
        return TaxOptimizerAgent(mock_approval_gate, mock_llm_manager)
    
    @pytest.mark.asyncio
    async def test_tax_loss_harvesting(self, agent):
        """Test tax loss harvesting functionality"""
        # Mock approval gate to approve
        agent.approval_gate.create_decision = Mock(return_value={
            "decision_id": "test_tax_decision",
            "status": "approved"
        })
        
        # Execute agent cycle
        await agent.execute_cycle()
        
        # Verify agent ran
        assert agent.run_count > 0
    
    def test_get_interval_seconds(self, agent):
        """Test agent interval configuration"""
        interval = agent.get_interval_seconds()
        assert interval == 3600  # Should run hourly


class TestRiskManagerAgent:
    """Test risk management agent"""
    
    @pytest.fixture
    def agent(self):
        """Create test agent instance"""
        mock_approval_gate = Mock()
        mock_llm_manager = Mock()
        return RiskManagerAgent(mock_approval_gate, mock_llm_manager)
    
    @pytest.mark.asyncio
    async def test_risk_monitoring(self, agent):
        """Test risk monitoring functionality"""
        # Mock approval gate to approve
        agent.approval_gate.create_decision = Mock(return_value={
            "decision_id": "test_risk_decision",
            "status": "approved"
        })
        
        # Execute agent cycle
        await agent.execute_cycle()
        
        # Verify agent ran
        assert agent.run_count > 0
    
    def test_get_interval_seconds(self, agent):
        """Test agent interval configuration"""
        interval = agent.get_interval_seconds()
        assert interval == 300  # Should run every 5 minutes


class TestPortfolioRebalancerAgent:
    """Test portfolio rebalancing agent"""
    
    @pytest.fixture
    def agent(self):
        """Create test agent instance"""
        mock_approval_gate = Mock()
        mock_llm_manager = Mock()
        return PortfolioRebalancerAgent(mock_approval_gate, mock_llm_manager)
    
    @pytest.mark.asyncio
    async def test_portfolio_rebalancing(self, agent):
        """Test portfolio rebalancing functionality"""
        # Mock approval gate to approve
        agent.approval_gate.create_decision = Mock(return_value={
            "decision_id": "test_rebalance_decision",
            "status": "approved"
        })
        
        # Execute agent cycle
        await agent.execute_cycle()
        
        # Verify agent ran
        assert agent.run_count > 0
    
    def test_get_interval_seconds(self, agent):
        """Test agent interval configuration"""
        interval = agent.get_interval_seconds()
        assert interval == 86400  # Should run daily


class TestAgentIntegration:
    """Test agent integration and coordination"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create test orchestrator with agents"""
        orch = AgentOrchestrator()
        
        # Register all default agents
        agent_ids = create_default_agents(orch)
        
        return orch
    
    @pytest.mark.asyncio
    async def test_agent_coordination(self, orchestrator):
        """Test multiple agents working together"""
        # Start all agents
        await orchestrator.start()
        
        # Let agents run for a short time
        await asyncio.sleep(0.1)
        
        # Stop orchestrator
        orchestrator.stop()
        
        # Verify agents were registered
        assert len(orchestrator.agents) >= 5  # At least 5 default agents
    
    def test_system_status(self, orchestrator):
        """Test system status reporting"""
        status = orchestrator.get_status()
        
        assert "running" in status
        assert "agents" in status
        assert "emergency_stop" in status
        assert "global_kill_switch" in status


if __name__ == "__main__":
    pytest.main([__file__])
