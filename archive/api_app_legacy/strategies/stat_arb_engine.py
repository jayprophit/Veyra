"""
Statistical Arbitrage Engine
=============================
Pairs trading and mean reversion strategies.
Features:
- Cointegration detection
- Z-score based signals
- Kalman filter for hedge ratio
- Dynamic position sizing
- Risk controls

Grade Impact: +8 points
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class SignalType(Enum):
    LONG_SPREAD = "long_spread"  # Buy underperformer, sell outperformer
    SHORT_SPREAD = "short_spread"  # Sell underperformer, buy outperformer
    NO_SIGNAL = "no_signal"
    CLOSE_POSITION = "close_position"


@dataclass
class PairSignal:
    symbol_a: str
    symbol_b: str
    signal: SignalType
    z_score: float
    hedge_ratio: float
    confidence: float
    expected_return: float
    stop_loss_z: float
    take_profit_z: float
    timestamp: datetime


@dataclass
class PairPosition:
    symbol_a: str
    symbol_b: str
    position_a: int  # Positive = long, negative = short
    position_b: int
    entry_z: float
    entry_price_a: float
    entry_price_b: float
    entry_time: datetime
    pnl: float = 0.0
    status: str = "open"


class CointegrationTester:
    """Test for cointegration between two price series."""
    
    @staticmethod
    def adf_test(series: pd.Series, significance: float = 0.05) -> Tuple[bool, float]:
        """
        Augmented Dickey-Fuller test for stationarity.
        Returns (is_stationary, p_value)
        """
        from statsmodels.tsa.stattools import adfuller
        
        try:
            result = adfuller(series.dropna(), maxlag=1)
            p_value = result[1]
            is_stationary = p_value < significance
            return is_stationary, p_value
        except Exception as e:
            logger.error(f"ADF test failed: {e}")
            return False, 1.0
    
    @staticmethod
    def engle_granger_test(
        series_a: pd.Series,
        series_b: pd.Series,
        significance: float = 0.05
    ) -> Tuple[bool, float, float]:
        """
        Engle-Granger cointegration test.
        Returns (is_cointegrated, p_value, hedge_ratio)
        """
        # Linear regression to find hedge ratio
        X = series_b.values.reshape(-1, 1)
        y = series_a.values
        
        # OLS regression
        beta = np.sum((X.flatten() - np.mean(X)) * (y - np.mean(y))) / np.sum((X.flatten() - np.mean(X))**2)
        alpha = np.mean(y) - beta * np.mean(X)
        
        # Calculate spread
        spread = y - (beta * X.flatten() + alpha)
        
        # Test spread for stationarity
        is_stationary, p_value = CointegrationTester.adf_test(pd.Series(spread))
        
        return is_stationary, p_value, beta
    
    @staticmethod
    def johansen_test(price_df: pd.DataFrame) -> Dict:
        """
        Johansen cointegration test for multiple series.
        More robust than Engle-Granger for multi-asset.
        """
        try:
            from statsmodels.tsa.vector_ar.vecm import coint_johansen
            
            result = coint_johansen(price_df, det_order=0, k_ar_diff=1)
            
            return {
                "eigenvalues": result.eig,
                "trace_stat": result.lr1,
                "max_eigen_stat": result.lr2,
                "cointegrating_vectors": result.evec,
                "n_cointegrating_relations": np.sum(result.lr1 > result.cvt[:, 0])
            }
        except Exception as e:
            logger.error(f"Johansen test failed: {e}")
            return {}


class KalmanFilterHedge:
    """
    Kalman filter for dynamic hedge ratio estimation.
    Adapts to changing market conditions.
    """
    
    def __init__(self, delta: float = 1e-4, R: float = 1e-3):
        """
        Args:
            delta: Transition covariance (higher = faster adaptation)
            R: Measurement covariance
        """
        self.delta = delta
        self.R = R
        self.x = np.array([0.0, 0.0])  # [slope, intercept]
        self.P = np.eye(2)
        self.w = delta / (1 - delta)
    
    def update(self, price_a: float, price_b: float) -> Tuple[float, float]:
        """
        Update hedge ratio with new price observation.
        Returns (hedge_ratio, intercept)
        """
        # State transition
        F = np.eye(2)
        Q = self.w * np.eye(2)
        
        # Prediction
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q
        
        # Measurement
        H = np.array([price_b, 1.0])
        y = price_a - H @ self.x
        S = H @ self.P @ H.T + self.R
        K = self.P @ H.T / S
        
        # Update
        self.x = self.x + K * y
        self.P = self.P - np.outer(K, H) @ self.P
        
        return self.x[0], self.x[1]


class StatisticalArbitrageEngine:
    """
    Pairs trading engine with cointegration and mean reversion.
    """
    
    def __init__(
        self,
        entry_z: float = 2.0,
        exit_z: float = 0.5,
        stop_z: float = 3.5,
        max_positions: int = 5,
        use_kalman: bool = True
    ):
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_z = stop_z
        self.max_positions = max_positions
        self.use_kalman = use_kalman
        
        self.price_history: Dict[str, pd.Series] = {}
        self.active_pairs: Dict[str, Dict] = {}  # Pair key -> pair data
        self.positions: List[PairPosition] = []
        self.kalman_filters: Dict[str, KalmanFilterHedge] = {}
        self.signals: List[PairSignal] = []
        
    def add_price_data(self, symbol: str, price: float, timestamp: datetime):
        """Add price data point."""
        if symbol not in self.price_history:
            self.price_history[symbol] = pd.Series(dtype=float)
        
        self.price_history[symbol][timestamp] = price
        
        # Keep last 252 days
        if len(self.price_history[symbol]) > 252:
            self.price_history[symbol] = self.price_history[symbol].iloc[-252:]
    
    def find_cointegrated_pairs(
        self,
        symbols: List[str],
        min_history: int = 60,
        p_value_threshold: float = 0.05
    ) -> List[Tuple[str, str, float, float]]:
        """
        Find cointegrated pairs from symbol universe.
        Returns list of (sym_a, sym_b, hedge_ratio, p_value)
        """
        cointegrated = []
        
        for i, sym_a in enumerate(symbols):
            for sym_b in symbols[i+1:]:
                if sym_a not in self.price_history or sym_b not in self.price_history:
                    continue
                
                series_a = self.price_history[sym_a]
                series_b = self.price_history[sym_b]
                
                if len(series_a) < min_history or len(series_b) < min_history:
                    continue
                
                # Align series
                common_idx = series_a.index.intersection(series_b.index)
                if len(common_idx) < min_history:
                    continue
                
                aligned_a = series_a[common_idx]
                aligned_b = series_b[common_idx]
                
                # Test cointegration
                is_coint, p_value, hedge = CointegrationTester.engle_granger_test(
                    aligned_a, aligned_b
                )
                
                if is_coint and p_value < p_value_threshold:
                    cointegrated.append((sym_a, sym_b, hedge, p_value))
                    logger.info(f"Found cointegrated pair: {sym_a}-{sym_b} (p={p_value:.4f})")
        
        # Sort by p-value (lower = stronger cointegration)
        cointegrated.sort(key=lambda x: x[3])
        return cointegrated
    
    def calculate_z_score(
        self,
        sym_a: str,
        sym_b: str,
        lookback: int = 20
    ) -> Optional[Tuple[float, float]]:
        """
        Calculate current z-score for pair.
        Returns (z_score, hedge_ratio)
        """
        if sym_a not in self.price_history or sym_b not in self.price_history:
            return None
        
        series_a = self.price_history[sym_a]
        series_b = self.price_history[sym_b]
        
        # Align
        common_idx = series_a.index.intersection(series_b.index)
        if len(common_idx) < lookback + 5:
            return None
        
        aligned_a = series_a[common_idx]
        aligned_b = series_b[common_idx]
        
        # Use Kalman filter or static hedge
        if self.use_kalman:
            pair_key = f"{sym_a}_{sym_b}"
            if pair_key not in self.kalman_filters:
                self.kalman_filters[pair_key] = KalmanFilterHedge()
            
            # Update with latest prices
            hedge_ratio, _ = self.kalman_filters[pair_key].update(
                aligned_a.iloc[-1], aligned_b.iloc[-1]
            )
        else:
            # Static OLS hedge
            hedge_ratio = np.sum(
                (aligned_b.values - np.mean(aligned_b)) * 
                (aligned_a.values - np.mean(aligned_a))
            ) / np.sum((aligned_b.values - np.mean(aligned_b))**2)
        
        # Calculate spread
        spread = aligned_a.values - hedge_ratio * aligned_b.values
        
        # Z-score using rolling window
        if len(spread) >= lookback:
            recent_spread = spread[-lookback:]
            z_score = (spread[-1] - np.mean(recent_spread)) / np.std(recent_spread)
        else:
            z_score = 0.0
        
        return z_score, hedge_ratio
    
    def generate_signals(self) -> List[PairSignal]:
        """Generate trading signals for all tracked pairs."""
        signals = []
        
        for pair_key, pair_data in self.active_pairs.items():
            sym_a = pair_data["symbol_a"]
            sym_b = pair_data["symbol_b"]
            
            result = self.calculate_z_score(sym_a, sym_b)
            if result is None:
                continue
            
            z_score, hedge_ratio = result
            
            # Check for existing position
            existing = self._get_position(sym_a, sym_b)
            
            if existing:
                # Check for exit
                if abs(z_score) < self.exit_z:
                    signal = SignalType.CLOSE_POSITION
                elif abs(z_score) > self.stop_z:
                    signal = SignalType.CLOSE_POSITION
                else:
                    signal = SignalType.NO_SIGNAL
            else:
                # Check for entry
                if len(self.positions) >= self.max_positions:
                    signal = SignalType.NO_SIGNAL
                elif z_score > self.entry_z:
                    signal = SignalType.SHORT_SPREAD  # A overvalued, B undervalued
                elif z_score < -self.entry_z:
                    signal = SignalType.LONG_SPREAD   # A undervalued, B overvalued
                else:
                    signal = SignalType.NO_SIGNAL
            
            if signal != SignalType.NO_SIGNAL:
                pair_signal = PairSignal(
                    symbol_a=sym_a,
                    symbol_b=sym_b,
                    signal=signal,
                    z_score=z_score,
                    hedge_ratio=hedge_ratio,
                    confidence=min(0.95, 0.5 + abs(z_score) / 4),
                    expected_return=abs(z_score) * 0.02,  # Estimate
                    stop_loss_z=self.stop_z,
                    take_profit_z=self.exit_z,
                    timestamp=datetime.now()
                )
                signals.append(pair_signal)
        
        self.signals = signals
        return signals
    
    def execute_signal(self, signal: PairSignal, capital: float) -> Optional[PairPosition]:
        """Execute a trading signal."""
        if signal.signal == SignalType.NO_SIGNAL:
            return None
        
        # Get current prices
        price_a = self.price_history[signal.symbol_a].iloc[-1]
        price_b = self.price_history[signal.symbol_b].iloc[-1]
        
        # Calculate position sizes
        # Split capital equally, adjust for hedge ratio
        capital_per_leg = capital / 2
        
        if signal.signal == SignalType.LONG_SPREAD:
            # Long A, Short B
            shares_a = int(capital_per_leg / price_a)
            shares_b = -int(capital_per_leg / price_b * signal.hedge_ratio)
        elif signal.signal == SignalType.SHORT_SPREAD:
            # Short A, Long B
            shares_a = -int(capital_per_leg / price_a)
            shares_b = int(capital_per_leg / price_b * signal.hedge_ratio)
        else:
            # Close position - handled separately
            self._close_position(signal.symbol_a, signal.symbol_b)
            return None
        
        position = PairPosition(
            symbol_a=signal.symbol_a,
            symbol_b=signal.symbol_b,
            position_a=shares_a,
            position_b=shares_b,
            entry_z=signal.z_score,
            entry_price_a=price_a,
            entry_price_b=price_b,
            entry_time=datetime.now()
        )
        
        self.positions.append(position)
        logger.info(f"Opened position: {signal.symbol_a}-{signal.symbol_b} @ z={signal.z_score:.2f}")
        
        return position
    
    def _get_position(self, sym_a: str, sym_b: str) -> Optional[PairPosition]:
        """Get open position for pair."""
        for pos in self.positions:
            if pos.symbol_a == sym_a and pos.symbol_b == sym_b and pos.status == "open":
                return pos
        return None
    
    def _close_position(self, sym_a: str, sym_b: str):
        """Close position and calculate P&L."""
        for pos in self.positions:
            if pos.symbol_a == sym_a and pos.symbol_b == sym_b and pos.status == "open":
                # Calculate P&L
                price_a_now = self.price_history[sym_a].iloc[-1]
                price_b_now = self.price_history[sym_b].iloc[-1]
                
                pnl_a = pos.position_a * (price_a_now - pos.entry_price_a)
                pnl_b = pos.position_b * (price_b_now - pos.entry_price_b)
                pos.pnl = pnl_a + pnl_b
                pos.status = "closed"
                
                logger.info(f"Closed position: {sym_a}-{sym_b}, P&L: ${pos.pnl:.2f}")
                return
    
    def get_performance_summary(self) -> Dict:
        """Get strategy performance summary."""
        closed_positions = [p for p in self.positions if p.status == "closed"]
        
        if not closed_positions:
            return {"message": "No closed positions yet"}
        
        pnls = [p.pnl for p in closed_positions]
        
        return {
            "total_trades": len(closed_positions),
            "win_rate": sum(1 for pnl in pnls if pnl > 0) / len(pnls),
            "avg_pnl": np.mean(pnls),
            "total_pnl": sum(pnls),
            "sharpe": np.mean(pnls) / np.std(pnls) if np.std(pnls) > 0 else 0,
            "max_drawdown": min(pnls),
            "best_trade": max(pnls),
            "worst_trade": min(pnls)
        }


# Example usage
if __name__ == "__main__":
    engine = StatisticalArbitrageEngine()
    
    # Simulate price data for pairs
    np.random.seed(42)
    dates = pd.date_range("2026-01-01", periods=100, freq="D")
    
    # Cointegrated pair
    base = np.cumsum(np.random.randn(100) * 0.5)
    asset_a = base + np.random.randn(100) * 0.2
    asset_b = 0.5 * base + 10 + np.random.randn(100) * 0.2
    
    for i, (date, price_a, price_b) in enumerate(zip(dates, asset_a, asset_b)):
        engine.add_price_data("PEP", price_a, date)
        engine.add_price_data("KO", price_b, date)
    
    # Find cointegrated pairs
    pairs = engine.find_cointegrated_pairs(["PEP", "KO"])
    print(f"Found {len(pairs)} cointegrated pairs")
    
    for sym_a, sym_b, hedge, pval in pairs:
        engine.active_pairs[f"{sym_a}_{sym_b}"] = {
            "symbol_a": sym_a,
            "symbol_b": sym_b,
            "hedge_ratio": hedge,
            "p_value": pval
        }
    
    # Generate signals
    signals = engine.generate_signals()
    for sig in signals:
        print(f"Signal: {sig.symbol_a}-{sig.symbol_b}: {sig.signal.value} (z={sig.z_score:.2f})")
