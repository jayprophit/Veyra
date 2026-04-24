# ================================================================
# FinOS Fuel & Mileage Tracker — Merged into Financial Master
# HMRC Mileage Allowance Payment (MAP) rates 2026/27:
#   Car/Van:     45p/mile (first 10,000) | 25p/mile (over 10,000)
#   Motorcycle:  24p/mile (all)
#   Bicycle:     20p/mile (all)
#   Passengers:  +5p/mile/passenger (employees only)
#
# Records kept for 6 years (HMRC audit requirement)
# ================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import uuid
import csv
import io

from database_layer import DatabaseManager

router = APIRouter(prefix="/api/fuel", tags=["fuel", "mileage", "vehicles"])

# Initialize database connection
db = DatabaseManager()

# HMRC rates 2026/27
HMRC_RATES = {
    "car":        {"first_10k": 0.45, "over_10k": 0.25},
    "van":        {"first_10k": 0.45, "over_10k": 0.25},
    "motorcycle": {"first_10k": 0.24, "over_10k": 0.24},
    "bicycle":    {"first_10k": 0.20, "over_10k": 0.20},
}
PASSENGER_RATE = 0.05  # per passenger per mile


# ── Request / Response Models ─────────────────────────────────────

class VehicleCreate(BaseModel):
    make: str
    model: str
    registration: Optional[str] = None
    fuel_type: Optional[str] = None
    engine_size_cc: Optional[int] = None
    year: Optional[int] = None

class MileageEntry(BaseModel):
    vehicle_id: Optional[str] = None
    trip_date: date
    start_location: str
    end_location: str
    start_postcode: Optional[str] = None
    end_postcode: Optional[str] = None
    purpose: str = Field(..., description="Business purpose of the journey")
    distance_miles: float = Field(..., gt=0)
    passengers: int = Field(default=0, ge=0)
    notes: Optional[str] = None

    @validator("trip_date")
    def date_not_future(cls, v):
        if v > date.today():
            raise ValueError("Trip date cannot be in the future")
        return v

class FuelPurchase(BaseModel):
    vehicle_id: Optional[str] = None
    purchase_date: date
    odometer_reading: int = Field(..., gt=0)
    litres: float = Field(..., gt=0)
    price_per_litre: float = Field(..., gt=0)
    total_cost: float = Field(..., gt=0)
    fuel_type: str = Field(..., pattern="^(petrol|diesel|electric|lpg|hybrid)$")
    is_full_tank: bool = False
    station: Optional[str] = None
    notes: Optional[str] = None

class MileageSummaryResponse(BaseModel):
    tax_year: str
    total_trips: int
    total_business_miles: float
    miles_at_45p: float
    miles_at_25p: float
    total_claimable: float
    total_passenger_allowance: float
    ytd_progress_pct: float  # % of 10,000-mile threshold used


# ── Vehicle Endpoints ─────────────────────────────────────────────

