"""Escalation simulation module."""
from typing import Dict, List, Any, Tuple

class EscalationSim:
    THRESHOLDS: List[Tuple[int, str]] = [(25, "MICRO"), (100, "SMALL"), (500, "MEDIUM"), (2000, "GROWTH"), (10000, "WEALTH")]
    
    def simulate(self, start: float = 20, target: float = 100, years: int = 5) -> Dict[str, Any]:
        weeks = years * 52
        capital = contributed = 0.0
        milestones: List[Tuple[int, str, float]] = []
        for week in range(weeks):
            monthly = start * (target / start) ** min(week / 4.33 / 24, 1)
            capital += monthly
            contributed += monthly
            capital *= 1.0015
            for t, label in self.THRESHOLDS:
                if capital >= t and label not in [m[1] for m in milestones]:
                    milestones.append((week, label, round(capital, 2)))
        return {"final": round(capital, 2), "contributed": round(contributed, 2), "gain": round(capital - contributed, 2), "milestones": milestones}

if __name__ == "__main__":
    r = EscalationSim().simulate(20, 100, 5)
    print(f"Final: {r['final']:.2f}, Gain: {r['gain']:.2f}")