"""Quantum Hardware Valuation"""
from typing import Dict

class QuantumHardwareValuation:
    """Value quantum computing hardware companies"""
    
    def __init__(self, company: str = "generic"):
        self.company = company
        self.comparables = {
            "ionq": {"market_cap": 1.5e9, "qubits": 32, "revenue": 30e6},
            "rigetti": {"market_cap": 0.3e9, "qubits": 80, "revenue": 10e6},
            "ibm_quantum": {"market_cap": "private", "qubits": 1000, "revenue": "part_of_ibm"}
        }
    
    def technology_comparison(self) -> Dict:
        platforms = {
            "superconducting": {
                "leaders": ["IBM", "Google", "Rigetti"],
                "qubit_count": 1000,
                "coherence_time_us": 100,
                "gate_fidelity": 0.999,
                "scaling_challenge": "Extreme cryogenics"
            },
            "trapped_ion": {
                "leaders": ["IonQ", "Honeywell", "Quantinuum"],
                "qubit_count": 32,
                "coherence_time_s": 10,
                "gate_fidelity": 0.998,
                "scaling_challenge": "Slow gate speeds"
            },
            "photonic": {
                "leaders": ["Xanadu", "PsiQuantum"],
                "qubit_count": 216,
                "coherence_time": "Room temp",
                "gate_fidelity": 0.99,
                "scaling_challenge": "Photon loss"
            }
        }
        
        return platforms
    
    def valuation_metrics(self, qubits: int = 100, revenue: float = 10e6) -> Dict:
        # Quantum company valuation heuristics
        
        # Price per qubit (highly speculative)
        value_per_qubit = 10e6  # $10M per qubit
        qubit_value = qubits * value_per_qubit
        
        # Revenue multiple (similar to high-growth tech)
        revenue_multiple = 50  # Very high for quantum
        revenue_value = revenue * revenue_multiple
        
        # Technology premium
        tech_premium = 1.5  # 50% premium for leading tech
        
        implied_value = max(qubit_value, revenue_value) * tech_premium
        
        return {
            "qubit_based_value_millions": round(qubit_value / 1e6, 1),
            "revenue_based_value_millions": round(revenue_value / 1e6, 1),
            "implied_valuation_millions": round(implied_value / 1e6, 1),
            "value_per_qubit_millions": value_per_qubit / 1e6,
            "revenue_multiple": revenue_multiple
        }
    
    def investment_risks(self) -> Dict:
        return {
            "technical_risks": [
                "Quantum decoherence",
                "Error correction scalability",
                "Gate fidelity limitations"
            ],
            "commercial_risks": [
                "Noisy Intermediate Scale Quantum (NISQ) limitations",
                "Long path to fault tolerance",
                "Competition from classical algorithms"
            ],
            "mitigation_factors": [
                "Government funding ($25B globally)",
                "Enterprise partnerships",
                "Cloud access models"
            ],
            "time_to_profitability": "10+ years for pure plays"
        }
    
    def market_timeline(self) -> Dict:
        return {
            "2024_2027": {
                "era": "NISQ",
                "qubits": "1000-10000",
                "applications": "Proof of concept, optimization",
                "revenue_potential": "Low"
            },
            "2028_2032": {
                "era": "Early Fault Tolerant",
                "qubits": "10000-100000",
                "applications": "Limited commercial use",
                "revenue_potential": "Medium"
            },
            "2033_plus": {
                "era": "Broad Quantum Advantage",
                "qubits": "100000+",
                "applications": "Widespread adoption",
                "revenue_potential": "High"
            }
        }
