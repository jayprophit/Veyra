"""Multi-Account Management System."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class AccountType(Enum):
    SPOT = "spot"
    MARGIN = "margin"
    FUTURES = "futures"
    PAPER = "paper"
    SAVINGS = "savings"

@dataclass
class TradingAccount:
    id: str
    user_id: str
    name: str
    account_type: AccountType
    balances: Dict[str, float]
    total_value_usd: float
    created_at: datetime
    api_keys: Dict[str, str]
    risk_limits: Dict[str, float]
    is_active: bool = True
    is_default: bool = False

class MultiAccountManager:
    """Manage multiple trading accounts per user."""
    
    def __init__(self):
        self.accounts: Dict[str, TradingAccount] = {}
        self.user_accounts: Dict[str, List[str]] = {}
        self.account_counter = 0
    
    def _generate_id(self) -> str:
        self.account_counter += 1
        return f"acc_{self.account_counter}_{datetime.now().strftime('%H%M%S')}"
    
    async def create_account(self, user_id: str, name: str, 
                            account_type: AccountType,
                            risk_limits: Optional[Dict] = None) -> TradingAccount:
        """Create a new trading account."""
        account_id = self._generate_id()
        
        # Set first account as default
        is_default = len(self.user_accounts.get(user_id, [])) == 0
        
        account = TradingAccount(
            id=account_id,
            user_id=user_id,
            name=name,
            account_type=account_type,
            balances={'USD': 0.0, 'BTC': 0.0, 'ETH': 0.0},
            total_value_usd=0.0,
            created_at=datetime.now(),
            api_keys={},
            risk_limits=risk_limits or {
                'max_position_size_pct': 10.0,
                'max_daily_loss_pct': 5.0,
                'max_leverage': 1.0 if account_type != AccountType.FUTURES else 10.0
            },
            is_default=is_default
        )
        
        self.accounts[account_id] = account
        
        if user_id not in self.user_accounts:
            self.user_accounts[user_id] = []
        self.user_accounts[user_id].append(account_id)
        
        logger.info(f"Created {account_type.value} account {account_id} for user {user_id}")
        return account
    
    async def get_account(self, account_id: str) -> Optional[TradingAccount]:
        """Get account by ID."""
        return self.accounts.get(account_id)
    
    async def get_user_accounts(self, user_id: str) -> List[TradingAccount]:
        """Get all accounts for a user."""
        account_ids = self.user_accounts.get(user_id, [])
        return [self.accounts[aid] for aid in account_ids if aid in self.accounts]
    
    async def update_balance(self, account_id: str, asset: str, 
                            amount: float) -> bool:
        """Update account balance."""
        account = self.accounts.get(account_id)
        if not account:
            return False
        
        account.balances[asset] = account.balances.get(asset, 0) + amount
        
        # Recalculate total USD value (simplified)
        account.total_value_usd = sum(
            balance * (1000 if asset == 'BTC' else 2000 if asset == 'ETH' else 1)
            for asset, balance in account.balances.items()
        )
        
        return True
    
    async def transfer_between_accounts(self, user_id: str, 
                                       from_account: str, to_account: str,
                                       asset: str, amount: float) -> Dict[str, Any]:
        """Transfer assets between user accounts."""
        from_acc = self.accounts.get(from_account)
        to_acc = self.accounts.get(to_account)
        
        if not from_acc or not to_acc:
            return {'success': False, 'error': 'Account not found'}
        
        if from_acc.user_id != user_id or to_acc.user_id != user_id:
            return {'success': False, 'error': 'Unauthorized'}
        
        current_balance = from_acc.balances.get(asset, 0)
        if current_balance < amount:
            return {'success': False, 'error': 'Insufficient balance'}
        
        # Execute transfer
        from_acc.balances[asset] = current_balance - amount
        to_acc.balances[asset] = to_acc.balances.get(asset, 0) + amount
        
        return {
            'success': True,
            'from_account': from_account,
            'to_account': to_account,
            'asset': asset,
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        }
    
    async def set_default_account(self, user_id: str, account_id: str) -> bool:
        """Set default account for user."""
        if account_id not in self.accounts:
            return False
        
        account = self.accounts[account_id]
        if account.user_id != user_id:
            return False
        
        # Unset previous default
        for acc_id in self.user_accounts.get(user_id, []):
            if acc_id in self.accounts:
                self.accounts[acc_id].is_default = False
        
        account.is_default = True
        return True
    
    async def get_account_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of all user accounts."""
        accounts = await self.get_user_accounts(user_id)
        
        total_value = sum(acc.total_value_usd for acc in accounts)
        
        by_type = {}
        for acc in accounts:
            type_name = acc.account_type.value
            if type_name not in by_type:
                by_type[type_name] = {'count': 0, 'value': 0}
            by_type[type_name]['count'] += 1
            by_type[type_name]['value'] += acc.total_value_usd
        
        return {
            'user_id': user_id,
            'total_accounts': len(accounts),
            'total_value_usd': total_value,
            'accounts_by_type': by_type,
            'accounts': [{
                'id': acc.id,
                'name': acc.name,
                'type': acc.account_type.value,
                'value_usd': acc.total_value_usd,
                'is_default': acc.is_default,
                'balances': acc.balances
            } for acc in accounts]
        }
    
    async def check_risk_limits(self, account_id: str, 
                               proposed_trade: Dict) -> Dict[str, Any]:
        """Check if proposed trade violates risk limits."""
        account = self.accounts.get(account_id)
        if not account:
            return {'allowed': False, 'error': 'Account not found'}
        
        limits = account.risk_limits
        trade_value = proposed_trade['quantity'] * proposed_trade['price']
        
        # Check position size limit
        max_position = account.total_value_usd * (limits['max_position_size_pct'] / 100)
        if trade_value > max_position:
            return {
                'allowed': False,
                'reason': f'Trade value (${trade_value:.2f}) exceeds max position size (${max_position:.2f})'
            }
        
        return {'allowed': True, 'limits': limits}

account_manager = MultiAccountManager()
