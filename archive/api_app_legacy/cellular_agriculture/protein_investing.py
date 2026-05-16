"""Protein Investing - Alternative protein investment"""
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class ProteinType(Enum):
    PLANT_BASED = "plant_based"
    CULTIVATED_MEAT = "cultivated_meat"
    FERMENTATION = "precision_fermentation"

@dataclass
class ProteinCompany:
    company_id: str
    name: str
    protein_type: ProteinType
    funding_millions: float
    valuation_millions: float
    revenue_millions: float

class AlternativeProteinInvesting:
    def __init__(self):
        self.companies: List[ProteinCompany] = []
    
    def add(self, c: ProteinCompany):
        self.companies.append(c)
    
    def get_summary(self) -> Dict:
        if not self.companies:
            return {'status': 'NO_COMPANIES'}
        return {
            'companies': len(self.companies),
            'total_funding': round(sum(c.funding_millions for c in self.companies), 1),
            'total_valuation': round(sum(c.valuation_millions for c in self.companies), 1)
        }
