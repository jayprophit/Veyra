"""
Veyra - Main Orchestrator & FastAPI Application
===========================================================
Entry point that wires all components together with REST API.

Usage:
    python main.py              # Start all systems
    python main.py --api        # Start API server only
    python main.py --dashboard  # Start dashboard only
    python main.py --agents     # Start agents only
    python main.py --websocket  # Start WebSocket feeds only
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import structured logging (replaces print statements)
from .monitoring.logging_setup import setup_logging, logger
logger = setup_logging('Veyra')

logger.info("="*60)
logger.info("Veyra - Application Starting")
logger.info("="*60)

# Load environment
load_dotenv()

# Import components (relative imports within app module)
from .database_layer import DatabaseManager, DatabaseConfig
from .autonomous_agent_framework import AgentOrchestrator, GuardrailConfig, create_default_agents
from .websocket_real_time_feeds import DataFeedManager, WebSocketConfig, DataProvider
from .llm_integration_free_tier import LLMManager, LLMConfig

# Import FastAPI
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Import all trading module routers - wrapped in try/except for graceful degradation
try:
    from .api.trading.strategy_builder_api import router as strategy_builder_router
except ImportError:
    strategy_builder_router = None
    logger.warning("Strategy builder API not available")

try:
    from .api.trading.copy_trading_api import router as copy_trading_router
except ImportError:
    copy_trading_router = None
    logger.warning("Copy trading API not available")

try:
    from .api.trading.bot_manager_api import router as bot_manager_router
except ImportError:
    bot_manager_router = None
    logger.warning("Bot manager API not available")

try:
    from .api.trading.metatrader_api import router as metatrader_router
except ImportError:
    metatrader_router = None
    logger.warning("MetaTrader API not available")

try:
    from .api.marketplace.marketplace_api import router as marketplace_router
except ImportError:
    marketplace_router = None
    logger.warning("Marketplace API not available")

try:
    from .api.blockchain.token_economy_api import router as token_economy_router
except ImportError:
    token_economy_router = None
    logger.warning("Token economy API not available")

try:
    from .api.treasury.treasury_api import router as treasury_router
except ImportError:
    treasury_router = None
    logger.warning("Treasury API not available")

TRADING_MODULES_AVAILABLE = any([
    strategy_builder_router,
    copy_trading_router,
    bot_manager_router,
    metatrader_router,
    marketplace_router,
    token_economy_router,
    treasury_router
])


class FinancialMasterSystem:
    """Main system orchestrator."""
    
    def __init__(self):
        self.db = None
        self.agent_orchestrator = None
        self.feed_manager = None
        self.llm_manager = None
        self.running = False
        
    async def initialize(self):
        """Initialize all subsystems."""
        logger.info("="*60)
        logger.info("Veyra - System Initialization")
        logger.info("="*60)
        
        # 1. Database
        logger.info("[1/4] Initializing database...")
        db_config = DatabaseConfig(
            db_type=os.getenv('DB_TYPE', 'sqlite'),
            sqlite_path=os.getenv('SQLITE_PATH', './data/veyra.db')
        )
        self.db = DatabaseManager(db_config)
        logger.info("✓ Database ready")
        
        # 2. LLM Manager (Ollama free tier)
        logger.info("[2/4] Initializing LLM manager...")
        llm_config = LLMConfig(
            primary_provider="ollama",
            ollama_model=os.getenv('OLLAMA_MODEL', 'llama3.2:3b'),
            fallback_to_paid=os.getenv('USE_PAID_LLM', 'false').lower() == 'true',
            openai_api_key=os.getenv('OPENAI_API_KEY') or None
        )
        self.llm_manager = LLMManager(llm_config)
        logger.info("✓ LLM manager ready")
        
        # 3. Agent Orchestrator
        logger.info("[3/4] Initializing agent orchestrator...")
        guardrail_config = GuardrailConfig(
            max_daily_trades=int(os.getenv('MAX_DAILY_TRADES', 5)),
            require_approval_above=float(os.getenv('APPROVAL_THRESHOLD', 10000)),
            fallback_to_paid=llm_config.fallback_to_paid
        )
        self.agent_orchestrator = AgentOrchestrator(guardrail_config)
        create_default_agents(self.agent_orchestrator, self.llm_manager)
        logger.info("✓ Agent orchestrator ready")
        
        # 4. Data Feed Manager
        logger.info("[4/4] Initializing data feeds...")
        ws_config = WebSocketConfig(
            primary_provider=DataProvider.MOCK if os.getenv('USE_MOCK_DATA', 'true').lower() == 'true' else DataProvider.FINNHUB,
            finnhub_api_key=os.getenv('FINNHUB_API_KEY'),
            mock_update_interval=2.0
        )
        self.feed_manager = DataFeedManager(ws_config).setup(ws_config.primary_provider)
        logger.info("✓ Data feeds ready")
        
        logger.info("="*60)
        logger.info("All systems initialized successfully!")
        logger.info("="*60)
    
    async def start(self):
        """Start all subsystems."""
        await self.initialize()
        self.running = True
        
        try:
            # Start everything concurrently
            await asyncio.gather(
                self.agent_orchestrator.start_all(),
                self.feed_manager.start(),
                self._keepalive()
            )
        except KeyboardInterrupt:
            logger.info("\nShutdown requested...")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down systems...")
        self.running = False
        
        if self.agent_orchestrator:
            await self.agent_orchestrator.stop_all()
        
        if self.feed_manager:
            self.feed_manager.stop()
        
        if self.db:
            self.db.close()
        
        logger.info("✓ Shutdown complete")
    
    async def _keepalive(self):
        """Keep main thread alive."""
        while self.running:
            await asyncio.sleep(1)
    
    def get_status(self):
        """Get full system status."""
        return {
            "running": self.running,
            "database": self.db is not None,
            "llm": self.llm_manager.get_status() if self.llm_manager else None,
            "agents": self.agent_orchestrator.get_status() if self.agent_orchestrator else None,
            "timestamp": datetime.now().isoformat()
        }


# Create FastAPI app
def create_fastapi_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Veyra API",
        description="Complete financial management and trading platform API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers that are available
    available_routers = []
    
    if strategy_builder_router:
        app.include_router(strategy_builder_router, prefix="/api/v1")
        available_routers.append("strategy-builder")
    
    if copy_trading_router:
        app.include_router(copy_trading_router, prefix="/api/v1")
        available_routers.append("copy-trading")
    
    if bot_manager_router:
        app.include_router(bot_manager_router, prefix="/api/v1")
        available_routers.append("bot-manager")
    
    if metatrader_router:
        app.include_router(metatrader_router, prefix="/api/v1")
        available_routers.append("metatrader")
    
    if marketplace_router:
        app.include_router(marketplace_router, prefix="/api/v1")
        available_routers.append("marketplace")
    
    if token_economy_router:
        app.include_router(token_economy_router, prefix="/api/v1")
        available_routers.append("token-economy")
    
    if treasury_router:
        app.include_router(treasury_router, prefix="/api/v1")
        available_routers.append("treasury")
    
    if available_routers:
        logger.info(f"✓ Loaded {len(available_routers)} API routers: {', '.join(available_routers)}")
    else:
        logger.info("⚠ No optional trading routers loaded, using core endpoints only")
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": "Veyra API",
            "version": "1.0.0",
            "status": "operational",
            "modules_loaded": TRADING_MODULES_AVAILABLE,
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "trading": "/api/v1/strategy-builder",
                "bots": "/api/v1/bots",
                "copy_trading": "/api/v1/copy-trading",
                "marketplace": "/api/v1/marketplace",
                "tokens": "/api/v1/tokens",
                "treasury": "/api/v1/treasury",
                "metatrader": "/api/v1/metatrader"
            }
        }
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "modules": {
                "trading": TRADING_MODULES_AVAILABLE,
                "ai_employees": True,
                "sentiment": True,
                "contrarian": True
            }
        }
    
    return app


async def start_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Start FastAPI server."""
    import uvicorn
    
    app = create_fastapi_app()
    
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False
    )
    
    server = uvicorn.Server(config)
    logger.info(f"Starting API server on {host}:{port}")
    await server.serve()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Veyra System')
    parser.add_argument('--api', action='store_true', help='Start API server only')
    parser.add_argument('--dashboard', action='store_true', help='Start dashboard server only')
    parser.add_argument('--agents', action='store_true', help='Start agents only')
    parser.add_argument('--websocket', action='store_true', help='Start WebSocket feeds only')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--host', default='0.0.0.0', help='API server host')
    parser.add_argument('--port', type=int, default=8000, help='API server port')
    args = parser.parse_args()
    
    # Start API server only
    if args.api:
        await start_api_server(args.host, args.port)
        return
    
    system = FinancialMasterSystem()
    
    if args.status:
        print(json.dumps(system.get_status(), indent=2))
        return
    
    # Start everything including API
    try:
        # Start API in background
        api_task = asyncio.create_task(start_api_server(args.host, args.port))
        
        # Start main system
        await system.start()
        
    except Exception as e:
        logger.error(f"System error: {e}")
        raise


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                FINANCIAL MASTER - 5 STAR SYSTEM                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Multi-Agent AI | Real-time Data | Tax Optimization | FIRE       ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
