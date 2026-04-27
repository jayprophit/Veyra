"""SEC Filing Analyzer - Analyze SEC filings for compliance and insights"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class FilingType(Enum):
    FORM_10K = "10-K"
    FORM_10Q = "10-Q"
    FORM_8K = "8-K"
    FORM_13F = "13-F"
    FORM_4 = "4"
    FORM_DEF14A = "DEF 14A"
    FORM_S1 = "S-1"

@dataclass
class SECFiling:
    symbol: str
    company_name: str
    filing_type: FilingType
    filing_date: datetime
    report_period_end: datetime
    key_metrics: Dict
    risk_factors: List[str]
    material_events: List[str]

class SECFilingAnalyzer:
    """Analyze SEC filings for investment insights"""
    
    def __init__(self):
        self.filings: List[SECFiling] = []
        self.red_flags = [
            "going concern",
            "material weakness",
            "restatement",
            "bankruptcy",
            "fraud",
            "investigation",
            "subpoena"
        ]
    
    def add_filing(self, filing: SECFiling):
        """Add SEC filing to database"""
        self.filings.append(filing)
    
    def analyze_financial_health(self, filing: SECFiling) -> Dict:
        """Analyze financial health from 10-K/10-Q"""
        metrics = filing.key_metrics
        
        health_score = 50
        concerns = []
        positives = []
        
        # Revenue trend
        if metrics.get("revenue_growth", 0) > 0.10:
            health_score += 15
            positives.append("Strong revenue growth")
        elif metrics.get("revenue_growth", 0) < 0:
            health_score -= 15
            concerns.append("Declining revenue")
        
        # Profitability
        if metrics.get("net_margin", 0) > 0.15:
            health_score += 15
            positives.append("Healthy margins")
        elif metrics.get("net_margin", 0) < 0.02:
            health_score -= 10
            concerns.append("Thin margins")
        
        # Balance sheet strength
        if metrics.get("current_ratio", 0) > 1.5:
            health_score += 10
        elif metrics.get("current_ratio", 0) < 1.0:
            health_score -= 15
            concerns.append("Liquidity concerns")
        
        # Debt levels
        if metrics.get("debt_to_equity", 1) < 0.5:
            health_score += 10
            positives.append("Low leverage")
        elif metrics.get("debt_to_equity", 0) > 1.5:
            health_score -= 15
            concerns.append("High debt burden")
        
        # Cash flow
        if metrics.get("fcf_positive", False):
            health_score += 15
            positives.append("Positive free cash flow")
        else:
            health_score -= 10
            concerns.append("Negative free cash flow")
        
        final_score = max(0, min(100, health_score))
        
        return {
            "symbol": filing.symbol,
            "filing_type": filing.filing_type.value,
            "financial_health_score": final_score,
            "rating": "STRONG" if final_score >= 80 else "SATISFACTORY" if final_score >= 60 else "WEAK" if final_score >= 40 else "DISTRESSED",
            "concerns": concerns,
            "positives": positives,
            "key_metrics": metrics
        }
    
    def detect_red_flags(self, filing: SECFiling) -> Dict:
        """Detect red flags in filings"""
        flags_found = []
        
        # Check risk factors
        for risk in filing.risk_factors:
            risk_lower = risk.lower()
            for flag in self.red_flags:
                if flag in risk_lower:
                    flags_found.append({
                        "flag": flag.upper(),
                        "context": risk[:200] + "..." if len(risk) > 200 else risk
                    })
        
        # Check material events for 8-K
        if filing.filing_type == FilingType.FORM_8K:
            for event in filing.material_events:
                event_lower = event.lower()
                for flag in self.red_flags:
                    if flag in event_lower:
                        flags_found.append({
                            "flag": flag.upper(),
                            "context": event[:200] + "..." if len(event) > 200 else event
                        })
        
        severity = "HIGH" if len(flags_found) >= 3 else "MODERATE" if len(flags_found) >= 1 else "LOW"
        
        return {
            "symbol": filing.symbol,
            "filing_type": filing.filing_type.value,
            "red_flags_count": len(flags_found),
            "red_flags": flags_found,
            "severity": severity,
            "recommendation": "AVOID" if severity == "HIGH" else "CAUTION" if severity == "MODERATE" else "PROCEED"
        }
    
    def track_filing_history(self, symbol: str) -> Dict:
        """Track filing history for a symbol"""
        symbol_filings = [f for f in self.filings if f.symbol == symbol]
        
        if not symbol_filings:
            return {"error": "No filings found for symbol"}
        
        # Sort by date
        symbol_filings.sort(key=lambda x: x.filing_date, reverse=True)
        
        # Count by type
        by_type = {}
        for f in symbol_filings:
            by_type[f.filing_type.value] = by_type.get(f.filing_type.value, 0) + 1
        
        # Check timeliness
        latest_10k = next((f for f in symbol_filings if f.filing_type == FilingType.FORM_10K), None)
        latest_10q = next((f for f in symbol_filings if f.filing_type == FilingType.FORM_10Q), None)
        
        days_since_10k = (datetime.utcnow() - latest_10k.filing_date).days if latest_10k else None
        days_since_10q = (datetime.utcnow() - latest_10q.filing_date).days if latest_10q else None
        
        return {
            "symbol": symbol,
            "total_filings": len(symbol_filings),
            "filings_by_type": by_type,
            "latest_10k": latest_10k.filing_date.strftime("%Y-%m-%d") if latest_10k else None,
            "latest_10q": latest_10q.filing_date.strftime("%Y-%m-%d") if latest_10q else None,
            "days_since_10k": days_since_10k,
            "days_since_10q": days_since_10q,
            "compliance_status": "CURRENT" if (days_since_10q is None or days_since_10q < 120) else "DELAYED"
        }
    
    def get_recent_filings_summary(self, days: int = 7) -> Dict:
        """Get summary of recent filings"""
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        recent = [f for f in self.filings if f.filing_date.timestamp() > cutoff]
        
        # Categorize
        earnings_related = [f for f in recent if f.filing_type in [FilingType.FORM_10Q, FilingType.FORM_10K]]
        events = [f for f in recent if f.filing_type == FilingType.FORM_8K]
        insider = [f for f in recent if f.filing_type == FilingType.FORM_4]
        
        return {
            "period_days": days,
            "total_filings": len(recent),
            "earnings_filings": len(earnings_related),
            "material_event_filings": len(events),
            "insider_transaction_filings": len(insider),
            "most_active_companies": self._get_most_active(recent),
            "notable_events": self._extract_notable_events(events)
        }
    
    def _get_most_active(self, filings: List[SECFiling], n: int = 5) -> List[str]:
        """Get companies with most filings"""
        from collections import Counter
        symbols = [f.symbol for f in filings]
        most_common = Counter(symbols).most_common(n)
        return [s[0] for s in most_common]
    
    def _extract_notable_events(self, filings: List[SECFiling]) -> List[Dict]:
        """Extract notable material events"""
        notable = []
        
        for f in filings:
            for event in f.material_events:
                if any(keyword in event.lower() for keyword in ["merger", "acquisition", "ceo", "bankruptcy", "dividend"]):
                    notable.append({
                        "symbol": f.symbol,
                        "date": f.filing_date.strftime("%Y-%m-%d"),
                        "event_type": "SIGNIFICANT",
                        "summary": event[:100] + "..." if len(event) > 100 else event
                    })
        
        return notable[:10]
