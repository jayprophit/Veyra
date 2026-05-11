"""
Master Orchestrator
===================
Central system controller that coordinates all modules:
- Event routing between components
- State management
- Health monitoring
- Configuration management
- Lifecycle management
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class ModuleStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    DEGRADED = "degraded"


@dataclass
class ModuleInfo:
    name: str
    status: ModuleStatus
    version: str
    dependencies: List[str] = field(default_factory=list)
    health_score: float = 1.0
    last_heartbeat: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    """Async event routing between modules."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_history: List[Dict] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Handler subscribed to {event_type}")
    
    async def publish(self, event_type: str, data: Any, source: str = "system"):
        """Publish event to all subscribers."""
        event = {
            "type": event_type,
            "data": data,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "id": f"evt_{datetime.now().timestamp()}"
        }
        
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        handlers = self._handlers.get(event_type, [])
        
        if handlers:
            await asyncio.gather(
                *[self._safe_call(h, event) for h in handlers],
                return_exceptions=True
            )
    
    async def _safe_call(self, handler: Callable, event: Dict):
        """Safely call handler with error handling."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Event handler error: {e}")


class MasterOrchestrator:
    """
    Central orchestrator for Veyra system.
    Coordinates all modules and manages system state.
    """
    
    def __init__(self):
        self.event_bus = EventBus()
        self.modules: Dict[str, ModuleInfo] = {}
        self.state: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}
        self._running = False
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Module instances (lazy loaded)
        self._instances: Dict[str, Any] = {}
    
    def register_module(
        self,
        name: str,
        version: str = "1.0.0",
        dependencies: List[str] = None,
        metadata: Dict = None
    ):
        """Register a module with the orchestrator."""
        self.modules[name] = ModuleInfo(
            name=name,
            status=ModuleStatus.STOPPED,
            version=version,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        logger.info(f"Module registered: {name} v{version}")
    
    def set_module_instance(self, name: str, instance: Any):
        """Set module instance for access by other modules."""
        self._instances[name] = instance
    
    def get_module(self, name: str) -> Optional[Any]:
        """Get module instance."""
        return self._instances.get(name)
    
    async def start(self):
        """Start the orchestrator and all modules."""
        logger.info("Starting Master Orchestrator...")
        self._running = True
        
        # Start modules in dependency order
        started = set()
        
        for name in self.modules:
            if name not in started:
                await self._start_module_recursive(name, started)
        
        # Start health checks
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        await self.event_bus.publish("system.started", {"modules": list(self.modules.keys())})
        logger.info("Master Orchestrator started successfully")
    
    async def _start_module_recursive(self, name: str, started: set):
        """Start module and its dependencies."""
        if name in started:
            return
        
        module = self.modules[name]
        
        # Start dependencies first
        for dep in module.dependencies:
            if dep not in started:
                await self._start_module_recursive(dep, started)
        
        # Start this module
        module.status = ModuleStatus.STARTING
        logger.info(f"Starting module: {name}")
        
        try:
            # Initialize module
            module.status = ModuleStatus.RUNNING
            module.last_heartbeat = datetime.now()
            started.add(name)
            
            await self.event_bus.publish(f"module.{name}.started", {"version": module.version})
            
        except Exception as e:
            module.status = ModuleStatus.ERROR
            logger.error(f"Failed to start module {name}: {e}")
            raise
    
    async def stop(self):
        """Stop all modules."""
        logger.info("Stopping Master Orchestrator...")
        self._running = False
        
        if self._health_check_task:
            self._health_check_task.cancel()
        
        # Stop modules in reverse dependency order
        for name in reversed(list(self.modules.keys())):
            module = self.modules[name]
            if module.status == ModuleStatus.RUNNING:
                module.status = ModuleStatus.STOPPED
                logger.info(f"Stopped module: {name}")
        
        await self.event_bus.publish("system.stopped", {})
        logger.info("Master Orchestrator stopped")
    
    async def _health_check_loop(self):
        """Periodic health check of all modules."""
        while self._running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for name, module in self.modules.items():
                    if module.status == ModuleStatus.RUNNING:
                        # Check if heartbeat is stale
                        if module.last_heartbeat:
                            stale = (datetime.now() - module.last_heartbeat).seconds > 60
                            if stale:
                                module.status = ModuleStatus.DEGRADED
                                logger.warning(f"Module {name} heartbeat stale")
                        
                        await self.event_bus.publish(
                            f"module.{name}.health",
                            {"status": module.status.value, "score": module.health_score}
                        )
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    def update_module_health(self, name: str, score: float):
        """Update module health score."""
        if name in self.modules:
            self.modules[name].health_score = score
            self.modules[name].last_heartbeat = datetime.now()
    
    def get_system_status(self) -> Dict:
        """Get complete system status."""
        return {
            "running": self._running,
            "modules": {
                name: {
                    "status": info.status.value,
                    "version": info.version,
                    "health": info.health_score,
                    "last_heartbeat": info.last_heartbeat.isoformat() if info.last_heartbeat else None
                }
                for name, info in self.modules.items()
            },
            "event_bus": {
                "subscribers": len(self.event_bus._handlers),
                "history_size": len(self.event_bus._event_history)
            }
        }
    
    def save_state(self, filepath: str):
        """Save system state to file."""
        state = {
            "config": self.config,
            "module_status": {
                name: info.status.value
                for name, info in self.modules.items()
            },
            "saved_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"State saved to {filepath}")
    
    def load_state(self, filepath: str):
        """Load system state from file."""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.config = state.get("config", {})
            logger.info(f"State loaded from {filepath}")
            
        except FileNotFoundError:
            logger.warning(f"State file not found: {filepath}")


# Global orchestrator instance
_orchestrator: Optional[MasterOrchestrator] = None


def get_orchestrator() -> MasterOrchestrator:
    """Get or create global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MasterOrchestrator()
    return _orchestrator


# Example usage
if __name__ == "__main__":
    async def main():
        orch = get_orchestrator()
        
        # Register modules
        orch.register_module("market_data", "1.0.0", [], {"type": "data_feed"})
        orch.register_module("risk_engine", "1.0.0", ["market_data"])
        orch.register_module("execution", "1.0.0", ["market_data", "risk_engine"])
        orch.register_module("ai_analysis", "1.0.0", ["market_data"])
        
        # Subscribe to events
        async def on_market_data(event):
            print(f"Market data received: {event['data']}")
        
        orch.event_bus.subscribe("market.data", on_market_data)
        
        # Start system
        await orch.start()
        
        # Publish test event
        await orch.event_bus.publish("market.data", {"price": 150.25, "symbol": "AAPL"})
        
        # Check status
        status = orch.get_system_status()
        print(f"\nSystem Status: {json.dumps(status, indent=2)}")
        
        # Stop
        await asyncio.sleep(1)
        await orch.stop()
    
    asyncio.run(main())
