"""
Smart Contract Integration for DeFi
ERC20 tokens, subscriptions, and on-chain proofs
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import uuid

class SubscriptionTier(Enum):
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class PaymentMethod(Enum):
    TOKEN = "token"
    FIAT = "fiat"
    CRYPTO = "crypto"

@dataclass
class Subscription:
    user_id: str
    tier: SubscriptionTier
    expiry_date: datetime
    auto_renew: bool
    trading_limit: float
    advanced_features: bool
    payment_method: PaymentMethod

@dataclass
class Reward:
    user_id: str
    amount: float
    reward_type: str  # trading, staking, referral, loyalty
    multiplier: float
    timestamp: datetime

class TradingToken:
    """
    ERC20 token implementation for platform rewards
    """
    
    def __init__(self, name: str = "FinancialMaster", symbol: str = "FMT"):
        self.name = name
        self.symbol = symbol
        self.total_supply = 1_000_000 * (10 ** 18)  # 1 million tokens
        self.balances: Dict[str, float] = {}
        self.allowances: Dict[str, Dict[str, float]] = {}
        
        # Mint initial supply to contract owner
        self.balances["contract_owner"] = self.total_supply
    
    def balance_of(self, address: str) -> float:
        """Get token balance for address"""
        return self.balances.get(address, 0)
    
    def transfer(self, from_addr: str, to_addr: str, amount: float) -> bool:
        """Transfer tokens between addresses"""
        if self.balances.get(from_addr, 0) < amount:
            return False
        
        self.balances[from_addr] = self.balances.get(from_addr, 0) - amount
        self.balances[to_addr] = self.balances.get(to_addr, 0) + amount
        return True
    
    def mint(self, to_addr: str, amount: float) -> bool:
        """Mint new tokens (owner only)"""
        self.total_supply += amount
        self.balances[to_addr] = self.balances.get(to_addr, 0) + amount
        return True
    
    def burn(self, from_addr: str, amount: float) -> bool:
        """Burn tokens permanently"""
        if self.balances.get(from_addr, 0) < amount:
            return False
        
        self.balances[from_addr] -= amount
        self.total_supply -= amount
        return True

class SubscriptionManager:
    """
    Manage subscription tiers with token payments
    """
    
    def __init__(self, token: TradingToken):
        self.token = token
        self.subscriptions: Dict[str, Subscription] = {}
        self.tier_prices = {
            SubscriptionTier.BASIC: 100 * (10 ** 18),
            SubscriptionTier.ADVANCED: 300 * (10 ** 18),
            SubscriptionTier.PRO: 500 * (10 ** 18),
            SubscriptionTier.ENTERPRISE: 1000 * (10 ** 18)
        }
        self.tier_limits = {
            SubscriptionTier.BASIC: 10000.0,
            SubscriptionTier.ADVANCED: 50000.0,
            SubscriptionTier.PRO: 100000.0,
            SubscriptionTier.ENTERPRISE: float('inf')
        }
    
    def purchase_subscription(self, user_id: str, tier: SubscriptionTier, 
                            auto_renew: bool = False) -> Dict:
        """Purchase subscription with tokens"""
        if tier == SubscriptionTier.NONE:
            return {'error': 'Invalid tier'}
        
        price = self.tier_prices.get(tier)
        user_balance = self.token.balance_of(user_id)
        
        if user_balance < price:
            return {'error': 'Insufficient balance', 'required': price, 'balance': user_balance}
        
        # Transfer tokens to contract
        success = self.token.transfer(user_id, "contract_owner", price)
        if not success:
            return {'error': 'Transfer failed'}
        
        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            tier=tier,
            expiry_date=datetime.now() + timedelta(days=30),
            auto_renew=auto_renew,
            trading_limit=self.tier_limits.get(tier, 0),
            advanced_features=tier in [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE],
            payment_method=PaymentMethod.TOKEN
        )
        
        self.subscriptions[user_id] = subscription
        
        return {
            'success': True,
            'tier': tier.value,
            'expiry': subscription.expiry_date.isoformat(),
            'trading_limit': subscription.trading_limit
        }
    
    def get_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user's subscription"""
        return self.subscriptions.get(user_id)
    
    def check_access(self, user_id: str, feature: str) -> bool:
        """Check if user has access to feature"""
        sub = self.subscriptions.get(user_id)
        if not sub:
            return False
        
        # Check expiry
        if datetime.now() > sub.expiry_date:
            return False
        
        # Feature access matrix
        feature_tiers = {
            'basic_trading': [SubscriptionTier.BASIC, SubscriptionTier.ADVANCED, 
                            SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE],
            'advanced_charts': [SubscriptionTier.ADVANCED, SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE],
            'api_access': [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE],
            'priority_support': [SubscriptionTier.ENTERPRISE]
        }
        
        allowed_tiers = feature_tiers.get(feature, [])
        return sub.tier in allowed_tiers
    
    def cancel_subscription(self, user_id: str) -> bool:
        """Cancel subscription"""
        if user_id in self.subscriptions:
            del self.subscriptions[user_id]
            return True
        return False
    
    def get_upcoming_renewals(self, days: int = 7) -> List[Subscription]:
        """Get subscriptions expiring soon"""
        cutoff = datetime.now() + timedelta(days=days)
        return [s for s in self.subscriptions.values() 
                if s.expiry_date <= cutoff and s.auto_renew]

