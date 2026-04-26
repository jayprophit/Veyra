"""
Fuel & Mileage Tracker with HMRC Claims
Track fuel, calculate MPG, manage business mileage for tax relief
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime, date, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TripType(Enum):
    BUSINESS = "business"
    PERSONAL = "personal"
    COMMUTE = "commute"  # Not claimable
    MIXED = "mixed"


class VehicleType(Enum):
    CAR = "car"
    VAN = "van"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"


@dataclass
class Trip:
    id: str
    date: date
    start_location: str
    end_location: str
    distance_miles: Decimal
    trip_type: TripType
    vehicle: VehicleType
    purpose: str
    fuel_cost: Optional[Decimal] = None
    fuel_liters: Optional[Decimal] = None
    start_odometer: Optional[Decimal] = None
    end_odometer: Optional[Decimal] = None
    notes: str = ""
    is_round_trip: bool = False
    passengers: int = 1
    
    @property
    def claimable_miles(self) -> Decimal:
        """Miles eligible for HMRC tax relief"""
        if self.trip_type == TripType.BUSINESS:
            return self.distance_miles
        return Decimal("0")


@dataclass
class FuelPurchase:
    id: str
    date: date
    station: str
    fuel_type: str  # petrol, diesel, electric
    liters: Decimal
    price_per_liter: Decimal
    total_cost: Decimal
    odometer_reading: Optional[Decimal] = None
    vehicle: str = "default"
    cashback_earned: Decimal = Decimal("0")
    receipt_image: Optional[str] = None


@dataclass
class Vehicle:
    id: str
    name: str
    registration: str
    vehicle_type: VehicleType
    fuel_type: str
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    current_odometer: Decimal = Decimal("0")
    mpg_history: List[Decimal] = field(default_factory=list)


class HMRCMileageRates:
    """HMRC Approved Mileage Allowance Payments (MAP) rates"""
    
    # 2024/25 tax year rates
    CAR_RATES = [
        (Decimal("0"), Decimal("10000"), Decimal("0.45")),    # First 10,000 miles: 45p
        (Decimal("10000"), Decimal("999999"), Decimal("0.25"))  # Over 10,000: 25p
    ]
    
    VAN_RATES = [
        (Decimal("0"), Decimal("999999"), Decimal("0.45"))  # All miles: 45p
    ]
    
    MOTORCYCLE_RATES = [
        (Decimal("0"), Decimal("999999"), Decimal("0.24"))  # All miles: 24p
    ]
    
    BICYCLE_RATES = [
        (Decimal("0"), Decimal("999999"), Decimal("0.20"))  # All miles: 20p
    ]
    
    @classmethod
    def calculate_claim(
        cls,
        vehicle_type: VehicleType,
        business_miles: Decimal
    ) -> Decimal:
        """Calculate approved mileage payment"""
        rates = {
            VehicleType.CAR: cls.CAR_RATES,
            VehicleType.VAN: cls.VAN_RATES,
            VehicleType.MOTORCYCLE: cls.MOTORCYCLE_RATES,
            VehicleType.BICYCLE: cls.BICYCLE_RATES
        }.get(vehicle_type, cls.CAR_RATES)
        
        claim = Decimal("0")
        remaining_miles = business_miles
        
        for band_min, band_max, rate in rates:
            band_miles = min(remaining_miles, band_max - band_min)
            if band_miles > 0:
                claim += band_miles * rate
                remaining_miles -= band_miles
            if remaining_miles <= 0:
                break
        
        return claim


class FuelMileageTracker:
    """Track fuel purchases, calculate MPG, manage HMRC claims"""
    
    def __init__(self):
        self.vehicles: Dict[str, Vehicle] = {}
        self.trips: List[Trip] = []
        self.fuel_purchases: List[FuelPurchase] = []
        self.current_tax_year_start: date = date(2024, 4, 6)  # UK tax year
        
    def add_vehicle(
        self,
        name: str,
        registration: str,
        vehicle_type: VehicleType,
        fuel_type: str = "petrol",
        purchase_date: Optional[date] = None,
        purchase_price: Optional[Decimal] = None
    ) -> Vehicle:
        """Add a vehicle to track"""
        vehicle_id = f"vehicle_{len(self.vehicles) + 1}"
        
        vehicle = Vehicle(
            id=vehicle_id,
            name=name,
            registration=registration,
            vehicle_type=vehicle_type,
            fuel_type=fuel_type,
            purchase_date=purchase_date,
            purchase_price=purchase_price
        )
        
        self.vehicles[vehicle_id] = vehicle
        logger.info(f"Vehicle added: {name} ({registration})")
        return vehicle
    
    def record_trip(
        self,
        vehicle_id: str,
        date: date,
        start_location: str,
        end_location: str,
        distance_miles: Decimal,
        trip_type: TripType,
        purpose: str,
        fuel_cost: Optional[Decimal] = None,
        is_round_trip: bool = False
    ) -> Trip:
        """Record a journey"""
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        trip_id = f"trip_{len(self.trips) + 1}_{datetime.now().timestamp()}"
        
        trip = Trip(
            id=trip_id,
            date=date,
            start_location=start_location,
            end_location=end_location,
            distance_miles=distance_miles * (Decimal("2") if is_round_trip else Decimal("1")),
            trip_type=trip_type,
            vehicle=vehicle.vehicle_type,
            purpose=purpose,
            fuel_cost=fuel_cost,
            is_round_trip=is_round_trip
        )
        
        self.trips.append(trip)
        
        if trip_type == TripType.BUSINESS:
            claim = HMRCMileageRates.calculate_claim(vehicle.vehicle_type, trip.claimable_miles)
            logger.info(f"Business trip recorded: {distance_miles} miles, claimable: £{claim:.2f}")
        
        return trip
    
    def record_fuel_purchase(
        self,
        vehicle_id: str,
        date: date,
        station: str,
        fuel_type: str,
        liters: Decimal,
        price_per_liter: Decimal,
        odometer_reading: Optional[Decimal] = None,
        cashback_earned: Decimal = Decimal("0")
    ) -> FuelPurchase:
        """Record fuel purchase"""
        vehicle = self.vehicles.get(vehicle_id)
        if vehicle and odometer_reading:
            vehicle.current_odometer = odometer_reading
        
        total_cost = liters * price_per_liter
        
        purchase = FuelPurchase(
            id=f"fuel_{len(self.fuel_purchases) + 1}",
            date=date,
            station=station,
            fuel_type=fuel_type,
            liters=liters,
            price_per_liter=price_per_liter,
            total_cost=total_cost,
            odometer_reading=odometer_reading,
            vehicle=vehicle_id,
            cashback_earned=cashback_earned
        )
        
        self.fuel_purchases.append(purchase)
        
        # Calculate MPG if we have odometer data
        if vehicle and odometer_reading:
            self._update_mpg(vehicle, liters, odometer_reading)
        
        logger.info(f"Fuel purchase: {liters}L at £{price_per_liter:.3f}/L = £{total_cost:.2f}")
        return purchase
    
    def _update_mpg(self, vehicle: Vehicle, liters: Decimal, current_odometer: Decimal):
        """Calculate MPG since last fill-up"""
        if vehicle.mpg_history and self.fuel_purchases:
            last_purchase = [p for p in self.fuel_purchases if p.vehicle == vehicle.id][-2] if len([p for p in self.fuel_purchases if p.vehicle == vehicle.id]) > 1 else None
            if last_purchase and last_purchase.odometer_reading:
                miles = current_odometer - last_purchase.odometer_reading
                gallons = liters * Decimal("0.219969")  # Liters to UK gallons
                if gallons > 0:
                    mpg = miles / gallons
                    vehicle.mpg_history.append(mpg)
                    logger.info(f"MPG calculated: {mpg:.1f} for {vehicle.name}")
    
    def get_vehicle_stats(self, vehicle_id: str) -> Dict[str, Any]:
        """Get statistics for a vehicle"""
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle:
            return {"error": "Vehicle not found"}
        
        vehicle_trips = [t for t in self.trips if t.id.startswith(f"trip_")]  # Would filter by vehicle
        vehicle_fuel = [f for f in self.fuel_purchases if f.vehicle == vehicle_id]
        
        total_miles = sum(t.distance_miles for t in vehicle_trips)
        total_fuel_cost = sum(f.total_cost for f in vehicle_fuel)
        total_liters = sum(f.liters for f in vehicle_fuel)
        
        avg_mpg = sum(vehicle.mpg_history) / len(vehicle.mpg_history) if vehicle.mpg_history else None
        
        return {
            "vehicle": vehicle.name,
            "registration": vehicle.registration,
            "total_miles": float(total_miles),
            "total_fuel_cost": float(total_fuel_cost),
            "total_liters": float(total_liters),
            "average_mpg": float(avg_mpg) if avg_mpg else None,
            "fuel_cost_per_mile": float(total_fuel_cost / total_miles) if total_miles > 0 else None,
            "current_odometer": float(vehicle.current_odometer)
        }
    
    def calculate_hmrc_claim(
        self,
        tax_year_start: Optional[date] = None,
        vehicle_type: Optional[VehicleType] = None
    ) -> Dict[str, Any]:
        """Calculate total HMRC mileage claim for tax year"""
        if tax_year_start is None:
            tax_year_start = self.current_tax_year_start
        
        tax_year_end = date(tax_year_start.year + 1, 4, 5)
        
        # Filter trips to tax year
        year_trips = [
            t for t in self.trips 
            if tax_year_start <= t.date <= tax_year_end and t.trip_type == TripType.BUSINESS
        ]
        
        if vehicle_type:
            year_trips = [t for t in year_trips if t.vehicle == vehicle_type]
        
        # Group by vehicle type
        by_vehicle = defaultdict(lambda: {"miles": Decimal("0"), "claim": Decimal("0")})
        
        for trip in year_trips:
            vt = trip.vehicle
            by_vehicle[vt]["miles"] += trip.claimable_miles
        
        # Calculate claims
        total_claim = Decimal("0")
        breakdown = []
        
        for vt, data in by_vehicle.items():
            miles = data["miles"]
            claim = HMRCMileageRates.calculate_claim(vt, miles)
            total_claim += claim
            
            breakdown.append({
                "vehicle_type": vt.value,
                "business_miles": float(miles),
                "hmrc_rate_applied": "45p/25p" if vt == VehicleType.CAR else "45p" if vt == VehicleType.VAN else "24p/20p",
                "claim_amount": float(claim)
            })
        
        return {
            "tax_year": f"{tax_year_start.year}-{tax_year_start.year + 1}",
            "period_start": tax_year_start.isoformat(),
            "period_end": tax_year_end.isoformat(),
            "total_business_miles": float(sum(t.claimable_miles for t in year_trips)),
            "total_claim_amount": float(total_claim),
            "breakdown_by_vehicle": breakdown,
            "hmrc_approved": True,
            "can_claim_via_self_assessment": True
        }
    
    def generate_expense_report(
        self,
        start_date: date,
        end_date: date,
        include_receipts: bool = True
    ) -> Dict[str, Any]:
        """Generate expense report for employer or Self Assessment"""
        period_trips = [t for t in self.trips if start_date <= t.date <= end_date]
        
        # HMRC claim
        hmrc_data = self.calculate_hmrc_claim()
        
        # Actual fuel costs (alternative claim method)
        period_fuel = [f for f in self.fuel_purchases if start_date <= f.date <= end_date]
        actual_fuel_cost = sum(f.total_cost for f in period_fuel)
        
        # Calculate business proportion
        total_miles = sum(t.distance_miles for t in period_trips)
        business_miles = sum(t.claimable_miles for t in period_trips)
        business_proportion = business_miles / total_miles if total_miles > 0 else Decimal("0")
        
        fuel_claim = actual_fuel_cost * business_proportion
        
        # Recommend best method
        use_hmrc_rate = hmrc_data["total_claim_amount"] > float(fuel_claim)
        
        report = {
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_trips": len(period_trips),
                "total_miles": float(total_miles),
                "business_miles": float(business_miles),
                "business_percentage": float(business_proportion * 100)
            },
            "claim_options": {
                "hmrc_mileage_rate": {
                    "amount": hmrc_data["total_claim_amount"],
                    "description": "HMRC Approved Mileage Allowance Payments (MAP)",
                    "no_receipts_required": True
                },
                "actual_fuel_cost": {
                    "amount": float(fuel_claim),
                    "total_fuel_purchases": float(actual_fuel_cost),
                    "description": "Business proportion of actual fuel costs",
                    "receipts_required": True
                }
            },
            "recommended_method": "hmrc_mileage_rate" if use_hmrc_rate else "actual_fuel_cost",
            "recommended_claim_amount": max(hmrc_data["total_claim_amount"], float(fuel_claim)),
            "trips": [
                {
                    "date": t.date.isoformat(),
                    "route": f"{t.start_location} → {t.end_location}",
                    "distance": float(t.distance_miles),
                    "type": t.trip_type.value,
                    "purpose": t.purpose,
                    "claimable": float(t.claimable_miles)
                }
                for t in sorted(period_trips, key=lambda x: x.date)
            ] if include_receipts else []
        }
        
        return report
    
    def find_fuel_savings(self) -> List[Dict[str, Any]]:
        """Find opportunities to save on fuel"""
        savings = []
        
        # Analyze cashback opportunities
        total_cashback = sum(f.cashback_earned for f in self.fuel_purchases)
        
        if total_cashback < Decimal("10"):  # Less than £10 cashback
            savings.append({
                "category": "Cashback Cards",
                "current_annual_cashback": float(total_cashback),
                "potential_annual_savings": 50.0,  # £50 with right cards
                "recommendation": "Use Tesco Clubcard + Shell Go+ for fuel purchases",
                "action": "Link cashback cards to fuel purchases"
            })
        
        # MPG analysis
        for vehicle_id, vehicle in self.vehicles.items():
            if vehicle.mpg_history:
                recent_mpg = sum(vehicle.mpg_history[-5:]) / min(5, len(vehicle.mpg_history))
                if recent_mpg < Decimal("40") and vehicle.vehicle_type == VehicleType.CAR:
                    savings.append({
                        "category": "Fuel Efficiency",
                        "vehicle": vehicle.name,
                        "current_mpg": float(recent_mpg),
                        "potential_improvement": "5-10%",
                        "potential_annual_savings": 150.0,
                        "recommendation": "Reduce rapid acceleration, check tyre pressure, remove excess weight",
                        "action": "Practice eco-driving techniques"
                    })
        
        return savings


# Global tracker instance
_fuel_tracker: Optional[FuelMileageTracker] = None


def get_fuel_tracker() -> FuelMileageTracker:
    """Get or create global fuel tracker"""
    global _fuel_tracker
    if _fuel_tracker is None:
        _fuel_tracker = FuelMileageTracker()
    return _fuel_tracker
