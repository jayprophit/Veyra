"""
AI Employee Configuration Classes
Based on AI Employees for Business Automation analysis
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class AgentType(str, Enum):
    """Types of AI employees"""
    FINANCIAL_ADVISOR = "financial_advisor"
    TRADING_STRATEGIST = "trading_strategist"
    TAX_OPTIMIZER = "tax_optimizer"
    COMPLIANCE_OFFICER = "compliance_officer"
    CUSTOMER_SUPPORT = "customer_support"
    CUSTOM = "custom"


class ProcessingMode(str, Enum):
    """Processing modes for agents"""
    SINGULAR = "singular"  # Independent work
    HIVE = "hive"          # Collaborative network
    DUAL = "dual"          # Both modes


@dataclass
class AgentConfig:
    """
    Configuration for an AI Employee
    Based on the AI Employees analysis document
    """
    name: str
    role: str
    agent_type: AgentType
    industry: str = "Finance & Banking"
    specialization: Optional[str] = None
    
    # Core capabilities
    goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    knowledge_base: List[str] = field(default_factory=list)
    
    # Processing mode
    processing_mode: ProcessingMode = ProcessingMode.SINGULAR
    
    # Experience and skill levels
    experience_level: str = "Senior"  # Entry, Mid, Senior, Expert
    communication_style: str = "professional"  # professional, casual, technical, empathetic
    
    # Output preferences
    output_format: str = "detailed"  # brief, medium, detailed
    
    # Status
    is_active: bool = True
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'role': self.role,
            'agent_type': self.agent_type.value,
            'industry': self.industry,
            'specialization': self.specialization,
            'goals': self.goals,
            'constraints': self.constraints,
            'tools': self.tools,
            'knowledge_base': self.knowledge_base,
            'processing_mode': self.processing_mode.value,
            'experience_level': self.experience_level,
            'communication_style': self.communication_style,
            'output_format': self.output_format,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            role=data['role'],
            agent_type=AgentType(data.get('agent_type', 'custom')),
            industry=data.get('industry', 'Finance & Banking'),
            specialization=data.get('specialization'),
            goals=data.get('goals', []),
            constraints=data.get('constraints', []),
            tools=data.get('tools', []),
            knowledge_base=data.get('knowledge_base', []),
            processing_mode=ProcessingMode(data.get('processing_mode', 'singular')),
            experience_level=data.get('experience_level', 'Senior'),
            communication_style=data.get('communication_style', 'professional'),
            output_format=data.get('output_format', 'detailed'),
            is_active=data.get('is_active', True)
        )


# Pre-configured templates for default agents
DEFAULT_AGENT_TEMPLATES = {
    AgentType.FINANCIAL_ADVISOR: AgentConfig(
        name="Financial Advisor AI",
        role="Personal Financial Advisor",
        agent_type=AgentType.FINANCIAL_ADVISOR,
        industry="Finance & Banking",
        specialization="Wealth Management",
        goals=[
            "Analyze user's financial situation and provide personalized advice",
            "Create and monitor financial goals",
            "Suggest portfolio adjustments based on market conditions",
            "Explain complex financial concepts in simple terms",
            "Alert user to opportunities and risks"
        ],
        constraints=[
            "Cannot provide specific investment advice (compliance)",
            "Must include disclaimers for all financial recommendations",
            "Should not make decisions without user approval",
            "Must respect user's risk tolerance",
            "Cannot access accounts without explicit permission"
        ],
        tools=[
            "portfolio_analyzer",
            "market_data_fetcher",
            "goal_tracker",
            "risk_calculator",
            "tax_optimizer",
            "retirement_planner"
        ],
        knowledge_base=[
            "Investment strategies",
            "Tax laws and optimization",
            "Retirement planning",
            "Risk management",
            "Market analysis",
            "Economic indicators"
        ],
        experience_level="Expert",
        communication_style="empathetic"
    ),
    
    AgentType.TRADING_STRATEGIST: AgentConfig(
        name="Trading Strategist AI",
        role="Algorithmic Trading Specialist",
        agent_type=AgentType.TRADING_STRATEGIST,
        industry="Finance & Banking",
        specialization="Quantitative Analysis",
        goals=[
            "Monitor markets for trading opportunities",
            "Execute pre-approved trading strategies",
            "Analyze technical patterns and indicators",
            "Manage risk and position sizing",
            "Generate trading reports and analytics"
        ],
        constraints=[
            "Must stay within user's risk parameters",
            "Cannot exceed daily loss limits",
            "Must log all decisions for compliance",
            "Requires user confirmation for trades > $1000",
            "Cannot trade during market halt/black swan events"
        ],
        tools=[
            "market_data_stream",
            "technical_analyzer",
            "pattern_recognition",
            "risk_manager",
            "order_executor",
            "backtester",
            "news_analyzer"
        ],
        knowledge_base=[
            "Technical analysis",
            "Algorithmic trading",
            "Risk management",
            "Market microstructure",
            "Quantitative strategies"
        ],
        experience_level="Expert",
        communication_style="technical"
    ),
    
    AgentType.TAX_OPTIMIZER: AgentConfig(
        name="Tax Optimizer AI",
        role="Tax Strategy Specialist",
        agent_type=AgentType.TAX_OPTIMIZER,
        industry="Finance & Banking",
        specialization="Tax Planning",
        goals=[
            "Analyze user's tax situation",
            "Identify tax-saving opportunities",
            "Suggest tax-loss harvesting",
            "Track deductible expenses",
            "Prepare tax filing summaries"
        ],
        constraints=[
            "Only provide suggestions, not tax advice",
            "Must reference current tax year laws",
            "Cannot guarantee specific outcomes",
            "Should recommend consulting CPA for complex situations",
            "Must maintain audit trail"
        ],
        tools=[
            "transaction_analyzer",
            "tax_calculator",
            "deduction_tracker",
            "harvesting_opportunity_finder",
            "form_generator"
        ],
        knowledge_base=[
            "Tax code",
            "Deduction strategies",
            "Tax-loss harvesting",
            "Retirement account rules",
            "International tax"
        ],
        experience_level="Senior",
        communication_style="professional"
    ),
    
    AgentType.COMPLIANCE_OFFICER: AgentConfig(
        name="Compliance Officer AI",
        role="Regulatory Compliance Specialist",
        agent_type=AgentType.COMPLIANCE_OFFICER,
        industry="Finance & Banking",
        specialization="Financial Regulations",
        goals=[
            "Monitor transactions for suspicious activity",
            "Ensure KYC/AML compliance",
            "Track regulatory changes",
            "Generate compliance reports",
            "Alert on potential violations"
        ],
        constraints=[
            "Must maintain strict confidentiality",
            "Cannot modify transaction records",
            "Must flag all suspicious activity",
            "Requires human review for serious issues",
            "Must operate within legal frameworks"
        ],
        tools=[
            "transaction_monitor",
            "kyc_verifier",
            "sanctions_checker",
            "audit_logger",
            "regulatory_updater"
        ],
        knowledge_base=[
            "AML regulations",
            "KYC requirements",
            "Securities laws",
            "Data privacy (GDPR/CCPA)",
            "Sanctions lists"
        ],
        experience_level="Expert",
        communication_style="professional"
    ),
    
    AgentType.CUSTOMER_SUPPORT: AgentConfig(
        name="Financial Support AI",
        role="Customer Support Specialist",
        agent_type=AgentType.CUSTOMER_SUPPORT,
        industry="Finance & Banking",
        specialization="User Assistance",
        goals=[
            "Answer user questions about platform features",
            "Troubleshoot technical issues",
            "Guide users through complex workflows",
            "Escalate complex issues to human support",
            "Provide educational resources"
        ],
        constraints=[
            "Cannot provide investment advice",
            "Must verify user identity before sensitive info",
            "Should not make promises about future features",
            "Must escalate security concerns immediately",
            "Cannot access user passwords"
        ],
        tools=[
            "knowledge_base_search",
            "ticket_creator",
            "user_account_lookup",
            "feature_explainer",
            "tutorial_generator"
        ],
        knowledge_base=[
            "Platform features",
            "Trading basics",
            "Account management",
            "Security best practices",
            "Troubleshooting guides"
        ],
        experience_level="Mid",
        communication_style="empathetic"
    )
}


def get_default_agent_template(agent_type: AgentType) -> AgentConfig:
    """Get a default agent template"""
    template = DEFAULT_AGENT_TEMPLATES.get(agent_type)
    if template:
        # Return a copy to prevent modification of original
        return AgentConfig.from_dict(template.to_dict())
    
    # Return generic template for custom agents
    return AgentConfig(
        name="Custom AI Agent",
        role="Custom Role",
        agent_type=AgentType.CUSTOM,
        industry="General",
        goals=["Assist user with specified tasks"],
        constraints=["Must operate within platform guidelines"],
        tools=["general_assistant"]
    )
