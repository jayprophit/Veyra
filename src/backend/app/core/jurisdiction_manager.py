"""
Jurisdiction Manager
Multi-jurisdiction tracking for tax, business, investments, trading
Handles UK, US, EU, and other jurisdictions
"""
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import date, datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Jurisdiction(Enum):
    """Supported jurisdictions"""
    # United Kingdom
    UK_ENGLAND = "uk_england"
    UK_SCOTLAND = "uk_scotland"  # Different tax rates
    UK_WALES = "uk_wales"
    UK_NORTHERN_IRELAND = "uk_northern_ireland"
    
    # Europe
    IRELAND = "ireland"
    GERMANY = "germany"
    FRANCE = "france"
    NETHERLANDS = "netherlands"
    SWITZERLAND = "switzerland"
    SPAIN = "spain"
    ITALY = "italy"
    PORTUGAL = "portugal"
    BELGIUM = "belgium"
    LUXEMBOURG = "luxembourg"
    
    # Americas
    USA = "usa"
    CANADA = "canada"
    BRAZIL = "brazil"
    MEXICO = "mexico"
    
    # Asia-Pacific
    AUSTRALIA = "australia"
    NEW_ZEALAND = "new_zealand"
    SINGAPORE = "singapore"
    HONG_KONG = "hong_kong"
    JAPAN = "japan"
    UAE = "uae"
    
    # Offshore
    CAYMAN_ISLANDS = "cayman_islands"
    BERMUDA = "bermuda"
    BRITISH_VIRGIN_ISLANDS = "bvi"
    JERSEY = "jersey"
    GUERNSEY = "guernsey"
    ISLE_OF_MAN = "isle_of_man"
    
    # Others
    INDIA = "india"
    SOUTH_AFRICA = "south_africa"
    

class TaxType(Enum):
    """Types of taxes across jurisdictions"""
    INCOME_TAX = "income_tax"
    CORPORATION_TAX = "corporation_tax"
    CAPITAL_GAINS_TAX = "capital_gains_tax"
    VAT = "vat"
    GST = "gst"  # Goods & Services Tax
    SALES_TAX = "sales_tax"
    WEALTH_TAX = "wealth_tax"
    INHERITANCE_TAX = "inheritance_tax"
    ESTATE_TAX = "estate_tax"
    STAMP_DUTY = "stamp_duty"
    PROPERTY_TAX = "property_tax"
    SOCIAL_SECURITY = "social_security"
    MEDICARE = "medicare"
    NI = "national_insurance"
    DIVIDEND_TAX = "dividend_tax"
    WITHHOLDING_TAX = "withholding_tax"
    CUSTOMS_DUTY = "customs_duty"
    EXCISE_DUTY = "excise_duty"
    CARBON_TAX = "carbon_tax"
    DIGITAL_SERVICES_TAX = "digital_services_tax"


@dataclass
class JurisdictionRules:
    """Tax rules for a specific jurisdiction"""
    jurisdiction: Jurisdiction
    
    # Personal tax
    personal_allowance: Optional[Decimal] = None
    income_tax_bands: List[Dict] = field(default_factory=list)
    capital_gains_allowance: Optional[Decimal] = None
    cgt_rates: List[Decimal] = field(default_factory=list)
    dividend_allowance: Optional[Decimal] = None
    dividend_tax_rates: List[Decimal] = field(default_factory=list)
    
    # Corporate tax
    corporation_tax_rate: Decimal = Decimal("0")
    small_business_rate: Optional[Decimal] = None
    small_business_threshold: Optional[Decimal] = None
    
    # VAT/GST
    vat_rate_standard: Decimal = Decimal("0")
    vat_rate_reduced: Optional[Decimal] = None
    vat_threshold: Optional[Decimal] = None
    
    # Social contributions
    social_security_employee_rate: Decimal = Decimal("0")
    social_security_employer_rate: Decimal = Decimal("0")
    
    # Property
    property_tax_rate: Optional[Decimal] = None
    stamp_duty_rates: List[Dict] = field(default_factory=list)
    
    # Other
    wealth_tax_rate: Optional[Decimal] = None
    wealth_tax_threshold: Optional[Decimal] = None
    inheritance_tax_rate: Optional[Decimal] = None
    inheritance_tax_threshold: Optional[Decimal] = None
    
    # Currency
    currency_code: str = "GBP"
    currency_symbol: str = "£"
    
    # Residency rules
    residency_days_threshold: int = 183
    statutory_residency_test: bool = False
    domicile_rules: str = ""
    
    # Reporting
    tax_year_end_month: int = 4  # April for UK
    tax_year_end_day: int = 5
    filing_deadline_months_after_year_end: int = 9


