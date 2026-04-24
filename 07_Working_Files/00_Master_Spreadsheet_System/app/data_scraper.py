"""Data Scraper - Import from Trading 212, Yahoo Finance, CSV."""

import csv
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger('DataScraper')

class Trading212Importer:
    def parse(self, filepath: str):
        txns = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                txns.append({
                    'ticker': row.get('Ticker'),
                    'type': 'BUY' if 'buy' in row.get('Action','').lower() else 'SELL',
                    'shares': float(row.get('No. of shares', 0)),
                    'price': float(row.get('Price / share', 0)),
                    'amount': abs(float(row.get('Total (GBP)', 0))),
                    'date': row.get('Time'),
                    'account': 'GIA'
                })
        return txns

class YahooFinanceScraper:
    def get_info(self, ticker: str):
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                'ticker': ticker,
                'name': info.get('longName'),
                'price': info.get('currentPrice'),
                'sector': info.get('sector'),
                'currency': info.get('currency', 'USD')
            }
        except Exception as e:
            logger.error(f"Failed: {e}")
            return {}

class CSVImporter:
    def import_file(self, filepath: str):
        if 'trading212' in filepath.lower():
            return Trading212Importer().parse(filepath)
        df = pd.read_csv(filepath)
        return df.to_dict('records')

if __name__ == "__main__":
    print("Usage: from data_scraper import Trading212Importer, YahooFinanceScraper")
