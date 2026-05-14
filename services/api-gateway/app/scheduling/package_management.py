"""
Package & Membership Management
Gymcatch-style session packages for financial advisors
10-packs, monthly memberships, tiered access
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid

class PackageType(Enum):
    SESSION_PACK = "session_pack"  # Fixed number of sessions
    MONTHLY = "monthly"  # Monthly membership
    ANNUAL = "annual"  # Annual membership
    UNLIMITED = "unlimited"  # Unlimited sessions
    TIERED = "tiered"  # Bronze/Silver/Gold tiers

@dataclass
class PackageTemplate:
    """Template for creating client packages"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    package_type: PackageType = PackageType.SESSION_PACK
    total_sessions: int = 0  # 0 for unlimited
    duration_days: int = 0  # 0 for no expiry
    price: float = 0.0
    currency: str = "USD"
    features: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ClientPackage:
    """Package purchased by a client"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = ""
    template_id: str = ""
    name: str = ""
    total_sessions: int = 0
    used_sessions: int = 0
    start_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    status: str = "active"  # active, expired, completed
    price_paid: float = 0.0
    appointments: List[str] = field(default_factory=list)  # Appointment IDs
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def remaining_sessions(self) -> int:
        if self.total_sessions == 0:
            return -1  # Unlimited
        return self.total_sessions - self.used_sessions
    
    @property
    def is_expired(self) -> bool:
        if not self.expiry_date:
            return False
        return datetime.now() > self.expiry_date
    
    @property
    def is_depleted(self) -> bool:
        if self.total_sessions == 0:
            return False
        return self.used_sessions >= self.total_sessions

class PackageManager:
    """
    Manages session packages and memberships
    Gymcatch-inspired package system
    """
    
    # Default package templates
    DEFAULT_TEMPLATES = [
        PackageTemplate(
            name="Starter Pack",
            description="5 financial consultation sessions",
            package_type=PackageType.SESSION_PACK,
            total_sessions=5,
            duration_days=180,
            price=750.0,
            features=["5 x 60-min sessions", "Email support", "Session recordings"]
        ),
        PackageTemplate(
            name="Pro Pack",
            description="10 sessions with priority booking",
            package_type=PackageType.SESSION_PACK,
            total_sessions=10,
            duration_days=365,
            price=1200.0,
            features=["10 x 60-min sessions", "Priority scheduling", "WhatsApp support", "Custom reports"]
        ),
        PackageTemplate(
            name="Monthly Membership",
            description="2 sessions per month",
            package_type=PackageType.MONTHLY,
            total_sessions=2,
            duration_days=30,
            price=250.0,
            features=["2 sessions/month", "Group webinars", "Monthly newsletter", "Resource library"]
        ),
        PackageTemplate(
            name="Annual Unlimited",
            description="Unlimited sessions for one year",
            package_type=PackageType.ANNUAL,
            total_sessions=0,  # Unlimited
            duration_days=365,
            price=5000.0,
            features=["Unlimited sessions", "24/7 support", "Tax filing included", "Family accounts"]
        ),
        PackageTemplate(
            name="Bronze Tier",
            description="Basic tier - 1 session/month",
            package_type=PackageType.TIERED,
            total_sessions=1,
            duration_days=30,
            price=150.0,
            features=["1 session/month", "Email support"]
        ),
        PackageTemplate(
            name="Silver Tier",
            description="Standard tier - 2 sessions/month",
            package_type=PackageType.TIERED,
            total_sessions=2,
            duration_days=30,
            price=280.0,
            features=["2 sessions/month", "Priority support", "Video calls"]
        ),
        PackageTemplate(
            name="Gold Tier",
            description="Premium tier - 4 sessions/month",
            package_type=PackageType.TIERED,
            total_sessions=4,
            duration_days=30,
            price=500.0,
            features=["4 sessions/month", "24/7 support", "Custom analysis", "Family included"]
        ),
    ]
    
    def __init__(self):
        self._templates: Dict[str, PackageTemplate] = {}
        self._client_packages: Dict[str, ClientPackage] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize with default package templates"""
        for template in self.DEFAULT_TEMPLATES:
            self._templates[template.id] = template
    
    def create_template(self, name: str, description: str, package_type: PackageType,
                       price: float, total_sessions: int = 0, duration_days: int = 0,
                       features: List[str] = None, currency: str = "USD") -> PackageTemplate:
        """Create a new package template"""
        template = PackageTemplate(
            name=name,
            description=description,
            package_type=package_type,
            total_sessions=total_sessions,
            duration_days=duration_days,
            price=price,
            currency=currency,
            features=features or []
        )
        
        self._templates[template.id] = template
        return template
    
    def get_templates(self, active_only: bool = True) -> List[PackageTemplate]:
        """Get all package templates"""
        templates = list(self._templates.values())
        if active_only:
            templates = [t for t in templates if t.is_active]
        return sorted(templates, key=lambda t: t.price)
    
    def purchase_package(self, client_id: str, template_id: str,
                        payment_amount: Optional[float] = None) -> ClientPackage:
        """Purchase a package for a client"""
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Package template {template_id} not found")
        
        if not template.is_active:
            raise ValueError("Package template is not active")
        
        # Calculate expiry date
        expiry = None
        if template.duration_days > 0:
            expiry = datetime.now() + timedelta(days=template.duration_days)
        
        client_package = ClientPackage(
            client_id=client_id,
            template_id=template_id,
            name=template.name,
            total_sessions=template.total_sessions,
            expiry_date=expiry,
            price_paid=payment_amount or template.price
        )
        
        self._client_packages[client_package.id] = client_package
        return client_package
    
    def use_session(self, package_id: str, appointment_id: str) -> ClientPackage:
        """Use a session from a package"""
        package = self._client_packages.get(package_id)
        if not package:
            raise ValueError(f"Package {package_id} not found")
        
        if package.is_expired:
            raise ValueError("Package has expired")
        
        if package.is_depleted:
            raise ValueError("No remaining sessions in package")
        
        package.used_sessions += 1
        package.appointments.append(appointment_id)
        
        # Update status if depleted
        if package.is_depleted:
            package.status = "completed"
        
        return package
    
    def get_client_packages(self, client_id: str, 
                           active_only: bool = True) -> List[ClientPackage]:
        """Get all packages for a client"""
        packages = [
            p for p in self._client_packages.values()
            if p.client_id == client_id
        ]
        
        if active_only:
            packages = [
                p for p in packages
                if p.status == "active" and not p.is_expired and not p.is_depleted
            ]
        
        return sorted(packages, key=lambda p: p.expiry_date or datetime.max)
    
    def get_best_package_for_booking(self, client_id: str) -> Optional[ClientPackage]:
        """Find best available package for a new booking"""
        packages = self.get_client_packages(client_id, active_only=True)
        
        if not packages:
            return None
        
        # Return package with earliest expiry that has sessions
        return packages[0]
    
    def renew_package(self, package_id: str, extension_days: Optional[int] = None) -> ClientPackage:
        """Renew or extend a package"""
        package = self._client_packages.get(package_id)
        if not package:
            raise ValueError(f"Package {package_id} not found")
        
        template = self._templates.get(package.template_id)
        if not template:
            raise ValueError("Original template not found")
        
        # Extend expiry
        if extension_days or template.duration_days:
            days = extension_days or template.duration_days
            if package.expiry_date:
                package.expiry_date = package.expiry_date + timedelta(days=days)
            else:
                package.expiry_date = datetime.now() + timedelta(days=days)
        
        # Reset if completed
        if package.status == "completed":
            package.status = "active"
            package.used_sessions = 0
            package.appointments = []
        
        package.start_date = datetime.now()
        
        return package
    
    def get_package_stats(self) -> Dict:
        """Get package usage statistics"""
        total_packages = len(self._client_packages)
        active_packages = sum(1 for p in self._client_packages.values() if p.status == "active")
        expired_packages = sum(1 for p in self._client_packages.values() if p.is_expired)
        depleted_packages = sum(1 for p in self._client_packages.values() if p.is_depleted)
        
        total_revenue = sum(p.price_paid for p in self._client_packages.values())
        
        # Usage rate
        total_sessions_sold = sum(p.total_sessions for p in self._client_packages.values() if p.total_sessions > 0)
        total_sessions_used = sum(p.used_sessions for p in self._client_packages.values())
        usage_rate = (total_sessions_used / total_sessions_sold * 100) if total_sessions_sold > 0 else 0
        
        return {
            "total_packages_sold": total_packages,
            "active_packages": active_packages,
            "expired_packages": expired_packages,
            "depleted_packages": depleted_packages,
            "total_revenue": total_revenue,
            "total_sessions_sold": total_sessions_sold,
            "total_sessions_used": total_sessions_used,
            "usage_rate_percent": usage_rate
        }
    
    def upgrade_package(self, package_id: str, new_template_id: str,
                       additional_payment: float) -> ClientPackage:
        """Upgrade a client to a higher tier package"""
        current = self._client_packages.get(package_id)
        if not current:
            raise ValueError(f"Package {package_id} not found")
        
        new_template = self._templates.get(new_template_id)
        if not new_template:
            raise ValueError(f"Template {new_template_id} not found")
        
        # Create new upgraded package
        upgraded = ClientPackage(
            client_id=current.client_id,
            template_id=new_template_id,
            name=new_template.name,
            total_sessions=new_template.total_sessions + current.remaining_sessions,
            expiry_date=current.expiry_date,
            price_paid=current.price_paid + additional_payment,
            appointments=current.appointments.copy()
        )
        
        # Deactivate old package
        current.status = "upgraded"
        
        self._client_packages[upgraded.id] = upgraded
        return upgraded

# Singleton instance
_package_manager: Optional[PackageManager] = None

def get_package_manager() -> PackageManager:
    """Get or create singleton Package Manager instance"""
    global _package_manager
    if _package_manager is None:
        _package_manager = PackageManager()
    return _package_manager
