"""
Music Teacher & Education Business Tracker
===========================================
Track music teaching income - private lessons, group classes
Studio rental, online teaching, recital income
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from enum import Enum


class LessonType(Enum):
    PRIVATE = "private"
    GROUP = "group"
    ONLINE = "online"
    MASTERCLASS = "masterclass"
    WORKSHOP = "workshop"


class Instrument(Enum):
    PIANO = "piano"
    GUITAR = "guitar"
    VIOLIN = "violin"
    VOICE = "voice"
    DRUMS = "drums"
    WOODWINDS = "woodwinds"
    BRASS = "brass"
    STRINGS = "strings"


@dataclass
class Student:
    id: str
    name: str
    instrument: str
    lesson_type: str
    lesson_duration: int  # minutes
    lessons_per_week: int
    rate_per_lesson: float
    start_date: date
    status: str  # 'active', 'paused', 'dropped'
    level: str  # 'beginner', 'intermediate', 'advanced'


@dataclass
class Lesson:
    student_id: str
    date: date
    duration_minutes: int
    type: str
    revenue: float
    location: str  # 'studio', 'student_home', 'online'
    materials_used: float  # cost


class MusicTeacherTracker:
    """Track music teaching business finances"""
    
    # Industry benchmarks
    BENCHMARKS = {
        'private_lesson_rates': {
            'beginner': 35,  # per 30 min
            'intermediate': 45,
            'advanced': 60
        },
        'group_class_rate': 25,  # per student per hour
        'online_discount': 0.90,  # 10% discount for online
        'studio_rental_hourly': 25,
        'student_retention_months': 18,
        'avg_students_per_teacher': 25
    }
    
    def __init__(self, teacher_name: str = "Music Teacher"):
        self.teacher_name = teacher_name
        self.students: List[Student] = []
        self.lessons: List[Lesson] = []
        self.instruments_taught: List[str] = []
    
    def add_student(self, student: Student):
        """Add new student"""
        self.students.append(student)
        if student.instrument not in self.instruments_taught:
            self.instruments_taught.append(student.instrument)
    
    def record_lesson(self, lesson: Lesson):
        """Record completed lesson"""
        self.lessons.append(lesson)
    
    def calculate_monthly_revenue(self, target_month: date = None) -> Dict:
        """Calculate projected monthly revenue"""
        if target_month is None:
            target_month = date.today()
        
        active_students = [s for s in self.students if s.status == 'active']
        
        revenue_by_type = {}
        total_monthly = 0
        
        for student in active_students:
            weekly_lessons = student.lessons_per_week
            monthly_lessons = weekly_lessons * 4.3
            monthly_revenue = monthly_lessons * student.rate_per_lesson
            
            ltype = student.lesson_type
            if ltype not in revenue_by_type:
                revenue_by_type[ltype] = 0
            revenue_by_type[ltype] += monthly_revenue
            
            total_monthly += monthly_revenue
        
        # Annual projection
        annual_revenue = total_monthly * 12
        
        # By instrument
        by_instrument = {}
        for s in active_students:
            inst = s.instrument
            if inst not in by_instrument:
                by_instrument[inst] = {'students': 0, 'monthly_revenue': 0}
            by_instrument[inst]['students'] += 1
            # Add portion of revenue
            weekly = s.lessons_per_week
            monthly = weekly * 4.3 * s.rate_per_lesson
            by_instrument[inst]['monthly_revenue'] += monthly
        
        return {
            'teacher': self.teacher_name,
            'month': target_month.strftime('%Y-%m'),
            'active_students': len(active_students),
            'monthly_revenue': round(total_monthly, 2),
            'annual_projection': round(annual_revenue, 2),
            'by_lesson_type': {k: round(v, 2) for k, v in revenue_by_type.items()},
            'by_instrument': by_instrument,
            'instruments_taught': self.instruments_taught,
            'avg_revenue_per_student': round(total_monthly / len(active_students), 2) if active_students else 0,
            'capacity_utilization': self._calculate_capacity(active_students)
        }
    
    def _calculate_capacity(self, active_students: List[Student]) -> Dict:
        """Calculate teaching capacity utilization"""
        # Assume 40 hours/week teaching capacity
        max_weekly_hours = 40
        
        current_weekly_hours = sum(
            s.lessons_per_week * (s.lesson_duration / 60)
            for s in active_students
        )
        
        utilization_pct = (current_weekly_hours / max_weekly_hours) * 100
        
        return {
            'weekly_teaching_hours': round(current_weekly_hours, 1),
            'max_capacity_hours': max_weekly_hours,
            'utilization_pct': round(utilization_pct, 1),
            'status': 'AT_CAPACITY' if utilization_pct > 90 else 'NEAR_CAPACITY' if utilization_pct > 75 else 'ROOM_TO_GROW',
            'remaining_slots': int((max_weekly_hours - current_weekly_hours) / 0.5)  # Assuming 30-min slots
        }
    
    def calculate_student_value(self, student: Student) -> Dict:
        """Calculate student lifetime value"""
        monthly_revenue = student.lessons_per_week * 4.3 * student.rate_per_lesson
        
        # Expected tenure
        avg_retention = self.BENCHMARKS['student_retention_months']
        
        # Adjust by level
        if student.level == 'advanced':
            avg_retention *= 1.2  # Advanced students stay longer
        elif student.level == 'beginner':
            avg_retention *= 0.8  # Beginners drop off faster
        
        gross_ltv = monthly_revenue * avg_retention
        
        # Costs (assuming online has lower cost)
        if student.lesson_type == 'online':
            cost_pct = 0.05
        else:
            cost_pct = 0.15  # Studio rental, travel, etc.
        
        costs = gross_ltv * cost_pct
        
        net_ltv = gross_ltv - costs
        
        return {
            'student_id': student.id,
            'student_name': student.name,
            'instrument': student.instrument,
            'level': student.level,
            'monthly_revenue': round(monthly_revenue, 2),
            'expected_tenure_months': round(avg_retention, 1),
            'gross_ltv': round(gross_ltv, 2),
            'estimated_costs': round(costs, 2),
            'net_ltv': round(net_ltv, 2),
            'value_tier': 'HIGH' if net_ltv > 2000 else 'MEDIUM' if net_ltv > 1000 else 'LOW'
        }
    
    def get_business_health(self) -> Dict:
        """Get overall business health"""
        
        active = [s for s in self.students if s.status == 'active']
        paused = [s for s in self.students if s.status == 'paused']
        dropped = [s for s in self.students if s.status == 'dropped']
        
        if not self.students:
            return {'status': 'NO_STUDENTS', 'message': 'Add students to see metrics'}
        
        # Retention rate
        total_ever = len(self.students)
        retention_rate = len(active) / total_ever if total_ever > 0 else 0
        
        # Churn analysis
        churn_rate = len(dropped) / total_ever if total_ever > 0 else 0
        
        # Monthly metrics
        monthly = self.calculate_monthly_revenue()
        
        # Student progression
        by_level = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        for s in active:
            if s.level in by_level:
                by_level[s.level] += 1
        
        # Capacity
        capacity = monthly['capacity_utilization']
        
        # Average lesson rate
        if active:
            avg_rate = sum(s.rate_per_lesson for s in active) / len(active)
        else:
            avg_rate = 0
        
        return {
            'teacher_name': self.teacher_name,
            'business_status': 'THRIVING' if len(active) > 30 else 'HEALTHY' if len(active) > 15 else 'BUILDING',
            'active_students': len(active),
            'paused_students': len(paused),
            'historical_dropped': len(dropped),
            'retention_rate_pct': round(retention_rate * 100, 1),
            'churn_rate_pct': round(churn_rate * 100, 1),
            'monthly_revenue': monthly['monthly_revenue'],
            'annual_projection': monthly['annual_projection'],
            'student_level_distribution': by_level,
            'capacity_status': capacity['status'],
            'capacity_utilization_pct': capacity['utilization_pct'],
            'avg_lesson_rate': round(avg_rate, 2),
            'instruments_offered': self.instruments_taught,
            'recommendations': self._generate_recommendations(active, capacity, churn_rate)
        }
    
    def _generate_recommendations(self, active: List[Student], 
                                  capacity: Dict, churn_rate: float) -> List[str]:
        """Generate business recommendations"""
        recs = []
        
        if capacity['utilization_pct'] < 50:
            recs.append("MARKETING_PUSH - Low capacity, acquire more students")
            recs.append("OFFER_INTRO_SPECIAL - Attract beginners with discount")
        
        if capacity['utilization_pct'] > 85:
            recs.append("RAISE_RATES - Near capacity, increase pricing")
            recs.append("ADD_GROUP_CLASSES - Serve more students efficiently")
            recs.append("WAITLIST_MANAGEMENT - Start waitlist for new inquiries")
        
        if churn_rate > 0.30:
            recs.append("RETENTION_FOCUS - High churn, improve student engagement")
            recs.append("RECITAL_EVENTS - Build community to reduce dropouts")
        
        # Check online presence
        online_students = [s for s in active if s.lesson_type == 'online']
        if len(online_students) / len(active) < 0.20 if active else 0:
            recs.append("EXPAND_ONLINE - Higher margins, broader reach")
        
        if not recs:
            recs.append("MAINTAIN_QUALITY - Business performing well")
        
        return recs
    
    def get_pricing_guide(self) -> Dict:
        """Get recommended pricing guide"""
        return {
            'private_lessons': {
                '30_minute': {
                    'beginner': 35,
                    'intermediate': 40,
                    'advanced': 50
                },
                '45_minute': {
                    'beginner': 45,
                    'intermediate': 55,
                    'advanced': 70
                },
                '60_minute': {
                    'beginner': 55,
                    'intermediate': 70,
                    'advanced': 90
                }
            },
            'group_classes': {
                'per_student_per_hour': 25,
                'min_students': 4,
                'max_students': 12,
                'description': 'Suzuki group, ensemble, theory class'
            },
            'online_lessons': {
                'discount_pct': 10,
                'note': 'Same rates but 10% discount for online',
                'platforms': ['Zoom', 'Skype', 'FaceTime']
            },
            'additional_services': {
                'recital_accompaniment': 75,
                'recording_session': 100,
                'music_theory_tutoring': 50,
                'college_audition_prep': 100,
                'instrument_rental_monthly': 35
            }
        }
    
    def get_expense_categories(self) -> Dict:
        """Get typical expense categories for music teachers"""
        return {
            'studio_rental': '20-30% of revenue if renting space',
            'instrument_maintenance': '5% of revenue',
            'sheet_music_materials': '3% of revenue',
            'marketing': '5% of revenue',
            'continuing_education': '3% of revenue',
            'insurance': '2% of revenue',
            'technology': '2% of revenue (scheduling, payment apps)',
            'taxes_self_employment': '15.3% of net income'
        }


# Usage
def quick_music_teacher_analysis(students_data: List[Dict]) -> Dict:
    """Quick music teaching business analysis"""
    tracker = MusicTeacherTracker()
    
    for s in students_data:
        student = Student(
            id=s['id'],
            name=s['name'],
            instrument=s.get('instrument', 'piano'),
            lesson_type=s.get('type', 'private'),
            lesson_duration=s.get('duration', 30),
            lessons_per_week=s.get('frequency', 1),
            rate_per_lesson=s.get('rate', 40),
            start_date=s.get('start', date.today()),
            status=s.get('status', 'active'),
            level=s.get('level', 'beginner')
        )
        tracker.add_student(student)
    
    return tracker.get_business_health()


def calculate_student_ltv(student_data: Dict) -> Dict:
    """Calculate single student lifetime value"""
    tracker = MusicTeacherTracker()
    
    student = Student(
        id=student_data['id'],
        name=student_data['name'],
        instrument=student_data.get('instrument', 'piano'),
        lesson_type=student_data.get('type', 'private'),
        lesson_duration=student_data.get('duration', 30),
        lessons_per_week=student_data.get('frequency', 1),
        rate_per_lesson=student_data.get('rate', 40),
        start_date=student_data.get('start', date.today()),
        status='active',
        level=student_data.get('level', 'beginner')
    )
    
    return tracker.calculate_student_value(student)


def get_teacher_pricing() -> Dict:
    """Get pricing guide"""
    tracker = MusicTeacherTracker()
    return tracker.get_pricing_guide()
