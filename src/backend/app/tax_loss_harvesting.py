"""Veyra - Tax-Loss Harvesting Automation. UK CGT optimization."""

import json, sqlite3
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TaxLossHarvesting')

class WashSaleStatus(Enum):
    CLEAN = "clean"           # No wash sale issue
    PENDING = "pending"       # Within 30 days, waiting
    VIOLATION = "violation"   # Would violate wash sale rule

@dataclass
class HarvestOpportunity:
    """A tax-loss harvesting opportunity."""
    ticker: str
    account_type: str
    shares_available: float
    current_price: float
    avg_cost: float
    unrealized_loss: float
    loss_per_share: float
    cgt_savings: float  # At 20% CGT rate
    wash_sale_status: WashSaleStatus
    days_since_last_buy: Optional[int] = None
    replacement_candidates: List[str] = None
    bed_and_isa_eligible: bool = False

@dataclass
class HarvestAction:
    """A specific tax-loss harvesting action."""
    action_id: str
    ticker: str
    account_type: str
    action_type: str  # "SELL", "BUY_SIMILAR", "BED_ISA"
    shares: float
    expected_proceeds: float
    realized_loss: float
    cgt_savings: float
    replacement_ticker: Optional[str] = None
    status: str = "proposed"  # proposed, approved, executed, rejected
    execution_date: Optional[date] = None

