"""DeFi Yield Farming Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class Protocol(Enum):
    AAVE = "aave"
    COMPOUND = "compound"
    UNISWAP = "uniswap"
    CURVE = "curve"
    CONVEX = "convex"
    LIDO = "lido"
    ROCKETPOOL = "rocketpool"

@dataclass
class YieldOpportunity:
    protocol: str
    pool_name: str
    asset: str
    apy_base: float
    apy_reward: float
    tvl: float
    risk_score: float
    impermanent_loss_risk: float
    lockup_period: int
    min_deposit: float

@dataclass
class FarmingPosition:
    position_id: str
    user_id: str
    protocol: str
    pool: str
    asset: str
    deposited_amount: float
    current_value: float
    earned_yield: float
    entry_date: datetime
    unlock_date: Optional[datetime]

class YieldFarming:
    """DeFi yield farming aggregator across multiple protocols."""
    
    def __init__(self):
        self.opportunities: Dict[str, YieldOpportunity] = {}
        self.positions: Dict[str, FarmingPosition] = {}
        self.user_rewards: Dict[str, Dict[str, float]] = {}
        self.protocol_fees: Dict[str, float] = {
            'aave': 0.0027, 'compound': 0.0025, 'uniswap': 0.003,
            'curve': 0.0004, 'convex': 0.001, 'lido': 0.10, 'rocketpool': 0.15
        }
        
        # Initialize sample opportunities
        self._init_opportunities()
    
    def _init_opportunities(self):
        """Initialize yield opportunities."""
        opportunities = [
            ('AAVE', 'USDC Lending', 'USDC', 5.5, 2.0, 500_000_000, 2, 0, 0, 0),
            ('AAVE', 'ETH Lending', 'ETH', 3.2, 1.5, 800_000_000, 2, 0, 0, 0),
            ('COMPOUND', 'DAI Lending', 'DAI', 4.8, 1.8, 300_000_000, 2, 0, 0, 0),
            ('UNISWAP', 'ETH/USDC LP', 'ETH/USDC', 8.5, 12.0, 200_000_000, 5, 15, 0, 1000),
            ('UNISWAP', 'WBTC/ETH LP', 'WBTC/ETH', 6.2, 8.0, 150_000_000, 5, 20, 0, 500),
            ('CURVE', '3Pool', 'DAI/USDC/USDT', 4.2, 3.5, 400_000_000, 2, 2, 0, 100),
            ('CURVE', 'stETH/ETH', 'stETH/ETH', 3.8, 2.2, 1_500_000_000, 2, 1, 0, 0.01),
            ('CONVEX', '3Pool Boosted', 'DAI/USDC/USDT', 5.5, 8.0, 400_000_000, 3, 2, 0, 100),
            ('LIDO', 'ETH Staking', 'ETH', 4.0, 0, 15_000_000_000, 1, 0, 0, 0),
            ('ROCKETPOOL', 'ETH Staking', 'ETH', 4.2, 0, 3_000_000_000, 1, 0, 0, 0.01)
        ]
        
        for opp in opportunities:
            opp_id = f"{opp[0]}_{opp[1].replace(' ', '_')}"
            self.opportunities[opp_id] = YieldOpportunity(
                protocol=opp[0].lower(),
                pool_name=opp[1],
                asset=opp[2],
                apy_base=opp[3],
                apy_reward=opp[4],
                tvl=opp[5],
                risk_score=opp[6],
                impermanent_loss_risk=opp[7],
                lockup_period=opp[8],
                min_deposit=opp[9]
            )
    
    async def get_yield_opportunities(self,
                                     min_apy: float = 0,
                                     max_risk: float = 10,
                                     asset_filter: Optional[str] = None) -> List[Dict]:
        """Get yield farming opportunities with filters."""
        results = []
        
        for opp_id, opp in self.opportunities.items():
            total_apy = opp.apy_base + opp.apy_reward
            
            if total_apy < min_apy:
                continue
            if opp.risk_score > max_risk:
                continue
            if asset_filter and asset_filter not in opp.asset:
                continue
            
            results.append({
                'opportunity_id': opp_id,
                'protocol': opp.protocol,
                'pool_name': opp.pool_name,
                'asset': opp.asset,
                'apy_base': opp.apy_base,
                'apy_reward': opp.apy_reward,
                'apy_total': total_apy,
                'tvl': opp.tvl,
                'risk_score': opp.risk_score,
                'impermanent_loss_risk': opp.impermanent_loss_risk,
                'lockup_period': opp.lockup_period,
                'min_deposit': opp.min_deposit
            })
        
        return sorted(results, key=lambda x: x['apy_total'], reverse=True)
    
    async def deposit(self,
                     user_id: str,
                     opportunity_id: str,
                     amount: float) -> Dict[str, Any]:
        """Deposit into yield farming pool."""
        if opportunity_id not in self.opportunities:
            return {'error': 'Opportunity not found'}
        
        opp = self.opportunities[opportunity_id]
        
        if amount < opp.min_deposit:
            return {'error': f'Minimum deposit is {opp.min_deposit}'}
        
        position_id = f"farm_{user_id}_{datetime.now().strftime('%H%M%S%f')}"
        
        position = FarmingPosition(
            position_id=position_id,
            user_id=user_id,
            protocol=opp.protocol,
            pool=opp.pool_name,
            asset=opp.asset,
            deposited_amount=amount,
            current_value=amount,
            earned_yield=0.0,
            entry_date=datetime.now(),
            unlock_date=datetime.now() + timedelta(days=opp.lockup_period) if opp.lockup_period > 0 else None
        )
        
        self.positions[position_id] = position
        
        return {
            'position_id': position_id,
            'protocol': opp.protocol,
            'pool': opp.pool_name,
            'deposited': amount,
            'expected_apy': opp.apy_base + opp.apy_reward,
            'unlock_date': position.unlock_date.isoformat() if position.unlock_date else None
        }
    
    async def harvest_rewards(self, position_id: str) -> Dict[str, Any]:
        """Harvest farming rewards."""
        if position_id not in self.positions:
            return {'error': 'Position not found'}
        
        position = self.positions[position_id]
        
        # Calculate pending rewards
        days_elapsed = (datetime.now() - position.entry_date).days
        opp = self.opportunities.get(f"{position.protocol}_{position.pool.replace(' ', '_')}")
        
        if opp:
            daily_yield = position.deposited_amount * (opp.apy_base + opp.apy_reward) / 365 / 100
            pending_rewards = daily_yield * days_elapsed
        else:
            pending_rewards = position.earned_yield
        
        harvested = pending_rewards
        position.earned_yield = 0
        
        return {
            'position_id': position_id,
            'harvested_rewards': harvested,
            'harvest_time': datetime.now().isoformat()
        }
    
    async def withdraw(self, position_id: str) -> Dict[str, Any]:
        """Withdraw from farming position."""
        if position_id not in self.positions:
            return {'error': 'Position not found'}
        
        position = self.positions[position_id]
        
        # Check lockup
        if position.unlock_date and datetime.now() < position.unlock_date:
            return {'error': 'Position is still locked'}
        
        # Harvest any remaining rewards
        harvest = await self.harvest_rewards(position_id)
        
        withdrawn = position.current_value
        del self.positions[position_id]
        
        return {
            'position_id': position_id,
            'withdrawn_amount': withdrawn,
            'harvested_rewards': harvest.get('harvested_rewards', 0),
            'total_return': withdrawn + harvest.get('harvested_rewards', 0)
        }
    
    async def get_user_farming_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user's yield farming summary."""
        user_positions = [p for p in self.positions.values() if p.user_id == user_id]
        
        total_deposited = sum(p.deposited_amount for p in user_positions)
        total_current = sum(p.current_value for p in user_positions)
        total_earned = sum(p.earned_yield for p in user_positions)
        
        return {
            'user_id': user_id,
            'active_positions': len(user_positions),
            'total_deposited': total_deposited,
            'total_current_value': total_current,
            'total_earned_yield': total_earned,
            'unrealized_yield': total_current - total_deposited,
            'positions': [{
                'position_id': p.position_id,
                'protocol': p.protocol,
                'pool': p.pool,
                'asset': p.asset,
                'deposited': p.deposited_amount,
                'current_value': p.current_value,
                'earned': p.earned_yield,
                'entry_date': p.entry_date.isoformat()
            } for p in user_positions]
        }

yield_farming = YieldFarming()
