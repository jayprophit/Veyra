"""
International Tax API Endpoints
================================
Multi-jurisdiction tax calculation API.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal

from database_layer import DatabaseManager
from tax.international_tax_engine import (
    InternationalTaxEngine, TaxJurisdiction, TaxEvent, TaxEventType,
    calculate_uk_tax, calculate_us_tax, calculate_multi_jurisdiction_tax
)

router = APIRouter(prefix="/api/tax/international", tags=["international-tax"])

# Initialize
db = DatabaseManager()
tax_engine = InternationalTaxEngine()


# ============================================================================
# Pydantic Models
# ============================================================================

class TaxEventCreate(BaseModel):
    event_date: date
    event_type: str = Field(..., description="capital_gain, dividend, interest, etc.")
    asset: str
    amount: float
    currency: str = "USD"
    cost_basis: Optional[float] = None
    proceeds: Optional[float] = None
    source_jurisdiction: str = "US"
    reporting_jurisdiction: str = "US"
    tax_year: str
    holding_days: Optional[int] = None
    notes: Optional[str] = None


class TaxProfileUpdate(BaseModel):
    primary_residence: str = "UK"
    secondary_residences: List[str] = []
    domicile: Optional[str] = None
    us_citizen: bool = False
    us_green_card: bool = False
    tax_id_numbers: Dict[str, str] = {}
    fatca_compliant: bool = False
    crs_compliant: bool = False


class TaxCalculationRequest(BaseModel):
    jurisdictions: List[str] = Field(..., description="List of jurisdiction codes: UK, US, DE, CA, etc.")
    tax_year: str
    cost_basis_method: str = "fifo"


class ExchangeRateAdd(BaseModel):
    rate_date: date
    from_currency: str
    to_currency: str
    rate: float
    source: str = "ECB"


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/events", summary="Add a taxable event")
async def add_tax_event(user_id: str, event: TaxEventCreate):
    """Add a taxable event for any jurisdiction."""
    try:
        event_id = db.add_tax_event(
            user_id=user_id,
            event_date=event.event_date.isoformat(),
            event_type=event.event_type,
            asset=event.asset,
            amount=event.amount,
            currency=event.currency,
            cost_basis=event.cost_basis,
            proceeds=event.proceeds,
            source_jurisdiction=event.source_jurisdiction,
            reporting_jurisdiction=event.reporting_jurisdiction,
            tax_year=event.tax_year,
            holding_days=event.holding_days,
            notes=event.notes
        )
        
        return {
            "status": "created",
            "event_id": event_id,
            "message": f"Tax event added for {event.reporting_jurisdiction}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events", summary="Get tax events")
async def get_tax_events(
    user_id: str,
    jurisdiction: Optional[str] = None,
    tax_year: Optional[str] = None,
    event_type: Optional[str] = None
):
    """Get tax events with optional filtering."""
    try:
        events = db.get_tax_events(
            user_id=user_id,
            jurisdiction=jurisdiction,
            tax_year=tax_year,
            event_type=event_type
        )
        return {
            "events": events,
            "count": len(events),
            "filters": {
                "jurisdiction": jurisdiction,
                "tax_year": tax_year,
                "event_type": event_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate", summary="Calculate tax for multiple jurisdictions")
async def calculate_tax(user_id: str, request: TaxCalculationRequest):
    """Calculate tax liability for specified jurisdictions."""
    try:
        # Get tax events for user
        events_data = db.get_tax_events(user_id=user_id, tax_year=request.tax_year)
        
        # Convert to TaxEvent objects
        events = []
        for e in events_data:
            events.append(TaxEvent(
                id=str(e['id']),
                user_id=e['user_id'],
                date=date.fromisoformat(e['event_date']),
                event_type=TaxEventType(e['event_type']),
                asset=e['asset'],
                amount=Decimal(str(e['amount'])),
                currency=e['currency'],
                cost_basis=Decimal(str(e['cost_basis'])) if e['cost_basis'] else None,
                proceeds=Decimal(str(e['proceeds'])) if e['proceeds'] else None,
                source_jurisdiction=TaxJurisdiction(e['source_jurisdiction']),
                reporting_jurisdiction=TaxJurisdiction(e['reporting_jurisdiction']),
                tax_year=e['tax_year'],
                metadata={'holding_days': e.get('holding_days', 0)}
            ))
        
        # Convert jurisdiction strings to enums
        jurisdictions = [TaxJurisdiction(j.lower()) for j in request.jurisdictions]
        
        # Calculate for all jurisdictions
        results = tax_engine.calculate_all_taxes(
            events, request.tax_year, jurisdictions, request.cost_basis_method
        )
        
        # Save calculations to database
        for jurisdiction, result in results.items():
            db.save_tax_calculation(
                user_id=user_id,
                jurisdiction=jurisdiction.value,
                tax_year=request.tax_year,
                total_gains=float(result.total_taxable_gain),
                total_losses=float(result.total_allowable_loss),
                net_taxable_gain=float(result.net_taxable_gain),
                tax_due=float(result.tax_due),
                currency=result.currency,
                effective_rate=float(result.effective_tax_rate),
                allowance_used=float(result.allowance_used),
                allowance_remaining=float(result.allowance_remaining),
                short_term_gains=float(result.short_term_gains),
                long_term_gains=float(result.long_term_gains)
            )
        
        # Generate summary
        summary = tax_engine.get_total_tax_liability(results)
        recommendations = tax_engine._generate_recommendations(results)
        
        return {
            "status": "calculated",
            "tax_year": request.tax_year,
            "jurisdictions": request.jurisdictions,
            "summary": summary,
            "recommendations": recommendations,
            "details": {
                j.value: {
                    "tax_due": float(r.tax_due),
                    "currency": r.currency,
                    "net_taxable_gain": float(r.net_taxable_gain),
                    "effective_rate": float(r.effective_tax_rate),
                    "allowance_used": float(r.allowance_used),
                    "allowance_remaining": float(r.allowance_remaining)
                }
                for j, r in results.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{tax_year}", summary="Get tax summary for year")
async def get_tax_summary(user_id: str, tax_year: str):
    """Get tax summary for all jurisdictions for a tax year."""
    try:
        summary = db.get_multi_jurisdiction_tax_summary(user_id, tax_year)
        
        # Calculate totals
        total_tax_due = sum(s['tax_due'] for s in summary.values())
        
        return {
            "tax_year": tax_year,
            "user_id": user_id,
            "jurisdictions": summary,
            "total_jurisdictions": len(summary),
            "summary": {
                "total_tax_due_all": total_tax_due,
                "currencies": list(set(s['currency'] for s in summary.values()))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calculate/{jurisdiction}/{tax_year}", summary="Calculate tax for single jurisdiction")
async def calculate_single_jurisdiction(
    user_id: str,
    jurisdiction: str,
    tax_year: str,
    cost_basis_method: str = "fifo"
):
    """Calculate tax for a single jurisdiction."""
    try:
        # Get cached calculation if available
        cached = db.get_tax_calculation(user_id, jurisdiction, tax_year)
        
        # Check if recalculation needed (older than 1 day)
        if cached:
            from datetime import datetime
            calc_date = datetime.fromisoformat(cached['calculation_date'])
            age_hours = (datetime.now() - calc_date).total_seconds() / 3600
            
            if age_hours < 24:
                return {
                    "status": "cached",
                    "jurisdiction": jurisdiction,
                    "tax_year": tax_year,
                    "calculation_date": cached['calculation_date'],
                    "result": {
                        "tax_due": cached['tax_due'],
                        "currency": cached['currency'],
                        "net_taxable_gain": cached['net_taxable_gain'],
                        "effective_rate": cached['effective_rate'],
                        "allowance_used": cached['allowance_used'],
                        "allowance_remaining": cached['allowance_remaining']
                    }
                }
        
        # Recalculate
        events_data = db.get_tax_events(
            user_id=user_id,
            jurisdiction=jurisdiction,
            tax_year=tax_year
        )
        
        if not events_data:
            return {
                "status": "no_data",
                "jurisdiction": jurisdiction,
                "tax_year": tax_year,
                "message": "No tax events found for this jurisdiction and year"
            }
        
        # Convert to TaxEvent objects
        events = []
        for e in events_data:
            events.append(TaxEvent(
                id=str(e['id']),
                user_id=e['user_id'],
                date=date.fromisoformat(e['event_date']),
                event_type=TaxEventType(e['event_type']),
                asset=e['asset'],
                amount=Decimal(str(e['amount'])),
                currency=e['currency'],
                cost_basis=Decimal(str(e['cost_basis'])) if e['cost_basis'] else None,
                proceeds=Decimal(str(e['proceeds'])) if e['proceeds'] else None,
                source_jurisdiction=TaxJurisdiction(e['source_jurisdiction']),
                reporting_jurisdiction=TaxJurisdiction(e['reporting_jurisdiction']),
                tax_year=e['tax_year'],
                metadata={'holding_days': e.get('holding_days', 0)}
            ))
        
        # Calculate
        j = TaxJurisdiction(jurisdiction.lower())
        result = tax_engine.calculate_tax_for_jurisdiction(
            j, events, tax_year, cost_basis_method
        )
        
        # Save calculation
        db.save_tax_calculation(
            user_id=user_id,
            jurisdiction=jurisdiction,
            tax_year=tax_year,
            total_gains=float(result.total_taxable_gain),
            total_losses=float(result.total_allowable_loss),
            net_taxable_gain=float(result.net_taxable_gain),
            tax_due=float(result.tax_due),
            currency=result.currency,
            effective_rate=float(result.effective_tax_rate),
            allowance_used=float(result.allowance_used),
            allowance_remaining=float(result.allowance_remaining),
            short_term_gains=float(result.short_term_gains),
            long_term_gains=float(result.long_term_gains)
        )
        
        return {
            "status": "calculated",
            "jurisdiction": jurisdiction,
            "tax_year": tax_year,
            "result": {
                "tax_due": float(result.tax_due),
                "currency": result.currency,
                "net_taxable_gain": float(result.net_taxable_gain),
                "effective_rate": float(result.effective_tax_rate),
                "allowance_used": float(result.allowance_used),
                "allowance_remaining": float(result.allowance_remaining),
                "short_term_gains": float(result.short_term_gains),
                "long_term_gains": float(result.long_term_gains)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile", summary="Set user tax profile")
async def set_tax_profile(user_id: str, profile: TaxProfileUpdate):
    """Set user's international tax profile."""
    try:
        profile_id = db.set_user_tax_profile(
            user_id=user_id,
            primary_residence=profile.primary_residence,
            secondary_residences=profile.secondary_residences,
            domicile=profile.domicile,
            us_citizen=profile.us_citizen,
            us_green_card=profile.us_green_card,
            tax_id_numbers=profile.tax_id_numbers,
            fatca_compliant=profile.fatca_compliant,
            crs_compliant=profile.crs_compliant
        )
        
        return {
            "status": "updated",
            "profile_id": profile_id,
            "primary_residence": profile.primary_residence,
            "message": "Tax profile updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", summary="Get user tax profile")
