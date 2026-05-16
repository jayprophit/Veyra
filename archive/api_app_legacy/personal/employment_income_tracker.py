"""
Employment & Income Type Tracker
Track multiple income sources: full-time, part-time, contract, freelance, day rate, etc.
Handles irregular income, tax implications, and budget forecasting
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime, date, timedelta
from collections import defaultdict
import calendar
import logging

logger = logging.getLogger(__name__)


class EmploymentType(Enum):
    FULL_TIME = "full_time"  # Permanent, PAYE
    PART_TIME = "part_time"  # Permanent, reduced hours
    CONTRACT = "contract"  # Fixed term, likely IR35
    FREELANCE = "freelance"  # Self-employed, project-based
    CONSULTANT = "consultant"  # Day rate, professional services
    GIG_ECONOMY = "gig_economy"  # Uber, Deliveroo, TaskRabbit
    COMMISSION = "commission"  # Sales, performance-based
    ZERO_HOURS = "zero_hours"  # Flexible, no guaranteed hours
    SEASONAL = "seasonal"  # Holiday work, harvest, etc
    TEMPORARY = "temporary"  # Agency work, short term
    CASUAL = "casual"  # As-needed, irregular
    SECOND_JOB = "second_job"  # Additional employment
    SIDE_HUSTLE = "side_hustle"  # Small business, evenings/weekends
    INVESTMENT_INCOME = "investment_income"  # Dividends, interest, rent
    PENSION = "pension"  # State, private, workplace
    BENEFITS = "benefits"  # Universal Credit, tax credits
    MATERNITY_PATERNITY = "maternity_paternity"  # Statutory pay
    SICKNESS = "sickness"  # SSP, ESA
    OTHER = "other"


class PayFrequency(Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"  # Every 2 weeks
    FOUR_WEEKLY = "four_weekly"
    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"  # Twice a month
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    IRREGULAR = "irregular"  # Project-based, commission
    ON_COMPLETION = "on_completion"
    MILESTONE = "milestone"  # Paid at project milestones


class TaxStatus(Enum):
    PAYE = "paye"  # Employer handles tax
    SELF_ASSESSMENT = "self_assessment"  # You handle tax
    IR35_INSIDE = "ir35_inside"  # Deemed employment
    IR35_OUTSIDE = "ir35_outside"  # Genuine contractor
    MIXED = "mixed"  # Some PAYE, some SA


@dataclass
class IncomeSource:
    id: str
    name: str  # e.g., "ABC Ltd Contract", "Uber Driving"
    employment_type: EmploymentType
    employer_client: str
    pay_frequency: PayFrequency
    tax_status: TaxStatus
    
    # Income details
    day_rate: Optional[Decimal] = None  # For day-rate work
    hourly_rate: Optional[Decimal] = None  # For hourly work
    annual_salary: Optional[Decimal] = None  # For salaried
    project_rate: Optional[Decimal] = None  # Per project
    commission_rate: Optional[Decimal] = None  # % of sales
    retainer_amount: Optional[Decimal] = None  # Monthly retainer
    
    # Hours/quantity
    standard_hours_per_week: Optional[Decimal] = None
    minimum_guaranteed_hours: Optional[Decimal] = None
    typical_days_per_month: Optional[int] = None
    
    # Timing
    start_date: Optional[date] = None
    end_date: Optional[date] = None  # For contracts
    notice_period_days: int = 0
    
    # Tax details
    tax_code: Optional[str] = None  # e.g., "1257L"
    ni_category: str = "A"  # National Insurance category
    vat_registered: bool = False
    vat_number: Optional[str] = None
    
    # Benefits
    includes_pension: bool = False
    employer_pension_contribution_percent: Decimal = Decimal("0")
    employee_pension_contribution_percent: Decimal = Decimal("0")
    includes_health_insurance: bool = False
    includes_bonus: bool = False
    bonus_frequency: Optional[str] = None
    typical_bonus_amount: Optional[Decimal] = None
    
    # Expenses
    deductible_expenses: List[str] = field(default_factory=list)
    travel_costs_per_month: Decimal = Decimal("0")
    equipment_costs_annual: Decimal = Decimal("0")
    
    notes: str = ""
    is_active: bool = True


@dataclass
class IncomePayment:
    id: str
    source_id: str
    date: date
    gross_amount: Decimal
    tax_deducted: Decimal
    ni_deducted: Decimal
    student_loan_deducted: Decimal = Decimal("0")
    pension_deducted: Decimal = Decimal("0")
    other_deductions: Decimal = Decimal("0")
    net_amount: Decimal
    hours_worked: Optional[Decimal] = None
    days_worked: Optional[int] = None
    description: str = ""
    is_bonus: bool = False
    is_overtime: bool = False
    period_start: Optional[date] = None
    period_end: Optional[date] = None


@dataclass
class IncomeForecast:
    source_id: str
    period_start: date
    period_end: date
    predicted_gross: Decimal
    predicted_net: Decimal
    confidence: str  # high, medium, low
    based_on: str  # average, last_period, seasonal
    factors: List[str]  # What influenced forecast


@dataclass
class IrregularIncomeBuffer:
    """Buffer calculation for irregular income"""
    target_months: int  # Months of expenses to cover
    monthly_expenses: Decimal
    current_buffer: Decimal
    buffer_progress_percent: float
    monthly_contribution_needed: Decimal
    months_until_fully_funded: Optional[int]


class EmploymentIncomeTracker:
    """Track multiple income sources and employment types"""
    
    def __init__(self):
        self.income_sources: Dict[str, IncomeSource] = {}
        self.payments: List[IncomePayment] = []
        self.forecasts: List[IncomeForecast] = []
        self.monthly_expenses_estimate: Decimal = Decimal("2000")  # Default
        
    def add_income_source(
        self,
        name: str,
        employment_type: EmploymentType,
        employer_client: str,
        pay_frequency: PayFrequency,
        tax_status: TaxStatus,
        **kwargs
    ) -> IncomeSource:
        """Add a new income source"""
        source_id = f"income_{len(self.income_sources) + 1}_{datetime.now().timestamp()}"
        
        source = IncomeSource(
            id=source_id,
            name=name,
            employment_type=employment_type,
            employer_client=employer_client,
            pay_frequency=pay_frequency,
            tax_status=tax_status,
            **kwargs
        )
        
        self.income_sources[source_id] = source
        
        logger.info(f"Income source added: {name} ({employment_type.value})")
        return source
    
    def record_payment(
        self,
        source_id: str,
        date: date,
        gross_amount: Decimal,
        tax_deducted: Decimal,
        ni_deducted: Decimal,
        net_amount: Optional[Decimal] = None,
        **kwargs
    ) -> IncomePayment:
        """Record an income payment"""
        if source_id not in self.income_sources:
            raise ValueError(f"Income source {source_id} not found")
        
        # Calculate net if not provided
        if net_amount is None:
            other_deductions = kwargs.get("student_loan_deducted", Decimal("0")) + \
                             kwargs.get("pension_deducted", Decimal("0")) + \
                             kwargs.get("other_deductions", Decimal("0"))
            net_amount = gross_amount - tax_deducted - ni_deducted - other_deductions
        
        payment = IncomePayment(
            id=f"pay_{len(self.payments) + 1}",
            source_id=source_id,
            date=date,
            gross_amount=gross_amount,
            tax_deducted=tax_deducted,
            ni_deducted=ni_deducted,
            net_amount=net_amount,
            **kwargs
        )
        
        self.payments.append(payment)
        
        source = self.income_sources[source_id]
        logger.info(f"Payment recorded: {source.name} - Gross: £{gross_amount}, Net: £{net_amount}")
        return payment
    
    def get_income_summary(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Get comprehensive income summary for period"""
        period_payments = [
            p for p in self.payments 
            if start_date <= p.date <= end_date
        ]
        
        # By source
        by_source = defaultdict(lambda: {
            "gross": Decimal("0"),
            "tax": Decimal("0"),
            "ni": Decimal("0"),
            "net": Decimal("0"),
            "payments": 0
        })
        
        for payment in period_payments:
            source = self.income_sources.get(payment.source_id)
            if source:
                by_source[source.name]["gross"] += payment.gross_amount
                by_source[source.name]["tax"] += payment.tax_deducted
                by_source[source.name]["ni"] += payment.ni_deducted
                by_source[source.name]["net"] += payment.net_amount
                by_source[source.name]["payments"] += 1
                by_source[source.name]["type"] = source.employment_type.value
                by_source[source.name]["frequency"] = source.pay_frequency.value
        
        # By employment type
        by_type = defaultdict(lambda: {"gross": Decimal("0"), "net": Decimal("0")})
        for payment in period_payments:
            source = self.income_sources.get(payment.source_id)
            if source:
                by_type[source.employment_type.value]["gross"] += payment.gross_amount
                by_type[source.employment_type.value]["net"] += payment.net_amount
        
        total_gross = sum(p.gross_amount for p in period_payments)
        total_tax = sum(p.tax_deducted for p in period_payments)
        total_ni = sum(p.ni_deducted for p in period_payments)
        total_net = sum(p.net_amount for p in period_payments)
        
        # Calculate effective tax rate
        effective_tax_rate = float(total_tax / total_gross * 100) if total_gross > 0 else 0
        effective_ni_rate = float(total_ni / total_gross * 100) if total_gross > 0 else 0
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total": {
                "gross": float(total_gross),
                "tax": float(total_tax),
                "ni": float(total_ni),
                "net": float(total_net),
                "payments_count": len(period_payments)
            },
            "effective_rates": {
                "tax_percent": round(effective_tax_rate, 1),
                "ni_percent": round(effective_ni_rate, 1),
                "total_deductions_percent": round(effective_tax_rate + effective_ni_rate, 1)
            },
            "by_source": {
                name: {
                    "gross": float(data["gross"]),
                    "net": float(data["net"]),
                    "payments": data["payments"],
                    "type": data.get("type"),
                    "frequency": data.get("frequency")
                }
                for name, data in by_source.items()
            },
            "by_employment_type": {
                emp_type: {
                    "gross": float(data["gross"]),
                    "net": float(data["net"])
                }
                for emp_type, data in by_type.items()
            }
        }
    
    def calculate_irregular_income_buffer(
        self,
        source_id: str,
        target_months: int = 3
    ) -> Optional[IrregularIncomeBuffer]:
        """Calculate how much buffer needed for irregular income"""
        source = self.income_sources.get(source_id)
        if not source:
            return None
        
        # Only relevant for irregular income
        if source.pay_frequency not in [PayFrequency.IRREGULAR, PayFrequency.ON_COMPLETION, PayFrequency.MILESTONE]:
            return None
        
        # Get last 12 months of payments
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        payments = [
            p for p in self.payments
            if p.source_id == source_id and start_date <= p.date <= end_date
        ]
        
        if not payments:
            return None
        
        total_net = sum(p.net_amount for p in payments)
        monthly_average = total_net / 12
        
        # Calculate current buffer (savings from this source)
        current_buffer = monthly_average * 2  # Assume 2 months saved (simplified)
        
        target_buffer = self.monthly_expenses_estimate * target_months
        
        progress = float(current_buffer / target_buffer * 100) if target_buffer > 0 else 0
        
        shortfall = target_buffer - current_buffer
        months_to_funded = None
        if shortfall > 0 and monthly_average > 0:
            # If saving 20% of income
            monthly_contribution = monthly_average * Decimal("0.2")
            months_to_funded = int(shortfall / monthly_contribution) if monthly_contribution > 0 else None
        
        return IrregularIncomeBuffer(
            target_months=target_months,
            monthly_expenses=self.monthly_expenses_estimate,
            current_buffer=current_buffer,
            buffer_progress_percent=progress,
            monthly_contribution_needed=monthly_average * Decimal("0.2"),
            months_until_fully_funded=months_to_funded
        )
    
    def forecast_income(
        self,
        months: int = 3
    ) -> List[IncomeForecast]:
        """Forecast income for next N months"""
        forecasts = []
        today = date.today()
        
        for source_id, source in self.income_sources.items():
            if not source.is_active:
                continue
            
            for i in range(1, months + 1):
                month_date = today + timedelta(days=30*i)
                month_start = date(month_date.year, month_date.month, 1)
                month_end = date(month_date.year, month_date.month, 
                                calendar.monthrange(month_date.year, month_date.month)[1])
                
                predicted_gross, predicted_net, confidence, factors = self._predict_source_income(
                    source, month_start, month_end
                )
                
                forecast = IncomeForecast(
                    source_id=source_id,
                    period_start=month_start,
                    period_end=month_end,
                    predicted_gross=predicted_gross,
                    predicted_net=predicted_net,
                    confidence=confidence,
                    based_on="historical_average",
                    factors=factors
                )
                
                forecasts.append(forecast)
        
        return forecasts
    
    def _predict_source_income(
        self,
        source: IncomeSource,
        period_start: date,
        period_end: date
    ) -> Tuple[Decimal, Decimal, str, List[str]]:
        """Predict income for a specific source and period"""
        factors = []
        
        # Get historical average
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        historical_payments = [
            p for p in self.payments
            if p.source_id == source.id and start_date <= p.date <= end_date
        ]
        
        if not historical_payments:
            # No history, use configured rates
            if source.day_rate and source.typical_days_per_month:
                gross = source.day_rate * source.typical_days_per_month
                factors.append(f"Based on day rate £{source.day_rate} x {source.typical_days_per_month} days")
            elif source.hourly_rate and source.standard_hours_per_week:
                gross = source.hourly_rate * source.standard_hours_per_week * 4
                factors.append(f"Based on hourly rate £{source.hourly_rate} x {source.standard_hours_per_week} hrs/week")
            elif source.annual_salary:
                gross = source.annual_salary / 12
                factors.append(f"Based on annual salary £{source.annual_salary}")
            elif source.retainer_amount:
                gross = source.retainer_amount
                factors.append(f"Based on monthly retainer")
            else:
                gross = Decimal("0")
                factors.append("No income data available")
            
            # Estimate net (rough calculation)
            net = gross * Decimal("0.75")  # Assume 25% deductions
            confidence = "low"
            
        else:
            # Use historical average
            total_gross = sum(p.gross_amount for p in historical_payments)
            total_net = sum(p.net_amount for p in historical_payments)
            
            if source.pay_frequency == PayFrequency.MONTHLY:
                gross = total_gross / 12
                net = total_net / 12
            elif source.pay_frequency == PayFrequency.WEEKLY:
                gross = total_gross / 52 * 4.33  # Convert to monthly
                net = total_net / 52 * 4.33
            elif source.pay_frequency == PayFrequency.IRREGULAR:
                gross = total_gross / 12
                net = total_net / 12
            else:
                gross = total_gross / 12
                net = total_net / 12
            
            factors.append(f"Based on {len(historical_payments)} historical payments")
            confidence = "high" if len(historical_payments) >= 6 else "medium"
        
        # Adjust for known factors
        if source.includes_bonus and source.typical_bonus_amount:
            # Check if bonus month
            if source.bonus_frequency == "quarterly" and period_start.month in [3, 6, 9, 12]:
                gross += source.typical_bonus_amount / 4  # Quarterly spread
                factors.append("Includes estimated quarterly bonus")
        
        return gross, net, confidence, factors
    
    def get_tax_summary(self, tax_year: int = 2026) -> Dict[str, Any]:
        """Get tax summary for self-assessment"""
        tax_year_start = date(tax_year, 4, 6)
        tax_year_end = date(tax_year + 1, 4, 5)
        
        # Group by tax status
        paye_income = Decimal("0")
        self_employment_income = Decimal("0")
        ir35_inside_income = Decimal("0")
        
        for payment in self.payments:
            if tax_year_start <= payment.date <= tax_year_end:
                source = self.income_sources.get(payment.source_id)
                if source:
                    if source.tax_status == TaxStatus.PAYE:
                        paye_income += payment.gross_amount
                    elif source.tax_status == TaxStatus.SELF_ASSESSMENT:
                        self_employment_income += payment.gross_amount
                    elif source.tax_status == TaxStatus.IR35_INSIDE:
                        ir35_inside_income += payment.gross_amount
        
        # Calculate tax due estimates
        paye_tax_paid = sum(
            p.tax_deducted for p in self.payments
            if tax_year_start <= p.date <= tax_year_end and
            self.income_sources.get(p.source_id, {}).tax_status == TaxStatus.PAYE
        )
        
        # Trading allowance for self-employment
        trading_allowance = min(self_employment_income, Decimal("1000"))
        taxable_self_employment = self_employment_income - trading_allowance
        
        return {
            "tax_year": f"{tax_year}-{tax_year+1}",
            "paye_employment": {
                "gross_income": float(paye_income),
                "tax_already_paid": float(paye_tax_paid),
                "status": "Tax handled by employer"
            },
            "self_employment": {
                "gross_income": float(self_employment_income),
                "trading_allowance": float(trading_allowance),
                "taxable_profit": float(taxable_self_employment),
                "status": "Report via Self Assessment",
                "class_2_ni_due": float(taxable_self_employment) > 6725,  # Small profits threshold
                "class_4_ni_estimate": float(taxable_self_employment * Decimal("0.09")) if taxable_self_employment > 9880 else 0
            },
            "ir35_contracts": {
                "gross_income": float(ir35_inside_income),
                "status": "Taxed at source like employment"
            },
            "self_assessment_required": self_employment_income > 1000 or ir35_inside_income > 0,
            "estimated_tax_due": float(taxable_self_employment * Decimal("0.2")) if taxable_self_employment > 12570 else 0
        }
    
    def get_employment_type_breakdown(self) -> Dict[str, Any]:
        """Get breakdown by employment type"""
        active_sources = [s for s in self.income_sources.values() if s.is_active]
        
        breakdown = defaultdict(lambda: {"count": 0, "monthly_gross_estimate": Decimal("0")})
        
        for source in active_sources:
            emp_type = source.employment_type.value
            breakdown[emp_type]["count"] += 1
            
            # Estimate monthly gross
            monthly = Decimal("0")
            if source.annual_salary:
                monthly = source.annual_salary / 12
            elif source.day_rate and source.typical_days_per_month:
                monthly = source.day_rate * source.typical_days_per_month
            elif source.hourly_rate and source.standard_hours_per_week:
                monthly = source.hourly_rate * source.standard_hours_per_week * 4.33
            elif source.retainer_amount:
                monthly = source.retainer_amount
            
            breakdown[emp_type]["monthly_gross_estimate"] += monthly
        
        return {
            "active_sources": len(active_sources),
            "breakdown": {
                emp_type: {
                    "count": data["count"],
                    "estimated_monthly_gross": float(data["monthly_gross_estimate"]),
                    "estimated_annual_gross": float(data["monthly_gross_estimate"] * 12)
                }
                for emp_type, data in breakdown.items()
            }
        }


# Global tracker
_employment_tracker: Optional[EmploymentIncomeTracker] = None


def get_employment_tracker() -> EmploymentIncomeTracker:
    """Get or create global employment tracker"""
    global _employment_tracker
    if _employment_tracker is None:
        _employment_tracker = EmploymentIncomeTracker()
    return _employment_tracker
