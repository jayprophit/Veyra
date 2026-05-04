"""Escalation simulation module."""
from typing import Dict, List, Any, Tuple


class EscalationSim:
    """Wealth escalation simulator."""

    THRESHOLDS: List[Tuple[int, str]] = [
        (25, "MICRO"),
        (100, "SMALL"),
        (500, "MEDIUM"),
        (2000, "GROWTH"),
        (10000, "WEALTH"),
    ]

    def simulate(self, start: float = 20, target: float = 100, years: int = 5) -> Dict[str, Any]:
        """Simulate wealth escalation."""
        weeks = years * 52
        capital = 0.0
        contributed = 0.0
        milestones: List[Tuple[int, str, float]] = []
        
        for week in range(weeks):
            months = week / 4.33
            weekly = start * (target / start) ** min(months / 24, 1)
            capital += weekly
            contributed += weekly
            capital *= 1.0015
            
            for threshold, label in self.THRESHOLDS:
                if capital >= threshold and label not in [m[1] for m in milestones]:
                    milestones.append((week, label, round(capital, 2)))
        
        return {
            "final": round(capital, 2),
            "contributed": round(contributed, 2),
            "gain": round(capital - contributed, 2),
            "milestones": milestones,
        }


if __name__ == "__main__":
    sim = EscalationSim()
    result = sim.simulate(20, 100, 5)
    print(f"Final: {result['final']:.2f}")
    print(f"Contributed: {result['contributed']:.2f}")
    print(f"Gain: {result['gain']:.2f}")
    for m in result["milestones"][:4]:
        print(f"Week {m[0]}: {m[1]} ({m[2]:.2f})")