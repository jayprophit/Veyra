"""
Data Import Module
CSV templates, bank statement parsers, bulk import functionality
Supports: CSV, Excel, OFX, QIF, JSON formats
"""
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
import csv
import json
import logging
from io import StringIO
from pathlib import Path

logger = logging.getLogger(__name__)


class ImportFormat(Enum):
    CSV = "csv"
    EXCEL = "excel"
    OFX = "ofx"  # Open Financial Exchange
    QIF = "qif"  # Quicken Interchange Format
    JSON = "json"
    MT940 = "mt940"  # SWIFT bank statement
    CAMT = "camt"  # ISO 20022 XML


class BankProvider(Enum):
    BARCLAYS = "barclays"
    HSBC = "hsbc"
    LLOYDS = "lloyds"
    NATWEST = "natwest"
    SANTANDER = "santander"
    MONZO = "monzo"
    STARLING = "starling"
    REVOLUT = "revolut"
    CHASE = "chase"
    FIRST_DIRECT = "first_direct"
    METRO = "metro"
    TSB = "tsb"
    COOPERATIVE = "cooperative"
    VIRGIN_MONEY = "virgin_money"
    HALIFAX = "halifax"
    NATIONWIDE = "nationwide"
    CUSTOM = "custom"


@dataclass
class ImportTemplate:
    """Template for importing data"""
    name: str
    format: ImportFormat
    required_columns: List[str]
    optional_columns: List[str]
    column_mapping: Dict[str, str]  # Maps file column -> internal field
    date_format: str = "%Y-%m-%d"
    currency: str = "GBP"
    delimiter: str = ","
    encoding: str = "utf-8"
    has_header: bool = True
    sample_data: List[Dict] = field(default_factory=list)


@dataclass
class ImportResult:
    """Result of import operation"""
    success: bool
    records_imported: int
    records_skipped: int
    records_failed: int
    errors: List[Dict[str, Any]]
    warnings: List[str]
    import_id: str
    duration_seconds: float
    summary: Dict[str, Any]


@dataclass
class ParsedTransaction:
    """Parsed transaction from import"""
    date: date
    description: str
    amount: Decimal
    transaction_type: str  # credit, debit, transfer
    category: Optional[str] = None
    merchant: Optional[str] = None
    account: Optional[str] = None
    reference: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)


