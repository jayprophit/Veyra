"""
Holding Company Tracker
========================
Track holding company structures, subsidiaries, NAV discounts
Conglomerate analysis, sum-of-parts valuation
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Subsidiary:
    name: str
    ticker: Optional[str]
    ownership_pct: float
    market_cap: Optional[float]
    enterprise_value: float
    revenue: float
    ebitda: float
    sector: str
    public: bool


class HoldingCompanyTracker:
    """Analyze holding companies and conglomerates"""
    
    # Famous holding companies
    HOLDING_COMPANIES = {
        'BRK.B': {
            'name': 'Berkshire Hathaway',
            'primary_holdings': [
                {'name': 'Apple', 'ticker': 'AAPL', 'value_b': 174},
                {'name': 'Bank of America', 'ticker': 'BAC', 'value_b': 39},
                {'name': 'Chevron', 'ticker': 'CVX', 'value_b': 27},
                {'name': 'Coca-Cola', 'ticker': 'KO', 'value_b': 24},
                {'name': 'American Express', 'ticker': 'AXP', 'value_b': 35},
            ],
            'wholly_owned': ['BNSF Railway', 'Berkshire Hathaway Energy', 'GEICO', 'Duracell']
        },
        'IEP': {
            'name': 'Icahn Enterprises',
            'primary_holdings': [
                {'name': 'CVR Energy', 'ticker': 'CVI', 'ownership': 71},
                {'name': 'Vivus', 'ticker': 'VVUS', 'ownership': 0},
            ],
            'sectors': ['Energy', 'Automotive', 'Food Packaging', 'Real Estate']
        }
    }
    
    def calculate_nav_discount(self, holding_ticker: str,
                               subsidiaries: List[Subsidiary],
                               holding_market_cap: float) -> Dict:
        """
        Calculate NAV discount/premium for holding company
        
        NAV Discount = (Holding Market Cap - Sum of Parts) / Sum of Parts
        """
        # Calculate sum of parts
        public_subs = [s for s in subsidiaries if s.public]
        private_subs = [s for s in subsidiaries if not s.public]
        
        # Public subsidiaries at market value
        public_value = sum(
            (s.market_cap or 0) * (s.ownership_pct / 100)
            for s in public_subs
        )
        
        # Private subsidiaries at estimated value (EV multiples)
        private_value = sum(
            s.enterprise_value * (s.ownership_pct / 100)
            for s in private_subs
        )
        
        sum_of_parts = public_value + private_value
        
        # Calculate discount
        discount = (sum_of_parts - holding_market_cap) / sum_of_parts if sum_of_parts > 0 else 0
        
        return {
            'holding_ticker': holding_ticker,
            'holding_market_cap': round(holding_market_cap, 0),
            'sum_of_parts': round(sum_of_parts, 0),
            'nav_discount_pct': round(discount * 100, 1),
            'public_subs_value': round(public_value, 0),
            'private_subs_value': round(private_value, 0),
            'interpretation': 'DEEP_DISCOUNT' if discount > 0.30 else
                            'DISCOUNT' if discount > 0.15 else
                            'PREMIUM' if discount < -0.10 else 'FAIR_VALUE',
            'opportunity': discount > 0.25
        }
    
    def analyze_conglomerate_discount(self, ticker: str,
                                      subsidiaries: List[Subsidiary]) -> Dict:
        """Analyze conglomerate complexity discount"""
        sectors = len(set(s.sector for s in subsidiaries))
        
        # Complexity penalty increases with sector count
        complexity_penalty = 0.05 + (sectors - 1) * 0.03
        
        return {
            'ticker': ticker,
            'subsidiary_count': len(subsidiaries),
            'sector_count': sectors,
            'complexity_penalty': round(complexity_penalty, 2),
            'conglomerate_discount_pct': round(complexity_penalty * 100, 1),
            'recommendation': 'BREAKUP_CANDIDATE' if sectors > 4 and complexity_penalty > 0.15 else 'HOLD',
            'diversification_benefit': sectors > 2
        }
    
    def get_holding_company_summary(self, ticker: str) -> Dict:
        """Get summary of major holding company"""
        if ticker not in self.HOLDING_COMPANIES:
            return {'error': f'No data for {ticker}'}
        
        data = self.HOLDING_COMPANIES[ticker]
        
        return {
            'ticker': ticker,
            'name': data['name'],
            'holdings_count': len(data.get('primary_holdings', [])),
            'wholly_owned_count': len(data.get('wholly_owned', [])),
            'largest_holdings': data.get('primary_holdings', [])[:5],
            'strategy': self._infer_strategy(ticker),
            'timestamp': datetime.now().isoformat()
        }
    
    def _infer_strategy(self, ticker: str) -> str:
        """Infer holding company strategy"""
        strategies = {
            'BRK.B': 'Value investing, permanent capital, insurance float',
            'IEP': 'Activist investing, breakup value, special situations',
            'MKL': 'Insurance + diversified industrials, decentralized management'
        }
        return strategies.get(ticker, 'Diversified holding strategy')


# Usage
def calculate_nav_opportunity(ticker: str, market_cap: float,
                               subsidiaries: List[Dict]) -> Dict:
    """Quick NAV discount calculation"""
    tracker = HoldingCompanyTracker()
    
    subs = [
        Subsidiary(
            name=s['name'],
            ticker=s.get('ticker'),
            ownership_pct=s.get('ownership', 100),
            market_cap=s.get('market_cap'),
            enterprise_value=s.get('ev', 0),
            revenue=s.get('revenue', 0),
            ebitda=s.get('ebitda', 0),
            sector=s.get('sector', 'Unknown'),
            public=s.get('public', False)
        )
        for s in subsidiaries
    ]
    
    return tracker.calculate_nav_discount(ticker, subs, market_cap)


def analyze_conglomerate(ticker: str, subs: List[Dict]) -> Dict:
    """Analyze conglomerate structure"""
    tracker = HoldingCompanyTracker()
    
    subsidiaries = [
        Subsidiary(
            name=s['name'],
            ticker=s.get('ticker'),
            ownership_pct=s.get('ownership', 100),
            market_cap=s.get('market_cap'),
            enterprise_value=s.get('ev', 0),
            revenue=s.get('revenue', 0),
            ebitda=s.get('ebitda', 0),
            sector=s.get('sector', 'Unknown'),
            public=s.get('public', False)
        )
        for s in subs
    ]
    
    return tracker.analyze_conglomerate_discount(ticker, subsidiaries)
