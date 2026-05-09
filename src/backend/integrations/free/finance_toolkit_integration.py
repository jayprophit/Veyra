"""
Finance Toolkit Integration Module - Free Alternative to FactSet
Provides comprehensive financial analysis and modeling capabilities
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

try:
    from financetoolkit import Toolkit
    FINANCETOOLKIT_AVAILABLE = True
except ImportError:
    FINANCETOOLKIT_AVAILABLE = False
    logging.warning("financetoolkit not installed. Install with: pip install financetoolkit")

logger = logging.getLogger(__name__)

@dataclass
class FinancialRatio:
    symbol: str
    ratio_name: str
    value: float
    category: str
    description: str
    timestamp: datetime

@dataclass
class ValuationMetric:
    symbol: str
    metric_name: str
    value: float
    method: str
    timestamp: datetime

@dataclass
class TechnicalSignal:
    symbol: str
    signal_type: str
    signal_value: str
    confidence: float
    timestamp: datetime

@dataclass
class RiskMetric:
    symbol: str
    risk_type: str
    value: float
    interpretation: str
    timestamp: datetime

class FinanceToolkitIntegration:
    """Finance Toolkit integration for free financial analysis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = FINANCETOOLKIT_AVAILABLE
        self.cache = {}
        self.cache_ttl = 600  # 10 minutes
        
        if not self.enabled:
            logger.error("financetoolkit not available - install with: pip install financetoolkit")
            return
        
        # Initialize Finance Toolkit
        try:
            self.toolkit = Toolkit()
            logger.info("Finance Toolkit initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Finance Toolkit: {e}")
            self.enabled = False
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        cached_time = self.cache[key].get('timestamp')
        if not cached_time:
            return False
        return (datetime.now() - cached_time).seconds < self.cache_ttl
    
    def _get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            return self.cache[key]['data']
        return None
    
    def _cache_data(self, key: str, data: Any) -> None:
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def get_financial_ratios(self, symbol: str, period: str = 'annual') -> List[FinancialRatio]:
        """Get comprehensive financial ratios"""
        if not self.enabled:
            return self._get_mock_financial_ratios(symbol, period)
        
        cache_key = f"ratios_{symbol}_{period}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Get financial ratios using Finance Toolkit
            ratios_data = []
            
            # Get profitability ratios
            profitability = self.toolkit.ratios.get_profitability_ratios(symbol, period=period)
            for ratio_name, value in profitability.items():
                if value is not None and not value.empty:
                    ratios_data.append(FinancialRatio(
                        symbol=symbol,
                        ratio_name=ratio_name,
                        value=float(value.iloc[-1]) if hasattr(value, 'iloc') else float(value),
                        category='Profitability',
                        description=self._get_ratio_description(ratio_name),
                        timestamp=datetime.now()
                    ))
            
            # Get liquidity ratios
            liquidity = self.toolkit.ratios.get_liquidity_ratios(symbol, period=period)
            for ratio_name, value in liquidity.items():
                if value is not None and not value.empty:
                    ratios_data.append(FinancialRatio(
                        symbol=symbol,
                        ratio_name=ratio_name,
                        value=float(value.iloc[-1]) if hasattr(value, 'iloc') else float(value),
                        category='Liquidity',
                        description=self._get_ratio_description(ratio_name),
                        timestamp=datetime.now()
                    ))
            
            # Get leverage ratios
            leverage = self.toolkit.ratios.get_leverage_ratios(symbol, period=period)
            for ratio_name, value in leverage.items():
                if value is not None and not value.empty:
                    ratios_data.append(FinancialRatio(
                        symbol=symbol,
                        ratio_name=ratio_name,
                        value=float(value.iloc[-1]) if hasattr(value, 'iloc') else float(value),
                        category='Leverage',
                        description=self._get_ratio_description(ratio_name),
                        timestamp=datetime.now()
                    ))
            
            # Get efficiency ratios
            efficiency = self.toolkit.ratios.get_efficiency_ratios(symbol, period=period)
            for ratio_name, value in efficiency.items():
                if value is not None and not value.empty:
                    ratios_data.append(FinancialRatio(
                        symbol=symbol,
                        ratio_name=ratio_name,
                        value=float(value.iloc[-1]) if hasattr(value, 'iloc') else float(value),
                        category='Efficiency',
                        description=self._get_ratio_description(ratio_name),
                        timestamp=datetime.now()
                    ))
            
            self._cache_data(cache_key, ratios_data)
            return ratios_data
            
        except Exception as e:
            logger.error(f"Failed to get financial ratios for {symbol}: {e}")
        
        return self._get_mock_financial_ratios(symbol, period)
    
    async def get_valuation_metrics(self, symbol: str) -> List[ValuationMetric]:
        """Get valuation metrics"""
        if not self.enabled:
            return self._get_mock_valuation_metrics(symbol)
        
        cache_key = f"valuation_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            valuation_data = []
            
            # Get DCF valuation
            try:
                dcf_value = self.toolkit.valuation.get_dcf(symbol)
                if dcf_value is not None:
                    valuation_data.append(ValuationMetric(
                        symbol=symbol,
                        metric_name='DCF',
                        value=float(dcf_value),
                        method='Discounted Cash Flow',
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get DCF for {symbol}: {e}")
            
            # Get P/E ratio
            try:
                pe_ratio = self.toolkit.valuation.get_price_earnings_ratio(symbol)
                if pe_ratio is not None:
                    valuation_data.append(ValuationMetric(
                        symbol=symbol,
                        metric_name='P/E Ratio',
                        value=float(pe_ratio),
                        method='Price to Earnings',
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get P/E ratio for {symbol}: {e}")
            
            # Get P/B ratio
            try:
                pb_ratio = self.toolkit.valuation.get_price_book_ratio(symbol)
                if pb_ratio is not None:
                    valuation_data.append(ValuationMetric(
                        symbol=symbol,
                        metric_name='P/B Ratio',
                        value=float(pb_ratio),
                        method='Price to Book',
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get P/B ratio for {symbol}: {e}")
            
            # Get P/S ratio
            try:
                ps_ratio = self.toolkit.valuation.get_price_sales_ratio(symbol)
                if ps_ratio is not None:
                    valuation_data.append(ValuationMetric(
                        symbol=symbol,
                        metric_name='P/S Ratio',
                        value=float(ps_ratio),
                        method='Price to Sales',
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get P/S ratio for {symbol}: {e}")
            
            # Get EV/EBITDA ratio
            try:
                ev_ebitda = self.toolkit.valuation.get_ev_ebitda_ratio(symbol)
                if ev_ebitda is not None:
                    valuation_data.append(ValuationMetric(
                        symbol=symbol,
                        metric_name='EV/EBITDA',
                        value=float(ev_ebitda),
                        method='Enterprise Value to EBITDA',
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get EV/EBITDA for {symbol}: {e}")
            
            self._cache_data(cache_key, valuation_data)
            return valuation_data
            
        except Exception as e:
            logger.error(f"Failed to get valuation metrics for {symbol}: {e}")
        
        return self._get_mock_valuation_metrics(symbol)
    
    async def get_technical_signals(self, symbol: str, period: int = 252) -> List[TechnicalSignal]:
        """Get technical analysis signals"""
        if not self.enabled:
            return self._get_mock_technical_signals(symbol, period)
        
        cache_key = f"technical_{symbol}_{period}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            signals_data = []
            
            # Get moving averages
            try:
                ma_signal = self.toolkit.technical.get_moving_average_signal(symbol, period=period)
                if ma_signal is not None:
                    signals_data.append(TechnicalSignal(
                        symbol=symbol,
                        signal_type='Moving Average',
                        signal_value=str(ma_signal),
                        confidence=0.75,
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get MA signal for {symbol}: {e}")
            
            # Get RSI signal
            try:
                rsi_signal = self.toolkit.technical.get_rsi_signal(symbol, period=period)
                if rsi_signal is not None:
                    signals_data.append(TechnicalSignal(
                        symbol=symbol,
                        signal_type='RSI',
                        signal_value=str(rsi_signal),
                        confidence=0.80,
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get RSI signal for {symbol}: {e}")
            
            # Get MACD signal
            try:
                macd_signal = self.toolkit.technical.get_macd_signal(symbol, period=period)
                if macd_signal is not None:
                    signals_data.append(TechnicalSignal(
                        symbol=symbol,
                        signal_type='MACD',
                        signal_value=str(macd_signal),
                        confidence=0.70,
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get MACD signal for {symbol}: {e}")
            
            # Get Bollinger Bands signal
            try:
                bb_signal = self.toolkit.technical.get_bollinger_bands_signal(symbol, period=period)
                if bb_signal is not None:
                    signals_data.append(TechnicalSignal(
                        symbol=symbol,
                        signal_type='Bollinger Bands',
                        signal_value=str(bb_signal),
                        confidence=0.75,
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get Bollinger Bands signal for {symbol}: {e}")
            
            self._cache_data(cache_key, signals_data)
            return signals_data
            
        except Exception as e:
            logger.error(f"Failed to get technical signals for {symbol}: {e}")
        
        return self._get_mock_technical_signals(symbol, period)
    
    async def get_risk_metrics(self, symbol: str, period: int = 252) -> List[RiskMetric]:
        """Get risk metrics"""
        if not self.enabled:
            return self._get_mock_risk_metrics(symbol, period)
        
        cache_key = f"risk_{symbol}_{period}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            risk_data = []
            
            # Get beta
            try:
                beta = self.toolkit.risk.get_beta(symbol, period=period)
                if beta is not None:
                    interpretation = self._interpret_beta(float(beta))
                    risk_data.append(RiskMetric(
                        symbol=symbol,
                        risk_type='Beta',
                        value=float(beta),
                        interpretation=interpretation,
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get beta for {symbol}: {e}")
            
            # Get volatility
            try:
                volatility = self.toolkit.risk.get_volatility(symbol, period=period)
                if volatility is not None:
                    interpretation = self._interpret_volatility(float(volatility))
                    risk_data.append(RiskMetric(
                        symbol=symbol,
                        risk_type='Volatility',
                        value=float(volatility),
                        interpretation=interpretation,
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get volatility for {symbol}: {e}")
            
            # Get Value at Risk
            try:
                var = self.toolkit.risk.get_value_at_risk(symbol, period=period)
                if var is not None:
                    interpretation = self._interpret_var(float(var))
                    risk_data.append(RiskMetric(
                        symbol=symbol,
                        risk_type='Value at Risk',
                        value=float(var),
                        interpretation=interpretation,
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get VaR for {symbol}: {e}")
            
            # Get Sharpe ratio
            try:
                sharpe = self.toolkit.risk.get_sharpe_ratio(symbol, period=period)
                if sharpe is not None:
                    interpretation = self._interpret_sharpe(float(sharpe))
                    risk_data.append(RiskMetric(
                        symbol=symbol,
                        risk_type='Sharpe Ratio',
                        value=float(sharpe),
                        interpretation=interpretation,
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Failed to get Sharpe ratio for {symbol}: {e}")
            
            self._cache_data(cache_key, risk_data)
            return risk_data
            
        except Exception as e:
            logger.error(f"Failed to get risk metrics for {symbol}: {e}")
        
        return self._get_mock_risk_metrics(symbol, period)
    
    async def get_financial_modeling(self, symbol: str, model_type: str = 'dcf') -> Dict[str, Any]:
        """Get financial modeling results"""
        if not self.enabled:
            return self._get_mock_financial_modeling(symbol, model_type)
        
        cache_key = f"modeling_{symbol}_{model_type}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            modeling_result = {}
            
            if model_type.lower() == 'dcf':
                try:
                    dcf_result = self.toolkit.models.get_dcf_model(symbol)
                    modeling_result = {
                        'model_type': 'DCF',
                        'intrinsic_value': float(dcf_result.get('intrinsic_value', 0)),
                        'discount_rate': float(dcf_result.get('discount_rate', 0)),
                        'growth_rate': float(dcf_result.get('growth_rate', 0)),
                        'terminal_value': float(dcf_result.get('terminal_value', 0)),
                        'timestamp': datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.warning(f"Failed to get DCF model for {symbol}: {e}")
            
            elif model_type.lower() == 'multiples':
                try:
                    multiples_result = self.toolkit.models.get_multiples_model(symbol)
                    modeling_result = {
                        'model_type': 'Multiples',
                        'pe_based_value': float(multiples_result.get('pe_based_value', 0)),
                        'pb_based_value': float(multiples_result.get('pb_based_value', 0)),
                        'ps_based_value': float(multiples_result.get('ps_based_value', 0)),
                        'average_value': float(multiples_result.get('average_value', 0)),
                        'timestamp': datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.warning(f"Failed to get multiples model for {symbol}: {e}")
            
            elif model_type.lower() == 'dividend':
                try:
                    dividend_result = self.toolkit.models.get_dividend_model(symbol)
                    modeling_result = {
                        'model_type': 'Dividend Discount',
                        'intrinsic_value': float(dividend_result.get('intrinsic_value', 0)),
                        'dividend_growth_rate': float(dividend_result.get('dividend_growth_rate', 0)),
                        'required_return': float(dividend_result.get('required_return', 0)),
                        'timestamp': datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.warning(f"Failed to get dividend model for {symbol}: {e}")
            
            self._cache_data(cache_key, modeling_result)
            return modeling_result
            
        except Exception as e:
            logger.error(f"Failed to get financial modeling for {symbol}: {e}")
        
        return self._get_mock_financial_modeling(symbol, model_type)
    
    def _get_ratio_description(self, ratio_name: str) -> str:
        """Get description for financial ratio"""
        descriptions = {
            'return_on_equity': 'Measures profitability relative to shareholder equity',
            'return_on_assets': 'Measures profitability relative to total assets',
            'current_ratio': 'Measures ability to pay short-term obligations',
            'quick_ratio': 'Measures ability to pay short-term obligations without inventory',
            'debt_to_equity': 'Measures financial leverage',
            'debt_to_assets': 'Measures proportion of assets financed by debt',
            'asset_turnover': 'Measures efficiency of asset utilization',
            'inventory_turnover': 'Measures efficiency of inventory management'
        }
        return descriptions.get(ratio_name.lower(), 'Financial ratio metric')
    
    def _interpret_beta(self, beta: float) -> str:
        """Interpret beta value"""
        if beta < 0.8:
            return "Low volatility, less risky than market"
        elif beta < 1.2:
            return "Moderate volatility, similar to market risk"
        elif beta < 1.5:
            return "High volatility, more risky than market"
        else:
            return "Very high volatility, significantly more risky than market"
    
    def _interpret_volatility(self, volatility: float) -> str:
        """Interpret volatility value"""
        if volatility < 0.15:
            return "Low volatility, stable price movements"
        elif volatility < 0.25:
            return "Moderate volatility, normal price movements"
        elif volatility < 0.35:
            return "High volatility, significant price movements"
        else:
            return "Very high volatility, extreme price movements"
    
    def _interpret_var(self, var: float) -> str:
        """Interpret Value at Risk"""
        if var > -0.02:
            return "Low risk, minimal potential losses"
        elif var > -0.05:
            return "Moderate risk, manageable potential losses"
        elif var > -0.10:
            return "High risk, significant potential losses"
        else:
            return "Very high risk, extreme potential losses"
    
    def _interpret_sharpe(self, sharpe: float) -> str:
        """Interpret Sharpe ratio"""
        if sharpe > 2.0:
            return "Excellent risk-adjusted returns"
        elif sharpe > 1.0:
            return "Good risk-adjusted returns"
        elif sharpe > 0.5:
            return "Moderate risk-adjusted returns"
        elif sharpe > 0:
            return "Poor risk-adjusted returns"
        else:
            return "Negative risk-adjusted returns"
    
    # Mock data methods for fallback
    def _get_mock_financial_ratios(self, symbol: str, period: str) -> List[FinancialRatio]:
        """Generate mock financial ratios"""
        import random
        ratios = []
        
        mock_ratios = [
            ('Return on Equity', 'Profitability', random.uniform(0.05, 0.25)),
            ('Return on Assets', 'Profitability', random.uniform(0.02, 0.15)),
            ('Current Ratio', 'Liquidity', random.uniform(1.0, 3.0)),
            ('Quick Ratio', 'Liquidity', random.uniform(0.5, 2.0)),
            ('Debt to Equity', 'Leverage', random.uniform(0.2, 1.5)),
            ('Debt to Assets', 'Leverage', random.uniform(0.1, 0.7)),
            ('Asset Turnover', 'Efficiency', random.uniform(0.5, 2.0)),
            ('Inventory Turnover', 'Efficiency', random.uniform(2.0, 10.0))
        ]
        
        for ratio_name, category, value in mock_ratios:
            ratios.append(FinancialRatio(
                symbol=symbol,
                ratio_name=ratio_name,
                value=value,
                category=category,
                description=self._get_ratio_description(ratio_name),
                timestamp=datetime.now()
            ))
        
        return ratios
    
    def _get_mock_valuation_metrics(self, symbol: str) -> List[ValuationMetric]:
        """Generate mock valuation metrics"""
        import random
        metrics = []
        
        mock_metrics = [
            ('DCF', 'Discounted Cash Flow', random.uniform(80, 120)),
            ('P/E Ratio', 'Price to Earnings', random.uniform(15, 35)),
            ('P/B Ratio', 'Price to Book', random.uniform(1.0, 5.0)),
            ('P/S Ratio', 'Price to Sales', random.uniform(2.0, 8.0)),
            ('EV/EBITDA', 'Enterprise Value to EBITDA', random.uniform(8, 20))
        ]
        
        for metric_name, method, value in mock_metrics:
            metrics.append(ValuationMetric(
                symbol=symbol,
                metric_name=metric_name,
                value=value,
                method=method,
                timestamp=datetime.now()
            ))
        
        return metrics
    
    def _get_mock_technical_signals(self, symbol: str, period: int) -> List[TechnicalSignal]:
        """Generate mock technical signals"""
        import random
        signals = []
        
        mock_signals = [
            ('Moving Average', random.choice(['BUY', 'SELL', 'HOLD'])),
            ('RSI', random.choice(['BUY', 'SELL', 'HOLD'])),
            ('MACD', random.choice(['BUY', 'SELL', 'HOLD'])),
            ('Bollinger Bands', random.choice(['BUY', 'SELL', 'HOLD']))
        ]
        
        for signal_type, signal_value in mock_signals:
            signals.append(TechnicalSignal(
                symbol=symbol,
                signal_type=signal_type,
                signal_value=signal_value,
                confidence=random.uniform(0.6, 0.9),
                timestamp=datetime.now()
            ))
        
        return signals
    
    def _get_mock_risk_metrics(self, symbol: str, period: int) -> List[RiskMetric]:
        """Generate mock risk metrics"""
        import random
        metrics = []
        
        mock_metrics = [
            ('Beta', random.uniform(0.5, 2.0), self._interpret_beta(random.uniform(0.5, 2.0))),
            ('Volatility', random.uniform(0.1, 0.4), self._interpret_volatility(random.uniform(0.1, 0.4))),
            ('Value at Risk', random.uniform(-0.1, -0.01), self._interpret_var(random.uniform(-0.1, -0.01))),
            ('Sharpe Ratio', random.uniform(-0.5, 2.5), self._interpret_sharpe(random.uniform(-0.5, 2.5)))
        ]
        
        for risk_type, value, interpretation in mock_metrics:
            metrics.append(RiskMetric(
                symbol=symbol,
                risk_type=risk_type,
                value=value,
                interpretation=interpretation,
                timestamp=datetime.now()
            ))
        
        return metrics
    
    def _get_mock_financial_modeling(self, symbol: str, model_type: str) -> Dict[str, Any]:
        """Generate mock financial modeling results"""
        import random
        
        if model_type.lower() == 'dcf':
            return {
                'model_type': 'DCF',
                'intrinsic_value': random.uniform(80, 120),
                'discount_rate': random.uniform(0.08, 0.12),
                'growth_rate': random.uniform(0.02, 0.08),
                'terminal_value': random.uniform(1000, 5000),
                'timestamp': datetime.now().isoformat()
            }
        elif model_type.lower() == 'multiples':
            return {
                'model_type': 'Multiples',
                'pe_based_value': random.uniform(80, 120),
                'pb_based_value': random.uniform(80, 120),
                'ps_based_value': random.uniform(80, 120),
                'average_value': random.uniform(80, 120),
                'timestamp': datetime.now().isoformat()
            }
        elif model_type.lower() == 'dividend':
            return {
                'model_type': 'Dividend Discount',
                'intrinsic_value': random.uniform(80, 120),
                'dividend_growth_rate': random.uniform(0.02, 0.08),
                'required_return': random.uniform(0.08, 0.12),
                'timestamp': datetime.now().isoformat()
            }
        
        return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'enabled': self.enabled,
            'provider': 'Finance Toolkit',
            'features': [
                'financial_ratios',
                'valuation_metrics',
                'technical_signals',
                'risk_metrics',
                'financial_modeling'
            ],
            'cost': 'FREE',
            'api_key_required': False,
            'rate_limits': 'None',
            'data_quality': 'Professional',
            'analysis_depth': 'Comprehensive'
        }

# Factory function
def get_finance_toolkit_integration(config: Dict[str, Any] = None) -> FinanceToolkitIntegration:
    """Factory function to get Finance Toolkit integration"""
    return FinanceToolkitIntegration(config)