@dataclass
class MultiJurisdictionTaxRecord:
    """Tax record spanning multiple jurisdictions"""
    record_id: str
    tax_year: int
    
    # Primary jurisdiction (residency)
    primary_jurisdiction: Jurisdiction
    residency_status: str = "resident"  # resident, non-resident, domiciled, non-dom
    days_in_jurisdiction: Dict[Jurisdiction, int] = field(default_factory=dict)
    
    # Income by source jurisdiction
    employment_income: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    self_employment_income: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    investment_income: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    property_income: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    pension_income: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    foreign_income: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    
    # Capital gains by asset location
    capital_gains: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    
    # Tax paid by jurisdiction
    tax_paid: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    tax_outstanding: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    
    # Foreign tax credits
    foreign_tax_credits: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    
    # Double Taxation Relief
    dtr_claimed: Dict[Jurisdiction, Decimal] = field(default_factory=dict)
    
    # Tax treaties applied
    treaties_applied: List[str] = field(default_factory=list)
    
    # Compliance
    filings_required: List[Jurisdiction] = field(default_factory=list)
    filings_completed: List[Jurisdiction] = field(default_factory=list)


@dataclass
class CrossBorderInvestment:
    """Track cross-border investments"""
    investment_id: str
    asset_name: str
    asset_type: str  # stock, bond, property, crypto, etc.
    
    # Location
    investor_jurisdiction: Jurisdiction
    asset_jurisdiction: Jurisdiction
    intermediary_jurisdiction: Optional[Jurisdiction] = None
    
    # Investment details
    acquisition_date: Optional[date] = None
    acquisition_cost: Decimal = Decimal("0")
    acquisition_cost_local: Decimal = Decimal("0")
    acquisition_exchange_rate: Decimal = Decimal("1")
    
    current_value: Decimal = Decimal("0")
    current_value_local: Decimal = Decimal("0")
    current_exchange_rate: Decimal = Decimal("1")
    
    # Currency
    base_currency: str = "GBP"
    local_currency: str = "USD"
    
    # Tax implications
    withholding_tax_rate: Decimal = Decimal("0")
    withholding_tax_paid: Decimal = Decimal("0")
    
    # Reporting
    fatca_reportable: bool = False
    crs_reportable: bool = False
    
    # Dividends/interest
    income_received: List[Dict] = field(default_factory=list)
    
    # Status
    is_sold: bool = False
    sale_date: Optional[date] = None
    sale_proceeds: Decimal = Decimal("0")
    realised_gain_loss: Decimal = Decimal("0")


@dataclass
class TransferPricingRecord:
    """For businesses - transfer pricing documentation"""
    record_id: str
    related_party: str
    related_party_jurisdiction: Jurisdiction
    transaction_type: str  # goods, services, intangible, financing
    
    # Transaction details
    transaction_date: date
    description: str
    local_currency: str
    
    # Amounts
    amount_charged: Decimal
    arm_s_length_range_low: Decimal
    arm_s_length_range_high: Decimal
    arm_s_length_median: Decimal
    
    # Compliance
    documentation_prepared: bool = False
    documentation_date: Optional[date] = None
    method_used: str = ""  # CUP, resale price, cost plus, TNMM, profit split
    
    # Risk assessment
    risk_level: str = "low"  # low, medium, high
    expected_adjustment_risk: Decimal = Decimal("0")


@dataclass
class CurrencyExposure:
    """Track FX exposure across activities"""
    exposure_id: str
    base_currency: str = "GBP"
    
    # By purpose
    trading_exposure: Dict[str, Decimal] = field(default_factory=dict)
    investment_exposure: Dict[str, Decimal] = field(default_factory=dict)
    business_exposure: Dict[str, Decimal] = field(default_factory=dict)
    personal_exposure: Dict[str, Decimal] = field(default_factory=dict)
    
    # Total exposure by currency
    total_long: Dict[str, Decimal] = field(default_factory=dict)
    total_short: Dict[str, Decimal] = field(default_factory=dict)
    net_exposure: Dict[str, Decimal] = field(default_factory=dict)
    
    # Hedging
    hedged_amount: Dict[str, Decimal] = field(default_factory=dict)
    unhedged_exposure: Dict[str, Decimal] = field(default_factory=dict)