async def get_tax_profile(user_id: str):
    """Get user's international tax profile."""
    try:
        profile = db.get_user_tax_profile(user_id)
        
        if not profile:
            return {
                "status": "not_found",
                "user_id": user_id,
                "message": "No tax profile found. Please set up your profile."
            }
        
        return {
            "status": "found",
            "profile": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exchange-rates", summary="Add exchange rate")
async def add_exchange_rate(rate: ExchangeRateAdd):
    """Add currency exchange rate for historical conversion."""
    try:
        rate_id = db.add_exchange_rate(
            date=rate.rate_date.isoformat(),
            from_currency=rate.from_currency,
            to_currency=rate.to_currency,
            rate=rate.rate,
            source=rate.source
        )
        
        return {
            "status": "added",
            "rate_id": rate_id,
            "message": f"Exchange rate added: {rate.from_currency} to {rate.to_currency}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jurisdictions", summary="Get supported jurisdictions")
async def get_jurisdictions():
    """Get list of supported tax jurisdictions."""
    jurisdictions = {
        "UK": {
            "name": "United Kingdom",
            "currency": "GBP",
            "tax_year_format": "2024-25",
            "features": ["CGT", "ISA", "SIPP", "Section_104_pooling"]
        },
        "US": {
            "name": "United States",
            "currency": "USD",
            "tax_year_format": "2024",
            "features": ["Short_term_gains", "Long_term_gains", "Wash_sale_rules", "FIFO_LIFO_SpecificID"]
        },
        "DE": {
            "name": "Germany",
            "currency": "EUR",
            "tax_year_format": "2024",
            "features": ["Abgeltungssteuer", "Sparer_Pauschbetrag", "1_year_holding_exemption"]
        },
        "CA": {
            "name": "Canada",
            "currency": "CAD",
            "tax_year_format": "2024",
            "features": ["50_percent_inclusion", "Superficial_loss_rules", "Lifetime_exemption"]
        },
        "AU": {
            "name": "Australia",
            "currency": "AUD",
            "tax_year_format": "2023-24",
            "features": ["CGT_discount", "12_month_rule"]
        },
        "CH": {
            "name": "Switzerland",
            "currency": "CHF",
            "tax_year_format": "2024",
            "features": ["Wealth_tax", "Withholding_tax"]
        },
        "SG": {
            "name": "Singapore",
            "currency": "SGD",
            "tax_year_format": "2024",
            "features": ["No_CGT", "Income_tax_on_trading"]
        },
        "HK": {
            "name": "Hong Kong",
            "currency": "HKD",
            "tax_year_format": "2024-25",
            "features": ["No_CGT", "Profits_tax_if_trading"]
        }
    }
    
    return {
        "jurisdictions": jurisdictions,
        "count": len(jurisdictions),
        "supported_features": [
            "Capital_Gains_Tax",
            "Dividend_Tax",
            "Interest_Income",
            "Crypto_taxation",
            "Wash_sale_rules",
            "Tax_loss_harvesting",
            "Multi_currency_support",
            "Tax_treaty_benefits"
        ]
    }


@router.get("/treaties/{country1}/{country2}", summary="Check tax treaty benefits")
async def check_tax_treaty(country1: str, country2: str):
    """Check for tax treaty benefits between two countries."""
    try:
        j1 = TaxJurisdiction(country1.lower())
        j2 = TaxJurisdiction(country2.lower())
        
        treaty = tax_engine.check_tax_treaty_benefits(j1, j2)
        
        if treaty:
            return {
                "has_treaty": True,
                "countries": f"{country1.upper()}-{country2.upper()}",
                "benefits": treaty,
                "note": "Tax treaty benefits may apply. Consult a tax professional."
            }
        else:
            return {
                "has_treaty": False,
                "countries": f"{country1.upper()}-{country2.upper()}",
                "note": "No tax treaty information available for these jurisdictions."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API Endpoints Summary:
# POST   /api/tax/international/events              - Add tax event
# GET    /api/tax/international/events                - Get tax events
# POST   /api/tax/international/calculate             - Calculate multi-jurisdiction tax
# GET    /api/tax/international/summary/{tax_year}    - Get tax summary
# GET    /api/tax/international/calculate/{jurisdiction}/{tax_year} - Single jurisdiction
# POST   /api/tax/international/profile             - Set tax profile
# GET    /api/tax/international/profile             - Get tax profile
# POST   /api/tax/international/exchange-rates        - Add exchange rate
# GET    /api/tax/international/jurisdictions         - List supported jurisdictions
# GET    /api/tax/international/treaties/{c1}/{c2}    - Check tax treaty
