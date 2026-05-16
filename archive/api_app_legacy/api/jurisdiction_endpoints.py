"""
Jurisdiction API Endpoints
International tax, business, and trading tracking
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import date

from ..core.jurisdiction_manager import (
    get_jurisdiction_manager,
    Jurisdiction,
    MultiJurisdictionTaxRecord,
    CrossBorderInvestment,
    TransferPricingRecord,
    CurrencyExposure
)

router = APIRouter(prefix="/jurisdiction", tags=["Multi-Jurisdiction"])


# ==================== REQUEST MODELS ====================

class TaxCalculationRequest(BaseModel):
    jurisdiction: str
    income: Decimal
    income_type: str = "employment"  # employment, self_employment, investment


class AddCrossBorderInvestmentRequest(BaseModel):
    asset_name: str
    asset_type: str
    investor_jurisdiction: str
    asset_jurisdiction: str
    base_currency: str = "GBP"
    local_currency: str = "USD"
    acquisition_cost: Decimal
    acquisition_date: Optional[date] = None


class TransferPricingRequest(BaseModel):
    related_party: str
    related_party_jurisdiction: str
    transaction_type: str
    transaction_date: date
    description: str
    amount_charged: Decimal
    arm_s_length_range_low: Decimal
    arm_s_length_range_high: Decimal
    method_used: str = "CUP"


class FXExposureRequest(BaseModel):
    base_currency: str = "GBP"
    exposures: Dict[str, Decimal]  # currency -> amount


# ==================== JURISDICTION ENDPOINTS ====================

@router.get("/list")
async def list_jurisdictions():
    """List all supported jurisdictions"""
    return {
        "jurisdictions": [
            {
                "id": j.value,
                "name": j.name.replace("_", " ").title(),
                "region": {
                    Jurisdiction.UK_ENGLAND: "United Kingdom",
                    Jurisdiction.UK_SCOTLAND: "United Kingdom",
                    Jurisdiction.USA: "Americas",
                    Jurisdiction.IRELAND: "Europe",
                    Jurisdiction.GERMANY: "Europe",
                    Jurisdiction.SINGAPORE: "Asia-Pacific",
                    Jurisdiction.UAE: "Middle East",
                    Jurisdiction.CAYMAN_ISLANDS: "Offshore"
                }.get(j, "Other")
            }
            for j in Jurisdiction
        ],
        "total": len(Jurisdiction)
    }


@router.get("/rules/{jurisdiction}")
async def get_jurisdiction_rules(jurisdiction: str):
    """Get tax rules for specific jurisdiction"""
    manager = get_jurisdiction_manager()
    
    try:
        jur = Jurisdiction(jurisdiction)
    except ValueError:
        raise HTTPException(400, "Invalid jurisdiction code")
    
    rules = manager.get_jurisdiction_rules(jur)
    if not rules:
        raise HTTPException(404, f"Rules not found for {jurisdiction}")
    
    return {
        "jurisdiction": jurisdiction,
        "currency": {
            "code": rules.currency_code,
            "symbol": rules.currency_symbol
        },
        "personal_tax": {
            "personal_allowance": float(rules.personal_allowance) if rules.personal_allowance else None,
            "income_tax_bands": rules.income_tax_bands,
            "capital_gains_allowance": float(rules.capital_gains_allowance) if rules.capital_gains_allowance else None,
            "cgt_rates": [float(r) for r in rules.cgt_rates],
            "dividend_allowance": float(rules.dividend_allowance) if rules.dividend_allowance else None,
            "dividend_tax_rates": [float(r) for r in rules.dividend_tax_rates]
        },
        "corporate_tax": {
            "main_rate": float(rules.corporation_tax_rate),
            "small_business_rate": float(rules.small_business_rate) if rules.small_business_rate else None,
            "small_business_threshold": float(rules.small_business_threshold) if rules.small_business_threshold else None
        },
        "vat_gst": {
            "standard_rate": float(rules.vat_rate_standard),
            "reduced_rate": float(rules.vat_rate_reduced) if rules.vat_rate_reduced else None,
            "registration_threshold": float(rules.vat_threshold) if rules.vat_threshold else None
        },
        "social_security": {
            "employee_rate": float(rules.social_security_employee_rate),
            "employer_rate": float(rules.social_security_employer_rate)
        },
        "wealth_tax": {
            "rate": float(rules.wealth_tax_rate) if rules.wealth_tax_rate else None,
            "threshold": float(rules.wealth_tax_threshold) if rules.wealth_tax_threshold else None
        },
        "inheritance_tax": {
            "rate": float(rules.inheritance_tax_rate) if rules.inheritance_tax_rate else None,
            "threshold": float(rules.inheritance_tax_threshold) if rules.inheritance_tax_threshold else None
        },
        "tax_year_end": f"{rules.tax_year_end_month:02d}-{rules.tax_year_end_day:02d}"
    }


@router.post("/tax/calculate")
async def calculate_jurisdiction_tax(req: TaxCalculationRequest):
    """Calculate tax for a specific jurisdiction"""
    manager = get_jurisdiction_manager()
    
    try:
        jur = Jurisdiction(req.jurisdiction)
    except ValueError:
        raise HTTPException(400, "Invalid jurisdiction")
    
    result = manager.calculate_tax_by_jurisdiction(
        jurisdiction=jur,
        income=req.income,
        income_type=req.income_type
    )
    
    return result


@router.post("/tax/compare")
async def compare_tax_across_jurisdictions(
    jurisdictions: List[str],
    income: Decimal,
    income_type: str = "employment"
):
    """Compare tax burden across multiple jurisdictions"""
    manager = get_jurisdiction_manager()
    
    comparisons = []
    for jur_code in jurisdictions:
        try:
            jur = Jurisdiction(jur_code)
            result = manager.calculate_tax_by_jurisdiction(jur, income, income_type)
            comparisons.append({
                "jurisdiction": jur_code,
                "name": jur.name.replace("_", " ").title(),
                "total_tax": result.get("total_tax"),
                "effective_rate": result.get("effective_rate"),
                "net_income": result.get("net_income")
            })
        except ValueError:
            continue
    
    # Sort by total tax
    comparisons.sort(key=lambda x: x["total_tax"])
    
    return {
        "income": float(income),
        "income_type": income_type,
        "comparisons": comparisons,
        "most_favorable": comparisons[0] if comparisons else None,
        "least_favorable": comparisons[-1] if comparisons else None
    }


# ==================== CROSS-BORDER INVESTMENTS ====================

@router.post("/investment/add")
async def add_cross_border_investment(req: AddCrossBorderInvestmentRequest):
    """Add cross-border investment tracking"""
    manager = get_jurisdiction_manager()
    
    try:
        investor_jur = Jurisdiction(req.investor_jurisdiction)
        asset_jur = Jurisdiction(req.asset_jurisdiction)
    except ValueError:
        raise HTTPException(400, "Invalid jurisdiction code")
    
    investment_id = f"cbi_{len(manager.cross_border_investments) + 1}"
    
    investment = CrossBorderInvestment(
        investment_id=investment_id,
        asset_name=req.asset_name,
        asset_type=req.asset_type,
        investor_jurisdiction=investor_jur,
        asset_jurisdiction=asset_jur,
        base_currency=req.base_currency,
        local_currency=req.local_currency,
        acquisition_cost=req.acquisition_cost,
        acquisition_cost_local=req.acquisition_cost,  # Simplified
        acquisition_exchange_rate=Decimal("1"),
        acquisition_date=req.acquisition_date
    )
    
    manager.add_cross_border_investment(investment)
    
    return {
        "investment_id": investment_id,
        "asset": req.asset_name,
        "investor_jurisdiction": req.investor_jurisdiction,
        "asset_jurisdiction": req.asset_jurisdiction,
        "acquisition_cost": float(req.acquisition_cost),
        "fatca_reportable": investment.fatca_reportable,
        "crs_reportable": investment.crs_reportable
    }


@router.get("/investments/list")
async def list_cross_border_investments(
    investor_jurisdiction: Optional[str] = None,
    asset_jurisdiction: Optional[str] = None
):
    """List cross-border investments"""
    manager = get_jurisdiction_manager()
    
    investments = list(manager.cross_border_investments.values())
    
    # Filter if specified
    if investor_jurisdiction:
        investments = [i for i in investments if i.investor_jurisdiction.value == investor_jurisdiction]
    if asset_jurisdiction:
        investments = [i for i in investments if i.asset_jurisdiction.value == asset_jurisdiction]
    
    return {
        "count": len(investments),
        "investments": [
            {
                "id": i.investment_id,
                "asset": i.asset_name,
                "type": i.asset_type,
                "investor_jurisdiction": i.investor_jurisdiction.value,
                "asset_jurisdiction": i.asset_jurisdiction.value,
                "currencies": f"{i.base_currency}/{i.local_currency}",
                "acquisition_cost_base": float(i.acquisition_cost),
                "current_value_base": float(i.current_value),
                "withholding_tax_rate": float(i.withholding_tax_rate),
                "fatca_reportable": i.fatca_reportable,
                "crs_reportable": i.crs_reportable,
                "is_sold": i.is_sold
            }
            for i in investments
        ]
    }


@router.get("/investments/summary")
async def get_cross_border_summary():
    """Get summary of all cross-border investments by jurisdiction"""
    manager = get_jurisdiction_manager()
    
    by_asset_jurisdiction = {}
    total_exposure = Decimal("0")
    
    for inv in manager.cross_border_investments.values():
        jur = inv.asset_jurisdiction.value
        if jur not in by_asset_jurisdiction:
            by_asset_jurisdiction[jur] = {"count": 0, "total_value": Decimal("0")}
        
        by_asset_jurisdiction[jur]["count"] += 1
        by_asset_jurisdiction[jur]["total_value"] += inv.current_value
        total_exposure += inv.current_value
    
    return {
        "total_investments": len(manager.cross_border_investments),
        "total_exposure": float(total_exposure),
        "by_asset_jurisdiction": {
            k: {"count": v["count"], "total_value": float(v["total_value"])}
            for k, v in by_asset_jurisdiction.items()
        },
        "reporting_required": {
            "fatca": sum(1 for i in manager.cross_border_investments.values() if i.fatca_reportable),
            "crs": sum(1 for i in manager.cross_border_investments.values() if i.crs_reportable)
        }
    }


# ==================== TRANSFER PRICING ====================

@router.post("/transfer-pricing/add")
async def add_transfer_pricing_record(req: TransferPricingRequest):
    """Add transfer pricing record for business"""
    manager = get_jurisdiction_manager()
    
    try:
        related_jur = Jurisdiction(req.related_party_jurisdiction)
    except ValueError:
        raise HTTPException(400, "Invalid jurisdiction")
    
    record_id = f"tp_{len(manager.transfer_pricing_records) + 1}"
    
    record = TransferPricingRecord(
        record_id=record_id,
        related_party=req.related_party,
        related_party_jurisdiction=related_jur,
        transaction_type=req.transaction_type,
        transaction_date=req.transaction_date,
        description=req.description,
        amount_charged=req.amount_charged,
        arm_s_length_range_low=req.arm_s_length_range_low,
        arm_s_length_range_high=req.arm_s_length_range_high,
        arm_s_length_median=(req.arm_s_length_range_low + req.arm_s_length_range_high) / 2,
        method_used=req.method_used
    )
    
    # Risk assessment
    if req.amount_charged < req.arm_s_length_range_low or req.amount_charged > req.arm_s_length_range_high:
        record.risk_level = "high"
    elif abs(req.amount_charged - record.arm_s_length_median) / record.arm_s_length_median > Decimal("0.1"):
        record.risk_level = "medium"
    else:
        record.risk_level = "low"
    
    manager.transfer_pricing_records.append(record)
    
    return {
        "record_id": record_id,
        "related_party": req.related_party,
        "jurisdiction": req.related_party_jurisdiction,
        "amount_charged": float(req.amount_charged),
        "arm_s_length_range": [float(req.arm_s_length_range_low), float(req.arm_s_length_range_high)],
        "risk_level": record.risk_level,
        "method": req.method_used
    }


@router.get("/transfer-pricing/list")
async def list_transfer_pricing_records(risk_level: Optional[str] = None):
    """List transfer pricing records"""
    manager = get_jurisdiction_manager()
    
    records = manager.transfer_pricing_records
    if risk_level:
        records = [r for r in records if r.risk_level == risk_level]
    
    return {
        "count": len(records),
        "records": [
            {
                "id": r.record_id,
                "related_party": r.related_party,
                "jurisdiction": r.related_party_jurisdiction.value,
                "transaction_type": r.transaction_type,
                "amount_charged": float(r.amount_charged),
                "arm_s_length_median": float(r.arm_s_length_median),
                "variance_from_median": float((r.amount_charged - r.arm_s_length_median) / r.arm_s_length_median * 100),
                "risk_level": r.risk_level,
                "method": r.method_used,
                "documentation_prepared": r.documentation_prepared
            }
            for r in records
        ]
    }


# ==================== CURRENCY EXPOSURE ====================

@router.post("/fx/exposure/update")
async def update_fx_exposure(req: FXExposureRequest):
    """Update FX exposure tracking"""
    manager = get_jurisdiction_manager()
    
    exposure = CurrencyExposure(
        exposure_id=f"fx_{datetime.now().timestamp()}",
        base_currency=req.base_currency,
        net_exposure=req.exposures
    )
    
    manager.currency_exposure = exposure
    
    total_long = sum(v for v in req.exposures.values() if v > 0)
    total_short = sum(abs(v) for v in req.exposures.values() if v < 0)
    
    return {
        "base_currency": req.base_currency,
        "exposures": {k: float(v) for k, v in req.exposures.items()},
        "total_long": float(total_long),
        "total_short": float(total_short),
        "net_exposure": float(total_long - total_short)
    }


@router.get("/fx/exposure/summary")
async def get_fx_exposure_summary():
    """Get FX exposure summary"""
    manager = get_jurisdiction_manager()
    
    if not manager.currency_exposure:
        return {"message": "No FX exposure data recorded"}
    
    return manager.get_currency_exposure_summary()


# ==================== COMPLIANCE ====================

@router.get("/compliance/fatca-crs")
async def get_fatca_crs_summary():
    """Get FATCA and CRS compliance summary"""
    manager = get_jurisdiction_manager()
    
    fatca_reportable = []
    crs_reportable = []
    
    for inv in manager.cross_border_investments.values():
        if inv.fatca_reportable:
            fatca_reportable.append({
                "investment_id": inv.investment_id,
                "asset": inv.asset_name,
                "jurisdiction": inv.asset_jurisdiction.value,
                "value": float(inv.current_value)
            })
        if inv.crs_reportable:
            crs_reportable.append({
                "investment_id": inv.investment_id,
                "asset": inv.asset_name,
                "jurisdiction": inv.asset_jurisdiction.value,
                "value": float(inv.current_value)
            })
    
    return {
        "fatca": {
            "reportable_accounts": len(fatca_reportable),
            "total_value": sum(a["value"] for a in fatca_reportable),
            "accounts": fatca_reportable
        },
        "crs": {
            "reportable_accounts": len(crs_reportable),
            "total_value": sum(a["value"] for a in crs_reportable),
            "accounts": crs_reportable
        }
    }


@router.get("/compliance/tax-treaties")
async def get_tax_treaty_info(
    residence: str,
    source: str
):
    """Get tax treaty information between two jurisdictions"""
    # Common treaty provisions
    treaties = {
        ("uk", "usa"): {
            "dividend_withholding_max": 15,
            "interest_withholding_max": 0,
            "royalty_withholding_max": 0,
            "cgt_article": "Article 13",
            "tie_breaker_rule": " OECD Model"
        },
        ("uk", "ireland"): {
            "dividend_withholding_max": 15,
            "interest_withholding_max": 0,
            "royalty_withholding_max": 0,
            "freedom_of_establishment": True
        },
        ("uk", "singapore"): {
            "dividend_withholding_max": 15,
            "interest_withholding_max": 10,
            "royalty_withholding_max": 8
        }
    }
    
    key = (residence.lower(), source.lower())
    reverse_key = (source.lower(), residence.lower())
    
    treaty_info = treaties.get(key) or treaties.get(reverse_key)
    
    if not treaty_info:
        return {
            "residence": residence,
            "source": source,
            "treaty_exists": False,
            "message": "No treaty information available for this jurisdiction pair"
        }
    
    return {
        "residence": residence,
        "source": source,
        "treaty_exists": True,
        "withholding_rates": {
            "dividends": treaty_info.get("dividend_withholding_max"),
            "interest": treaty_info.get("interest_withholding_max"),
            "royalties": treaty_info.get("royalty_withholding_max")
        },
        "cgt_provisions": treaty_info.get("cgt_article"),
        "notes": "Claim treaty benefits via tax return or Form W-8BEN (US)"
    }


# ==================== SUMMARY ====================

@router.get("/summary")
async def get_jurisdiction_summary():
    """Get complete multi-jurisdiction summary"""
    manager = get_jurisdiction_manager()
    
    # Tax records by jurisdiction
    tax_by_jurisdiction = {}
    for record in manager.tax_records:
        jur = record.primary_jurisdiction.value
        if jur not in tax_by_jurisdiction:
            tax_by_jurisdiction[jur] = {"tax_paid": 0, "tax_outstanding": 0}
        tax_by_jurisdiction[jur]["tax_paid"] += float(sum(record.tax_paid.values()))
        tax_by_jurisdiction[jur]["tax_outstanding"] += float(sum(record.tax_outstanding.values()))
    
    # Investments by jurisdiction
    investment_summary = {}
    for inv in manager.cross_border_investments.values():
        jur = inv.asset_jurisdiction.value
        if jur not in investment_summary:
            investment_summary[jur] = {"count": 0, "value": 0}
        investment_summary[jur]["count"] += 1
        investment_summary[jur]["value"] += float(inv.current_value)
    
    return {
        "tracked_jurisdictions": len(tax_by_jurisdiction),
        "primary_residence": manager.tax_records[0].primary_jurisdiction.value if manager.tax_records else None,
        "tax_summary": tax_by_jurisdiction,
        "investment_summary": investment_summary,
        "transfer_pricing_records": len(manager.transfer_pricing_records),
        "cross_border_investments": len(manager.cross_border_investments),
        "fx_exposure_tracked": manager.currency_exposure is not None
    }