@router.get("/vehicles", summary="List user's vehicles")
async def list_vehicles(user_id: str):
    """Return all active vehicles for the user."""
    try:
        rows = db.conn.execute(
            """SELECT * FROM vehicles
               WHERE user_id = ? AND is_active = 1
               ORDER BY created_at DESC""",
            (user_id,)
        ).fetchall()
        return {"vehicles": [dict(row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vehicles", summary="Add a new vehicle")
async def add_vehicle(vehicle: VehicleCreate, user_id: str):
    """Add a new vehicle to track fuel and mileage."""
    try:
        cursor = db.conn.execute(
            """INSERT INTO vehicles
                (user_id, make, model, registration, fuel_type, engine_size_cc, year)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, vehicle.make, vehicle.model, vehicle.registration,
             vehicle.fuel_type, vehicle.engine_size_cc, vehicle.year)
        )
        db.conn.commit()
        return {"status": "created", "vehicle_id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Mileage Endpoints ─────────────────────────────────────────────

@router.post("/mileage", summary="Log a business mileage trip")
async def log_mileage(entry: MileageEntry, user_id: str):
    """Log a business trip for HMRC Mileage Allowance Payment claim."""
    try:
        # Get tax year start (April 6th in UK)
        today = date.today()
        tax_year_start = date(today.year if today.month >= 4 else today.year - 1, 4, 6)

        # Fetch year-to-date miles
        row = db.conn.execute(
            """SELECT COALESCE(SUM(distance_miles), 0) as ytd
               FROM mileage_log
               WHERE user_id = ? AND trip_date >= ? AND is_business = 1""",
            (user_id, tax_year_start.isoformat())
        ).fetchone()

        ytd_miles = float(dict(row)['ytd']) if row else 0.0

        # Calculate tiered rate for this specific trip
        miles_before = ytd_miles
        miles_this = entry.distance_miles
        miles_after = miles_before + miles_this
        threshold = 10_000.0

        if miles_after <= threshold:
            claimable = miles_this * 0.45
            rate_applied = "45p"
        elif miles_before >= threshold:
            claimable = miles_this * 0.25
            rate_applied = "25p"
        else:
            at_45p = (threshold - miles_before) * 0.45
            at_25p = (miles_after - threshold) * 0.25
            claimable = at_45p + at_25p
            rate_applied = "mixed"

        passenger_allowance = entry.passengers * miles_this * PASSENGER_RATE

        # Save to database
        cursor = db.conn.execute(
            """INSERT INTO mileage_log
                (user_id, vehicle_id, trip_date, start_location, end_location,
                 start_postcode, end_postcode, purpose, distance_miles,
                 passengers, is_business, amount_claimable, passenger_allowance, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, entry.vehicle_id, entry.trip_date.isoformat(), entry.start_location,
             entry.end_location, entry.start_postcode, entry.end_postcode,
             entry.purpose, entry.distance_miles, entry.passengers, True,
             round(claimable, 2), round(passenger_allowance, 2), entry.notes)
        )
        db.conn.commit()

        return {
            "status": "logged",
            "trip_id": cursor.lastrowid,
            "distance_miles": miles_this,
            "claimable_gbp": round(claimable, 2),
            "passenger_allowance_gbp": round(passenger_allowance, 2),
            "rate_applied": rate_applied,
            "ytd_business_miles": round(miles_after, 2),
            "miles_remaining_at_45p": max(0, threshold - miles_after)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mileage", summary="List mileage log entries")
async def list_mileage(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    tax_year: Optional[str] = None
):
    """Paginated mileage log. Filter by tax year (e.g. '2026-27')."""
    # TODO: Fetch from database
    # rows = await db.fetch_all(
    #     """SELECT m.*, v.make || ' ' || v.model AS vehicle_name
    #        FROM mileage_log m
    #        LEFT JOIN vehicles v ON m.vehicle_id = v.id
    #        WHERE m.user_id = $1
    #        ORDER BY m.trip_date DESC
    #        LIMIT $2 OFFSET $3""",
    #     user_id, limit, offset
    # )
    return {"trips": [], "total": 0, "message": "Integrate with your database"}


# ── Fuel Purchase Endpoints ───────────────────────────────────────

@router.post("/purchases", summary="Log a fuel purchase")
async def log_fuel_purchase(purchase: FuelPurchase, user_id: str):
    """Log a fuel fill-up. Receipt image can be uploaded separately."""
    # TODO: Save to database
    # await db.execute(
    #     """INSERT INTO fuel_log
    #            (user_id, vehicle_id, purchase_date, odometer_reading, litres,
    #             price_per_litre, total_cost, fuel_type, is_full_tank, station, notes)
    #        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)""",
    #     user_id, purchase.vehicle_id, purchase.purchase_date,
    #     purchase.odometer_reading, purchase.litres, purchase.price_per_litre,
    #     purchase.total_cost, purchase.fuel_type, purchase.is_full_tank,
    #     purchase.station, purchase.notes
    # )
    
    # Calculate MPG
    mpg = None
    if purchase.is_full_tank:
        # TODO: Fetch previous full-tank fill from database
        # prev = await db.fetch_one(...)
        # if prev:
        #     miles = purchase.odometer_reading - prev["odometer_reading"]
        #     gallons = purchase.litres / 4.54609
        #     mpg = round(miles / gallons, 1) if gallons > 0 else None
        pass

    return {"status": "logged", "mpg": mpg, "message": "Integrate with your database"}


@router.post("/purchases/{purchase_id}/receipt", summary="Upload fuel receipt")
async def upload_fuel_receipt(
    purchase_id: str,
    user_id: str,
    file: UploadFile = File(...)
):
    """Upload and store receipt image; updates fuel_log.receipt_path."""
    # TODO: Integrate with your storage (MinIO, S3, or local)
    # object_path = f"receipts/fuel/{user_id}/{purchase_id}/{file.filename}"
    # await storage.put_object("receipts", object_path, file.file, file.size)
    # await db.execute(
    #     "UPDATE fuel_log SET receipt_path = $1 WHERE id = $2 AND user_id = $3",
    #     object_path, purchase_id, user_id
    # )
    return {"status": "uploaded", "path": f"receipts/fuel/{user_id}/{purchase_id}/{file.filename}"}


# ── Summary & Self Assessment ─────────────────────────────────────

@router.get("/summary/{tax_year}", summary="HMRC mileage summary for Self Assessment")
async def get_mileage_summary(tax_year: str, user_id: str):
    """
    Returns year-to-date mileage data formatted for SA103 'Vehicle and travel costs'.
    Keeps HMRC tiered rates (45p/25p) correctly applied.
    tax_year format: '2026-27'
    """
    # TODO: Refresh materialized view
    # await db.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY yearly_mileage_summary")
    
    # TODO: Fetch from database
    # row = await db.fetch_one(
    #     "SELECT * FROM yearly_mileage_summary WHERE user_id = $1",
    #     user_id
    # )
    
    # Placeholder response
    total = 0.0
    return {
        "tax_year": tax_year,
        "total_trips": 0,
        "total_business_miles": round(total, 2),
        "miles_at_45p": round(min(total, 10000), 2),
        "miles_at_25p": round(max(0, total - 10000), 2),
        "total_claimable": 0.0,
        "total_passenger_allowance": 0.0,
        "ytd_progress_pct": round(min(100.0, (total / 10000) * 100), 1),
        "message": "Integrate with your database"
    }


@router.get("/summary/{tax_year}/export", summary="Export mileage log as CSV for HMRC")
async def export_mileage_csv(tax_year: str, user_id: str):
    """
    Export full mileage log as CSV for HMRC audit.
    HMRC can request records up to 6 years after tax year end.
    """
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    # TODO: Fetch from database
    # rows = await db.fetch_all(
    #     """SELECT trip_date, start_location, end_location, purpose,
    #               distance_miles, amount_claimable, passenger_allowance, notes
    #        FROM mileage_log
    #        WHERE user_id = $1 AND is_business = TRUE
    #        ORDER BY trip_date""",
    #     user_id
    # )
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "Date", "From", "To", "Purpose",
        "Miles", "Claimable (£)", "Passenger (£)", "Notes"
    ])
    writer.writeheader()
    
    # TODO: Write rows from database
    # for r in rows:
    #     writer.writerow({...})
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=mileage-{tax_year}.csv"}
    )
