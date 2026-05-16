"""Product Management for Digital Marketplace"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import uuid

class ProductType(Enum):
    DIGITAL = "digital"
    SUBSCRIPTION = "subscription"
    SERVICE = "service"

@dataclass
class Product:
    id: str
    vendor_id: str
    name: str
    description: str
    type: ProductType
    price: float
    currency: str
    category: str
    tags: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

class ProductManager:
    def __init__(self):
        self._products: Dict[str, Product] = {}
    
    def create_product(self, vendor_id: str, name: str, description: str,
                      product_type: ProductType, price: float, 
                      category: str, currency: str = "USD") -> Product:
        product = Product(
            id=str(uuid.uuid4()),
            vendor_id=vendor_id,
            name=name,
            description=description,
            type=product_type,
            price=price,
            currency=currency,
            category=category
        )
        self._products[product.id] = product
        return product
    
    def get_products(self, category: Optional[str] = None, 
                    vendor_id: Optional[str] = None) -> List[Product]:
        products = list(self._products.values())
        if category:
            products = [p for p in products if p.category == category]
        if vendor_id:
            products = [p for p in products if p.vendor_id == vendor_id]
        return [p for p in products if p.is_active]
    
    def get_product(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)
