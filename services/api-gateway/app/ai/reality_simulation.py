"""
Predictive Reality Simulation - Phase 10 Transcendent (+15 points)
Monte Carlo universe simulation for trading
"""
import numpy as np
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class TimelineBranch:
    probability: float
    price_path: List[float]
    outcome: str
    pnl: float
    key_events: List[str]

@dataclass
class SimulationResult:
    symbol: str
    current_price: float
    timelines: List[TimelineBranch]
    expected_value: float
    risk_score: float
    confidence_interval: Tuple[float, float]
    recommendation: str

class RealitySimulator:
    """
    Monte Carlo universe simulation for trading decisions.
    
    Simulates thousands of possible market futures to help
    traders understand probability distributions of outcomes.
    
    Inspired by: Devs (TV series), quantum multiverse theory
    """
    
    def __init__(self, num_simulations: int = 10000):
        self.num_simulations = num_simulations
        self.volatility_model = 0.02  # 2% daily volatility
        self.drift_model = 0.0002     # Slight upward drift
        
    def simulate_timelines(
        self,
        symbol: str,
        current_price: float,
        days_forward: int = 30,
        scenario_type: str = "neutral"
    ) -> SimulationResult:
        """
        Simulate thousands of possible price paths.
        
        Args:
            symbol: Stock symbol
            current_price: Current price
            days_forward: Days to simulate
            scenario_type: neutral, bullish, bearish, volatile
        """
        timelines = []
        
        # Adjust parameters based on scenario
        if scenario_type == "bullish":
            drift = self.drift_model * 2
            vol = self.volatility_model * 0.8
        elif scenario_type == "bearish":
            drift = -self.drift_model * 2
            vol = self.volatility_model * 1.2
        elif scenario_type == "volatile":
            drift = self.drift_model
            vol = self.volatility_model * 2
        else:  # neutral
            drift = self.drift_model
            vol = self.volatility_model
        
        final_prices = []
        
        for i in range(self.num_simulations):
            # Generate price path using Geometric Brownian Motion
            path = self._generate_price_path(
                current_price, days_forward, drift, vol
            )
            
            # Calculate outcome metrics
            final_price = path[-1]
            final_prices.append(final_price)
            
            # Determine outcome category
            change_pct = (final_price - current_price) / current_price
            
            if change_pct > 0.2:
                outcome = "strong_bull"
            elif change_pct > 0.05:
                outcome = "moderate_bull"
            elif change_pct > -0.05:
                outcome = "neutral"
            elif change_pct > -0.2:
                outcome = "moderate_bear"
            else:
                outcome = "strong_bear"
            
            # Generate key events for this timeline
            events = self._generate_timeline_events(change_pct, days_forward)
            
            timeline = TimelineBranch(
                probability=1.0 / self.num_simulations,  # Will normalize
                price_path=path,
                outcome=outcome,
                pnl=change_pct,
                key_events=events
            )
            timelines.append(timeline)
        
        # Calculate statistics
        final_prices_array = np.array(final_prices)
        expected_value = np.mean(final_prices_array)
        std_dev = np.std(final_prices_array)
        
        # Confidence intervals
        ci_95_lower = np.percentile(final_prices_array, 2.5)
        ci_95_upper = np.percentile(final_prices_array, 97.5)
        
        # Risk score (0-100)
        risk_score = min(100, (std_dev / current_price) * 100 * 10)
        
        # Generate recommendation
        expected_return = (expected_value - current_price) / current_price
        
        if expected_return > 0.1 and risk_score < 50:
            recommendation = "STRONG BUY - High expected return, manageable risk"
        elif expected_return > 0.05:
            recommendation = "BUY - Positive expected value"
        elif expected_return > -0.05:
            recommendation = "HOLD - Neutral expected outcome"
        elif expected_return > -0.1:
            recommendation = "CONSIDER SELLING - Negative expected value"
        else:
            recommendation = "SELL - Strong negative expected value"
        
        return SimulationResult(
            symbol=symbol,
            current_price=current_price,
            timelines=timelines[:100],  # Return sample for display
            expected_value=expected_value,
            risk_score=risk_score,
            confidence_interval=(ci_95_lower, ci_95_upper),
            recommendation=recommendation
        )
    
    def _generate_price_path(
        self,
        start_price: float,
        days: int,
        drift: float,
        volatility: float
    ) -> List[float]:
        """Generate a single price path using geometric Brownian motion."""
        prices = [start_price]
        current = start_price
        
        for _ in range(days):
            # Random shock
            z = np.random.standard_normal()
            
            # Price change
            change = current * (drift + volatility * z)
            current = max(0.01, current + change)  # Price can't go below 0.01
            prices.append(current)
        
        return prices
    
    def _generate_timeline_events(self, change_pct: float, days: int) -> List[str]:
        """Generate plausible events that could lead to this outcome."""
        events = []
        
        if change_pct > 0.3:
            events.append("Major product launch success")
            events.append("Analyst upgrades")
        elif change_pct > 0.15:
            events.append("Strong earnings beat")
            events.append("Sector rotation in favor")
        elif change_pct < -0.3:
            events.append("Regulatory crackdown")
            events.append("CEO scandal")
        elif change_pct < -0.15:
            events.append("Earnings miss")
            events.append("Macro headwinds")
        else:
            events.append("Normal market fluctuation")
        
        return events
    
    def counterfactual_analysis(
        self,
        symbol: str,
        entry_price: float,
        exit_price: float,
        alternative_action: str  # "hold", "double_down", "reverse"
    ) -> Dict:
        """
        Analyze "what if" scenarios for past trades.
        
        Args:
            alternative_action: What you could have done instead
        """
        actual_pnl = exit_price - entry_price
        
        if alternative_action == "hold":
            # Simulate holding longer
            future_sim = self.simulate_timelines(
                symbol, exit_price, days_forward=30
            )
            alt_expected_pnl = future_sim.expected_value - entry_price
            
        elif alternative_action == "double_down":
            # Simulate if you had bought more
            alt_expected_pnl = actual_pnl * 2
            
        elif alternative_action == "reverse":
            # Simulate if you had shorted instead
            alt_expected_pnl = -actual_pnl
            
        else:
            alt_expected_pnl = 0
        
        return {
            "actual_pnl": actual_pnl,
            "alternative_action": alternative_action,
            "alternative_expected_pnl": alt_expected_pnl,
            "difference": alt_expected_pnl - actual_pnl,
            "lesson": self._generate_lesson(actual_pnl, alt_expected_pnl)
        }
    
    def _generate_lesson(self, actual: float, alternative: float) -> str:
        """Generate learning insight from counterfactual."""
        if alternative > actual * 1.5:
            return f"The alternative '{alternative}' would have been significantly better. Consider this strategy in similar situations."
        elif actual > alternative:
            return f"Your actual decision was better than the alternative. Good judgment!"
        else:
            return "Both options were similar - either choice was reasonable."
    
    def get_probability_cloud(
        self,
        symbol: str,
        current_price: float,
        target_prices: List[float]
    ) -> Dict:
        """
        Get probability of reaching various price levels.
        
        Returns probability cloud showing likelihood of each target.
        """
        sim_result = self.simulate_timelines(symbol, current_price, days_forward=30)
        
        probabilities = {}
        final_prices = [t.price_path[-1] for t in sim_result.timelines]
        
        for target in target_prices:
            # Probability of reaching at least this price
            prob_above = sum(1 for p in final_prices if p >= target) / len(final_prices)
            probabilities[target] = {
                "probability_above": prob_above,
                "probability_below": 1 - prob_above
            }
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "probability_cloud": probabilities,
            "interpretation": self._interpret_cloud(probabilities)
        }
    
    def _interpret_cloud(self, probabilities: Dict) -> str:
        """Generate human-readable interpretation."""
        # Find most likely outcome
        max_prob = 0
        most_likely = None
        
        for price, probs in probabilities.items():
            if probs["probability_above"] > max_prob:
                max_prob = probs["probability_above"]
                most_likely = price
        
        if most_likely and max_prob > 0.6:
            return f"Most likely to reach ${most_likely} ({max_prob:.0%} probability)"
        else:
            return "Uncertain outcome - probabilities evenly distributed"

# Global instance
reality_simulator = RealitySimulator()