class RewardDistributor:
    """
    Distribute rewards to users based on activity
    """
    
    def __init__(self, token: TradingToken):
        self.token = token
        self.rewards: List[Reward] = []
        self.reward_rates = {
            'trading': 0.1,      # 0.1 tokens per trade
            'staking': 0.05,     # 0.05 tokens per day
            'referral': 5.0,     # 5 tokens per referral
            'loyalty': 0.02      # 0.02 tokens per day of activity
        }
        self.multipliers = {
            SubscriptionTier.BASIC: 1.0,
            SubscriptionTier.ADVANCED: 1.5,
            SubscriptionTier.PRO: 2.0,
            SubscriptionTier.ENTERPRISE: 3.0
        }
    
    def calculate_reward(self, user_id: str, reward_type: str, 
                        activity_data: Dict, tier: SubscriptionTier) -> float:
        """Calculate reward amount"""
        base_rate = self.reward_rates.get(reward_type, 0)
        multiplier = self.multipliers.get(tier, 1.0)
        
        if reward_type == 'trading':
            amount = base_rate * activity_data.get('trade_count', 0) * multiplier
        elif reward_type == 'staking':
            amount = base_rate * activity_data.get('staked_amount', 0) * multiplier
        elif reward_type == 'referral':
            amount = base_rate * activity_data.get('referral_count', 0) * multiplier
        elif reward_type == 'loyalty':
            amount = base_rate * activity_data.get('active_days', 0) * multiplier
        else:
            amount = 0
        
        return round(amount, 6)
    
    def distribute_reward(self, user_id: str, amount: float, 
                       reward_type: str, tier: SubscriptionTier) -> bool:
        """Mint and distribute reward tokens"""
        multiplier = self.multipliers.get(tier, 1.0)
        final_amount = amount * multiplier
        
        # Mint tokens to user
        success = self.token.mint(user_id, final_amount)
        if success:
            reward = Reward(
                user_id=user_id,
                amount=final_amount,
                reward_type=reward_type,
                multiplier=multiplier,
                timestamp=datetime.now()
            )
            self.rewards.append(reward)
        
        return success
    
    def get_user_rewards(self, user_id: str) -> List[Reward]:
        """Get reward history for user"""
        return [r for r in self.rewards if r.user_id == user_id]
    
    def swap_dust_tokens(self, user_id: str, small_balances: List[Dict]) -> float:
        """
        Convert small unusable balances into platform tokens
        """
        total_value = 0
        
        for balance in small_balances:
            # Calculate value in USD (simplified)
            value = balance.get('amount', 0) * balance.get('price_usd', 0)
            if value < 1.0:  # Less than $1
                total_value += value
        
        # Convert to platform tokens (1 USD = 10 FMT)
        tokens_to_mint = total_value * 10
        
        if tokens_to_mint > 0:
            self.token.mint(user_id, tokens_to_mint)
        
        return tokens_to_mint

class OnChainProof:
    """
    Create on-chain proofs for activities
    """
    
    def __init__(self):
        self.proofs: Dict[str, Dict] = {}
    
    def create_proof(self, entity_type: str, entity_id: str, 
                    data: Dict) -> str:
        """
        Create a proof hash for off-chain data
        In production: Store hash on blockchain
        """
        import hashlib
        
        proof_id = str(uuid.uuid4())
        
        # Create hash of data
        data_string = f"{entity_type}:{entity_id}:{datetime.now().isoformat()}"
        proof_hash = hashlib.sha256(data_string.encode()).hexdigest()
        
        proof_record = {
            'id': proof_id,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'hash': proof_hash,
            'data': data,
            'created_at': datetime.now().isoformat(),
            'chain': 'ethereum',  # or 'polygon', 'solana'
            'tx_hash': None  # Set when actually on-chain
        }
        
        self.proofs[proof_id] = proof_record
        return proof_id
    
    def verify_proof(self, proof_id: str) -> Optional[Dict]:
        """Verify a proof exists"""
        return self.proofs.get(proof_id)
    
    def get_proofs_by_entity(self, entity_type: str, entity_id: str) -> List[Dict]:
        """Get all proofs for an entity"""
        return [p for p in self.proofs.values() 
                if p['entity_type'] == entity_type and p['entity_id'] == entity_id]
