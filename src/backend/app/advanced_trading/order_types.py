"""
Advanced Order Types
==================
Implementation of advanced order types for institutional trading
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Advanced order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    PEGGED = "pegged"
    RESERVE = "reserve"
    TRAILING_STOP = "trailing_stop"
    OCO = "oco"  # One-Cancels-Other
    IFD = "ifd"  # If-Done
    BASKET = "basket"
    CONTINGENT = "contingent"


@dataclass
class IcebergOrder:
    """Iceberg order configuration"""
    total_quantity: float
    display_quantity: float
    random_variation: bool = True
    min_display: float = 100.0


@dataclass
class TWAPOrder:
    """TWAP order configuration"""
    total_quantity: float
    duration_minutes: int
    num_slices: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class VWAPOrder:
    """VWAP order configuration"""
    total_quantity: float
    duration_minutes: int
    num_slices: int
    volume_profile: str = "uniform"  # uniform, front_loaded, back_loaded


@dataclass
class OCOOrder:
    """One-Cancels-Other order configuration"""
    primary_order: Dict[str, Any]
    secondary_order: Dict[str, Any]


@dataclass
class ContingentOrder:
    """Contingent order configuration"""
    condition_type: str  # price, time, volume
    condition_value: float
    condition_operator: str  # >, <, >=, <=, ==
    primary_order: Dict[str, Any]
    contingent_order: Dict[str, Any]


class AdvancedOrderTypes:
    """Advanced order types manager"""
    
    def __init__(self):
        self.active_orders: Dict[str, Dict] = {}
        self.order_history: List[Dict] = []
        
    async def create_iceberg_order(self, symbol: str, side: str, 
                               iceberg_config: IcebergOrder) -> str:
        """Create iceberg order"""
        try:
            order_id = str(uuid.uuid4())
            
            order = {
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "order_type": OrderType.ICEBERG,
                "total_quantity": iceberg_config.total_quantity,
                "display_quantity": iceberg_config.display_quantity,
                "remaining_quantity": iceberg_config.total_quantity,
                "executed_quantity": 0.0,
                "status": "active",
                "created_at": datetime.now(),
                "config": iceberg_config
            }
            
            self.active_orders[order_id] = order
            
            # Execute iceberg logic
            await self._execute_iceberg_order(order)
            
            logger.info(f"Iceberg order created: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error creating iceberg order: {e}")
            raise
            
    async def create_twap_order(self, symbol: str, side: str,
                             twap_config: TWAPOrder) -> str:
        """Create TWAP order"""
        try:
            order_id = str(uuid.uuid4())
            
            order = {
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "order_type": OrderType.TWAP,
                "total_quantity": twap_config.total_quantity,
                "remaining_quantity": twap_config.total_quantity,
                "executed_quantity": 0.0,
                "status": "active",
                "created_at": datetime.now(),
                "config": twap_config
            }
            
            self.active_orders[order_id] = order
            
            # Execute TWAP logic
            await self._execute_twap_order(order)
            
            logger.info(f"TWAP order created: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error creating TWAP order: {e}")
            raise
            
    async def create_vwap_order(self, symbol: str, side: str,
                             vwap_config: VWAPOrder) -> str:
        """Create VWAP order"""
        try:
            order_id = str(uuid.uuid4())
            
            order = {
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "order_type": OrderType.VWAP,
                "total_quantity": vwap_config.total_quantity,
                "remaining_quantity": vwap_config.total_quantity,
                "executed_quantity": 0.0,
                "status": "active",
                "created_at": datetime.now(),
                "config": vwap_config
            }
            
            self.active_orders[order_id] = order
            
            # Execute VWAP logic
            await self._execute_vwap_order(order)
            
            logger.info(f"VWAP order created: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error creating VWAP order: {e}")
            raise
            
    async def create_oco_order(self, symbol: str, oco_config: OCOOrder) -> str:
        """Create One-Cancels-Other order"""
        try:
            order_id = str(uuid.uuid4())
            
            order = {
                "order_id": order_id,
                "symbol": symbol,
                "order_type": OrderType.OCO,
                "primary_order": oco_config.primary_order,
                "secondary_order": oco_config.secondary_order,
                "status": "active",
                "created_at": datetime.now(),
                "config": oco_config
            }
            
            self.active_orders[order_id] = order
            
            # Execute OCO logic
            await self._execute_oco_order(order)
            
            logger.info(f"OCO order created: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error creating OCO order: {e}")
            raise
            
    async def create_contingent_order(self, symbol: str, 
                                  contingent_config: ContingentOrder) -> str:
        """Create contingent order"""
        try:
            order_id = str(uuid.uuid4())
            
            order = {
                "order_id": order_id,
                "symbol": symbol,
                "order_type": OrderType.CONTINGENT,
                "condition_type": contingent_config.condition_type,
                "condition_value": contingent_config.condition_value,
                "condition_operator": contingent_config.condition_operator,
                "primary_order": contingent_config.primary_order,
                "contingent_order": contingent_config.contingent_order,
                "status": "waiting",
                "created_at": datetime.now(),
                "config": contingent_config
            }
            
            self.active_orders[order_id] = order
            
            # Monitor condition
            await self._monitor_contingent_order(order)
            
            logger.info(f"Contingent order created: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error creating contingent order: {e}")
            raise
            
    async def _execute_iceberg_order(self, order: Dict):
        """Execute iceberg order logic"""
        config = order["config"]
        
        while order["remaining_quantity"] > 0 and order["status"] == "active":
            # Calculate display quantity with random variation
            display_qty = config.display_quantity
            if config.random_variation:
                variation = 0.2  # 20% variation
                display_qty = max(
                    config.min_display,
                    display_qty * (1 + (hash(str(datetime.now())) % 100 - 50) / 100 * variation)
                )
                
            # Limit to remaining quantity
            display_qty = min(display_qty, order["remaining_quantity"])
            
            # Execute slice
            await self._execute_market_slice(order, display_qty)
            
            # Update order
            order["executed_quantity"] += display_qty
            order["remaining_quantity"] -= display_qty
            
            # Wait between slices
            await asyncio.sleep(1)  # 1 second between slices
            
        order["status"] = "completed"
        
    async def _execute_twap_order(self, order: Dict):
        """Execute TWAP order logic"""
        config = order["config"]
        
        slice_size = config.total_quantity / config.num_slices
        slice_interval = config.duration_minutes * 60 / config.num_slices  # seconds
        
        for i in range(config.num_slices):
            if order["remaining_quantity"] <= 0:
                break
                
            # Execute slice
            current_slice = min(slice_size, order["remaining_quantity"])
            await self._execute_market_slice(order, current_slice)
            
            # Update order
            order["executed_quantity"] += current_slice
            order["remaining_quantity"] -= current_slice
            
            # Wait for next slice
            await asyncio.sleep(slice_interval)
            
        order["status"] = "completed"
        
    async def _execute_vwap_order(self, order: Dict):
        """Execute VWAP order logic"""
        config = order["config"]
        
        # Get volume profile
        if config.volume_profile == "uniform":
            slice_sizes = [config.total_quantity / config.num_slices] * config.num_slices
        elif config.volume_profile == "front_loaded":
            # More volume at beginning
            weights = [2.0 - (i / config.num_slices) for i in range(config.num_slices)]
            total_weight = sum(weights)
            slice_sizes = [w / total_weight * config.total_quantity for w in weights]
        elif config.volume_profile == "back_loaded":
            # More volume at end
            weights = [(i + 1) / config.num_slices for i in range(config.num_slices)]
            total_weight = sum(weights)
            slice_sizes = [w / total_weight * config.total_quantity for w in weights]
        else:
            slice_sizes = [config.total_quantity / config.num_slices] * config.num_slices
            
        slice_interval = config.duration_minutes * 60 / config.num_slices  # seconds
        
        for i, slice_size in enumerate(slice_sizes):
            if order["remaining_quantity"] <= 0:
                break
                
            # Execute slice
            current_slice = min(slice_size, order["remaining_quantity"])
            await self._execute_market_slice(order, current_slice)
            
            # Update order
            order["executed_quantity"] += current_slice
            order["remaining_quantity"] -= current_slice
            
            # Wait for next slice
            await asyncio.sleep(slice_interval)
            
        order["status"] = "completed"
        
    async def _execute_oco_order(self, order: Dict):
        """Execute OCO order logic"""
        # Submit both orders
        primary_id = await self._submit_simple_order(order["primary_order"])
        secondary_id = await self._submit_simple_order(order["secondary_order"])
        
        # Monitor both orders
        while True:
            primary_status = await self._get_order_status(primary_id)
            secondary_status = await self._get_order_status(secondary_id)
            
            # If primary order fills, cancel secondary
            if primary_status.get("status") == "filled":
                await self._cancel_order(secondary_id)
                order["status"] = "primary_filled"
                break
                
            # If secondary order fills, cancel primary
            if secondary_status.get("status") == "filled":
                await self._cancel_order(primary_id)
                order["status"] = "secondary_filled"
                break
                
            # If both cancelled
            if (primary_status.get("status") == "cancelled" and 
                secondary_status.get("status") == "cancelled"):
                order["status"] = "both_cancelled"
                break
                
            await asyncio.sleep(1)  # Check every second
            
    async def _monitor_contingent_order(self, order: Dict):
        """Monitor contingent order condition"""
        while order["status"] == "waiting":
            # Check condition
            condition_met = await self._check_condition(order)
            
            if condition_met:
                # Submit contingent order
                await self._submit_simple_order(order["contingent_order"])
                order["status"] = "triggered"
                break
                
            await asyncio.sleep(1)  # Check every second
            
    async def _check_condition(self, order: Dict) -> bool:
        """Check contingent order condition"""
        # Get current market data
        current_price = await self._get_market_price(order["symbol"])
        
        if order["condition_type"] == "price":
            if order["condition_operator"] == ">":
                return current_price > order["condition_value"]
            elif order["condition_operator"] == "<":
                return current_price < order["condition_value"]
            elif order["condition_operator"] == ">=":
                return current_price >= order["condition_value"]
            elif order["condition_operator"] == "<=":
                return current_price <= order["condition_value"]
            elif order["condition_operator"] == "==":
                return abs(current_price - order["condition_value"]) < 0.01
                
        # Add other condition types (time, volume, etc.)
        
        return False
        
    async def _execute_market_slice(self, order: Dict, quantity: float):
        """Execute market order slice"""
        # Simulate market execution
        execution_price = await self._get_market_price(order["symbol"])
        
        # Record execution
        execution = {
            "order_id": order["order_id"],
            "quantity": quantity,
            "price": execution_price,
            "timestamp": datetime.now(),
            "execution_type": "market"
        }
        
        # Add to order history
        if "executions" not in order:
            order["executions"] = []
        order["executions"].append(execution)
        
        # Simulate execution delay
        await asyncio.sleep(0.1)
        
    async def _submit_simple_order(self, order_config: Dict) -> str:
        """Submit simple order"""
        # Simulate order submission
        order_id = str(uuid.uuid4())
        return order_id
        
    async def _get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        # Simulate order status check
        return {"status": "active"}
        
    async def _cancel_order(self, order_id: str):
        """Cancel order"""
        # Simulate order cancellation
        pass
        
    async def _get_market_price(self, symbol: str) -> float:
        """Get current market price"""
        # Simulate market price
        return 100.0  # Mock price
        
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get order status"""
        return self.active_orders.get(order_id)
        
    def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        try:
            order = self.active_orders.get(order_id)
            if not order:
                return False
                
            order["status"] = "cancelled"
            order["cancelled_at"] = datetime.now()
            
            # Move to history
            self.order_history.append(order.copy())
            del self.active_orders[order_id]
            
            logger.info(f"Order cancelled: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
            
    def get_active_orders(self) -> List[Dict]:
        """Get all active orders"""
        return list(self.active_orders.values())
        
    def get_order_history(self) -> List[Dict]:
        """Get order history"""
        return self.order_history.copy()


# Global advanced order types instance
_advanced_order_types = None

def get_advanced_order_types() -> AdvancedOrderTypes:
    """Get the global advanced order types instance"""
    global _advanced_order_types
    if _advanced_order_types is None:
        _advanced_order_types = AdvancedOrderTypes()
    return _advanced_order_types
