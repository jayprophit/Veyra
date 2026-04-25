"""
Financial Master - Main Orchestrator
====================================
Entry point that wires all components together.

Usage:
    python main.py              # Start all systems
    python main.py --dashboard  # Start dashboard only
    python main.py --agents     # Start agents only
    python main.py --websocket  # Start WebSocket feeds only
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'logs/financial_master_{datetime.now():%Y%m%d}.log')
    ]
)
logger = logging.getLogger('FinancialMaster')

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Load environment
load_dotenv()

# Import components
from database_layer import DatabaseManager, DatabaseConfig
from autonomous_agent_framework import AgentOrchestrator, GuardrailConfig, create_default_agents
from websocket_real_time_feeds import DataFeedManager, WebSocketConfig, DataProvider
from llm_integration_free_tier import LLMManager, LLMConfig


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
        logger.info("Financial Master - System Initialization")
        logger.info("="*60)
        
        # 1. Database
        logger.info("[1/4] Initializing database...")
        db_config = DatabaseConfig(
            db_type=os.getenv('DB_TYPE', 'sqlite'),
            sqlite_path=os.getenv('SQLITE_PATH', './data/financial_master.db')
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


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Financial Master System')
    parser.add_argument('--dashboard', action='store_true', help='Start dashboard server only')
    parser.add_argument('--agents', action='store_true', help='Start agents only')
    parser.add_argument('--websocket', action='store_true', help='Start WebSocket feeds only')
    parser.add_argument('--status', action='store_true', help='Show system status')
    args = parser.parse_args()
    
    system = FinancialMasterSystem()
    
    if args.status:
        print(json.dumps(system.get_status(), indent=2))
        return
    
    # For now, start everything (can be modularized later)
    try:
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
