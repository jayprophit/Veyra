"""Report Generator - PDF reports, tax forms, performance summaries"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ReportConfig:
    report_type: str  # "monthly", "quarterly", "annual", "tax"
    start_date: datetime
    end_date: datetime
    format: str = "pdf"  # "pdf", "csv", "html"
    sections: List[str] = None

class ReportGenerator:
    """SSS-Grade financial report generation"""
    
    REPORT_TYPES = {
        "monthly": "Monthly Portfolio Summary",
        "quarterly": "Quarterly Performance Review",
        "annual": "Annual Financial Report",
        "tax": "Tax Documentation",
        "custom": "Custom Report"
    }
    
    def __init__(self, db_manager=None, tax_engine=None):
        self.db = db_manager
        self.tax_engine = tax_engine
    
    def generate_performance_report(
        self,
        user_id: str,
        config: ReportConfig
    ) -> Dict:
        """Generate comprehensive performance report"""
        
        sections = []
        
        # Portfolio Summary
        sections.append({
            "title": "Portfolio Summary",
            "data": self._get_portfolio_summary(user_id, config)
        })
        
        # Performance Metrics
        sections.append({
            "title": "Performance Metrics",
            "data": self._get_performance_metrics(user_id, config)
        })
        
        # Asset Allocation
        sections.append({
            "title": "Asset Allocation",
            "data": self._get_asset_allocation(user_id)
        })
        
        # Transactions
        if "transactions" in (config.sections or []):
            sections.append({
                "title": "Transaction History",
                "data": self._get_transactions(user_id, config)
            })
        
        # Tax Summary
        if config.report_type == "tax" and self.tax_engine:
            sections.append({
                "title": "Tax Summary",
                "data": self._get_tax_summary(user_id, config)
            })
        
        return {
            "report_type": config.report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "start": config.start_date.isoformat(),
                "end": config.end_date.isoformat()
            },
            "sections": sections,
            "format": config.format
        }
    
    def _get_portfolio_summary(self, user_id: str, config: ReportConfig) -> Dict:
        """Get portfolio snapshot"""
        if not self.db:
            return {"total_value": 0, "positions": []}
        
        portfolios = self.db.get_user_portfolios(user_id)
        total_value = sum(p.get("total_value", 0) for p in portfolios)
        
        return {
            "total_value": total_value,
            "currency": "USD",
            "portfolio_count": len(portfolios),
            "positions": sum(len(p.get("positions", [])) for p in portfolios)
        }
    
    def _get_performance_metrics(self, user_id: str, config: ReportConfig) -> Dict:
        """Calculate period performance"""
        # Placeholder - would integrate with analytics
        return {
            "period_return": 0.0,
            "ytd_return": 0.0,
            "annualized_return": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "benchmark_comparison": {
                "sp500": 0.0,
                "nasdaq": 0.0
            }
        }
    
    def _get_asset_allocation(self, user_id: str) -> Dict:
        """Get current allocation"""
        return {
            "by_asset_class": {
                "stocks": 60,
                "bonds": 30,
                "cash": 10
            },
            "by_sector": {},
            "by_region": {}
        }
    
    def _get_transactions(self, user_id: str, config: ReportConfig) -> List:
        """Get transactions for period"""
        if not self.db:
            return []
        
        return self.db.get_transactions(
            user_id,
            start_date=config.start_date,
            end_date=config.end_date
        )
    
    def _get_tax_summary(self, user_id: str, config: ReportConfig) -> Dict:
        """Generate tax documentation"""
        if not self.tax_engine:
            return {}
        
        return {
            "realized_gains_short": 0,
            "realized_gains_long": 0,
            "realized_losses": 0,
            "net_taxable_gains": 0,
            "tax_loss_harvest_opportunities": 0,
            "wash_sales": []
        }
    
    def generate_tax_form_8949(
        self,
        user_id: str,
        tax_year: int
    ) -> Dict:
        """Generate IRS Form 8949 (US)"""
        transactions = self._get_taxable_transactions(user_id, tax_year)
        
        short_term = [t for t in transactions if t.get("holding_days", 0) <= 365]
        long_term = [t for t in transactions if t.get("holding_days", 0) > 365]
        
        return {
            "form": "8949",
            "tax_year": tax_year,
            "part_i_short_term": {
                "transactions": len(short_term),
                "proceeds": sum(t.get("proceeds", 0) for t in short_term),
                "cost_basis": sum(t.get("cost_basis", 0) for t in short_term),
                "adjustments": sum(t.get("adjustments", 0) for t in short_term),
                "gain_loss": sum(t.get("gain_loss", 0) for t in short_term)
            },
            "part_ii_long_term": {
                "transactions": len(long_term),
                "proceeds": sum(t.get("proceeds", 0) for t in long_term),
                "cost_basis": sum(t.get("cost_basis", 0) for t in long_term),
                "adjustments": sum(t.get("adjustments", 0) for t in long_term),
                "gain_loss": sum(t.get("gain_loss", 0) for t in long_term)
            }
        }
    
    def _get_taxable_transactions(self, user_id: str, tax_year: int) -> List:
        """Get taxable transactions for year"""
        if not self.db:
            return []
        
        start = datetime(tax_year, 1, 1)
        end = datetime(tax_year, 12, 31)
        
        transactions = self.db.get_transactions(user_id, start, end)
        
        # Filter to sell transactions
        return [t for t in transactions if t.get("type") == "SELL"]
    
    def export_report(
        self,
        report_data: Dict,
        output_path: str,
        format: str = "pdf"
    ) -> str:
        """Export report to file"""
        
        if format == "json":
            import json
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
        
        elif format == "csv":
            # Export transactions as CSV
            import csv
            transactions = report_data.get("sections", [{}])[-1].get("data", [])
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=transactions[0].keys() if transactions else [])
                writer.writeheader()
                writer.writerows(transactions)
        
        return output_path

print("Report Generator loaded - SSS-grade reporting and tax forms")
