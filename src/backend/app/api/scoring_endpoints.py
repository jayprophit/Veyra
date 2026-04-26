"""
Scoring Systems API Endpoints
Credit Score, Fuel/Mileage, and Financial Behavior Scoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import date

from ..personal.credit_score_tracker import get_credit_tracker, CreditAgency
from ..personal.fuel_mileage_tracker import get_fuel_tracker, TripType, VehicleType
from ..personal.financial_behavior_score import get_behavior_scorer, ScoreCategory
from ..personal.security_score import get_security_manager

router = APIRouter(prefix="/scoring", tags=["Personal Scoring Systems"])


# ==================== CREDIT SCORE ENDPOINTS ====================

class AddScoreRequest(BaseModel):
    agency: str  # experian, equifax, transunion
    score: int
    factors: Optional[Dict] = None

@router.post("/credit/add")
async def add_credit_score(req: AddScoreRequest):
    """Record new credit score reading"""
    tracker = get_credit_tracker()
    
    try:
        agency = CreditAgency(req.agency.lower())
    except ValueError:
        raise HTTPException(400, f"Invalid agency. Options: experian, equifax, transunion")
    
    score = tracker.add_score(
        agency=agency,
        score=req.score,
        factors=req.factors or {}
    )
    
    return {
        "agency": score.agency.value,
        "score": score.score,
        "max_score": score.max_score,
        "band": score.score_band,
        "change_30d": score.change_30d,
        "percentile": int(score.score / score.max_score * 100)
    }

@router.get("/credit/latest")
async def latest_credit_scores():
    """Get latest scores from all agencies"""
    tracker = get_credit_tracker()
    return tracker.get_latest_scores()

@router.get("/credit/history/{agency}")
async def credit_history(agency: str, months: int = 12):
    """Get score history for agency"""
    tracker = get_credit_tracker()
    
    try:
        agency_enum = CreditAgency(agency.lower())
    except ValueError:
        raise HTTPException(400, "Invalid agency")
    
    return {"history": tracker.get_score_history(agency_enum, months)}

@router.get("/credit/factors")
async def credit_factors():
    """Analyze credit factors"""
    tracker = get_credit_tracker()
    factors = tracker.analyze_factors()
    
    return {
        "factors": [
            {
                "category": f.category,
                "status": f.status,
                "impact": f.impact,
                "description": f.description,
                "recommendation": f.recommendation,
                "score_impact": f"{f.score_impact_estimate:+d}"
            }
            for f in factors
        ]
    }

@router.get("/credit/improvement-plan")
async def credit_improvement_plan():
    """Get personalized credit improvement plan"""
    tracker = get_credit_tracker()
    return tracker.get_improvement_plan()

@router.get("/credit/simulate/{action}")
async def simulate_credit_action(action: str):
    """Simulate impact of credit actions"""
    tracker = get_credit_tracker()
    return tracker.simulate_score_change(action)


# ==================== FUEL & MILEAGE ENDPOINTS ====================

class AddVehicleRequest(BaseModel):
    name: str
    registration: str
    vehicle_type: str  # car, van, motorcycle, bicycle
    fuel_type: str = "petrol"

class RecordTripRequest(BaseModel):
    vehicle_id: str
    date: date
    start_location: str
    end_location: str
    distance_miles: Decimal
    trip_type: str  # business, personal, commute, mixed
    purpose: str
    fuel_cost: Optional[Decimal] = None
    is_round_trip: bool = False

class RecordFuelRequest(BaseModel):
    vehicle_id: str
    date: date
    station: str
    fuel_type: str
    liters: Decimal
    price_per_liter: Decimal
    odometer: Optional[Decimal] = None
    cashback: Decimal = Decimal("0")

@router.post("/fuel/vehicle")
async def add_vehicle(req: AddVehicleRequest):
    """Add vehicle for tracking"""
    tracker = get_fuel_tracker()
    
    try:
        vtype = VehicleType(req.vehicle_type.lower())
    except ValueError:
        raise HTTPException(400, f"Invalid type. Options: {[t.value for t in VehicleType]}")
    
    vehicle = tracker.add_vehicle(
        name=req.name,
        registration=req.registration,
        vehicle_type=vtype,
        fuel_type=req.fuel_type
    )
    
    return {
        "vehicle_id": vehicle.id,
        "name": vehicle.name,
        "registration": vehicle.registration,
        "type": vehicle.vehicle_type.value
    }

@router.post("/fuel/trip")
async def record_trip(req: RecordTripRequest):
    """Record a journey"""
    tracker = get_fuel_tracker()
    
    try:
        ttype = TripType(req.trip_type.lower())
    except ValueError:
        raise HTTPException(400, f"Invalid trip type. Options: {[t.value for t in TripType]}")
    
    trip = tracker.record_trip(
        vehicle_id=req.vehicle_id,
        date=req.date,
        start_location=req.start_location,
        end_location=req.end_location,
        distance_miles=req.distance_miles,
        trip_type=ttype,
        purpose=req.purpose,
        fuel_cost=req.fuel_cost,
        is_round_trip=req.is_round_trip
    )
    
    return {
        "trip_id": trip.id,
        "distance": float(trip.distance_miles),
        "claimable_miles": float(trip.claimable_miles),
        "type": trip.trip_type.value
    }

@router.post("/fuel/purchase")
async def record_fuel(req: RecordFuelRequest):
    """Record fuel purchase"""
    tracker = get_fuel_tracker()
    
    purchase = tracker.record_fuel_purchase(
        vehicle_id=req.vehicle_id,
        date=req.date,
        station=req.station,
        fuel_type=req.fuel_type,
        liters=req.liters,
        price_per_liter=req.price_per_liter,
        odometer_reading=req.odometer,
        cashback_earned=req.cashback
    )
    
    return {
        "purchase_id": purchase.id,
        "total_cost": float(purchase.total_cost),
        "cashback_earned": float(purchase.cashback_earned)
    }

@router.get("/fuel/vehicle/{vehicle_id}/stats")
async def vehicle_stats(vehicle_id: str):
    """Get vehicle statistics"""
    tracker = get_fuel_tracker()
    return tracker.get_vehicle_stats(vehicle_id)

@router.get("/fuel/hmrc-claim")
async def calculate_hmrc_claim(tax_year: Optional[int] = None):
    """Calculate HMRC mileage claim"""
    tracker = get_fuel_tracker()
    
    tax_year_start = date(tax_year, 4, 6) if tax_year else None
    return tracker.calculate_hmrc_claim(tax_year_start)

@router.get("/fuel/expense-report")
async def expense_report(start: date, end: date):
    """Generate expense report for employer/Self Assessment"""
    tracker = get_fuel_tracker()
    return tracker.generate_expense_report(start, end)

@router.get("/fuel/savings")
async def fuel_savings():
    """Find fuel savings opportunities"""
    tracker = get_fuel_tracker()
    return {"opportunities": tracker.find_fuel_savings()}


# ==================== BEHAVIORAL SCORING ENDPOINTS ====================

class UserDataRequest(BaseModel):
    savings_balance: Decimal
    monthly_income: Decimal
    savings_rate: Decimal
    savings_consistency_months: int
    total_debt: Decimal
    debt_to_income: Decimal
    on_time_payments: int
    payoff_progress: Decimal
    dca_streak: int
    under_budget_months: int
    no_spend_streak: int
    isa_contribution: Decimal
    emergency_fund_months: Decimal

@router.post("/behavior/calculate")
async def calculate_behavior_score(req: UserDataRequest):
    """Calculate financial behavior score"""
    scorer = get_behavior_scorer()
    
    user_data = {
        "savings_balance": req.savings_balance,
        "monthly_income": req.monthly_income,
        "savings_rate": req.savings_rate,
        "savings_consistency_months": req.savings_consistency_months,
        "total_debt": req.total_debt,
        "debt_to_income": req.debt_to_income,
        "on_time_payments": req.on_time_payments,
        "payoff_progress": req.payoff_progress,
        "dca_streak": req.dca_streak,
        "under_budget_months": req.under_budget_months,
        "no_spend_streak": req.no_spend_streak,
        "isa_contribution": req.isa_contribution,
        "emergency_fund_months": req.emergency_fund_months
    }
    
    profile = scorer.calculate_overall_score(user_data)
    
    return {
        "overall_score": profile.overall_score,
        "percentile": profile.percentile,
        "level": profile.level,
        "title": profile.title,
        "xp": profile.xp,
        "components": {
            cat.value: {
                "score": comp.score,
                "weight": comp.weight,
                "details": comp.details,
                "trend": comp.trend
            }
            for cat, comp in profile.components.items()
        },
        "achievements": [
            {
                "name": a.name,
                "description": a.description,
                "tier": a.tier.value,
                "category": a.category.value,
                "icon": a.icon,
                "earned": a.date_earned.isoformat() if a.date_earned else None
            }
            for a in profile.achievements
        ],
        "streaks": [
            {
                "category": s.category,
                "current_days": s.current_days,
                "longest_days": s.longest_days,
                "description": s.description
            }
            for s in profile.streaks
        ],
        "next_goals": profile.next_goals
    }

@router.post("/behavior/streak/{category}")
async def update_streak(category: str, completed: bool):
    """Update activity streak"""
    scorer = get_behavior_scorer()
    scorer.update_streak(category, completed)
    
    return {
        "category": category,
        "completed": completed,
        "current_streak": scorer.streaks.get(category, {}).current_days if category in scorer.streaks else 0
    }

@router.get("/behavior/achievements")
async def list_achievements():
    """List all available achievements"""
    scorer = get_behavior_scorer()
    
    return {
        "total_achievements": len(scorer.achievements_db),
        "earned": len(scorer.user_achievements),
        "available": [
            {
                "id": aid,
                "name": a.name,
                "description": a.description,
                "tier": a.tier.value,
                "category": a.category.value,
                "criteria": a.criteria,
                "icon": a.icon,
                "points": a.points
            }
            for aid, a in scorer.achievements_db.items()
        ]
    }


# ==================== SECURITY SCORE ENDPOINTS ====================

class AddAccountSecurityRequest(BaseModel):
    name: str
    account_type: str
    has_2fa: bool = False
    password_strength: str = "unknown"
    uses_unique_password: bool = True
    uses_password_manager: bool = False
    has_backup_codes: bool = False

@router.post("/security/account")
async def add_security_account(req: AddAccountSecurityRequest):
    """Add account to security tracking"""
    manager = get_security_manager()
    
    account = manager.add_account(
        name=req.name,
        account_type=req.account_type,
        has_2fa=req.has_2fa,
        password_strength=req.password_strength,
        uses_unique_password=req.uses_unique_password,
        uses_password_manager=req.uses_password_manager,
        has_backup_codes=req.has_backup_codes
    )
    
    return {
        "account": account.account_name,
        "type": account.account_type,
        "security_status": "secured" if (account.has_2fa and account.has_strong_password) else "needs_improvement"
    }

@router.get("/security/score")
async def security_score():
    """Calculate security score"""
    manager = get_security_manager()
    score = manager.calculate_security_score()
    
    return {
        "overall_score": score.overall_score,
        "risk_level": score.risk_level,
        "category_scores": score.category_scores,
        "strengths": score.strengths,
        "issues": [
            {
                "category": i.category,
                "severity": i.severity.value,
                "description": i.description,
                "recommendation": i.recommendation,
                "effort": i.effort_to_fix,
                "impact": i.potential_impact
            }
            for i in score.issues
        ],
        "action_items": score.action_items,
        "last_updated": score.last_updated.isoformat()
    }

@router.post("/security/credit-freeze/{agency}")
async def freeze_credit(agency: str, freeze: bool = True):
    """Update credit freeze status"""
    manager = get_security_manager()
    
    if freeze:
        success = manager.freeze_credit(agency.lower())
    else:
        success = manager.thaw_credit(agency.lower())
    
    return {
        "agency": agency,
        "frozen": freeze,
        "success": success
    }

@router.get("/security/credit-status")
async def credit_freeze_status():
    """Get credit freeze status at all agencies"""
    manager = get_security_manager()
    return {
        "credit_frozen": manager.credit_frozen,
        "all_frozen": all(manager.credit_frozen.values()),
        "recommendation": "Freeze at all three agencies" if not all(manager.credit_frozen.values()) else "All frozen - excellent!"
    }

@router.get("/security/checklist")
async def security_checklist():
    """Get security checklist"""
    manager = get_security_manager()
    return manager.get_security_checklist()


# ==================== COMBINED DASHBOARD ====================

@router.get("/dashboard")
async def scoring_dashboard():
    """Get all scoring systems summary"""
    credit = get_credit_tracker()
    fuel = get_fuel_tracker()
    behavior = get_behavior_scorer()
    security = get_security_manager()
    
    return {
        "credit_scores": credit.get_latest_scores(),
        "fuel_summary": {
            "vehicles": len(fuel.vehicles),
            "total_trips": len(fuel.trips),
            "hmrc_claim_this_year": float(fuel.calculate_hmrc_claim().get("total_claim_amount", 0))
        },
        "behavior": {
            "achievements_earned": len(behavior.user_achievements),
            "total_available": len(behavior.achievements_db),
            "active_streaks": len([s for s in behavior.streaks.values() if s.current_days > 0])
        },
        "security": {
            "accounts_tracked": len(security.accounts),
            "overall_score": security.calculate_security_score().overall_score,
            "risk_level": security.calculate_security_score().risk_level,
            "credit_frozen_all": all(security.credit_frozen.values())
        }
    }
