"""
Dual-Token Economy System for Veyra
Work Token (WT) and Governance Token (GT) Implementation

Features:
- Work Token (WT) - utility token for platform access and rewards
- Governance Token (GT) - voting rights and protocol governance
- Token minting, burning, and distribution
- Staking mechanisms
- Anti-whale protection
- Reward distribution
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """Token types"""
    WORK = "wt"  # Work Token - utility
    GOVERNANCE = "gt"  # Governance Token - voting


class RewardType(Enum):
    """Types of rewards"""
    TRADING = "trading"  # Rewards from trading activity
    STAKING = "staking"  # Rewards from staking tokens
    REFERRAL = "referral"  # Referral rewards
    CONTRIBUTION = "contribution"  # Platform contributions
    LIQUIDITY = "liquidity"  # Liquidity provision


class StakingTier(Enum):
    """Staking tiers with different benefits"""
    BRONZE = "bronze"  # 100-1,000 tokens
    SILVER = "silver"  # 1,000-10,000 tokens
    GOLD = "gold"  # 10,000-50,000 tokens
    PLATINUM = "platinum"  # 50,000-100,000 tokens
    DIAMOND = "diamond"  # 100,000+ tokens


@dataclass
class TokenConfig:
    """Token configuration"""
    name: str
    symbol: str
    decimals: int = 18
    total_supply: float = 0.0
    max_supply: float = 100_000_000.0  # 100 million
    
    # Distribution
    team_allocation_pct: float = 15.0
    community_allocation_pct: float = 40.0
    ecosystem_allocation_pct: float = 25.0
    liquidity_allocation_pct: float = 15.0
    reserve_allocation_pct: float = 5.0
    
    # Features
    burnable: bool = True
    mintable: bool = True
    pausable: bool = False
    
    def __post_init__(self):
        self.total_supply = 0.0  # Start with 0, mint as needed


@dataclass
class TokenBalance:
    """User token balance"""
    user_id: str
    wt_balance: float = 0.0
    gt_balance: float = 0.0
    wt_staked: float = 0.0
    gt_staked: float = 0.0
    wt_rewards_pending: float = 0.0
    gt_rewards_pending: float = 0.0
    
    # Timestamps
    last_claimed: Optional[datetime] = None
    first_staked: Optional[datetime] = None
    
    def get_tier(self) -> StakingTier:
        """Calculate staking tier based on staked WT"""
        staked = self.wt_staked
        if staked >= 100_000:
            return StakingTier.DIAMOND
        elif staked >= 50_000:
            return StakingTier.PLATINUM
        elif staked >= 10_000:
            return StakingTier.GOLD
        elif staked >= 1_000:
            return StakingTier.SILVER
        else:
            return StakingTier.BRONZE
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'balances': {
                'wt_available': self.wt_balance,
                'gt_available': self.gt_balance,
                'wt_staked': self.wt_staked,
                'gt_staked': self.gt_staked,
                'wt_total': self.wt_balance + self.wt_staked,
                'gt_total': self.gt_balance + self.gt_staked
            },
            'rewards_pending': {
                'wt': self.wt_rewards_pending,
                'gt': self.gt_rewards_pending
            },
            'staking_tier': self.get_tier().value,
            'timestamps': {
                'last_claimed': self.last_claimed.isoformat() if self.last_claimed else None,
                'first_staked': self.first_staked.isoformat() if self.first_staked else None
            }
        }


@dataclass
class StakingPosition:
    """Individual staking position"""
    id: str
    user_id: str
    token_type: TokenType
    amount: float
    start_date: datetime
    duration_days: int  # 30, 90, 180, 365
    apy: float
    
    # Rewards
    rewards_earned: float = 0.0
    last_compound: datetime = None
    
    # Status
    locked: bool = True
    maturity_date: datetime = None
    withdrawn: bool = False
    
    def __post_init__(self):
        if self.maturity_date is None:
            self.maturity_date = self.start_date + timedelta(days=self.duration_days)
        if self.last_compound is None:
            self.last_compound = self.start_date
    
    def calculate_rewards(self, current_time: datetime = None) -> float:
        """Calculate accrued rewards"""
        if current_time is None:
            current_time = datetime.now()
        
        days_staked = (current_time - self.last_compound).days
        daily_rate = (self.apy / 100) / 365
        
        return self.amount * daily_rate * days_staked
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'token_type': self.token_type.value,
            'amount': self.amount,
            'apy': self.apy,
            'duration_days': self.duration_days,
            'start_date': self.start_date.isoformat(),
            'maturity_date': self.maturity_date.isoformat(),
            'rewards_earned': self.rewards_earned,
            'locked': self.locked and not self.withdrawn,
            'withdrawn': self.withdrawn,
            'can_withdraw': datetime.now() >= self.maturity_date and not self.withdrawn
        }


@dataclass
class GovernanceProposal:
    """Governance proposal for GT holders"""
    id: str
    proposer_id: str
    title: str
    description: str
    
    # Proposal details
    proposal_type: str  # parameter_change, upgrade, treasury, other
    proposed_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Voting
    voting_start: datetime = None
    voting_end: datetime = None
    min_quorum_pct: float = 10.0  # Minimum % of total GT needed
    
    # Results
    votes_for: float = 0.0
    votes_against: float = 0.0
    votes_abstain: float = 0.0
    voters: Dict[str, str] = field(default_factory=dict)  # user_id -> vote
    
    # Status
    status: str = "pending"  # pending, active, passed, rejected, executed
    executed_at: Optional[datetime] = None
    execution_tx_hash: Optional[str] = None
    
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.voting_start is None:
            self.voting_start = datetime.now()
        if self.voting_end is None:
            self.voting_end = self.voting_start + timedelta(days=7)
    
    def cast_vote(self, user_id: str, vote: str, weight: float) -> bool:
        """Cast a vote (for, against, abstain)"""
        if self.status != "active":
            return False
        
        if datetime.now() > self.voting_end:
            return False
        
        # Remove previous vote if exists
        if user_id in self.voters:
            prev_vote = self.voters[user_id]
            if prev_vote == 'for':
                self.votes_for -= weight
            elif prev_vote == 'against':
                self.votes_against -= weight
            elif prev_vote == 'abstain':
                self.votes_abstain -= weight
        
        # Add new vote
        self.voters[user_id] = vote
        if vote == 'for':
            self.votes_for += weight
        elif vote == 'against':
            self.votes_against += weight
        elif vote == 'abstain':
            self.votes_abstain += weight
        
        return True
    
    def get_results(self) -> Dict:
        """Get current voting results"""
        total_votes = self.votes_for + self.votes_against + self.votes_abstain
        
        return {
            'total_votes': total_votes,
            'for': self.votes_for,
            'against': self.votes_against,
            'abstain': self.votes_abstain,
            'for_pct': (self.votes_for / total_votes * 100) if total_votes > 0 else 0,
            'against_pct': (self.votes_against / total_votes * 100) if total_votes > 0 else 0,
            'quorum_reached': total_votes >= self.min_quorum_pct  # Simplified
        }
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'proposer': self.proposer_id,
            'type': self.proposal_type,
            'proposed_changes': self.proposed_changes,
            'voting': {
                'start': self.voting_start.isoformat(),
                'end': self.voting_end.isoformat(),
                'min_quorum_pct': self.min_quorum_pct
            },
            'results': self.get_results(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class DualTokenEconomy:
    """
    Dual-Token Economy System (WT + GT)
    """
    
    # Staking APY rates by duration
    STAKING_RATES = {
        30: 5.0,    # 30 days - 5% APY
        90: 8.0,    # 90 days - 8% APY
        180: 12.0,  # 180 days - 12% APY
        365: 18.0   # 365 days - 18% APY
    }
    
    # Tier benefits
    TIER_BENEFITS = {
        StakingTier.BRONZE: {
            'trading_discount': 0.05,  # 5% discount
            'referral_bonus': 1.0,  # 1x
            'wt_rewards_multiplier': 1.0,
            'support_priority': 'normal'
        },
        StakingTier.SILVER: {
            'trading_discount': 0.10,
            'referral_bonus': 1.25,
            'wt_rewards_multiplier': 1.25,
            'support_priority': 'priority'
        },
        StakingTier.GOLD: {
            'trading_discount': 0.15,
            'referral_bonus': 1.5,
            'wt_rewards_multiplier': 1.5,
            'support_priority': 'priority'
        },
        StakingTier.PLATINUM: {
            'trading_discount': 0.20,
            'referral_bonus': 2.0,
            'wt_rewards_multiplier': 2.0,
            'support_priority': 'vip'
        },
        StakingTier.DIAMOND: {
            'trading_discount': 0.30,
            'referral_bonus': 3.0,
            'wt_rewards_multiplier': 3.0,
            'support_priority': 'vip'
        }
    }
    
    def __init__(self):
        # Token configurations
        self.wt_config = TokenConfig(
            name="Work Token",
            symbol="WT",
            max_supply=500_000_000.0  # 500M WT
        )
        
        self.gt_config = TokenConfig(
            name="Governance Token",
            symbol="GT",
            max_supply=10_000_000.0  # 10M GT
        )
        
        # User balances
        self.balances: Dict[str, TokenBalance] = {}
        
        # Staking positions
        self.staking_positions: Dict[str, StakingPosition] = {}
        self.user_stakes: Dict[str, List[str]] = {}  # user_id -> position_ids
        
        # Proposals
        self.proposals: Dict[str, GovernanceProposal] = {}
        
        # Reward distribution tracking
        self.daily_rewards_pool: Dict[str, float] = {'wt': 50_000, 'gt': 100}  # Daily distribution
        
        # Anti-whale settings
        self.max_transaction_pct = 1.0  # Max 1% of supply per transaction
        self.max_wallet_pct = 5.0  # Max 5% of supply per wallet
    
    def get_or_create_balance(self, user_id: str) -> TokenBalance:
        """Get or create user balance"""
        if user_id not in self.balances:
            self.balances[user_id] = TokenBalance(user_id=user_id)
        return self.balances[user_id]
    
    def mint_wt(self, user_id: str, amount: float, reason: str = "") -> bool:
        """Mint Work Tokens to user"""
        if self.wt_config.total_supply + amount > self.wt_config.max_supply:
            return False
        
        balance = self.get_or_create_balance(user_id)
        balance.wt_balance += amount
        self.wt_config.total_supply += amount
        
        logger.info(f"Minted {amount} WT to {user_id} - {reason}")
        return True
    
    def mint_gt(self, user_id: str, amount: float, reason: str = "") -> bool:
        """Mint Governance Tokens to user"""
        if self.gt_config.total_supply + amount > self.gt_config.max_supply:
            return False
        
        balance = self.get_or_create_balance(user_id)
        balance.gt_balance += amount
        self.gt_config.total_supply += amount
        
        logger.info(f"Minted {amount} GT to {user_id} - {reason}")
        return True
    
    def burn_wt(self, user_id: str, amount: float) -> bool:
        """Burn Work Tokens from user"""
        balance = self.balances.get(user_id)
        if not balance or balance.wt_balance < amount:
            return False
        
        balance.wt_balance -= amount
        self.wt_config.total_supply -= amount
        
        logger.info(f"Burned {amount} WT from {user_id}")
        return True
    
    def transfer_wt(self, from_user: str, to_user: str, amount: float) -> bool:
        """Transfer WT between users"""
        from_balance = self.balances.get(from_user)
        if not from_balance or from_balance.wt_balance < amount:
            return False
        
        # Anti-whale check
        if amount > (self.wt_config.total_supply * self.max_transaction_pct / 100):
            logger.warning(f"Transfer exceeds max transaction limit: {amount}")
            return False
        
        to_balance = self.get_or_create_balance(to_user)
        
        # Check max wallet limit
        if (to_balance.wt_balance + to_balance.wt_staked + amount) > \
           (self.wt_config.total_supply * self.max_wallet_pct / 100):
            logger.warning(f"Transfer would exceed max wallet limit for {to_user}")
            return False
        
        from_balance.wt_balance -= amount
        to_balance.wt_balance += amount
        
        return True
    
    def stake_tokens(self, user_id: str, token_type: str, amount: float, 
                    duration_days: int) -> Optional[StakingPosition]:
        """Stake tokens for rewards"""
        balance = self.balances.get(user_id)
        if not balance:
            return None
        
        # Check available balance
        if token_type == 'wt':
            if balance.wt_balance < amount:
                return None
            balance.wt_balance -= amount
            balance.wt_staked += amount
        elif token_type == 'gt':
            if balance.gt_balance < amount:
                return None
            balance.gt_balance -= amount
            balance.gt_staked += amount
        else:
            return None
        
        # Get APY for duration
        apy = self.STAKING_RATES.get(duration_days, 5.0)
        
        # Create staking position
        position = StakingPosition(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_type=TokenType(token_type),
            amount=amount,
            start_date=datetime.now(),
            duration_days=duration_days,
            apy=apy
        )
        
        self.staking_positions[position.id] = position
        
        if user_id not in self.user_stakes:
            self.user_stakes[user_id] = []
        self.user_stakes[user_id].append(position.id)
        
        # Update first staked timestamp
        if balance.first_staked is None:
            balance.first_staked = datetime.now()
        
        logger.info(f"Created staking position: {position.id} for {user_id}")
        return position
    
    def unstake_tokens(self, position_id: str) -> Dict:
        """Unstake tokens and claim rewards"""
        position = self.staking_positions.get(position_id)
        if not position:
            return {'error': 'Position not found'}
        
        if position.withdrawn:
            return {'error': 'Already withdrawn'}
        
        if position.locked and datetime.now() < position.maturity_date:
            return {'error': 'Position still locked'}
        
        balance = self.balances.get(position.user_id)
        if not balance:
            return {'error': 'User balance not found'}
        
        # Calculate final rewards
        final_rewards = position.calculate_rewards()
        total_rewards = position.rewards_earned + final_rewards
        
        # Return staked amount + rewards
        if position.token_type == TokenType.WT:
            balance.wt_staked -= position.amount
            balance.wt_balance += position.amount + total_rewards
        else:
            balance.gt_staked -= position.amount
            balance.gt_balance += position.amount + total_rewards
        
        position.withdrawn = True
        position.locked = False
        
        logger.info(f"Unstaked position: {position_id}, rewards: {total_rewards}")
        
        return {
            'success': True,
            'principal_returned': position.amount,
            'rewards_earned': total_rewards,
            'total_received': position.amount + total_rewards
        }
    
    def claim_rewards(self, user_id: str) -> Dict:
        """Claim pending rewards"""
        balance = self.balances.get(user_id)
        if not balance:
            return {'error': 'User not found'}
        
        total_wt = balance.wt_rewards_pending
        total_gt = balance.gt_rewards_pending
        
        # Add staking rewards from positions
        position_ids = self.user_stakes.get(user_id, [])
        for pos_id in position_ids:
            position = self.staking_positions.get(pos_id)
            if position and not position.withdrawn:
                rewards = position.calculate_rewards()
                position.rewards_earned += rewards
                position.last_compound = datetime.now()
                
                if position.token_type == TokenType.WT:
                    total_wt += rewards
                else:
                    total_gt += rewards
        
        # Transfer to available balance
        balance.wt_balance += total_wt
        balance.gt_balance += total_gt
        balance.wt_rewards_pending = 0
        balance.gt_rewards_pending = 0
        balance.last_claimed = datetime.now()
        
        return {
            'success': True,
            'wt_claimed': total_wt,
            'gt_claimed': total_gt,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_balance(self, user_id: str) -> Optional[Dict]:
        """Get user token balance"""
        balance = self.balances.get(user_id)
        if balance:
            return balance.to_dict()
        return None
    
    def get_staking_positions(self, user_id: str) -> List[Dict]:
        """Get all staking positions for user"""
        position_ids = self.user_stakes.get(user_id, [])
        positions = []
        for pos_id in position_ids:
            position = self.staking_positions.get(pos_id)
            if position:
                # Update rewards before returning
                new_rewards = position.calculate_rewards()
                pos_dict = position.to_dict()
                pos_dict['rewards_earned'] += new_rewards
                positions.append(pos_dict)
        return positions
    
    def get_tier_benefits(self, tier: str) -> Dict:
        """Get benefits for a staking tier"""
        tier_enum = StakingTier(tier)
        return self.TIER_BENEFITS.get(tier_enum, {})
    
    def create_proposal(self, proposer_id: str, title: str, description: str,
                       proposal_type: str, changes: Dict) -> GovernanceProposal:
        """Create a governance proposal"""
        
        # Check if proposer has enough GT (need at least 100 GT)
        balance = self.balances.get(proposer_id)
        if not balance or (balance.gt_balance + balance.gt_staked) < 100:
            raise ValueError("Insufficient GT to create proposal (minimum 100 GT)")
        
        proposal = GovernanceProposal(
            id=str(uuid.uuid4()),
            proposer_id=proposer_id,
            title=title,
            description=description,
            proposal_type=proposal_type,
            proposed_changes=changes,
            status="active"
        )
        
        self.proposals[proposal.id] = proposal
        
        logger.info(f"Created proposal: {proposal.id} by {proposer_id}")
        return proposal
    
    def vote_on_proposal(self, proposal_id: str, user_id: str, 
                        vote: str) -> bool:
        """Vote on a proposal (for, against, abstain)"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
        
        # Get voting weight (1 GT = 1 vote)
        balance = self.balances.get(user_id)
        if not balance:
            return False
        
        weight = balance.gt_balance + balance.gt_staked
        if weight <= 0:
            return False
        
        return proposal.cast_vote(user_id, vote, weight)
    
    def get_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Get proposal details"""
        proposal = self.proposals.get(proposal_id)
        if proposal:
            return proposal.to_dict()
        return None
    
    def list_proposals(self, status: str = None, limit: int = 20) -> List[Dict]:
        """List proposals"""
        proposals = list(self.proposals.values())
        
        if status:
            proposals = [p for p in proposals if p.status == status]
        
        # Sort by newest first
        proposals.sort(key=lambda p: p.created_at, reverse=True)
        
        return [p.to_dict() for p in proposals[:limit]]
    
    def distribute_trading_rewards(self, user_id: str, trading_volume: float):
        """Distribute rewards based on trading activity"""
        balance = self.get_or_create_balance(user_id)
        
        # Calculate reward (0.1 WT per $1000 volume)
        reward = (trading_volume / 1000) * 0.1
        
        # Apply tier multiplier
        tier = balance.get_tier()
        multiplier = self.TIER_BENEFITS[tier]['wt_rewards_multiplier']
        reward *= multiplier
        
        balance.wt_rewards_pending += reward
        
        logger.info(f"Distributed {reward} WT trading rewards to {user_id}")
    
    def get_tokenomics_summary(self) -> Dict:
        """Get tokenomics overview"""
        return {
            'work_token': {
                'symbol': self.wt_config.symbol,
                'total_supply': self.wt_config.total_supply,
                'max_supply': self.wt_config.max_supply,
                'circulating': sum(b.wt_balance + b.wt_staked for b in self.balances.values()),
                'staked': sum(b.wt_staked for b in self.balances.values()),
                'burned': self.wt_config.max_supply - self.wt_config.total_supply
            },
            'governance_token': {
                'symbol': self.gt_config.symbol,
                'total_supply': self.gt_config.total_supply,
                'max_supply': self.gt_config.max_supply,
                'circulating': sum(b.gt_balance + b.gt_staked for b in self.balances.values()),
                'staked': sum(b.gt_staked for b in self.balances.values())
            },
            'staking_stats': {
                'total_positions': len(self.staking_positions),
                'active_proposals': len([p for p in self.proposals.values() if p.status == 'active'])
            },
            'anti_whale': {
                'max_transaction_pct': self.max_transaction_pct,
                'max_wallet_pct': self.max_wallet_pct
            }
        }
