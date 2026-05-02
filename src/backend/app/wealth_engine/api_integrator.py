"""API Integrator - Connects to exchanges, banks, and platforms"""
from typing import Dict, Optional
from abc import ABC, abstractmethod

class PlatformAPI(ABC):
    """Abstract base for platform connections"""
    
    @abstractmethod
    def connect(self, credentials: Dict) -> bool:
        pass
    
    @abstractmethod
    def get_balance(self) -> float:
        pass
    
    @abstractmethod
    def execute_trade(self, action: str, amount: float, asset: str) -> Dict:
        pass

class CoinbaseAPI(PlatformAPI):
    """Coinbase Pro/Retail API integration"""
    
    def connect(self, credentials: Dict) -> bool:
        # Placeholder for actual API connection
        return True
    
    def get_balance(self) -> float:
        return 0.0  # Placeholder
    
    def execute_trade(self, action: str, amount: float, asset: str) -> Dict:
        return {
            'platform': 'coinbase',
            'action': action,
            'amount': amount,
            'asset': asset,
            'status': 'simulated'
        }
    
    def stake(self, amount: float, asset: str = 'ETH') -> Dict:
        """Stake crypto for yield"""
        return {
            'action': 'stake',
            'amount': amount,
            'asset': asset,
            'apy': 0.04,
            'status': 'simulated'
        }

class BinanceAPI(PlatformAPI):
    """Binance API integration"""
    
    def connect(self, credentials: Dict) -> bool:
        return True
    
    def get_balance(self) -> float:
        return 0.0
    
    def execute_trade(self, action: str, amount: float, asset: str) -> Dict:
        return {
            'platform': 'binance',
            'action': action,
            'amount': amount,
            'asset': asset,
            'status': 'simulated'
        }
    
    def start_grid_bot(self, pair: str, lower: float, upper: float, grids: int) -> Dict:
        """Start grid trading bot"""
        return {
            'strategy': 'grid',
            'pair': pair,
            'range': [lower, upper],
            'grids': grids,
            'status': 'active'
        }

class Trading212API(PlatformAPI):
    """Trading 212 API integration"""
    
    def connect(self, credentials: Dict) -> bool:
        return True
    
    def buy_etf(self, ticker: str, amount: float) -> Dict:
        """Buy fractional ETF"""
        return {
            'platform': 'trading212',
            'action': 'buy',
            'ticker': ticker,
            'amount': amount,
            'status': 'executed'
        }

class ChipAPI(PlatformAPI):
    """Chip savings account integration"""
    
    def connect(self, credentials: Dict) -> bool:
        return True
    
    def deposit(self, amount: float) -> Dict:
        return {
            'platform': 'chip',
            'action': 'deposit',
            'amount': amount,
            'apy': 0.046
        }

class APIIntegrator:
    """Manages all platform connections"""
    
    def __init__(self):
        self.connections = {
            'coinbase': CoinbaseAPI(),
            'binance': BinanceAPI(),
            'trading212': Trading212API(),
            'chip': ChipAPI()
        }
        self.active_connections = {}
    
    def connect_all(self, credentials: Dict) -> Dict:
        """Connect to all configured platforms"""
        results = {}
        
        for name, api in self.connections.items():
            creds = credentials.get(name)
            if creds:
                success = api.connect(creds)
                if success:
                    self.active_connections[name] = api
                    results[name] = 'connected'
                else:
                    results[name] = 'failed'
            else:
                results[name] = 'no_credentials'
        
        return results
    
    def execute_allocation(self, allocation: Dict) -> Dict:
        """Execute single allocation via appropriate API"""
        platform = allocation.get('platform', allocation.get('pot'))
        
        if platform not in self.active_connections:
            return {'status': 'error', 'message': f'{platform} not connected'}
        
        api = self.active_connections[platform]
        strategy = allocation.get('module') or allocation.get('strategy')
        amount = allocation['amount']
        
        # Route to appropriate method
        if strategy in ['eth_staking', 'crypto_staking'] and hasattr(api, 'stake'):
            return api.stake(amount)
        
        elif strategy in ['grid_bots', 'grid'] and hasattr(api, 'start_grid_bot'):
            return api.start_grid_bot('BTC/USDT', 20000, 60000, 20)
        
        elif strategy in ['gold_etf', 'index'] and hasattr(api, 'buy_etf'):
            ticker = 'SGLN' if 'gold' in strategy else 'VWRL'
            return api.buy_etf(ticker, amount)
        
        elif strategy in ['high_yield_savings', 'savings'] and hasattr(api, 'deposit'):
            return api.deposit(amount)
        
        else:
            return api.execute_trade('buy', amount, strategy)
    
    def get_all_balances(self) -> Dict:
        """Get balances across all connected platforms"""
        balances = {}
        
        for name, api in self.active_connections.items():
            try:
                balances[name] = api.get_balance()
            except:
                balances[name] = None
        
        return balances
