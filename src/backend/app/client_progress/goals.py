"""Goal Setting and Tracking for Clients"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, date
from enum import Enum
import uuid

class GoalType(Enum):
    FINANCIAL = "financial"
    INVESTMENT = "investment"
    SAVINGS = "savings"
    DEBT = "debt"
    EDUCATION = "education"

class GoalStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

@dataclass
class Goal:
    id: str
    client_id: str
    advisor_id: str
    title: str
    description: str
    goal_type: GoalType
    target_value: float
    current_value: float
    deadline: Optional[date]
    status: GoalStatus
    created_at: datetime
    milestones: List[Dict]

class GoalManager:
    def __init__(self):
        self._goals: Dict[str, Goal] = {}
    
    def create_goal(self, client_id: str, advisor_id: str, title: str,
                   description: str, goal_type: GoalType, target_value: float,
                   deadline: Optional[date] = None) -> Goal:
        goal = Goal(
            id=str(uuid.uuid4()),
            client_id=client_id,
            advisor_id=advisor_id,
            title=title,
            description=description,
            goal_type=goal_type,
            target_value=target_value,
            current_value=0.0,
            deadline=deadline,
            status=GoalStatus.ACTIVE,
            created_at=datetime.now(),
            milestones=[]
        )
        self._goals[goal.id] = goal
        return goal
    
    def update_progress(self, goal_id: str, new_value: float) -> Optional[Goal]:
        if goal := self._goals.get(goal_id):
            goal.current_value = new_value
            if goal.current_value >= goal.target_value:
                goal.status = GoalStatus.COMPLETED
            return goal
        return None
    
    def get_client_goals(self, client_id: str) -> List[Goal]:
        return [g for g in self._goals.values() if g.client_id == client_id]
    
    def get_goal_progress(self, goal_id: str) -> Dict:
        if goal := self._goals.get(goal_id):
            pct = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
            return {
                "goal_id": goal_id,
                "title": goal.title,
                "target": goal.target_value,
                "current": goal.current_value,
                "percentage": round(pct, 1),
                "status": goal.status.value,
                "remaining": round(goal.target_value - goal.current_value, 2)
            }
        return {}
    
    def get_upcoming_deadlines(self, days: int = 30) -> List[Goal]:
        cutoff = date.today() + __import__('datetime').timedelta(days=days)
        return [
            g for g in self._goals.values()
            if g.deadline and g.deadline <= cutoff and g.status == GoalStatus.ACTIVE
        ]
