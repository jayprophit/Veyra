"""
Tax Identifiers & References Tracker
UK tax numbers: UTR, VAT, NINO, PAYE, CT, Tax Codes
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import date, datetime
from decimal import Decimal
import re


class TaxIdentifierType(Enum):
    UTR = "utr"
    NINO = "nino"
    VAT_NUMBER = "vat_number"
    PAYE_REFERENCE = "paye_reference"
    ACCOUNTS_OFFICE_REF = "accounts_office_ref"
    CORPORATION_TAX_REF = "corporation_tax_ref"
    CT_UTR = "ct_utr"
    TAX_CODE = "tax_code"
    GATEWAY_ID = "gateway_id"
    AGENT_REFERENCE = "agent_reference"
    PARTNERSHIP_UTR = "partnership_utr"
    CIS_NUMBER = "cis_number"
    EORI_NUMBER = "eori_number"
    CH_NUMBER = "ch_number"
    CHARITY_NUMBER = "charity_number"
    TRUST_UTR = "trust_utr"
    IHT_REF = "iht_ref"
    SDLT_REF = "sdlt_ref"


class IdentifierStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CLOSED = "closed"


@dataclass
class TaxIdentifier:
    id: str
    identifier_type: TaxIdentifierType
    reference_number: str
    status: IdentifierStatus
    entity_name: str = ""
    entity_type: str = ""  # individual, sole_trader, partnership, limited_company
    date_issued: Optional[date] = None
    date_registered: Optional[date] = None
    expiry_date: Optional[date] = None
    hmrc_office_number: Optional[str] = None
    is_verified: bool = False
    verification_date: Optional[date] = None
    notes: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class TaxCode:
    code: str  # e.g., "1257L", "BR", "D0"
    base_allowance: Decimal = Decimal("0")
    is_emergency: bool = False
    is_week1_month1: bool = False
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    
    def calculate_tax_free_amount(self) -> Decimal:
        if self.code == "BR" or self.code in ["D0", "D1", "NT"]:
            return Decimal("0")
        elif self.code.startswith("K"):
            return Decimal("0")
        else:
            match = re.match(r'(\d+)', self.code)
            if match:
                return Decimal(match.group(1)) * 10
        return Decimal("0")


@dataclass
class VATRegistration:
    vat_number: str  # GB123456789
    registration_date: Optional[date] = None
    effective_date: Optional[date] = None
    scheme: str = "standard"  # standard, flat_rate, cash_accounting, annual
    flat_rate_percentage: Optional[Decimal] = None
    return_period: str = "quarterly"
    stagger_group: str = ""  # 1, 2, 3
    next_return_due: Optional[date] = None
    next_payment_due: Optional[date] = None
    mtd_enabled: bool = True
    status: IdentifierStatus = IdentifierStatus.ACTIVE
    deregistration_date: Optional[date] = None


@dataclass
class SelfAssessmentRecord:
    utr: str
    registered_for_sa: bool = False
    registration_date: Optional[date] = None
    current_tax_year: int = 2026
    filing_status: str = "not_filed"
    paper_deadline: date = field(default_factory=lambda: date(2026, 10, 31))
    online_deadline: date = field(default_factory=lambda: date(2027, 1, 31))
    payment_deadline: date = field(default_factory=lambda: date(2027, 1, 31))
    poa_required: bool = False
    poa_january: Decimal = Decimal("0")
    poa_july: Decimal = Decimal("0")
    balancing_payment: Decimal = Decimal("0")
    tax_calculated: Decimal = Decimal("0")
    tax_paid: Decimal = Decimal("0")
    tax_outstanding: Decimal = Decimal("0")
    mtd_itsa_enabled: bool = False


@dataclass
class PAYERecord:
    paye_reference: str
    accounts_office_ref: str = ""
    employer_name: str = ""
    scheme_type: str = "regular"
    employee_count: int = 0
    eps_filing_frequency: str = "monthly"
    p60_issued: bool = False
    rti_compliant: bool = True
    penalties_outstanding: Decimal = Decimal("0")


@dataclass
class CorporationTaxRecord:
    ct_utr: str
    company_name: str
    company_number: str
    accounting_period_start: Optional[date] = None
    accounting_period_end: Optional[date] = None
    taxable_profits: Decimal = Decimal("0")
    ct_liability: Decimal = Decimal("0")
    ct_paid: Decimal = Decimal("0")
    ct_outstanding: Decimal = Decimal("0")
    instalments_required: bool = False
    ct600_filed: bool = False
    filing_deadline: Optional[date] = None
    payment_deadline: Optional[date] = None


class TaxIdentifierManager:
    """Manage all tax identifiers and references"""
    
    def __init__(self):
        self.identifiers: Dict[str, TaxIdentifier] = {}
        self.tax_codes: List[TaxCode] = []
        self.vat_registrations: Dict[str, VATRegistration] = {}
        self.sa_records: Dict[str, SelfAssessmentRecord] = {}
        self.paye_records: Dict[str, PAYERecord] = {}
        self.ct_records: Dict[str, CorporationTaxRecord] = {}
    
    def add_identifier(
        self,
        identifier_type: TaxIdentifierType,
        reference_number: str,
        entity_name: str,
        entity_type: str,
        **kwargs
    ) -> TaxIdentifier:
        """Add a tax identifier"""
        identifier_id = f"tax_id_{len(self.identifiers) + 1}"
        
        identifier = TaxIdentifier(
            id=identifier_id,
            identifier_type=identifier_type,
            reference_number=reference_number,
            status=IdentifierStatus.ACTIVE,
            entity_name=entity_name,
            entity_type=entity_type,
            **kwargs
        )
        
        self.identifiers[identifier_id] = identifier
        return identifier
    
    def get_identifier_by_type(
        self,
        identifier_type: TaxIdentifierType
    ) -> List[TaxIdentifier]:
        """Get all identifiers of a specific type"""
        return [
            i for i in self.identifiers.values()
            if i.identifier_type == identifier_type
        ]
    
    def get_utr(self, entity_name: str = None) -> Optional[TaxIdentifier]:
        """Get UTR for entity"""
        utrs = self.get_identifier_by_type(TaxIdentifierType.UTR)
        if entity_name:
            for utr in utrs:
                if utr.entity_name == entity_name:
                    return utr
        return utrs[0] if utrs else None
    
    def get_vat_number(self, entity_name: str = None) -> Optional[TaxIdentifier]:
        """Get VAT number"""
        vats = self.get_identifier_by_type(TaxIdentifierType.VAT_NUMBER)
        if entity_name:
            for vat in vats:
                if vat.entity_name == entity_name:
                    return vat
        return vats[0] if vats else None
    
    def get_nino(self) -> Optional[TaxIdentifier]:
        """Get National Insurance Number"""
        ninos = self.get_identifier_by_type(TaxIdentifierType.NINO)
        return ninos[0] if ninos else None
    
    def add_vat_registration(self, vat_reg: VATRegistration) -> None:
        """Add VAT registration"""
        self.vat_registrations[vat_reg.vat_number] = vat_reg
    
    def add_sa_record(self, sa_record: SelfAssessmentRecord) -> None:
        """Add Self Assessment record"""
        self.sa_records[sa_record.utr] = sa_record
    
    def add_paye_record(self, paye_record: PAYERecord) -> None:
        """Add PAYE record"""
        self.paye_records[paye_record.paye_reference] = paye_record
    
    def add_ct_record(self, ct_record: CorporationTaxRecord) -> None:
        """Add Corporation Tax record"""
        self.ct_records[ct_record.ct_utr] = ct_record
    
    def validate_utr(self, utr: str) -> bool:
        """Validate UTR format (10 digits)"""
        return bool(re.match(r'^\d{10}$', utr))
    
    def validate_vat_number(self, vat: str) -> bool:
        """Validate UK VAT number format (GB + 9 digits)"""
        return bool(re.match(r'^GB\d{9}$', vat))
    
    def validate_nino(self, nino: str) -> bool:
        """Validate NINO format (AB123456C)"""
        return bool(re.match(r'^[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]$', nino.upper()))
    
    def get_all_identifiers_summary(self) -> Dict[str, Any]:
        """Get summary of all tax identifiers"""
        by_type = {}
        for ident in self.identifiers.values():
            type_name = ident.identifier_type.value
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append({
                "reference": ident.reference_number,
                "entity": ident.entity_name,
                "status": ident.status.value,
                "verified": ident.is_verified
            })
        
        return {
            "total_identifiers": len(self.identifiers),
            "by_type": by_type,
            "vat_registrations": len(self.vat_registrations),
            "sa_records": len(self.sa_records),
            "paye_schemes": len(self.paye_records),
            "ct_records": len(self.ct_records)
        }
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get tax compliance overview"""
        deadlines = []
        outstanding = []
        
        # Check VAT deadlines
        for vat in self.vat_registrations.values():
            if vat.next_return_due and vat.next_return_due < date.today():
                deadlines.append({
                    "type": "VAT Return",
                    "reference": vat.vat_number,
                    "due_date": vat.next_return_due.isoformat(),
                    "status": "overdue"
                })
        
        # Check SA deadlines
        for sa in self.sa_records.values():
            if sa.tax_outstanding > 0:
                outstanding.append({
                    "type": "Self Assessment",
                    "utr": sa.utr,
                    "amount": float(sa.tax_outstanding),
                    "due_date": sa.payment_deadline.isoformat()
                })
        
        return {
            "vat_registrations": len(self.vat_registrations),
            "sa_accounts": len(self.sa_records),
            "paye_schemes": len(self.paye_records),
            "ct_accounts": len(self.ct_records),
            "upcoming_deadlines": deadlines,
            "outstanding_payments": outstanding,
            "total_outstanding": sum(o["amount"] for o in outstanding)
        }


# Global manager instance
_identifier_manager: Optional[TaxIdentifierManager] = None


def get_tax_identifier_manager() -> TaxIdentifierManager:
    """Get or create global tax identifier manager"""
    global _identifier_manager
    if _identifier_manager is None:
        _identifier_manager = TaxIdentifierManager()
    return _identifier_manager
