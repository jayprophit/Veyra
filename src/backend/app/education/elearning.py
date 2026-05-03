"""E-Learning System for Financial Master."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

class CourseLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class Course:
    id: str
    title: str
    description: str
    level: CourseLevel
    duration_minutes: int
    points_reward: int = 100
    certification_nft: bool = False

@dataclass
class UserProgress:
    user_id: str
    course_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress_percent: float = 0.0
    certificate_issued: bool = False

class ELearningSystem:
    """Trading education platform with blockchain certificates."""
    
    def __init__(self):
        self.courses: Dict[str, Course] = {}
        self.progress: Dict[str, Dict[str, UserProgress]] = defaultdict(dict)
        self._init_courses()
    
    def _init_courses(self):
        self.courses['trading-101'] = Course(
            id='trading-101', title='Trading 101',
            description='Trading fundamentals', level=CourseLevel.BEGINNER,
            duration_minutes=120, points_reward=200
        )
        self.courses['technical-analysis'] = Course(
            id='technical-analysis', title='Technical Analysis',
            description='Charts and indicators', level=CourseLevel.BEGINNER,
            duration_minutes=180, points_reward=300
        )
        self.courses['risk-management'] = Course(
            id='risk-management', title='Risk Management',
            description='Position sizing and stops', level=CourseLevel.INTERMEDIATE,
            duration_minutes=150, points_reward=400
        )
        self.courses['algo-trading'] = Course(
            id='algo-trading', title='Algorithmic Trading',
            description='Build trading bots', level=CourseLevel.ADVANCED,
            duration_minutes=300, points_reward=800, certification_nft=True
        )
        self.courses['ai-trading'] = Course(
            id='ai-trading', title='AI Trading',
            description='ML for trading', level=CourseLevel.EXPERT,
            duration_minutes=400, points_reward=1000, certification_nft=True
        )
    
    async def get_courses(self, level: Optional[CourseLevel] = None) -> List[Dict]:
        return [{
            'id': c.id, 'title': c.title, 'level': c.level.value,
            'duration': c.duration_minutes, 'points': c.points_reward,
            'cert_nft': c.certification_nft
        } for c in self.courses.values() if not level or c.level == level]
    
    async def enroll(self, user_id: str, course_id: str) -> Dict:
        if course_id not in self.courses:
            return {'success': False, 'error': 'Course not found'}
        
        progress = UserProgress(
            user_id=user_id, course_id=course_id,
            started_at=datetime.now()
        )
        self.progress[user_id][course_id] = progress
        return {'success': True, 'course': self.courses[course_id].title}
    
    async def update_progress(self, user_id: str, course_id: str, percent: float) -> Dict:
        if course_id not in self.progress[user_id]:
            return {'success': False, 'error': 'Not enrolled'}
        
        p = self.progress[user_id][course_id]
        p.progress_percent = min(percent, 100)
        
        if p.progress_percent >= 100 and not p.completed_at:
            p.completed_at = datetime.now()
            course = self.courses[course_id]
            return {
                'success': True,
                'completed': True,
                'points_earned': course.points_reward,
                'cert_nft': course.certification_nft
            }
        
        return {'success': True, 'progress': p.progress_percent}
    
    async def issue_certificate(self, user_id: str, course_id: str) -> Optional[str]:
        """Issue blockchain certificate. Returns certificate hash."""
        p = self.progress[user_id].get(course_id)
        if not p or not p.completed_at:
            return None
        
        course = self.courses[course_id]
        if not course.certification_nft:
            return None
        
        import hashlib
        cert_data = f"{user_id}:{course_id}:{p.completed_at.isoformat()}"
        cert_hash = hashlib.sha256(cert_data.encode()).hexdigest()
        p.certificate_issued = True
        return cert_hash

elearning = ELearningSystem()
