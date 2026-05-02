"""
Open Source Intelligence (OSINT) Tracker
========================================
Gather intelligence from open sources
Satellite imagery, shipping data, flight tracking, supply chain
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class IntelSource(Enum):
    SATELLITE = "satellite_imagery"
    SHIPPING = "shipping_data"
    FLIGHT = "flight_tracking"
    SOCIAL = "social_media"
    NEWS = "news_analysis"
    WEB = "web_scraping"


@dataclass
class IntelReport:
    source: str
    company: str
    finding: str
    confidence: float
    timestamp: datetime
    evidence: List[str]
    impact: str  # 'high', 'medium', 'low'


class OSINTTracker:
    """
    Open Source Intelligence gathering for investment analysis
    
    Sources:
    - Satellite imagery (parking lots, factory activity)
    - Shipping data (port congestion, trade flows)
    - Flight tracking (executive jets, supply chain)
    - Social media (employee sentiment, product launches)
    """
    
    def analyze_satellite_imagery(self, company: str, location: str,
                                   image_analysis: Dict) -> Dict:
        """
        Analyze satellite imagery for economic activity
        
        Use cases:
        - Retail: Parking lot fullness
        - Manufacturing: Factory activity
        - Mining: Extraction progress
        - Agriculture: Crop health
        """
        findings = []
        
        # Parking lot analysis (retail)
        if 'parking_occupancy' in image_analysis:
            occupancy = image_analysis['parking_occupancy']
            if occupancy > 0.8:
                findings.append({
                    'type': 'high_foot_traffic',
                    'description': f'Parking at {occupancy*100:.0f}% capacity',
                    'implication': 'Strong sales expected'
                })
            elif occupancy < 0.3:
                findings.append({
                    'type': 'low_foot_traffic',
                    'description': f'Parking at {occupancy*100:.0f}% capacity',
                    'implication': 'Weak sales expected'
                })
        
        # Factory activity (manufacturing)
        if 'thermal_signature' in image_analysis:
            thermal = image_analysis['thermal_signature']
            if thermal == 'elevated':
                findings.append({
                    'type': 'high_production',
                    'description': 'Elevated thermal signature detected',
                    'implication': 'Running at high capacity'
                })
        
        # Shipping containers (logistics)
        if 'container_count' in image_analysis:
            containers = image_analysis['container_count']
            baseline = image_analysis.get('baseline_containers', 100)
            
            if containers > baseline * 1.3:
                findings.append({
                    'type': 'inventory_buildup',
                    'description': f'{containers} containers (vs {baseline} baseline)',
                    'implication': 'Potential demand slowdown'
                })
            elif containers < baseline * 0.7:
                findings.append({
                    'type': 'strong_shipments',
                    'description': f'{containers} containers (vs {baseline} baseline)',
                    'implication': 'Strong demand, low inventory'
                })
        
        return {
            'company': company,
            'location': location,
            'analysis_date': datetime.now().isoformat(),
            'findings': findings,
            'confidence': 0.75 if findings else 0.5,
            'signal': self._generate_signal(findings)
        }
    
    def track_shipping_lanes(self, company: str,
                            shipping_data: List[Dict]) -> Dict:
        """Track shipping data for supply chain analysis"""
        
        if not shipping_data:
            return {'error': 'No shipping data provided'}
        
        # Analyze shipping patterns
        recent_delays = len([s for s in shipping_data if s.get('delayed', False)])
        total_shipments = len(shipping_data)
        
        delay_rate = recent_delays / total_shipments if total_shipments > 0 else 0
        
        # Port congestion
        congested_ports = set()
        for shipment in shipping_data:
            if shipment.get('port_congestion', False):
                congested_ports.add(shipment.get('port', 'Unknown'))
        
        return {
            'company': company,
            'shipments_analyzed': total_shipments,
            'delay_rate': round(delay_rate * 100, 1),
            'congested_ports': list(congested_ports),
            'supply_chain_health': 'STRESSED' if delay_rate > 0.3 else 'NORMAL',
            'recommendation': 'INVESTIGATE' if delay_rate > 0.3 else 'MONITOR',
            'timestamp': datetime.now().isoformat()
        }
    
    def monitor_executive_travel(self, company: str,
                                 flight_data: List[Dict]) -> Dict:
        """
        Monitor executive private jet travel
        
        Potential signals:
        - M&A activity (frequent trips to target HQ)
        - Deal negotiations (repeated city pairs)
        - Crisis management (unusual destinations)
        """
        if not flight_data:
            return {'error': 'No flight data provided'}
        
        # Analyze patterns
        destinations = {}
        for flight in flight_data:
            dest = flight.get('destination', 'Unknown')
            if dest not in destinations:
                destinations[dest] = 0
            destinations[dest] += 1
        
        # Find repeated destinations (potential deals)
        repeated = {k: v for k, v in destinations.items() if v >= 3}
        
        return {
            'company': company,
            'flights_tracked': len(flight_data),
            'unique_destinations': len(destinations),
            'repeated_destinations': repeated,
            'potential_mna_signals': len(repeated) > 0,
            'anomaly_score': len(repeated) * 0.3,
            'interpretation': 'Potential deal activity' if repeated else 'Normal travel pattern',
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_signal(self, findings: List[Dict]) -> str:
        """Generate trading signal from findings"""
        if not findings:
            return 'NEUTRAL'
        
        positive = len([f for f in findings if f['implication'].startswith('Strong')])
        negative = len([f for f in findings if f['implication'].startswith('Weak')])
        
        if positive > negative:
            return 'BULLISH'
        elif negative > positive:
            return 'BEARISH'
        else:
            return 'MIXED'


# Usage
def analyze_retail_parking(ticker: str, occupancy: float) -> Dict:
    """Quick retail parking analysis"""
    tracker = OSINTTracker()
    
    return tracker.analyze_satellite_imagery(
        company=ticker,
        location='HQ',
        image_analysis={'parking_occupancy': occupancy}
    )


def check_supply_chain(company: str, shipments: List[Dict]) -> Dict:
    """Check supply chain health"""
    tracker = OSINTTracker()
    return tracker.track_shipping_lanes(company, shipments)
