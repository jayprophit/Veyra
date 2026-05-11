"""
Veyra AI Automation Engine
Autonomous Wealth Management System
Version: 1.0 | Python 3.8+
"""

import json
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import schedule
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AI_Automation_Engine')


class FinancialCalculator:
    """Core financial calculation engine with all formulas"""
    
    @staticmethod
    def calculate_monthly_net_income(daily_rate: float, days_worked: int, tax_rate: float, additional_income: float = 0) -> float:
        """Formula: B6 = B2 * B3 * (1 - B4) + B5"""
        return daily_rate * days_worked * (1 - tax_rate) + additional_income
    
    @staticmethod
    def calculate_monthly_surplus(net_income: float, essential_outgoings: float) -> float:
        """Formula: B8 = B6 - B7"""
        return net_income - essential_outgoings
    
    @staticmethod
    def calculate_months_to_emergency_fund(target: float, monthly_surplus: float) -> float:
        """Formula: B10 = B9 / B8"""
        if monthly_surplus <= 0:
            return float('inf')
        return target / monthly_surplus
    
    @staticmethod
    def calculate_months_to_debt_freedom(debt_balance: float, monthly_payment: float) -> float:
        """Formula: B17 = B13 / (B15 + B16)"""
        if monthly_payment <= 0:
            return float('inf')
        return debt_balance / monthly_payment
    
    @staticmethod
    def calculate_investment_allocation(available_funds: float, allocation_pct: float) -> float:
        """Formula: B29-B33 = B22 * B23-27"""
        return available_funds * allocation_pct
    
    @staticmethod
    def calculate_compound_interest(principal: float, annual_rate: float, years: float, compound_freq: int = 365) -> float:
        """Compound interest formula: A = P(1 + r/n)^(nt)"""
        return principal * (1 + annual_rate / compound_freq) ** (compound_freq * years)
    
    @staticmethod
    def calculate_cgt_tax(gains: float, allowance: float = 3000, rate: float = 0.18) -> float:
        """CGT calculation: Tax = max(0, Gains - Allowance) * Rate"""
        taxable = max(0, gains - allowance)
        return taxable * rate
    
    @staticmethod
    def calculate_portfolio_value(holdings: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate total portfolio value from all positions"""
        values = {}
        total = 0
        for asset, data in holdings.items():
            value = data['units'] * data['price']
            values[asset] = value
            total += value
        values['total'] = total
        return values
    
    @staticmethod
    def calculate_allocation_percentages(values: Dict[str, float]) -> Dict[str, float]:
        """Calculate percentage allocation for each asset"""
        total = values.get('total', sum(v for k, v in values.items() if k != 'total'))
        if total == 0:
            return {k: 0 for k in values.keys()}
        return {k: (v / total if k != 'total' else v) for k, v in values.items()}


class RebalancingEngine:
    """Portfolio rebalancing automation"""
    
    TARGET_ALLOCATIONS = {
        'BTC': 0.35,
        'VWRP': 0.25,
        'GOLD': 0.10,
        'LISA': 0.20,
        'STAKED_ETH': 0.10
    }
    
    REBALANCE_THRESHOLD = 0.05  # 5% deviation triggers rebalance
    
    def __init__(self, calculator: FinancialCalculator):
        self.calc = calculator
    
    def check_rebalance_needed(self, current_values: Dict[str, float]) -> Tuple[bool, Dict[str, float]]:
        """Check if portfolio needs rebalancing"""
        allocations = self.calc.calculate_allocation_percentages(current_values)
        deviations = {}
        needs_rebalance = False
        
        for asset, target in self.TARGET_ALLOCATIONS.items():
            current = allocations.get(asset, 0)
            deviation = abs(current - target)
            deviations[asset] = {
                'current': current,
                'target': target,
                'deviation': deviation,
                'action': 'HOLD'
            }
            
            if deviation > self.REBALANCE_THRESHOLD:
                needs_rebalance = True
                deviations[asset]['action'] = 'REDUCE' if current > target else 'INCREASE'
        
        return needs_rebalance, deviations
    
    def generate_rebalance_instructions(self, total_value: float, deviations: Dict) -> List[Dict]:
        """Generate specific rebalancing instructions"""
        instructions = []
        
        for asset, data in deviations.items():
            if data['action'] != 'HOLD':
                target_value = total_value * data['target']
                current_value = total_value * data['current']
                difference = target_value - current_value
                
                instructions.append({
                    'asset': asset,
                    'action': data['action'],
                    'amount_gbp': abs(difference),
                    'priority': 'HIGH' if data['deviation'] > 0.10 else 'MEDIUM'
                })
        
        return sorted(instructions, key=lambda x: x['amount_gbp'], reverse=True)


class TaxOptimizer:
    """Tax optimization and planning engine"""
    
    UK_ALLOWANCES_2025_26 = {
        'personal_allowance': 12570,
        'cgt_allowance': 3000,
        'trading_allowance': 1000,
        'dividend_allowance': 500,
        'isa_annual': 20000,
        'lisa_annual': 4000,
        'lisa_bonus_rate': 0.25
    }
    
    TAX_RATES = {
        'cgt_basic': 0.18,
        'cgt_higher': 0.24,
        'income_basic': 0.20,
        'income_higher': 0.40,
        'dividend_basic': 0.0875,
        'dividend_higher': 0.3375
    }
    
    def __init__(self):
        self.allowances = self.UK_ALLOWANCES_2025_26
        self.rates = self.TAX_RATES
    
    def calculate_tax_liability(self, 
                              crypto_gains: float = 0,
                              trading_profit: float = 0,
                              staking_rewards: float = 0,
                              dividends: float = 0,
                              is_higher_rate: bool = False) -> Dict[str, float]:
        """Calculate total tax liability"""
        cgt_rate = self.rates['cgt_higher'] if is_higher_rate else self.rates['cgt_basic']
        income_rate = self.rates['income_higher'] if is_higher_rate else self.rates['income_basic']
        dividend_rate = self.rates['dividend_higher'] if is_higher_rate else self.rates['dividend_basic']
        
        cgt_tax = max(0, crypto_gains - self.allowances['cgt_allowance']) * cgt_rate
        trading_tax = max(0, trading_profit - self.allowances['trading_allowance']) * income_rate
        staking_tax = staking_rewards * income_rate  # Staking is income
        dividend_tax = max(0, dividends - self.allowances['dividend_allowance']) * dividend_rate
        
        total = cgt_tax + trading_tax + staking_tax + dividend_tax
        
        return {
            'cgt_tax': cgt_tax,
            'trading_tax': trading_tax,
            'staking_tax': staking_tax,
            'dividend_tax': dividend_tax,
            'total_tax': total,
            'effective_rate': total / max(1, crypto_gains + trading_profit + staking_rewards + dividends)
        }
    
    def optimize_tax_sinking_fund(self, estimated_gains: float, buffer: float = 0.20) -> float:
        """Calculate recommended tax sinking fund with 20% buffer"""
        liability = self.calculate_tax_liability(crypto_gains=estimated_gains)
        return liability['total_tax'] * (1 + buffer)
    
    def check_isa_optimization(self, current_isa_deposit: float, planned_deposit: float) -> Dict:
        """Check ISA allowance optimization"""
        remaining = self.allowances['isa_annual'] - current_isa_deposit
        can_deposit = min(planned_deposit, remaining)
        
        return {
            'remaining_allowance': remaining,
            'can_deposit': can_deposit,
            'would_exceed': planned_deposit > remaining,
            'excess_amount': max(0, planned_deposit - remaining)
        }


class AutonomousScheduler:
    """Manages all scheduled autonomous tasks"""
    
    def __init__(self):
        self.tasks = []
        self.running = False
    
    def setup_default_schedule(self):
        """Setup the standard financial management schedule"""
        # Daily tasks
        schedule.every().day.at("09:00").do(self.check_pionex_bot)
        schedule.every().day.at("18:00").do(self.update_portfolio_prices)
        
        # Weekly tasks (Sundays)
        schedule.every().sunday.at("10:00").do(self.weekly_review)
        
        # Monthly tasks (1st of month)
        schedule.every().month.at("09:00").do(self.monthly_deposits)
        
        # Quarterly tasks (Jan, Apr, Jul, Oct)
        schedule.every().quarter.at("10:00").do(self.quarterly_review)
        
        logger.info("Default schedule configured")
    
    def check_pionex_bot(self):
        """Daily: Verify Pionex DCA bot is running"""
        logger.info("Checking Pionex DCA bot status...")
        # Would integrate with Pionex API here
        return {"status": "OK", "last_buy": datetime.now().isoformat()}
    
    def update_portfolio_prices(self):
        """Daily: Update all asset prices"""
        logger.info("Updating portfolio prices...")
        # Would fetch prices from APIs
        return {"updated": datetime.now().isoformat()}
    
    def weekly_review(self):
        """Weekly: TradingView paper trading review"""
        logger.info("Weekly review: Paper trading stats")
        return {"action": "Review TradingView stats and log lessons"}
    
    def monthly_deposits(self):
        """Monthly: Execute scheduled deposits"""
        logger.info("Monthly deposits triggered")
        deposits = {
            'pionex': 35,
            'coinbase_savings': 20,
            'trading_212': 20,
            'goldwise': 10,
            'lisa': 20,
            'staking': 10,
            'tax_sink': 20
        }
        return deposits
    
    def quarterly_review(self):
        """Quarterly: Full portfolio analysis"""
        logger.info("Quarterly comprehensive review")
        return {
            'export_koinly': True,
            'rebalance_check': True,
            'fca_register_check': True,
            'tax_estimate': True
        }
    
    def run(self):
        """Run the scheduler loop"""
        self.running = True
        logger.info("Autonomous scheduler started")
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Autonomous scheduler stopped")


class FinancialMasterEngine:
    """Main engine that integrates all components"""
    
    def __init__(self, config_path: str = "engine_config.json"):
        self.config = self.load_config(config_path)
        self.calculator = FinancialCalculator()
        self.rebalancer = RebalancingEngine(self.calculator)
        self.tax_optimizer = TaxOptimizer()
        self.scheduler = AutonomousScheduler()
        
        logger.info("Veyra Engine initialized")
    
    def load_config(self, path: str) -> Dict:
        """Load engine configuration"""
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return self.default_config()
    
    def default_config(self) -> Dict:
        """Default engine configuration"""
        return {
            "daily_rate": 145,
            "days_per_month": 22,
            "tax_rate": 0.20,
            "emergency_target": 1000,
            "debt_balance": 1200,
            "debt_payment": 360,
            "monthly_allocations": {
                "pionex": 0.35,
                "isa": 0.25,
                "gold": 0.10,
                "lisa": 0.20,
                "staking": 0.10
            },
            "rebalance_threshold": 0.05,
            "tax_buffer": 0.20
        }
    
    def run_financial_projection(self, months: int = 24) -> pd.DataFrame:
        """Run multi-month financial projection"""
        projections = []
        
        monthly_income = self.calculator.calculate_monthly_net_income(
            self.config['daily_rate'],
            self.config['days_per_month'],
            self.config['tax_rate']
        )
        
        emergency_fund = 0
        debt_balance = self.config['debt_balance']
        investments = 0
        
        for month in range(1, months + 1):
            # Phase 1: Emergency Fund (Months 1-3)
            if month <= 3:
                emergency_deposit = min(200, self.config['emergency_target'] - emergency_fund)
                emergency_fund += emergency_deposit
                invest_deposit = 0
            # Phase 2: Debt Elimination (Months 4-6)
            elif month <= 6:
                debt_payment = min(360, debt_balance)
                debt_balance -= debt_payment
                emergency_deposit = 0
                invest_deposit = 0
            # Phase 3+: Investment Phase
            else:
                emergency_deposit = 0
                invest_deposit = 120  # Total monthly investment
            
            investments += invest_deposit
            
            projections.append({
                'month': month,
                'phase': self.get_phase(month),
                'emergency_fund': emergency_fund,
                'debt_balance': max(0, debt_balance),
                'investments': investments,
                'total_net_worth': emergency_fund + investments - max(0, debt_balance),
                'monthly_deposit': emergency_deposit + invest_deposit
            })
        
        return pd.DataFrame(projections)
    
    def get_phase(self, month: int) -> str:
        """Determine which phase a month falls into"""
        if month <= 3:
            return "Phase_1_Foundation"
        elif month <= 6:
            return "Phase_2_Debt_Elimination"
        elif month <= 12:
            return "Phase_3_Core_Engines"
        elif month <= 24:
            return "Phase_4_Advanced"
        else:
            return "Phase_5_Speculative"
    
    def generate_recommendation(self, current_state: Dict) -> Dict:
        """Generate personalized recommendations based on current state"""
        recommendations = {
            'immediate_actions': [],
            'weekly_actions': [],
            'monthly_actions': [],
            'alerts': []
        }
        
        # Check emergency fund
        if current_state.get('emergency_fund', 0) < 1000:
            recommendations['immediate_actions'].append(
                "Priority: Build emergency fund to £1,000 (Phase 1)"
            )
        
        # Check debt
        if current_state.get('debt_balance', 0) > 0:
            recommendations['immediate_actions'].append(
                f"Pay off remaining debt: £{current_state['debt_balance']}"
            )
        
        # Check allocations
        actual = current_state.get('allocations', {})
        for asset, target in self.config['monthly_allocations'].items():
            current = actual.get(asset, 0)
            if abs(current - target) > 0.05:
                recommendations['alerts'].append(
                    f"Rebalance needed: {asset} at {current:.0%} vs target {target:.0%}"
                )
        
        return recommendations
    
    def export_to_csv(self, data: pd.DataFrame, filename: str):
        """Export projections to CSV"""
        data.to_csv(filename, index=False)
        logger.info(f"Exported data to {filename}")
    
    def start_autonomous_mode(self):
        """Start the autonomous scheduler"""
        self.scheduler.setup_default_schedule()
        self.scheduler.run()


# Main execution
def main():
    """Main entry point"""
    engine = FinancialMasterEngine()
    
    # Run 24-month projection
    projections = engine.run_financial_projection(24)
    print("\n=== 24-Month Financial Projection ===")
    print(projections.to_string())
    
    # Export to CSV
    engine.export_to_csv(projections, 'financial_projection.csv')
    
    # Example recommendation
    example_state = {
        'emergency_fund': 800,
        'debt_balance': 1200,
        'allocations': {'BTC': 0.40, 'VWRP': 0.20, 'GOLD': 0.05, 'LISA': 0.15, 'STAKED_ETH': 0.20}
    }
    recommendations = engine.generate_recommendation(example_state)
    print("\n=== Recommendations ===")
    print(json.dumps(recommendations, indent=2))
    
    # Start autonomous mode (would run indefinitely)
    # engine.start_autonomous_mode()


if __name__ == "__main__":
    main()
