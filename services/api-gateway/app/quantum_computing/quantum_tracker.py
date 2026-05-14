"""Quantum Computing Research Tracker
Monitor quantum computing progress and related investments"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class QuantumCompany:
    name: str
    ticker: str
    approach: str  # 'superconducting', 'trapped_ion', 'photonic', etc.
    qubits: int
    stage: str
    focus: str

class QuantumComputingTracker:
    """Track quantum computing companies and research progress"""
    
    COMPANIES = [
        # Public companies
        QuantumCompany('IBM', 'IBM', 'superconducting', 1000, 'commercial', 'cloud_services'),
        QuantumCompany('Google', 'GOOGL', 'superconducting', 70, 'research', 'supremacy'),
        QuantumCompany('Microsoft', 'MSFT', 'topological', 0, 'research', 'azure_quantum'),
        QuantumCompany('Amazon', 'AMZN', 'multiple', 0, 'cloud', 'braket_platform'),
        QuantumCompany('Intel', 'INTC', 'silicon_spin', 12, 'research', 'manufacturing'),
        QuantumCompany('Nvidia', 'NVDA', 'simulation', 0, 'software', 'cuquantum'),
        
        # Pure-play quantum
        QuantumCompany('Rigetti Computing', 'RGTI', 'superconducting', 84, 'commercial', 'cloud_qpu'),
        QuantumCompany('IonQ', 'IONQ', 'trapped_ion', 32, 'commercial', 'cloud_access'),
        QuantumCompany('D-Wave', 'QBTS', 'annealing', 5000, 'commercial', 'optimization'),
        QuantumCompany('Quantum Computing Inc', 'QUBT', 'photonic', 10, 'development', 'software'),
        
        # Private leaders
        QuantumCompany('PsiQuantum', 'PRIVATE', 'photonic', 0, 'development', 'million_qubits'),
        QuantumCompany('Xanadu', 'PRIVATE', 'photonic', 216, 'commercial', 'borealis'),
        QuantumCompany('ColdQuanta', 'PRIVATE', 'neutral_atom', 100, 'development', 'cold_atom'),
        QuantumCompany('Atom Computing', 'PRIVATE', 'neutral_atom', 100, 'development', 'scalable'),
        QuantumCompany('QuEra', 'PRIVATE', 'neutral_atom', 256, 'development', 'analog'),
    ]
    
    def get_by_approach(self, approach: str) -> List[QuantumCompany]:
        """Get companies by quantum approach"""
        return [c for c in self.COMPANIES if c.approach == approach]
    
    def get_quantum_readiness_ladder(self) -> Dict:
        """Get quantum readiness milestones"""
        return {
            'current_2024': {
                'stage': 'NISQ Era',
                'description': 'Noisy Intermediate-Scale Quantum',
                'qubit_count': '50-1000',
                'applications': 'Optimization, Simulation',
                'error_rates': 'High (0.1-1%)',
                'investment_focus': 'Hardware scaling, Error mitigation'
            },
            'near_term_2025_2027': {
                'stage': 'Early Fault Tolerance',
                'description': 'First error-corrected logical qubits',
                'qubit_count': '1000-10000',
                'applications': 'Cryptography breaking (small keys), Drug discovery',
                'error_rates': 'Medium (0.01-0.1%)',
                'investment_focus': 'Error correction algorithms, Quantum networking'
            },
            'medium_term_2028_2032': {
                'stage': 'Quantum Advantage',
                'description': 'Practical quantum advantage for commercial problems',
                'qubit_count': '10000-100000',
                'applications': 'Financial modeling, AI/ML, Materials science',
                'error_rates': 'Low (0.001-0.01%)',
                'investment_focus': 'Quantum software ecosystem, Cloud platforms'
            },
            'long_term_2033_plus': {
                'stage': 'Fault Tolerant Era',
                'description': 'Fully error-corrected quantum computers',
                'qubit_count': '100000+',
                'applications': 'Breaking RSA-2048, General AI, Climate modeling',
                'error_rates': 'Negligible (<0.001%)',
                'investment_focus': 'Post-quantum security, Quantum internet'
            }
        }
    
    def get_financial_applications(self) -> Dict:
        """Get quantum computing applications in finance"""
        return {
            'portfolio_optimization': {
                'description': 'Solve complex portfolio optimization faster',
                'timeline': '2026-2028',
                'advantage': '10-100x speedup for mean-variance optimization',
                'companies': ['RGTI', 'IONQ', 'IBM']
            },
            'risk_analysis': {
                'description': 'Monte Carlo simulations for risk modeling',
                'timeline': '2025-2027',
                'advantage': 'Quadratic speedup in sampling',
                'companies': ['IBM', 'QBTS', 'GOOGL']
            },
            'fraud_detection': {
                'description': 'Pattern recognition in transaction data',
                'timeline': '2027-2030',
                'advantage': 'Quantum machine learning advantages',
                'companies': ['IONQ', 'MSFT']
            },
            'cryptography_security': {
                'description': 'Post-quantum cryptography preparation',
                'timeline': 'NOW-2030',
                'advantage': 'Protect against quantum attacks',
                'companies': ['All - use lattice-based crypto']
            }
        }
    
    def get_investment_recommendations(self) -> Dict:
        """Get quantum computing investment recommendations"""
        return {
            'conservative': {
                'strategy': 'Invest in large tech with quantum divisions',
                'tickers': ['IBM', 'GOOGL', 'MSFT', 'AMZN'],
                'rationale': 'Diversified exposure with quantum as bonus'
            },
            'moderate': {
                'strategy': 'Mix of pure-play and tech giants',
                'tickers': ['IONQ', 'RGTI', 'IBM', 'NVDA'],
                'rationale': 'Balanced quantum-specific and diversified exposure'
            },
            'aggressive': {
                'strategy': 'Pure-play quantum computing',
                'tickers': ['IONQ', 'RGTI', 'QBTS', 'QUBT'],
                'rationale': 'Maximum quantum upside, high volatility'
            },
            'quantum_enablers': {
                'strategy': 'Companies enabling quantum ecosystem',
                'tickers': ['NVDA', 'AMAT', 'LRCX', 'KLAC'],
                'rationale': 'Pick-and-shovel play on quantum infrastructure'
            }
        }
    
    def track_ibm_roadmap(self) -> Dict:
        """Track IBM quantum roadmap milestones"""
        return {
            '2023': {'milestone': 'Condor 1121 qubits', 'status': 'completed'},
            '2024': {'milestone': 'Flamingo 5000+ qubits', 'status': 'in_progress'},
            '2025': {'milestone': 'Kookaburra error correction', 'status': 'planned'},
            '2029': {'milestone': '100000 qubits', 'status': 'roadmap'},
            '2033': {'milestone': '1000000 qubits', 'status': 'vision'}
        }

# Usage
def get_quantum_summary() -> Dict:
    """Quick quantum computing summary"""
    tracker = QuantumComputingTracker()
    
    return {
        'readiness_ladder': tracker.get_quantum_readiness_ladder(),
        'financial_applications': tracker.get_financial_applications(),
        'recommendations': tracker.get_investment_recommendations(),
        'public_pure_play': [
            {'name': c.name, 'ticker': c.ticker, 'qubits': c.qubits}
            for c in tracker.COMPANIES
            if c.ticker != 'PRIVATE'
        ]
    }
