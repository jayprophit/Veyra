"""Financial Master - Retirement Planning with Monte Carlo Simulation."""

import numpy as np
import json
import sqlite3
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RetirementPlanning')

class WithdrawalStrategy(Enum):
    FIXED = "fixed"              # Fixed amount yearly
    PERCENTAGE = "percentage"    # Fixed % of portfolio
    VPW = "vpw"                  # Variable Percentage Withdrawal
    GLIDE = "glide"              # Glide path (decreasing %)

@dataclass
class RetirementScenario:
    """Parameters for retirement simulation."""
    current_age: int
    retirement_age: int
    current_savings: float
    monthly_contribution: float
    expected_return_mean: float = 0.07      # 7% average return
    expected_return_std: float = 0.15       # 15% volatility
    inflation_rate: float = 0.025           # 2.5% inflation
    annual_withdrawal: float = 40000        # £40k/year target
    social_security: float = 0              # UK: State pension
    safe_withdrawal_rate: float = 0.04      # 4% rule
    strategy: WithdrawalStrategy = WithdrawalStrategy.PERCENTAGE

@dataclass
class SimulationResult:
    """Results from a single Monte Carlo simulation run."""
    success: bool                           # Did money last until end?
    final_balance: float                    # Final portfolio value
    min_balance: float                      # Lowest balance reached
    max_balance: float                      # Highest balance reached
    depletion_age: Optional[int]            # Age when money ran out
    total_withdrawn: float                  # Total withdrawals over lifetime
    yearly_balances: List[float]            # Balance at each year

@dataclass
class MonteCarloResults:
    """Aggregated results from all simulations."""
    num_simulations: int
    success_rate: float                     # % of simulations that succeeded
    median_final_balance: float
    p10_final_balance: float                # 10th percentile (conservative)
    p90_final_balance: float                # 90th percentile (optimistic)
    median_depletion_age: Optional[float]   # When money runs out (if it does)
    probability_of_failure: float
    safe_annual_withdrawal: float           # SWR-based calculation
    fire_number: float                      # 25x annual expenses (4% rule)
    years_to_fire: Optional[int]            # Years until FIRE achieved
    all_results: List[SimulationResult]

