"""
Financial Advisor Scheduling System
Inspired by Gymcatch - Online booking with automated reminders
Features: Appointments, packages, virtual sessions, client tracking
"""

from .appointment_booking import AppointmentBooking
from .package_management import PackageManager
from .client_progress import ClientProgressTracker
from .reminder_system import ReminderSystem

__all__ = [
    'AppointmentBooking',
    'PackageManager',
    'ClientProgressTracker',
    'ReminderSystem',
]
