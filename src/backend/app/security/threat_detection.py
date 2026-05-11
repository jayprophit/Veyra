"""
Advanced Threat Detection System
===============================
AI-powered threat detection and prevention for Veyra
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re
from collections import defaultdict, deque
import aiohttp
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    DDOS_ATTACK = "ddos_attack"
    PHISHING_ATTEMPT = "phishing_attempt"
    MALICIOUS_PAYLOAD = "malicious_payload"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_IP = "suspicious_ip"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThreatIndicator:
    """Threat indicator information"""
    indicator_id: str
    threat_type: ThreatType
    severity: AlertSeverity
    confidence: float
    source_ip: str
    user_id: Optional[str]
    session_id: Optional[str]
    description: str
    evidence: Dict[str, Any]
    timestamp: datetime
    is_blocked: bool = False


@dataclass
class SecurityPattern:
    """Security pattern for anomaly detection"""
    pattern_id: str
    name: str
    description: str
    threat_type: ThreatType
    pattern: str
    severity: AlertSeverity
    is_active: bool


class ThreatDetectionEngine:
    """Advanced threat detection engine with ML capabilities"""
    
    def __init__(self):
        self.threat_indicators: deque = deque(maxlen=100000)
        self.security_patterns: Dict[str, SecurityPattern] = {}
        self.blocked_ips: Set[str] = set()
        self.suspicious_ips: Dict[str, int] = defaultdict(int)
        self.user_behavior_profiles: Dict[str, Dict[str, Any]] = {}
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Initialize security patterns
        self._initialize_security_patterns()
        
        # Rate limiting
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.block_durations: Dict[str, datetime] = {}
        
    def _initialize_security_patterns(self):
        """Initialize security threat patterns"""
        patterns = [
            SecurityPattern(
                pattern_id="sql_injection_1",
                name="SQL Injection Pattern 1",
                description="Classic SQL injection with UNION",
                threat_type=ThreatType.SQL_INJECTION,
                pattern=r"(?i)(union|select|insert|update|delete|drop|create|alter).*\b(from|into)\\\b",
                severity=AlertSeverity.HIGH,
                is_active=True
            ),
            SecurityPattern(
                pattern_id="sql_injection_2",
                name="SQL Injection Pattern 2",
                description="SQL injection with quotes",
                threat_type=ThreatType.SQL_INJECTION,
                pattern=r"(?i)(\%27|\').*(\%27|').*([;]|--)",
                severity=AlertSeverity.HIGH,
                is_active=True
            ),
            SecurityPattern(
                pattern_id="xss_script_1",
                name="XSS Script Pattern",
                description="Cross-site scripting with script tags",
                threat_type=ThreatType.XSS_ATTACK,
                pattern=r"(?i)<script[^>]*>.*?</script>",
                severity=AlertSeverity.HIGH,
                is_active=True
            ),
            SecurityPattern(
                pattern_id="xss_js_1",
                name="XSS JavaScript Pattern",
                description="Cross-site scripting with javascript:",
                threat_type=ThreatType.XSS_ATTACK,
                pattern=r"(?i)javascript\s*:",
                severity=AlertSeverity.MEDIUM,
                is_active=True
            ),
            SecurityPattern(
                pattern_id="path_traversal_1",
                name="Path Traversal Pattern",
                description="Directory traversal attack",
                threat_type=ThreatType.MALICIOUS_PAYLOAD,
                pattern=r"(?i)(\.\./|%2e%2e%2f|%5c%2e%2e)",
                severity=AlertSeverity.HIGH,
                is_active=True
            ),
            SecurityPattern(
                pattern_id="command_injection_1",
                name="Command Injection Pattern",
                description="OS command injection",
                threat_type=ThreatType.MALICIOUS_PAYLOAD,
                pattern=r"(?i)(;|\||&|`|\$\(|\${).*\b(cat|ls|dir|whoami|id|pwd)\\\b",
                severity=AlertSeverity.CRITICAL,
                is_active=True
            )
        ]
        
        for pattern in patterns:
            self.security_patterns[pattern.pattern_id] = pattern
            
    async def analyze_request(self, request_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Analyze incoming request for threats"""
        threats = []
        
        try:
            # Extract request components
            ip_address = request_data.get("ip_address", "")
            user_id = request_data.get("user_id")
            session_id = request_data.get("session_id")
            user_agent = request_data.get("user_agent", "")
            method = request_data.get("method", "")
            path = request_data.get("path", "")
            headers = request_data.get("headers", {})
            body = request_data.get("body", "")
            query_params = request_data.get("query_params", {})
            
            # Check rate limiting
            rate_limit_threat = await self._check_rate_limiting(ip_address, user_id)
            if rate_limit_threat:
                threats.append(rate_limit_threat)
                
            # Check blocked IPs
            if ip_address in self.blocked_ips:
                threats.append(ThreatIndicator(
                    indicator_id=secrets.token_urlsafe(16),
                    threat_type=ThreatType.SUSPICIOUS_IP,
                    severity=AlertSeverity.HIGH,
                    confidence=1.0,
                    source_ip=ip_address,
                    user_id=user_id,
                    session_id=session_id,
                    description="Request from blocked IP address",
                    evidence={"ip_address": ip_address},
                    timestamp=datetime.now(),
                    is_blocked=True
                ))
                
            # Pattern matching
            pattern_threats = await self._pattern_matching(
                ip_address, user_id, session_id, method, path, body, query_params
            )
            threats.extend(pattern_threats)
            
            # Anomaly detection
            anomaly_threats = await self._detect_anomalies(
                ip_address, user_id, session_id, request_data
            )
            threats.extend(anomaly_threats)
            
            # Behavioral analysis
            behavioral_threats = await self._behavioral_analysis(
                ip_address, user_id, session_id, request_data
            )
            threats.extend(behavioral_threats)
            
            # Log all detected threats
            for threat in threats:
                await self._handle_threat_indicator(threat)
                
        except Exception as e:
            logger.error(f"Threat analysis error: {e}")
            
        return threats
        
    async def _check_rate_limiting(self, ip_address: str, user_id: Optional[str]) -> Optional[ThreatIndicator]:
        """Check for rate limiting violations"""
        now = datetime.now()
        
        # Check IP-based rate limiting
        ip_requests = self.request_counts[ip_address]
        ip_requests.append(now)
        
        # Count requests in last minute
        recent_ip_requests = [req for req in ip_requests if now - req <= timedelta(minutes=1)]
        
        if len(recent_ip_requests) > 100:  # More than 100 requests per minute
            return ThreatIndicator(
                indicator_id=secrets.token_urlsafe(16),
                threat_type=ThreatType.DDOS_ATTACK,
                severity=AlertSeverity.HIGH,
                confidence=0.8,
                source_ip=ip_address,
                user_id=user_id,
                session_id=None,
                description="High request rate detected",
                evidence={
                    "requests_per_minute": len(recent_ip_requests),
                    "threshold": 100
                },
                timestamp=now
            )
            
        # Check user-based rate limiting
        if user_id:
            user_requests = self.request_counts[f"user_{user_id}"]
            user_requests.append(now)
            
            recent_user_requests = [req for req in user_requests if now - req <= timedelta(minutes=1)]
            
            if len(recent_user_requests) > 50:  # More than 50 requests per minute per user
                return ThreatIndicator(
                    indicator_id=secrets.token_urlsafe(16),
                    threat_type=ThreatType.DDOS_ATTACK,
                    severity=AlertSeverity.MEDIUM,
                    confidence=0.7,
                    source_ip=ip_address,
                    user_id=user_id,
                    session_id=None,
                    description="High user request rate detected",
                    evidence={
                        "requests_per_minute": len(recent_user_requests),
                        "threshold": 50
                    },
                    timestamp=now
                )
                
        return None
        
    async def _pattern_matching(self, ip_address: str, user_id: Optional[str],
                             session_id: Optional[str], method: str, path: str,
                             body: str, query_params: Dict[str, Any]) -> List[ThreatIndicator]:
        """Perform pattern matching for known threats"""
        threats = []
        
        # Combine all text to analyze
        text_to_analyze = f"{path} {body} {json.dumps(query_params)}"
        
        for pattern in self.security_patterns.values():
            if not pattern.is_active:
                continue
                
            try:
                matches = re.finditer(pattern.pattern, text_to_analyze, re.IGNORECASE)
                
                for match in matches:
                    threats.append(ThreatIndicator(
                        indicator_id=secrets.token_urlsafe(16),
                        threat_type=pattern.threat_type,
                        severity=pattern.severity,
                        confidence=0.9,
                        source_ip=ip_address,
                        user_id=user_id,
                        session_id=session_id,
                        description=f"{pattern.name} detected",
                        evidence={
                            "pattern_id": pattern.pattern_id,
                            "matched_text": match.group(),
                            "location": f"Position {match.start()}"
                        },
                        timestamp=datetime.now()
                    ))
                    
            except Exception as e:
                logger.error(f"Pattern matching error for {pattern.pattern_id}: {e}")
                
        return threats
        
    async def _detect_anomalies(self, ip_address: str, user_id: Optional[str],
                              session_id: Optional[str], request_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Detect anomalous behavior using ML"""
        threats = []
        
        try:
            # Extract features for anomaly detection
            features = self._extract_features(request_data)
            
            if len(features) > 0:
                # Normalize features
                features_array = np.array([list(features.values())])
                
                if not self.is_trained:
                    # Train on some normal data (would use historical data)
                    self._train_anomaly_detector()
                    
                # Predict anomaly
                anomaly_score = self.anomaly_detector.decision_function(features_array)[0]
                is_anomaly = self.anomaly_detector.predict(features_array)[0] == -1
                
                if is_anomaly and anomaly_score < -0.5:
                    threats.append(ThreatIndicator(
                        indicator_id=secrets.token_urlsafe(16),
                        threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                        severity=AlertSeverity.MEDIUM,
                        confidence=abs(anomaly_score),
                        source_ip=ip_address,
                        user_id=user_id,
                        session_id=session_id,
                        description="Anomalous request pattern detected",
                        evidence={
                            "anomaly_score": float(anomaly_score),
                            "features": features
                        },
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            
        return threats
        
    async def _behavioral_analysis(self, ip_address: str, user_id: Optional[str],
                                 session_id: Optional[str], request_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Analyze user behavior patterns"""
        threats = []
        
        try:
            if user_id:
                # Get or create user behavior profile
                if user_id not in self.user_behavior_profiles:
                    self.user_behavior_profiles[user_id] = {
                        "first_seen": datetime.now(),
                        "last_activity": datetime.now(),
                        "total_requests": 0,
                        "unique_ips": set(),
                        "typical_request_patterns": defaultdict(int),
                        "suspicious_activities": []
                    }
                    
                profile = self.user_behavior_profiles[user_id]
                
                # Update profile
                profile["last_activity"] = datetime.now()
                profile["total_requests"] += 1
                profile["unique_ips"].add(ip_address)
                
                # Check for suspicious behavior
                path = request_data.get("path", "")
                method = request_data.get("method", "")
                
                # Unusual time of day (simplified)
                current_hour = datetime.now().hour
                if current_hour < 6 or current_hour > 22:
                    profile["suspicious_activities"].append({
                        "type": "unusual_time",
                        "timestamp": datetime.now(),
                        "details": {"hour": current_hour}
                    })
                    
                # Unusual access patterns
                if len(profile["unique_ips"]) > 10:  # Access from many different IPs
                    threats.append(ThreatIndicator(
                        indicator_id=secrets.token_urlsafe(16),
                        threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                        severity=AlertSeverity.MEDIUM,
                        confidence=0.6,
                        source_ip=ip_address,
                        user_id=user_id,
                        session_id=session_id,
                        description="User accessing from multiple IPs",
                        evidence={
                            "unique_ip_count": len(profile["unique_ips"]),
                            "recent_ips": list(profile["unique_ips"])[-5:]
                        },
                        timestamp=datetime.now()
                    ))
                    
                # Check for data exfiltration patterns
                if "export" in path.lower() or "download" in path.lower():
                    profile["suspicious_activities"].append({
                        "type": "data_access",
                        "timestamp": datetime.now(),
                        "details": {"path": path, "method": method}
                    })
                    
                    # Check if too many data access attempts
                    recent_data_access = [
                        activity for activity in profile["suspicious_activities"]
                        if activity["type"] == "data_access" and
                        datetime.now() - activity["timestamp"] <= timedelta(hours=1)
                    ]
                    
                    if len(recent_data_access) > 10:
                        threats.append(ThreatIndicator(
                            indicator_id=secrets.token_urlsafe(16),
                            threat_type=ThreatType.DATA_EXFILTRATION,
                            severity=AlertSeverity.HIGH,
                            confidence=0.8,
                            source_ip=ip_address,
                            user_id=user_id,
                            session_id=session_id,
                            description="Potential data exfiltration detected",
                            evidence={
                                "data_access_count": len(recent_data_access),
                                "time_window": "1 hour"
                            },
                            timestamp=datetime.now()
                        ))
                        
        except Exception as e:
            logger.error(f"Behavioral analysis error: {e}")
            
        return threats
        
    def _extract_features(self, request_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features for anomaly detection"""
        features = {}
        
        try:
            # Time-based features
            now = datetime.now()
            features["hour_of_day"] = now.hour
            features["day_of_week"] = now.weekday()
            
            # Request-based features
            features["path_length"] = len(request_data.get("path", ""))
            features["body_size"] = len(request_data.get("body", ""))
            features["header_count"] = len(request_data.get("headers", {}))
            features["param_count"] = len(request_data.get("query_params", {}))
            
            # Content-based features
            body = request_data.get("body", "")
            features["special_char_count"] = sum(1 for c in body if not c.isalnum() and c not in " \t\n\\\r")
            features["numeric_char_count"] = sum(1 for c in body if c.isdigit())
            
            # Method encoding
            method = request_data.get("method", "")
            features["is_get"] = 1.0 if method.upper() == "GET" else 0.0
            features["is_post"] = 1.0 if method.upper() == "POST" else 0.0
            features["is_put"] = 1.0 if method.upper() == "PUT" else 0.0
            features["is_delete"] = 1.0 if method.upper() == "DELETE" else 0.0
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            
        return features
        
    def _train_anomaly_detector(self):
        """Train the anomaly detection model"""
        try:
            # Generate some sample normal data (would use historical data)
            sample_features = []
            for _ in range(1000):
                features = {
                    "hour_of_day": np.random.randint(0, 24),
                    "day_of_week": np.random.randint(0, 7),
                    "path_length": np.random.randint(10, 100),
                    "body_size": np.random.randint(0, 1000),
                    "header_count": np.random.randint(5, 20),
                    "param_count": np.random.randint(0, 10),
                    "special_char_count": np.random.randint(0, 50),
                    "numeric_char_count": np.random.randint(0, 20),
                    "is_get": np.random.choice([0.0, 1.0]),
                    "is_post": np.random.choice([0.0, 1.0]),
                    "is_put": np.random.choice([0.0, 1.0]),
                    "is_delete": np.random.choice([0.0, 1.0])
                }
                sample_features.append(list(features.values()))
                
            # Train the model
            X = np.array(sample_features)
            X_scaled = self.scaler.fit_transform(X)
            self.anomaly_detector.fit(X_scaled)
            self.is_trained = True
            
        except Exception as e:
            logger.error(f"Anomaly detector training error: {e}")
            
    async def _handle_threat_indicator(self, threat: ThreatIndicator):
        """Handle detected threat"""
        # Store threat
        self.threat_indicators.append(threat)
        
        # Block IP if critical threat
        if threat.severity == AlertSeverity.CRITICAL:
            self.blocked_ips.add(threat.source_ip)
            
        # Update suspicious IP counter
        self.suspicious_ips[threat.source_ip] += 1
        
        # Auto-block if too many suspicious activities
        if self.suspicious_ips[threat.source_ip] >= 5:
            self.blocked_ips.add(threat.source_ip)
            
        # Log for SIEM integration
        logger.warning(f"Threat detected: {threat.threat_type.value} - {threat.description}")
        
    def get_threat_indicators(self, since: Optional[datetime] = None,
                             threat_type: Optional[ThreatType] = None,
                             severity: Optional[AlertSeverity] = None) -> List[ThreatIndicator]:
        """Get threat indicators with filtering"""
        indicators = list(self.threat_indicators)
        
        if since:
            indicators = [ind for ind in indicators if ind.timestamp >= since]
            
        if threat_type:
            indicators = [ind for ind in indicators if ind.threat_type == threat_type]
            
        if severity:
            indicators = [ind for ind in indicators if ind.severity == severity]
            
        return sorted(indicators, key=lambda x: x.timestamp, reverse=True)
        
    def get_blocked_ips(self) -> Set[str]:
        """Get all blocked IP addresses"""
        return self.blocked_ips.copy()
        
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip_address)
        self.suspicious_ips.pop(ip_address, None)
        
    def get_threat_summary(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get threat summary statistics"""
        indicators = self.get_threat_indicators(since=since)
        
        # Count by threat type
        threat_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for indicator in indicators:
            threat_counts[indicator.threat_type.value] += 1
            severity_counts[indicator.severity.value] += 1
            
        return {
            "total_threats": len(indicators),
            "blocked_ips": len(self.blocked_ips),
            "threat_types": dict(threat_counts),
            "severity_distribution": dict(severity_counts),
            "top_threat_sources": self._get_top_threat_sources(indicators),
            "recent_indicators": [
                {
                    "threat_type": ind.threat_type.value,
                    "severity": ind.severity.value,
                    "description": ind.description,
                    "timestamp": ind.timestamp.isoformat(),
                    "source_ip": ind.source_ip
                }
                for ind in indicators[:10]
            ]
        }
        
    def _get_top_threat_sources(self, indicators: List[ThreatIndicator]) -> List[Dict[str, Any]]:
        """Get top threat source IPs"""
        ip_counts = defaultdict(int)
        
        for indicator in indicators:
            ip_counts[indicator.source_ip] += 1
            
        return [
            {"ip": ip, "count": count}
            for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]


# Global threat detection engine instance
_threat_detection = None

def get_threat_detection_engine() -> ThreatDetectionEngine:
    """Get the global threat detection engine instance"""
    global _threat_detection
    if _threat_detection is None:
        _threat_detection = ThreatDetectionEngine()
    return _threat_detection
