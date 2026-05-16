"""
API Endpoints for Tax Identifiers
UTR, VAT, NINO, PAYE, CT, Tax Codes management
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import date

from ..tax.tax_identifiers import (
    get_tax_identifier_manager,
    TaxIdentifierType,
    TaxIdentifier,
    VATRegistration,
    SelfAssessmentRecord,
    PAYERecord,
    CorporationTaxRecord,
    IdentifierStatus,
    TaxCode
)

router = APIRouter(prefix="/tax/identifiers", tags=["Tax Identifiers"])


# ==================== REQUEST MODELS ====================

class AddIdentifierRequest(BaseModel):
    identifier_type: str  # utr, vat_number, nino, paye_reference, etc.
    reference_number: str
    entity_name: str
    entity_type: str = "individual"  # individual, sole_trader, partnership, limited_company
    date_issued: Optional[date] = None
    date_registered: Optional[date] = None
    notes: str = ""


class AddVATRegistrationRequest(BaseModel):
    vat_number: str
    registration_date: Optional[date] = None
    scheme: str = "standard"
    flat_rate_percentage: Optional[Decimal] = None
    return_period: str = "quarterly"


class AddSARecordRequest(BaseModel):
    utr: str
    current_tax_year: int = 2026
    tax_calculated: Decimal = Decimal("0")
    tax_paid: Decimal = Decimal("0")


class AddPAYERecordRequest(BaseModel):
    paye_reference: str
    accounts_office_ref: str = ""
    employer_name: str = ""


class AddCTRecordRequest(BaseModel):
    ct_utr: str
    company_name: str
    company_number: str


class UpdateTaxCodeRequest(BaseModel):
    code: str
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


# ==================== ENDPOINTS ====================

@router.post("/add")
async def add_tax_identifier(req: AddIdentifierRequest):
    """Add a new tax identifier (UTR, NINO, VAT, etc.)"""
    manager = get_tax_identifier_manager()
    
    try:
        id_type = TaxIdentifierType(req.identifier_type)
    except ValueError:
        valid_types = [t.value for t in TaxIdentifierType]
        raise HTTPException(400, f"Invalid type. Options: {valid_types}")
    
    # Validate format
    if id_type == TaxIdentifierType.UTR and not manager.validate_utr(req.reference_number):
        raise HTTPException(400, "UTR must be 10 digits")
    elif id_type == TaxIdentifierType.VAT_NUMBER and not manager.validate_vat_number(req.reference_number):
        raise HTTPException(400, "VAT number must be GB + 9 digits (e.g., GB123456789)")
    elif id_type == TaxIdentifierType.NINO and not manager.validate_nino(req.reference_number):
        raise HTTPException(400, "NINO format invalid (e.g., AB123456C)")
    
    identifier = manager.add_identifier(
        identifier_type=id_type,
        reference_number=req.reference_number,
        entity_name=req.entity_name,
        entity_type=req.entity_type,
        date_issued=req.date_issued,
        date_registered=req.date_registered
    )
    
    return {
        "id": identifier.id,
        "type": identifier.identifier_type.value,
        "reference": identifier.reference_number,
        "entity": identifier.entity_name,
        "status": identifier.status.value
    }


@router.get("/list")
async def list_identifiers(identifier_type: Optional[str] = None):
    """List all tax identifiers, optionally filtered by type"""
    manager = get_tax_identifier_manager()
    
    if identifier_type:
        try:
            id_type = TaxIdentifierType(identifier_type)
            identifiers = manager.get_identifier_by_type(id_type)
        except ValueError:
            raise HTTPException(400, "Invalid identifier type")
    else:
        identifiers = list(manager.identifiers.values())
    
    return {
        "count": len(identifiers),
        "identifiers": [
            {
                "id": i.id,
                "type": i.identifier_type.value,
                "reference": i.reference_number,
                "entity": i.entity_name,
                "entity_type": i.entity_type,
                "status": i.status.value,
                "verified": i.is_verified,
                "date_registered": i.date_registered.isoformat() if i.date_registered else None
            }
            for i in identifiers
        ]
    }


@router.get("/types")
async def get_identifier_types():
    """Get all available tax identifier types"""
    return {
        "types": [
            {
                "id": t.value,
                "name": t.name.replace("_", " ").title(),
                "description": {
                    TaxIdentifierType.UTR: "Self Assessment Unique Taxpayer Reference",
                    TaxIdentifierType.NINO: "National Insurance Number",
                    TaxIdentifierType.VAT_NUMBER: "VAT Registration Number",
                    TaxIdentifierType.PAYE_REFERENCE: "Employer PAYE Reference",
                    TaxIdentifierType.ACCOUNTS_OFFICE_REF: "Accounts Office Reference (for PAYE payments)",
                    TaxIdentifierType.CORPORATION_TAX_REF: "Corporation Tax Reference",
                    TaxIdentifierType.CT_UTR: "Corporation Tax UTR",
                    TaxIdentifierType.TAX_CODE: "PAYE Tax Code",
                    TaxIdentifierType.GATEWAY_ID: "Government Gateway User ID",
                    TaxIdentifierType.AGENT_REFERENCE: "Agent/Accountant Reference",
                    TaxIdentifierType.PARTNERSHIP_UTR: "Partnership UTR",
                    TaxIdentifierType.CIS_NUMBER: "Construction Industry Scheme Number",
                    TaxIdentifierType.EORI_NUMBER: "Economic Operator Registration",
                    TaxIdentifierType.CH_NUMBER: "Companies House Number",
                    TaxIdentifierType.CHARITY_NUMBER: "Charity Commission Number",
                    TaxIdentifierType.TRUST_UTR: "Trust UTR",
                    TaxIdentifierType.IHT_REF: "Inheritance Tax Reference",
                    TaxIdentifierType.SDLT_REF: "Stamp Duty Land Tax Reference"
                }.get(t, "")
            }
            for t in TaxIdentifierType
        ]
    }


@router.get("/utr")
async def get_utr(entity_name: Optional[str] = None):
    """Get UTR (Unique Taxpayer Reference)"""
    manager = get_tax_identifier_manager()
    utr = manager.get_utr(entity_name)
    
    if not utr:
        raise HTTPException(404, "UTR not found")
    
    return {
        "utr": utr.reference_number,
        "entity": utr.entity_name,
        "status": utr.status.value,
        "verified": utr.is_verified,
        "date_registered": utr.date_registered.isoformat() if utr.date_registered else None
    }


@router.get("/nino")
async def get_nino():
    """Get National Insurance Number"""
    manager = get_tax_identifier_manager()
    nino = manager.get_nino()
    
    if not nino:
        raise HTTPException(404, "NINO not found")
    
    # Mask for security (show only last 3 chars)
    masked = "***" + nino.reference_number[-3:]
    
    return {
        "nino": masked,
        "nino_full": nino.reference_number,  # Only in secure contexts
        "entity": nino.entity_name,
        "status": nino.status.value
    }


@router.get("/vat")
async def get_vat_number(entity_name: Optional[str] = None):
    """Get VAT registration number"""
    manager = get_tax_identifier_manager()
    vat = manager.get_vat_number(entity_name)
    
    if not vat:
        raise HTTPException(404, "VAT number not found")
    
    return {
        "vat_number": vat.reference_number,
        "entity": vat.entity_name,
        "status": vat.status.value,
        "verified": vat.is_verified
    }


# ==================== VAT REGISTRATION ====================

@router.post("/vat/registration")
async def add_vat_registration(req: AddVATRegistrationRequest):
    """Add VAT registration details"""
    manager = get_tax_identifier_manager()
    
    vat_reg = VATRegistration(
        vat_number=req.vat_number,
        registration_date=req.registration_date,
        scheme=req.scheme,
        flat_rate_percentage=req.flat_rate_percentage,
        return_period=req.return_period
    )
    
    manager.add_vat_registration(vat_reg)
    
    return {
        "vat_number": req.vat_number,
        "scheme": req.scheme,
        "return_period": req.return_period,
        "status": "registered"
    }


@router.get("/vat/registrations")
async def list_vat_registrations():
    """List all VAT registrations"""
    manager = get_tax_identifier_manager()
    
    return {
        "registrations": [
            {
                "vat_number": v.vat_number,
                "registration_date": v.registration_date.isoformat() if v.registration_date else None,
                "scheme": v.scheme,
                "flat_rate_percentage": float(v.flat_rate_percentage) if v.flat_rate_percentage else None,
                "return_period": v.return_period,
                "next_return_due": v.next_return_due.isoformat() if v.next_return_due else None,
                "next_payment_due": v.next_payment_due.isoformat() if v.next_payment_due else None,
                "mtd_enabled": v.mtd_enabled,
                "status": v.status.value
            }
            for v in manager.vat_registrations.values()
        ]
    }


# ==================== SELF ASSESSMENT ====================

@router.post("/sa/record")
async def add_sa_record(req: AddSARecordRequest):
    """Add Self Assessment record"""
    manager = get_tax_identifier_manager()
    
    sa_record = SelfAssessmentRecord(
        utr=req.utr,
        current_tax_year=req.current_tax_year,
        tax_calculated=req.tax_calculated,
        tax_paid=req.tax_paid,
        tax_outstanding=req.tax_calculated - req.tax_paid
    )
    
    manager.add_sa_record(sa_record)
    
    return {
        "utr": req.utr,
        "tax_year": req.current_tax_year,
        "tax_calculated": float(req.tax_calculated),
        "tax_paid": float(req.tax_paid),
        "tax_outstanding": float(sa_record.tax_outstanding)
    }


@router.get("/sa/records")
async def list_sa_records():
    """List all Self Assessment records"""
    manager = get_tax_identifier_manager()
    
    return {
        "records": [
            {
                "utr": r.utr,
                "tax_year": r.current_tax_year,
                "filing_status": r.filing_status,
                "paper_deadline": r.paper_deadline.isoformat(),
                "online_deadline": r.online_deadline.isoformat(),
                "payment_deadline": r.payment_deadline.isoformat(),
                "tax_calculated": float(r.tax_calculated),
                "tax_paid": float(r.tax_paid),
                "tax_outstanding": float(r.tax_outstanding),
                "poa_required": r.poa_required,
                "mtd_itsa_enabled": r.mtd_itsa_enabled
            }
            for r in manager.sa_records.values()
        ]
    }


# ==================== PAYE ====================

@router.post("/paye/record")
async def add_paye_record(req: AddPAYERecordRequest):
    """Add PAYE scheme record"""
    manager = get_tax_identifier_manager()
    
    paye_record = PAYERecord(
        paye_reference=req.paye_reference,
        accounts_office_ref=req.accounts_office_ref,
        employer_name=req.employer_name
    )
    
    manager.add_paye_record(paye_record)
    
    return {
        "paye_reference": req.paye_reference,
        "accounts_office_ref": req.accounts_office_ref,
        "employer_name": req.employer_name
    }


@router.get("/paye/records")
async def list_paye_records():
    """List all PAYE schemes"""
    manager = get_tax_identifier_manager()
    
    return {
        "paye_schemes": [
            {
                "paye_reference": r.paye_reference,
                "accounts_office_ref": r.accounts_office_ref,
                "employer_name": r.employer_name,
                "scheme_type": r.scheme_type,
                "employee_count": r.employee_count,
                "rti_compliant": r.rti_compliant,
                "penalties_outstanding": float(r.penalties_outstanding)
            }
            for r in manager.paye_records.values()
        ]
    }


# ==================== CORPORATION TAX ====================

@router.post("/ct/record")
async def add_ct_record(req: AddCTRecordRequest):
    """Add Corporation Tax record"""
    manager = get_tax_identifier_manager()
    
    ct_record = CorporationTaxRecord(
        ct_utr=req.ct_utr,
        company_name=req.company_name,
        company_number=req.company_number
    )
    
    manager.add_ct_record(ct_record)
    
    return {
        "ct_utr": req.ct_utr,
        "company_name": req.company_name,
        "company_number": req.company_number
    }


@router.get("/ct/records")
async def list_ct_records():
    """List all Corporation Tax records"""
    manager = get_tax_identifier_manager()
    
    return {
        "ct_records": [
            {
                "ct_utr": r.ct_utr,
                "company_name": r.company_name,
                "company_number": r.company_number,
                "accounting_period_start": r.accounting_period_start.isoformat() if r.accounting_period_start else None,
                "accounting_period_end": r.accounting_period_end.isoformat() if r.accounting_period_end else None,
                "taxable_profits": float(r.taxable_profits),
                "ct_liability": float(r.ct_liability),
                "ct_paid": float(r.ct_paid),
                "ct_outstanding": float(r.ct_outstanding),
                "ct600_filed": r.ct600_filed,
                "payment_deadline": r.payment_deadline.isoformat() if r.payment_deadline else None
            }
            for r in manager.ct_records.values()
        ]
    }


# ==================== TAX CODES ====================

@router.post("/tax-code")
async def update_tax_code(req: UpdateTaxCodeRequest):
    """Update PAYE tax code"""
    manager = get_tax_identifier_manager()
    
    tax_code = TaxCode(
        code=req.code,
        effective_from=req.effective_from,
        effective_to=req.effective_to
    )
    
    manager.tax_codes.append(tax_code)
    
    return {
        "tax_code": req.code,
        "tax_free_amount": float(tax_code.calculate_tax_free_amount()),
        "is_emergency": tax_code.is_emergency,
        "effective_from": req.effective_from.isoformat() if req.effective_from else None
    }


@router.get("/tax-codes")
async def list_tax_codes():
    """List all tax codes"""
    manager = get_tax_identifier_manager()
    
    return {
        "tax_codes": [
            {
                "code": t.code,
                "tax_free_amount": float(t.calculate_tax_free_amount()),
                "is_emergency": t.is_emergency,
                "is_week1_month1": t.is_week1_month1,
                "effective_from": t.effective_from.isoformat() if t.effective_from else None,
                "effective_to": t.effective_to.isoformat() if t.effective_to else None
            }
            for t in manager.tax_codes
        ]
    }


# ==================== COMPLIANCE & SUMMARY ====================

@router.get("/summary")
async def get_identifiers_summary():
    """Get summary of all tax identifiers"""
    manager = get_tax_identifier_manager()
    return manager.get_all_identifiers_summary()


@router.get("/compliance")
async def get_compliance_summary():
    """Get tax compliance overview"""
    manager = get_tax_identifier_manager()
    return manager.get_compliance_summary()


@router.get("/validate/{identifier_type}")
async def validate_identifier(identifier_type: str, value: str):
    """Validate a tax identifier format"""
    manager = get_tax_identifier_manager()
    
    is_valid = False
    if identifier_type == "utr":
        is_valid = manager.validate_utr(value)
    elif identifier_type == "vat":
        is_valid = manager.validate_vat_number(value)
    elif identifier_type == "nino":
        is_valid = manager.validate_nino(value)
    else:
        raise HTTPException(400, "Unknown identifier type. Use: utr, vat, nino")
    
    return {
        "identifier_type": identifier_type,
        "value": value,
        "valid": is_valid,
        "format": {
            "utr": "10 digits (e.g., 1234567890)",
            "vat": "GB + 9 digits (e.g., GB123456789)",
            "nino": "2 letters + 6 digits + 1 letter (e.g., AB123456C)"
        }.get(identifier_type, "")
    }
