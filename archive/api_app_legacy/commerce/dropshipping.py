"""
Drop Shipping Management System
Connects with suppliers, manages orders, tracks fulfillment
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
import asyncio


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class FulfillmentStatus(Enum):
    PENDING = "pending"
    PICKED = "picked"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


@dataclass
class Supplier:
    """Drop shipping supplier"""
    supplier_id: str
    name: str
    contact_info: Dict[str, str]
    
    # Products & Catalog
    product_categories: List[str]
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    
    # Shipping
    shipping_methods: List[str]  # epacket, dhl, fedex, etc.
    average_processing_time: int  # Days
    average_shipping_time: int  # Days
    
    # Quality & Pricing
    quality_rating: float  # 0-5
    reliability_score: float  # 0-100
    pricing_tier: str  # premium, standard, budget
    
    # Locations
    warehouse_locations: List[str]  # Country codes
    ships_to: List[str]  # Country codes
    
    is_active: bool = True


@dataclass
class Product:
    """Product in supplier catalog"""
    product_id: str
    supplier_id: str
    
    name: str
    description: str
    sku: str
    category: str
    
    # Pricing
    cost_price: Decimal  # Supplier price
    suggested_retail: Decimal
    min_order_quantity: int = 1
    
    # Inventory
    stock_quantity: int
    stock_status: str  # in_stock, low_stock, out_of_stock
    
    # Variants
    variants: List[Dict[str, Any]] = field(default_factory=list)  # Size, color, etc.
    
    # Media
    images: List[str] = field(default_factory=list)
    
    # Shipping
    weight_kg: Decimal = Decimal("0.5")
    dimensions_cm: Dict[str, Decimal] = field(default_factory=dict)
    
    # Metrics
    times_sold: int = 0
    return_rate: float = 0.0


@dataclass
class DropShipOrder:
    """Customer order fulfilled via drop shipping"""
    order_id: str
    customer_id: str
    
    # Products
    items: List[Dict[str, Any]]  # [{product_id, variant_id, quantity, price}]
    
    # Pricing
    subtotal: Decimal
    shipping_cost: Decimal
    tax: Decimal
    total: Decimal
    
    # Supplier assignment
    supplier_assignments: Dict[str, str]  # product_id -> supplier_id
    
    # Status
    order_status: OrderStatus = OrderStatus.PENDING
    fulfillment_status: FulfillmentStatus = FulfillmentStatus.PENDING
    
    # Shipping
    shipping_address: Dict[str, str]
    tracking_number: str = ""
    carrier: str = ""
    
    # Timeline
    created_at: datetime = None
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class DropShippingManager:
    """
    Manages drop shipping operations
    
    Features:
    - Supplier management
    - Product catalog sync
    - Order routing to suppliers
    - Automated fulfillment
    - Shipping tracking
    - Profit calculation
    """
    
    def __init__(self):
        self.suppliers: Dict[str, Supplier] = {}
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, DropShipOrder] = {}
        
        # Supplier performance tracking
        self.supplier_metrics: Dict[str, Dict[str, Any]] = {}
    
    async def add_supplier(
        self,
        name: str,
        contact_info: Dict[str, str],
        product_categories: List[str],
        warehouse_locations: List[str],
        shipping_methods: List[str],
        api_credentials: Optional[Dict] = None
    ) -> Supplier:
        """Add new drop shipping supplier"""
        supplier_id = f"SUP_{name.replace(' ', '_').upper()}"
        
        supplier = Supplier(
            supplier_id=supplier_id,
            name=name,
            contact_info=contact_info,
            product_categories=product_categories,
            api_endpoint=api_credentials.get("endpoint") if api_credentials else None,
            api_key=api_credentials.get("api_key") if api_credentials else None,
            shipping_methods=shipping_methods,
            average_processing_time=2,  # Default 2 days
            average_shipping_time=14,  # Default 14 days
            quality_rating=4.0,
            reliability_score=85.0,
            pricing_tier="standard",
            warehouse_locations=warehouse_locations,
            ships_to=["US", "CA", "UK", "EU", "AU"]  # Default
        )
        
        self.suppliers[supplier_id] = supplier
        self.supplier_metrics[supplier_id] = {
            "total_orders": 0,
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "average_fulfillment_time": 0,
            "customer_satisfaction": 0
        }
        
        return supplier
    
    async def sync_product_catalog(
        self,
        supplier_id: str
    ) -> Dict[str, Any]:
        """
        Sync product catalog from supplier
        
        Fetches products, inventory levels, pricing via API
        """
        supplier = self.suppliers.get(supplier_id)
        if not supplier:
            raise ValueError("Supplier not found")
        
        if not supplier.api_endpoint:
            return {"error": "Supplier has no API integration"}
        
        # In production: Call supplier API
        # Mock sync
        new_products = 0
        updated_products = 0
        
        # Mock product data
        mock_products = [
            {
                "product_id": f"PROD_{supplier_id}_001",
                "name": "Wireless Bluetooth Headphones",
                "sku": "WBH-001",
                "cost_price": 15.00,
                "suggested_retail": 49.99,
                "stock": 150,
                "category": "Electronics"
            },
            {
                "product_id": f"PROD_{supplier_id}_002",
                "name": "Phone Case - iPhone 15",
                "sku": "PC-IP15-001",
                "cost_price": 3.50,
                "suggested_retail": 19.99,
                "stock": 500,
                "category": "Accessories"
            }
        ]
        
        for prod_data in mock_products:
            product_id = prod_data["product_id"]
            
            if product_id in self.products:
                # Update existing
                product = self.products[product_id]
                product.stock_quantity = prod_data["stock"]
                product.cost_price = Decimal(str(prod_data["cost_price"]))
                updated_products += 1
            else:
                # Add new
                product = Product(
                    product_id=product_id,
                    supplier_id=supplier_id,
                    name=prod_data["name"],
                    description="",
                    sku=prod_data["sku"],
                    category=prod_data["category"],
                    cost_price=Decimal(str(prod_data["cost_price"])),
                    suggested_retail=Decimal(str(prod_data["suggested_retail"])),
                    stock_quantity=prod_data["stock"],
                    stock_status="in_stock" if prod_data["stock"] > 20 else "low_stock"
                )
                self.products[product_id] = product
                new_products += 1
        
        return {
            "supplier": supplier_id,
            "new_products": new_products,
            "updated_products": updated_products,
            "sync_time": datetime.utcnow().isoformat()
        }
    
    async def create_order(
        self,
        customer_id: str,
        items: List[Dict[str, Any]],
        shipping_address: Dict[str, str]
    ) -> DropShipOrder:
        """
        Create drop shipping order
        
        Automatically routes to best suppliers based on:
        - Product availability
        - Shipping destination
        - Supplier reliability
        - Cost optimization
        """
        order_id = f"DSO_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate pricing
        subtotal = Decimal("0")
        supplier_assignments = {}
        
        for item in items:
            product_id = item["product_id"]
            quantity = item.get("quantity", 1)
            
            product = self.products.get(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")
            
            # Assign to supplier
            supplier_assignments[product_id] = product.supplier_id
            
            # Calculate line total
            retail_price = Decimal(str(item.get("price", product.suggested_retail)))
            line_total = retail_price * quantity
            subtotal += line_total
        
        # Calculate shipping
        shipping_cost = await self._calculate_shipping(items, shipping_address)
        
        # Calculate tax (simplified)
        tax_rate = Decimal("0.08")  # 8% default
        tax = subtotal * tax_rate
        
        total = subtotal + shipping_cost + tax
        
        order = DropShipOrder(
            order_id=order_id,
            customer_id=customer_id,
            items=items,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            total=total,
            supplier_assignments=supplier_assignments,
            shipping_address=shipping_address
        )
        
        self.orders[order_id] = order
        
        return order
    
    async def _calculate_shipping(
        self,
        items: List[Dict[str, Any]],
        destination: Dict[str, str]
    ) -> Decimal:
        """Calculate shipping cost based on items and destination"""
        # In production: Use shipping APIs (EasyPost, ShipStation, etc.)
        
        total_weight = Decimal("0")
        for item in items:
            product = self.products.get(item["product_id"])
            if product:
                total_weight += product.weight_kg * item.get("quantity", 1)
        
        # Base rate + weight
        base_rate = Decimal("5.00")
        weight_rate = total_weight * Decimal("2.00")  # $2 per kg
        
        return base_rate + weight_rate
    
    async def route_to_supplier(self, order_id: str) -> Dict[str, Any]:
        """
        Route order to supplier for fulfillment
        
        Sends order details to supplier API
        """
        order = self.orders.get(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Group items by supplier
        supplier_items: Dict[str, List[Dict]] = {}
        for item in order.items:
            supplier_id = order.supplier_assignments.get(item["product_id"])
            if supplier_id:
                if supplier_id not in supplier_items:
                    supplier_items[supplier_id] = []
                supplier_items[supplier_id].append(item)
        
        # Send to each supplier
        results = []
        for supplier_id, items in supplier_items.items():
            supplier = self.suppliers.get(supplier_id)
            if supplier and supplier.api_endpoint:
                # In production: Call supplier API
                results.append({
                    "supplier": supplier_id,
                    "status": "submitted",
                    "items_count": len(items)
                })
        
        order.order_status = OrderStatus.CONFIRMED
        order.confirmed_at = datetime.utcnow()
        
        return {
            "order_id": order_id,
            "suppliers_notified": len(results),
            "details": results
        }
    
    async def update_fulfillment(
        self,
        order_id: str,
        status: FulfillmentStatus,
        tracking_number: str = "",
        carrier: str = ""
    ) -> DropShipOrder:
        """Update order fulfillment status"""
        order = self.orders.get(order_id)
        if not order:
            raise ValueError("Order not found")
        
        order.fulfillment_status = status
        
        if tracking_number:
            order.tracking_number = tracking_number
        if carrier:
            order.carrier = carrier
        
        if status == FulfillmentStatus.SHIPPED:
            order.order_status = OrderStatus.SHIPPED
            order.shipped_at = datetime.utcnow()
        elif status == FulfillmentStatus.DELIVERED:
            order.order_status = OrderStatus.DELIVERED
            order.delivered_at = datetime.utcnow()
        
        return order
    
    async def calculate_profit(
        self,
        order_id: str
    ) -> Dict[str, Any]:
        """Calculate profit margin for drop shipping order"""
        order = self.orders.get(order_id)
        if not order:
            return {"error": "Order not found"}
        
        # Calculate costs
        product_costs = Decimal("0")
        for item in order.items:
            product = self.products.get(item["product_id"])
            if product:
                product_costs += product.cost_price * item.get("quantity", 1)
        
        total_costs = product_costs + order.shipping_cost + (order.total * Decimal("0.03"))  # 3% platform fee
        
        # Revenue
        revenue = order.subtotal
        
        # Profit
        gross_profit = revenue - product_costs
        net_profit = revenue - total_costs
        
        return {
            "order_id": order_id,
            "revenue": float(revenue),
            "costs": {
                "products": float(product_costs),
                "shipping": float(order.shipping_cost),
                "platform_fee": float(order.total * Decimal("0.03")),
                "total": float(total_costs)
            },
            "profit": {
                "gross": float(gross_profit),
                "net": float(net_profit),
                "margin_pct": float((net_profit / revenue) * 100) if revenue > 0 else 0
            }
        }
    
    async def get_supplier_performance(
        self,
        supplier_id: str
    ) -> Dict[str, Any]:
        """Get performance metrics for supplier"""
        supplier = self.suppliers.get(supplier_id)
        metrics = self.supplier_metrics.get(supplier_id, {})
        
        if not supplier:
            return {"error": "Supplier not found"}
        
        # Calculate derived metrics
        success_rate = 0
        if metrics.get("total_orders", 0) > 0:
            success_rate = metrics["successful_deliveries"] / metrics["total_orders"] * 100
        
        return {
            "supplier_id": supplier_id,
            "name": supplier.name,
            "reliability_score": supplier.reliability_score,
            "quality_rating": supplier.quality_rating,
            "metrics": {
                "total_orders": metrics.get("total_orders", 0),
                "successful_deliveries": metrics.get("successful_deliveries", 0),
                "success_rate_pct": round(success_rate, 2),
                "average_fulfillment_days": metrics.get("average_fulfillment_time", 0)
            },
            "products_count": len([p for p in self.products.values() if p.supplier_id == supplier_id]),
            "avg_processing_time": supplier.average_processing_time,
            "avg_shipping_time": supplier.average_shipping_time
        }
    
    async def find_best_supplier(
        self,
        product_category: str,
        destination_country: str
    ) -> Optional[str]:
        """
        Find best supplier for product and destination
        
        Considers:
        - Product category match
        - Ships to destination
        - Reliability score
        - Stock availability
        """
        candidates = []
        
        for supplier in self.suppliers.values():
            if not supplier.is_active:
                continue
            
            # Check product category
            if product_category not in supplier.product_categories:
                continue
            
            # Check shipping
            if destination_country not in supplier.ships_to:
                continue
            
            # Score
            score = supplier.reliability_score + (supplier.quality_rating * 10)
            
            candidates.append((supplier.supplier_id, score))
        
        if not candidates:
            return None
        
        # Return highest scoring
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
