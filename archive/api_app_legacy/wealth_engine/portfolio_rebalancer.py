"""Portfolio Rebalancer - Smart rebalancing with profit-taking and loss recovery"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class RebalanceTrigger(Enum):
    SCHEDULED = 'scheduled'                    # Monthly/quarterly rebalance
    THRESHOLD_CROSS = 'threshold_cross'       # Major capital change
    UNDERPERFORMER_DETECTED = 'underperformer'  # Cut losses
    PROFIT_TARGET_HIT = 'profit_target'        # Take gains
    ALLOCATION_DRIFT = 'allocation_drift'     # Target weights off
    NEW_CAPITAL = 'new_capital'                # Fresh contribution

class RebalanceAction(Enum):
    SELL_FULL = 'sell_full'
    SELL_PARTIAL = 'sell_partial'
    HOLD = 'hold'
    BUY_MORE = 'buy_more'
    SWAP = 'swap'  # Sell A, buy B

@dataclass
class RebalanceRecommendation:
    trigger: RebalanceTrigger
    action: RebalanceAction
    asset_id: str
    symbol: str
    current_value: float
    current_allocation_pct: float
    target_allocation_pct: float
    action_amount: float
    reason: str
    expected_outcome: str

class PortfolioRebalancer:
    """
    Intelligent rebalancing engine.
    Takes profits, cuts losses, optimizes allocation.
    """
    
    def __init__(self, tracker):
        self.tracker = tracker
        self.rebalance_history = []
        self.target_allocations = {}  # asset_class -> target %
    
    def set_target_allocation(self, asset_class: str, target_pct: float):
        """Set target allocation for asset class"""
        self.target_allocations[asset_class] = target_pct
    
    def analyze_rebalance_needed(self) -> Dict:
        """Check if portfolio needs rebalancing"""
        summary = self.tracker.get_portfolio_summary()
        recommendations = []
        triggers = []
        
        total_value = summary['total_value']
        
        # 1. Check for losers to cut
        for loser in summary.get('losers', []):
            if loser['pnl_pct'] < -15:  # -15% stop loss
                rec = self._create_sell_recommendation(
                    loser['symbol'],
                    RebalanceTrigger.UNDERPERFORMER_DETECTED,
                    f"Cut losses at {loser['pnl_pct']:.1f}%"
                )
                recommendations.append(rec)
                triggers.append(RebalanceTrigger.UNDERPERFORMER_DETECTED)
        
        # 2. Check for profit takers
        for winner in summary.get('winners', []):
            if winner['pnl_pct'] > 25:  # 25% profit target
                rec = self._create_partial_sell_recommendation(
                    winner['symbol'],
                    0.3,  # Sell 30% of position
                    winner['value'],
                    RebalanceTrigger.PROFIT_TARGET_HIT,
                    f"Take 30% profit at {winner['pnl_pct']:.1f}% gain"
                )
                recommendations.append(rec)
                triggers.append(RebalanceTrigger.PROFIT_TARGET_HIT)
        
        # 3. Check allocation drift
        for ac_name, ac_data in summary.get('by_asset_class', {}).items():
            current_pct = (ac_data['value'] / total_value) * 100 if total_value > 0 else 0
            target_pct = self.target_allocations.get(ac_name, 20)
            
            drift = abs(current_pct - target_pct)
            if drift > 10:  # >10% drift triggers rebalance
                # Need more or less of this class
                if current_pct < target_pct:
                    recommendations.append(
                        RebalanceRecommendation(
                            trigger=RebalanceTrigger.ALLOCATION_DRIFT,
                            action=RebalanceAction.BUY_MORE,
                            asset_id=f'class_{ac_name}',
                            symbol=ac_name,
                            current_value=ac_data['value'],
                            current_allocation_pct=current_pct,
                            target_allocation_pct=target_pct,
                            action_amount=(target_pct - current_pct) / 100 * total_value,
                            reason=f"{ac_name} underweight by {drift:.1f}%",
                            expected_outcome=f"Rebalance to {target_pct:.0f}% target"
                        )
                    )
                triggers.append(RebalanceTrigger.ALLOCATION_DRIFT)
        
        return {
            'needs_rebalance': len(recommendations) > 0,
            'triggers': list(set(t.value for t in triggers)),
            'recommendations': recommendations,
            'estimated_proceeds': sum(r.action_amount for r in recommendations if r.action in [RebalanceAction.SELL_FULL, RebalanceAction.SELL_PARTIAL]),
            'estimated_reinvestment': sum(r.action_amount for r in recommendations if r.action == RebalanceAction.BUY_MORE)
        }
    
    def _create_sell_recommendation(self, symbol: str, trigger: RebalanceTrigger, reason: str) -> RebalanceRecommendation:
        """Create full sell recommendation"""
        # Find asset
        for asset_id, asset in self.tracker.assets.items():
            if asset.symbol == symbol:
                summary = self.tracker.get_portfolio_summary()
                current_pct = (asset.current_value / summary['total_value']) * 100 if summary['total_value'] > 0 else 0
                
                return RebalanceRecommendation(
                    trigger=trigger,
                    action=RebalanceAction.SELL_FULL,
                    asset_id=asset_id,
                    symbol=symbol,
                    current_value=asset.current_value,
                    current_allocation_pct=current_pct,
                    target_allocation_pct=0,
                    action_amount=asset.current_value,
                    reason=reason,
                    expected_outcome=f"Cut loss, redeploy £{asset.current_value:.2f} into better opportunities"
                )
        return None
    
    def _create_partial_sell_recommendation(self, symbol: str, sell_pct: float, value: float,
                                           trigger: RebalanceTrigger, reason: str) -> RebalanceRecommendation:
        """Create partial sell recommendation"""
        for asset_id, asset in self.tracker.assets.items():
            if asset.symbol == symbol:
                sell_amount = value * sell_pct
                
                return RebalanceRecommendation(
                    trigger=trigger,
                    action=RebalanceAction.SELL_PARTIAL,
                    asset_id=asset_id,
                    symbol=symbol,
                    current_value=value,
                    current_allocation_pct=0,
                    target_allocation_pct=0,
                    action_amount=sell_amount,
                    reason=reason,
                    expected_outcome=f"Lock in £{sell_amount:.2f} profit, keep {100-sell_pct*100:.0f}% for more upside"
                )
        return None
    
    def execute_rebalance(self, recommendations: List[RebalanceRecommendation]) -> Dict:
        """Execute rebalance recommendations"""
        results = {
            'executed_at': datetime.now(),
            'sells': [],
            'proceeds': 0,
            'deployed': [],
            'status': 'completed'
        }
        
        # Execute sells
        for rec in recommendations:
            if rec.action in [RebalanceAction.SELL_FULL, RebalanceAction.SELL_PARTIAL]:
                quantity = None if rec.action == RebalanceAction.SELL_FULL else 'partial'
                sell_result = self.tracker.execute_sell(rec.asset_id)
                
                if 'error' not in sell_result:
                    results['sells'].append({
                        'symbol': rec.symbol,
                        'proceeds': sell_result['proceeds'],
                        'realized_pnl': sell_result['realized_pnl']
                    })
                    results['proceeds'] += sell_result['proceeds']
        
        # Deploy proceeds (simplified - would integrate with allocator)
        if results['proceeds'] > 0:
            results['deployed'] = self._deploy_proceeds(results['proceeds'])
        
        # Record
        self.rebalance_history.append(results)
        
        return results
    
    def _deploy_proceeds(self, amount: float) -> List[Dict]:
        """Deploy proceeds into better opportunities"""
        # Simplified - would use AI allocator
        deployments = []
        
        # Rebalance into underweight classes
        summary = self.tracker.get_portfolio_summary()
        total_value = summary['total_value'] + amount
        
        for ac_name, target_pct in self.target_allocations.items():
            current_value = summary.get('by_asset_class', {}).get(ac_name, {}).get('value', 0)
            target_value = total_value * (target_pct / 100)
            
            if current_value < target_value:
                deploy_amount = min(amount * 0.5, target_value - current_value)
                if deploy_amount > 10:
                    deployments.append({
                        'asset_class': ac_name,
                        'amount': round(deploy_amount, 2),
                        'strategy': 'rebalance_fill',
                        'expected_return': 0.08
                    })
                    amount -= deploy_amount
        
        return deployments
    
    def get_rebalance_history(self) -> List[Dict]:
        """Get history of all rebalances"""
        return self.rebalance_history
    
    def generate_rebalance_report(self) -> Dict:
        """Generate comprehensive rebalance report"""
        analysis = self.analyze_rebalance_needed()
        history = self.rebalance_history
        
        total_realized_gains = sum(
            s['realized_pnl'] for h in history for s in h['sells'] if s['realized_pnl'] > 0
        )
        total_realized_losses = sum(
            s['realized_pnl'] for h in history for s in h['sells'] if s['realized_pnl'] < 0
        )
        
        return {
            'current_analysis': analysis,
            'rebalances_count': len(history),
            'total_sell_proceeds': sum(h['proceeds'] for h in history),
            'total_realized_gains': round(total_realized_gains, 2),
            'total_realized_losses': round(total_realized_losses, 2),
            'net_realized_pnl': round(total_realized_gains + total_realized_losses, 2),
            'loss_cutting_effectiveness': f"{abs(total_realized_losses/total_realized_gains)*100:.1f}%" if total_realized_gains > 0 else "N/A"
        }

if __name__ == "__main__":
    from asset_portfolio_tracker import AssetPortfolioTracker, Asset, AssetClass
    
    tracker = AssetPortfolioTracker('user_001')
    rebalancer = PortfolioRebalancer(tracker)
    
    # Set targets
    rebalancer.set_target_allocation('crypto', 20)
    rebalancer.set_target_allocation('stocks', 40)
    rebalancer.set_target_allocation('cash', 10)
    
    # Add assets
    tracker.add_asset(Asset('1', 'BTC', 'Bitcoin', AssetClass.CRYPTO, 0.01, 30000, 38000, platform='coinbase'))
    tracker.add_asset(Asset('2', 'DOGE', 'Dogecoin', AssetClass.CRYPTO, 1000, 0.15, 0.08, platform='binance'))
    tracker.add_asset(Asset('3', 'VWRL', 'Vanguard', AssetClass.STOCKS, 10, 85, 95, platform='t212'))
    
    # Analyze
    analysis = rebalancer.analyze_rebalance_needed()
    print(f"Rebalance needed: {analysis['needs_rebalance']}")
    print(f"Triggers: {analysis['triggers']}")
    print(f"\nRecommendations:")
    for rec in analysis['recommendations']:
        print(f"  - {rec.action.value.upper()}: {rec.symbol} ({rec.reason})")
        print(f"    Amount: £{rec.action_amount:.2f} | Outcome: {rec.expected_outcome}")