class DataImporter:
    """Main data import handler"""
    
    # Pre-defined templates for common formats
    TEMPLATES = {
        # Bank Statement Templates
        "barclays_csv": ImportTemplate(
            name="Barclays Bank Statement (CSV)",
            format=ImportFormat.CSV,
            required_columns=["Date", "Description", "Amount"],
            optional_columns=["Balance", "Category", "Reference"],
            column_mapping={
                "Date": "date",
                "Description": "description",
                "Amount": "amount",
                "Balance": "balance",
                "Category": "category",
                "Reference": "reference"
            },
            date_format="%d/%m/%Y",
            sample_data=[
                {"Date": "26/04/2026", "Description": "TESCO STORES", "Amount": "-45.50", "Balance": "2500.00"},
                {"Date": "25/04/2026", "Description": "SALARY", "Amount": "2555.00", "Balance": "2545.50"}
            ]
        ),
        
        "monzo_csv": ImportTemplate(
            name="Monzo Bank Statement (CSV)",
            format=ImportFormat.CSV,
            required_columns=["Date", "Name", "Amount", "Category"],
            optional_columns=["Notes", "Address", "Receipt"],
            column_mapping={
                "Date": "date",
                "Name": "description",
                "Amount": "amount",
                "Category": "category",
                "Notes": "notes"
            },
            date_format="%Y-%m-%d",
            sample_data=[
                {"Date": "2026-04-26", "Name": "Tesco", "Amount": "-45.50", "Category": "groceries"},
                {"Date": "2026-04-25", "Name": "Employer Ltd", "Amount": "2555.00", "Category": "income"}
            ]
        ),
        
        "starling_csv": ImportTemplate(
            name="Starling Bank Statement (CSV)",
            format=ImportFormat.CSV,
            required_columns=["Date", "Counter Party", "Amount", "Reference"],
            optional_columns=["Type", "Category", "Notes"],
            column_mapping={
                "Date": "date",
                "Counter Party": "description",
                "Amount": "amount",
                "Reference": "reference",
                "Type": "transaction_type"
            },
            date_format="%d/%m/%Y",
            sample_data=[
                {"Date": "26/04/2026", "Counter Party": "Tesco", "Amount": "-45.50", "Reference": "Card payment"},
                {"Date": "25/04/2026", "Counter Party": "Employer", "Amount": "2555.00", "Reference": "Salary"}
            ]
        ),
        
        "revolut_csv": ImportTemplate(
            name="Revolut Statement (CSV)",
            format=ImportFormat.CSV,
            required_columns=["Date", "Description", "Amount", "Currency"],
            optional_columns=["Category", "Notes", "Tags"],
            column_mapping={
                "Date": "date",
                "Description": "description",
                "Amount": "amount",
                "Category": "category"
            },
            date_format="%Y-%m-%d %H:%M:%S",
            sample_data=[
                {"Date": "2026-04-26 14:30:00", "Description": "Tesco", "Amount": "-45.50", "Currency": "GBP"}
            ]
        ),
        
        # Generic Templates
        "generic_expense_csv": ImportTemplate(
            name="Generic Expense Import (CSV)",
            format=ImportFormat.CSV,
            required_columns=["date", "amount", "category", "description"],
            optional_columns=["merchant", "payment_method", "account", "tags", "is_tax_deductible"],
            column_mapping={
                "date": "date",
                "amount": "amount",
                "category": "category",
                "description": "description",
                "merchant": "merchant",
                "payment_method": "payment_method",
                "account": "account",
                "tags": "tags",
                "is_tax_deductible": "is_tax_deductible"
            },
            date_format="%Y-%m-%d",
            sample_data=[
                {"date": "2026-04-26", "amount": "45.50", "category": "food", "description": "Weekly shop", "merchant": "Tesco"}
            ]
        ),
        
        "generic_income_csv": ImportTemplate(
            name="Generic Income Import (CSV)",
            format=ImportFormat.CSV,
            required_columns=["date", "amount", "source", "description"],
            optional_columns=["employment_type", "tax_deducted", "ni_deducted", "account"],
            column_mapping={
                "date": "date",
                "amount": "amount",
                "source": "source",
                "description": "description",
                "employment_type": "employment_type",
                "tax_deducted": "tax_deducted",
                "ni_deducted": "ni_deducted"
            },
            date_format="%Y-%m-%d",
            sample_data=[
                {"date": "2026-04-26", "amount": "2555.00", "source": "Employer Ltd", "description": "Monthly salary", "tax_deducted": "425.00", "ni_deducted": "215.00"}
            ]
        ),
        
        "trading212_csv": ImportTemplate(
            name="Trading 212 Export (CSV)",
            format=ImportFormat.CSV,
            required_columns=["Date", "Ticker", "Type", "Price", "Quantity"],
            optional_columns=["Fees", "Currency", "Notes"],
            column_mapping={
                "Date": "date",
                "Ticker": "symbol",
                "Type": "transaction_type",
                "Price": "price",
                "Quantity": "quantity",
                "Fees": "fees"
            },
            date_format="%Y-%m-%d %H:%M:%S",
            sample_data=[
                {"Date": "2026-04-26 09:30:00", "Ticker": "VUSA", "Type": "Buy", "Price": "75.50", "Quantity": "10", "Fees": "0.00"}
            ]
        ),
        
        "cryptocom_csv": ImportTemplate(
            name="Crypto.com Export (CSV)",
            format=ImportFormat.CSV,
            required_columns=["Timestamp", "Transaction Description", "Currency", "Amount"],
            optional_columns=["To Currency", "To Amount", "Native Currency", "Native Amount"],
            column_mapping={
                "Timestamp": "date",
                "Transaction Description": "description",
                "Currency": "currency",
                "Amount": "amount"
            },
            date_format="%Y-%m-%d %H:%M:%S",
            sample_data=[
                {"Timestamp": "2026-04-26 14:30:00", "Transaction Description": "Buy BTC", "Currency": "BTC", "Amount": "0.001"}
            ]
        )
    }
    
    def __init__(self):
        self.custom_templates: Dict[str, ImportTemplate] = {}
    
    def get_template(self, name: str) -> Optional[ImportTemplate]:
        """Get import template by name"""
        return self.TEMPLATES.get(name) or self.custom_templates.get(name)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        templates = []
        
        for name, template in {**self.TEMPLATES, **self.custom_templates}.items():
            templates.append({
                "id": name,
                "name": template.name,
                "format": template.format.value,
                "required_columns": template.required_columns,
                "optional_columns": template.optional_columns,
                "sample_row": template.sample_data[0] if template.sample_data else None
            })
        
        return templates
    
    def create_custom_template(
        self,
        name: str,
        format_type: ImportFormat,
        column_mapping: Dict[str, str],
        required_columns: List[str],
        optional_columns: Optional[List[str]] = None,
        date_format: str = "%Y-%m-%d",
        delimiter: str = ",",
        has_header: bool = True
    ) -> ImportTemplate:
        """Create custom import template"""
        template = ImportTemplate(
            name=name,
            format=format_type,
            required_columns=required_columns,
            optional_columns=optional_columns or [],
            column_mapping=column_mapping,
            date_format=date_format,
            delimiter=delimiter,
            has_header=has_header
        )
        
        self.custom_templates[name] = template
        logger.info(f"Custom template created: {name}")
        return template
    
    def parse_csv(
        self,
        csv_content: str,
        template_name: str,
        account_name: str = "imported"
    ) -> ImportResult:
        """Parse CSV data using template"""
        import time
        start_time = time.time()
        
        template = self.get_template(template_name)
        if not template:
            return ImportResult(
                success=False,
                records_imported=0,
                records_skipped=0,
                records_failed=0,
                errors=[{"message": f"Template '{template_name}' not found"}],
                warnings=[],
                import_id=f"import_{datetime.now().timestamp()}",
                duration_seconds=0,
                summary={}
            )
        
        errors = []
        warnings = []
        transactions = []
        
        try:
            # Parse CSV
            reader = csv.DictReader(StringIO(csv_content))
            
            # Validate headers
            if template.has_header:
                headers = reader.fieldnames or []
                missing_required = [col for col in template.required_columns if col not in headers]
                if missing_required:
                    return ImportResult(
                        success=False,
                        records_imported=0,
                        records_skipped=0,
                        records_failed=0,
                        errors=[{"message": f"Missing required columns: {missing_required}"}],
                        warnings=[],
                        import_id=f"import_{datetime.now().timestamp()}",
                        duration_seconds=time.time() - start_time,
                        summary={}
                    )
            
            # Process rows
            for row_num, row in enumerate(reader, start=1):
                try:
                    transaction = self._parse_row(row, template, account_name)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    errors.append({
                        "row": row_num,
                        "message": str(e),
                        "data": row
                    })
            
            duration = time.time() - start_time
            
            return ImportResult(
                success=len(errors) == 0,
                records_imported=len(transactions),
                records_skipped=0,
                records_failed=len(errors),
                errors=errors,
                warnings=warnings,
                import_id=f"import_{datetime.now().timestamp()}",
                duration_seconds=duration,
                summary={
                    "template_used": template_name,
                    "account": account_name,
                    "total_amount": sum(t.amount for t in transactions),
                    "date_range": {
                        "earliest": min(t.date for t in transactions).isoformat() if transactions else None,
                        "latest": max(t.date for t in transactions).isoformat() if transactions else None
                    }
                }
            )
            
        except Exception as e:
            return ImportResult(
                success=False,
                records_imported=0,
                records_skipped=0,
                records_failed=0,
                errors=[{"message": f"Parse error: {str(e)}"}],
                warnings=[],
                import_id=f"import_{datetime.now().timestamp()}",
                duration_seconds=time.time() - start_time,
                summary={}
            )
    
    def _parse_row(
        self,
        row: Dict[str, str],
        template: ImportTemplate,
        account_name: str
    ) -> Optional[ParsedTransaction]:
        """Parse single CSV row into transaction"""
        # Map columns
        mapped_data = {}
        for file_col, internal_col in template.column_mapping.items():
            if file_col in row:
                mapped_data[internal_col] = row[file_col]
        
        # Parse date
        date_str = mapped_data.get("date", "")
        try:
            parsed_date = datetime.strptime(date_str, template.date_format).date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")
        
        # Parse amount
        amount_str = mapped_data.get("amount", "0")
        # Remove currency symbols and commas
        amount_str = amount_str.replace("£", "").replace(",", "").strip()
        try:
            amount = Decimal(amount_str)
        except:
            raise ValueError(f"Invalid amount: {amount_str}")
        
        # Determine transaction type
        transaction_type = "debit"
        if amount > 0:
            transaction_type = "credit"
        elif "income" in mapped_data.get("category", "").lower() or \
             "salary" in mapped_data.get("description", "").lower():
            transaction_type = "credit"
        
        return ParsedTransaction(
            date=parsed_date,
            description=mapped_data.get("description", ""),
            amount=abs(amount),
            transaction_type=transaction_type,
            category=mapped_data.get("category"),
            merchant=mapped_data.get("merchant"),
            account=account_name,
            reference=mapped_data.get("reference"),
            raw_data=row
        )
    
    def generate_csv_template(self, template_name: str) -> str:
        """Generate CSV template with headers and sample data"""
        template = self.get_template(template_name)
        if not template:
            return ""
        
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=template.required_columns + template.optional_columns,
            delimiter=template.delimiter
        )
        
        writer.writeheader()
        
        # Write sample data
        for sample in template.sample_data:
            writer.writerow(sample)
        
        return output.getvalue()
    
    def auto_detect_template(self, csv_content: str) -> Optional[str]:
        """Auto-detect which template to use based on headers"""
        try:
            reader = csv.DictReader(StringIO(csv_content))
            headers = set(reader.fieldnames or [])
            
            best_match = None
            best_score = 0
            
            for name, template in {**self.TEMPLATES, **self.custom_templates}.items():
                required = set(template.required_columns)
                match_score = len(headers & required) / len(required)
                
                if match_score > best_score and match_score >= 0.7:  # 70% threshold
                    best_score = match_score
                    best_match = name
            
            return best_match
            
        except Exception as e:
            logger.error(f"Auto-detect error: {e}")
            return None
    
    def validate_csv(self, csv_content: str, template_name: str) -> Dict[str, Any]:
        """Validate CSV without importing"""
        template = self.get_template(template_name)
        if not template:
            return {"valid": False, "error": f"Template '{template_name}' not found"}
        
        try:
            reader = csv.DictReader(StringIO(csv_content))
            headers = reader.fieldnames or []
            
            # Check required columns
            missing = [col for col in template.required_columns if col not in headers]
            if missing:
                return {
                    "valid": False,
                    "error": f"Missing required columns: {missing}",
                    "headers_found": list(headers),
                    "required": template.required_columns
                }
            
            # Sample first few rows
            rows = []
            for i, row in enumerate(reader):
                if i >= 3:  # Sample first 3 rows
                    break
                rows.append(row)
            
            return {
                "valid": True,
                "headers": list(headers),
                "sample_rows": rows,
                "template": template_name,
                "estimated_records": sum(1 for _ in csv_content.strip().split('\n')) - 1  # Rough count
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}


# Global importer instance
_data_importer: Optional[DataImporter] = None


def get_data_importer() -> DataImporter:
    """Get or create global data importer"""
    global _data_importer
    if _data_importer is None:
        _data_importer = DataImporter()
    return _data_importer
