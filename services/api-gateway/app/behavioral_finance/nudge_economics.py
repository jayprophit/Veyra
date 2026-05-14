"""Nudge Economics"""
from typing import Dict

class NudgeEconomics:
    def default_effect(self, opt_in_default: bool, participation_rate: float) -> Dict:
        base_rate = 0.3
        nudge_lift = 0.25 if opt_in_default else 0
        return {"participation": participation_rate, "lift_from_default": nudge_lift}
    
    def loss_aversion_nudge(self, frame_as_loss: bool, response_rate: float) -> Dict:
        multiplier = 2.25 if frame_as_loss else 1.0
        return {"effective_rate": response_rate * multiplier, "framing": "loss" if frame_as_loss else "gain"}
