"""
Open-Source Integrations
100% free, open-source alternatives to paid financial data providers
"""

from .opensource_data_sources import OpenSourceDataManager, get_opensource_data_manager
from .github_integrations import GitHubIntegrations, get_github_integrations
from .huggingface_integrations import HuggingFaceIntegrations, get_huggingface_integrations
from .kaggle_integrations import KaggleIntegrations, get_kaggle_integrations

__all__ = [
    'OpenSourceDataManager',
    'get_opensource_data_manager',
    'GitHubIntegrations',
    'get_github_integrations',
    'HuggingFaceIntegrations',
    'get_huggingface_integrations',
    'KaggleIntegrations',
    'get_kaggle_integrations'
]
