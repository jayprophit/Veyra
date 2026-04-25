"""UK Business Structure Tracker"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Structure(Enum):
    HOBBY = "hobby"
    SOLE_TRADER = "sole_trader"
    LIMITED = "limited"
    VAT = "vat_registered"
    HOLDING = "holding"

@dataclass
class Milestone:
    phase: int
    name: str
    threshold: str
    action: str
    done: bool = False

class BusinessTracker:
    """Tracks business progression"""
    
    THRESHOLDS = {
        "trading_allowance": 1000,
        "ltd_optimal": 50000,
        "vat": 90000,
        "fic": 2000000
    }
    
    def __init__(self):
        self.milestones = [
            Milestone(1, "Hobby", "< £1,000", "No action"),
            Milestone(2, "Sole Trader", "> £1,000", "Self Assessment by Oct 5"),
            Milestone(3, "Limited", "> £50,000", "Incorporate Ltd"),
            Milestone(4, "VAT", "> £90,000 turnover", "VAT registration"),
            Milestone(5, "FIC", "> £2M", "Family Investment Co")
        ]
    
    def check_progress(self, income: float, profit: float, turnover: float) -> List[Milestone]:
        """Check triggered milestones"""
        triggered = []
        if income > 1000:
            triggered.append(self.milestones[1])
        if profit > 50000:
            triggered.append(self.milestones[2])
        if turnover > 90000:
            triggered.append(self.milestones[3])
        return triggered
    
    def tax_analysis(self, profit: float) -> Dict:
        """Compare sole trader vs Ltd tax"""
        sole_tax = profit * 0.29  # 20% + 9% NI
        corp_tax = profit * 0.19  # 19% corporation
        div_tax = (profit * 0.81) * 0.0875  # Dividend tax
        total_ltd = corp_tax + div_tax
        
        return {
            "sole_trader_tax": sole_tax,
            "limited_tax": total_ltd,
            "savings": sole_tax - total_ltd,
            "optimal": "Ltd" if profit > 50000 else "Sole Trader"
        }
