"""
Dual-Token Economy API Routes
FastAPI endpoints for WT/GT tokens
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel

from .token_economy import DualTokenEconomy

router = APIRouter(prefix="/tokens", tags=["Token Economy"])

# Initialize token economy
token_economy = DualTokenEconomy()


class MintRequest(BaseModel):
    user_id: str
    amount: float
    reason: str = ""


class TransferRequest(BaseModel):
    from_user: str
    to_user: str
    amount: float


class StakeRequest(BaseModel):
    user_id: str
    token_type: str  # wt or gt
    amount: float
    duration_days: int


class VoteRequest(BaseModel):
    user_id: str
    vote: str  # for, against, abstain


class ProposalRequest(BaseModel):
    proposer_id: str
    title: str
    description: str
    proposal_type: str
    changes: Dict


@router.get("/balance/{user_id}")
async def get_balance(user_id: str):
    """Get user's token balance"""
    balance = token_economy.get_balance(user_id)
    if not balance:
        return {'balance': None}
    return balance


@router.post("/mint/wt")
async def mint_wt(request: MintRequest):
    """Mint Work Tokens (admin only)"""
    success = token_economy.mint_wt(request.user_id, request.amount, request.reason)
    if not success:
        raise HTTPException(status_code=400, detail="Mint failed - max supply reached")
    return {'success': True, 'amount': request.amount, 'user_id': request.user_id}


@router.post("/mint/gt")
async def mint_gt(request: MintRequest):
    """Mint Governance Tokens (admin only)"""
    success = token_economy.mint_gt(request.user_id, request.amount, request.reason)
    if not success:
        raise HTTPException(status_code=400, detail="Mint failed - max supply reached")
    return {'success': True, 'amount': request.amount, 'user_id': request.user_id}


@router.post("/burn")
async def burn_wt(user_id: str, amount: float):
    """Burn Work Tokens"""
    success = token_economy.burn_wt(user_id, amount)
    if not success:
        raise HTTPException(status_code=400, detail="Burn failed - insufficient balance")
    return {'success': True, 'amount': amount}


@router.post("/transfer")
async def transfer_wt(request: TransferRequest):
    """Transfer WT between users"""
    success = token_economy.transfer_wt(request.from_user, request.to_user, request.amount)
    if not success:
        raise HTTPException(status_code=400, detail="Transfer failed")
    return {'success': True}


@router.post("/stake")
async def stake_tokens(request: StakeRequest):
    """Stake tokens for rewards"""
    position = token_economy.stake_tokens(
        request.user_id, 
        request.token_type, 
        request.amount, 
        request.duration_days
    )
    if not position:
        raise HTTPException(status_code=400, detail="Stake failed - insufficient balance")
    return position.to_dict()


@router.get("/staking/{user_id}")
async def get_staking_positions(user_id: str):
    """Get user's staking positions"""
    return {'positions': token_economy.get_staking_positions(user_id)}


@router.post("/staking/{position_id}/unstake")
async def unstake_tokens(position_id: str):
    """Unstake tokens and claim rewards"""
    result = token_economy.unstake_tokens(position_id)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result


@router.post("/claim/{user_id}")
async def claim_rewards(user_id: str):
    """Claim pending rewards"""
    result = token_economy.claim_rewards(user_id)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result


@router.get("/tier-benefits/{tier}")
async def get_tier_benefits(tier: str):
    """Get benefits for a staking tier"""
    return {'tier': tier, 'benefits': token_economy.get_tier_benefits(tier)}


@router.post("/proposals")
async def create_proposal(request: ProposalRequest):
    """Create governance proposal"""
    try:
        proposal = token_economy.create_proposal(
            request.proposer_id,
            request.title,
            request.description,
            request.proposal_type,
            request.changes
        )
        return proposal.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/proposals")
async def list_proposals(status: str = None, limit: int = 20):
    """List governance proposals"""
    return {'proposals': token_economy.list_proposals(status, limit)}


@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get proposal details"""
    proposal = token_economy.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.post("/proposals/{proposal_id}/vote")
async def vote_on_proposal(proposal_id: str, request: VoteRequest):
    """Vote on a proposal"""
    success = token_economy.vote_on_proposal(proposal_id, request.user_id, request.vote)
    if not success:
        raise HTTPException(status_code=400, detail="Vote failed")
    return {'success': True}


@router.get("/tokenomics")
async def get_tokenomics():
    """Get tokenomics overview"""
    return token_economy.get_tokenomics_summary()


@router.get("/staking-rates")
async def get_staking_rates():
    """Get staking APY rates"""
    return {
        'rates': token_economy.STAKING_RATES,
        'tier_benefits': {t.value: b for t, b in token_economy.TIER_BENEFITS.items()}
    }