class RetirementPlanner:
    """
    Retirement planning with Monte Carlo simulation.
    Supports traditional retirement and FIRE (Financial Independence).
    """
    
    def __init__(self, db_connection: Optional[sqlite3.Connection] = None):
        self.conn = db_connection
        self.default_iterations = 10000
        self.default_years = 50  # Simulate to age 100
    
    def run_monte_carlo(
        self,
        scenario: RetirementScenario,
        num_simulations: int = 10000,
        target_age: int = 100
    ) -> MonteCarloResults:
        """
        Run Monte Carlo simulation for retirement scenario.
        
        Returns success probability and distribution of outcomes.
        """
        years = target_age - scenario.current_age
        results = []
        
        for _ in range(num_simulations):
            result = self._simulate_one_path(scenario, years)
            results.append(result)
        
        # Calculate aggregate statistics
        successes = sum(1 for r in results if r.success)
        failures = num_simulations - successes
        
        final_balances = [r.final_balance for r in results]
        depletion_ages = [r.depletion_age for r in results if r.depletion_age is not None]
        
        success_rate = successes / num_simulations
        
        return MonteCarloResults(
            num_simulations=num_simulations,
            success_rate=success_rate,
            probability_of_failure=1 - success_rate,
            median_final_balance=np.median(final_balances),
            p10_final_balance=np.percentile(final_balances, 10),
            p90_final_balance=np.percentile(final_balances, 90),
            median_depletion_age=np.median(depletion_ages) if depletion_ages else None,
            safe_annual_withdrawal=scenario.current_savings * scenario.safe_withdrawal_rate,
            fire_number=scenario.annual_withdrawal / scenario.safe_withdrawal_rate,
            years_to_fire=self._calculate_years_to_fire(scenario),
            all_results=results
        )
    
    def _simulate_one_path(self, scenario: RetirementScenario, years: int) -> SimulationResult:
        """Simulate one possible future path."""
        balance = scenario.current_savings
        balances = []
        total_withdrawn = 0
        min_balance = balance
        max_balance = balance
        depletion_age = None
        age = scenario.current_age
        
        for year in range(years):
            # Accumulation phase
            if age < scenario.retirement_age:
                annual_contribution = scenario.monthly_contribution * 12
                # Random return for this year
                annual_return = np.random.normal(
                    scenario.expected_return_mean,
                    scenario.expected_return_std
                )
                balance = (balance + annual_contribution) * (1 + annual_return)
            
            # Decumulation phase (retirement)
            else:
                withdrawal = self._calculate_withdrawal(
                    scenario, balance, age, years - year
                )
                
                annual_return = np.random.normal(
                    scenario.expected_return_mean,
                    scenario.expected_return_std
                )
                
                balance = balance * (1 + annual_return) - withdrawal + scenario.social_security
                total_withdrawn += withdrawal
                
                if balance <= 0 and depletion_age is None:
                    depletion_age = age
                    balance = 0
            
            # Adjust for inflation
            balance = balance / (1 + scenario.inflation_rate)
            
            balances.append(balance)
            min_balance = min(min_balance, balance)
            max_balance = max(max_balance, balance)
            age += 1
        
        success = balance > 0 or depletion_age is None
        
        return SimulationResult(
            success=success,
            final_balance=balance,
            min_balance=min_balance,
            max_balance=max_balance,
            depletion_age=depletion_age,
            total_withdrawn=total_withdrawn,
            yearly_balances=balances
        )
    
    def _calculate_withdrawal(
        self,
        scenario: RetirementScenario,
        balance: float,
        age: int,
        years_remaining: int
    ) -> float:
        """Calculate withdrawal amount based on strategy."""
        if scenario.strategy == WithdrawalStrategy.FIXED:
            return scenario.annual_withdrawal
        
        elif scenario.strategy == WithdrawalStrategy.PERCENTAGE:
            return balance * scenario.safe_withdrawal_rate
        
        elif scenario.strategy == WithdrawalStrategy.VPW:
            # Variable Percentage Withdrawal (increases with age)
            # Based on mortality tables: % = 1 / remaining life expectancy
            life_expectancy = 90 - age if age < 90 else 5
            vpw_rate = 1.0 / life_expectancy
            return balance * vpw_rate
        
        elif scenario.strategy == WithdrawalStrategy.GLIDE:
            # Start at 5%, glide down to 3% over 20 years
            years_in_retirement = age - scenario.retirement_age
            rate = max(0.03, 0.05 - (years_in_retirement * 0.001))
            return balance * rate
        
        return scenario.annual_withdrawal
    
    def _calculate_years_to_fire(self, scenario: RetirementScenario) -> Optional[int]:
        """Calculate years to reach FIRE number."""
        fire_number = scenario.annual_withdrawal / scenario.safe_withdrawal_rate
        
        balance = scenario.current_savings
        for year in range(50):  # Max 50 years
            if balance >= fire_number:
                return year
            
            annual_return = scenario.expected_return_mean
            annual_contribution = scenario.monthly_contribution * 12
            balance = (balance + annual_contribution) * (1 + annual_return)
        
        return None  # FIRE not achievable in 50 years
    
    def analyze_fi_progress(self, scenario: RetirementScenario) -> Dict:
        """Analyze progress toward Financial Independence."""
        fire_number = scenario.annual_withdrawal / scenario.safe_withdrawal_rate
        current_multiple = scenario.current_savings / scenario.annual_withdrawal
        progress_pct = min(100, scenario.current_savings / fire_number * 100)
        
        # Savings rate calculation
        assumed_income = scenario.monthly_contribution * 12 / 0.30  # Assuming 30% savings rate
        savings_rate = (scenario.monthly_contribution * 12) / assumed_income if assumed_income > 0 else 0
        
        return {
            "fire_number": fire_number,
            "current_savings": scenario.current_savings,
            "progress_percentage": progress_pct,
            "current_multiple": current_multiple,
            "years_to_fire": self._calculate_years_to_fire(scenario),
            "annual_expenses": scenario.annual_withdrawal,
            "safe_withdrawal_rate": scenario.safe_withdrawal_rate,
            "monthly_contribution": scenario.monthly_contribution,
            "savings_rate": savings_rate,
            "status": self._fi_status(progress_pct)
        }
    
    def _fi_status(self, progress_pct: float) -> str:
        """FI status based on progress."""
        if progress_pct >= 100:
            return "FIRE ACHIEVED!"
        elif progress_pct >= 75:
            return "Coast FI - Work optional"
        elif progress_pct >= 50:
            return "Halfway to FI"
        elif progress_pct >= 25:
            return "Building momentum"
        else:
            return "Starting the journey"
    
    def compare_strategies(
        self,
        scenario: RetirementScenario,
        strategies: Optional[List[WithdrawalStrategy]] = None
    ) -> List[Dict]:
        """Compare different withdrawal strategies."""
        if strategies is None:
            strategies = [
                WithdrawalStrategy.FIXED,
                WithdrawalStrategy.PERCENTAGE,
                WithdrawalStrategy.VPW,
                WithdrawalStrategy.GLIDE
            ]
        
        results = []
        for strategy in strategies:
            scenario.strategy = strategy
            mc_result = self.run_monte_carlo(scenario, num_simulations=2000)
            
            results.append({
                "strategy": strategy.value,
                "success_rate": mc_result.success_rate,
                "median_final_balance": mc_result.median_final_balance,
                "median_depletion_age": mc_result.median_depletion_age,
                "p10_balance": mc_result.p10_final_balance,
                "p90_balance": mc_result.p90_final_balance
            })
        
        return sorted(results, key=lambda x: x["success_rate"], reverse=True)
    
    def calculate_safe_contribution(
        self,
        target_retirement_age: int,
        desired_annual_income: float,
        current_age: int,
        current_savings: float,
        target_success_rate: float = 0.95
    ) -> Dict:
        """Calculate required monthly contribution for target success rate."""
        fire_number = desired_annual_income / 0.04
        years_remaining = target_retirement_age - current_age
        
        # Binary search for required contribution
        low, high = 0, 10000
        best_contribution = high
        
        for _ in range(20):  # 20 iterations for precision
            mid = (low + high) / 2
            scenario = RetirementScenario(
                current_age=current_age,
                retirement_age=target_retirement_age,
                current_savings=current_savings,
                monthly_contribution=mid
            )
            result = self.run_monte_carlo(scenario, num_simulations=1000)
            
            if result.success_rate >= target_success_rate:
                best_contribution = mid
                high = mid
            else:
                low = mid
        
        return {
            "required_monthly_contribution": round(best_contribution, 2),
            "annual_contribution": round(best_contribution * 12, 2),
            "target_fire_number": fire_number,
            "years_remaining": years_remaining,
            "target_success_rate": target_success_rate
        }

# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("Financial Master - Retirement Planning with Monte Carlo")
    print("="*70)
    
    planner = RetirementPlanner()
    
    # Example: 35-year-old planning to retire at 60
    scenario = RetirementScenario(
        current_age=35,
        retirement_age=60,
        current_savings=200000,
        monthly_contribution=1500,
        annual_withdrawal=45000,
        expected_return_mean=0.07,
        expected_return_std=0.15,
        strategy=WithdrawalStrategy.PERCENTAGE
    )
    
    print(f"\n📊 Scenario:")
    print(f"   Current Age: {scenario.current_age}")
    print(f"   Target Retirement: {scenario.retirement_age}")
    print(f"   Current Savings: £{scenario.current_savings:,.0f}")
    print(f"   Monthly Contribution: £{scenario.monthly_contribution:,.0f}")
    print(f"   Target Annual Income: £{scenario.annual_withdrawal:,.0f}")
    
    # FI Progress
    print(f"\n🔥 Financial Independence Progress:")
    fi = planner.analyze_fi_progress(scenario)
    print(f"   Status: {fi['status']}")
    print(f"   FIRE Number: £{fi['fire_number']:,.0f}")
    print(f"   Progress: {fi['progress_percentage']:.1f}%")
    print(f"   Years to FIRE: {fi['years_to_fire'] or 'N/A'}")
    print(f"   Current Multiple: {fi['current_multiple']:.1f}x expenses")
    
    # Run Monte Carlo
    print(f"\n🎲 Running Monte Carlo Simulation (10,000 iterations)...")
    results = planner.run_monte_carlo(scenario, num_simulations=10000)
    
    print(f"\n📈 Simulation Results:")
    print(f"   Success Rate: {results.success_rate*100:.1f}%")
    print(f"   Failure Probability: {results.probability_of_failure*100:.1f}%")
    print(f"   Median Final Balance: £{results.median_final_balance:,.0f}")
    print(f"   10th Percentile (Conservative): £{results.p10_final_balance:,.0f}")
    print(f"   90th Percentile (Optimistic): £{results.p90_final_balance:,.0f}")
    
    if results.median_depletion_age:
        print(f"   Median Depletion Age: {results.median_depletion_age:.0f}")
    
    # Compare withdrawal strategies
    print(f"\n🔄 Strategy Comparison:")
    strategies = planner.compare_strategies(scenario)
    for s in strategies:
        print(f"   {s['strategy']:12s}: {s['success_rate']*100:5.1f}% | Final: £{s['median_final_balance']:,.0f}")
    
    # Safe contribution calculation
    print(f"\n💰 Required Contributions for 95% Success:")
    safe = planner.calculate_safe_contribution(
        target_retirement_age=60,
        desired_annual_income=45000,
        current_age=35,
        current_savings=200000
    )
    print(f"   Monthly: £{safe['required_monthly_contribution']:,.0f}")
    print(f"   Annual: £{safe['annual_contribution']:,.0f}")
    
    print("\n" + "="*70)
