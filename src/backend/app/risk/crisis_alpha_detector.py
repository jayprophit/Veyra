"""
Crisis Alpha Detector
=====================
Real-time detection of market stress, tail risk events, and crisis opportunities
VIX analysis, credit spreads, liquidity metrics, safe-haven rotation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)


class CrisisLevel(Enum):
    NORMAL = "normal"           # Business as usual
    ELEVATED = "elevated"       # Some concern
    WARNING = "warning"         # Rising risk
    CRISIS = "crisis"           # Active crisis
    EXTREME = "extreme"         # Once-in-decade event


class CrisisType(Enum):
    VOLATILITY_SPIKE = "volatility_spike"
    CREDIT_STRESS = "credit_stress"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    SAFE_HAVEN_RUSH = "safe_haven_rush"
    CORRELATION_BREAKDOWN = "correlation_breakdown"
    FLASH_CRASH = "flash_crash"
    CONTAGION = "contagion"


@dataclass
class CrisisSignal:
    """Detected crisis signal"""
    crisis_type: CrisisType
    level: CrisisLevel
    confidence: float
    timestamp: datetime
    indicators: Dict[str, float]
    description: str
    recommended_action: str
    expected_duration_days: int


class CrisisAlphaDetector:
    """
    Production crisis detection system
    
    Monitors:
    - VIX and term structure
    - Credit spreads (HY, IG, EM)
    - Liquidity metrics (bid-ask spreads, volume)
    - Safe haven flows (USD, JPY, Gold, Treasuries)
    - Correlation breakdown
    - Flash crash detection
    """
    
    # Crisis thresholds
    VIX_ELEVATED = 20
    VIX_WARNING = 30
    VIX_CRISIS = 40
    VIX_EXTREME = 50
    
    CREDIT_SPREAD_ELEVATED = 400  # bps
    CREDIT_SPREAD_WARNING = 600
    CREDIT_SPREAD_CRISIS = 1000
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.lookback_days = self.config.get('lookback_days', 60)
        self.correlation_window = self.config.get('correlation_window', 20)
        
        # Data storage
        self.vix_history: List[Dict] = []
        self.credit_spreads: Dict[str, List[float]] = {}
        self.liquidity_metrics: Dict[str, pd.DataFrame] = {}
        self.safe_haven_flows: Dict[str, float] = {}
        self.correlation_matrix: Optional[pd.DataFrame] = None
        
        # State
        self.current_crisis_level = CrisisLevel.NORMAL
        self.active_signals: List[CrisisSignal] = []
        self.crisis_history: List[CrisisSignal] = []
    
    async def fetch_market_data(self, data_sources: Optional[Dict] = None):
        """
        Fetch all required market data for crisis detection
        
        In production: Connect to Bloomberg, IEX, Polygon, etc.
        For now: Simulate with realistic data
        """
        logger.info("Fetching crisis detection data...")
        
        # Simulate VIX data
        self.vix_history = self._simulate_vix_data()
        
        # Simulate credit spreads
        self.credit_spreads = {
            'hy_spread': self._simulate_credit_spread('high_yield'),
            'ig_spread': self._simulate_credit_spread('investment_grade'),
            'em_spread': self._simulate_credit_spread('emerging_markets'),
            'cdx_ig': self._simulate_credit_spread('cdx_ig'),
            'cdx_hy': self._simulate_credit_spread('cdx_hy')
        }
        
        # Simulate liquidity metrics
        self.liquidity_metrics = {
            'sp500_bid_ask': self._simulate_liquidity_metric('sp500'),
            'corporate_bond_liquidity': self._simulate_liquidity_metric('bonds'),
            'fx_liquidity': self._simulate_liquidity_metric('fx')
        }
        
        # Simulate safe haven flows
        self.safe_haven_flows = self._simulate_safe_haven_flows()
        
        logger.info("Market data fetched successfully")
    
    def _simulate_vix_data(self) -> List[Dict]:
        """Simulate VIX spot and futures data"""
        np.random.seed(42)
        
        base_vix = 18
        dates = pd.date_range(end=datetime.now(), periods=self.lookback_days, freq='D')
        
        # Generate realistic VIX series with occasional spikes
        vix_values = []
        for i, date in enumerate(dates):
            # Base mean reversion
            if i == 0:
                vix = base_vix
            else:
                prev_vix = vix_values[-1]['spot']
                mean_rev = 0.05 * (base_vix - prev_vix)
                shock = np.random.normal(0, 2)
                vix = max(10, prev_vix + mean_rev + shock)
            
            # Occasional spikes
            if np.random.random() < 0.05:
                vix *= np.random.uniform(1.3, 2.0)
            
            vix_values.append({
                'date': date,
                'spot': round(vix, 2),
                'front_month': round(vix * np.random.uniform(0.95, 1.05), 2),
                'second_month': round(vix * np.random.uniform(0.98, 1.08), 2),
                'term_structure': 'contango' if vix < 25 else 'backwardation'
            })
        
        return vix_values
    
    def _simulate_credit_spread(self, spread_type: str) -> List[float]:
        """Simulate credit spread data in basis points"""
        np.random.seed(hash(spread_type) % 2**32)
        
        base_spreads = {
            'high_yield': 350,
            'investment_grade': 120,
            'emerging_markets': 280,
            'cdx_ig': 80,
            'cdx_hy': 350
        }
        
        base = base_spreads.get(spread_type, 200)
        
        spreads = []
        for _ in range(self.lookback_days):
            noise = np.random.normal(0, base * 0.05)
            spread = max(50, base + noise)
            spreads.append(round(spread, 1))
        
        return spreads
    
    def _simulate_liquidity_metric(self, market: str) -> pd.DataFrame:
        """Simulate liquidity metrics"""
        np.random.seed(hash(market) % 2**32)
        
        dates = pd.date_range(end=datetime.now(), periods=self.lookback_days, freq='D')
        
        base_bid_ask = 0.02 if market == 'sp500' else 0.1
        
        data = {
            'date': dates,
            'bid_ask_spread_pct': np.random.normal(base_bid_ask, base_bid_ask * 0.3, self.lookback_days),
            'volume': np.random.randint(1000000, 10000000, self.lookback_days),
            'market_depth': np.random.normal(100, 20, self.lookback_days)
        }
        
        return pd.DataFrame(data).set_index('date')
    
    def _simulate_safe_haven_flows(self) -> Dict[str, float]:
        """Simulate safe haven asset flows"""
        return {
            'usd_index_change': np.random.normal(0, 0.5),
            'jpy_change': np.random.normal(0, 0.3),
            'gold_change': np.random.normal(0.02, 0.5),
            'treasury_flow': np.random.normal(0, 1.0),
            'long_term_treasury_yield_change': np.random.normal(-0.05, 0.1),
            'flight_to_quality_score': np.random.uniform(-1, 1)
        }
    
    def analyze_vix(self) -> Dict:
        """
        Analyze VIX level and term structure
        """
        if not self.vix_history:
            return {'error': 'No VIX data available'}
        
        current = self.vix_history[-1]
        spot = current['spot']
        
        # Determine crisis level from VIX
        if spot >= self.VIX_EXTREME:
            level = CrisisLevel.EXTREME
        elif spot >= self.VIX_CRISIS:
            level = CrisisLevel.CRISIS
        elif spot >= self.VIX_WARNING:
            level = CrisisLevel.WARNING
        elif spot >= self.VIX_ELEVATED:
            level = CrisisLevel.ELEVATED
        else:
            level = CrisisLevel.NORMAL
        
        # Analyze term structure
        front = current['front_month']
        second = current['second_month']
        term_slope = (second - front) / front if front > 0 else 0
        
        # Backwardation is bearish (near-term fear)
        is_backwardation = term_slope < 0
        
        # Calculate VIX momentum
        vix_series = [d['spot'] for d in self.vix_history]
        vix_change_5d = (vix_series[-1] - vix_series[-5]) / vix_series[-5] * 100 if len(vix_series) >= 5 else 0
        vix_change_20d = (vix_series[-1] - vix_series[-20]) / vix_series[-20] * 100 if len(vix_series) >= 20 else 0
        
        return {
            'current_vix': spot,
            'level': level.value,
            'term_structure': current['term_structure'],
            'is_backwardation': is_backwardation,
            'term_slope': round(term_slope * 100, 2),
            'change_5d_pct': round(vix_change_5d, 2),
            'change_20d_pct': round(vix_change_20d, 2),
            'percentile_90d': self._calculate_percentile(vix_series, 90),
            'signal': 'extreme_fear' if spot > 40 else 'fear' if spot > 30 else 'elevated' if spot > 20 else 'normal'
        }
    
    def _calculate_percentile(self, series: List[float], percentile: int) -> float:
        """Calculate percentile of series"""
        return np.percentile(series, percentile)
    
    def analyze_credit_stress(self) -> Dict:
        """
        Analyze credit market stress indicators
        """
        if not self.credit_spreads:
            return {'error': 'No credit spread data'}
        
        results = {}
        
        for spread_name, spreads in self.credit_spreads.items():
            current = spreads[-1]
            avg_20d = np.mean(spreads[-20:]) if len(spreads) >= 20 else np.mean(spreads)
            change = current - avg_20d
            
            # Determine stress level
            if current > 1000:
                level = 'crisis'
            elif current > 600:
                level = 'warning'
            elif current > 400:
                level = 'elevated'
            else:
                level = 'normal'
            
            results[spread_name] = {
                'current_bps': current,
                'avg_20d_bps': round(avg_20d, 1),
                'change_from_avg': round(change, 1),
                'level': level,
                'widening': change > 20
            }
        
        # Overall credit stress
        hy_stress = results.get('hy_spread', {}).get('level', 'normal')
        ig_stress = results.get('ig_spread', {}).get('level', 'normal')
        
        overall_stress = max(
            [self._level_to_int(hy_stress), self._level_to_int(ig_stress)]
        )
        
        results['overall_credit_stress'] = self._int_to_level(overall_stress)
        results['credit_crisis_probability'] = self._estimate_credit_crisis_probability(results)
        
        return results
    
    def _level_to_int(self, level: str) -> int:
        """Convert level string to int for comparison"""
        mapping = {'normal': 0, 'elevated': 1, 'warning': 2, 'crisis': 3}
        return mapping.get(level, 0)
    
    def _int_to_level(self, level_int: int) -> str:
        """Convert int to level string"""
        mapping = {0: 'normal', 1: 'elevated', 2: 'warning', 3: 'crisis'}
        return mapping.get(level_int, 'normal')
    
    def _estimate_credit_crisis_probability(self, spreads: Dict) -> float:
        """Estimate probability of credit crisis based on spreads"""
        hy = spreads.get('hy_spread', {}).get('current_bps', 0)
        
        if hy > 1000:
            return 0.8
        elif hy > 800:
            return 0.5
        elif hy > 600:
            return 0.3
        elif hy > 400:
            return 0.15
        else:
            return 0.05
    
    def analyze_liquidity(self) -> Dict:
        """
        Analyze market liquidity conditions
        """
        results = {}
        
        for market, data in self.liquidity_metrics.items():
            current_bid_ask = data['bid_ask_spread_pct'].iloc[-1]
            avg_bid_ask = data['bid_ask_spread_pct'].mean()
            bid_ask_trend = current_bid_ask / avg_bid_ask - 1
            
            current_volume = data['volume'].iloc[-1]
            avg_volume = data['volume'].mean()
            volume_trend = current_volume / avg_volume - 1
            
            # Liquidity score (higher = more illiquid)
            liquidity_score = (bid_ask_trend * 100) - (volume_trend * 50)
            
            if liquidity_score > 50:
                level = 'severe_stress'
            elif liquidity_score > 30:
                level = 'stress'
            elif liquidity_score > 15:
                level = 'elevated'
            else:
                level = 'normal'
            
            results[market] = {
                'bid_ask_spread_pct': round(current_bid_ask * 100, 3),
                'bid_ask_trend_pct': round(bid_ask_trend * 100, 2),
                'volume_vs_avg_pct': round(volume_trend * 100, 2),
                'liquidity_score': round(liquidity_score, 2),
                'level': level
            }
        
        return results
    
    def analyze_safe_haven_rotation(self) -> Dict:
        """
        Analyze flows into safe haven assets
        """
        if not self.safe_haven_flows:
            return {'error': 'No safe haven data'}
        
        flows = self.safe_haven_flows
        
        # Calculate flight-to-quality score
        ftq_indicators = [
            flows.get('usd_index_change', 0) > 0.5,
            flows.get('jpy_change', 0) > 0.3,
            flows.get('gold_change', 0) > 0.5,
            flows.get('treasury_flow', 0) > 1.0,
            flows.get('long_term_treasury_yield_change', 0) < -0.1
        ]
        
        ftq_score = sum(ftq_indicators) / len(ftq_indicators)
        
        return {
            'usd_index_change': round(flows.get('usd_index_change', 0), 2),
            'jpy_change_pct': round(flows.get('jpy_change', 0), 2),
            'gold_change_pct': round(flows.get('gold_change', 0), 2),
            'treasury_flow_std': round(flows.get('treasury_flow', 0), 2),
            'treasury_yield_change': round(flows.get('long_term_treasury_yield_change', 0), 3),
            'flight_to_quality_score': round(ftq_score, 2),
            'rotation_detected': ftq_score > 0.6,
            'severity': 'extreme' if ftq_score > 0.8 else 'high' if ftq_score > 0.6 else 'moderate' if ftq_score > 0.4 else 'low'
        }
    
    def detect_crisis_signals(self) -> List[CrisisSignal]:
        """
        Detect and generate crisis signals based on all indicators
        """
        signals = []
        
        # VIX signal
        vix_analysis = self.analyze_vix()
        if vix_analysis.get('level') in ['crisis', 'extreme']:
            signals.append(CrisisSignal(
                crisis_type=CrisisType.VOLATILITY_SPIKE,
                level=CrisisLevel(vix_analysis['level']),
                confidence=min(vix_analysis['current_vix'] / 50, 0.99),
                timestamp=datetime.now(),
                indicators={'vix': vix_analysis['current_vix']},
                description=f"VIX at {vix_analysis['current_vix']}: Extreme volatility expected",
                recommended_action="Reduce equity exposure, buy VIX calls, increase cash",
                expected_duration_days=5
            ))
        
        # Credit stress signal
        credit_analysis = self.analyze_credit_stress()
        if credit_analysis.get('overall_credit_stress') in ['warning', 'crisis']:
            signals.append(CrisisSignal(
                crisis_type=CrisisType.CREDIT_STRESS,
                level=CrisisLevel.WARNING if credit_analysis['overall_credit_stress'] == 'warning' else CrisisLevel.CRISIS,
                confidence=credit_analysis.get('credit_crisis_probability', 0.5),
                timestamp=datetime.now(),
                indicators={'hy_spread': credit_analysis.get('hy_spread', {}).get('current_bps', 0)},
                description="Credit spreads widening: corporate debt stress",
                recommended_action="Reduce HY bonds, buy CDX protection, increase quality",
                expected_duration_days=30
            ))
        
        # Safe haven signal
        safe_haven = self.analyze_safe_haven_rotation()
        if safe_haven.get('rotation_detected'):
            signals.append(CrisisSignal(
                crisis_type=CrisisType.SAFE_HAVEN_RUSH,
                level=CrisisLevel.WARNING if safe_haven['severity'] == 'high' else CrisisLevel.ELEVATED,
                confidence=safe_haven['flight_to_quality_score'],
                timestamp=datetime.now(),
                indicators={'ftq_score': safe_haven['flight_to_quality_score']},
                description="Flight to quality detected: risk-off rotation",
                recommended_action="Rotate to safe havens, reduce EM exposure",
                expected_duration_days=10
            ))
        
        # Liquidity crisis
        liquidity = self.analyze_liquidity()
        severe_liquidity = any(
            m.get('level') in ['stress', 'severe_stress']
            for m in liquidity.values()
        )
        
        if severe_liquidity:
            signals.append(CrisisSignal(
                crisis_type=CrisisType.LIQUIDITY_CRISIS,
                level=CrisisLevel.CRISIS,
                confidence=0.85,
                timestamp=datetime.now(),
                indicators={k: v.get('liquidity_score', 0) for k, v in liquidity.items()},
                description="Market liquidity severely impaired",
                recommended_action="Reduce position sizes, avoid illiquid assets, increase cash",
                expected_duration_days=3
            ))
        
        self.active_signals = signals
        self.crisis_history.extend(signals)
        
        # Update overall crisis level
        if signals:
            max_level = max([self._level_to_int(s.level.value) for s in signals])
            self.current_crisis_level = CrisisLevel(self._int_to_level(max_level))
        else:
            self.current_crisis_level = CrisisLevel.NORMAL
        
        return signals
    
    def generate_crisis_alpha_opportunities(self) -> List[Dict]:
        """
        Generate actionable alpha opportunities during crisis
        """
        opportunities = []
        
        vix_analysis = self.analyze_vix()
        safe_haven = self.analyze_safe_haven_rotation()
        
        # VIX spike fade
        if vix_analysis['current_vix'] > 35:
            opportunities.append({
                'strategy': 'vix_fade',
                'description': 'Short VIX futures/ETPs - mean reversion trade',
                'expected_return': '15-30% in 1-2 weeks',
                'risk': 'high',
                'timeframe': '1-2 weeks',
                'confidence': 0.7
            })
        
        # Safe haven momentum
        if safe_haven.get('rotation_detected'):
            opportunities.append({
                'strategy': 'safe_haven_momentum',
                'description': 'Long Treasuries, Gold, USD/JPY - follow the flow',
                'expected_return': '5-15% in crisis period',
                'risk': 'medium',
                'timeframe': '1-4 weeks',
                'confidence': safe_haven['flight_to_quality_score']
            })
        
        # Credit stress opportunities
        credit_analysis = self.analyze_credit_stress()
        if credit_analysis.get('overall_credit_stress') == 'crisis':
            opportunities.append({
                'strategy': 'credit_recovery',
                'description': 'Buy distressed credits post-crisis, sell CDX protection',
                'expected_return': '20-50% over 6-12 months',
                'risk': 'very_high',
                'timeframe': '6-12 months',
                'confidence': 0.6
            })
        
        # Equity dip buying
        if vix_analysis['current_vix'] > 30:
            opportunities.append({
                'strategy': 'crisis_buying',
                'description': 'Buy broad equity indices (SPY, QQQ) - crisis premium',
                'expected_return': '10-25% in 3-6 months',
                'risk': 'medium_high',
                'timeframe': '3-6 months',
                'confidence': 0.75
            })
        
        return opportunities
    
    def get_full_report(self) -> Dict:
        """Get comprehensive crisis analysis report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'crisis_level': self.current_crisis_level.value,
            'vix_analysis': self.analyze_vix(),
            'credit_analysis': self.analyze_credit_stress(),
            'liquidity_analysis': self.analyze_liquidity(),
            'safe_haven_analysis': self.analyze_safe_haven_rotation(),
            'active_crisis_signals': [
                {
                    'type': s.crisis_type.value,
                    'level': s.level.value,
                    'confidence': s.confidence,
                    'description': s.description,
                    'action': s.recommended_action
                }
                for s in self.active_signals
            ],
            'alpha_opportunities': self.generate_crisis_alpha_opportunities(),
            'risk_management': {
                'recommended_equity_exposure': self._get_equity_exposure_recommendation(),
                'recommended_cash_level': self._get_cash_recommendation(),
                'hedging_recommended': self.current_crisis_level.value in ['crisis', 'extreme']
            }
        }
    
    def _get_equity_exposure_recommendation(self) -> str:
        """Recommend equity exposure based on crisis level"""
        recommendations = {
            'normal': '100% target allocation',
            'elevated': '85% target allocation',
            'warning': '60-70% target allocation',
            'crisis': '30-50% target allocation',
            'extreme': '0-20% target allocation - prioritize capital preservation'
        }
        return recommendations.get(self.current_crisis_level.value, '100%')
    
    def _get_cash_recommendation(self) -> str:
        """Recommend cash level based on crisis level"""
        recommendations = {
            'normal': '5-10%',
            'elevated': '10-15%',
            'warning': '20-30%',
            'crisis': '40-60%',
            'extreme': '70-90% - maximum liquidity'
        }
        return recommendations.get(self.current_crisis_level.value, '10%')
    
    async def run_continuous_monitoring(self, interval_seconds: int = 300):
        """Run continuous crisis monitoring (every 5 minutes by default)"""
        logger.info(f"Starting continuous crisis monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                await self.fetch_market_data()
                signals = self.detect_crisis_signals()
                
                if signals:
                    logger.warning(f"CRISIS ALERT: {len(signals)} signals detected!")
                    for signal in signals:
                        logger.warning(
                            f"  - {signal.crisis_type.value}: {signal.description}"
                        )
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in crisis monitoring: {e}")
                await asyncio.sleep(interval_seconds)


# Convenience function
def get_current_crisis_assessment() -> Dict:
    """Quick crisis assessment"""
    detector = CrisisAlphaDetector()
    asyncio.run(detector.fetch_market_data())
    detector.detect_crisis_signals()
    return detector.get_full_report()
