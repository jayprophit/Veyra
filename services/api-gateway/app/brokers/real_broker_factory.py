"""
Real Broker API Factory - Production Implementations
Replaces mock implementations with live trading capabilities
"""

from typing import Dict, List, Optional, Union
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RealBrokerFactory:
    """Factory for creating real broker clients"""
    
    @staticmethod
    def create_ibkr_client(paper: bool = True) -> Optional['InteractiveBrokersReal']:
        """Create real Interactive Brokers client"""
        try:
            from brokers.ibkr_live import InteractiveBrokersLive
            api_key = os.getenv('IBKR_API_KEY')
            if not api_key:
                logger.error("IBKR_API_KEY not set in environment")
                return None
            return InteractiveBrokersLive(api_key=api_key, paper=paper)
        except Exception as e:
            logger.error(f"Failed to create IBKR client: {e}")
            return None
    
    @staticmethod
    def create_coinbase_client() -> Optional['CoinbaseReal']:
        """Create real Coinbase Pro client"""
        try:
            from brokers.coinbase_live import CoinbaseLive
            api_key = os.getenv('COINBASE_API_KEY')
            api_secret = os.getenv('COINBASE_API_SECRET')
            if not api_key or not api_secret:
                logger.error("Coinbase API credentials not set")
                return None
            return CoinbaseLive(api_key=api_key, api_secret=api_secret)
        except Exception as e:
            logger.error(f"Failed to create Coinbase client: {e}")
            return None
    
    @staticmethod
    def create_alpaca_client(paper: bool = True) -> Optional['AlpacaReal']:
        """Create real Alpaca client"""
        try:
            from brokers.alpaca_broker import AlpacaBroker
            api_key = os.getenv('ALPACA_API_KEY')
            api_secret = os.getenv('ALPACA_API_SECRET')
            if not api_key or not api_secret:
                logger.error("Alpaca API credentials not set")
                return None
            return AlpacaBroker(api_key=api_key, secret_key=api_secret, paper=paper)
        except Exception as e:
            logger.error(f"Failed to create Alpaca client: {e}")
            return None


class BrokerManager:
    """Manage multiple real broker connections"""
    
    def __init__(self):
        self.brokers: Dict[str, any] = {}
        self.active_broker: Optional[str] = None
    
    async def connect_all(self):
        """Connect to all configured brokers"""
        # Interactive Brokers
        ibkr = RealBrokerFactory.create_ibkr_client(paper=True)
        if ibkr:
            connected = await ibkr.connect()
            if connected:
                self.brokers['ibkr'] = ibkr
                logger.info("IBKR connected successfully")
        
        # Coinbase
        coinbase = RealBrokerFactory.create_coinbase_client()
        if coinbase:
            connected = await coinbase.connect()
            if connected:
                self.brokers['coinbase'] = coinbase
                logger.info("Coinbase connected successfully")
        
        # Alpaca
        alpaca = RealBrokerFactory.create_alpaca_client(paper=True)
        if alpaca:
            connected = await alpaca.connect()
            if connected:
                self.brokers['alpaca'] = alpaca
                logger.info("Alpaca connected successfully")
        
        if self.brokers:
            self.active_broker = list(self.brokers.keys())[0]
        
        return len(self.brokers) > 0
    
    async def get_account_summary(self, broker: Optional[str] = None) -> Dict:
        """Get account summary from specified or active broker"""
        broker_key = broker or self.active_broker
        if not broker_key or broker_key not in self.brokers:
            return {'error': 'Broker not connected'}
        
        return await self.brokers[broker_key].get_account_summary()
    
    async def place_order(self, symbol: str, action: str, quantity: float,
                         broker: Optional[str] = None, **kwargs) -> Dict:
        """Place order through specified or active broker"""
        broker_key = broker or self.active_broker
        if not broker_key or broker_key not in self.brokers:
            return {'error': 'Broker not connected', 'status': 'failed'}
        
        return await self.brokers[broker_key].place_order(
            symbol=symbol,
            action=action,
            quantity=quantity,
            **kwargs
        )
    
    async def get_positions(self, broker: Optional[str] = None) -> List[Dict]:
        """Get positions from specified or active broker"""
        broker_key = broker or self.active_broker
        if not broker_key or broker_key not in self.brokers:
            return []
        
        return await self.brokers[broker_key].get_positions()
    
    def get_connected_brokers(self) -> List[str]:
        """Get list of connected broker names"""
        return list(self.brokers.keys())
    
    async def disconnect_all(self):
        """Disconnect all brokers"""
        for name, broker in self.brokers.items():
            try:
                if hasattr(broker, 'disconnect'):
                    await broker.disconnect()
                logger.info(f"Disconnected from {name}")
            except Exception as e:
                logger.warning(f"Error disconnecting {name}: {e}")
        
        self.brokers.clear()
        self.active_broker = None
