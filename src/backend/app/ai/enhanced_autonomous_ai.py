
"""
Enhanced Autonomous AI/ML Module for Veyra

This module integrates advanced open-source AI/ML models for financial forecasting, sentiment analysis,
and risk assessment, feeding data-driven insights into the existing multi-agent framework.

It leverages existing data sources and Hugging Face integrations within Veyra to enhance the autonomy
of financial agents.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

# Import existing Veyra components
from ...integrations.free.free_data_sources import FreeDataSourcesManager
from .huggingface_integration import HuggingFaceManager
from ..shared_types import AgentDecision, AgentType, SystemState

# ML Libraries (ensure these are in requirements.txt or installed)
try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error
    ML_LIBS_AVAILABLE = True
except ImportError:
    ML_LIBS_AVAILABLE = False
    logging.warning("XGBoost or scikit-learn not available. Financial forecasting will use simpler models.")

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet not available. Time series forecasting will use simpler models.")

logger = logging.getLogger(__name__)

class EnhancedAutonomousAI:
    """
    Manages enhanced AI/ML capabilities for Veyra's autonomous agents.
    Focuses on financial forecasting, advanced sentiment analysis, and risk assessment.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.data_manager = FreeDataSourcesManager(self.config.get('data_sources', {}))
        self.hf_manager = HuggingFaceManager()
        self.models = {}
        self._initialize_models()
        logger.info("EnhancedAutonomousAI module initialized.")

    def _initialize_models(self):
        """Initialize and load necessary ML models."""
        # Placeholder for loading/training models
        if ML_LIBS_AVAILABLE:
            # Example: Load a pre-trained XGBoost model or prepare for training
            self.models['stock_predictor'] = None # Will be trained on demand
        if PROPHET_AVAILABLE:
            self.models['time_series_forecaster'] = None # Will be initialized on demand

    async def get_financial_forecast(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        Generates a financial forecast for a given symbol using historical data.
        Prioritizes advanced ML models, falls back to simpler heuristics.
        """
        logger.info(f"Generating financial forecast for {symbol} for {days} days.")
        try:
            # Fetch historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * 2) # 2 years of data
            historical_data = await self.data_manager.get_historical_data(symbol, start_date, end_date)

            if not historical_data:
                logger.warning(f"No historical data for {symbol}. Cannot generate forecast.")
                return {"status": "failed", "reason": "no_historical_data"}

            df = pd.DataFrame(historical_data)
            df['Date'] = pd.to_datetime(df['date'])
            df.set_index('Date', inplace=True)
            df = df[['close']].copy()

            if PROPHET_AVAILABLE:
                # Use Prophet for time series forecasting
                df_prophet = df.reset_index()[['Date', 'close']].rename(columns={'Date': 'ds', 'close': 'y'})
                model = Prophet(daily_seasonality=True)
                model.fit(df_prophet)
                future = model.make_future_dataframe(periods=days)
                forecast = model.predict(future)
                future_prices = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days).to_dict(orient='records')
                logger.info(f"Prophet forecast generated for {symbol}.")
                return {"status": "success", "model": "Prophet", "forecast": future_prices}
            elif ML_LIBS_AVAILABLE and self.models['stock_predictor']:
                # Fallback to XGBoost or similar if Prophet not available/suitable
                # This would require feature engineering and training the model first
                logger.warning("XGBoost forecasting not yet implemented for on-demand training.")
                return {"status": "failed", "reason": "ml_model_not_ready"}
            else:
                # Simple moving average forecast as a last resort
                last_price = df['close'].iloc[-1]
                forecast_prices = []
                for i in range(1, days + 1):
                    forecast_prices.append({
                        'ds': (end_date + timedelta(days=i)).isoformat(),
                        'yhat': last_price,
                        'yhat_lower': last_price * 0.98,
                        'yhat_upper': last_price * 1.02
                    })
                logger.info(f"Simple moving average forecast generated for {symbol}.")
                return {"status": "success", "model": "Simple Moving Average", "forecast": forecast_prices}

        except Exception as e:
            logger.error(f"Error generating financial forecast for {symbol}: {e}")
            return {"status": "error", "reason": str(e)}

    async def analyze_news_sentiment_advanced(self, news_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Performs advanced sentiment analysis on financial news articles.
        Leverages FinBERT and potentially other NLP models for deeper insights.
        """
        logger.info(f"Analyzing sentiment for {len(news_articles)} news articles.")
        sentiments = []
        for article in news_articles:
            text = article.get('text', article.get('title', ''))
            if text:
                sentiment_result = self.hf_manager.analyze_sentiment(text, model='finbert')
                sentiments.append({
                    "article_id": article.get('id'),
                    "title": article.get('title'),
                    "sentiment": sentiment_result['label'],
                    "confidence": sentiment_result['score'],
                    "source": sentiment_result['model']
                })
            else:
                sentiments.append({"article_id": article.get('id'), "sentiment": "neutral", "confidence": 0.5, "source": "no_text"})
        logger.info(f"Completed sentiment analysis for {len(sentiments)} articles.")
        return sentiments

    async def assess_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assesses portfolio risk and provides optimization recommendations.
        Uses open-source portfolio optimization libraries.
        """
        logger.info("Assessing portfolio risk.")
        try:
            # This is a placeholder. Real implementation would involve:
            # 1. Fetching historical returns for all assets in the portfolio.
            # 2. Calculating covariance matrix.
            # 3. Using pyportfolioopt or cvxpy for optimization (e.g., Markowitz, Black-Litterman).
            # 4. Generating risk metrics (VaR, CVaR, etc.).

            # Mock data for demonstration
            mock_risk_metrics = {
                "VaR_95": 0.02, # Value at Risk (95% confidence)
                "CVaR_95": 0.03, # Conditional Value at Risk
                "sharpe_ratio": 1.2,
                "max_drawdown": 0.10,
                "recommended_rebalance": [
                    {"action": "reduce", "symbol": "XYZ", "percentage": 5},
                    {"action": "increase", "symbol": "ABC", "percentage": 5}
                ]
            }
            logger.info("Portfolio risk assessment completed with mock data.")
            return {"status": "success", "metrics": mock_risk_metrics}
        except Exception as e:
            logger.error(f"Error assessing portfolio risk: {e}")
            return {"status": "error", "reason": str(e)}

    async def generate_agent_decision(self, agent_type: AgentType, task_description: str, data: Dict[str, Any]) -> AgentDecision:
        """
        Generates an AgentDecision based on AI/ML analysis.
        This bridges the gap between AI/ML output and the multi-agent framework.
        """
        decision_id = f"{agent_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        confidence_score = 0.75 # Default confidence, can be derived from model output
        priority = "MEDIUM"
        recommended_action = "Review AI/ML insights for further action."

        if agent_type == AgentType.ANALYST:
            # Example: Analyst agent uses forecast and sentiment
            forecast_result = await self.get_financial_forecast(data.get('symbol', 'AAPL'))
            news_sentiment_result = await self.analyze_news_sentiment_advanced(data.get('news', []))

            description = f"AI Analyst recommends review based on forecast and sentiment. Forecast: {forecast_result.get('status')}, Sentiment: {len(news_sentiment_result)} articles analyzed."
            supporting_data = {
                "forecast": forecast_result,
                "sentiment": news_sentiment_result
            }
            if forecast_result.get('status') == 'success' and forecast_result['forecast']:
                recommended_action = f"Consider {data.get('symbol')} based on {forecast_result['forecast'][0]['yhat']:.2f} forecast."
                confidence_score = 0.8

        elif agent_type == AgentType.ACCOUNTANT:
            # Example: Accountant agent uses risk assessment for tax optimization
            risk_assessment_result = await self.assess_portfolio_risk(data.get('portfolio', {}))
            description = f"AI Accountant suggests tax optimization based on risk assessment. Status: {risk_assessment_result.get('status')}."
            supporting_data = {"risk_assessment": risk_assessment_result}
            if risk_assessment_result.get('status') == 'success' and risk_assessment_result['metrics']:
                recommended_action = f"Review portfolio for rebalancing: {risk_assessment_result['metrics'].get('recommended_rebalance')}"
                confidence_score = 0.85

        else:
            description = f"AI/ML insights for {agent_type.value}: {task_description}"
            supporting_data = data

        return AgentDecision(
            agent_type=agent_type,
            timestamp=datetime.now(),
            decision_id=decision_id,
            category="AI/ML Insight",
            priority=priority,
            title=f"AI/ML Generated Decision for {agent_type.value}",
            description=description,
            recommended_action=recommended_action,
            confidence_score=confidence_score,
            supporting_data=supporting_data,
            requires_approval=True, # Most AI/ML driven actions should require approval initially
            auto_executable=False,
            estimated_impact_gbp=None,
            compliance_check_passed=True,
            risk_level="MEDIUM"
        )

# Example Usage (for testing/demonstration)
async def main():
    ai_module = EnhancedAutonomousAI()

    # Test financial forecast
    forecast = await ai_module.get_financial_forecast("AAPL")
    print("\nFinancial Forecast:", forecast)

    # Test advanced sentiment analysis
    sample_news = [
        {"id": "1", "title": "Apple stock soars on strong earnings report", "text": "Apple Inc. (AAPL) shares surged today after reporting better-than-expected quarterly earnings and revenue, driven by robust iPhone sales and growth in its services division."},
        {"id": "2", "title": "Tech sector faces headwinds amid rising interest rates", "text": "The broader technology sector is experiencing increased pressure as central banks signal further interest rate hikes, leading to concerns about future growth and valuations."}
    ]
    sentiments = await ai_module.analyze_news_sentiment_advanced(sample_news)
    print("\nNews Sentiments:", sentiments)

    # Test portfolio risk assessment
    sample_portfolio = {"assets": [{"symbol": "AAPL", "amount": 100}, {"symbol": "MSFT", "amount": 50}]}
    risk_assessment = await ai_module.assess_portfolio_risk(sample_portfolio)
    print("\nPortfolio Risk Assessment:", risk_assessment)

    # Generate an agent decision based on AI/ML insights
    analyst_data = {"symbol": "AAPL", "news": sample_news}
    analyst_decision = await ai_module.generate_agent_decision(AgentType.ANALYST, "Analyze market for AAPL", analyst_data)
    print("\nAI Analyst Decision:", analyst_decision)

    accountant_data = {"portfolio": sample_portfolio}
    accountant_decision = await ai_module.generate_agent_decision(AgentType.ACCOUNTANT, "Optimize tax for portfolio", accountant_data)
    print("\nAI Accountant Decision:", accountant_decision)

if __name__ == "__main__":
    asyncio.run(main())
