"""Form 13F Tracker - Track hedge fund holdings via SEC filings"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class Holding13F:
    issuer: str
    cusip: str
    shares: int
    value: float
    position_type: str  # CALL, PUT, STOCK, CONVERTIBLE
    ownership_pct: float

@dataclass
class Filing13F:
    manager_name: str
    filing_date: datetime
    report_date: datetime
    total_value: float
    num_positions: int
    holdings: List[Holding13F]

class Form13FTracker:
    """Track and analyze 13F filings"""
    
    def __init__(self):
        self.filings: Dict[str, List[Filing13F]] = {}  # manager -> filings
        self.all_holdings: Dict[str, Dict] = {}  # issuer -> aggregated data
    
    def add_filing(self, manager: str, filing: Filing13F):
        """Add 13F filing for manager"""
        if manager not in self.filings:
            self.filings[manager] = []
        self.filings[manager].append(filing)
    
    def analyze_manager_changes(self, manager: str, 
                                 current_filing: Filing13F,
                                 previous_filing: Filing13F) -> Dict:
        """Analyze changes between two filings"""
        
        # Build position maps
        current_positions = {h.cusip: h for h in current_filing.holdings}
        previous_positions = {h.cusip: h for h in previous_filing.holdings}
        
        # New positions
        new_positions = [cusip for cusip in current_positions if cusip not in previous_positions]
        
        # Closed positions
        closed_positions = [cusip for cusip in previous_positions if cusip not in current_positions]
        
        # Increased positions
        increased = []
        decreased = []
        
        for cusip in current_positions:
            if cusip in previous_positions:
                curr_val = current_positions[cusip].value
                prev_val = previous_positions[cusip].value
                
                change_pct = ((curr_val - prev_val) / prev_val * 100) if prev_val > 0 else 0
                
                if change_pct > 20:
                    increased.append({
                        "cusip": cusip,
                        "issuer": current_positions[cusip].issuer,
                        "change_pct": round(change_pct, 1),
                        "prev_value": prev_val,
                        "curr_value": curr_val
                    })
                elif change_pct < -20:
                    decreased.append({
                        "cusip": cusip,
                        "issuer": current_positions[cusip].issuer,
                        "change_pct": round(change_pct, 1),
                        "prev_value": prev_val,
                        "curr_value": curr_val
                    })
        
        # Portfolio turnover estimate
        total_value_current = current_filing.total_value
        buys = sum(current_positions[c].value for c in new_positions)
        sells = sum(previous_positions[c].value for c in closed_positions)
        
        turnover = ((buys + sells) / 2) / total_value_current if total_value_current > 0 else 0
        
        return {
            "manager": manager,
            "filing_period": current_filing.report_date.strftime("%Y-Q%q"),
            "new_positions": len(new_positions),
            "closed_positions": len(closed_positions),
            "increased_positions": increased[:5],  # Top 5
            "decreased_positions": decreased[:5],
            "estimated_turnover": round(turnover * 100, 1),
            "concentration_change": self._analyze_concentration(current_filing, previous_filing),
            "activity_level": "HIGH" if turnover > 0.5 else "MODERATE" if turnover > 0.25 else "LOW"
        }
    
    def _analyze_concentration(self, current: Filing13F, previous: Filing13F) -> Dict:
        """Analyze portfolio concentration changes"""
        if not current.holdings:
            return {}
        
        # Current top 10 concentration
        sorted_current = sorted(current.holdings, key=lambda x: x.value, reverse=True)
        top10_current = sum(h.value for h in sorted_current[:10]) / current.total_value if current.total_value > 0 else 0
        
        sorted_prev = sorted(previous.holdings, key=lambda x: x.value, reverse=True)
        top10_previous = sum(h.value for h in sorted_prev[:10]) / previous.total_value if previous.total_value > 0 else 0
        
        return {
            "top10_concentration_current": round(top10_current * 100, 1),
            "top10_concentration_previous": round(top10_previous * 100, 1),
            "concentration_trend": "INCREASING" if top10_current > top10_previous else "DECREASING",
            "diversification": "CONCENTRATED" if top10_current > 0.5 else "MODERATE" if top10_current > 0.3 else "DIVERSIFIED"
        }
    
    def find_consensus_trades(self, min_managers: int = 3) -> List[Dict]:
        """Find stocks with high consensus among tracked managers"""
        position_counts = defaultdict(lambda: {"count": 0, "total_value": 0, "managers": []})
        
        for manager, filings in self.filings.items():
            if not filings:
                continue
            latest = filings[-1]  # Most recent
            
            for holding in latest.holdings:
                cusip = holding.cusip
                position_counts[cusip]["count"] += 1
                position_counts[cusip]["total_value"] += holding.value
                position_counts[cusip]["issuer"] = holding.issuer
                position_counts[cusip]["managers"].append(manager)
        
        # Filter by consensus threshold
        consensus = []
        for cusip, data in position_counts.items():
            if data["count"] >= min_managers:
                consensus.append({
                    "cusip": cusip,
                    "issuer": data["issuer"],
                    "num_managers": data["count"],
                    "total_value": round(data["total_value"], 0),
                    "avg_position_size": round(data["total_value"] / data["count"], 0),
                    "managers": data["managers"],
                    "consensus_strength": "STRONG" if data["count"] >= 10 else "MODERATE" if data["count"] >= 5 else "WEAK"
                })
        
        # Sort by number of managers
        consensus.sort(key=lambda x: x["num_managers"], reverse=True)
        
        return consensus[:20]  # Top 20 consensus ideas
    
    def track_insider_cluster(self, target_issuers: List[str]) -> Dict:
        """Track cluster buying in specific issuers"""
        cluster_data = defaultdict(lambda: {"buying_managers": [], "selling_managers": [], "net_flow": 0})
        
        for manager, filings in self.filings.items():
            if len(filings) < 2:
                continue
            
            current = filings[-1]
            previous = filings[-2]
            
            curr_positions = {h.cusip: h for h in current.holdings}
            prev_positions = {h.cusip: h for h in previous.holdings}
            
            for issuer in target_issuers:
                # Find CUSIP for issuer (simplified)
                cusip = next((h.cusip for h in current.holdings if h.issuer == issuer), None)
                
                if not cusip:
                    continue
                
                if cusip in curr_positions and cusip not in prev_positions:
                    # New position
                    cluster_data[issuer]["buying_managers"].append(manager)
                    cluster_data[issuer]["net_flow"] += curr_positions[cusip].value
                elif cusip in curr_positions and cusip in prev_positions:
                    # Position change
                    change = curr_positions[cusip].value - prev_positions[cusip].value
                    if change > 0:
                        cluster_data[issuer]["buying_managers"].append(manager)
                    else:
                        cluster_data[issuer]["selling_managers"].append(manager)
                    cluster_data[issuer]["net_flow"] += change
        
        # Generate signals
        signals = []
        for issuer, data in cluster_data.items():
            buy_count = len(data["buying_managers"])
            sell_count = len(data["selling_managers"])
            
            if buy_count >= 3 and buy_count > sell_count:
                signal = "BULLISH_CLUSTER"
            elif sell_count >= 3 and sell_count > buy_count:
                signal = "BEARISH_CLUSTER"
            else:
                signal = "MIXED"
            
            signals.append({
                "issuer": issuer,
                "buying_managers": data["buying_managers"],
                "selling_managers": data["selling_managers"],
                "net_flow_millions": round(data["net_flow"] / 1e6, 1),
                "signal": signal,
                "confidence": "HIGH" if abs(buy_count - sell_count) >= 3 else "MODERATE"
            })
        
        return {"cluster_signals": signals}
    
    def get_manager_summary(self, manager: str) -> Dict:
        """Get summary for specific manager"""
        if manager not in self.filings or not self.filings[manager]:
            return {"error": f"No filings for {manager}"}
        
        latest = self.filings[manager][-1]
        
        # Calculate metrics
        sorted_holdings = sorted(latest.holdings, key=lambda x: x.value, reverse=True)
        
        # Sector allocation estimate (simplified based on position sizes)
        top_10_value = sum(h.value for h in sorted_holdings[:10])
        
        # Long vs short estimate (based on puts)
        put_positions = [h for h in latest.holdings if h.position_type == "PUT"]
        call_positions = [h for h in latest.holdings if h.position_type == "CALL"]
        
        gross_exposure = latest.total_value
        net_exposure = latest.total_value - sum(p.value for p in put_positions)
        
        return {
            "manager": manager,
            "aum_reported": round(latest.total_value / 1e6, 1),
            "num_positions": latest.num_positions,
            "filing_date": latest.filing_date.isoformat(),
            "top_holdings": [
                {
                    "issuer": h.issuer,
                    "value_millions": round(h.value / 1e6, 1),
                    "pct_of_portfolio": round((h.value / latest.total_value) * 100, 2)
                }
                for h in sorted_holdings[:10]
            ],
            "concentration_top10": round((top_10_value / latest.total_value) * 100, 1),
            "options_activity": {
                "put_positions": len(put_positions),
                "call_positions": len(call_positions),
                "hedging_indicator": "ACTIVE" if len(put_positions) > 5 else "MODERATE" if len(put_positions) > 2 else "LOW"
            },
            "exposure_metrics": {
                "gross_millions": round(gross_exposure / 1e6, 1),
                "net_millions": round(net_exposure / 1e6, 1)
            }
        }
    
    def generate_heatmap(self) -> Dict:
        """Generate sector/position heatmap across all managers"""
        all_positions = []
        
        for manager, filings in self.filings.items():
            if filings:
                for holding in filings[-1].holdings:
                    all_positions.append({
                        "manager": manager,
                        **holding.__dict__
                    })
        
        # Aggregate by issuer
        issuer_data = defaultdict(lambda: {"count": 0, "total_value": 0})
        for pos in all_positions:
            issuer_data[pos["issuer"]]["count"] += 1
            issuer_data[pos["issuer"]]["total_value"] += pos["value"]
        
        # Create heatmap
        heatmap = []
        for issuer, data in sorted(issuer_data.items(), 
                                     key=lambda x: x[1]["total_value"], 
                                     reverse=True)[:50]:
            heatmap.append({
                "issuer": issuer,
                "manager_count": data["count"],
                "total_value_millions": round(data["total_value"] / 1e6, 1),
                "heatmap_intensity": min(10, int(data["count"] * 2))  # Scale 0-10
            })
        
        return {
            "total_managers": len(self.filings),
            "total_positions_tracked": len(all_positions),
            "heatmap": heatmap,
            "last_updated": datetime.utcnow().isoformat()
        }
