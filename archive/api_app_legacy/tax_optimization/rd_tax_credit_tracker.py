"""
R&D Tax Credit Tracker
======================
Track R&D tax credits, qualified research expenses
Maximize tax benefits from innovation spending
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class RDExpense:
    category: str  # 'wages', 'supplies', 'contractors', 'cloud'
    amount: float
    project: str
    date: date
    qualified: bool


class RDTaxCreditTracker:
    """
    Track R&D tax credits for companies
    
    US R&D Tax Credit = 20% of qualified research expenses above base amount
    Can offset up to $250k against payroll taxes for startups
    """
    
    # Qualified expense categories
    QUALIFIED_CATEGORIES = [
        'wages', 'supplies', 'contractors', 'cloud_computing',
        'prototyping', 'testing', 'software_dev', 'process_improvement'
    ]
    
    def calculate_credit(self, expenses: List[RDExpense],
                        company_type: str = 'established') -> Dict:
        """Calculate R&D tax credit"""
        
        # Filter qualified expenses
        qualified = [e for e in expenses if e.qualified]
        total_qualified = sum(e.amount for e in qualified)
        
        # Calculate by category
        by_category = {}
        for e in qualified:
            if e.category not in by_category:
                by_category[e.category] = 0
            by_category[e.category] += e.amount
        
        # Credit calculation (simplified - 20% of qualified)
        # Real calculation uses complex base period formula
        credit_rate = 0.20
        estimated_credit = total_qualified * credit_rate
        
        # Startup provision (up to $250k against payroll taxes)
        payroll_offset_limit = 250000 if company_type == 'startup' else 0
        
        return {
            'total_expenses': round(sum(e.amount for e in expenses), 2),
            'qualified_expenses': round(total_qualified, 2),
            'qualification_rate': round(len(qualified) / len(expenses) * 100, 1) if expenses else 0,
            'estimated_credit': round(estimated_credit, 2),
            'by_category': {k: round(v, 2) for k, v in by_category.items()},
            'payroll_offset_available': company_type == 'startup',
            'payroll_offset_limit': payroll_offset_limit,
            'recommendations': self._generate_recommendations(qualified, expenses)
        }
    
    def _generate_recommendations(self, qualified: List[RDExpense],
                                   all_expenses: List[RDExpense]) -> List[str]:
        """Generate optimization recommendations"""
        recs = []
        
        # Check for unqualified expenses that could be qualified
        unqualified = [e for e in all_expenses if not e.qualified]
        
        if unqualified:
            recs.append(f"Review {len(unqualified)} expenses for qualification - potential missed opportunity")
        
        # Check documentation
        missing_project = [e for e in qualified if not e.project]
        if missing_project:
            recs.append(f"{len(missing_project)} expenses missing project linkage - document for audit defense")
        
        # Cloud computing
        cloud_qualified = sum(e.amount for e in qualified if 'cloud' in e.category)
        if cloud_qualified < 10000:
            recs.append("Consider tracking cloud computing costs for R&D - often overlooked")
        
        return recs
    
    def project_annual_benefit(self, monthly_rd_spend: float,
                               growth_rate: float = 0.10,
                               years: int = 5) -> Dict:
        """Project multi-year R&D tax credit benefit"""
        
        projections = []
        cumulative = 0
        
        for year in range(1, years + 1):
            annual_spend = monthly_rd_spend * 12 * ((1 + growth_rate) ** (year - 1))
            credit = annual_spend * 0.20  # Simplified 20%
            cumulative += credit
            
            projections.append({
                'year': year,
                'rd_spend': round(annual_spend, 0),
                'tax_credit': round(credit, 0),
                'cumulative_credit': round(cumulative, 0)
            })
        
        return {
            'projections': projections,
            'total_5yr_credit': round(sum(p['tax_credit'] for p in projections), 0),
            'avg_annual_credit': round(sum(p['tax_credit'] for p in projections) / years, 0),
            'assumptions': {
                'starting_monthly_spend': monthly_rd_spend,
                'annual_growth_rate': growth_rate,
                'credit_rate': 0.20
            }
        }


# Usage
def calculate_rd_credit(expenses: List[Dict], company_type: str = 'established') -> Dict:
    """Quick R&D credit calculation"""
    tracker = RDTaxCreditTracker()
    
    rd_expenses = [
        RDExpense(
            category=e['category'],
            amount=e['amount'],
            project=e.get('project', ''),
            date=e.get('date', date.today()),
            qualified=e.get('qualified', True)
        )
        for e in expenses
    ]
    
    return tracker.calculate_credit(rd_expenses, company_type)


def project_rd_benefit(monthly_spend: float, growth: float = 0.10) -> Dict:
    """Project future R&D benefits"""
    tracker = RDTaxCreditTracker()
    return tracker.project_annual_benefit(monthly_spend, growth)
