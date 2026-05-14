"""Tax Optimizer - Tax-loss harvesting and tax-efficient trading"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Position:
    symbol: str
    quantity: int
    cost_basis: float
    current_price: float
    purchase_date: datetime

@dataclass
class TaxLossOpportunity:
    symbol: str
    unrealized_loss: float
    loss_pct: float
    harvest_value: float
    replacement_candidates: List[str]
    days_held: int

class TaxOptimizer:
    """Optimize portfolio for tax efficiency"""
    
    def __init__(self, tax_bracket: float = 0.35):
        self.tax_bracket = tax_bracket  # Short-term capital gains rate
        self.long_term_rate = 0.15  # Long-term capital gains rate
        self.wash_sale_window = 30  # days
        self.positions: List[Position] = []
        self.realized_gains_ytd: float = 0
        self.realized_losses_ytd: float = 0
    
    def add_position(self, position: Position):
        """Add position to track"""
        self.positions.append(position)
    
    def find_tax_loss_opportunities(self, 
                                   min_loss_pct: float = 5.0) -> List[TaxLossOpportunity]:
        """Find positions with unrealized losses suitable for harvesting"""
        opportunities = []
        
        for pos in self.positions:
            unrealized_pnl = (pos.current_price - pos.cost_basis) * pos.quantity
            
            if unrealized_pnl >= 0:
                continue  # Only losses
            
            loss_pct = abs(unrealized_pnl) / (pos.cost_basis * pos.quantity) * 100
            
            if loss_pct < min_loss_pct:
                continue  # Too small to harvest
            
            days_held = (datetime.utcnow() - pos.purchase_date).days
            
            # Find similar ETFs/funds as replacement
            replacements = self._find_replacements(pos.symbol)
            
            opportunities.append(TaxLossOpportunity(
                symbol=pos.symbol,
                unrealized_loss=abs(unrealized_pnl),
                loss_pct=loss_pct,
                harvest_value=abs(unrealized_pnl) * self.tax_bracket,
                replacement_candidates=replacements,
                days_held=days_held
            ))
        
        return sorted(opportunities, key=lambda x: x.harvest_value, reverse=True)
    
    def _find_replacements(self, symbol: str) -> List[str]:
        """Find replacement securities to avoid wash sale"""
        # Sector-based replacements (simplified)
        replacements = {
            "AAPL": ["QQQ", "VGT", "FTEC"],  # Tech ETFs
            "MSFT": ["QQQ", "VGT", "XLK"],
            "JPM": ["XLF", "VFH", "KRE"],   # Financial ETFs
            "XOM": ["XLE", "VDE", "USO"],   # Energy ETFs
            "JNJ": ["XLV", "VHT", "IYH"],   # Healthcare ETFs
            "TSLA": ["ARKK", "DRIV", "LIT"] # Disruption/EV ETFs
        }
        
        return replacements.get(symbol, ["SPY", "VTI"])  # Default to broad market
    
    def calculate_tax_harvesting_plan(self, 
                                    target_harvest: float = 50000) -> Dict:
        """Create tax-loss harvesting plan"""
        opportunities = self.find_tax_loss_opportunities()
        
        if not opportunities:
            return {"message": "No tax-loss harvesting opportunities found"}
        
        plan = []
        total_harvested = 0
        total_tax_savings = 0
        
        for opp in opportunities:
            if total_harvested >= target_harvest:
                break
            
            # Check for wash sale risk
            wash_sale_risk = "HIGH" if opp.days_held < 30 else "LOW"
            
            action = {
                "symbol": opp.symbol,
                "unrealized_loss": round(opp.unrealized_loss, 2),
                "tax_savings": round(opp.harvest_value, 2),
                "replacement": opp.replacement_candidates[0] if opp.replacement_candidates else None,
                "wash_sale_risk": wash_sale_risk,
                "recommended_action": "HARVEST_NOW" if wash_sale_risk == "LOW" else "WAIT_30_DAYS"
            }
            
            plan.append(action)
            total_harvested += opp.unrealized_loss
            total_tax_savings += opp.harvest_value
        
        return {
            "opportunities_found": len(opportunities),
            "harvest_plan": plan,
            "total_losses_available": round(total_harvested, 2),
            "total_tax_savings": round(total_tax_savings, 2),
            "net_benefit": round(total_tax_savings * 0.9, 2)  # Account for transaction costs
        }
    
    def optimize_gain_realization(self, 
                                  desired_gains: float = 10000) -> Dict:
        """Optimize which gains to realize for tax purposes"""
        # Find positions with gains
        gain_positions = []
        
        for pos in self.positions:
            unrealized = (pos.current_price - pos.cost_basis) * pos.quantity
            if unrealized > 0:
                days_held = (datetime.utcnow() - pos.purchase_date).days
                tax_rate = self.long_term_rate if days_held > 365 else self.tax_bracket
                
                gain_positions.append({
                    "symbol": pos.symbol,
                    "unrealized_gain": unrealized,
                    "days_held": days_held,
                    "tax_rate": tax_rate,
                    "after_tax_gain": unrealized * (1 - tax_rate)
                })
        
        # Sort by lowest tax rate first (tax-efficient realization)
        gain_positions.sort(key=lambda x: (x["tax_rate"], -x["unrealized_gain"]))
        
        plan = []
        accumulated_gains = 0
        
        for pos in gain_positions:
            if accumulated_gains >= desired_gains:
                break
            
            plan.append({
                "symbol": pos["symbol"],
                "realize_amount": min(pos["unrealized_gain"], desired_gains - accumulated_gains),
                "tax_rate": pos["tax_rate"],
                "tax_efficiency": "HIGH" if pos["tax_rate"] == self.long_term_rate else "LOW"
            })
            accumulated_gains += pos["unrealized_gain"]
        
        return {
            "gain_realization_plan": plan,
            "total_gains_to_realize": round(accumulated_gains, 2),
            "estimated_tax": round(sum(p["realize_amount"] * p["tax_rate"] for p in plan), 2)
        }
    
    def get_tax_summary(self) -> Dict:
        """Get year-to-date tax summary"""
        net_realized = self.realized_gains_ytd - self.realized_losses_ytd
        
        # Calculate unrealized
        total_unrealized = 0
        short_term_unrealized = 0
        long_term_unrealized = 0
        
        for pos in self.positions:
            unrealized = (pos.current_price - pos.cost_basis) * pos.quantity
            total_unrealized += unrealized
            
            days_held = (datetime.utcnow() - pos.purchase_date).days
            if days_held < 365:
                short_term_unrealized += unrealized
            else:
                long_term_unrealized += unrealized
        
        return {
            "realized_gains_ytd": round(self.realized_gains_ytd, 2),
            "realized_losses_ytd": round(self.realized_losses_ytd, 2),
            "net_realized_pnl": round(net_realized, 2),
            "unrealized_gains": round(max(0, total_unrealized), 2),
            "unrealized_losses": round(abs(min(0, total_unrealized)), 2),
            "short_term_exposure": round(short_term_unrealized, 2),
            "long_term_exposure": round(long_term_unrealized, 2),
            "harvesting_opportunity": round(abs(min(0, total_unrealized)), 2),
            "estimated_tax_liability": round(max(0, net_realized) * 0.25, 2)
        }

from datetime import timedelta
