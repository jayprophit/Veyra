"""
Quantum Portfolio Optimization
=============================
Quantum computing algorithms for portfolio optimization using Qiskit
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from scipy.optimize import minimize
import json

logger = logging.getLogger(__name__)


class QuantumAlgorithm(Enum):
    """Quantum algorithm types"""
    VQE = "variational_quantum_eigensolver"
    QAOA = "quantum_approximate_optimization_algorithm"
    GROVER = "grover_search"
    QUANTUM_ANNEALING = "quantum_annealing"
    QUANTUM_ML = "quantum_machine_learning"


@dataclass
class QuantumPortfolio:
    """Quantum portfolio optimization result"""
    portfolio_id: str
    optimal_weights: Dict[str, float]
    expected_return: float
    risk: float
    sharpe_ratio: float
    quantum_algorithm: QuantumAlgorithm
    quantum_circuit_depth: int
    classical_comparison: Dict[str, float]
    quantum_advantage: float
    computation_time: float
    created_at: datetime


@dataclass
class QuantumAsset:
    """Asset for quantum optimization"""
    symbol: str
    expected_return: float
    volatility: float
    correlation_matrix: Optional[np.ndarray] = None
    quantum_state: Optional[np.ndarray] = None


class QuantumPortfolioOptimizer:
    """Quantum portfolio optimization using quantum algorithms"""
    
    def __init__(self, backend_name: str = "aer_simulator"):
        self.backend_name = backend_name
        self.quantum_assets: List[QuantumAsset] = []
        self.portfolio_results: Dict[str, QuantumPortfolio] = []
        self.quantum_circuits: Dict[str, Any] = {}
        
        # Initialize quantum backend (mock implementation)
        self._initialize_quantum_backend()
        
    def _initialize_quantum_backend(self):
        """Initialize quantum computing backend"""
        try:
            # Mock quantum backend initialization
            # In production, would use actual Qiskit or Cirq
            logger.info(f"Initializing quantum backend: {self.backend_name}")
            
            # Mock quantum backend properties
            self.quantum_backend = {
                "name": self.backend_name,
                "qubits": 32,
                "gate_fidelity": 0.999,
                "measurement_fidelity": 0.995,
                "coherence_time": 100.0,  # microseconds
                "gate_time": 0.1  # nanoseconds
            }
            
        except Exception as e:
            logger.error(f"Error initializing quantum backend: {e}")
            raise
            
    def add_quantum_asset(self, symbol: str, expected_return: float, volatility: float, 
                         correlation_data: Optional[np.ndarray] = None):
        """Add asset for quantum optimization"""
        try:
            # Create quantum state representation
            quantum_state = self._create_quantum_state(expected_return, volatility)
            
            asset = QuantumAsset(
                symbol=symbol,
                expected_return=expected_return,
                volatility=volatility,
                correlation_matrix=correlation_data,
                quantum_state=quantum_state
            )
            
            self.quantum_assets.append(asset)
            logger.info(f"Added quantum asset: {symbol}")
            
        except Exception as e:
            logger.error(f"Error adding quantum asset: {e}")
            raise
            
    def _create_quantum_state(self, expected_return: float, volatility: float) -> np.ndarray:
        """Create quantum state representation of asset"""
        try:
            # Normalize expected return and volatility to quantum state
            normalized_return = (expected_return + 1) / 2  # Normalize to [0, 1]
            normalized_volatility = volatility / (volatility + 1)  # Normalize to [0, 1]
            
            # Create 2-qubit quantum state
            # First qubit represents return, second qubit represents risk
            alpha = np.sqrt(normalized_return)
            beta = np.sqrt(1 - normalized_return)
            gamma = np.sqrt(normalized_volatility)
            delta = np.sqrt(1 - normalized_volatility)
            
            # Create entangled state
            quantum_state = np.array([
                alpha * gamma,  # |00⟩
                alpha * delta,  # |01⟩
                beta * gamma,   # |10⟩
                beta * delta    # |11⟩
            ], dtype=complex)
            
            # Normalize
            quantum_state = quantum_state / np.linalg.norm(quantum_state)
            
            return quantum_state
            
        except Exception as e:
            logger.error(f"Error creating quantum state: {e}")
            raise
            
    async def optimize_portfolio_qaoa(self, risk_aversion: float = 0.5, max_iterations: int = 100) -> QuantumPortfolio:
        """Optimize portfolio using Quantum Approximate Optimization Algorithm (QAOA)"""
        try:
            logger.info("Starting QAOA portfolio optimization")
            
            start_time = datetime.now()
            
            # Prepare quantum problem
            n_assets = len(self.quantum_assets)
            if n_assets < 2:
                raise ValueError("Need at least 2 assets for optimization")
                
            # Create QAOA circuit
            qaoa_circuit = self._create_qaoa_circuit(n_assets, risk_aversion)
            
            # Optimize parameters (mock implementation)
            optimal_params = await self._optimize_qaoa_parameters(qaoa_circuit, max_iterations)
            
            # Extract optimal portfolio weights
            optimal_weights = self._extract_weights_from_qaoa_result(optimal_params, n_assets)
            
            # Calculate portfolio metrics
            expected_return = self._calculate_portfolio_return(optimal_weights)
            risk = self._calculate_portfolio_risk(optimal_weights)
            sharpe_ratio = expected_return / risk if risk > 0 else 0
            
            # Compare with classical optimization
            classical_result = await self._classical_portfolio_optimization(risk_aversion)
            
            # Calculate quantum advantage
            quantum_advantage = self._calculate_quantum_advantage(sharpe_ratio, classical_result["sharpe_ratio"])
            
            computation_time = (datetime.now() - start_time).total_seconds()
            
            portfolio = QuantumPortfolio(
                portfolio_id=f"qaoa_{int(datetime.now().timestamp())}",
                optimal_weights=optimal_weights,
                expected_return=expected_return,
                risk=risk,
                sharpe_ratio=sharpe_ratio,
                quantum_algorithm=QuantumAlgorithm.QAOA,
                quantum_circuit_depth=len(optimal_params) * 2,
                classical_comparison=classical_result,
                quantum_advantage=quantum_advantage,
                computation_time=computation_time,
                created_at=datetime.now()
            )
            
            self.portfolio_results[portfolio.portfolio_id] = portfolio
            
            logger.info(f"QAOA optimization completed. Sharpe ratio: {sharpe_ratio:.4f}")
            return portfolio
            
        except Exception as e:
            logger.error(f"Error in QAOA optimization: {e}")
            raise
            
    def _create_qaoa_circuit(self, n_assets: int, risk_aversion: float) -> Dict[str, Any]:
        """Create QAOA circuit for portfolio optimization"""
        try:
            # Mock QAOA circuit creation
            # In production, would use actual Qiskit QAOA implementation
            
            circuit = {
                "n_qubits": n_assets,
                "n_layers": 2,
                "cost_function": "portfolio_sharpe_ratio",
                "mixing_operator": "x_mixer",
                "cost_operator": "portfolio_cost",
                "parameters": {
                    "gamma": np.random.uniform(0, np.pi, 2),
                    "beta": np.random.uniform(0, np.pi, 2)
                },
                "risk_aversion": risk_aversion
            }
            
            # Store quantum circuit
            self.quantum_circuits[f"qaoa_{n_assets}"] = circuit
            
            return circuit
            
        except Exception as e:
            logger.error(f"Error creating QAOA circuit: {e}")
            raise
            
    async def _optimize_qaoa_parameters(self, circuit: Dict[str, Any], max_iterations: int) -> np.ndarray:
        """Optimize QAOA parameters"""
        try:
            # Mock parameter optimization
            # In production, would use actual quantum optimization
            
            best_params = circuit["parameters"]
            best_cost = float('inf')
            
            for iteration in range(max_iterations):
                # Random parameter search (mock)
                current_params = {
                    "gamma": np.random.uniform(0, np.pi, 2),
                    "beta": np.random.uniform(0, np.pi, 2)
                }
                
                # Evaluate cost function (mock)
                current_cost = self._evaluate_qaoa_cost(current_params)
                
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_params = current_params
                    
            # Convert to numpy array
            optimal_params = np.concatenate([
                best_params["gamma"],
                best_params["beta"]
            ])
            
            return optimal_params
            
        except Exception as e:
            logger.error(f"Error optimizing QAOA parameters: {e}")
            raise
            
    def _evaluate_qaoa_cost(self, params: Dict[str, Any]) -> float:
        """Evaluate QAOA cost function"""
        try:
            # Mock cost evaluation
            # In production, would run quantum circuit and measure expectation value
            
            # Simulate cost based on parameter values
            gamma_sum = np.sum(params["gamma"])
            beta_sum = np.sum(params["beta"])
            
            cost = gamma_sum * 0.5 + beta_sum * 0.3 + np.random.uniform(-0.1, 0.1)
            
            return cost
            
        except Exception as e:
            logger.error(f"Error evaluating QAOA cost: {e}")
            raise
            
    def _extract_weights_from_qaoa_result(self, optimal_params: np.ndarray, n_assets: int) -> Dict[str, float]:
        """Extract optimal portfolio weights from QAOA result"""
        try:
            # Mock weight extraction
            # In production, would decode quantum measurement results
            
            # Generate weights based on quantum parameters
            weights = []
            for i in range(n_assets):
                # Use quantum parameters to determine weight
                weight = 0.5 + 0.3 * np.sin(optimal_params[i % len(optimal_params)])
                weight = max(0, min(1, weight))  # Clamp to [0, 1]
                weights.append(weight)
                
            # Normalize weights to sum to 1
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            # Map to asset symbols
            optimal_weights = {}
            for i, asset in enumerate(self.quantum_assets):
                optimal_weights[asset.symbol] = normalized_weights[i]
                
            return optimal_weights
            
        except Exception as e:
            logger.error(f"Error extracting weights from QAOA result: {e}")
            raise
            
    async def optimize_portfolio_vqe(self, risk_aversion: float = 0.5, max_iterations: int = 100) -> QuantumPortfolio:
        """Optimize portfolio using Variational Quantum Eigensolver (VQE)"""
        try:
            logger.info("Starting VQE portfolio optimization")
            
            start_time = datetime.now()
            
            # Prepare quantum problem
            n_assets = len(self.quantum_assets)
            if n_assets < 2:
                raise ValueError("Need at least 2 assets for optimization")
                
            # Create VQE circuit
            vqe_circuit = self._create_vqe_circuit(n_assets, risk_aversion)
            
            # Optimize parameters
            optimal_params = await self._optimize_vqe_parameters(vqe_circuit, max_iterations)
            
            # Extract optimal portfolio weights
            optimal_weights = self._extract_weights_from_vqe_result(optimal_params, n_assets)
            
            # Calculate portfolio metrics
            expected_return = self._calculate_portfolio_return(optimal_weights)
            risk = self._calculate_portfolio_risk(optimal_weights)
            sharpe_ratio = expected_return / risk if risk > 0 else 0
            
            # Compare with classical optimization
            classical_result = await self._classical_portfolio_optimization(risk_aversion)
            
            # Calculate quantum advantage
            quantum_advantage = self._calculate_quantum_advantage(sharpe_ratio, classical_result["sharpe_ratio"])
            
            computation_time = (datetime.now() - start_time).total_seconds()
            
            portfolio = QuantumPortfolio(
                portfolio_id=f"vqe_{int(datetime.now().timestamp())}",
                optimal_weights=optimal_weights,
                expected_return=expected_return,
                risk=risk,
                sharpe_ratio=sharpe_ratio,
                quantum_algorithm=QuantumAlgorithm.VQE,
                quantum_circuit_depth=len(optimal_params) * 3,
                classical_comparison=classical_result,
                quantum_advantage=quantum_advantage,
                computation_time=computation_time,
                created_at=datetime.now()
            )
            
            self.portfolio_results[portfolio.portfolio_id] = portfolio
            
            logger.info(f"VQE optimization completed. Sharpe ratio: {sharpe_ratio:.4f}")
            return portfolio
            
        except Exception as e:
            logger.error(f"Error in VQE optimization: {e}")
            raise
            
    def _create_vqe_circuit(self, n_assets: int, risk_aversion: float) -> Dict[str, Any]:
        """Create VQE circuit for portfolio optimization"""
        try:
            # Mock VQE circuit creation
            circuit = {
                "n_qubits": n_assets,
                "ansatz": "hardware_efficient",
                "optimizer": "SPSA",
                "initial_point": np.random.uniform(0, 2*np.pi, n_assets*2),
                "risk_aversion": risk_aversion
            }
            
            self.quantum_circuits[f"vqe_{n_assets}"] = circuit
            return circuit
            
        except Exception as e:
            logger.error(f"Error creating VQE circuit: {e}")
            raise
            
    async def _optimize_vqe_parameters(self, circuit: Dict[str, Any], max_iterations: int) -> np.ndarray:
        """Optimize VQE parameters"""
        try:
            # Mock VQE parameter optimization
            optimal_params = circuit["initial_point"]
            
            for iteration in range(max_iterations):
                # Simulate parameter update
                gradient = np.random.uniform(-0.1, 0.1, len(optimal_params))
                learning_rate = 0.01
                optimal_params = optimal_params - learning_rate * gradient
                
            return optimal_params
            
        except Exception as e:
            logger.error(f"Error optimizing VQE parameters: {e}")
            raise
            
    def _extract_weights_from_vqe_result(self, optimal_params: np.ndarray, n_assets: int) -> Dict[str, float]:
        """Extract optimal portfolio weights from VQE result"""
        try:
            # Mock weight extraction from VQE
            weights = []
            for i in range(n_assets):
                # Use VQE parameters to determine weight
                weight = 0.5 + 0.2 * np.cos(optimal_params[i])
                weight = max(0, min(1, weight))
                weights.append(weight)
                
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            optimal_weights = {}
            for i, asset in enumerate(self.quantum_assets):
                optimal_weights[asset.symbol] = normalized_weights[i]
                
            return optimal_weights
            
        except Exception as e:
            logger.error(f"Error extracting weights from VQE result: {e}")
            raise
            
    def _calculate_portfolio_return(self, weights: Dict[str, float]) -> float:
        """Calculate expected portfolio return"""
        try:
            portfolio_return = 0.0
            for asset in self.quantum_assets:
                if asset.symbol in weights:
                    portfolio_return += weights[asset.symbol] * asset.expected_return
            return portfolio_return
            
        except Exception as e:
            logger.error(f"Error calculating portfolio return: {e}")
            raise
            
    def _calculate_portfolio_risk(self, weights: Dict[str, float]) -> float:
        """Calculate portfolio risk (volatility)"""
        try:
            # Mock risk calculation
            # In production, would use full covariance matrix
            portfolio_risk = 0.0
            
            for asset in self.quantum_assets:
                if asset.symbol in weights:
                    weight = weights[asset.symbol]
                    portfolio_risk += (weight ** 2) * (asset.volatility ** 2)
                    
            return np.sqrt(portfolio_risk)
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            raise
            
    async def _classical_portfolio_optimization(self, risk_aversion: float) -> Dict[str, float]:
        """Classical portfolio optimization for comparison"""
        try:
            # Mock classical optimization using Markowitz model
            n_assets = len(self.quantum_assets)
            
            # Initial weights (equal allocation)
            initial_weights = np.array([1/n_assets] * n_assets)
            
            # Constraints: weights sum to 1
            constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
            
            # Bounds: weights between 0 and 1
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # Objective function (negative Sharpe ratio)
            def objective(weights):
                weights_dict = {self.quantum_assets[i].symbol: weights[i] for i in range(n_assets)}
                return_ = self._calculate_portfolio_return(weights_dict)
                risk = self._calculate_portfolio_risk(weights_dict)
                sharpe = return_ / risk if risk > 0 else 0
                return -sharpe  # Minimize negative Sharpe ratio
                
            # Optimize
            result = minimize(objective, initial_weights, method="SLSQP", 
                            bounds=bounds, constraints=constraints)
            
            optimal_weights = result.x
            weights_dict = {self.quantum_assets[i].symbol: optimal_weights[i] for i in range(n_assets)}
            
            expected_return = self._calculate_portfolio_return(weights_dict)
            risk = self._calculate_portfolio_risk(weights_dict)
            sharpe_ratio = expected_return / risk if risk > 0 else 0
            
            return {
                "weights": weights_dict,
                "expected_return": expected_return,
                "risk": risk,
                "sharpe_ratio": sharpe_ratio
            }
            
        except Exception as e:
            logger.error(f"Error in classical optimization: {e}")
            raise
            
    def _calculate_quantum_advantage(self, quantum_sharpe: float, classical_sharpe: float) -> float:
        """Calculate quantum advantage over classical approach"""
        try:
            if classical_sharpe == 0:
                return float('inf') if quantum_sharpe > 0 else 0
                
            advantage = (quantum_sharpe - classical_sharpe) / abs(classical_sharpe)
            return advantage
            
        except Exception as e:
            logger.error(f"Error calculating quantum advantage: {e}")
            raise
            
    async def quantum_risk_analysis(self, portfolio_id: str) -> Dict[str, Any]:
        """Perform quantum risk analysis on portfolio"""
        try:
            portfolio = self.portfolio_results.get(portfolio_id)
            if not portfolio:
                raise ValueError(f"Portfolio not found: {portfolio_id}")
                
            # Quantum Monte Carlo simulation
            quantum_monte_carlo = await self._quantum_monte_carlo_simulation(portfolio)
            
            # Quantum Value at Risk (VaR)
            quantum_var = await self._quantum_var_calculation(portfolio)
            
            # Quantum stress testing
            quantum_stress = await self._quantum_stress_testing(portfolio)
            
            risk_analysis = {
                "portfolio_id": portfolio_id,
                "quantum_monte_carlo": quantum_monte_carlo,
                "quantum_var": quantum_var,
                "quantum_stress": quantum_stress,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            return risk_analysis
            
        except Exception as e:
            logger.error(f"Error in quantum risk analysis: {e}")
            raise
            
    async def _quantum_monte_carlo_simulation(self, portfolio: QuantumPortfolio) -> Dict[str, Any]:
        """Quantum Monte Carlo simulation"""
        try:
            # Mock quantum Monte Carlo
            n_simulations = 10000
            returns = []
            
            for _ in range(n_simulations):
                # Simulate quantum-enhanced random walk
                quantum_noise = np.random.normal(0, 0.1)  # Quantum uncertainty
                simulated_return = portfolio.expected_return + quantum_noise
                returns.append(simulated_return)
                
            returns = np.array(returns)
            
            return {
                "simulations": n_simulations,
                "mean_return": np.mean(returns),
                "volatility": np.std(returns),
                "var_95": np.percentile(returns, 5),
                "var_99": np.percentile(returns, 1),
                "quantum_enhancement": 0.15  # Mock quantum enhancement
            }
            
        except Exception as e:
            logger.error(f"Error in quantum Monte Carlo: {e}")
            raise
            
    async def _quantum_var_calculation(self, portfolio: QuantumPortfolio) -> Dict[str, Any]:
        """Quantum Value at Risk calculation"""
        try:
            # Mock quantum VaR calculation
            confidence_levels = [0.90, 0.95, 0.99]
            var_results = {}
            
            for confidence in confidence_levels:
                # Quantum-enhanced VaR calculation
                quantum_var = portfolio.risk * np.percentile(np.random.normal(0, 1, 1000), (1-confidence) * 100)
                var_results[f"var_{int(confidence*100)}"] = quantum_var
                
            return var_results
            
        except Exception as e:
            logger.error(f"Error in quantum VaR calculation: {e}")
            raise
            
    async def _quantum_stress_testing(self, portfolio: QuantumPortfolio) -> Dict[str, Any]:
        """Quantum stress testing"""
        try:
            # Mock quantum stress testing scenarios
            scenarios = {
                "market_crash": {"return_shock": -0.3, "volatility_multiplier": 2.0},
                "interest_rate_shock": {"return_shock": -0.1, "volatility_multiplier": 1.5},
                "liquidity_crisis": {"return_shock": -0.2, "volatility_multiplier": 1.8}
            }
            
            stress_results = {}
            
            for scenario_name, scenario_params in scenarios.items():
                # Apply quantum-enhanced stress scenario
                stressed_return = portfolio.expected_return * (1 + scenario_params["return_shock"])
                stressed_volatility = portfolio.risk * scenario_params["volatility_multiplier"]
                
                stress_results[scenario_name] = {
                    "stressed_return": stressed_return,
                    "stressed_volatility": stressed_volatility,
                    "quantum_resilience": 0.8  # Mock quantum resilience factor
                }
                
            return stress_results
            
        except Exception as e:
            logger.error(f"Error in quantum stress testing: {e}")
            raise
            
    def get_quantum_advantage_report(self) -> Dict[str, Any]:
        """Generate comprehensive quantum advantage report"""
        try:
            if not self.portfolio_results:
                return {"error": "No portfolio results available"}
                
            # Calculate aggregate quantum advantage
            quantum_advantages = [p.quantum_advantage for p in self.portfolio_results.values()]
            avg_quantum_advantage = np.mean(quantum_advantages)
            
            # Algorithm performance comparison
            algorithm_performance = {}
            for portfolio in self.portfolio_results.values():
                algo = portfolio.quantum_algorithm.value
                if algo not in algorithm_performance:
                    algorithm_performance[algo] = []
                algorithm_performance[algo].append(portfolio.sharpe_ratio)
                
            # Calculate average performance by algorithm
            avg_performance = {}
            for algo, sharpe_ratios in algorithm_performance.items():
                avg_performance[algo] = np.mean(sharpe_ratios)
                
            return {
                "total_portfolios": len(self.portfolio_results),
                "average_quantum_advantage": avg_quantum_advantage,
                "algorithm_performance": avg_performance,
                "quantum_backend": self.quantum_backend,
                "best_portfolio": max(self.portfolio_results.values(), key=lambda p: p.sharpe_ratio),
                "report_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating quantum advantage report: {e}")
            raise


# Global quantum portfolio optimizer instance
_quantum_optimizer = None

def get_quantum_portfolio_optimizer() -> QuantumPortfolioOptimizer:
    """Get the global quantum portfolio optimizer instance"""
    global _quantum_optimizer
    if _quantum_optimizer is None:
        _quantum_optimizer = QuantumPortfolioOptimizer()
    return _quantum_optimizer
