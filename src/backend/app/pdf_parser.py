"""PDF Statement Parser - Extract data from broker statements."""

import re
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger('PDFParser')

class StatementParser:
    """Parse PDF statements from various brokers."""
    
    def __init__(self):
        self.patterns = {
            'trading212': {
                'txn': r'(Market buy|Market sell|Dividend).*?(\w{3,5}).*?([\d,]+\.?\d*).*?([\d\.]+)',
                'date': r'(\d{2}/\d{2}/\d{4})'
            },
            'freetrade': {
                'txn': r'(BUY|SELL)\s+(\w+)\s+([\d\.]+)\s+@\s+([\d\.]+)',
                'date': r'(\d{2}\s+\w+\s+\d{4})'
            },
            'hl': {
                'txn': r'(Purchase|Sale)\s+.*?(\w+).*?(\d+)\s+shares\s+@\s+([\d\.]+)p?',
                'date': r'(\d{2}-\w+-\d{4})'
            }
        }
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF."""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.error("pip install pdfplumber")
            return ""
    
    def parse_trading212(self, text: str) -> List[Dict]:
        """Parse Trading 212 statement."""
        txns = []
        lines = text.split('\n')
        
        for line in lines:
            # Match transaction lines
            if 'Market buy' in line or 'Market sell' in line:
                parts = line.split()
                try:
                    # Extract ticker (usually in ALL CAPS)
                    ticker = [p for p in parts if p.isupper() and len(p) <= 5][0]
                    # Extract numbers
                    nums = [float(p.replace(',', '')) for p in parts if re.match(r'[\d,]+\.?\d*', p)]
                    
                    if len(nums) >= 2:
                        txns.append({
                            'type': 'BUY' if 'buy' in line.lower() else 'SELL',
                            'ticker': ticker,
                            'shares': nums[0],
                            'price': nums[1],
                            'source': 'trading212_pdf'
                        })
                except:
                    continue
        
        return txns
    
    def parse_generic(self, text: str, broker: str = 'unknown') -> List[Dict]:
        """Generic PDF parsing."""
        txns = []
        
        # Try Trading 212 format first
        if 'trading 212' in text.lower() or 't212' in text.lower():
            return self.parse_trading212(text)
        
        # Generic pattern matching
        lines = text.split('\n')
        for line in lines:
            # Look for ticker symbols (ALL CAPS, 2-5 chars)
            tickers = re.findall(r'\b[A-Z]{2,5}\\\b', line)
            # Look for numbers
            numbers = re.findall(r'\d+\.?\d*', line)
            
            if tickers and len(numbers) >= 2:
                txns.append({
                    'ticker': tickers[0],
                    'raw_data': line,
                    'source': broker
                })
        
        return txns
    
    def parse_file(self, pdf_path: str, broker: str = None) -> List[Dict]:
        """Parse PDF file and return transactions."""
        text = self.extract_text(pdf_path)
        if not text:
            return []
        
        # Auto-detect broker
        if not broker:
            text_lower = text.lower()
            if 'trading 212' in text_lower:
                broker = 'trading212'
            elif 'freetrade' in text_lower:
                broker = 'freetrade'
            elif 'hargreaves lansdown' in text_lower or 'h-l' in text_lower:
                broker = 'hl'
            else:
                broker = 'unknown'
        
        logger.info(f"Parsing {pdf_path} as {broker}")
        return self.parse_generic(text, broker)

class AutoPDFImporter:
    """Automatically process PDFs from downloads folder."""
    
    def __init__(self, watch_folder: str = None):
        if not watch_folder:
            import os
            watch_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.watch_folder = watch_folder
        self.parser = StatementParser()
    
    def scan_and_import(self) -> List[Dict]:
        """Scan folder and import all PDF statements."""
        import os
        
        all_txns = []
        for filename in os.listdir(self.watch_folder):
            if filename.endswith('.pdf') and any(x in filename.lower() for x in ['statement', 'export', 'trade']):
                filepath = os.path.join(self.watch_folder, filename)
                txns = self.parser.parse_file(filepath)
                all_txns.extend(txns)
                logger.info(f"Imported {len(txns)} from {filename}")
        
        return all_txns

if __name__ == "__main__":
    print("PDF Parser ready")
    print("Usage: from pdf_parser import StatementParser; p = StatementParser(); txns = p.parse_file('statement.pdf')")
