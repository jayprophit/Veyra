"""
Web3 API Endpoints
==================
Comprehensive Web3 and blockchain API for Financial Master
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..blockchain.web3_integration import (
    get_web3_integration,
    WalletType,
    BlockchainNetwork
)
from ..blockchain.defi_integration import (
    get_defi_integration,
    DeFiProtocol
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/web3", tags=["web3"])


@router.post("/wallet/connect")
async def connect_wallet(
    address: str,
    wallet_type: WalletType,
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM
):
    """Connect a wallet"""
    try:
        web3 = get_web3_integration()
        wallet_info = await web3.connect_wallet(address, wallet_type, network)
        
        return {
            "wallet": {
                "address": wallet_info.address,
                "wallet_type": wallet_info.wallet_type.value,
                "chain_id": wallet_info.chain_id,
                "balance_eth": wallet_info.balance_eth,
                "nonce": wallet_info.nonce,
                "is_connected": wallet_info.is_connected
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wallet/disconnect")
async def disconnect_wallet(address: str):
    """Disconnect a wallet"""
    try:
        web3 = get_web3_integration()
        await web3.disconnect_wallet(address)
        
        return {"message": "Wallet disconnected successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallets")
async def get_connected_wallets():
    """Get all connected wallets"""
    try:
        web3 = get_web3_integration()
        wallets = web3.get_connected_wallets()
        
        return {
            "wallets": [
                {
                    "address": wallet.address,
                    "wallet_type": wallet.wallet_type.value,
                    "chain_id": wallet.chain_id,
                    "balance_eth": wallet.balance_eth,
                    "nonce": wallet.nonce,
                    "last_active": wallet.last_active.isoformat(),
                    "is_connected": wallet.is_connected
                }
                for wallet in wallets
            ],
            "count": len(wallets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wallet/{address}/balance")
async def get_wallet_balance(
    address: str,
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM
):
    """Get wallet balance"""
    try:
        web3 = get_web3_integration()
        balance_wei, nonce = await web3._get_wallet_balance_and_nonce(address, network)
        
        return {
            "address": address,
            "network": network.value,
            "balance_wei": balance_wei,
            "balance_eth": web3._wei_to_eth(balance_wei),
            "nonce": nonce
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallet/{address}/transactions")
async def get_wallet_transactions(
    address: str,
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM,
    limit: int = Query(50, ge=1, le=1000)
):
    """Get wallet transactions"""
    try:
        web3 = get_web3_integration()
        transactions = await web3.get_wallet_transactions(address, network, limit)
        
        return {
            "transactions": [
                {
                    "hash": tx.hash,
                    "from_address": tx.from_address,
                    "to_address": tx.to_address,
                    "value_eth": tx.value_eth,
                    "gas_price": tx.gas_price,
                    "gas_limit": tx.gas_limit,
                    "gas_used": tx.gas_used,
                    "block_number": tx.block_number,
                    "block_timestamp": tx.block_timestamp.isoformat(),
                    "status": tx.status,
                    "data": tx.data
                }
                for tx in transactions
            ],
            "count": len(transactions)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transaction/{tx_hash}")
async def get_transaction(
    tx_hash: str,
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM
):
    """Get transaction details"""
    try:
        web3 = get_web3_integration()
        transaction = await web3.get_transaction(tx_hash, network)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        return {
            "transaction": {
                "hash": transaction.hash,
                "from_address": transaction.from_address,
                "to_address": transaction.to_address,
                "value_eth": transaction.value_eth,
                "gas_price": transaction.gas_price,
                "gas_limit": transaction.gas_limit,
                "gas_used": transaction.gas_used,
                "block_number": transaction.block_number,
                "block_timestamp": transaction.block_timestamp.isoformat(),
                "status": transaction.status,
                "data": transaction.data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tokens")
async def get_supported_tokens():
    """Get supported tokens"""
    try:
        web3 = get_web3_integration()
        tokens = web3.get_supported_tokens()
        
        return {
            "tokens": [
                {
                    "address": token.address,
                    "symbol": token.symbol,
                    "name": token.name,
                    "decimals": token.decimals,
                    "price_usd": token.price_usd,
                    "market_cap": token.market_cap,
                    "volume_24h": token.volume_24h
                }
                for token in tokens
            ],
            "count": len(tokens)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/token/{symbol}/price")
async def get_token_price(symbol: str):
    """Get token price"""
    try:
        web3 = get_web3_integration()
        price = await web3.get_token_price(symbol)
        
        return {
            "symbol": symbol.upper(),
            "price_usd": price,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wallet/{address}/tokens/{token_address}/balance")
async def get_token_balance(
    address: str,
    token_address: str,
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM
):
    """Get ERC-20 token balance"""
    try:
        web3 = get_web3_integration()
        balance = await web3.get_token_balance(address, token_address, network)
        
        return {
            "address": address,
            "token_address": token_address,
            "balance": balance,
            "network": network.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wallet/{address}/send")
async def send_transaction(
    address: str,
    to_address: str,
    value_eth: float,
    data: str = "",
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM
):
    """Send transaction"""
    try:
        web3 = get_web3_integration()
        tx_hash = await web3.send_transaction(address, to_address, value_eth, data, network)
        
        return {
            "transaction_hash": tx_hash,
            "from_address": address,
            "to_address": to_address,
            "value_eth": value_eth,
            "network": network.value,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallet/{address}/defi/positions")
async def get_defi_positions(address: str):
    """Get DeFi positions for address"""
    try:
        defi = get_defi_integration()
        positions = await defi.get_user_positions(address)
        
        return {
            "positions": [
                {
                    "protocol": pos.protocol.value,
                    "pool_address": pos.pool_address,
                    "token_address": pos.token_address,
                    "token_symbol": pos.token_symbol,
                    "amount": str(pos.amount),
                    "value_usd": str(pos.value_usd),
                    "apy": pos.apy,
                    "rewards": pos.rewards,
                    "created_at": pos.created_at.isoformat(),
                    "last_updated": pos.last_updated.isoformat()
                }
                for pos in positions
            ],
            "count": len(positions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/defi/pools/liquidity")
async def get_liquidity_pools(
    protocol: Optional[DeFiProtocol] = Query(None)
):
    """Get liquidity pools"""
    try:
        defi = get_defi_integration()
        pools = await defi.get_liquidity_pools(protocol)
        
        return {
            "pools": [
                {
                    "protocol": pool.protocol.value,
                    "address": pool.address,
                    "token0_address": pool.token0_address,
                    "token1_address": pool.token1_address,
                    "token0_symbol": pool.token0_symbol,
                    "token1_symbol": pool.token1_symbol,
                    "reserve0": str(pool.reserve0),
                    "reserve1": str(pool.reserve1),
                    "total_supply": str(pool.total_supply),
                    "apr": pool.apr,
                    "volume_24h": str(pool.volume_24h),
                    "fee": pool.fee
                }
                for pool in pools
            ],
            "count": len(pools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/defi/pools/lending")
async def get_lending_pools(
    protocol: Optional[DeFiProtocol] = Query(None)
):
    """Get lending pools"""
    try:
        defi = get_defi_integration()
        pools = await defi.get_lending_pools(protocol)
        
        return {
            "pools": [
                {
                    "protocol": pool.protocol.value,
                    "asset_address": pool.asset_address,
                    "asset_symbol": pool.asset_symbol,
                    "total_liquidity": str(pool.total_liquidity),
                    "total_borrows": str(pool.total_borrows),
                    "supply_apy": pool.supply_apy,
                    "borrow_apy": pool.borrow_apy,
                    "utilization_rate": pool.utilization_rate,
                    "collateral_factor": pool.collateral_factor
                }
                for pool in pools
            ],
            "count": len(pools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/defi/liquidity/add")
async def add_liquidity(
    address: str,
    pool_address: str,
    token0_amount: float,
    token1_amount: float
):
    """Add liquidity to a pool"""
    try:
        from decimal import Decimal
        defi = get_defi_integration()
        tx_hash = await defi.add_liquidity(
            address, pool_address, 
            Decimal(str(token0_amount)), 
            Decimal(str(token1_amount))
        )
        
        return {
            "transaction_hash": tx_hash,
            "pool_address": pool_address,
            "token0_amount": token0_amount,
            "token1_amount": token1_amount,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/defi/lending/supply")
async def supply_to_lending_pool(
    address: str,
    pool_address: str,
    amount: float
):
    """Supply assets to lending pool"""
    try:
        from decimal import Decimal
        defi = get_defi_integration()
        tx_hash = await defi.supply_to_lending_pool(
            address, pool_address, Decimal(str(amount))
        )
        
        return {
            "transaction_hash": tx_hash,
            "pool_address": pool_address,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/defi/opportunities")
async def get_yield_farming_opportunities():
    """Get yield farming opportunities"""
    try:
        defi = get_defi_integration()
        opportunities = await defi.get_yield_farming_opportunities()
        
        return {
            "opportunities": opportunities,
            "count": len(opportunities)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/defi/impermanent-loss")
async def calculate_impermanent_loss(
    pool_address: str,
    initial_amount0: float,
    initial_amount1: float,
    current_amount0: float,
    current_amount1: float
):
    """Calculate impermanent loss"""
    try:
        from decimal import Decimal
        defi = get_defi_integration()
        loss = await defi.calculate_impermanent_loss(
            pool_address,
            Decimal(str(initial_amount0)),
            Decimal(str(initial_amount1)),
            Decimal(str(current_amount0)),
            Decimal(str(current_amount1))
        )
        
        return {
            "pool_address": pool_address,
            "initial_amount0": initial_amount0,
            "initial_amount1": initial_amount1,
            "current_amount0": current_amount0,
            "current_amount1": current_amount1,
            "impermanent_loss_percent": float(loss)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/defi/summary/{address}")
async def get_defi_summary(address: str):
    """Get comprehensive DeFi summary for user"""
    try:
        defi = get_defi_integration()
        summary = await defi.get_defi_summary(address)
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/networks")
async def get_supported_networks():
    """Get supported blockchain networks"""
    try:
        web3 = get_web3_integration()
        
        return {
            "networks": [
                {
                    "name": network.value,
                    "chain_id": config["chain_id"],
                    "native_currency": config["native_currency"],
                    "block_time": config["block_time"]
                }
                for network, config in web3.network_configs.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{address}")
async def get_web3_dashboard(address: str):
    """Get comprehensive Web3 dashboard for user"""
    try:
        web3 = get_web3_integration()
        defi = get_defi_integration()
        
        # Get wallet info
        wallet_info = None
        for wallet in web3.get_connected_wallets():
            if wallet.address.lower() == address.lower():
                wallet_info = wallet
                break
                
        if not wallet_info:
            raise HTTPException(status_code=404, detail="Wallet not connected")
            
        # Get transactions
        transactions = await web3.get_wallet_transactions(address, BlockchainNetwork.ETHEREUM, 10)
        
        # Get DeFi summary
        defi_summary = await defi.get_defi_summary(address)
        
        return {
            "wallet": {
                "address": wallet_info.address,
                "wallet_type": wallet_info.wallet_type.value,
                "chain_id": wallet_info.chain_id,
                "balance_eth": wallet_info.balance_eth,
                "nonce": wallet_info.nonce,
                "last_active": wallet_info.last_active.isoformat()
            },
            "transactions": [
                {
                    "hash": tx.hash,
                    "value_eth": tx.value_eth,
                    "status": tx.status,
                    "block_timestamp": tx.block_timestamp.isoformat()
                }
                for tx in transactions[:5]
            ],
            "defi": defi_summary,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
