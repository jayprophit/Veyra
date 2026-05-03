"""
Appointment Booking System
Gymcatch-inspired scheduling for financial advisors
Online booking with availability management
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid

class SessionType(Enum):
    CONSULTATION = "consultation"  # Initial meeting
    REVIEW = "review"  # Portfolio review
    PLANNING = "planning"  # Financial planning
    TAX_PLANNING = "tax_planning"  # Tax consultation
    INVESTMENT = "investment"  # Investment strategy
    VIRTUAL = "virtual"  # Video call
    PHONE = "phone"  # Phone call

class AppointmentStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

@dataclass
class TimeSlot:
    """Available time slot for booking"""
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    advisor_id: str = ""
    session_type: SessionType = SessionType.CONSULTATION
    
@dataclass
class Appointment:
    """Scheduled appointment"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = ""
    client_name: str = ""
    client_email: str = ""
    client_phone: str = ""
    advisor_id: str = ""
    advisor_name: str = ""
    session_type: SessionType = SessionType.CONSULTATION
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    status: AppointmentStatus = AppointmentStatus.PENDING
    notes: str = ""
    zoom_link: str = ""
    package_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    reminders_sent: List[str] = field(default_factory=list)

class AppointmentBooking:
    """
    Online appointment booking system
    Manages availability, bookings, and scheduling
    """
    
    def __init__(self):
        self._appointments: Dict[str, Appointment] = {}
        self._advisor_schedules: Dict[str, List[TimeSlot]] = {}
        self._session_durations: Dict[SessionType, int] = {
            SessionType.CONSULTATION: 60,
            SessionType.REVIEW: 45,
            SessionType.PLANNING: 90,
            SessionType.TAX_PLANNING: 60,
            SessionType.INVESTMENT: 60,
            SessionType.VIRTUAL: 30,
            SessionType.PHONE: 30,
        }
    
    def set_advisor_availability(self, advisor_id: str, date: datetime,
                               start_hour: int = 9, end_hour: int = 17,
                               slot_duration: int = 30,
                               session_types: List[SessionType] = None):
        """
        Set availability for an advisor on a specific date
        
        Args:
            advisor_id: Advisor identifier
            date: Date for availability
            start_hour: Start of day (24h format)
            end_hour: End of day (24h format)
            slot_duration: Duration of each slot in minutes
            session_types: Types of sessions available
        """
        if advisor_id not in self._advisor_schedules:
            self._advisor_schedules[advisor_id] = []
        
        session_types = session_types or [SessionType.CONSULTATION]
        
        # Create time slots
        current_time = datetime(date.year, date.month, date.day, start_hour, 0)
        end_time = datetime(date.year, date.month, date.day, end_hour, 0)
        
        while current_time < end_time:
            for session_type in session_types:
                slot_duration = self._session_durations.get(session_type, 60)
                slot_end = current_time + timedelta(minutes=slot_duration)
                
                if slot_end <= end_time:
                    slot = TimeSlot(
                        start_time=current_time,
                        end_time=slot_end,
                        is_available=True,
                        advisor_id=advisor_id,
                        session_type=session_type
                    )
                    self._advisor_schedules[advisor_id].append(slot)
            
            current_time += timedelta(minutes=slot_duration)
    
    def get_available_slots(self, advisor_id: str, 
                          start_date: datetime,
                          end_date: datetime,
                          session_type: Optional[SessionType] = None) -> List[TimeSlot]:
        """Get available booking slots for an advisor"""
        slots = self._advisor_schedules.get(advisor_id, [])
        
        available = [
            slot for slot in slots
            if slot.is_available
            and start_date <= slot.start_time <= end_date
            and (session_type is None or slot.session_type == session_type)
        ]
        
        return sorted(available, key=lambda s: s.start_time)
    
    def book_appointment(self, client_id: str, client_name: str, client_email: str,
                        advisor_id: str, session_type: SessionType,
                        start_time: datetime, 
                        notes: str = "",
                        client_phone: str = "",
                        package_id: Optional[str] = None) -> Appointment:
        """Book a new appointment"""
        # Check availability
        slots = self._advisor_schedules.get(advisor_id, [])
        
        # Find matching slot
        duration = self._session_durations.get(session_type, 60)
        end_time = start_time + timedelta(minutes=duration)
        
        slot_found = False
        for slot in slots:
            if (slot.start_time == start_time and 
                slot.advisor_id == advisor_id and
                slot.session_type == session_type and
                slot.is_available):
                slot.is_available = False
                slot_found = True
                break
        
        if not slot_found:
            raise ValueError(f"Time slot not available: {start_time}")
        
        # Create appointment
        appointment = Appointment(
            client_id=client_id,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            advisor_id=advisor_id,
            session_type=session_type,
            start_time=start_time,
            end_time=end_time,
            notes=notes,
            package_id=package_id
        )
        
        self._appointments[appointment.id] = appointment
        
        # Generate Zoom link for virtual sessions
        if session_type in [SessionType.VIRTUAL]:
            appointment.zoom_link = self._generate_zoom_link(appointment.id)
        
        return appointment
    
    def cancel_appointment(self, appointment_id: str, reason: str = "") -> Appointment:
        """Cancel an appointment"""
        appointment = self._appointments.get(appointment_id)
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment.status = AppointmentStatus.CANCELLED
        appointment.notes += f"\nCancelled: {reason}"
        appointment.updated_at = datetime.now()
        
        # Free up the time slot
        slots = self._advisor_schedules.get(appointment.advisor_id, [])
        for slot in slots:
            if (slot.start_time == appointment.start_time and
                slot.session_type == appointment.session_type):
                slot.is_available = True
                break
        
        return appointment
    
    def reschedule_appointment(self, appointment_id: str, 
                             new_start_time: datetime) -> Appointment:
        """Reschedule to a new time slot"""
        appointment = self._appointments.get(appointment_id)
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        # Cancel old slot
        self.cancel_appointment(appointment_id, "Rescheduled")
        
        # Book new slot
        new_appointment = self.book_appointment(
            client_id=appointment.client_id,
            client_name=appointment.client_name,
            client_email=appointment.client_email,
            advisor_id=appointment.advisor_id,
            session_type=appointment.session_type,
            start_time=new_start_time,
            notes=appointment.notes,
            client_phone=appointment.client_phone,
            package_id=appointment.package_id
        )
        
        return new_appointment
    
    def get_appointments(self, advisor_id: Optional[str] = None,
                        client_id: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        status: Optional[AppointmentStatus] = None) -> List[Appointment]:
        """Get appointments with filters"""
        appointments = list(self._appointments.values())
        
        if advisor_id:
            appointments = [a for a in appointments if a.advisor_id == advisor_id]
        
        if client_id:
            appointments = [a for a in appointments if a.client_id == client_id]
        
        if start_date:
            appointments = [a for a in appointments if a.start_time >= start_date]
        
        if end_date:
            appointments = [a for a in appointments if a.start_time <= end_date]
        
        if status:
            appointments = [a for a in appointments if a.status == status]
        
        return sorted(appointments, key=lambda a: a.start_time)
    
    def get_advisor_calendar(self, advisor_id: str, 
                            start_date: datetime,
                            end_date: datetime) -> Dict:
        """Get full calendar view for an advisor"""
        appointments = self.get_appointments(
            advisor_id=advisor_id,
            start_date=start_date,
            end_date=end_date
        )
        
        available_slots = self.get_available_slots(
            advisor_id=advisor_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "advisor_id": advisor_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "appointments": [
                {
                    "id": a.id,
                    "client_name": a.client_name,
                    "type": a.session_type.value,
                    "start": a.start_time.isoformat(),
                    "end": a.end_time.isoformat(),
                    "status": a.status.value,
                    "zoom_link": a.zoom_link
                }
                for a in appointments
            ],
            "available_slots": [
                {
                    "start": s.start_time.isoformat(),
                    "end": s.end_time.isoformat(),
                    "type": s.session_type.value
                }
                for s in available_slots
            ]
        }
    
    def complete_appointment(self, appointment_id: str, 
                           notes: str = "") -> Appointment:
        """Mark appointment as completed"""
        appointment = self._appointments.get(appointment_id)
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment.status = AppointmentStatus.COMPLETED
        appointment.notes += f"\nSession Notes: {notes}"
        appointment.updated_at = datetime.now()
        
        return appointment
    
    def _generate_zoom_link(self, appointment_id: str) -> str:
        """Generate Zoom meeting link (placeholder)"""
        # In production, integrate with Zoom API
        return f"https://zoom.us/j/{appointment_id[:10]}"
    
    def get_upcoming_appointments(self, hours: int = 24) -> List[Appointment]:
        """Get appointments happening within next N hours"""
        now = datetime.now()
        future = now + timedelta(hours=hours)
        
        return [
            a for a in self._appointments.values()
            if now <= a.start_time <= future
            and a.status in [AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]
        ]

# Singleton instance
_appointment_booking: Optional[AppointmentBooking] = None

def get_appointment_booking() -> AppointmentBooking:
    """Get or create singleton Appointment Booking instance"""
    global _appointment_booking
    if _appointment_booking is None:
        _appointment_booking = AppointmentBooking()
    return _appointment_booking
