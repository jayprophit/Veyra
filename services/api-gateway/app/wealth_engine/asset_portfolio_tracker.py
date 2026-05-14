"""Asset Portfolio Tracker - Tracks all assets, P&L, performance"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class AssetClass(Enum):
    CASH = 'cash'
    CRYPTO = 'crypto'
    STOCKS = 'stocks'
    BONDS = 'bonds'
    P2P = 'p2p'
    GOLD = 'gold'
    ALTERNATIVE = 'alternative'
    DEBT = 'debt'

class AssetStatus(Enum):
    ACTIVE = 'active'
    UNDERPERFORMING = 'underperforming'
    PROFITABLE = 'profitable'
    FLAGGED_EXIT = 'flagged_exit'
    EXITED = 'exited'

@dataclass
class Asset:
    asset_id: str
    symbol: str
    name: str
    asset_class: AssetClass
    quantity: float
    avg_buy_price: float
    current_price: float
    status: AssetStatus = AssetStatus.ACTIVE
    platform: str = ''
    acquired_date: datetime = None
    target_allocation_pct: float = 0.0
    
    def __post_init__(self):
        if self.acquired_date is None:
            self.acquired_date = datetime.now()
    
    @property
    def current_value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        return self.quantity * self.avg_buy_price
    
    @property
    def unrealized_pnl(self) -> float:
        return self.current_value - self.cost_basis
    
    @property
    def unrealized_pnl_pct(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100

class AssetPortfolioTracker:
    """
    Tracks all user assets across all platforms.
    Calculates real P&L, identifies underperformers.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.assets = {}  # asset_id -> Asset
        self.transactions = []
        self.platform_balances = {}
        self.rebalance_history = []
    
    def add_asset(self, asset: Asset) -> str:
        """Add new asset to portfolio"""
        self.assets[asset.asset_id] = asset
        self.transactions.append({
            'type': 'BUY',
            'asset_id': asset.asset_id,
            'quantity': asset.quantity,
            'price': asset.avg_buy_price,
            'timestamp': datetime.now()
        })
        return asset.asset_id
    
    def update_price(self, asset_id: str, new_price: float):
        """Update current market price"""
        if asset_id in self.assets:
            self.assets[asset_id].current_price = new_price
            self._update_status(asset_id)
    
    def update_all_prices(self, price_feed: Dict[str, float]):
        """Batch update prices from API feed"""
        for asset_id, price in price_feed.items():
            if asset_id in self.assets:
                self.assets[asset_id].current_price = price
                self._update_status(asset_id)
    
    def _update_status(self, asset_id: str):
        """Update asset status based on performance"""
        asset = self.assets[asset_id]
        pnl_pct = asset.unrealized_pnl_pct
        
        # Flag for exit if significant loss
        if pnl_pct < -20:
            asset.status = AssetStatus.FLAGGED_EXIT
        # Mark profitable if good gains
        elif pnl_pct > 15:
            asset.status = AssetStatus.PROFITABLE
        # Underperforming if flat or slight loss
        elif pnl_pct < -5:
            asset.status = AssetStatus.UNDERPERFORMING
        else:
            asset.status = AssetStatus.ACTIVE
    
    def get_portfolio_summary(self) -> Dict:
        """Get complete portfolio overview"""
        total_value = sum(a.current_value for a in self.assets.values())
        total_cost = sum(a.cost_basis for a in self.assets.values())
        
        by_class = {}
        for asset in self.assets.values():
            ac = asset.asset_class.value
            if ac not in by_class:
                by_class[ac] = {'value': 0, 'cost': 0, 'assets': []}
            by_class[ac]['value'] += asset.current_value
            by_class[ac]['cost'] += asset.cost_basis
            by_class[ac]['assets'].append({
                'symbol': asset.symbol,
                'value': asset.current_value,
                'pnl': asset.unrealized_pnl,
                'pnl_pct': asset.unrealized_pnl_pct,
                'status': asset.status.value
            })
        
        # Sort by P&L within each class
        for ac in by_class:
            by_class[ac]['assets'].sort(key=lambda x: x['pnl_pct'], reverse=True)
        
        return {
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'total_unrealized_pnl': round(total_value - total_cost, 2),
            'total_pnl_pct': round(((total_value - total_cost) / max(total_cost, 1)) * 100, 2),
            'num_assets': len(self.assets),
            'by_asset_class': by_class,
            'winners': self._get_top_performers(3),
            'losers': self._get_worst_performers(3),
            'flagged_for_exit': self._get_flagged_assets()
        }
    
    def _get_top_performers(self, n: int) -> List[Dict]:
        """Get top N performing assets"""
        sorted_assets = sorted(
            [a for a in self.assets.values() if a.status != AssetStatus.EXITED],
            key=lambda x: x.unrealized_pnl_pct,
            reverse=True
        )
        return [
            {
                'symbol': a.symbol,
                'class': a.asset_class.value,
                'pnl_pct': a.unrealized_pnl_pct,
                'value': a.current_value
            }
            for a in sorted_assets[:n]
        ]
    
    def _get_worst_performers(self, n: int) -> List[Dict]:
        """Get worst N performing assets"""
        sorted_assets = sorted(
            [a for a in self.assets.values() if a.status != AssetStatus.EXITED],
            key=lambda x: x.unrealized_pnl_pct
        )
        return [
            {
                'symbol': a.symbol,
                'class': a.asset_class.value,
                'pnl_pct': a.unrealized_pnl_pct,
                'value': a.current_value
            }
            for a in sorted_assets[:n]
        ]
    
    def _get_flagged_assets(self) -> List[Dict]:
        """Get assets flagged for exit"""
        flagged = []
        for a in self.assets.values():
            if a.status == AssetStatus.FLAGGED_EXIT:
                flagged.append({
                    'asset_id': a.asset_id,
                    'symbol': a.symbol,
                    'loss_pct': a.unrealized_pnl_pct,
                    'value': a.current_value,
                    'suggestion': 'Sell and redeploy capital'
                })
        return flagged
    
    def execute_sell(self, asset_id: str, quantity: Optional[float] = None,
                     sell_price: Optional[float] = None) -> Dict:
        """Execute sell (partial or full)"""
        asset = self.assets.get(asset_id)
        if not asset:
            return {'error': 'Asset not found'}
        
        sell_qty = quantity or asset.quantity
        price = sell_price or asset.current_price
        
        proceeds = sell_qty * price
        cost = sell_qty * asset.avg_buy_price
        realized_pnl = proceeds - cost
        
        # Record transaction
        self.transactions.append({
            'type': 'SELL',
            'asset_id': asset_id,
            'quantity': sell_qty,
            'price': price,
            'proceeds': proceeds,
            'realized_pnl': realized_pnl,
            'timestamp': datetime.now()
        })
        
        # Update asset
        asset.quantity -= sell_qty
        if asset.quantity <= 0:
            asset.status = AssetStatus.EXITED
        
        return {
            'asset_id': asset_id,
            'quantity_sold': sell_qty,
            'proceeds': round(proceeds, 2),
            'realized_pnl': round(realized_pnl, 2),
            'remaining_qty': asset.quantity
        }
    
    def get_tax_report(self, year: int) -> Dict:
        """Generate tax report for year"""
        year_txns = [t for t in self.transactions 
                    if t['timestamp'].year == year and t['type'] == 'SELL']
        
        total_gains = sum(t['realized_pnl'] for t in year_txns if t['realized_pnl'] > 0)
        total_losses = sum(t['realized_pnl'] for t in year_txns if t['realized_pnl'] < 0)
        
        return {
            'year': year,
            'total_transactions': len(year_txns),
            'total_gains': round(total_gains, 2),
            'total_losses': round(abs(total_losses), 2),
            'net_pnl': round(total_gains + total_losses, 2),
            'transactions': year_txns
        }

if __name__ == "__main__":
    tracker = AssetPortfolioTracker('user_001')
    
    # Add some assets
    tracker.add_asset(Asset('1', 'BTC', 'Bitcoin', AssetClass.CRYPTO, 0.01, 30000, 35000, platform='coinbase'))
    tracker.add_asset(Asset('2', 'ETH', 'Ethereum', AssetClass.CRYPTO, 0.1, 1800, 1700, platform='binance'))
    tracker.add_asset(Asset('3', 'VWRL', 'Vanguard FTSE All-World', AssetClass.STOCKS, 10, 85, 92, platform='trading212'))
    
    # Get summary
    summary = tracker.get_portfolio_summary()
    print(f"Total Value: £{summary['total_value']:,.2f}")
    print(f"Total P&L: £{summary['total_unrealized_pnl']:,.2f} ({summary['total_pnl_pct']}%)")
    print(f"\nWinners: {summary['winners']}")
    print(f"Losers: {summary['losers']}")
    print(f"\nFlagged for exit: {summary['flagged_for_exit']}")
