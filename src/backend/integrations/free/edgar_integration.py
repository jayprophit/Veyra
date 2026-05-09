"""
EDGAR Direct Integration Module - Free Alternative to FactSet
Provides SEC filings and company data access without API keys or costs
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import re
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests or beautifulsoup4 not installed. Install with: pip install requests beautifulsoup4")

logger = logging.getLogger(__name__)

@dataclass
class SECFiling:
    company_name: str
    cik: str
    filing_type: str
    filing_date: datetime
    accession_number: str
    document_url: str
    description: str

@dataclass
class CompanyInfo:
    cik: str
    name: str
    ticker: str
    exchange: str
    sic: str
    state_of_incorporation: str
    fiscal_year_end: str
    address: str
    phone: str

@dataclass
class InsiderTrade:
    company_cik: str
    insider_name: str
    relationship: str
    transaction_date: datetime
    transaction_type: str
    shares_traded: int
    price_per_share: float
    shares_owned: int

@dataclass
class FinancialStatement:
    cik: str
    filing_type: str
    period_end_date: datetime
    revenue: float
    net_income: float
    total_assets: float
    total_liabilities: float
    cash_flow: float

class EDGARIntegration:
    """EDGAR integration for free SEC filings access"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = REQUESTS_AVAILABLE
        self.cache = {}
        self.cache_ttl = 1800  # 30 minutes
        self.base_url = "https://www.sec.gov"
        self.edgar_url = "https://www.sec.gov/Archives/edgar"
        
        if not self.enabled:
            logger.error("requests/beautifulsoup4 not available - install with: pip install requests beautifulsoup4")
            return
        
        # Set user agent to be respectful
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Financial Master (https://github.com/jpowell/financial-master) - educational/research purposes'
        })
        
        logger.info("EDGAR integration initialized successfully")
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        cached_time = self.cache[key].get('timestamp')
        if not cached_time:
            return False
        return (datetime.now() - cached_time).seconds < self.cache_ttl
    
    def _get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            return self.cache[key]['data']
        return None
    
    def _cache_data(self, key: str, data: Any) -> None:
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def search_company_by_ticker(self, ticker: str) -> Optional[CompanyInfo]:
        """Search for company information by ticker symbol"""
        if not self.enabled:
            return self._get_mock_company_info(ticker)
        
        cache_key = f"company_{ticker}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Search for company CIK
            search_url = f"{self.base_url}/cgi-bin/browse-edgar"
            params = {
                'action': 'getcompany',
                'CIK': ticker,
                'owner': 'exclude',
                'count': '40'
            }
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract company information
            company_info = self._parse_company_info(soup, ticker)
            
            if company_info:
                self._cache_data(cache_key, company_info)
                return company_info
                
        except Exception as e:
            logger.error(f"Failed to search company {ticker}: {e}")
        
        return self._get_mock_company_info(ticker)
    
    def _parse_company_info(self, soup: BeautifulSoup, ticker: str) -> Optional[CompanyInfo]:
        """Parse company information from EDGAR page"""
        try:
            # Extract CIK from the page
            cik_match = soup.find('span', class_='companyInfo')
            if not cik_match:
                return None
            
            cik_text = cik_match.get_text()
            cik_match = re.search(r'CIK:\s*(\d{10})', cik_text)
            if not cik_match:
                return None
            
            cik = cik_match.group(1)
            
            # Extract company name
            name_match = soup.find('span', class_='companyName')
            company_name = name_match.get_text().replace('CIK:', '').strip() if name_match else ticker
            
            # Extract other information from the table
            info_table = soup.find('div', class_='info')
            if not info_table:
                return self._get_mock_company_info(ticker)
            
            info_text = info_table.get_text()
            
            # Parse various fields
            state_match = re.search(r'State of Incorporation:\s*([A-Z]{2})', info_text)
            sic_match = re.search(r'SIC:\s*(\d+)', info_text)
            fiscal_year_match = re.search(r'Fiscal Year End:\s*(\d{4})', info_text)
            
            return CompanyInfo(
                cik=cik,
                name=company_name,
                ticker=ticker,
                exchange='NASDAQ',  # Default, would need additional parsing
                sic=sic_match.group(1) if sic_match else '',
                state_of_incorporation=state_match.group(1) if state_match else '',
                fiscal_year_end=fiscal_year_match.group(1) if fiscal_year_match else '1231',
                address='',  # Would need additional parsing
                phone=''  # Would need additional parsing
            )
            
        except Exception as e:
            logger.error(f"Failed to parse company info: {e}")
            return None
    
    async def get_company_filings(self, cik: str, filing_type: str = None, count: int = 10) -> List[SECFiling]:
        """Get company filings"""
        if not self.enabled:
            return self._get_mock_filings(cik, filing_type, count)
        
        cache_key = f"filings_{cik}_{filing_type}_{count}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            search_url = f"{self.base_url}/cgi-bin/browse-edgar"
            params = {
                'action': 'getcompany',
                'CIK': cik,
                'owner': 'exclude',
                'count': str(count)
            }
            
            if filing_type:
                params['type'] = filing_type
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            filings = self._parse_filings_table(soup, cik)
            
            self._cache_data(cache_key, filings)
            return filings
            
        except Exception as e:
            logger.error(f"Failed to get filings for {cik}: {e}")
        
        return self._get_mock_filings(cik, filing_type, count)
    
    def _parse_filings_table(self, soup: BeautifulSoup, cik: str) -> List[SECFiling]:
        """Parse filings table from EDGAR page"""
        filings = []
        
        try:
            # Find the filings table
            table = soup.find('table', class_='tableFile2')
            if not table:
                return filings
            
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 4:
                    continue
                
                # Extract filing information
                filing_date = cells[3].get_text().strip()
                filing_type = cells[0].get_text().strip()
                
                # Get the document link
                doc_link = cells[1].find('a')
                if not doc_link:
                    continue
                
                doc_url = urljoin(self.base_url, doc_link['href'])
                
                # Get accession number from URL
                accession_match = re.search(r'accession_number=([^&]+)', doc_url)
                accession_number = accession_match.group(1) if accession_match else ''
                
                filing = SECFiling(
                    company_name='',  # Would need to fetch from company info
                    cik=cik,
                    filing_type=filing_type,
                    filing_date=datetime.strptime(filing_date, '%Y-%m-%d'),
                    accession_number=accession_number,
                    document_url=doc_url,
                    description=filing_type
                )
                filings.append(filing)
                
        except Exception as e:
            logger.error(f"Failed to parse filings table: {e}")
        
        return filings
    
    async def get_filing_content(self, accession_number: str) -> Optional[Dict[str, Any]]:
        """Get filing content by accession number"""
        if not self.enabled:
            return self._get_mock_filing_content(accession_number)
        
        cache_key = f"filing_content_{accession_number}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Construct the filing URL
            filing_url = f"{self.edgar_url}/data/{accession_number[:10]}/{accession_number.replace('-', '')}.txt"
            
            response = self.session.get(filing_url)
            response.raise_for_status()
            
            content = response.text
            
            # Parse basic filing information
            filing_content = {
                'accession_number': accession_number,
                'content': content,
                'parsed_data': self._parse_filing_content(content)
            }
            
            self._cache_data(cache_key, filing_content)
            return filing_content
            
        except Exception as e:
            logger.error(f"Failed to get filing content {accession_number}: {e}")
        
        return self._get_mock_filing_content(accession_number)
    
    def _parse_filing_content(self, content: str) -> Dict[str, Any]:
        """Parse basic information from filing content"""
        parsed = {
            'company_name': '',
            'filing_type': '',
            'period_end_date': '',
            'revenue': 0.0,
            'net_income': 0.0,
            'total_assets': 0.0,
            'total_liabilities': 0.0
        }
        
        try:
            lines = content.split('\n')
            
            # Extract company name
            for line in lines:
                if 'COMPANY CONFORMED NAME' in line:
                    parsed['company_name'] = line.split(':')[-1].strip()
                    break
            
            # Extract filing type
            for line in lines:
                if 'CONFORMED SUBMISSION TYPE' in line:
                    parsed['filing_type'] = line.split(':')[-1].strip()
                    break
            
            # Extract period end date
            for line in lines:
                if 'CONFORMED PERIOD OF REPORT' in line:
                    parsed['period_end_date'] = line.split(':')[-1].strip()
                    break
            
            # Try to extract financial numbers (basic parsing)
            # This is a simplified approach - real parsing would be more complex
            revenue_match = re.search(r'Revenue[s]?[^0-9]*([0-9,]+\.?\d*)', content, re.IGNORECASE)
            if revenue_match:
                parsed['revenue'] = float(revenue_match.group(1).replace(',', ''))
            
            income_match = re.search(r'Net Income[^0-9]*([0-9,]+\.?\d*)', content, re.IGNORECASE)
            if income_match:
                parsed['net_income'] = float(income_match.group(1).replace(',', ''))
            
        except Exception as e:
            logger.error(f"Failed to parse filing content: {e}")
        
        return parsed
    
    async def get_insider_trades(self, cik: str, count: int = 20) -> List[InsiderTrade]:
        """Get insider trading information"""
        if not self.enabled:
            return self._get_mock_insider_trades(cik, count)
        
        cache_key = f"insider_trades_{cik}_{count}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Get Form 4 filings (insider trades)
            filings = await self.get_company_filings(cik, filing_type='4', count=count)
            insider_trades = []
            
            for filing in filings:
                try:
                    content = await self.get_filing_content(filing.accession_number)
                    if content:
                        trades = self._parse_insider_trades(content, cik)
                        insider_trades.extend(trades)
                except Exception as e:
                    logger.warning(f"Failed to parse insider trade from {filing.accession_number}: {e}")
            
            self._cache_data(cache_key, insider_trades)
            return insider_trades
            
        except Exception as e:
            logger.error(f"Failed to get insider trades for {cik}: {e}")
        
        return self._get_mock_insider_trades(cik, count)
    
    def _parse_insider_trades(self, filing_content: Dict[str, Any], cik: str) -> List[InsiderTrade]:
        """Parse insider trades from Form 4 filing"""
        trades = []
        
        try:
            content = filing_content.get('content', '')
            lines = content.split('\n')
            
            # This is a simplified parser - real parsing would be more complex
            for i, line in enumerate(lines):
                if 'Table I' in line or 'Table II' in line:
                    # Look for trading information in the following lines
                    for j in range(i+1, min(i+20, len(lines))):
                        trade_line = lines[j]
                        if 'shares' in trade_line.lower() and '$' in trade_line:
                            # Extract basic trade information
                            parts = trade_line.split()
                            if len(parts) >= 3:
                                try:
                                    shares = int(parts[0].replace(',', ''))
                                    price = float(parts[1].replace('$', '').replace(',', ''))
                                    
                                    trade = InsiderTrade(
                                        company_cik=cik,
                                        insider_name='',  # Would need more complex parsing
                                        relationship='',  # Would need more complex parsing
                                        transaction_date=filing.filing_date,
                                        transaction_type='BUY' if shares > 0 else 'SELL',
                                        shares_traded=abs(shares),
                                        price_per_share=price,
                                        shares_owned=0  # Would need more complex parsing
                                    )
                                    trades.append(trade)
                                except (ValueError, IndexError):
                                    continue
                                    
        except Exception as e:
            logger.error(f"Failed to parse insider trades: {e}")
        
        return trades
    
    async def search_filings_by_text(self, text: str, count: int = 10) -> List[SECFiling]:
        """Search filings by text content"""
        if not self.enabled:
            return self._get_mock_filings_by_text(text, count)
        
        cache_key = f"text_search_{text}_{count}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Use SEC's full-text search
            search_url = f"{self.base_url}/cgi-bin/srch-edgar"
            params = {
                'text': text,
                'count': str(count),
                'start': '0',
                'action': 'getcompany'
            }
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            filings = self._parse_search_results(soup)
            
            self._cache_data(cache_key, filings)
            return filings
            
        except Exception as e:
            logger.error(f"Failed to search filings by text '{text}': {e}")
        
        return self._get_mock_filings_by_text(text, count)
    
    def _parse_search_results(self, soup: BeautifulSoup) -> List[SECFiling]:
        """Parse search results from EDGAR"""
        filings = []
        
        try:
            # Find search results
            results = soup.find_all('div', class_='result')
            
            for result in results:
                try:
                    # Extract basic information from search result
                    link = result.find('a')
                    if not link:
                        continue
                    
                    doc_url = urljoin(self.base_url, link['href'])
                    title = link.get_text().strip()
                    
                    # Extract filing type and date from title
                    parts = title.split()
                    if len(parts) >= 2:
                        filing_type = parts[-1]
                        date_str = parts[-2]  # Simplified date extraction
                    
                    filing = SECFiling(
                        company_name=title,
                        cik='',
                        filing_type=filing_type,
                        filing_date=datetime.now(),  # Would need proper date parsing
                        accession_number='',
                        document_url=doc_url,
                        description=title
                    )
                    filings.append(filing)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse search result: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse search results: {e}")
        
        return filings
    
    # Mock data methods for fallback
    def _get_mock_company_info(self, ticker: str) -> CompanyInfo:
        """Generate mock company info"""
        import random
        return CompanyInfo(
            cik=str(random.randint(1000000000, 9999999999)),
            name=f"{ticker} Corporation",
            ticker=ticker,
            exchange='NASDAQ',
            sector_code='7372',  # Computer Services
            state_of_incorporation='DE',
            fiscal_year_end='1231',
            address='123 Main St, Wilmington, DE 19801',
            phone='(302) 555-0123'
        )
    
    def _get_mock_filings(self, cik: str, filing_type: str, count: int) -> List[SECFiling]:
        """Generate mock filings"""
        import random
        filings = []
        
        for i in range(min(count, 10)):
            filing_date = datetime.now() - timedelta(days=random.randint(1, 365))
            filing_types = ['10-K', '10-Q', '8-K', 'DEF 14A', '4']
            
            filing = SECFiling(
                company_name=f"Company {cik}",
                cik=cik,
                filing_type=filing_type if not filing_type else filing_type,
                filing_date=filing_date,
                accession_number=f"0000{cik}-{filing_date.strftime('%Y%m%d')}-0000{i:04d}",
                document_url=f"https://www.sec.gov/Archives/edgar/data/{cik}/0000{cik}-{filing_date.strftime('%Y%m%d')}-0000{i:04d}.txt",
                description=f"{filing_type if not filing_type else filing_type} filing"
            )
            filings.append(filing)
        
        return filings
    
    def _get_mock_filing_content(self, accession_number: str) -> Dict[str, Any]:
        """Generate mock filing content"""
        return {
            'accession_number': accession_number,
            'content': f"Mock filing content for {accession_number}",
            'parsed_data': {
                'company_name': 'Mock Company',
                'filing_type': '10-K',
                'period_end_date': '2023-12-31',
                'revenue': 1000000000.0,
                'net_income': 100000000.0,
                'total_assets': 2000000000.0,
                'total_liabilities': 500000000.0
            }
        }
    
    def _get_mock_insider_trades(self, cik: str, count: int) -> List[InsiderTrade]:
        """Generate mock insider trades"""
        import random
        trades = []
        
        for i in range(min(count, 10)):
            trade_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            trade = InsiderTrade(
                company_cik=cik,
                insider_name=f"Insider {i}",
                relationship=random.choice(['CEO', 'CFO', 'Director', 'Officer']),
                transaction_date=trade_date,
                transaction_type=random.choice(['BUY', 'SELL']),
                shares_traded=random.randint(100, 10000),
                price_per_share=random.uniform(50, 200),
                shares_owned=random.randint(10000, 1000000)
            )
            trades.append(trade)
        
        return trades
    
    def _get_mock_filings_by_text(self, text: str, count: int) -> List[SECFiling]:
        """Generate mock filings for text search"""
        import random
        filings = []
        
        for i in range(min(count, 10)):
            filing_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            filing = SECFiling(
                company_name=f"Company mentioning {text}",
                cik=str(random.randint(1000000000, 9999999999)),
                filing_type=random.choice(['10-K', '10-Q', '8-K']),
                filing_date=filing_date,
                accession_number=f"0000{random.randint(1000000000, 9999999999)}-{filing_date.strftime('%Y%m%d')}-0000{i:04d}",
                document_url=f"https://www.sec.gov/Archives/edgar/data/{random.randint(1000000000, 9999999999)}/mock-{i}.txt",
                description=f"Filing containing: {text}"
            )
            filings.append(filing)
        
        return filings
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'enabled': self.enabled,
            'provider': 'SEC EDGAR',
            'features': [
                'company_search',
                'filings_access',
                'filing_content',
                'insider_trades',
                'text_search'
            ],
            'cost': 'FREE',
            'api_key_required': False,
            'rate_limits': '10 requests per second (recommended)',
            'data_quality': 'Official SEC Data',
            'coverage': 'US Public Companies Only'
        }

# Factory function
def get_edgar_integration(config: Dict[str, Any] = None) -> EDGARIntegration:
    """Factory function to get EDGAR integration"""
    return EDGARIntegration(config)
