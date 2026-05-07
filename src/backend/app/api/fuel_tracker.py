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
    try:
        query = """
            SELECT m.*, v.make || ' ' || v.model AS vehicle_name
            FROM mileage_log m
            LEFT JOIN vehicles v ON m.vehicle_id = v.id
            WHERE m.user_id = $1 AND m.trip_date >= date '$tax_year-04-06'
            AND m.trip_date < date '$tax_year-04-06' + interval '1 year'
            ORDER BY m.trip_date DESC
            LIMIT $2 OFFSET $3
        """
        
        rows = await db.fetch_all(query, (user_id, limit, offset))
        
        return {
            "user_id": user_id,
            "tax_year": tax_year,
            "entries": rows,
            "total_entries": len(rows)
        }
    except Exception as e:
        logger.error(f"Error fetching mileage log: {e}")
        return {
            "user_id": user_id,
            "tax_year": tax_year,
            "entries": [],
            "total_entries": 0,
            "error": str(e)
        }


# ── Fuel Purchase Endpoints ───────────────────────────────────────

@router.post("/purchases", summary="Log a fuel purchase")
async def log_fuel_purchase(purchase: FuelPurchase, user_id: str):
    """Log a fuel fill-up. Receipt image can be uploaded separately."""
    try:
        query = """
            INSERT INTO fuel_log
            (user_id, vehicle_id, purchase_date, odometer_reading, litres,
             cost_per_litre, total_cost, fuel_type, station, receipt_path)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        
        await db.execute(query, (
            user_id, purchase.vehicle_id, purchase.purchase_date,
            purchase.odometer_reading, purchase.litres, purchase.cost_per_litre,
            purchase.total_cost, purchase.fuel_type, purchase.station, purchase.receipt_path
        ))
        
        return {"success": True, "message": "Fuel purchase logged successfully"}
    except Exception as e:
        logger.error(f"Error saving fuel purchase: {e}")
        return {"success": False, "error": str(e)}


@router.post("/purchases/{purchase_id}/receipt", summary="Upload fuel receipt")
async def upload_fuel_receipt(
    purchase_id: str,
    user_id: str,
    file: UploadFile = File(...)
):
    """Upload and store receipt image; updates fuel_log.receipt_path."""
    try:
        object_path = f"receipts/fuel/{user_id}/{purchase_id}/{file.filename}"
        
        # Simulate storage upload - in production would use actual storage service
        file_content = await file.read()
        
        # Save file locally for now
        os.makedirs(f"receipts/fuel/{user_id}", exist_ok=True)
        local_path = f"receipts/fuel/{user_id}/{purchase_id}/{file.filename}"
        
        with open(local_path, 'wb') as f:
            f.write(file_content)
        
        # Update database with local path
        update_query = """
            UPDATE fuel_log SET receipt_path = $1 WHERE id = $2
        """
        
        await db.execute(update_query, (local_path, purchase_id))
        
        return {"success": True, "receipt_path": local_path, "storage": "local"}
    except Exception as e:
        logger.error(f"Error saving receipt: {e}")
        return {"success": False, "error": str(e)}


# ── Summary & Self Assessment ─────────────────────────────────────

@router.get("/summary/{tax_year}", summary="HMRC mileage summary for Self Assessment")
async def get_mileage_summary(tax_year: str, user_id: str):
    """
    Returns year-to-date mileage data formatted for SA103 'Vehicle and travel costs'.
    Keeps HMRC tiered rates (45p/25p) correctly applied.
    tax_year format: '2026-27'
    """
    try:
        await db.execute("""REFRESH MATERIALIZED VIEW CONCURRENTLY yearly_mileage_summary""")
        
        row = await db.fetch_one(
            """SELECT * FROM yearly_mileage_summary WHERE user_id = $1""",
            user_id
        )
        
        return row if row else {"error": "No data found"}
    except Exception as e:
        logger.error(f"Error refreshing materialized view: {e}")
        return {"error": str(e)}


@router.get("/summary/{tax_year}/export", summary="Export mileage log as CSV for HMRC")
async def export_mileage_csv(tax_year: str, user_id: str):
    """
    Export full mileage log as CSV for HMRC audit.
    HMRC can request records up to 6 years after tax year end.
    """
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    # Write rows from database
    try:
        for r in rows:
            writer.writerow({
                'trip_date': r.get('trip_date', ''),
                'start_location': r.get('start_location', ''),
                'end_location': r.get('end_location', ''),
                'purpose': r.get('purpose', ''),
                'distance_miles': r.get('distance_miles', 0),
                'amount_claimable': r.get('amount_claimable', 0.45),
                'passenger_allowance': r.get('passenger_allowance', 0.05),
                'notes': r.get('notes', '')
            })
    except Exception as e:
        logger.error(f"Error writing CSV: {e}")
        raise
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=mileage-{tax_year}.csv"}
    )
