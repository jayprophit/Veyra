"""Mushroom Cultivation Economics - Production cost analysis and ROI"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class CultivationBatch:
    batch_id: str
    mushroom_type: str
    substrate_cost: float
    labor_hours: float
    harvest_yield_kg: float
    market_price_per_kg: float
    start_date: datetime
    harvest_date: Optional[datetime] = None

class CultivationEconomics:
    """Analyze mushroom cultivation profitability and economics"""
    
    def __init__(self):
        self.batches: List[CultivationBatch] = []
        self.labor_rate = 15.0  # $/hour
    
    def add_batch(self, batch: CultivationBatch):
        self.batches.append(batch)
    
    def calculate_batch_profit(self, batch: CultivationBatch) -> Dict:
        labor_cost = batch.labor_hours * self.labor_rate
        total_cost = batch.substrate_cost + labor_cost
        revenue = batch.harvest_yield_kg * batch.market_price_per_kg
        profit = revenue - total_cost
        
        return {
            'batch_id': batch.batch_id,
            'mushroom_type': batch.mushroom_type,
            'revenue': round(revenue, 2),
            'substrate_cost': round(batch.substrate_cost, 2),
            'labor_cost': round(labor_cost, 2),
            'total_cost': round(total_cost, 2),
            'profit': round(profit, 2),
            'profit_margin': round(profit / revenue * 100, 1) if revenue else 0,
            'yield_per_hour': round(batch.harvest_yield_kg / batch.labor_hours, 2) if batch.labor_hours else 0
        }
    
    def get_summary(self) -> Dict:
        if not self.batches:
            return {'status': 'NO_DATA'}
        
        total_revenue = sum(b.harvest_yield_kg * b.market_price_per_kg for b in self.batches)
        total_cost = sum(b.substrate_cost + b.labor_hours * self.labor_rate for b in self.batches)
        total_profit = total_revenue - total_cost
        
        by_type = {}
        for b in self.batches:
            if b.mushroom_type not in by_type:
                by_type[b.mushroom_type] = {'batches': 0, 'revenue': 0, 'cost': 0}
            by_type[b.mushroom_type]['batches'] += 1
            by_type[b.mushroom_type]['revenue'] += b.harvest_yield_kg * b.market_price_per_kg
            by_type[b.mushroom_type]['cost'] += b.substrate_cost + b.labor_hours * self.labor_rate
        
        return {
            'total_batches': len(self.batches),
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_profit, 2),
            'profit_margin': round(total_profit / total_revenue * 100, 1) if total_revenue else 0,
            'by_mushroom_type': by_type
        }
