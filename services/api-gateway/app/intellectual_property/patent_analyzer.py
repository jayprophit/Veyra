"""
Patent & IP Analyzer
=====================
Analyze patent portfolios, IP valuations, licensing opportunities
Track R&D pipelines, patent cliffs, generic competition
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class Patent:
    patent_id: str
    title: str
    company: str
    filing_date: date
    grant_date: Optional[date]
    expiration_date: date
    patent_type: str  # 'utility', 'design', 'method'
    technology_area: str
    citations: int
    claim_count: int
    status: str  # 'pending', 'granted', 'expired'


class PatentAnalyzer:
    """Analyze patent portfolios and IP value"""
    
    def analyze_company_portfolio(self, ticker: str, patents: List[Patent]) -> Dict:
        """Analyze company patent portfolio strength"""
        if not patents:
            return {'error': 'No patents provided'}
        
        granted = [p for p in patents if p.status == 'granted']
        pending = [p for p in patents if p.status == 'pending']
        
        # Calculate metrics
        avg_citations = sum(p.citations for p in granted) / len(granted) if granted else 0
        total_claims = sum(p.claim_count for p in granted)
        
        # Patent cliff analysis
        upcoming_expirations = [
            p for p in granted
            if (p.expiration_date - date.today()).days < 365 * 5
        ]
        
        # Technology diversity
        tech_areas = set(p.technology_area for p in patents)
        
        return {
            'ticker': ticker,
            'total_patents': len(patents),
            'granted': len(granted),
            'pending': len(pending),
            'avg_citations': round(avg_citations, 1),
            'total_claims': total_claims,
            'avg_claims_per_patent': round(total_claims / len(granted), 1) if granted else 0,
            'technology_areas': len(tech_areas),
            'upcoming_expirations_5yr': len(upcoming_expirations),
            'patent_cliff_risk': 'HIGH' if len(upcoming_expirations) > len(granted) * 0.3 else 'LOW',
            'portfolio_score': self._calculate_portfolio_score(patents),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_portfolio_score(self, patents: List[Patent]) -> float:
        """Calculate overall portfolio quality score"""
        if not patents:
            return 0
        
        granted = [p for p in patents if p.status == 'granted']
        if not granted:
            return 30  # Pending only
        
        score = 50  # Base
        
        # Citation bonus
        avg_citations = sum(p.citations for p in granted) / len(granted)
        score += min(avg_citations * 2, 20)
        
        # Claim diversity
        avg_claims = sum(p.claim_count for p in granted) / len(granted)
        score += min(avg_claims / 2, 15)
        
        # Technology diversity
        tech_areas = len(set(p.technology_area for p in patents))
        score += min(tech_areas * 3, 15)
        
        return min(score, 100)
    
    def estimate_licensing_value(self, patent: Patent, 
                                 market_size: float,
                                 royalty_rate: float = 0.03) -> Dict:
        """Estimate patent licensing value"""
        years_remaining = (patent.expiration_date - date.today()).days / 365
        
        if years_remaining <= 0:
            return {'value': 0, 'note': 'Patent expired'}
        
        # Annual licensing value
        annual_value = market_size * royalty_rate
        
        # Discounted over remaining life
        discount_rate = 0.10
        pv = annual_value * (1 - (1 + discount_rate) ** -years_remaining) / discount_rate
        
        return {
            'patent_id': patent.patent_id,
            'annual_licensing_potential': round(annual_value, 0),
            'years_remaining': round(years_remaining, 1),
            'present_value': round(pv, 0),
            'royalty_rate': royalty_rate,
            'market_size': market_size
        }
    
    def get_pharma_patent_cliff(self, company: str, 
                                 drug_patents: List[Dict]) -> Dict:
        """Analyze pharmaceutical patent cliff"""
        today = date.today()
        
        expiring_drugs = []
        for drug in drug_patents:
            exp_date = drug.get('expiration_date')
            if not exp_date:
                continue
            
            days_to_expiry = (exp_date - today).days
            
            if days_to_expiry < 365 * 3:  # Expiring in 3 years
                expiring_drugs.append({
                    'drug_name': drug['name'],
                    'revenue': drug.get('annual_revenue', 0),
                    'expiration_date': exp_date.isoformat(),
                    'days_remaining': days_to_expiry,
                    'percent_of_revenue': drug.get('percent_revenue', 0)
                })
        
        total_at_risk = sum(d['revenue'] for d in expiring_drugs)
        
        return {
            'company': company,
            'drugs_expiring_3yr': len(expiring_drugs),
            'total_revenue_at_risk': round(total_at_risk, 0),
            'percent_revenue_at_risk': round(
                sum(d['percent_of_revenue'] for d in expiring_drugs), 1
            ),
            'at_risk_drugs': sorted(expiring_drugs, 
                                   key=lambda x: x['days_remaining']),
            'cliff_severity': 'SEVERE' if total_at_risk > 1e9 else 
                            'MODERATE' if total_at_risk > 500e6 else 'LOW',
            'timestamp': datetime.now().isoformat()
        }


# Usage
def analyze_patent_portfolio(ticker: str, patents: List[Dict]) -> Dict:
    """Quick patent portfolio analysis"""
    analyzer = PatentAnalyzer()
    
    patent_objects = [
        Patent(
            patent_id=p['id'],
            title=p.get('title', ''),
            company=ticker,
            filing_date=p['filing_date'],
            grant_date=p.get('grant_date'),
            expiration_date=p['expiration_date'],
            patent_type=p.get('type', 'utility'),
            technology_area=p.get('tech_area', 'general'),
            citations=p.get('citations', 0),
            claim_count=p.get('claims', 0),
            status=p.get('status', 'granted')
        )
        for p in patents
    ]
    
    return analyzer.analyze_company_portfolio(ticker, patent_objects)
