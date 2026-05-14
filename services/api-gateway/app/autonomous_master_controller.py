"""
Veyra Autonomous Controller
Main orchestrator that runs the entire system autonomously
Version: 1.0
"""

import json
import logging
import schedule
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import sys

# Import our custom modules
from ai_automation_engine import FinancialMasterEngine, FinancialCalculator
from ml_prediction_model import MLEngineManager
from data_ingestion_engine import DataAggregationEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autonomous_controller.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('Autonomous_Master_Controller')


class AutonomousFinancialSystem:
    """
    Fully autonomous financial management system
    Runs 24/7, makes decisions, executes trades (simulated), tracks performance
    """
    
    def __init__(self, config_path: str = "system_config.json"):
        self.config = self.load_config(config_path)
        self.calc_engine = FinancialMasterEngine(self.config)
        self.ml_engine = MLEngineManager()
        self.data_engine = DataAggregationEngine()
        
        # State tracking
        self.is_running = False
        self.current_phase = "Phase_1"
        self.last_run = None
        self.decision_log = []
        self.performance_metrics = {}
        
        logger.info("Autonomous Financial System initialized")
    
    def load_config(self, path: str) -> Dict:
        """Load or create default configuration"""
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "user_profile": {
                "daily_rate": 145,
                "days_per_month": 22,
                "tax_rate": 0.20,
                "essential_outgoings": 1887,
                "current_emergency_fund": 0,
                "debt_balance": 1200,
                "debt_payment": 360
            },
            "assets": {
                "BTC": {"symbol": "BTC", "type": "crypto", "target_allocation": 0.35},
                "VWRP": {"symbol": "VWRP.L", "type": "etf", "target_allocation": 0.25},
                "GOLD": {"symbol": "GC=F", "type": "commodity", "target_allocation": 0.10},
                "LISA": {"symbol": "CASH", "type": "cash", "target_allocation": 0.20},
                "ETH": {"symbol": "ETH", "type": "crypto", "target_allocation": 0.10}
            },
            "automation_settings": {
                "enable_live_trading": False,  # Simulation mode by default
                "rebalance_threshold": 0.05,
                "risk_tolerance": "medium",
                "max_daily_loss_pct": 2.0,
                "min_confidence_for_trade": 0.65
            },
            "schedule": {
                "price_update_interval_minutes": 60,
                "portfolio_review_hour": 18,
                "weekly_report_day": "sunday",
                "monthly_rebalance_day": 1
            },
            "api_keys": {
                "alphavantage": os.getenv("ALPHAVANTAGE_KEY", ""),
                "openai": os.getenv("OPENAI_KEY", "")
            }
        }
    
    def determine_phase(self) -> str:
        """Determine which financial phase the user is in"""
        profile = self.config['user_profile']
        
        emergency_fund = profile.get('current_emergency_fund', 0)
        debt_balance = profile.get('debt_balance', 0)
        
        if emergency_fund < 1000:
            return "Phase_1_Foundation"
        elif debt_balance > 0:
            return "Phase_2_Debt_Elimination"
        else:
            # Check if advanced features active
            return "Phase_3_Core_Engines"  # Default to Phase 3
    
    def calculate_monthly_projection(self) -> pd.DataFrame:
        """Calculate 12-month financial projection"""
        return self.calc_engine.run_financial_projection(12)
    
    def execute_daily_analysis(self) -> Dict:
        """
        Daily autonomous analysis routine
        1. Fetch current prices
        2. Assess portfolio risk
        3. Generate trading signals
        4. Make recommendations
        """
        logger.info("Executing daily analysis...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'phase': self.determine_phase(),
            'prices': {},
            'risk_assessment': {},
            'signals': {},
            'recommendations': {},
            'actions_taken': []
        }
        
        # 1. Get current prices
        asset_symbols = {k: v['symbol'] for k, v in self.config['assets'].items()}
        prices = self.data_engine.get_current_prices(asset_symbols)
        results['prices'] = {k: v.price if v else None for k, v in prices.items()}
        
        # 2. Portfolio risk assessment (would use historical data)
        # Simplified for demo
        
        # 3. Generate signals for rebalancing
        # Get current allocations from user input or tracking
        current_allocations = self.get_current_allocations()
        target_allocations = {k: v['target_allocation'] for k, v in self.config['assets'].items()}
        
        # Calculate deviations
        deviations = {}
        for asset in self.config['assets'].keys():
            current = current_allocations.get(asset, 0)
            target = target_allocations.get(asset, 0)
            deviations[asset] = {
                'current': current,
                'target': target,
                'deviation': current - target,
                'action_needed': abs(current - target) > 0.05
            }
        
        results['deviations'] = deviations
        
        # 4. Generate recommendations
        for asset, dev in deviations.items():
            if dev['action_needed']:
                if dev['deviation'] > 0:
                    results['recommendations'][asset] = f"REDUCE by {dev['deviation']:.1%}"
                else:
                    results['recommendations'][asset] = f"INCREASE by {abs(dev['deviation']):.1%}"
                
                # Log decision
                self.decision_log.append({
                    'timestamp': results['timestamp'],
                    'asset': asset,
                    'action': results['recommendations'][asset],
                    'reason': f"Allocation deviation: {dev['deviation']:.1%}"
                })
        
        # 5. Phase-specific actions
        phase = results['phase']
        if phase == "Phase_1_Foundation":
            results['priority_action'] = "Build emergency fund to £1,000"
        elif phase == "Phase_2_Debt_Elimination":
            results['priority_action'] = f"Pay off remaining debt: £{self.config['user_profile']['debt_balance']}"
        else:
            results['priority_action'] = "Maintain and optimize investment engines"
        
        # Save results
        self.save_analysis_results(results)
        
        return results
    
    def get_current_allocations(self) -> Dict[str, float]:
        """Get current portfolio allocations from actual tracking data"""
        # Read from portfolio database or tracking system
        try:
            # Simulate reading from actual portfolio data
            current_holdings = self.data_engine.get_current_holdings()
            total_value = sum(holding['value'] for holding in current_holdings)
            
            # Calculate allocations by asset class
            allocations = {}
            
            for holding in current_holdings:
                asset_class = self._classify_asset(holding['symbol'])
                allocation_pct = (holding['value'] / total_value) * 100 if total_value > 0 else 0
                allocations[asset_class] = allocations.get(asset_class, 0) + allocation_pct
            
            # Round to 2 decimal places
            allocations = {k: round(v, 2) for k, v in allocations.items()}
            
            return allocations
            
        except Exception as e:
            logger.error(f"Error reading portfolio allocations: {e}")
            # Fallback to default allocations
            return {
                'Equity': 60.0,
                'Bonds': 25.0,
                'Real_Estate': 10.0,
                'Commodities': 3.0,
                'Cash': 2.0
            }
    
    def _classify_asset(self, symbol: str) -> str:
        """Classify asset symbol into asset class"""
        asset_mapping = {
            # Equities
            'AAPL': 'Equity', 'MSFT': 'Equity', 'GOOGL': 'Equity', 'AMZN': 'Equity',
            'TSLA': 'Equity', 'META': 'Equity', 'NVDA': 'Equity', 'JPM': 'Equity',
            # Bonds
            'AGGH': 'Bonds', 'BND': 'Bonds', 'TLT': 'Bonds', 'IEF': 'Bonds',
            # Real Estate
            'VNQ': 'Real_Estate', 'IYR': 'Real_Estate', 'REZ': 'Real_Estate',
            # Commodities
            'GLD': 'Commodities', 'SLV': 'Commodities', 'USO': 'Commodities',
            # Crypto
            'BTC': 'Crypto', 'ETH': 'Crypto', 'BNB': 'Crypto', 'SOL': 'Crypto',
            # Cash equivalents
            'VWRP': 'Cash', 'LISA': 'Cash', 'HYG': 'Cash'
        }
        
        return asset_mapping.get(symbol, 'Other')
    
    def execute_monthly_rebalance(self) -> Dict:
        """
        Monthly portfolio rebalancing routine
        Executes rebalancing trades to maintain target allocations
        """
        logger.info("Executing monthly rebalance...")
        
        rebalance_results = {
            'timestamp': datetime.now().isoformat(),
            'actions': [],
            'simulated_only': not self.config['automation_settings']['enable_live_trading']
        }
        
        # Get current state
        current_allocations = self.get_current_allocations()
        targets = {k: v['target_allocation'] for k, v in self.config['assets'].items()}
        
        # Calculate required trades
        # Simplified: assume £1000 total portfolio for calculation
        total_value = 1000
        
        for asset, target in targets.items():
            current = current_allocations.get(asset, 0)
            deviation = current - target
            
            if abs(deviation) > self.config['automation_settings']['rebalance_threshold']:
                trade_value = abs(deviation) * total_value
                action = "SELL" if deviation > 0 else "BUY"
                
                trade = {
                    'asset': asset,
                    'action': action,
                    'value_gbp': trade_value,
                    'reason': f"Rebalance: {current:.1%} vs target {target:.1%}"
                }
                
                rebalance_results['actions'].append(trade)
                
                if self.config['automation_settings']['enable_live_trading']:
                    # Would execute actual trade here
                    logger.info(f"Executing trade: {action} £{trade_value:.2f} of {asset}")
                else:
                    logger.info(f"[SIMULATED] {action} £{trade_value:.2f} of {asset}")
        
        self.save_rebalance_results(rebalance_results)
        return rebalance_results
    
    def generate_weekly_report(self) -> Dict:
        """Generate weekly performance report"""
        report = {
            'week_ending': datetime.now().isoformat(),
            'phase': self.determine_phase(),
            'portfolio_value_gbp': 0,  # Would be calculated
            'week_pnl_pct': 0,
            'decisions_made': len(self.decision_log),
            'key_actions': self.decision_log[-5:] if self.decision_log else [],
            'recommendations_for_next_week': []
        }
        
        # Generate next week recommendations
        phase = self.determine_phase()
        if phase == "Phase_1_Foundation":
            report['recommendations_for_next_week'] = [
                "Continue emergency fund deposits",
                "Review standing orders are executing",
                "Check bank switching bonus opportunities"
            ]
        elif phase == "Phase_3_Core_Engines":
            report['recommendations_for_next_week'] = [
                "Review Pionex DCA bot performance",
                "Check Trading 212 ISA contributions",
                "Monitor gold price for Goldwise purchase",
                "Verify staking rewards received"
            ]
        
        self.save_weekly_report(report)
        return report
    
    def save_analysis_results(self, results: Dict):
        """Save analysis results to JSON"""
        filename = f"analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    
    def save_rebalance_results(self, results: Dict):
        """Save rebalance results to JSON"""
        filename = f"rebalance_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    
    def save_weekly_report(self, report: Dict):
        """Save weekly report to JSON and CSV"""
        json_file = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also append to CSV log
        csv_file = "weekly_reports.csv"
        df = pd.DataFrame([{
            'date': report['week_ending'],
            'phase': report['phase'],
            'decisions': report['decisions_made']
        }])
        
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, index=False)
    
    def setup_autonomous_schedule(self):
        """Setup the autonomous execution schedule"""
        
        # Daily analysis at 9 AM and 6 PM
        schedule.every().day.at("09:00").do(self.execute_daily_analysis)
        schedule.every().day.at("18:00").do(self.execute_daily_analysis)
        
        # Weekly report on Sundays at 10 AM
        schedule.every().sunday.at("10:00").do(self.generate_weekly_report)
        
        # Monthly rebalance on 1st of month at 9 AM
        schedule.every().month.at("09:00").do(self.execute_monthly_rebalance)
        
        logger.info("Autonomous schedule configured")
    
    def run_single_cycle(self) -> Dict:
        """Run a single autonomous cycle (for testing)"""
        logger.info("Running single autonomous cycle...")
        
        results = {
            'analysis': self.execute_daily_analysis(),
            'phase': self.determine_phase(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Only rebalance if it's the right day
        if datetime.now().day == 1:
            results['rebalance'] = self.execute_monthly_rebalance()
        
        return results
    
    def run_continuous(self):
        """Run autonomous system continuously"""
        self.is_running = True
        self.setup_autonomous_schedule()
        
        logger.info("Autonomous system started - Running 24/7")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down autonomous system...")
        self.is_running = False
        
        # Save final state
        state = {
            'shutdown_time': datetime.now().isoformat(),
            'final_phase': self.determine_phase(),
            'total_decisions': len(self.decision_log),
            'decision_log': self.decision_log
        }
        
        with open('final_state.json', 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info("Shutdown complete")


# CLI Interface
def main():
    """Main entry point for autonomous system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Veyra Autonomous System')
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                       help='Run mode: single cycle or continuous')
    parser.add_argument('--config', default='system_config.json',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Initialize system
    system = AutonomousFinancialSystem(args.config)
    
    if args.mode == 'single':
        # Run single cycle and exit
        results = system.run_single_cycle()
        
        print("\n" + "="*50)
        print("AUTONOMOUS CYCLE RESULTS")
        print("="*50)
        print(f"Phase: {results['phase']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"\nCurrent Prices:")
        for asset, price in results['analysis']['prices'].items():
            if price:
                print(f"  {asset}: £{price:,.2f}")
        
        print(f"\nRecommendations:")
        for asset, rec in results['analysis']['recommendations'].items():
            print(f"  {asset}: {rec}")
        
        print(f"\nPriority Action: {results['analysis']['priority_action']}")
        
    else:
        # Run continuously
        print("Starting autonomous system (Press Ctrl+C to stop)...")
        system.run_continuous()


if __name__ == "__main__":
    main()
