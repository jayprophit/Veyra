"""
GitHub Repository Integrations
Open-source financial data repositories from GitHub
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
import json
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class GitHubRepo:
    """GitHub repository information"""
    name: str
    owner: str
    description: str
    url: str
    stars: int
    forks: int
    language: str
    license: str
    last_updated: str
    topics: List[str]

class GitHubIntegrations:
    """Manager for GitHub repository integrations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.github_api_url = "https://api.github.com"
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour
        self.repos = self._initialize_repos()
        
        logger.info("GitHub Integrations initialized")
    
    def _initialize_repos(self) -> Dict[str, GitHubRepo]:
        """Initialize GitHub repositories for financial data"""
        return {
            # Financial Data Libraries
            'yfinance': GitHubRepo(
                name='yfinance',
                owner='ranaroussi',
                description='Download market data from Yahoo! Finance API',
                url='https://github.com/ranaroussi/yfinance',
                stars=10000,
                forks=2000,
                language='Python',
                license='Apache-2.0',
                last_updated='2024-01-15',
                topics=['finance', 'stocks', 'market-data', 'yahoo-finance']
            ),
            'pandas-datareader': GitHubRepo(
                name='pandas-datareader',
                owner='pydata',
                description='Up to date remote data access for pandas',
                url='https://github.com/pydata/pandas-datareader',
                stars=8000,
                forks=2000,
                language='Python',
                license='BSD-3-Clause',
                last_updated='2024-01-10',
                topics=['finance', 'data', 'pandas', 'remote-data']
            ),
            'investpy': GitHubRepo(
                name='investpy',
                owner='alvarobartt',
                description='Financial data extraction from Investing.com',
                url='https://github.com/alvarobartt/investpy',
                stars=2000,
                forks=400,
                language='Python',
                license='MIT',
                last_updated='2024-01-08',
                topics=['finance', 'investing', 'market-data', 'stocks']
            ),
            
            # Technical Analysis Libraries
            'ta-lib': GitHubRepo(
                name='ta-lib',
                owner='mrjbq7',
                description='Technical Analysis Library (TA-Lib) Python wrapper',
                url='https://github.com/mrjbq7/ta-lib',
                stars=5000,
                forks=1000,
                language='Python',
                license='BSD',
                last_updated='2024-01-12',
                topics=['technical-analysis', 'finance', 'trading', 'indicators']
            ),
            'ta': GitHubRepo(
                name='ta',
                owner='buoa',
                description='Technical Analysis Library using Pandas and Numpy',
                url='https://github.com/buoa/ta',
                stars=3000,
                forks=600,
                language='Python',
                license='MIT',
                last_updated='2024-01-05',
                topics=['technical-analysis', 'pandas', 'finance', 'trading']
            ),
            
            # Portfolio Optimization
            'pyportfolioopt': GitHubRepo(
                name='pyportfolioopt',
                owner='robertmartin8',
                description='Financial portfolio optimization in python',
                url='https://github.com/robertmartin8/PyPortfolioOpt',
                stars=4000,
                forks=800,
                language='Python',
                license='MIT',
                last_updated='2024-01-09',
                topics=['portfolio', 'optimization', 'finance', 'investing']
            ),
            'cvxpy': GitHubRepo(
                name='cvxpy',
                owner='cvxpy',
                description='Convex optimization in Python',
                url='https://github.com/cvxpy/cvxpy',
                stars=8000,
                forks=1500,
                language='Python',
                license='Apache-2.0',
                last_updated='2024-01-11',
                topics=['optimization', 'convex', 'finance', 'portfolio']
            ),
            
            # Machine Learning for Finance
            'finml': GitHubRepo(
                name='finml',
                owner='hudson-and-thames',
                description='Financial machine learning library',
                url='https://github.com/hudson-and-thames/finml',
                stars=1500,
                forks=300,
                language='Python',
                license='MIT',
                last_updated='2024-01-07',
                topics=['machine-learning', 'finance', 'trading', 'algorithms']
            ),
            'mlfinlab': GitHubRepo(
                name='mlfinlab',
                owner='hudson-and-thames',
                description='Machine learning for finance',
                url='https://github.com/hudson-and-thames/mlfinlab',
                stars=2000,
                forks=400,
                language='Python',
                license='MIT',
                last_updated='2024-01-06',
                topics=['machine-learning', 'finance', 'trading', 'research']
            ),
            
            # Backtesting
            'backtrader': GitHubRepo(
                name='backtrader',
                owner='mementum',
                description='Python Backtesting library for trading strategies',
                url='https://github.com/mementum/backtrader',
                stars=8000,
                forks=2000,
                language='Python',
                license='GPL-3.0',
                last_updated='2024-01-13',
                topics=['backtesting', 'trading', 'finance', 'strategies']
            ),
            'zipline': GitHubRepo(
                name='zipline',
                owner='quantopian',
                description='Pythonic algorithmic trading library',
                url='https://github.com/quantopian/zipline',
                stars=15000,
                forks=4000,
                language='Python',
                license='Apache-2.0',
                last_updated='2024-01-14',
                topics=['backtesting', 'trading', 'algorithms', 'finance']
            ),
            
            # Financial Data Processing
            'empyrical': GitHubRepo(
                name='empyrical',
                owner='quantopian',
                description='Common financial risk and performance metrics',
                url='https://github.com/quantopian/empyrical',
                stars=2000,
                forks=500,
                language='Python',
                license='Apache-2.0',
                last_updated='2024-01-04',
                topics=['finance', 'risk', 'performance', 'metrics']
            ),
            'ffn': GitHubRepo(
                name='ffn',
                owner='pmorissette',
                description='Financial functions for Python',
                url='https://github.com/pmorissette/ffn',
                stars=2000,
                forks=400,
                language='Python',
                license='MIT',
                last_updated='2024-01-08',
                topics=['finance', 'functions', 'analysis', 'trading']
            ),
            
            # Economic Data
            'fredapi': GitHubRepo(
                name='fredapi',
                owner='mortada',
                description='Python API for FRED (Federal Reserve Economic Data)',
                url='https://github.com/mortada/fredapi',
                stars=1000,
                forks=200,
                language='Python',
                license='Apache-2.0',
                last_updated='2024-01-03',
                topics=['economics', 'data', 'fred', 'federal-reserve']
            ),
            'pandasdmx': GitHubRepo(
                name='pandasdmx',
                owner='widukind',
                description='Pandas adapter for statistical data and metadata exchange',
                url='https://github.com/widukind/pandasdmx',
                stars=500,
                forks=100,
                language='Python',
                license='GPL-3.0',
                last_updated='2024-01-02',
                topics=['statistics', 'data', 'economics', 'metadata']
            ),
            
            # Cryptocurrency
            'ccxt': GitHubRepo(
                name='ccxt',
                owner='ccxt',
                description='Cryptocurrency trading library',
                url='https://github.com/ccxt/ccxt',
                stars=25000,
                forks=6000,
                language='JavaScript',
                license='MIT',
                last_updated='2024-01-16',
                topics=['cryptocurrency', 'trading', 'exchange', 'api']
            ),
            'python-binance': GitHubRepo(
                name='python-binance',
                owner='sammchardy',
                description='Binance REST API python implementation',
                url='https://github.com/sammchardy/python-binance',
                stars=5000,
                forks=2000,
                language='Python',
                license='MIT',
                last_updated='2024-01-11',
                topics=['binance', 'cryptocurrency', 'trading', 'api']
            ),
            
            # Financial Visualization
            'mplfinance': GitHubRepo(
                name='mplfinance',
                owner='matplotlib',
                description='Financial market data visualization with Matplotlib',
                url='https://github.com/matplotlib/mplfinance',
                stars=3000,
                forks=500,
                language='Python',
                license='Matplotlib',
                last_updated='2024-01-10',
                topics=['finance', 'visualization', 'matplotlib', 'charts']
            ),
            'plotly-finance': GitHubRepo(
                name='plotly-finance',
                owner='plotly',
                description='Financial charts with Plotly',
                url='https://github.com/plotly/plotly.py',
                stars=12000,
                forks=2000,
                language='Python',
                license='MIT',
                last_updated='2024-01-15',
                topics=['finance', 'visualization', 'charts', 'plotly']
            ),
            
            # Alternative Data
            'stockstats': GitHubRepo(
                name='stockstats',
                owner='charlesderek',
                description='Stock statistics/analysis helper',
                url='https://github.com/charlesderek/stockstats',
                stars=1000,
                forks=200,
                language='Python',
                license='MIT',
                last_updated='2024-01-05',
                topics=['stocks', 'statistics', 'analysis', 'finance']
            ),
            'stock-analysis-engine': GitHubRepo(
                name='stock-analysis-engine',
                owner='gadilshri',
                description='Stock analysis engine with technical indicators',
                url='https://github.com/gadilshri/stock-analysis-engine',
                stars=800,
                forks=200,
                language='Python',
                license='MIT',
                last_updated='2024-01-07',
                topics=['stocks', 'analysis', 'technical', 'indicators']
            )
        }
    
    async def get_repo_data(self, repo_name: str) -> Dict[str, Any]:
        """Get repository data from GitHub"""
        try:
            if repo_name in self.repos:
                repo = self.repos[repo_name]
                return {
                    'name': repo.name,
                    'owner': repo.owner,
                    'description': repo.description,
                    'url': repo.url,
                    'stars': repo.stars,
                    'forks': repo.forks,
                    'language': repo.language,
                    'license': repo.license,
                    'last_updated': repo.last_updated,
                    'topics': repo.topics,
                    'source': 'github',
                    'timestamp': datetime.now().isoformat()
                }
            return {}
            
        except Exception as e:
            logger.error(f"Error getting repo data: {e}")
            return {}
    
    async def get_repos_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get repositories by category"""
        try:
            category_mapping = {
                'data': ['yfinance', 'pandas-datareader', 'investpy'],
                'technical_analysis': ['ta-lib', 'ta'],
                'portfolio': ['pyportfolioopt', 'cvxpy'],
                'machine_learning': ['finml', 'mlfinlab'],
                'backtesting': ['backtrader', 'zipline'],
                'risk': ['empyrical', 'ffn'],
                'economic': ['fredapi', 'pandasdmx'],
                'crypto': ['ccxt', 'python-binance'],
                'visualization': ['mplfinance', 'plotly-finance'],
                'alternative': ['stockstats', 'stock-analysis-engine']
            }
            
            repo_names = category_mapping.get(category, [])
            repos_data = []
            
            for repo_name in repo_names:
                repo_data = await self.get_repo_data(repo_name)
                if repo_data:
                    repos_data.append(repo_data)
            
            return repos_data
            
        except Exception as e:
            logger.error(f"Error getting repos by category: {e}")
            return []
    
    async def get_all_repos(self) -> List[Dict[str, Any]]:
        """Get all repositories"""
        try:
            all_repos = []
            
            for repo_name in self.repos:
                repo_data = await self.get_repo_data(repo_name)
                if repo_data:
                    all_repos.append(repo_data)
            
            # Sort by stars
            all_repos.sort(key=lambda x: x.get('stars', 0), reverse=True)
            
            return all_repos
            
        except Exception as e:
            logger.error(f"Error getting all repos: {e}")
            return []
    
    async def get_repo_stats(self) -> Dict[str, Any]:
        """Get statistics for all repositories"""
        try:
            all_repos = await self.get_all_repos()
            
            total_stars = sum(repo.get('stars', 0) for repo in all_repos)
            total_forks = sum(repo.get('forks', 0) for repo in all_repos)
            
            languages = {}
            for repo in all_repos:
                lang = repo.get('language', 'Unknown')
                languages[lang] = languages.get(lang, 0) + 1
            
            licenses = {}
            for repo in all_repos:
                license_type = repo.get('license', 'Unknown')
                licenses[license_type] = licenses.get(license_type, 0) + 1
            
            return {
                'total_repos': len(all_repos),
                'total_stars': total_stars,
                'total_forks': total_forks,
                'languages': languages,
                'licenses': licenses,
                'most_starred': max(all_repos, key=lambda x: x.get('stars', 0)) if all_repos else None,
                'most_forked': max(all_repos, key=lambda x: x.get('forks', 0)) if all_repos else None,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting repo stats: {e}")
            return {}
    
    async def search_repos(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search repositories by query"""
        try:
            # Search through local repos first
            matching_repos = []
            
            for repo_name, repo in self.repos.items():
                if (query.lower() in repo.name.lower() or 
                    query.lower() in repo.description.lower() or
                    any(query.lower() in topic.lower() for topic in repo.topics)):
                    
                    repo_data = await self.get_repo_data(repo_name)
                    if repo_data:
                        matching_repos.append(repo_data)
            
            # Sort by stars
            matching_repos.sort(key=lambda x: x.get('stars', 0), reverse=True)
            
            return matching_repos[:limit]
            
        except Exception as e:
            logger.error(f"Error searching repos: {e}")
            return []
    
    async def get_repo_contributors(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get repository contributors (mock data)"""
        try:
            # Mock contributor data
            contributors = [
                {
                    'username': 'contributor1',
                    'contributions': 100,
                    'type': 'User'
                },
                {
                    'username': 'contributor2',
                    'contributions': 50,
                    'type': 'User'
                },
                {
                    'username': 'contributor3',
                    'contributions': 25,
                    'type': 'User'
                }
            ]
            
            return contributors
            
        except Exception as e:
            logger.error(f"Error getting contributors: {e}")
            return []
    
    async def get_repo_releases(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get repository releases (mock data)"""
        try:
            # Mock release data
            releases = [
                {
                    'tag_name': 'v1.0.0',
                    'name': 'Version 1.0.0',
                    'published_at': '2024-01-01T00:00:00Z',
                    'download_url': f'https://github.com/owner/{repo_name}/archive/v1.0.0.tar.gz'
                },
                {
                    'tag_name': 'v0.9.0',
                    'name': 'Version 0.9.0',
                    'published_at': '2023-12-01T00:00:00Z',
                    'download_url': f'https://github.com/owner/{repo_name}/archive/v0.9.0.tar.gz'
                }
            ]
            
            return releases
            
        except Exception as e:
            logger.error(f"Error getting releases: {e}")
            return []
    
    async def install_repo(self, repo_name: str, install_path: str = './libs') -> bool:
        """Install repository locally (mock implementation)"""
        try:
            # Mock installation
            logger.info(f"Installing {repo_name} to {install_path}")
            
            # In a real implementation, this would:
            # 1. Clone the repository
            # 2. Install dependencies
            # 3. Set up configuration
            
            return True
            
        except Exception as e:
            logger.error(f"Error installing repo: {e}")
            return False
    
    async def update_repo(self, repo_name: str) -> bool:
        """Update repository to latest version (mock implementation)"""
        try:
            # Mock update
            logger.info(f"Updating {repo_name} to latest version")
            
            # In a real implementation, this would:
            # 1. Pull latest changes
            # 2. Update dependencies
            # 3. Restart services if needed
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating repo: {e}")
            return False

# Factory function
def get_github_integrations(config: Dict[str, Any] = None) -> GitHubIntegrations:
    """Factory function to get GitHub integrations"""
    return GitHubIntegrations(config)
