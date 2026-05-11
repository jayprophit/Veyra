"""
Veyra MCP Server
Inspired by FactSet MCP - Free open-source alternative
Provides seamless AI integration with financial data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import json
import uuid
from enum import Enum

# MCP Server imports (mock implementation for demonstration)
# In production, these would be actual MCP library imports
from mcp.server import Server
from mcp.types import Tool, Resource

logger = logging.getLogger(__name__)

class DataCategory(Enum):
    """Financial data categories"""
    FUNDAMENTALS = "fundamentals"
    ESTIMATES = "estimates"
    OWNERSHIP = "ownership"
    MA = "ma"  # Mergers & Acquisitions
    PRICING = "pricing"
    PEOPLE = "people"
    EVENTS = "events"
    SUPPLY_CHAIN = "supply_chain"

class WorkflowType(Enum):
    """Banking workflow types"""
    MA_SCREENING = "ma_screening"
    CREDIT_RISK = "credit_risk"
    CAPITAL_STRUCTURE = "capital_structure"

@dataclass
class MCPRequest:
    """MCP request structure"""
    request_id: str
    user_id: str
    data_category: DataCategory
    query: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MCPResponse:
    """MCP response structure"""
    request_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class FinancialMCPServer:
    """Veyra MCP Server - Free alternative to FactSet MCP"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.server = Server("veyra-mcp")
        self.data_manager = self._get_data_manager()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
        
        logger.info("Financial MCP Server initialized")
    
    def _get_data_manager(self):
        """Get free data sources manager"""
        from ..integrations.free.free_data_sources import get_free_data_sources_manager
        return get_free_data_sources_manager(self.config.get('data_sources', {}))
    
    def _register_tools(self):
        """Register MCP tools"""
        
        # Data access tools
        self.server.add_tool(Tool(
            name="get_fundamentals",
            description="Get company fundamentals including financial statements and ratios",
            input_schema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "statement_type": {"type": "string", "enum": ["income", "balance", "cash_flow"], "description": "Statement type"},
                    "period": {"type": "string", "enum": ["annual", "quarterly"], "description": "Reporting period"}
                },
                "required": ["symbol"]
            }
        ))
        
        self.server.add_tool(Tool(
            name="get_estimates",
            description="Get analyst estimates and price targets",
            input_schema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "estimate_type": {"type": "string", "enum": ["eps", "revenue", "price_target"], "description": "Estimate type"}
                },
                "required": ["symbol"]
            }
        ))
        
        self.server.add_tool(Tool(
            name="get_ownership",
            description="Get institutional ownership and insider trading data",
            input_schema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "ownership_type": {"type": "string", "enum": ["institutional", "insider", "mutual_fund"], "description": "Ownership type"}
                },
                "required": ["symbol"]
            }
        ))
        
        self.server.add_tool(Tool(
            name="get_ma_data",
            description="Get mergers and acquisitions data and analysis",
            input_schema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name or symbol"},
                    "deal_type": {"type": "string", "enum": ["acquirer", "target", "all"], "description": "Deal type"},
                    "timeframe": {"type": "string", "description": "Timeframe (e.g., '1Y', '5Y')"}
                },
                "required": ["company"]
            }
        ))
        
        self.server.add_tool(Tool(
            name="get_pricing",
            description="Get real-time and historical pricing data",
            input_schema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "data_type": {"type": "string", "enum": ["real_time", "historical", "technical"], "description": "Data type"},
                    "period": {"type": "string", "description": "Historical period"}
                },
                "required": ["symbol"]
            }
        ))
        
        self.server.add_tool(Tool(
            name="get_people",
            description="Get company leadership and board information",
            input_schema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name or symbol"},
                    "role_type": {"type": "string", "enum": ["executive", "board", "all"], "description": "Role type"}
                },
                "required": ["company"]
            }
        ))
        
        self.server.add_tool(Tool(
            name="get_events",
            description="Get corporate events and calendar data",
            input_schema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "event_type": {"type": "string", "enum": ["earnings", "dividend", "split", "all"], "description": "Event type"},
                    "date_range": {"type": "string", "description": "Date range"}
                },
                "required": ["symbol"]
            }
        ))
        
        self.server.add_tool(Tool(
            name="get_supply_chain",
            description="Get supply chain and relationship data",
            input_schema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name or symbol"},
                    "relationship_type": {"type": "string", "enum": ["supplier", "customer", "competitor", "all"], "description": "Relationship type"}
                },
                "required": ["company"]
            }
        ))
        
        # Banking workflow tools
        self.server.add_tool(Tool(
            name="ma_screening_workflow",
            description="M&A screening and deal analysis workflow",
            input_schema={
                "type": "object",
                "properties": {
                    "target_company": {"type": "string", "description": "Target company"},
                    "acquirer_company": {"type": "string", "description": "Acquirer company"},
                    "analysis_depth": {"type": "string", "enum": ["basic", "comprehensive", "deep"], "description": "Analysis depth"}
                },
                "required": ["target_company"]
            }
        ))
        
        self.server.add_tool(Tool(
            name="credit_risk_workflow",
            description="Credit and counterparty risk analysis workflow",
            input_schema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company to analyze"},
                    "risk_type": {"type": "string", "enum": ["credit", "counterparty", "sovereign"], "description": "Risk type"},
                    "time_horizon": {"type": "string", "enum": ["1M", "3M", "6M", "1Y", "5Y"], "description": "Time horizon"}
                },
                "required": ["company"]
            }
        ))
        
        self.server.add_tool(Tool(
            name="capital_structure_workflow",
            description="Capital structure and ownership analysis workflow",
            input_schema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company to analyze"},
                    "analysis_type": {"type": "string", "enum": ["debt", "equity", "comprehensive"], "description": "Analysis type"},
                    "comparative": {"type": "boolean", "description": "Include comparative analysis"}
                },
                "required": ["company"]
            }
        ))
    
    def _register_resources(self):
        """Register MCP resources"""
        
        # Data resources
        self.server.add_resource(Resource(
            uri="veyra://data/fundamentals/{symbol}",
            name="Company Fundamentals",
            description="Comprehensive company fundamentals data",
            mime_type="application/json"
        ))
        
        self.server.add_resource(Resource(
            uri="veyra://data/estimates/{symbol}",
            name="Analyst Estimates",
            description="Analyst estimates and forecasts",
            mime_type="application/json"
        ))
        
        self.server.add_resource(Resource(
            uri="veyra://data/ownership/{symbol}",
            name="Ownership Data",
            description="Institutional and insider ownership",
            mime_type="application/json"
        ))
        
        self.server.add_resource(Resource(
            uri="veyra://data/pricing/{symbol}",
            name="Pricing Data",
            description="Real-time and historical pricing",
            mime_type="application/json"
        ))
        
        # Workflow resources
        self.server.add_resource(Resource(
            uri="veyra://workflows/ma/{company}",
            name="M&A Analysis",
            description="Mergers and acquisitions analysis",
            mime_type="application/json"
        ))
        
        self.server.add_resource(Resource(
            uri="veyra://workflows/credit/{company}",
            name="Credit Analysis",
            description="Credit risk analysis",
            mime_type="application/json"
        ))
        
        self.server.add_resource(Resource(
            uri="veyra://workflows/capital/{company}",
            name="Capital Structure",
            description="Capital structure analysis",
            mime_type="application/json"
        ))
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls"""
        try:
            if tool_name == "get_fundamentals":
                return await self._handle_get_fundamentals(arguments)
            elif tool_name == "get_estimates":
                return await self._handle_get_estimates(arguments)
            elif tool_name == "get_ownership":
                return await self._handle_get_ownership(arguments)
            elif tool_name == "get_ma_data":
                return await self._handle_get_ma_data(arguments)
            elif tool_name == "get_pricing":
                return await self._handle_get_pricing(arguments)
            elif tool_name == "get_people":
                return await self._handle_get_people(arguments)
            elif tool_name == "get_events":
                return await self._handle_get_events(arguments)
            elif tool_name == "get_supply_chain":
                return await self._handle_get_supply_chain(arguments)
            elif tool_name == "ma_screening_workflow":
                return await self._handle_ma_screening_workflow(arguments)
            elif tool_name == "credit_risk_workflow":
                return await self._handle_credit_risk_workflow(arguments)
            elif tool_name == "capital_structure_workflow":
                return await self._handle_capital_structure_workflow(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def _handle_get_fundamentals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fundamentals request"""
        symbol = args.get('symbol')
        statement_type = args.get('statement_type', 'income')
        period = args.get('period', 'annual')
        
        # Get fundamentals data
        fundamentals = await self.data_manager.get_financial_statements(symbol, statement_type, period)
        
        # Get financial analysis
        analysis = await self.data_manager.get_financial_analysis(symbol)
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "statement_type": statement_type,
                "period": period,
                "fundamentals": fundamentals,
                "financial_analysis": analysis,
                "metadata": {
                    "source": "free_data_sources",
                    "timestamp": datetime.now().isoformat(),
                    "data_quality": "high"
                }
            }
        }
    
    async def _handle_get_estimates(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle estimates request"""
        symbol = args.get('symbol')
        estimate_type = args.get('estimate_type', 'eps')
        
        # Mock estimates data (in production, integrate with real estimates APIs)
        estimates_data = {
            "symbol": symbol,
            "estimate_type": estimate_type,
            "current_quarter": {
                "eps_estimate": 2.45,
                "revenue_estimate": 125000000000,
                "consensus_date": "2024-01-15",
                "analyst_count": 25
            },
            "next_quarter": {
                "eps_estimate": 2.68,
                "revenue_estimate": 132000000000,
                "consensus_date": "2024-01-15",
                "analyst_count": 25
            },
            "current_year": {
                "eps_estimate": 10.25,
                "revenue_estimate": 520000000000,
                "growth_rate": 0.085,
                "analyst_count": 30
            },
            "price_targets": {
                "mean": 185.50,
                "high": 220.00,
                "low": 150.00,
                "median": 185.00,
                "analyst_count": 28
            },
            "recommendations": {
                "buy": 18,
                "hold": 8,
                "sell": 2,
                "consensus": "Buy"
            }
        }
        
        return {
            "success": True,
            "data": estimates_data
        }
    
    async def _handle_get_ownership(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ownership request"""
        symbol = args.get('symbol')
        ownership_type = args.get('ownership_type', 'institutional')
        
        # Mock ownership data
        ownership_data = {
            "symbol": symbol,
            "ownership_type": ownership_type,
            "institutional_ownership": {
                "total_institutions": 1250,
                "total_shares": 8500000000,
                "ownership_percentage": 0.68,
                "top_institutions": [
                    {"name": "Vanguard Group", "shares": 1250000000, "percentage": 0.10},
                    {"name": "BlackRock", "shares": 980000000, "percentage": 0.078},
                    {"name": "State Street", "shares": 650000000, "percentage": 0.052}
                ]
            },
            "insider_ownership": {
                "total_insiders": 25,
                "total_shares": 125000000,
                "ownership_percentage": 0.01,
                "recent_insider_trades": [
                    {"insider": "CEO", "shares": 10000, "type": "sale", "date": "2024-01-10"},
                    {"insider": "CFO", "shares": 5000, "type": "purchase", "date": "2024-01-08"}
                ]
            }
        }
        
        return {
            "success": True,
            "data": ownership_data
        }
    
    async def _handle_get_ma_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle M&A data request"""
        company = args.get('company')
        deal_type = args.get('deal_type', 'all')
        timeframe = args.get('timeframe', '5Y')
        
        # Mock M&A data
        ma_data = {
            "company": company,
            "deal_type": deal_type,
            "timeframe": timeframe,
            "recent_deals": [
                {
                    "deal_id": "DEAL_001",
                    "target": company,
                    "acquirer": "Acquirer Corp",
                    "deal_value": 25000000000,
                    "deal_type": "Acquisition",
                    "status": "Completed",
                    "announcement_date": "2023-06-15",
                    "completion_date": "2023-09-30"
                }
            ],
            "ma_activity": {
                "total_deals": 5,
                "total_value": 125000000000,
                "average_deal_size": 25000000000,
                "success_rate": 0.80
            },
            "strategic_fit": {
                "synergy_potential": "High",
                "cultural_alignment": "Medium",
                "integration_complexity": "Low"
            }
        }
        
        return {
            "success": True,
            "data": ma_data
        }
    
    async def _handle_get_pricing(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pricing request"""
        symbol = args.get('symbol')
        data_type = args.get('data_type', 'real_time')
        period = args.get('period', '1M')
        
        # Get pricing data
        if data_type == 'real_time':
            quotes = await self.data_manager.get_real_time_quotes([symbol])
            pricing_data = {
                "symbol": symbol,
                "data_type": data_type,
                "current_price": quotes[0].price if quotes else 0,
                "change": quotes[0].additional_data.get('change', 0) if quotes else 0,
                "change_percent": quotes[0].additional_data.get('change_percent', 0) if quotes else 0,
                "volume": quotes[0].volume if quotes else 0,
                "timestamp": quotes[0].timestamp.isoformat() if quotes else datetime.now().isoformat()
            }
        elif data_type == 'historical':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            historical = await self.data_manager.get_historical_data(symbol, start_date, end_date)
            pricing_data = {
                "symbol": symbol,
                "data_type": data_type,
                "period": period,
                "historical_data": historical,
                "statistics": self._calculate_price_statistics(historical)
            }
        else:  # technical
            pricing_data = {
                "symbol": symbol,
                "data_type": data_type,
                "technical_indicators": await self._get_technical_indicators(symbol),
                "signals": await self._get_trading_signals(symbol)
            }
        
        return {
            "success": True,
            "data": pricing_data
        }
    
    async def _handle_get_people(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle people request"""
        company = args.get('company')
        role_type = args.get('role_type', 'all')
        
        # Mock people data
        people_data = {
            "company": company,
            "role_type": role_type,
            "executives": [
                {
                    "name": "John Smith",
                    "title": "Chief Executive Officer",
                    "age": 52,
                    "tenure": 8,
                    "compensation": 15000000,
                    "background": "Technology industry veteran with 25+ years experience"
                },
                {
                    "name": "Jane Johnson",
                    "title": "Chief Financial Officer",
                    "age": 45,
                    "tenure": 5,
                    "compensation": 8500000,
                    "background": "Finance professional with previous experience at major banks"
                }
            ],
            "board_members": [
                {
                    "name": "Michael Brown",
                    "title": "Independent Director",
                    "age": 65,
                    "tenure": 12,
                    "committees": ["Audit", "Compensation"],
                    "background": "Retired CEO of Fortune 500 company"
                }
            ]
        }
        
        return {
            "success": True,
            "data": people_data
        }
    
    async def _handle_get_events(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle events request"""
        symbol = args.get('symbol')
        event_type = args.get('event_type', 'all')
        date_range = args.get('date_range', '3M')
        
        # Mock events data
        events_data = {
            "symbol": symbol,
            "event_type": event_type,
            "date_range": date_range,
            "events": [
                {
                    "event_type": "earnings",
                    "date": "2024-01-25",
                    "description": "Q4 2023 Earnings Release",
                    "expected_eps": 2.45,
                    "actual_eps": 2.52,
                    "surprise": 0.07
                },
                {
                    "event_type": "dividend",
                    "date": "2024-02-15",
                    "description": "Quarterly Dividend Payment",
                    "amount": 0.96,
                    "yield": 0.005
                }
            ]
        }
        
        return {
            "success": True,
            "data": events_data
        }
    
    async def _handle_get_supply_chain(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle supply chain request"""
        company = args.get('company')
        relationship_type = args.get('relationship_type', 'all')
        
        # Mock supply chain data
        supply_chain_data = {
            "company": company,
            "relationship_type": relationship_type,
            "suppliers": [
                {
                    "name": "Supplier A",
                    "relationship": "Key Supplier",
                    "dependency_level": "High",
                    "revenue_dependency": 0.15
                }
            ],
            "customers": [
                {
                    "name": "Customer A",
                    "relationship": "Major Customer",
                    "revenue_contribution": 0.12
                }
            ],
            "competitors": [
                {
                    "name": "Competitor A",
                    "market_position": "Direct Competitor",
                    "market_share_diff": 0.05
                }
            ]
        }
        
        return {
            "success": True,
            "data": supply_chain_data
        }
    
    async def _handle_ma_screening_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle M&A screening workflow"""
        target_company = args.get('target_company')
        acquirer_company = args.get('acquirer_company')
        analysis_depth = args.get('analysis_depth', 'comprehensive')
        
        # Execute M&A screening workflow
        workflow_result = await self._execute_ma_screening_workflow(
            target_company, acquirer_company, analysis_depth
        )
        
        return {
            "success": True,
            "data": workflow_result
        }
    
    async def _handle_credit_risk_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle credit risk workflow"""
        company = args.get('company')
        risk_type = args.get('risk_type', 'credit')
        time_horizon = args.get('time_horizon', '1Y')
        
        # Execute credit risk workflow
        workflow_result = await self._execute_credit_risk_workflow(
            company, risk_type, time_horizon
        )
        
        return {
            "success": True,
            "data": workflow_result
        }
    
    async def _handle_capital_structure_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capital structure workflow"""
        company = args.get('company')
        analysis_type = args.get('analysis_type', 'comprehensive')
        comparative = args.get('comparative', False)
        
        # Execute capital structure workflow
        workflow_result = await self._execute_capital_structure_workflow(
            company, analysis_type, comparative
        )
        
        return {
            "success": True,
            "data": workflow_result
        }
    
    async def _execute_ma_screening_workflow(self, target: str, acquirer: str, depth: str) -> Dict[str, Any]:
        """Execute M&A screening workflow"""
        # Mock M&A screening workflow
        return {
            "workflow_type": "ma_screening",
            "target_company": target,
            "acquirer_company": acquirer,
            "analysis_depth": depth,
            "screening_results": {
                "strategic_fit": {
                    "score": 0.85,
                    "rationale": "Strong strategic alignment and market synergies"
                },
                "financial_feasibility": {
                    "score": 0.78,
                    "rationale": "Financially viable with reasonable debt capacity"
                },
                "integration_complexity": {
                    "score": 0.72,
                    "rationale": "Moderate integration complexity expected"
                },
                "regulatory_risk": {
                    "score": 0.65,
                    "rationale": "Some regulatory approval required but manageable"
                }
            },
            "recommendation": "Proceed with due diligence",
            "confidence_score": 0.75
        }
    
    async def _execute_credit_risk_workflow(self, company: str, risk_type: str, horizon: str) -> Dict[str, Any]:
        """Execute credit risk workflow"""
        # Mock credit risk workflow
        return {
            "workflow_type": "credit_risk",
            "company": company,
            "risk_type": risk_type,
            "time_horizon": horizon,
            "risk_assessment": {
                "credit_rating": "BBB",
                "probability_of_default": 0.025,
                "loss_given_default": 0.40,
                "expected_loss": 0.01,
                "risk_score": 0.68
            },
            "key_factors": [
                "Strong cash flow generation",
                "Moderate debt levels",
                "Industry cyclicality",
                "Management quality"
            ],
            "recommendation": "Acceptable credit risk with monitoring"
        }
    
    async def _execute_capital_structure_workflow(self, company: str, analysis_type: str, comparative: bool) -> Dict[str, Any]:
        """Execute capital structure workflow"""
        # Mock capital structure workflow
        return {
            "workflow_type": "capital_structure",
            "company": company,
            "analysis_type": analysis_type,
            "comparative": comparative,
            "capital_structure": {
                "total_debt": 50000000000,
                "total_equity": 80000000000,
                "debt_to_equity": 0.625,
                "debt_to_assets": 0.385,
                "interest_coverage": 8.5,
                "credit_rating": "BBB"
            },
            "analysis": {
                "capital_efficiency": "Good",
                "financial_leverage": "Moderate",
                "flexibility": "Adequate",
                "cost_of_capital": 0.085
            },
            "comparative_analysis": {
                "industry_average_debt_to_equity": 0.75,
                "industry_average_interest_coverage": 7.2,
                "relative_position": "Better than industry average"
            } if comparative else None
        }
    
    def _calculate_price_statistics(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate price statistics"""
        if not historical_data:
            return {}
        
        prices = [data['close'] for data in historical_data]
        
        return {
            "mean_price": sum(prices) / len(prices),
            "min_price": min(prices),
            "max_price": max(prices),
            "volatility": self._calculate_volatility(prices),
            "trend": "upward" if prices[-1] > prices[0] else "downward"
        }
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility"""
        if len(prices) < 2:
            return 0.0
        
        returns = [(prices[i] / prices[i-1]) - 1 for i in range(1, len(prices))]
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        
        return variance ** 0.5
    
    async def _get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Get technical indicators"""
        # Mock technical indicators
        return {
            "rsi": 65.5,
            "macd": {
                "macd": 2.45,
                "signal": 2.10,
                "histogram": 0.35
            },
            "bollinger_bands": {
                "upper": 185.50,
                "middle": 175.25,
                "lower": 165.00
            },
            "moving_averages": {
                "sma_20": 172.50,
                "sma_50": 168.75,
                "ema_20": 173.25
            }
        }
    
    async def _get_trading_signals(self, symbol: str) -> List[Dict[str, Any]]:
        """Get trading signals"""
        # Mock trading signals
        return [
            {
                "signal": "BUY",
                "strength": "Moderate",
                "reason": "RSI oversold and bullish MACD crossover",
                "confidence": 0.75
            }
        ]
    
    async def start_server(self, host: str = "localhost", port: int = 8000):
        """Start the MCP server"""
        logger.info(f"Starting Financial MCP Server on {host}:{port}")
        
        # In production, this would start the actual MCP server
        # For now, we'll simulate server startup
        logger.info("Financial MCP Server started successfully")
        
        # Keep server running
        while True:
            await asyncio.sleep(1)

# Factory function
def get_financial_mcp_server(config: Dict[str, Any] = None) -> FinancialMCPServer:
    """Factory function to get Financial MCP Server"""
    return FinancialMCPServer(config)
