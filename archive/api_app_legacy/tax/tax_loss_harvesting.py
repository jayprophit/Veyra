"""
Tax-Loss Harvesting System
Automated tax optimization through strategic loss realization
Inspired by Wealthfront, Betterment, Personal Capital
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum


class HarvestStatus(Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    REPLACED = "replaced"
    REJECTED = "rejected"


@dataclass
class HarvestOpportunity:
    """Potential tax-loss harvesting opportunity"""
    opportunity_id: str
    user_id: str
    symbol: str
    
    # Position details
    quantity: Decimal
    cost_basis: Decimal  # Average purchase price
    current_price: Decimal
    
    # Loss calculation
    unrealized_loss: Decimal
    unrealized_loss_pct: float
    
    # Tax benefit estimate
    estimated_tax_savings: Decimal  # Based on tax bracket
    tax_bracket_applied: float
    
    # Wash sale prevention
    replacement_symbol: Optional[str]  # Similar but not "substantially identical"
    days_since_purchase: int
    wash_sale_risk: str  # "low", "medium", "high"
    
    # Metadata
    status: HarvestStatus = HarvestStatus.PENDING
    created_at: datetime = None
    executed_at: Optional[datetime] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def is_wash_sale_violation(self) -> bool:
        """Check if harvesting would trigger wash sale rule"""
        return self.days_since_purchase < 30


@dataclass
class HarvestedLoss:
    """Record of executed tax-loss harvest"""
    id: str
    user_id: str
    opportunity_id: str
    
    # Original position
    symbol: str
    quantity: Decimal
    cost_basis: Decimal
    sale_price: Decimal
    
    # Loss details
    realized_loss: Decimal
    tax_savings: Decimal
    
    # Replacement (if applicable)
    replacement_symbol: Optional[str]
    replacement_quantity: Optional[Decimal]
    replacement_price: Optional[Decimal]
    
    # Dates
    harvested_at: datetime
    year: int  # Tax year
    
    # Wash sale tracking
    wash_sale_adjusted_basis: Optional[Decimal] = None
    wash_sale_disallowed_loss: Decimal = Decimal("0")


class TaxLossHarvestingManager:
    """
    Automated tax-loss harvesting system
    
    Monitors portfolio for unrealized losses and:
    1. Identifies harvesting opportunities
    2. Calculates tax savings
    3. Prevents wash sale violations
    4. Suggests replacement securities
    5. Automates execution (if enabled)
    """
    
    # Minimum loss threshold to consider ($100)
    MIN_LOSS_THRESHOLD = Decimal("100")
    
    # Maximum loss threshold (don't harvest huge losses at once)
    MAX_LOSS_PER_HARVEST = Decimal("3000")  # Match annual deduction limit
    
    def __init__(self):
        self.opportunities: Dict[str, HarvestOpportunity] = {}
        self.harvested_losses: List[HarvestedLoss] = []
        self.recent_purchases: Dict[str, datetime] = {}  # symbol -> last purchase date
        
        # Replacement ETF mappings (avoid wash sales)
        self.replacement_map = {
            # US Large Cap
            "SPY": "VTI",  # SP500 -> Total Market
            "VOO": "VV",   # SP500 -> Large Cap
            "VTI": "ITOT", # Total Market -> different provider
            
            # US Small Cap
            "IWM": "VB",   # Russell 2000 -> Small Cap
            "VB": "VBR",   # Small Cap -> Small Cap Value
            
            # International
            "VEA": "IEFA", # Developed Markets
            "VWO": "IEMG", # Emerging Markets
            
            # Bonds
            "BND": "AGG",  # Total Bond Market
            "AGG": "SCHZ", # Different provider
            
            # Individual stocks (sector-based replacements)
            "AAPL": "VGT",  # Apple -> Tech ETF
            "MSFT": "VGT",  # Microsoft -> Tech ETF
            "JPM": "VFH",   # JPMorgan -> Financials ETF
            "XOM": "VDE",   # Exxon -> Energy ETF
        }
    
    async def scan_for_opportunities(
        self,
        user_id: str,
        holdings: Dict[str, Dict[str, Any]],
        tax_bracket: float = 0.25
    ) -> List[HarvestOpportunity]:
        """
        Scan portfolio for tax-loss harvesting opportunities
        
        Args:
            user_id: User to scan
            holdings: Current positions {symbol: {quantity, cost_basis, current_price}}
            tax_bracket: Marginal tax bracket for savings calculation
        """
        opportunities = []
        
        for symbol, position in holdings.items():
            quantity = Decimal(str(position.get("quantity", 0)))
            cost_basis = Decimal(str(position.get("cost_basis", 0)))
            current_price = Decimal(str(position.get("current_price", 0)))
            
            if quantity <= 0:
                continue
            
            # Calculate unrealized loss
            current_value = quantity * current_price
            cost_value = quantity * cost_basis
            unrealized_loss = cost_value - current_value
            
            # Check if it's a loss and meets threshold
            if unrealized_loss >= self.MIN_LOSS_THRESHOLD:
                unrealized_loss_pct = float((current_price - cost_basis) / cost_basis * 100)
                
                # Calculate tax savings
                estimated_savings = unrealized_loss * Decimal(str(tax_bracket))
                
                # Check wash sale risk
                days_since_purchase = self._get_days_since_purchase(symbol)
                wash_sale_risk = "high" if days_since_purchase < 30 else "low"
                
                # Find replacement
                replacement = self.replacement_map.get(symbol)
                
                opportunity = HarvestOpportunity(
                    opportunity_id=f"harvest_{user_id}_{symbol}_{datetime.utcnow().timestamp()}",
                    user_id=user_id,
                    symbol=symbol,
                    quantity=quantity,
                    cost_basis=cost_basis,
                    current_price=current_price,
                    unrealized_loss=unrealized_loss,
                    unrealized_loss_pct=unrealized_loss_pct,
                    estimated_tax_savings=estimated_savings,
                    tax_bracket_applied=tax_bracket,
                    replacement_symbol=replacement,
                    days_since_purchase=days_since_purchase,
                    wash_sale_risk=wash_sale_risk,
                    notes=f"Potential tax savings: ${estimated_savings:.2f}"
                )
                
                opportunities.append(opportunity)
                self.opportunities[opportunity.opportunity_id] = opportunity
        
        # Sort by estimated tax savings (highest first)
        opportunities.sort(key=lambda x: x.estimated_tax_savings, reverse=True)
        
        return opportunities
    
    async def execute_harvest(
        self,
        opportunity_id: str,
        auto_replace: bool = True
    ) -> Optional[HarvestedLoss]:
        """
        Execute a tax-loss harvest
        
        1. Sell the losing position
        2. Record the loss for tax purposes
        3. Optionally buy replacement (different security)
        """
        if opportunity_id not in self.opportunities:
            return None
        
        opp = self.opportunities[opportunity_id]
        
        # Check wash sale
        if opp.is_wash_sale_violation:
            opp.status = HarvestStatus.REJECTED
            opp.notes = "Wash sale violation - must wait 30 days"
            return None
        
        # Execute sale (mock)
        sale_price = opp.current_price  # In production: actual execution price
        realized_loss = opp.unrealized_loss
        
        harvested = HarvestedLoss(
            id=f"loss_{opp.user_id}_{opp.symbol}_{datetime.utcnow().timestamp()}",
            user_id=opp.user_id,
            opportunity_id=opportunity_id,
            symbol=opp.symbol,
            quantity=opp.quantity,
            cost_basis=opp.cost_basis,
            sale_price=sale_price,
            realized_loss=realized_loss,
            tax_savings=opp.estimated_tax_savings,
            replacement_symbol=None,
            replacement_quantity=None,
            replacement_price=None,
            harvested_at=datetime.utcnow(),
            year=datetime.utcnow().year
        )
        
        # Execute replacement if specified
        if auto_replace and opp.replacement_symbol:
            # Buy replacement with proceeds
            proceeds = opp.quantity * sale_price
            replacement_qty = proceeds / sale_price  # Assume similar price
            
            harvested.replacement_symbol = opp.replacement_symbol
            harvested.replacement_quantity = replacement_qty
            harvested.replacement_price = sale_price
            
            opp.status = HarvestStatus.REPLACED
        else:
            opp.status = HarvestStatus.EXECUTED
        
        opp.executed_at = datetime.utcnow()
        self.harvested_losses.append(harvested)
        
        return harvested
    
    async def get_yearly_tax_summary(
        self,
        user_id: str,
        year: int = None
    ) -> Dict[str, Any]:
        """
        Get tax-loss harvesting summary for tax year
        
        Shows total losses harvested and tax savings
        """
        if year is None:
            year = datetime.utcnow().year
        
        user_losses = [
            h for h in self.harvested_losses
            if h.user_id == user_id and h.year == year
        ]
        
        total_losses = sum(h.realized_loss for h in user_losses)
        total_savings = sum(h.tax_savings for h in user_losses)
        
        # Group by symbol
        by_symbol = {}
        for h in user_losses:
            if h.symbol not in by_symbol:
                by_symbol[h.symbol] = {"count": 0, "total_loss": Decimal("0")}
            by_symbol[h.symbol]["count"] += 1
            by_symbol[h.symbol]["total_loss"] += h.realized_loss
        
        return {
            "year": year,
            "user_id": user_id,
            "total_harvests": len(user_losses),
            "total_realized_losses": float(total_losses),
            "estimated_tax_savings": float(total_savings),
            "remaining_deduction_limit": float(max(Decimal("3000") - total_losses, Decimal("0"))),
            "harvests_by_symbol": {
                sym: {
                    "count": data["count"],
                    "total_loss": float(data["total_loss"])
                }
                for sym, data in by_symbol.items()
            },
            "replacement_summary": {
                "total_replacements": len([h for h in user_losses if h.replacement_symbol]),
                "replacement_symbols_used": list(set(
                    h.replacement_symbol for h in user_losses if h.replacement_symbol
                ))
            }
        }
    
    async def should_harvest(
        self,
        user_id: str,
        symbol: str,
        current_price: float,
        cost_basis: float
    ) -> Dict[str, Any]:
        """Quick check if a position should be harvested"""
        unrealized_loss = cost_basis - current_price
        
        if unrealized_loss < float(self.MIN_LOSS_THRESHOLD):
            return {
                "should_harvest": False,
                "reason": "Loss below threshold",
                "unrealized_loss": unrealized_loss
            }
        
        days_held = self._get_days_since_purchase(symbol)
        
        if days_held < 30:
            return {
                "should_harvest": False,
                "reason": "Wash sale violation risk",
                "days_until_eligible": 30 - days_held,
                "unrealized_loss": unrealized_loss
            }
        
        # Calculate tax benefit
        # Assume 25% bracket - in production: get from user profile
        tax_savings = unrealized_loss * 0.25
        
        return {
            "should_harvest": True,
            "unrealized_loss": unrealized_loss,
            "unrealized_loss_pct": (unrealized_loss / cost_basis) * 100,
            "estimated_tax_savings": tax_savings,
            "days_held": days_held,
            "replacement_suggestion": self.replacement_map.get(symbol)
        }
    
    def _get_days_since_purchase(self, symbol: str) -> int:
        """Get days since last purchase (for wash sale check)"""
        if symbol in self.recent_purchases:
            delta = datetime.utcnow() - self.recent_purchases[symbol]
            return delta.days
        return 999  # Assume held long time if no record
