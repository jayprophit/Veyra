"""Precision Fermentation - Lab-grown protein production"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class FermentationBatch:
    batch_id: str
    product_type: str  # 'dairy_protein', 'egg_protein', 'collagen'
    volume_liters: float
    production_cost_per_liter: float
    yield_grams_per_liter: float
    market_price_per_gram: float

class PrecisionFermentation:
    def __init__(self):
        self.batches: List[FermentationBatch] = []
    
    def add(self, b: FermentationBatch):
        self.batches.append(b)
    
    def calculate_profitability(self, b: FermentationBatch) -> Dict:
        total_production_cost = b.volume_liters * b.production_cost_per_liter
        total_yield_grams = b.volume_liters * b.yield_grams_per_liter
        revenue = total_yield_grams * b.market_price_per_gram
        profit = revenue - total_production_cost
        
        return {
            'batch_id': b.batch_id,
            'product': b.product_type,
            'revenue': round(revenue, 2),
            'production_cost': round(total_production_cost, 2),
            'profit': round(profit, 2),
            'margin_pct': round(profit / revenue * 100, 1) if revenue else 0,
            'yield_kg': round(total_yield_grams / 1000, 2)
        }
    
    def get_summary(self) -> Dict:
        if not self.batches:
            return {'status': 'NO_BATCHES'}
        
        by_product = {}
        for b in self.batches:
            if b.product_type not in by_product:
                by_product[b.product_type] = {'batches': 0, 'volume': 0, 'revenue': 0}
            by_product[b.product_type]['batches'] += 1
            by_product[b.product_type]['volume'] += b.volume_liters
            total_yield = b.volume_liters * b.yield_grams_per_liter
            by_product[b.product_type]['revenue'] += total_yield * b.market_price_per_gram
        
        return {
            'total_batches': len(self.batches),
            'total_volume_liters': sum(b.volume_liters for b in self.batches),
            'by_product_type': by_product
        }
