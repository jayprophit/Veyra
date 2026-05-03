"""Regulatory Compliance and Reporting Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)

class Regulation(Enum):
    SEC = "sec"                    # US Securities and Exchange Commission
    FCA = "fca"                    # UK Financial Conduct Authority
    MiFID_II = "mifid_ii"          # EU Markets in Financial Instruments
    FINRA = "finra"                # US Financial Industry Regulatory
    CFTC = "cftc"                  # US Commodity Futures Trading
    GDPR = "gdpr"                  # EU Data Protection
    AML = "aml"                    # Anti-Money Laundering
    KYC = "kyc"                    # Know Your Customer

@dataclass
class TradeReport:
    report_id: str
    trade_id: str
    user_id: str
    symbol: str
    quantity: float
    price: float
    side: str
    timestamp: datetime
    venue: str
    compliance_hash: str

@dataclass
class SuspiciousActivity:
    alert_id: str
    user_id: str
    activity_type: str
    description: str
    risk_score: float
    timestamp: datetime
    status: str

class ComplianceEngine:
    """
    Regulatory compliance automation for multiple jurisdictions.
    Trade reporting, surveillance, audit trails, and regulatory submissions.
    """
    
    def __init__(self):
        self.regulations = [Regulation.SEC, Regulation.FCA, Regulation.MiFID_II]
        self.trade_reports: List[TradeReport] = []
        self.suspicious_activities: List[SuspiciousActivity] = []
        self.audit_trail: List[Dict] = []
        self.retention_years = 7
        
        # Surveillance rules
        self.surveillance_rules = {
            'wash_trading': self._detect_wash_trading,
            'spoofing': self._detect_spoofing,
            'layering': self._detect_layering,
            'insider_trading': self._detect_insider_patterns,
            'money_laundering': self._detect_aml_patterns
        }
    
    async def report_trade(self, trade: Dict[str, Any], 
                          jurisdiction: Regulation = Regulation.SEC) -> TradeReport:
        """Generate regulatory trade report with immutable audit trail."""
        
        # Create compliance hash
        trade_data = json.dumps(trade, sort_keys=True, default=str)
        compliance_hash = hashlib.sha256(trade_data.encode()).hexdigest()
        
        report = TradeReport(
            report_id=f"TR{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            trade_id=trade['trade_id'],
            user_id=trade['user_id'],
            symbol=trade['symbol'],
            quantity=trade['quantity'],
            price=trade['price'],
            side=trade['side'],
            timestamp=datetime.now(),
            venue=trade.get('venue', 'internal'),
            compliance_hash=compliance_hash
        )
        
        self.trade_reports.append(report)
        
        # Log to audit trail
        await self._log_audit_event('trade_reported', report)
        
        logger.info(f"Trade reported to {jurisdiction.value}: {report.trade_id}")
        return report
    
    async def _log_audit_event(self, event_type: str, data: Any):
        """Create immutable audit log entry."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data_hash': hashlib.sha256(str(data).encode()).hexdigest()[:16],
            'integrity_proof': self._calculate_integrity_proof()
        }
        self.audit_trail.append(entry)
    
    def _calculate_integrity_proof(self) -> str:
        """Calculate chain hash for audit integrity."""
        if not self.audit_trail:
            return hashlib.sha256(b'genesis').hexdigest()[:16]
        
        last_entry = self.audit_trail[-1]
        combined = f"{last_entry['timestamp']}{last_entry['data_hash']}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    async def run_trade_surveillance(self, 
                                    trades: List[Dict],
                                    orders: List[Dict]) -> List[SuspiciousActivity]:
        """Run market abuse surveillance algorithms."""
        alerts = []
        
        for rule_name, detector in self.surveillance_rules.items():
            try:
                detected = detector(trades, orders)
                for activity in detected:
                    alert = SuspiciousActivity(
                        alert_id=f"SAR{datetime.now().strftime('%H%M%S%f')}",
                        user_id=activity['user_id'],
                        activity_type=rule_name,
                        description=activity['description'],
                        risk_score=activity['risk_score'],
                        timestamp=datetime.now(),
                        status='open'
                    )
                    self.suspicious_activities.append(alert)
                    alerts.append(alert)
            except Exception as e:
                logger.error(f"Surveillance error in {rule_name}: {e}")
        
        return alerts
    
    def _detect_wash_trading(self, trades: List[Dict], 
                            orders: List[Dict]) -> List[Dict]:
        """Detect wash trading (self-matching orders)."""
        suspicious = []
        
        # Group by user and symbol
        user_symbol_trades = {}
        for trade in trades:
            key = (trade['user_id'], trade['symbol'])
            if key not in user_symbol_trades:
                user_symbol_trades[key] = []
            user_symbol_trades[key].append(trade)
        
        # Check for matching buy/sell within short time window
        for (user_id, symbol), user_trades in user_symbol_trades.items():
            buys = [t for t in user_trades if t['side'] == 'buy']
            sells = [t for t in user_trades if t['side'] == 'sell']
            
            for buy in buys:
                for sell in sells:
                    time_diff = abs(
                        datetime.fromisoformat(buy['timestamp']) - 
                        datetime.fromisoformat(sell['timestamp'])
                    ).total_seconds()
                    
                    if time_diff < 60 and abs(buy['price'] - sell['price']) < 0.01:
                        suspicious.append({
                            'user_id': user_id,
                            'description': f'Potential wash trade: {symbol}',
                            'risk_score': 0.85,
                            'evidence': {'buy': buy, 'sell': sell}
                        })
        
        return suspicious
    
    def _detect_spoofing(self, trades: List[Dict], 
                        orders: List[Dict]) -> List[Dict]:
        """Detect spoofing (large orders placed and cancelled)."""
        suspicious = []
        
        # Check for large cancelled orders
        cancelled_large = [
            o for o in orders 
            if o.get('status') == 'cancelled' 
            and o.get('quantity', 0) > 10000
        ]
        
        for order in cancelled_large:
            suspicious.append({
                'user_id': order['user_id'],
                'description': f'Potential spoofing: Large cancelled order',
                'risk_score': 0.75,
                'evidence': {'order': order}
            })
        
        return suspicious
    
    def _detect_layering(self, trades: List[Dict], 
                        orders: List[Dict]) -> List[Dict]:
        """Detect layering (multiple orders at different prices)."""
        # Simplified implementation
        return []
    
    def _detect_insider_patterns(self, trades: List[Dict], 
                                 orders: List[Dict]) -> List[Dict]:
        """Detect potential insider trading patterns."""
        suspicious = []
        
        # Check for unusual trading before major price moves
        symbol_trades = {}
        for trade in trades:
            symbol = trade['symbol']
            if symbol not in symbol_trades:
                symbol_trades[symbol] = []
            symbol_trades[symbol].append(trade)
        
        # In production, correlate with news/events
        return suspicious
    
    def _detect_aml_patterns(self, trades: List[Dict], 
                            orders: List[Dict]) -> List[Dict]:
        """Detect money laundering patterns."""
        suspicious = []
        
        # Check for structuring (small trades to avoid reporting)
        user_daily_volumes = {}
        for trade in trades:
            user_id = trade['user_id']
            date = trade['timestamp'][:10]
            key = (user_id, date)
            
            if key not in user_daily_volumes:
                user_daily_volumes[key] = {'count': 0, 'volume': 0}
            
            user_daily_volumes[key]['count'] += 1
            user_daily_volumes[key]['volume'] += trade['quantity'] * trade['price']
        
        # Flag high-frequency small trades
        for (user_id, date), stats in user_daily_volumes.items():
            if stats['count'] > 50 and stats['volume'] > 100000:
                suspicious.append({
                    'user_id': user_id,
                    'description': f'AML: High frequency trading pattern',
                    'risk_score': 0.7,
                    'evidence': stats
                })
        
        return suspicious
    
    async def generate_regulatory_filing(self,
                                        jurisdiction: Regulation,
                                        period: str) -> Dict[str, Any]:
        """Generate regulatory filing report."""
        # Filter reports by period
        period_start = datetime.now() - timedelta(days=30 if period == 'monthly' else 90)
        
        relevant_trades = [
            t for t in self.trade_reports
            if t.timestamp >= period_start
        ]
        
        suspicious = [
            a for a in self.suspicious_activities
            if a.timestamp >= period_start
        ]
        
        report = {
            'jurisdiction': jurisdiction.value,
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'total_trades': len(relevant_trades),
            'total_volume': sum(t.quantity * t.price for t in relevant_trades),
            'suspicious_activities': len(suspicious),
            'suspicious_breakdown': {
                'wash_trading': sum(1 for s in suspicious if s.activity_type == 'wash_trading'),
                'spoofing': sum(1 for s in suspicious if s.activity_type == 'spoofing'),
                'aml': sum(1 for s in suspicious if s.activity_type == 'money_laundering')
            },
            'audit_hash': self._calculate_integrity_proof()
        }
        
        return report
    
    async def verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify integrity of audit trail."""
        if not self.audit_trail:
            return {'status': 'empty', 'integrity': True}
        
        # Verify chain
        is_valid = True
        for i in range(1, len(self.audit_trail)):
            current = self.audit_trail[i]
            previous = self.audit_trail[i-1]
            
            expected = hashlib.sha256(
                f"{previous['timestamp']}{previous['data_hash']}".encode()
            ).hexdigest()[:16]
            
            if current['integrity_proof'] != expected:
                is_valid = False
                break
        
        return {
            'status': 'verified' if is_valid else 'compromised',
            'integrity': is_valid,
            'entries': len(self.audit_trail),
            'first_entry': self.audit_trail[0]['timestamp'] if self.audit_trail else None,
            'last_entry': self.audit_trail[-1]['timestamp'] if self.audit_trail else None
        }

compliance_engine = ComplianceEngine()