class TaxLossHarvester:
    """
    Automated tax-loss harvesting for UK portfolios.
    
    Rules implemented:
    - 30-day rule (UK wash sale): Can't rebuy same asset within 30 days
    - CGT allowance tracking: Harvest up to £3,000 allowance
    - Bed & ISA: Move assets from GIA to ISA to crystallize loss
    - Same fund replacement: Use similar (not identical) ETFs
    """
    
    def __init__(self, db_connection: sqlite3.Connection, cgt_allowance: float = 3000.0):
        self.conn = db_connection
        self.cgt_allowance = cgt_allowance
        self.cgt_rate = 0.20  # 20% for higher rate taxpayers
        self.wash_sale_days = 30
    
    def find_opportunities(self) -> List[HarvestOpportunity]:
        """Find all tax-loss harvesting opportunities in current holdings."""
        opportunities = []
        
        # Get all holdings with unrealized losses
        holdings = self.conn.execute("""
            SELECT ticker, account_type, shares, avg_cost, current_price
            FROM holdings
            WHERE shares > 0 AND current_price IS NOT NULL
        """).fetchall()
        
        for h in holdings:
            ticker, account_type, shares, avg_cost, current_price = h
            
            if not current_price or current_price >= avg_cost:
                continue  # No loss
            
            loss_per_share = avg_cost - current_price
            total_loss = loss_per_share * shares
            
            # Check wash sale status
            wash_status, days_since_buy = self._check_wash_sale_status(ticker, account_type)
            
            # Find replacement candidates (similar funds)
            replacements = self._find_replacements(ticker)
            
            # Check Bed & ISA eligibility
            bed_isa_eligible = (account_type == "GIA" and total_loss > 0)
            
            opp = HarvestOpportunity(
                ticker=ticker,
                account_type=account_type,
                shares_available=shares,
                current_price=current_price,
                avg_cost=avg_cost,
                unrealized_loss=total_loss,
                loss_per_share=loss_per_share,
                cgt_savings=total_loss * self.cgt_rate,
                wash_sale_status=wash_status,
                days_since_last_buy=days_since_buy,
                replacement_candidates=replacements,
                bed_and_isa_eligible=bed_isa_eligible
            )
            
            opportunities.append(opp)
        
        # Sort by biggest loss first
        opportunities.sort(key=lambda x: x.unrealized_loss, reverse=True)
        return opportunities
    
    def _check_wash_sale_status(self, ticker: str, account_type: str) -> Tuple[WashSaleStatus, Optional[int]]:
        """Check 30-day rule (UK version of wash sale)."""
        # Find last purchase of this ticker
        last_buy = self.conn.execute("""
            SELECT transaction_date, shares
            FROM transactions
            WHERE ticker = ? AND account_type = ? AND transaction_type = 'BUY'
            ORDER BY transaction_date DESC
            LIMIT 1
        """, (ticker, account_type)).fetchone()
        
        if not last_buy:
            return WashSaleStatus.CLEAN, None
        
        last_buy_date = datetime.strptime(last_buy[0], '%Y-%m-%d').date()
        days_since = (date.today() - last_buy_date).days
        
        if days_since < self.wash_sale_days:
            return WashSaleStatus.PENDING, days_since
        
        return WashSaleStatus.CLEAN, days_since
    
    def _find_replacements(self, ticker: str) -> List[str]:
        """Find similar ETFs/funds for replacement after sale."""
        # Mapping of funds to their replacements (similar but not identical)
        replacement_map = {
            # S&P 500 trackers
            "VUAG": ["HMWO", "IUSA", "VUSA"],  # Vanguard -> iShares/HSBC alternatives
            "VUSA": ["VUAG", "IUSA", "HMWO"],
            "IUSA": ["VUAG", "VUSA", "HMWO"],
            # Bond funds
            "AGGH": ["VAGP", "SAAA", "GLAD"],  # iShares -> Vanguard alternatives
            # Emerging markets
            "AYEM": ["VFEM", "HMEF", "EMIM"],  # Vanguard -> HSBC/iShares
            # All-world
            "HMWO": ["VWRL", "IWDA", "SWDA"],  # HSBC -> Vanguard/iShares
            "VWRL": ["HMWO", "IWDA", "VEVE"],
        }
        return replacement_map.get(ticker, [])
    
    def generate_actions(self, opportunities: Optional[List[HarvestOpportunity]] = None,
                         max_cgt_usage: Optional[float] = None) -> List[HarvestAction]:
        """Generate specific harvest actions from opportunities."""
        if opportunities is None:
            opportunities = self.find_opportunities()
        
        if not opportunities:
            return []
        
        actions = []
        cgt_remaining = max_cgt_usage or self._get_remaining_cgt_allowance()
        
        for opp in opportunities:
            if cgt_remaining <= 0:
                break
            
            # Skip if wash sale violation
            if opp.wash_sale_status == WashSaleStatus.VIOLATION:
                continue
            
            # Calculate how much to harvest
            harvestable_loss = min(opp.unrealized_loss, cgt_remaining / self.cgt_rate)
            shares_to_sell = harvestable_loss / opp.loss_per_share if opp.loss_per_share > 0 else 0
            shares_to_sell = min(shares_to_sell, opp.shares_available)
            
            if shares_to_sell < 1:  # Minimum 1 share
                continue
            
            actual_loss = shares_to_sell * opp.loss_per_share
            cgt_savings = actual_loss * self.cgt_rate
            proceeds = shares_to_sell * opp.current_price
            
            # Action 1: Sell the position
            sell_action = HarvestAction(
                action_id=f"HARVEST_{opp.ticker}_{date.today().isoformat()}",
                ticker=opp.ticker,
                account_type=opp.account_type,
                action_type="SELL",
                shares=shares_to_sell,
                expected_proceeds=proceeds,
                realized_loss=actual_loss,
                cgt_savings=cgt_savings
            )
            actions.append(sell_action)
            
            # Action 2: Buy similar fund (if not Bed & ISA)
            if opp.replacement_candidates and opp.account_type != "ISA":
                replacement = opp.replacement_candidates[0]
                buy_action = HarvestAction(
                    action_id=f"REPLACE_{opp.ticker}_{replacement}_{date.today().isoformat()}",
                    ticker=replacement,
                    account_type=opp.account_type,
                    action_type="BUY_SIMILAR",
                    shares=shares_to_sell,
                    expected_proceeds=-proceeds,  # Negative = cost
                    realized_loss=0,
                    cgt_savings=0,
                    replacement_ticker=replacement
                )
                actions.append(buy_action)
            
            # Action 3: Bed & ISA (if eligible)
            if opp.bed_and_isa_eligible:
                bed_isa_action = HarvestAction(
                    action_id=f"BEDISA_{opp.ticker}_{date.today().isoformat()}",
                    ticker=opp.ticker,
                    account_type="ISA",
                    action_type="BED_ISA",
                    shares=shares_to_sell,
                    expected_proceeds=0,  # Transfer
                    realized_loss=actual_loss,
                    cgt_savings=cgt_savings
                )
                actions.append(bed_isa_action)
            
            cgt_remaining -= cgt_savings
        
        return actions
    
    def _get_remaining_cgt_allowance(self) -> float:
        """Get remaining CGT allowance for current tax year."""
        tax_year = self._get_current_tax_year()
        row = self.conn.execute(
            "SELECT cgt_allowance_used FROM tax_records WHERE tax_year = ?",
            (tax_year,)
        ).fetchone()
        
        used = row[0] if row else 0
        return max(0, self.cgt_allowance - used)
    
    def _get_current_tax_year(self) -> str:
        """Get current UK tax year (e.g., '2024-25')."""
        today = date.today()
        if today.month < 4 or (today.month == 4 and today.day < 6):
            year = today.year - 1
        else:
            year = today.year
        return f"{year}-{(year + 1) % 100:02d}"
    
    def execute_action(self, action: HarvestAction, approved_by: str) -> bool:
        """Execute an approved harvest action."""
        try:
            if action.action_type == "SELL":
                # Record sell transaction
                self.conn.execute("""
                    INSERT INTO transactions 
                    (ticker, transaction_type, shares, price, amount, account_type, 
                     transaction_date, executed_by, notes)
                    VALUES (?, 'SELL', ?, ?, ?, ?, ?, ?, 'Tax loss harvesting')
                """, (action.ticker, action.shares, 
                      action.expected_proceeds / action.shares,
                      action.expected_proceeds, action.account_type,
                      date.today(), approved_by))
                
                # Update holdings
                self.conn.execute("""
                    UPDATE holdings 
                    SET shares = shares - ?, last_updated = CURRENT_TIMESTAMP
                    WHERE ticker = ? AND account_type = ?
                """, (action.shares, action.ticker, action.account_type))
                
                # Update CGT usage
                tax_year = self._get_current_tax_year()
                self.conn.execute("""
                    INSERT INTO tax_records (tax_year, cgt_allowance_used)
                    VALUES (?, ?)
                    ON CONFLICT(tax_year) DO UPDATE SET
                    cgt_allowance_used = cgt_allowance_used + excluded.cgt_allowance_used
                """, (tax_year, action.realized_loss))
                
            elif action.action_type == "BUY_SIMILAR":
                # Record buy of replacement
                price = abs(action.expected_proceeds) / action.shares
                self.conn.execute("""
                    INSERT INTO transactions
                    (ticker, transaction_type, shares, price, amount, account_type,
                     transaction_date, executed_by, notes)
                    VALUES (?, 'BUY', ?, ?, ?, ?, ?, ?, 'Replacement after harvest')
                """, (action.ticker, action.shares, price,
                      action.expected_proceeds, action.account_type,
                      date.today(), approved_by))
            
            self.conn.commit()
            action.status = "executed"
            action.execution_date = date.today()
            logger.info(f"✓ Executed: {action.action_type} {action.shares} {action.ticker}")
            return True
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            action.status = "failed"
            return False
    
    def get_harvest_summary(self) -> Dict:
        """Get summary of tax-loss harvesting activity."""
        tax_year = self._get_current_tax_year()
        
        # Get total harvested this year
        harvested = self.conn.execute("""
            SELECT COALESCE(SUM(realized_loss), 0)
            FROM tax_records WHERE tax_year = ?
        """, (tax_year,)).fetchone()[0]
        
        # Get remaining allowance
        remaining = self._get_remaining_cgt_allowance()
        
        # Count current opportunities
        opportunities = self.find_opportunities()
        harvestable = sum(o.unrealized_loss for o in opportunities if o.wash_sale_status != WashSaleStatus.VIOLATION)
        
        return {
            "tax_year": tax_year,
            "cgt_allowance": self.cgt_allowance,
            "cgt_used": self.cgt_allowance - remaining,
            "cgt_remaining": remaining,
            "utilization_pct": (self.cgt_allowance - remaining) / self.cgt_allowance * 100,
            "total_harvested": harvested,
            "current_opportunities": len(opportunities),
            "harvestable_losses": harvestable,
            "potential_cgt_savings": harvestable * self.cgt_rate
        }

# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Veyra - Tax-Loss Harvesting")
    print("="*60)
    
    # Connect to database
    conn = sqlite3.connect("./data/veyra.db")
    
    # Create harvester
    harvester = TaxLossHarvester(conn, cgt_allowance=3000.0)
    
    # Find opportunities
    print("\n🔍 Finding opportunities...")
    opportunities = harvester.find_opportunities()
    
    if opportunities:
        print(f"\n✓ Found {len(opportunities)} harvest opportunities:\n")
        for opp in opportunities[:5]:  # Show top 5
            status_icon = "🟢" if opp.wash_sale_status == WashSaleStatus.CLEAN else "🟡"
            print(f"{status_icon} {opp.ticker} [{opp.account_type}]")
            print(f"   Unrealized Loss: £{opp.unrealized_loss:,.2f}")
            print(f"   CGT Savings: £{opp.cgt_savings:,.2f}")
            print(f"   Wash Sale: {opp.wash_sale_status.value}")
            if opp.replacement_candidates:
                print(f"   Replacements: {', '.join(opp.replacement_candidates[:3])}")
            print()
        
        # Generate actions
        print("\n📋 Proposed Actions:")
        actions = harvester.generate_actions(opportunities)
        for action in actions[:8]:  # Show top 8
            icon = "🔴" if action.action_type == "SELL" else "🟢"
            print(f"{icon} {action.action_type}: {action.shares:.0f} {action.ticker}")
            if action.realized_loss > 0:
                print(f"   Loss: £{action.realized_loss:,.2f} | Savings: £{action.cgt_savings:,.2f}")
    else:
        print("\n✓ No tax-loss harvesting opportunities found.")
    
    # Show summary
    summary = harvester.get_harvest_summary()
    print(f"\n📊 {summary['tax_year']} Tax Year Summary:")
    print(f"   CGT Allowance: £{summary['cgt_allowance']:,.2f}")
    print(f"   Used: £{summary['cgt_used']:,.2f} ({summary['utilization_pct']:.1f}%)")
    print(f"   Remaining: £{summary['cgt_remaining']:,.2f}")
    print(f"   Harvestable Losses: £{summary['harvestable_losses']:,.2f}")
    print(f"   Potential Savings: £{summary['potential_cgt_savings']:,.2f}")
    
    conn.close()
    print("\n" + "="*60)
