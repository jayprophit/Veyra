"""
No-Code Strategy Builder API Routes
FastAPI endpoints for visual strategy building
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel

from .strategy_builder import StrategyBuilder, StrategyBlockLibrary

router = APIRouter(prefix="/strategy-builder", tags=["No-Code Builder"])

# Initialize builder
builder = StrategyBuilder()


class CreateStrategyRequest(BaseModel):
    name: str
    description: str
    user_id: str


class AddBlockRequest(BaseModel):
    strategy_id: str
    block_type: str
    position: Dict
    config: Optional[Dict] = None


class UpdateBlockRequest(BaseModel):
    strategy_id: str
    block_id: str
    config: Dict


class ConnectBlocksRequest(BaseModel):
    strategy_id: str
    from_block_id: str
    to_block_id: str


@router.get("/blocks")
async def get_all_blocks():
    """Get all available strategy building blocks"""
    return {
        'blocks': StrategyBlockLibrary.get_all_blocks(),
        'categories': StrategyBlockLibrary.get_categories()
    }


@router.get("/blocks/{category}")
async def get_blocks_by_category(category: str):
    """Get blocks filtered by category"""
    return {
        'category': category,
        'blocks': StrategyBlockLibrary.get_blocks_by_category(category)
    }


@router.post("/strategies")
async def create_strategy(request: CreateStrategyRequest):
    """Create a new blank strategy"""
    strategy = builder.create_strategy(
        name=request.name,
        description=request.description,
        user_id=request.user_id
    )
    return strategy.to_dict()


@router.get("/strategies")
async def list_strategies(user_id: Optional[str] = None):
    """List all strategies, optionally filtered by user"""
    return {'strategies': builder.list_strategies(user_id)}


@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    """Get strategy details"""
    strategy = builder.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.post("/strategies/{strategy_id}/blocks")
async def add_block(request: AddBlockRequest):
    """Add a block to a strategy"""
    block = builder.add_block(
        strategy_id=request.strategy_id,
        block_type=request.block_type,
        position=request.position,
        config=request.config
    )
    if not block:
        raise HTTPException(status_code=400, detail="Failed to add block")
    return block.to_dict()


@router.post("/strategies/{strategy_id}/connect")
async def connect_blocks(request: ConnectBlocksRequest):
    """Connect two blocks"""
    success = builder.connect_blocks(
        strategy_id=request.strategy_id,
        from_block_id=request.from_block_id,
        to_block_id=request.to_block_id
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to connect blocks")
    return {'success': True}


@router.put("/strategies/{strategy_id}/blocks/{block_id}")
async def update_block_config(strategy_id: str, block_id: str, request: UpdateBlockRequest):
    """Update block configuration"""
    success = builder.update_block_config(
        strategy_id=strategy_id,
        block_id=block_id,
        config=request.config
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update block")
    return {'success': True}


@router.delete("/strategies/{strategy_id}/blocks/{block_id}")
async def delete_block(strategy_id: str, block_id: str):
    """Remove a block from strategy"""
    success = builder.delete_block(strategy_id, block_id)
    if not success:
        raise HTTPException(status_code=404, detail="Block not found")
    return {'success': True}


@router.post("/strategies/{strategy_id}/validate")
async def validate_strategy(strategy_id: str):
    """Validate a strategy"""
    result = builder.validate_strategy(strategy_id)
    return result


@router.post("/strategies/{strategy_id}/generate")
async def generate_code(strategy_id: str):
    """Generate Python code from strategy"""
    code = builder.generate_code(strategy_id)
    if not code:
        raise HTTPException(status_code=400, detail="Failed to generate code - strategy may be invalid")
    return {'code': code}


@router.post("/strategies/{strategy_id}/duplicate")
async def duplicate_strategy(strategy_id: str, new_name: str):
    """Duplicate an existing strategy"""
    new_strategy = builder.duplicate_strategy(strategy_id, new_name)
    if not new_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return new_strategy.to_dict()


@router.post("/strategies/{strategy_id}/publish")
async def publish_strategy(strategy_id: str):
    """Publish strategy to marketplace"""
    success = builder.publish_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to publish - strategy may be invalid")
    return {'success': True, 'published': True}
