"""
SovereignOps: Unified Operations Framework

Modules:
- finops_manager: Financial operations (cost optimization, trading fees)
- devops_manager: CI/CD, deployments, feature flags
- mlops_manager: Model lifecycle, training, monitoring
- aiops_manager: Anomaly detection, root cause analysis
- blockchain_ops: Blockchain monitoring, gas optimization
- crypto_ops: Exchange management, arbitrage, liquidity
"""

from .finops_manager import FinOpsManager
from .devops_manager import DevOpsManager
from .mlops_manager import MLOpsManager
from .aiops_manager import AIOpsManager
from .blockchain_ops import BlockchainOpsManager
from .crypto_ops import CryptoOpsManager

__all__ = [
    'FinOpsManager',
    'DevOpsManager',
    'MLOpsManager',
    'AIOpsManager',
    'BlockchainOpsManager',
    'CryptoOpsManager'
]