class JurisdictionManager:
    """Main manager for multi-jurisdiction operations"""
    
    # Pre-defined rules for major jurisdictions
    JURISDICTION_RULES = {
        Jurisdiction.UK_ENGLAND: JurisdictionRules(
            jurisdiction=Jurisdiction.UK_ENGLAND,
            personal_allowance=Decimal("12570"),
            income_tax_bands=[
                {"threshold": Decimal("0"), "rate": Decimal("0.20"), "name": "Basic"},
                {"threshold": Decimal("37700"), "rate": Decimal("0.40"), "name": "Higher"},
                {"threshold": Decimal("125140"), "rate": Decimal("0.45"), "name": "Additional"}
            ],
            capital_gains_allowance=Decimal("3000"),
            cgt_rates=[Decimal("0.10"), Decimal("0.20")],
            dividend_allowance=Decimal("500"),
            dividend_tax_rates=[Decimal("0.0875"), Decimal("0.3375"), Decimal("0.3935")],
            corporation_tax_rate=Decimal("0.25"),
            small_business_rate=Decimal("0.19"),
            small_business_threshold=Decimal("50000"),
            vat_rate_standard=Decimal("0.20"),
            vat_rate_reduced=Decimal("0.05"),
            vat_threshold=Decimal("85000"),
            social_security_employee_rate=Decimal("0.08"),  # NI
            social_security_employer_rate=Decimal("0.138"),
            stamp_duty_rates=[
                {"threshold": Decimal("0"), "rate": Decimal("0")},
                {"threshold": Decimal("250000"), "rate": Decimal("0.05")},
                {"threshold": Decimal("925000"), "rate": Decimal("0.10")},
                {"threshold": Decimal("1500000"), "rate": Decimal("0.12")}
            ],
            inheritance_tax_rate=Decimal("0.40"),
            inheritance_tax_threshold=Decimal("325000"),
            currency_code="GBP",
            currency_symbol="£"
        ),
        
        Jurisdiction.USA: JurisdictionRules(
            jurisdiction=Jurisdiction.USA,
            personal_allowance=None,  # Standard deduction instead
            income_tax_bands=[
                {"threshold": Decimal("0"), "rate": Decimal("0.10")},
                {"threshold": Decimal("11000"), "rate": Decimal("0.12")},
                {"threshold": Decimal("44725"), "rate": Decimal("0.22")},
                {"threshold": Decimal("95375"), "rate": Decimal("0.24")},
                {"threshold": Decimal("182100"), "rate": Decimal("0.32")},
                {"threshold": Decimal("231250"), "rate": Decimal("0.35")},
                {"threshold": Decimal("578125"), "rate": Decimal("0.37")}
            ],
            capital_gains_allowance=None,
            cgt_rates=[Decimal("0.15"), Decimal("0.20")],
            corporation_tax_rate=Decimal("0.21"),
            social_security_employee_rate=Decimal("0.062"),
            social_security_employer_rate=Decimal("0.062"),
            vat_rate_standard=Decimal("0"),  # No federal VAT
            sales_tax=True,  # State-level
            estate_tax_rate=Decimal("0.40"),
            estate_tax_threshold=Decimal("11700000"),
            currency_code="USD",
            currency_symbol="$",
            tax_year_end_month=12,
            tax_year_end_day=31
        ),
        
        Jurisdiction.IRELAND: JurisdictionRules(
            jurisdiction=Jurisdiction.IRELAND,
            personal_allowance=Decimal("20000"),
            income_tax_bands=[
                {"threshold": Decimal("0"), "rate": Decimal("0.20"), "name": "Standard"},
                {"threshold": Decimal("40000"), "rate": Decimal("0.40"), "name": "Higher"}
            ],
            capital_gains_allowance=None,
            cgt_rates=[Decimal("0.33")],
            corporation_tax_rate=Decimal("0.125"),  # 12.5% for trading
            vat_rate_standard=Decimal("0.23"),
            social_security_employee_rate=Decimal("0.04"),  # PRSI
            currency_code="EUR",
            currency_symbol="€"
        ),
        
        Jurisdiction.SWITZERLAND: JurisdictionRules(
            jurisdiction=Jurisdiction.SWITZERLAND,
            wealth_tax_rate=Decimal("0.001"),  # Varies by canton
            wealth_tax_threshold=Decimal("100000"),
            currency_code="CHF",
            currency_symbol="Fr"
        ),
        
        Jurisdiction.SINGAPORE: JurisdictionRules(
            jurisdiction=Jurisdiction.SINGAPORE,
            personal_allowance=None,
            income_tax_bands=[
                {"threshold": Decimal("0"), "rate": Decimal("0")},
                {"threshold": Decimal("30000"), "rate": Decimal("0.035")},
                {"threshold": Decimal("40000"), "rate": Decimal("0.055")},
                {"threshold": Decimal("80000"), "rate": Decimal("0.07")},
                {"threshold": Decimal("120000"), "rate": Decimal("0.115")},
                {"threshold": Decimal("160000"), "rate": Decimal("0.15")},
                {"threshold": Decimal("200000"), "rate": Decimal("0.18")},
                {"threshold": Decimal("1000000"), "rate": Decimal("0.24")}
            ],
            capital_gains_allowance=None,
            cgt_rates=[Decimal("0")],  # No CGT
            dividend_allowance=None,
            dividend_tax_rates=[Decimal("0")],  # No dividend tax
            corporation_tax_rate=Decimal("0.17"),
            vat_rate_standard=Decimal("0.09"),  # GST
            currency_code="SGD",
            currency_symbol="S$",
            tax_year_end_month=12,
            tax_year_end_day=31
        ),
        
        Jurisdiction.UAE: JurisdictionRules(
            jurisdiction=Jurisdiction.UAE,
            personal_allowance=None,
            income_tax_bands=[],
            capital_gains_allowance=None,
            cgt_rates=[Decimal("0")],
            dividend_tax_rates=[Decimal("0")],
            corporation_tax_rate=Decimal("0.09"),  # New 2023
            vat_rate_standard=Decimal("0.05"),
            currency_code="AED",
            currency_symbol="AED",
            tax_year_end_month=12,
            tax_year_end_day=31
        ),
        
        Jurisdiction.CAYMAN_ISLANDS: JurisdictionRules(
            jurisdiction=Jurisdiction.CAYMAN_ISLANDS,
            income_tax_bands=[],
            cgt_rates=[Decimal("0")],
            dividend_tax_rates=[Decimal("0")],
            corporation_tax_rate=Decimal("0"),
            currency_code="KYD",
            currency_symbol="$"
        ),
    }
    
    def __init__(self):
        self.tax_records: List[MultiJurisdictionTaxRecord] = []
        self.cross_border_investments: Dict[str, CrossBorderInvestment] = {}
        self.transfer_pricing_records: List[TransferPricingRecord] = []
        self.currency_exposure: Optional[CurrencyExposure] = None
    
    def get_jurisdiction_rules(self, jurisdiction: Jurisdiction) -> Optional[JurisdictionRules]:
        """Get tax rules for jurisdiction"""
        return self.JURISDICTION_RULES.get(jurisdiction)
    
    def add_tax_record(self, record: MultiJurisdictionTaxRecord) -> None:
        """Add multi-jurisdiction tax record"""
        self.tax_records.append(record)
    
    def add_cross_border_investment(self, investment: CrossBorderInvestment) -> None:
        """Add cross-border investment"""
        self.cross_border_investments[investment.investment_id] = investment
    
    def calculate_tax_by_jurisdiction(
        self,
        jurisdiction: Jurisdiction,
        income: Decimal,
        income_type: str = "employment"
    ) -> Dict[str, Any]:
        """Calculate tax for specific jurisdiction"""
        rules = self.get_jurisdiction_rules(jurisdiction)
        if not rules:
            return {"error": "Jurisdiction rules not found"}
        
        tax_details = {
            "jurisdiction": jurisdiction.value,
            "currency": rules.currency_code,
            "income": float(income),
            "tax_breakdown": []
        }
        
        total_tax = Decimal("0")
        remaining_income = income
        
        # Apply personal allowance if available
        if rules.personal_allowance and income_type == "employment":
            allowance = min(income, rules.personal_allowance)
            remaining_income -= allowance
            tax_details["personal_allowance"] = float(allowance)
        
        # Apply tax bands
        previous_threshold = Decimal("0")
        for band in rules.income_tax_bands:
            threshold = band["threshold"]
            rate = band["rate"]
            
            if remaining_income > threshold:
                taxable_in_band = min(remaining_income - threshold, threshold - previous_threshold)
                tax_in_band = taxable_in_band * rate
                total_tax += tax_in_band
                
                tax_details["tax_breakdown"].append({
                    "band": band.get("name", f"{threshold}+"),
                    "rate": float(rate),
                    "taxable_amount": float(taxable_in_band),
                    "tax": float(tax_in_band)
                })
            
            previous_threshold = threshold
        
        tax_details["total_tax"] = float(total_tax)
        tax_details["effective_rate"] = float(total_tax / income * 100) if income > 0 else 0
        tax_details["net_income"] = float(income - total_tax)
        
        return tax_details
    
    def get_currency_exposure_summary(self) -> Dict[str, Any]:
        """Get summary of all currency exposures"""
        if not self.currency_exposure:
            return {"message": "No exposure data"}
        
        return {
            "base_currency": self.currency_exposure.base_currency,
            "trading_exposure": self.currency_exposure.trading_exposure,
            "investment_exposure": self.currency_exposure.investment_exposure,
            "business_exposure": self.currency_exposure.business_exposure,
            "net_exposure": self.currency_exposure.net_exposure,
            "unhedged_exposure": self.currency_exposure.unhedged_exposure
        }


# Global manager
_jurisdiction_manager: Optional[JurisdictionManager] = None


def get_jurisdiction_manager() -> JurisdictionManager:
    """Get or create global jurisdiction manager"""
    global _jurisdiction_manager
    if _jurisdiction_manager is None:
        _jurisdiction_manager = JurisdictionManager()
    return _jurisdiction_manager
