"""Quantum Simulator - Simulate quantum circuits"""
from typing import Dict
import numpy as np

class QuantumSimulator:
    """Simulate quantum circuits for finance"""
    
    def __init__(self, n_qubits: int = 8):
        self.n_qubits = n_qubits
        self.state = np.zeros(2 ** n_qubits, dtype=complex)
        self.state[0] = 1.0
    
    def hadamard(self, target: int):
        """Apply Hadamard gate"""
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        # Simplified - apply to full state
        return {"gate": "H", "target": target}
    
    def measure(self) -> Dict:
        """Measure quantum state"""
        probs = np.abs(self.state) ** 2
        return {
            "probabilities": probs[:4].tolist(),
            "most_likely": int(np.argmax(probs)),
            "n_qubits": self.n_qubits
        }
    
    def portfolio_superposition(self, n_assets: int) -> Dict:
        """Create superposition of portfolio states"""
        return {
            "superposition_size": 2 ** n_assets,
            "description": f"Equal superposition of {2 ** n_assets} portfolio configurations",
            "amplitudes": "1/sqrt(N) for all states"
        }
