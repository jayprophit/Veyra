"""FDA Monitor - Track FDA approvals, trials, and drug pipeline"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TrialPhase(Enum):
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    FDA_REVIEW = "fda_review"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class DrugTrial:
    company: str
    ticker: str
    drug_name: str
    indication: str
    phase: TrialPhase
    expected_milestone_date: datetime
    catalyst_importance: str  # HIGH, MEDIUM, LOW

class FDAMonitor:
    """Monitor FDA-related catalysts for biotech/pharma stocks"""
    
    def __init__(self):
        self.trials: List[DrugTrial] = []
        self.catalyst_weights = {
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1
        }
    
    def add_trial(self, trial: DrugTrial):
        """Add drug trial to monitor"""
        self.trials.append(trial)
    
    def predict_price_move(self, trial: DrugTrial, 
                          outcome: str) -> Dict:
        """Predict price movement on FDA news"""
        base_moves = {
            TrialPhase.PHASE_1: {
                "positive": 15,
                "negative": -10,
                "neutral": 2
            },
            TrialPhase.PHASE_2: {
                "positive": 35,
                "negative": -25,
                "neutral": 5
            },
            TrialPhase.PHASE_3: {
                "positive": 80,
                "negative": -50,
                "neutral": 10
            },
            TrialPhase.FDA_REVIEW: {
                "approved": 45,
                "rejected": -60,
                "delayed": -15
            }
        }
        
        moves = base_moves.get(trial.phase, {})
        expected_move = moves.get(outcome, 0)
        
        # Adjust for catalyst importance
        weight = self.catalyst_weights.get(trial.catalyst_importance, 1)
        adjusted_move = expected_move * (0.7 + 0.3 * weight / 3)
        
        return {
            "ticker": trial.ticker,
            "drug": trial.drug_name,
            "phase": trial.phase.value,
            "expected_move_pct": round(adjusted_move, 1),
            "direction": "UP" if adjusted_move > 0 else "DOWN",
            "confidence": "HIGH" if trial.phase in [TrialPhase.PHASE_3, TrialPhase.FDA_REVIEW] else "MEDIUM",
            "risk_reward": self._calculate_risk_reward(trial, adjusted_move)
        }
    
    def _calculate_risk_reward(self, trial: DrugTrial, expected_move: float) -> str:
        """Calculate risk/reward ratio"""
        if trial.phase == TrialPhase.PHASE_3:
            # High risk/reward for Phase 3
            return "1:2.5" if expected_move > 0 else "2.5:1"
        elif trial.phase == TrialPhase.PHASE_2:
            return "1:1.8" if expected_move > 0 else "1.8:1"
        return "1:1.2"
    
    def get_upcoming_catalysts(self, days: int = 30) -> List[Dict]:
        """Get upcoming FDA catalysts"""
        cutoff = datetime.utcnow() + timedelta(days=days)
        
        upcoming = []
        for trial in self.trials:
            if trial.expected_milestone_date <= cutoff:
                days_until = (trial.expected_milestone_date - datetime.utcnow()).days
                
                upcoming.append({
                    "ticker": trial.ticker,
                    "company": trial.company,
                    "drug": trial.drug_name,
                    "indication": trial.indication,
                    "phase": trial.phase.value,
                    "milestone_date": trial.expected_milestone_date.strftime("%Y-%m-%d"),
                    "days_until": days_until,
                    "importance": trial.catalyst_importance,
                    "trade_setup": self._get_trade_setup(trial)
                })
        
        return sorted(upcoming, key=lambda x: (x["days_until"], -self.catalyst_weights[x["importance"]]))
    
    def _get_trade_setup(self, trial: DrugTrial) -> str:
        """Get trade setup recommendation"""
        if trial.phase == TrialPhase.FDA_REVIEW:
            return "STRADDLE_HIGH_IV"
        elif trial.phase == TrialPhase.PHASE_3:
            return "POSITION_BEFORE_BINARY"
        elif trial.catalyst_importance == "HIGH":
            return "WATCH_FOR_RUNUP"
        return "LOW_PRIORITY"
    
    def analyze_biotech_portfolio(self, holdings: List[str]) -> Dict:
        """Analyze FDA risk in portfolio"""
        portfolio_trials = [t for t in self.trials if t.ticker in holdings]
        
        high_risk_binary = sum(1 for t in portfolio_trials 
                              if t.phase in [TrialPhase.PHASE_3, TrialPhase.FDA_REVIEW])
        
        catalyst_dates = [t.expected_milestone_date for t in portfolio_trials]
        
        return {
            "fda_exposure_count": len(portfolio_trials),
            "high_risk_binary_events": high_risk_binary,
            "next_catalyst": min(catalyst_dates).strftime("%Y-%m-%d") if catalyst_dates else None,
            "risk_concentration": "HIGH" if high_risk_binary > 2 else "MEDIUM" if high_risk_binary > 0 else "LOW",
            "hedging_recommended": high_risk_binary > 0,
            "diversification_alert": high_risk_binary > 3
        }

from datetime import timedelta
