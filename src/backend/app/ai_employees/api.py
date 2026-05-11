"""
FastAPI Routes for AI Employees System
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

from .multi_agent_manager import MultiAgentManager
from .financial_agents import AgentTask
from .agent_config import AgentConfig, AgentType, get_default_agent_template

ai_employees_router = APIRouter(prefix="/ai-employees", tags=["ai-employees"])

# Global manager instance
agent_manager = MultiAgentManager()

# Initialize default team on startup
def initialize_default_team():
    """Initialize the default financial team"""
    agent_manager.create_default_team(
        team_id="financial_team_001",
        name="Veyra Team"
    )


# Pydantic models for API
class CreateTaskRequest(BaseModel):
    task_type: str
    description: str
    parameters: Dict[str, Any]
    priority: int = 1
    agent_id: Optional[str] = None
    team_id: Optional[str] = None


class CreateAgentRequest(BaseModel):
    agent_type: str
    custom_config: Optional[Dict] = None


class CollaborationRequest(BaseModel):
    coordination_type: str
    parameters: Dict[str, Any]


class MessageRequest(BaseModel):
    sender_id: str
    recipient_id: str
    content: Dict[str, Any]


# API Endpoints

@ai_employees_router.post("/tasks")
async def create_task(request: CreateTaskRequest):
    """
    Create and assign a task to an AI employee
    
    Either agent_id OR team_id must be provided
    """
    task = AgentTask(
        task_id=f"task_{datetime.now().timestamp()}",
        task_type=request.task_type,
        description=request.description,
        parameters=request.parameters,
        priority=request.priority
    )
    
    result = await agent_manager.assign_task(
        task=task,
        agent_id=request.agent_id,
        team_id=request.team_id
    )
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return {
        'status': 'success',
        'task_id': task.task_id,
        'assignment': result
    }


@ai_employees_router.get("/agents")
async def list_agents():
    """List all registered AI agents with their status"""
    return agent_manager.get_agent_status()


@ai_employees_router.get("/agents/{agent_id}")
async def get_agent_status(agent_id: str):
    """Get detailed status of a specific agent"""
    status = agent_manager.get_agent_status(agent_id)
    if 'error' in status:
        raise HTTPException(status_code=404, detail=status['error'])
    return status


@ai_employees_router.post("/agents")
async def create_agent(request: CreateAgentRequest):
    """Create a new AI agent"""
    try:
        agent_type = AgentType(request.agent_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {request.agent_type}")
    
    # Generate unique agent ID
    agent_id = f"{agent_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Get configuration
    if request.custom_config:
        config = AgentConfig.from_dict(request.custom_config)
    else:
        config = get_default_agent_template(agent_type)
    
    # Create agent
    agent = agent_manager._create_agent_by_type(agent_id, agent_type)
    agent.config = config
    
    # Register
    agent_manager.register_agent(agent)
    
    return {
        'status': 'success',
        'agent_id': agent_id,
        'agent_type': agent_type.value,
        'name': config.name
    }


@ai_employees_router.get("/teams")
async def list_teams():
    """List all agent teams"""
    return {
        'teams': [
            {
                'team_id': team.team_id,
                'name': team.name,
                'objective': team.objective,
                'status': team.status,
                'member_count': len(team.member_ids)
            }
            for team in agent_manager.teams.values()
        ]
    }


@ai_employees_router.get("/teams/{team_id}")
async def get_team_status(team_id: str):
    """Get detailed status of a team"""
    status = agent_manager.get_team_status(team_id)
    if 'error' in status:
        raise HTTPException(status_code=404, detail=status['error'])
    return status


@ai_employees_router.post("/teams")
async def create_team(name: str, objective: str = "Financial management"):
    """Create a new agent team"""
    team_id = f"team_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    team = agent_manager.create_default_team(
        team_id=team_id,
        name=name
    )
    
    return {
        'status': 'success',
        'team_id': team.team_id,
        'name': team.name,
        'members': team.member_ids
    }


@ai_employees_router.post("/collaborate")
async def coordinate_agents(request: CollaborationRequest):
    """
    Coordinate multiple agents for complex tasks
    
    Types:
    - portfolio_rebalancing
    - tax_optimization
    - compliance_audit
    - customer_onboarding
    """
    result = await agent_manager.coordinate_agents(
        coordination_type=request.coordination_type,
        parameters=request.parameters
    )
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@ai_employees_router.post("/message")
async def send_message(request: MessageRequest):
    """Send a message between agents"""
    response = await agent_manager.facilitate_collaboration(
        sender_id=request.sender_id,
        recipient_id=request.recipient_id,
        content=request.content
    )
    
    if response is None:
        raise HTTPException(status_code=400, detail="Message delivery failed")
    
    return {
        'status': 'delivered',
        'message': {
            'sender': response.sender,
            'recipient': response.recipient,
            'type': response.message_type,
            'content': response.content,
            'timestamp': response.timestamp.isoformat()
        }
    }


@ai_employees_router.get("/templates")
async def get_agent_templates():
    """Get available agent templates"""
    templates = {}
    for agent_type in AgentType:
        if agent_type != AgentType.CUSTOM:
            config = get_default_agent_template(agent_type)
            templates[agent_type.value] = config.to_dict()
    
    return {
        'templates': templates,
        'count': len(templates)
    }


@ai_employees_router.get("/templates/{agent_type}")
async def get_specific_template(agent_type: str):
    """Get a specific agent template"""
    try:
        at = AgentType(agent_type)
        config = get_default_agent_template(at)
        return config.to_dict()
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Template not found: {agent_type}")


# Specific task endpoints for convenience

@ai_employees_router.post("/advice/portfolio-analysis")
async def portfolio_analysis(user_id: str, portfolio: Dict):
    """Request portfolio analysis from Financial Advisor"""
    task = AgentTask(
        task_id=f"portfolio_{user_id}_{datetime.now().timestamp()}",
        task_type="portfolio_analysis",
        description="Analyze user portfolio",
        parameters={'portfolio': portfolio, 'user_profile': {'user_id': user_id}},
        priority=2
    )
    
    result = await agent_manager.assign_task(task, agent_id='advisor_001')
    return result


@ai_employees_router.post("/trading/market-scan")
async def market_scan(universe: str = "sp500", criteria: Optional[Dict] = None):
    """Request market scan from Trading Strategist"""
    task = AgentTask(
        task_id=f"scan_{datetime.now().timestamp()}",
        task_type="market_scan",
        description="Scan markets for opportunities",
        parameters={'universe': universe, 'criteria': criteria or {}},
        priority=3
    )
    
    result = await agent_manager.assign_task(task, agent_id='trader_001')
    return result


@ai_employees_router.post("/tax/loss-harvesting")
async def tax_loss_harvesting(user_id: str, portfolio: Dict):
    """Find tax-loss harvesting opportunities"""
    task = AgentTask(
        task_id=f"tax_{user_id}_{datetime.now().timestamp()}",
        task_type="tax_loss_harvesting",
        description="Find tax loss harvesting opportunities",
        parameters={'portfolio': portfolio, 'user_id': user_id},
        priority=2
    )
    
    result = await agent_manager.assign_task(task, agent_id='tax_001')
    return result


@ai_employees_router.post("/support/ask")
async def ask_support(question: str, user_id: Optional[str] = None):
    """Ask customer support a question"""
    task = AgentTask(
        task_id=f"support_{datetime.now().timestamp()}",
        task_type="answer_question",
        description="Answer user question",
        parameters={'question': question, 'user_id': user_id, 'category': 'general'},
        priority=1
    )
    
    result = await agent_manager.assign_task(task, agent_id='support_001')
    return result


# Initialize on module load
initialize_default_team()
