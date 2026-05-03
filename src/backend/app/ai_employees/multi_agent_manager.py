"""
Multi-Agent Manager for Financial Master
Implements Hive Mind and Singular Mind coordination
Based on AI Employees analysis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field

from .financial_agents import (
    BaseAIAgent, AgentTask, AgentMessage,
    FinancialAdvisorAI, TradingStrategistAI,
    TaxOptimizerAI, ComplianceOfficerAI, CustomerSupportAI
)
from .agent_config import AgentConfig, AgentType, ProcessingMode

logger = logging.getLogger(__name__)


@dataclass
class AgentTeam:
    """A team of agents working on a specific objective"""
    team_id: str
    name: str
    objective: str
    member_ids: List[str] = field(default_factory=list)
    lead_agent_id: Optional[str] = None
    created_at: datetime = None
    status: str = "active"  # active, completed, dissolved
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class MultiAgentManager:
    """
    Manages multiple AI agents with different coordination modes
    
    Two primary modes:
    1. Singular Mind (Independent) - Agents work independently
    2. Hive Mind (Collaborative) - Agents work together as a network
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAIAgent] = {}
        self.teams: Dict[str, AgentTeam] = {}
        self.message_bus: asyncio.Queue = asyncio.Queue()
        self.active_conversations: Dict[str, List[AgentMessage]] = {}
        self.coordination_mode: ProcessingMode = ProcessingMode.SINGULAR
        
        # Collaboration rules
        self.collaboration_rules: Dict[str, Callable] = {
            'portfolio_rebalancing': self._coordinate_portfolio_rebalancing,
            'tax_optimization': self._coordinate_tax_optimization,
            'compliance_audit': self._coordinate_compliance_audit,
            'customer_onboarding': self._coordinate_customer_onboarding
        }
    
    def register_agent(self, agent: BaseAIAgent) -> str:
        """Register an agent with the manager"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id} ({agent.config.name})")
        return agent.agent_id
    
    def create_default_team(self, team_id: str, name: str = "Financial Team") -> AgentTeam:
        """Create a default team with all 5 core agents"""
        # Create agents if they don't exist
        agents_to_create = [
            ('advisor_001', AgentType.FINANCIAL_ADVISOR),
            ('trader_001', AgentType.TRADING_STRATEGIST),
            ('tax_001', AgentType.TAX_OPTIMIZER),
            ('compliance_001', AgentType.COMPLIANCE_OFFICER),
            ('support_001', AgentType.CUSTOMER_SUPPORT)
        ]
        
        member_ids = []
        for agent_id, agent_type in agents_to_create:
            if agent_id not in self.agents:
                agent = self._create_agent_by_type(agent_id, agent_type)
                self.register_agent(agent)
            member_ids.append(agent_id)
        
        team = AgentTeam(
            team_id=team_id,
            name=name,
            objective="Comprehensive financial management and support",
            member_ids=member_ids,
            lead_agent_id='advisor_001'  # Financial Advisor leads
        )
        
        self.teams[team_id] = team
        logger.info(f"Created team: {team_id} with {len(member_ids)} agents")
        return team
    
    def _create_agent_by_type(self, agent_id: str, agent_type: AgentType) -> BaseAIAgent:
        """Factory method to create agent by type"""
        from .agent_config import get_default_agent_template
        config = get_default_agent_template(agent_type)
        
        agent_map = {
            AgentType.FINANCIAL_ADVISOR: FinancialAdvisorAI,
            AgentType.TRADING_STRATEGIST: TradingStrategistAI,
            AgentType.TAX_OPTIMIZER: TaxOptimizerAI,
            AgentType.COMPLIANCE_OFFICER: ComplianceOfficerAI,
            AgentType.CUSTOMER_SUPPORT: CustomerSupportAI
        }
        
        agent_class = agent_map.get(agent_type)
        if agent_class:
            return agent_class(agent_id, config)
        
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    async def assign_task(self, task: AgentTask, 
                         agent_id: Optional[str] = None,
                         team_id: Optional[str] = None) -> Dict:
        """
        Assign a task to an agent or team
        
        If agent_id provided: singular mode
        If team_id provided: hive mode - distributes to appropriate agent
        """
        if agent_id:
            # Singular mode - direct assignment
            agent = self.agents.get(agent_id)
            if not agent:
                return {'error': f'Agent {agent_id} not found'}
            
            await agent.assign_task(task)
            
            # Execute task
            try:
                result = await agent.process_task(task)
                return {
                    'status': 'success',
                    'agent_id': agent_id,
                    'task_id': task.task_id,
                    'result': result
                }
            except Exception as e:
                return {
                    'status': 'failed',
                    'agent_id': agent_id,
                    'task_id': task.task_id,
                    'error': str(e)
                }
        
        elif team_id:
            # Hive mode - intelligent routing
            return await self._route_task_to_team(task, team_id)
        
        else:
            # Auto-select agent based on task type
            agent_id = self._select_agent_for_task(task)
            if agent_id:
                return await self.assign_task(task, agent_id=agent_id)
            
            return {'error': 'No suitable agent found for task'}
    
    def _select_agent_for_task(self, task: AgentTask) -> Optional[str]:
        """Intelligently select the best agent for a task"""
        task_type = task.task_type
        
        # Task-to-agent mapping
        mapping = {
            # Financial Advisor tasks
            'portfolio_analysis': 'advisor_001',
            'goal_planning': 'advisor_001',
            'risk_assessment': 'advisor_001',
            'retirement_planning': 'advisor_001',
            
            # Trading Strategist tasks
            'strategy_backtest': 'trader_001',
            'market_scan': 'trader_001',
            'signal_generation': 'trader_001',
            'pattern_detection': 'trader_001',
            
            # Tax Optimizer tasks
            'tax_loss_harvesting': 'tax_001',
            'tax_projection': 'tax_001',
            'deduction_analysis': 'tax_001',
            'year_end_strategy': 'tax_001',
            
            # Compliance tasks
            'transaction_review': 'compliance_001',
            'kyc_check': 'compliance_001',
            'audit_trail': 'compliance_001',
            
            # Support tasks
            'answer_question': 'support_001',
            'troubleshoot': 'support_001',
            'escalate': 'support_001'
        }
        
        return mapping.get(task_type)
    
    async def _route_task_to_team(self, task: AgentTask, team_id: str) -> Dict:
        """Route task to appropriate team member in hive mode"""
        team = self.teams.get(team_id)
        if not team:
            return {'error': f'Team {team_id} not found'}
        
        # Select best agent from team
        agent_id = self._select_agent_for_task(task)
        
        if agent_id and agent_id in team.member_ids:
            return await self.assign_task(task, agent_id=agent_id)
        
        # Fallback: assign to lead agent
        if team.lead_agent_id:
            return await self.assign_task(task, agent_id=team.lead_agent_id)
        
        return {'error': 'Could not route task in team'}
    
    async def coordinate_agents(self, coordination_type: str, 
                               parameters: Dict) -> Dict:
        """
        Coordinate multiple agents for complex tasks
        
        Types:
        - portfolio_rebalancing
        - tax_optimization
        - compliance_audit
        - customer_onboarding
        """
        coordinator = self.collaboration_rules.get(coordination_type)
        if coordinator:
            return await coordinator(parameters)
        
        return {'error': f'Unknown coordination type: {coordination_type}'}
    
    async def _coordinate_portfolio_rebalancing(self, params: Dict) -> Dict:
        """Coordinate Financial Advisor and Trading Strategist for rebalancing"""
        user_id = params.get('user_id')
        portfolio = params.get('portfolio', {})
        
        # Step 1: Financial Advisor analyzes portfolio
        advisor_task = AgentTask(
            task_id=f"rebalance_analysis_{user_id}",
            task_type="portfolio_analysis",
            description="Analyze portfolio for rebalancing",
            parameters={'portfolio': portfolio, 'user_profile': params.get('user_profile')}
        )
        
        advisor_result = await self.assign_task(advisor_task, agent_id='advisor_001')
        
        if advisor_result.get('status') != 'success':
            return {'error': 'Portfolio analysis failed', 'details': advisor_result}
        
        analysis = advisor_result.get('result', {}).get('analysis', {})
        
        # Step 2: Trading Strategist generates execution plan
        if analysis.get('rebalancing_needed'):
            trader_task = AgentTask(
                task_id=f"rebalance_execution_{user_id}",
                task_type="market_scan",
                description="Generate rebalancing trades",
                parameters={
                    'rebalancing_changes': analysis.get('suggested_changes', []),
                    'market_conditions': params.get('market_conditions')
                }
            )
            
            trader_result = await self.assign_task(trader_task, agent_id='trader_001')
            
            return {
                'status': 'success',
                'analysis': analysis,
                'execution_plan': trader_result.get('result', {}),
                'coordinated_by': ['advisor_001', 'trader_001']
            }
        
        return {
            'status': 'no_action_needed',
            'message': 'Portfolio is already balanced',
            'analysis': analysis
        }
    
    async def _coordinate_tax_optimization(self, params: Dict) -> Dict:
        """Coordinate Tax Optimizer and Financial Advisor"""
        user_id = params.get('user_id')
        
        # Tax Optimizer finds opportunities
        tax_task = AgentTask(
            task_id=f"tax_opt_{user_id}",
            task_type="tax_loss_harvesting",
            description="Find tax optimization opportunities",
            parameters=params
        )
        
        tax_result = await self.assign_task(tax_task, agent_id='tax_001')
        
        if tax_result.get('status') == 'success':
            tax_opportunities = tax_result.get('result', {})
            
            # Financial Advisor reviews impact on portfolio
            if tax_opportunities.get('opportunities'):
                advisor_task = AgentTask(
                    task_id=f"tax_review_{user_id}",
                    task_type="goal_planning",
                    description="Review tax optimization impact",
                    parameters={'tax_changes': tax_opportunities}
                )
                
                advisor_result = await self.assign_task(advisor_task, agent_id='advisor_001')
                
                return {
                    'status': 'success',
                    'tax_optimization': tax_opportunities,
                    'portfolio_impact': advisor_result.get('result', {}),
                    'recommended_action': 'proceed_with_harvesting'
                }
        
        return tax_result
    
    async def _coordinate_compliance_audit(self, params: Dict) -> Dict:
        """Coordinate Compliance Officer with all agents"""
        # Compliance Officer reviews recent activities
        compliance_task = AgentTask(
            task_id=f"audit_{params.get('user_id')}",
            task_type="audit_trail",
            description="Review user activities for compliance",
            parameters=params
        )
        
        return await self.assign_task(compliance_task, agent_id='compliance_001')
    
    async def _coordinate_customer_onboarding(self, params: Dict) -> Dict:
        """Coordinate multiple agents for new customer onboarding"""
        user_id = params.get('user_id')
        
        results = {}
        
        # 1. Support Agent welcomes and guides
        support_task = AgentTask(
            task_id=f"onboard_support_{user_id}",
            task_type="guide_user",
            description="Guide new user through onboarding",
            parameters={'user_id': user_id, 'step': 'welcome'}
        )
        results['support'] = await self.assign_task(support_task, agent_id='support_001')
        
        # 2. Compliance Officer verifies identity
        compliance_task = AgentTask(
            task_id=f"onboard_kyc_{user_id}",
            task_type="kyc_check",
            description="Verify new user identity",
            parameters={'user_id': user_id}
        )
        results['compliance'] = await self.assign_task(compliance_task, agent_id='compliance_001')
        
        # 3. Financial Advisor creates initial assessment
        advisor_task = AgentTask(
            task_id=f"onboard_assessment_{user_id}",
            task_type="risk_assessment",
            description="Initial risk assessment",
            parameters={'user_id': user_id, 'profile': params.get('profile')}
        )
        results['advisor'] = await self.assign_task(advisor_task, agent_id='advisor_001')
        
        return {
            'status': 'success',
            'onboarding_complete': all(r.get('status') == 'success' for r in results.values()),
            'agent_results': results
        }
    
    async def facilitate_collaboration(self, sender_id: str, 
                                      recipient_id: str,
                                      content: Dict) -> Optional[AgentMessage]:
        """Facilitate message exchange between agents"""
        sender = self.agents.get(sender_id)
        recipient = self.agents.get(recipient_id)
        
        if not sender or not recipient:
            logger.error(f"Agent not found: sender={sender_id}, recipient={recipient_id}")
            return None
        
        # Create message
        message = AgentMessage(
            sender=sender_id,
            recipient=recipient_id,
            message_type=content.get('type', 'query'),
            content=content,
            requires_response=content.get('requires_response', False)
        )
        
        # Deliver to recipient
        response = await recipient.handle_message(message)
        
        return response
    
    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict:
        """Get status of one or all agents"""
        if agent_id:
            agent = self.agents.get(agent_id)
            return agent.get_status() if agent else {'error': 'Agent not found'}
        
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }
    
    def get_team_status(self, team_id: str) -> Dict:
        """Get status of a team"""
        team = self.teams.get(team_id)
        if not team:
            return {'error': 'Team not found'}
        
        return {
            'team_id': team.team_id,
            'name': team.name,
            'objective': team.objective,
            'status': team.status,
            'member_count': len(team.member_ids),
            'lead_agent': team.lead_agent_id,
            'members': [self.get_agent_status(mid) for mid in team.member_ids]
        }
    
    async def broadcast_to_team(self, team_id: str, content: Dict) -> List[Dict]:
        """Broadcast a message to all team members"""
        team = self.teams.get(team_id)
        if not team:
            return [{'error': 'Team not found'}]
        
        responses = []
        for member_id in team.member_ids:
            message = AgentMessage(
                sender="system",
                recipient=member_id,
                message_type="broadcast",
                content=content,
                requires_response=False
            )
            
            agent = self.agents.get(member_id)
            if agent:
                response = await agent.handle_message(message)
                responses.append({
                    'agent_id': member_id,
                    'acknowledged': True
                })
        
        return responses
