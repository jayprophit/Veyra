"""Crypto Staking Aggregator Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class StakingType(Enum):
    PROOF_OF_STAKE = "pos"
    LIQUID_STAKING = "liquid"
    DELEGATED = "delegated"
    VALIDATOR = "validator"
    LIQUIDITY_MINING = "liquidity_mining"

@dataclass
class StakingOpportunity:
    opportunity_id: str
    asset: str
    platform: str
    staking_type: StakingType
    apy: float
    tvl: float
    lock_period_days: Optional[int]
    min_stake: float
    max_stake: Optional[float]
    rewards_token: str
    auto_compound: bool
    risk_score: float  # 0-10
    impermanent_loss_risk: bool

class CryptoStakingAggregator:
    """Aggregate staking opportunities across protocols."""
    
    def __init__(self):
        self.opportunities: Dict[str, StakingOpportunity] = {}
        self.user_positions: Dict[str, List[Dict]] = {}
        self._init_opportunities()
    
    def _init_opportunities(self):
        """Initialize staking opportunities."""
        opportunities = [
            StakingOpportunity("eth_lido", "ETH", "Lido", StakingType.LIQUID_STAKING, 4.2, 15000000000, None, 0.01, None, "stETH", True, 2.0, False),
            StakingOpportunity("eth_coinbase", "ETH", "Coinbase", StakingType.PROOF_OF_STAKE, 3.8, 5000000000, None, 0.01, None, "ETH", False, 2.5, False),
            StakingOpportunity("sol_solana", "SOL", "Solana", StakingType.DELEGATED, 6.5, 80000000000, 2, 0.01, None, "SOL", True, 3.0, False),
            StakingOpportunity("ada_cardano", "ADA", "Cardano", StakingType.DELEGATED, 4.8, 12000000000, None, 10, None, "ADA", True, 2.5, False),
            StakingOpportunity("dot_polkadot", "DOT", "Polkadot", StakingType.NOMINATED, 14.0, 5000000000, 28, 1, None, "DOT", True, 4.0, False),
            StakingOpportunity("atom_cosmos", "ATOM", "Cosmos", StakingType.DELEGATED, 18.5, 2000000000, 21, 0.1, None, "ATOM", True, 4.5, False),
            StakingOpportunity("uni_lp", "UNI-ETH", "Uniswap V3", StakingType.LIQUIDITY_MINING, 25.0, 300000000, None, 0.001, None, "UNI", True, 6.0, True),
            StakingOpportunity("aave_lp", "USDC-ETH", "Aave", StakingType.LIQUIDITY_MINING, 8.5, 5000000000, None, 100, None, "AAVE", True, 3.5, True),
        ]
        for opp in opportunities:
            self.opportunities[opp.opportunity_id] = opp
    
    async def get_all_opportunities(self, min_apy: Optional[float] = None, 
                                    max_risk: Optional[float] = None,
                                    asset: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get staking opportunities with filters."""
        results = []
        
        for opp in self.opportunities.values():
            if min_apy and opp.apy < min_apy:
                continue
            if max_risk and opp.risk_score > max_risk:
                continue
            if asset and opp.asset != asset:
                continue
            
            results.append({
                'opportunity_id': opp.opportunity_id,
                'asset': opp.asset,
                'platform': opp.platform,
                'staking_type': opp.staking_type.value,
                'apy': opp.apy,
                'tvl': opp.tvl,
                'lock_period_days': opp.lock_period_days,
                'min_stake': opp.min_stake,
                'auto_compound': opp.auto_compound,
                'risk_score': opp.risk_score,
                'impermanent_loss_risk': opp.impermanent_loss_risk
            })
        
        return sorted(results, key=lambda x: x['apy'], reverse=True)
    
    async def stake(self, user_id: str, opportunity_id: str, amount: float) -> Dict[str, Any]:
        """Stake assets in opportunity."""
        if opportunity_id not in self.opportunities:
            return {'error': 'Opportunity not found'}
        
        opp = self.opportunities[opportunity_id]
        
        if amount < opp.min_stake:
            return {'error': f'Minimum stake is {opp.min_stake}'}
        
        if user_id not in self.user_positions:
            self.user_positions[user_id] = []
        
        position = {
            'position_id': f"pos_{user_id}_{int(datetime.now().timestamp())}",
            'opportunity_id': opportunity_id,
            'asset': opp.asset,
            'amount': amount,
            'entry_time': datetime.now().isoformat(),
            'estimated_daily_reward': amount * (opp.apy / 100) / 365,
            'auto_compound': opp.auto_compound
        }
        
        self.user_positions[user_id].append(position)
        
        logger.info(f"User {user_id} staked {amount} {opp.asset} in {opp.platform}")
        
        return {
            'status': 'staked',
            'position': position,
            'projected_annual_yield': amount * (opp.apy / 100),
            'projected_monthly_yield': amount * (opp.apy / 100) / 12
        }
    
    async def unstake(self, user_id: str, position_id: str) -> Dict[str, Any]:
        """Unstake assets from position."""
        if user_id not in self.user_positions:
            return {'error': 'No positions found'}
        
        for pos in self.user_positions[user_id]:
            if pos['position_id'] == position_id:
                opp = self.opportunities.get(pos['opportunity_id'])
                unlock_time = datetime.now()
                if opp and opp.lock_period_days:
                    unlock_time += timedelta(days=opp.lock_period_days)
                
                return {
                    'status': 'unstake_initiated',
                    'position_id': position_id,
                    'amount': pos['amount'],
                    'unlock_time': unlock_time.isoformat(),
                    'total_rewards_earned': pos.get('rewards_earned', 0)
                }
        
        return {'error': 'Position not found'}
    
    async def get_user_staking_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user's staking portfolio summary."""
        if user_id not in self.user_positions:
            return {'total_staked': 0, 'positions': [], 'total_daily_yield': 0}
        
        positions = self.user_positions[user_id]
        total_staked = sum(p['amount'] for p in positions)
        total_daily = sum(p.get('estimated_daily_reward', 0) for p in positions)
        
        return {
            'user_id': user_id,
            'total_positions': len(positions),
            'total_staked_value': total_staked,
            'total_daily_yield': total_daily,
            'total_monthly_yield': total_daily * 30,
            'total_annual_yield': total_daily * 365,
            'average_apr': sum(p['estimated_daily_reward'] * 365 / p['amount'] for p in positions) / len(positions) * 100 if positions else 0,
            'positions': positions
        }
    
    async def get_staking_calculator(self, asset: str, amount: float, years: int = 1) -> Dict[str, Any]:
        """Calculate staking rewards projection."""
        opps = [o for o in self.opportunities.values() if o.asset == asset]
        if not opps:
            return {'error': 'No staking opportunities for asset'}
        
        best_opp = max(opps, key=lambda x: x.apy)
        
        daily_rate = best_opp.apy / 100 / 365
        final_amount = amount * ((1 + daily_rate) ** (years * 365)) if best_opp.auto_compound else amount + (amount * daily_rate * years * 365)
        
        return {
            'asset': asset,
            'initial_stake': amount,
            'years': years,
            'apy': best_opp.apy,
            'auto_compound': best_opp.auto_compound,
            'projected_final_amount': final_amount,
            'total_rewards': final_amount - amount,
            'roi_percentage': ((final_amount - amount) / amount) * 100,
            'monthly_yield': amount * (best_opp.apy / 100) / 12,
            'platform': best_opp.platform
        }

staking_aggregator = CryptoStakingAggregator()
