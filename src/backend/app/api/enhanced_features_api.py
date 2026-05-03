"""
Enhanced Features API for Financial Master

FastAPI routers for:
- Anomaly Detection
- Gamification/Rewards
- Social Activity Feed
- Voice Commands
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, WebSocket
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.trading.anomaly_detection import anomaly_detector, AnomalyType, analyze_trade_for_anomalies
from app.gamification.rewards_system import rewards_system, ActivityType, award_points
from app.social.activity_feed import activity_feed, ActivityCategory, share_trade, share_strategy
from app.ai.voice_commands import voice_processor, process_text_command
from app.education.elearning import elearning, CourseLevel
from app.marketplace.job_marketplace import jobs
from app.portfolio.advanced_analytics import analytics
from app.market_data.websocket_feeds import feed_manager, FeedType
from app.ai.news_sentiment import sentiment_analyzer
from app.trading.advanced_orders import order_manager, OrderType, OrderStatus
from app.reporting.tax_compliance import tax_compliance
from app.accounts.multi_account import account_manager, AccountType
from app.journal.trading_journal import trading_journal
from app.notifications.smart_alerts import smart_alerts, AlertType, AlertCondition
from app.backtesting.engine import backtest_engine, BacktestResult
from app.social.copy_trading_system import copy_trading
from app.execution.liquidity_aggregator import liquidity_aggregator
from app.derivatives.options_trading import options_trading, OptionsPricing, OptionType, OptionStrategy
from app.hft.execution_engine import hft_engine, HFTOrder, Tick
from app.risk.risk_management import risk_manager, RiskLevel, RiskLimit
from app.compliance.regulatory_reporting import compliance_engine, Regulation, TradeReport
from app.data_pipeline.etl_engine import etl_pipeline, DataSource, DataType
from app.feature_store.feature_engineering import feature_store
from app.simulation.paper_trading import paper_trading, PaperOrder, OrderStatus

router = APIRouter(prefix="/api/v1/enhanced", tags=["enhanced-features"])


# ========== ANOMALY DETECTION ENDPOINTS ==========

@router.post("/anomaly/analyze")
async def analyze_for_anomalies(
    symbol: str,
    price: float,
    volume: float
) -> Dict[str, Any]:
    """
    Analyze a trade for anomalies.
    
    - **symbol**: Trading pair symbol (e.g., BTC/USD)
    - **price**: Trade price
    - **volume**: Trade volume
    
    Returns anomaly alert if detected.
    """
    alert = await analyze_trade_for_anomalies(symbol, price, volume)
    
    if alert:
        return {
            'anomaly_detected': True,
            'alert': alert.to_dict()
        }
    
    return {
        'anomaly_detected': False,
        'message': 'No anomalies detected'
    }


@router.get("/anomaly/baseline/{symbol}")
async def get_baseline_metrics(symbol: str) -> Dict[str, Any]:
    """Get baseline metrics for a symbol."""
    metrics = anomaly_detector.get_baseline_metrics(symbol)
    
    if not metrics:
        raise HTTPException(status_code=404, detail=f"No data for symbol {symbol}")
    
    return {
        'symbol': symbol,
        'baseline_metrics': metrics
    }


@router.get("/anomaly/types")
async def get_anomaly_types() -> List[str]:
    """Get list of detectable anomaly types."""
    return [t.value for t in AnomalyType]


# ========== GAMIFICATION ENDPOINTS ==========

@router.post("/gamification/activity")
async def record_activity(
    user_id: str,
    activity_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Record user activity and award points.
    
    - **user_id**: User identifier
    - **activity_type**: Type of activity (e.g., trade_executed, strategy_created)
    - **metadata**: Additional activity data
    """
    try:
        activity_enum = ActivityType(activity_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid activity type: {activity_type}")
    
    result = await award_points(user_id, activity_enum, metadata)
    return result


@router.get("/gamification/profile/{user_id}")
async def get_gamification_profile(user_id: str) -> Dict[str, Any]:
    """Get user's complete gamification profile."""
    profile = rewards_system.get_user_stats(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    return profile


@router.get("/gamification/leaderboard")
async def get_leaderboard(top_n: int = Query(10, ge=1, le=100)) -> List[Dict[str, Any]]:
    """Get global leaderboard."""
    return rewards_system.get_leaderboard(top_n)


@router.get("/gamification/achievements")
async def get_achievements_catalog() -> Dict[str, Any]:
    """Get all available achievements."""
    achievements = {
        k: v.to_dict() 
        for k, v in rewards_system.achievements_catalog.items()
    }
    
    return {
        'total_achievements': len(achievements),
        'achievements': achievements
    }


@router.post("/gamification/redeem")
async def redeem_points(
    user_id: str,
    points_cost: int,
    reward_type: str
) -> Dict[str, Any]:
    """Redeem points for rewards."""
    success = rewards_system.redeem_points(user_id, points_cost, reward_type)
    
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient points")
    
    return {
        'success': True,
        'points_redeemed': points_cost,
        'reward': reward_type,
        'remaining_points': rewards_system.get_or_create_profile(user_id).total_points
    }


@router.get("/gamification/activity-types")
async def get_activity_types() -> Dict[str, int]:
    """Get activity types and their point values."""
    return {
        k.value: v 
        for k, v in rewards_system.ACTIVITY_POINTS.items()
    }


# ========== SOCIAL ACTIVITY FEED ENDPOINTS ==========

@router.get("/social/feed/{user_id}")
async def get_activity_feed(
    user_id: str,
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """
    Get personalized activity feed for a user.
    
    - **user_id**: User identifier
    - **category**: Filter by category (trade, strategy, achievement, social)
    - **limit**: Number of activities to return
    - **offset**: Pagination offset
    """
    category_enum = None
    if category:
        try:
            category_enum = ActivityCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    feed = await activity_feed.get_feed(user_id, category_enum, limit, offset)
    return feed


@router.post("/social/share/trade")
async def share_trade_activity(
    user_id: str,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    pnl: Optional[float] = None
) -> Dict[str, Any]:
    """Share a trade to the activity feed."""
    activity = await share_trade(user_id, symbol, side, quantity, price, pnl)
    return {
        'success': True,
        'activity': activity.to_dict()
    }


@router.post("/social/share/strategy")
async def share_strategy_activity(
    user_id: str,
    strategy_name: str,
    strategy_id: str
) -> Dict[str, Any]:
    """Share a strategy to the activity feed."""
    activity = await share_strategy(user_id, strategy_name, strategy_id)
    return {
        'success': True,
        'activity': activity.to_dict()
    }


@router.post("/social/follow/{user_id}")
async def follow_user(user_id: str, target_user_id: str) -> Dict[str, Any]:
    """Follow a user."""
    success = await activity_feed.follow_user(user_id, target_user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Cannot follow user")
    
    return {
        'success': True,
        'message': f"Now following {target_user_id}"
    }


@router.post("/social/unfollow/{user_id}")
async def unfollow_user(user_id: str, target_user_id: str) -> Dict[str, Any]:
    """Unfollow a user."""
    success = await activity_feed.unfollow_user(user_id, target_user_id)
    
    return {
        'success': success,
        'message': f"Unfollowed {target_user_id}" if success else "Not following this user"
    }


@router.post("/social/like/{activity_id}")
async def like_activity(user_id: str, activity_id: str) -> Dict[str, Any]:
    """Like an activity."""
    success = await activity_feed.like_activity(user_id, activity_id)
    
    return {
        'success': success,
        'message': "Activity liked" if success else "Already liked"
    }


@router.post("/social/comment/{activity_id}")
async def comment_on_activity(
    user_id: str,
    activity_id: str,
    comment: str
) -> Dict[str, Any]:
    """Comment on an activity."""
    comment_data = await activity_feed.comment_on_activity(user_id, activity_id, comment)
    
    if not comment_data:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return {
        'success': True,
        'comment': comment_data
    }


@router.get("/social/trending")
async def get_trending_activities(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(10, ge=1, le=50)
) -> List[Dict[str, Any]]:
    """Get trending activities."""
    return activity_feed.get_trending(hours, limit)


@router.get("/social/profile/{user_id}")
async def get_social_profile(user_id: str) -> Dict[str, Any]:
    """Get user's social profile and stats."""
    profile = activity_feed.get_user_stats(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    return profile


# ========== VOICE COMMAND ENDPOINTS ==========

@router.post("/voice/command")
async def process_voice_command_endpoint(
    command: str,
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a voice/text command.
    
    - **command**: Voice command text
    - **language**: Language code (optional)
    
    Examples:
    - "Buy 0.5 BTC"
    - "Check my balance"
    - "Start the grid bot"
    - "What's the price of Ethereum"
    """
    result = await process_text_command(command)
    return result


@router.post("/voice/upload")
async def process_voice_upload(
    audio: UploadFile = File(...),
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process uploaded audio file for voice commands.
    
    Supports WAV, MP3, M4A formats.
    """
    try:
        audio_data = await audio.read()
        
        from app.ai.voice_commands import process_voice_command
        result = await process_voice_command(audio_data, language)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")


@router.get("/voice/commands")
async def get_supported_voice_commands() -> Dict[str, List[str]]:
    """Get list of supported voice commands."""
    return voice_processor.get_supported_commands()


@router.get("/voice/history")
async def get_voice_command_history(limit: int = Query(10, ge=1, le=50)) -> List[Dict[str, Any]]:
    """Get recent voice command history."""
    return voice_processor.get_command_history(limit)


# ========== WEBSOCKET FOR REAL-TIME FEED ==========

@router.websocket("/social/ws/{user_id}")
async def social_feed_websocket(websocket: WebSocket, user_id: str):
    """WebSocket for real-time social feed updates."""
    await websocket.accept()
    
    # Subscribe to feed
    queue = await activity_feed.subscribe_to_feed(user_id)
    
    try:
        while True:
            # Wait for new activities
            activity = await queue.get()
            await websocket.send_json(activity)
            
    except Exception as e:
        # Unsubscribe on disconnect
        await activity_feed.unsubscribe_from_feed(user_id, queue)


# ========== COMBINED DASHBOARD ENDPOINT ==========

@router.get("/dashboard/{user_id}")
async def get_enhanced_dashboard(user_id: str) -> Dict[str, Any]:
    """
    Get complete enhanced dashboard for a user.
    
    Includes:
    - Gamification stats
    - Social profile
    - Recent anomalies
    - Voice command history
    """
    # Get gamification stats
    gamification = rewards_system.get_user_stats(user_id)
    
    # Get social profile
    social = activity_feed.get_user_stats(user_id)
    
    # Get recent voice commands
    voice_history = voice_processor.get_command_history(5)
    
    return {
        'user_id': user_id,
        'gamification': gamification,
        'social': social,
        'voice_history': voice_history,
        'anomalies': anomaly_detector.get_recent_anomalies(hours=24),
        'timestamp': datetime.now().isoformat()
    }


# ========== E-LEARNING ENDPOINTS ==========

@router.get("/education/courses")
async def get_courses(level: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get available courses with optional level filter."""
    course_level = CourseLevel(level) if level else None
    return await elearning.get_courses(course_level)

@router.post("/education/enroll")
async def enroll_course(user_id: str, course_id: str) -> Dict[str, Any]:
    """Enroll a user in a course."""
    return await elearning.enroll(user_id, course_id)

@router.post("/education/progress")
async def update_progress(user_id: str, course_id: str, percent: float) -> Dict[str, Any]:
    """Update course progress."""
    return await elearning.update_progress(user_id, course_id, percent)

@router.post("/education/certificate")
async def issue_certificate(user_id: str, course_id: str) -> Dict[str, Any]:
    """Issue blockchain certificate for completed course."""
    cert_hash = await elearning.issue_certificate(user_id, course_id)
    if cert_hash:
        return {'success': True, 'certificate_hash': cert_hash}
    return {'success': False, 'error': 'Certificate not available'}


# ========== JOB MARKETPLACE ENDPOINTS ==========

@router.post("/jobs/post")
async def post_job(job_data: Dict[str, Any]) -> Dict[str, str]:
    """Post a new job listing."""
    job_id = await jobs.post_job(job_data)
    return {'job_id': job_id, 'status': 'posted'}

@router.get("/jobs/search")
async def search_jobs(
    category: Optional[str] = None,
    job_type: Optional[str] = None,
    location: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search job listings."""
    return await jobs.search_jobs(category, job_type, location)

@router.post("/jobs/cv/store")
async def store_cv(user_id: str, cv_data: str) -> Dict[str, str]:
    """Store CV hash on blockchain."""
    cv_hash = await jobs.store_cv_blockchain(user_id, cv_data)
    return {'user_id': user_id, 'cv_hash': cv_hash}

@router.post("/jobs/apply")
async def apply_job(user_id: str, job_id: str, message: str) -> Dict[str, Any]:
    """Apply for a job with blockchain-verified CV."""
    return await jobs.apply(user_id, job_id, message)


# ========== PORTFOLIO ANALYTICS ENDPOINTS ==========

@router.post("/analytics/portfolio/metrics")
async def get_portfolio_metrics(
    returns: List[float],
    benchmark_returns: Optional[List[float]] = None,
    risk_free_rate: float = 0.02
) -> Dict[str, Any]:
    """Calculate professional portfolio metrics."""
    import pandas as pd
    
    returns_series = pd.Series(returns)
    benchmark_series = pd.Series(benchmark_returns) if benchmark_returns else None
    
    metrics = analytics.calculate_metrics(returns_series, benchmark_series, risk_free_rate)
    
    return {
        'total_return': metrics.total_return,
        'total_return_pct': metrics.total_return_pct,
        'sharpe_ratio': metrics.sharpe_ratio,
        'max_drawdown': metrics.max_drawdown,
        'volatility': metrics.volatility,
        'alpha': metrics.alpha,
        'beta': metrics.beta,
        'var_95': metrics.var_95
    }

@router.post("/analytics/portfolio/monte-carlo")
async def monte_carlo_simulation(
    mean_return: float,
    volatility: float,
    initial_value: float = 100000,
    days: int = 252,
    simulations: int = 1000
) -> Dict[str, Any]:
    """Run Monte Carlo simulation for portfolio projections."""
    return analytics.monte_carlo_simulation(mean_return, volatility, initial_value, days, simulations)

@router.post("/analytics/portfolio/efficient-frontier")
async def efficient_frontier(returns_data: Dict[str, List[float]]) -> List[Dict[str, Any]]:
    """Generate efficient frontier for portfolio optimization."""
    import pandas as pd
    
    returns_df = pd.DataFrame(returns_data)
    return analytics.efficient_frontier(returns_df)


# ========== MARKET DATA WEBSOCKET ENDPOINTS ==========

@router.post("/market/subscribe")
async def subscribe_market_data(client_id: str, symbols: List[str], feed_type: str = "ticker"):
    """Subscribe to real-time market data feed."""
    ft = FeedType(feed_type)
    await feed_manager.subscribe(client_id, symbols, ft)
    return {'success': True, 'subscribed': len(symbols), 'feed_type': feed_type}

@router.post("/market/unsubscribe")
async def unsubscribe_market_data(client_id: str, symbols: List[str], feed_type: str = "ticker"):
    """Unsubscribe from market data feed."""
    ft = FeedType(feed_type)
    await feed_manager.unsubscribe(client_id, symbols, ft)
    return {'success': True, 'unsubscribed': len(symbols)}


# ========== NEWS SENTIMENT ANALYSIS ENDPOINTS ==========

@router.post("/sentiment/analyze")
async def analyze_news_sentiment(headline: str, source: str = "news") -> Dict[str, Any]:
    """Analyze sentiment of a news headline."""
    result = await sentiment_analyzer.analyze(headline, source)
    return result.to_dict()

@router.get("/sentiment/symbol/{symbol}")
async def get_symbol_sentiment(symbol: str, hours: int = 24) -> Dict[str, Any]:
    """Get aggregated sentiment for a symbol."""
    return await sentiment_analyzer.get_symbol_sentiment(symbol, hours)

@router.post("/sentiment/batch")
async def batch_sentiment_analysis(headlines: List[str]) -> List[Dict[str, Any]]:
    """Analyze multiple headlines."""
    results = await sentiment_analyzer.scan_news(headlines)
    return [r.to_dict() for r in results]


# ========== ADVANCED ORDER ENDPOINTS ==========

@router.post("/orders/market")
async def place_market_order(symbol: str, side: str, quantity: float) -> Dict[str, Any]:
    """Place a market order."""
    order = await order_manager.place_market_order(symbol, side, quantity)
    return {'order_id': order.id, 'status': order.status.value, 'symbol': symbol}

@router.post("/orders/limit")
async def place_limit_order(symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
    """Place a limit order."""
    order = await order_manager.place_limit_order(symbol, side, quantity, price)
    return {'order_id': order.id, 'status': order.status.value, 'price': price}

@router.post("/orders/trailing-stop")
async def place_trailing_stop(symbol: str, side: str, quantity: float, trailing_pct: float) -> Dict[str, Any]:
    """Place a trailing stop order."""
    order = await order_manager.place_trailing_stop(symbol, side, quantity, trailing_pct)
    return {'order_id': order.id, 'trailing_pct': trailing_pct, 'status': order.status.value}

@router.post("/orders/oco")
async def place_oco_order(symbol: str, side: str, quantity: float, 
                         limit_price: float, stop_price: float) -> Dict[str, Any]:
    """Place One-Cancels-Other order."""
    result = await order_manager.place_oco_order(symbol, side, quantity, limit_price, stop_price)
    return {
        'parent_id': result['parent_id'],
        'limit_order_id': result['limit_order'].id,
        'stop_order_id': result['stop_order'].id
    }

@router.post("/orders/bracket")
async def place_bracket_order(symbol: str, side: str, quantity: float,
                              entry_price: float, take_profit: float, 
                              stop_loss: float) -> Dict[str, Any]:
    """Place bracket order (entry + TP + SL)."""
    result = await order_manager.place_bracket_order(symbol, side, quantity, entry_price, take_profit, stop_loss)
    return {
        'parent_id': result['parent_id'],
        'entry_order_id': result['entry'].id,
        'tp_order_id': result['take_profit'].id,
        'sl_order_id': result['stop_loss'].id
    }

@router.post("/orders/iceberg")
async def place_iceberg_order(symbol: str, side: str, total_quantity: float,
                            display_qty: float, price: float) -> Dict[str, Any]:
    """Place iceberg order (hidden large order)."""
    order = await order_manager.place_iceberg_order(symbol, side, total_quantity, display_qty, price)
    return {
        'order_id': order.id,
        'total_qty': total_quantity,
        'display_qty': display_qty,
        'hidden_qty': order.hidden_qty,
        'status': order.status.value
    }

@router.post("/orders/cancel/{order_id}")
async def cancel_order(order_id: str) -> Dict[str, Any]:
    """Cancel an order."""
    success = await order_manager.cancel_order(order_id)
    return {'success': success, 'order_id': order_id}

@router.get("/orders/open")
async def get_open_orders(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all open orders."""
    orders = await order_manager.get_open_orders(symbol)
    return [{
        'order_id': o.id,
        'symbol': o.symbol,
        'side': o.side,
        'type': o.order_type.value,
        'quantity': o.quantity,
        'price': o.price,
        'status': o.status.value
    } for o in orders]


# ========== TAX COMPLIANCE ENDPOINTS ==========

@router.post("/tax/record-trade")
async def record_trade_for_tax(user_id: str, trade: Dict[str, Any]) -> Dict[str, str]:
    """Record a trade for tax reporting."""
    trade_id = await tax_compliance.record_trade(user_id, trade)
    return {'trade_id': trade_id, 'status': 'recorded'}

@router.get("/tax/report/{user_id}/{year}")
async def generate_tax_report(user_id: str, year: int, method: str = "fifo") -> Dict[str, Any]:
    """Generate annual tax report."""
    return await tax_compliance.generate_tax_report(user_id, year, method)

@router.post("/tax/unrealized-gains/{user_id}")
async def get_unrealized_gains(user_id: str, current_prices: Dict[str, float]) -> Dict[str, Any]:
    """Calculate unrealized gains/losses."""
    return await tax_compliance.get_unrealized_gains(user_id, current_prices)


# ========== MULTI-ACCOUNT MANAGEMENT ENDPOINTS ==========

@router.post("/accounts/create")
async def create_account(user_id: str, name: str, account_type: str, 
                        risk_limits: Optional[Dict] = None) -> Dict[str, Any]:
    """Create a new trading account."""
    acc_type = AccountType(account_type)
    account = await account_manager.create_account(user_id, name, acc_type, risk_limits)
    return {
        'account_id': account.id,
        'name': account.name,
        'type': account.account_type.value,
        'is_default': account.is_default,
        'risk_limits': account.risk_limits
    }

@router.get("/accounts/{user_id}")
async def get_user_accounts(user_id: str) -> List[Dict[str, Any]]:
    """Get all accounts for a user."""
    accounts = await account_manager.get_user_accounts(user_id)
    return [{
        'id': acc.id,
        'name': acc.name,
        'type': acc.account_type.value,
        'balances': acc.balances,
        'value_usd': acc.total_value_usd,
        'is_default': acc.is_default
    } for acc in accounts]

@router.get("/accounts/summary/{user_id}")
async def get_account_summary(user_id: str) -> Dict[str, Any]:
    """Get account summary."""
    return await account_manager.get_account_summary(user_id)

@router.post("/accounts/transfer")
async def transfer_between_accounts(user_id: str, from_account: str, 
                                   to_account: str, asset: str, 
                                   amount: float) -> Dict[str, Any]:
    """Transfer assets between accounts."""
    return await account_manager.transfer_between_accounts(user_id, from_account, to_account, asset, amount)

@router.post("/accounts/check-risk/{account_id}")
async def check_risk_limits(account_id: str, proposed_trade: Dict[str, Any]) -> Dict[str, Any]:
    """Check if trade violates risk limits."""
    return await account_manager.check_risk_limits(account_id, proposed_trade)


# ========== TRADING JOURNAL ENDPOINTS ==========

@router.post("/journal/entry")
async def create_journal_entry(user_id: str, trade_data: Dict[str, Any], 
                              reflection: Dict[str, Any]) -> Dict[str, str]:
    """Create a trading journal entry."""
    entry = await trading_journal.create_entry(user_id, trade_data, reflection)
    return {'entry_id': entry.entry.entry_id, 'status': 'created'}

@router.get("/journal/entries/{user_id}")
async def get_journal_entries(user_id: str, 
                              symbol: Optional[str] = None,
                              strategy: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get journal entries with filters."""
    filters = {}
    if symbol:
        filters['symbol'] = symbol
    if strategy:
        filters['strategy'] = strategy
    return await trading_journal.get_entries(user_id, filters if filters else None)

@router.get("/journal/stats/{user_id}")
async def get_journal_stats(user_id: str) -> Dict[str, Any]:
    """Get trading performance statistics."""
    return await trading_journal.get_performance_stats(user_id)

@router.get("/journal/insights/{user_id}")
async def get_journal_insights(user_id: str) -> List[str]:
    """Get AI-generated insights from trading patterns."""
    return await trading_journal.generate_insights(user_id)


# ========== SMART ALERTS ENDPOINTS ==========

@router.post("/alerts/create")
async def create_alert(user_id: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new price/P&L alert."""
    alert = await smart_alerts.create_alert(user_id, alert_data)
    return {
        'alert_id': alert.alert_id,
        'type': alert.alert_type.value,
        'symbol': alert.symbol,
        'condition': alert.condition.value,
        'threshold': alert.threshold,
        'channels': alert.notification_channels
    }

@router.get("/alerts/{user_id}")
async def get_user_alerts(user_id: str, active_only: bool = False) -> List[Dict[str, Any]]:
    """Get all alerts for a user."""
    return await smart_alerts.get_user_alerts(user_id, active_only)

@router.post("/alerts/toggle/{alert_id}")
async def toggle_alert(alert_id: str) -> Dict[str, Any]:
    """Toggle alert active status."""
    new_status = await smart_alerts.toggle_alert(alert_id)
    return {'alert_id': alert_id, 'is_active': new_status}

@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str) -> Dict[str, bool]:
    """Delete an alert."""
    success = await smart_alerts.delete_alert(alert_id)
    return {'deleted': success}

@router.post("/alerts/preset/{user_id}")
async def create_preset_alerts(user_id: str, preset: str) -> Dict[str, Any]:
    """Create preset alert configuration (conservative/aggressive/hodler)."""
    alert_ids = await smart_alerts.create_preset_alerts(user_id, preset)
    return {'preset': preset, 'created_alerts': len(alert_ids), 'alert_ids': alert_ids}


# ========== BACKTESTING ENDPOINTS ==========

@router.post("/backtest/run")
async def run_backtest(strategy_name: str,
                      price_data: List[Dict[str, Any]],
                      initial_capital: float = 100000.0,
                      commission: float = 0.001) -> Dict[str, Any]:
    """Run strategy backtest with historical data."""
    import pandas as pd
    
    # Convert to DataFrame
    df = pd.DataFrame(price_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Simple momentum strategy as example
    def momentum_strategy(data):
        if len(data) < 20:
            return 0
        sma20 = data['close'].rolling(20).mean().iloc[-1]
        current = data['close'].iloc[-1]
        return 1 if current > sma20 else -1 if current < sma20 else 0
    
    result = await backtest_engine.run_backtest(
        momentum_strategy, df, initial_capital=initial_capital, commission=commission
    )
    
    return result.to_dict()

@router.post("/backtest/optimize")
async def optimize_parameters(strategy_name: str,
                            price_data: List[Dict[str, Any]],
                            param_grid: Dict[str, List[Any]]) -> Dict[str, Any]:
    """Grid search for optimal strategy parameters."""
    import pandas as pd
    
    df = pd.DataFrame(price_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    def strategy(data, **params):
        # Generic parameterizable strategy
        fast = params.get('fast_period', 10)
        slow = params.get('slow_period', 20)
        
        if len(data) < slow:
            return 0
        
        fast_ma = data['close'].rolling(fast).mean().iloc[-1]
        slow_ma = data['close'].rolling(slow).mean().iloc[-1]
        
        return 1 if fast_ma > slow_ma else -1 if fast_ma < slow_ma else 0
    
    return await backtest_engine.optimize_parameters(strategy, df, param_grid)

@router.post("/backtest/walk-forward")
async def walk_forward_analysis(strategy_name: str,
                              price_data: List[Dict[str, Any]],
                              train_size: int = 252,
                              test_size: int = 63) -> List[Dict]:
    """Walk-forward optimization to prevent overfitting."""
    import pandas as pd
    
    df = pd.DataFrame(price_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    def simple_strategy(data):
        if len(data) < 20:
            return 0
        return 1 if data['close'].iloc[-1] > data['close'].rolling(20).mean().iloc[-1] else -1
    
    return await backtest_engine.walk_forward_analysis(simple_strategy, df, train_size, test_size)


# ========== COPY TRADING ENDPOINTS ==========

@router.post("/copy/register-trader")
async def register_as_trader(user_id: str, username: str,
                            monthly_fee: float = 0,
                            performance_fee_pct: float = 20) -> Dict[str, Any]:
    """Register as pro trader for others to copy."""
    trader = await copy_trading.register_as_trader(user_id, username, monthly_fee, performance_fee_pct)
    return {
        'trader_id': trader.user_id,
        'username': trader.username,
        'monthly_fee': trader.monthly_fee,
        'performance_fee': trader.performance_fee_pct
    }

@router.post("/copy/start")
async def start_copy_trading(follower_id: str, trader_id: str,
                            allocation: float,
                            copy_percentage: float = 100.0,
                            max_position_size: Optional[float] = None) -> Dict[str, Any]:
    """Start copying a trader's trades."""
    copy = await copy_trading.start_copying(
        follower_id, trader_id, allocation, copy_percentage, max_position_size
    )
    return {
        'copy_id': copy.copy_id,
        'trader_id': copy.trader_id,
        'allocation': copy.allocation,
        'copy_percentage': copy.copy_percentage,
        'status': 'active'
    }

@router.post("/copy/stop/{copy_id}")
async def stop_copy_trading(copy_id: str) -> Dict[str, Any]:
    """Stop copying a trader."""
    success = await copy_trading.stop_copying(copy_id)
    return {'copy_id': copy_id, 'stopped': success}

@router.get("/copy/top-traders")
async def get_top_traders(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top performing traders to copy."""
    return await copy_trading.get_top_traders(limit)

@router.get("/copy/portfolio/{follower_id}")
async def get_copy_portfolio(follower_id: str) -> Dict[str, Any]:
    """Get copy trading portfolio for a follower."""
    return await copy_trading.get_follower_portfolio(follower_id)

@router.post("/copy/update-stats/{trader_id}")
async def update_trader_stats(trader_id: str,
                             return_30d: float,
                             win_rate: float,
                             sharpe: float,
                             max_dd: float) -> Dict[str, str]:
    """Update trader performance statistics."""
    await copy_trading.update_trader_stats(trader_id, return_30d, win_rate, sharpe, max_dd)
    return {'status': 'updated', 'trader_id': trader_id}


# ========== LIQUIDITY AGGREGATION ENDPOINTS ==========

@router.get("/liquidity/quote/{symbol}")
async def get_liquidity_quote(symbol: str, side: str, size: float) -> Dict[str, Any]:
    """Get best aggregated quote across exchanges."""
    quote = await liquidity_aggregator.get_best_quote(symbol, side, size)
    if not quote:
        return {'error': 'No liquidity available'}
    
    return {
        'symbol': quote.symbol,
        'best_bid': quote.best_bid,
        'best_ask': quote.best_ask,
        'best_bid_exchange': quote.best_bid_exchange,
        'best_ask_exchange': quote.best_ask_exchange,
        'spread': quote.spread,
        'effective_price': quote.effective_price,
        'total_bid_liquidity': quote.total_bid_liquidity,
        'total_ask_liquidity': quote.total_ask_liquidity,
        'sources': len(quote.sources)
    }

@router.post("/liquidity/route")
async def smart_order_routing(symbol: str, side: str, size: float) -> Dict[str, Any]:
    """Get smart order routing plan across multiple exchanges."""
    return await liquidity_aggregator.smart_routing(symbol, side, size)

@router.post("/liquidity/update")
async def update_liquidity_sources(market_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """Update liquidity sources with new market data."""
    await liquidity_aggregator.update_all_sources(market_data)
    return {'status': 'updated', 'symbols_updated': len(market_data)}


# ========== OPTIONS TRADING ENDPOINTS ==========

@router.post("/options/price")
async def calculate_option_price(S: float, K: float, T_days: int,
                                 r: float, sigma: float,
                                 option_type: str) -> Dict[str, float]:
    """Calculate option price and Greeks using Black-Scholes."""
    T = T_days / 365
    opt_type = OptionType(option_type)
    pricing = OptionsPricing.calculate_price(S, K, T, r, sigma, opt_type)
    return pricing

@router.post("/options/implied-vol")
async def calculate_implied_volatility(S: float, K: float, T_days: int,
                                       r: float, market_price: float,
                                       option_type: str) -> Dict[str, float]:
    """Calculate implied volatility from market price."""
    T = T_days / 365
    opt_type = OptionType(option_type)
    iv = OptionsPricing.implied_volatility(S, K, T, r, market_price, opt_type)
    return {'implied_volatility': iv, 'market_price': market_price}

@router.post("/options/buy")
async def buy_option_contract(user_id: str, underlying: str,
                              option_type: str, strike: float,
                              expiry_days: int, quantity: int,
                              current_price: float, volatility: float) -> Dict[str, Any]:
    """Buy an option contract."""
    position = await options_trading.buy_option(
        user_id, underlying, option_type, strike, expiry_days, quantity,
        current_price, volatility
    )
    return {
        'position_id': position.position_id,
        'symbol': position.option.symbol,
        'premium': position.entry_price,
        'quantity': position.option.quantity,
        'entry_date': position.entry_date.isoformat(),
        'greeks': {
            'delta': position.option.delta,
            'gamma': position.option.gamma,
            'theta': position.option.theta,
            'vega': position.option.vega
        }
    }

@router.post("/options/strategy-payoff")
async def calculate_strategy_payoff(strategy: str,
                                   legs: List[Dict],
                                   price_range: List[float]) -> Dict[str, Any]:
    """Calculate payoff diagram for multi-leg option strategies."""
    return await options_trading.calculate_strategy_payoff(
        strategy, legs, (price_range[0], price_range[1])
    )

@router.get("/options/portfolio-greeks/{user_id}")
async def get_portfolio_greeks(user_id: str) -> Dict[str, Any]:
    """Get aggregate Greeks for user's options portfolio."""
    return await options_trading.get_portfolio_greeks(user_id)

@router.get("/options/screen")
async def screen_options(underlying: str,
                        min_volume: int = 100,
                        max_iv: float = 1.0) -> List[Dict]:
    """Screen for attractive option opportunities."""
    return await options_trading.screen_options(underlying, min_volume, max_iv)


# ========== HFT EXECUTION ENDPOINTS ==========

@router.post("/hft/submit-order")
async def submit_hft_order(order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit ultra-low latency HFT order."""
    order = HFTOrder(
        order_id=order_data['order_id'],
        symbol=order_data['symbol'],
        side=order_data['side'],
        quantity=order_data['quantity'],
        price=order_data.get('price', 0),
        order_type=order_data.get('order_type', 'market'),
        timestamp=order_data.get('timestamp', __import__('time').time()),
        latency_target_ms=order_data.get('latency_target_ms', 0.1),
        strategy_id=order_data.get('strategy_id', 'default')
    )
    return await hft_engine.submit_order(order)

@router.get("/hft/latency-report")
async def get_hft_latency_report() -> Dict[str, Any]:
    """Get HFT execution latency statistics."""
    return await hft_engine.get_latency_report()

@router.post("/hft/arbitrage-scan")
async def scan_arbitrage_opportunities(symbols: List[str]) -> List[Dict]:
    """Scan for HFT arbitrage opportunities."""
    return await hft_engine.arbitrage_scan(symbols)

@router.post("/hft/register-strategy")
async def register_hft_strategy(strategy_id: str, 
                                strategy_code: Optional[str] = None) -> Dict[str, Any]:
    """Register high-frequency trading strategy."""
    def sample_strategy(tick: Tick):
        # Placeholder strategy logic
        pass
    
    hft_engine.register_strategy(strategy_id, sample_strategy)
    return {'strategy_id': strategy_id, 'status': 'registered'}


# ========== RISK MANAGEMENT ENDPOINTS ==========

@router.post("/risk/set-limits/{user_id}")
async def set_risk_limits(user_id: str, limits: Dict[str, float]) -> Dict[str, Any]:
    """Set user-specific risk limits."""
    await risk_manager.set_user_limits(user_id, limits)
    return {'user_id': user_id, 'limits_set': list(limits.keys())}

@router.post("/risk/check-order/{user_id}")
async def check_order_risk(user_id: str, order: Dict[str, Any]) -> Dict[str, Any]:
    """Pre-trade risk check for order."""
    return await risk_manager.check_order_risk(user_id, order)

@router.post("/risk/update-exposure/{user_id}")
async def update_exposure(user_id: str, positions: List[Dict]) -> Dict[str, Any]:
    """Update portfolio exposure calculations."""
    return await risk_manager.update_exposure(user_id, positions)

@router.get("/risk/portfolio-var/{user_id}")
async def get_portfolio_var(user_id: str, 
                            positions: List[Dict],
                            confidence: float = 0.95) -> Dict[str, float]:
    """Calculate portfolio Value at Risk."""
    var = await risk_manager.calculate_portfolio_var(user_id, positions, confidence)
    return {'var_95': var, 'confidence': confidence}

@router.post("/risk/stress-test/{user_id}")
async def run_stress_test(user_id: str,
                         positions: List[Dict],
                         scenarios: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run stress tests on portfolio."""
    return await risk_manager.stress_test(user_id, positions, scenarios)

@router.get("/risk/report/{user_id}")
async def get_risk_report(user_id: str) -> Dict[str, Any]:
    """Generate comprehensive risk report."""
    return await risk_manager.get_risk_report(user_id)

@router.post("/risk/circuit-breaker")
async def check_circuit_breaker(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if circuit breakers should trigger."""
    triggered = await risk_manager.circuit_breaker_check(market_data)
    return {'circuit_breaker_triggered': triggered, 'daily_change_pct': market_data.get('daily_change_pct', 0)}


# ========== COMPLIANCE & REGULATORY ENDPOINTS ==========

@router.post("/compliance/report-trade")
async def report_trade(trade: Dict[str, Any],
                      jurisdiction: str = "sec") -> Dict[str, Any]:
    """Submit trade for regulatory reporting."""
    regulation = Regulation(jurisdiction)
    report = await compliance_engine.report_trade(trade, regulation)
    return {
        'report_id': report.report_id,
        'trade_id': report.trade_id,
        'compliance_hash': report.compliance_hash,
        'status': 'reported'
    }

@router.post("/compliance/surveillance")
async def run_trade_surveillance(trades: List[Dict],
                                orders: List[Dict]) -> Dict[str, Any]:
    """Run market abuse surveillance."""
    alerts = await compliance_engine.run_trade_surveillance(trades, orders)
    return {
        'alerts_generated': len(alerts),
        'alerts': [{
            'alert_id': a.alert_id,
            'type': a.activity_type,
            'risk_score': a.risk_score,
            'description': a.description
        } for a in alerts]
    }

@router.get("/compliance/regulatory-filing/{jurisdiction}")
async def generate_regulatory_filing(jurisdiction: str,
                                    period: str = "monthly") -> Dict[str, Any]:
    """Generate regulatory filing report."""
    regulation = Regulation(jurisdiction)
    return await compliance_engine.generate_regulatory_filing(regulation, period)

@router.get("/compliance/verify-integrity")
async def verify_audit_integrity() -> Dict[str, Any]:
    """Verify integrity of audit trail."""
    return await compliance_engine.verify_audit_integrity()

@router.get("/compliance/audit-trail")
async def get_audit_trail(limit: int = 100) -> List[Dict]:
    """Get recent audit trail entries."""
    return compliance_engine.audit_trail[-limit:]


# ========== ETL DATA PIPELINE ENDPOINTS ==========

@router.post("/etl/create-job")
async def create_etl_job(source: str,
                        data_type: str,
                        symbol: str,
                        start_date: str,
                        end_date: str) -> Dict[str, Any]:
    """Create ETL job for data ingestion."""
    job = await etl_pipeline.create_etl_job(source, data_type, symbol, start_date, end_date)
    return {
        'job_id': job.job_id,
        'symbol': job.symbol,
        'source': job.source.value,
        'data_type': job.data_type.value,
        'status': job.status,
        'created_at': job.created_at.isoformat()
    }

@router.post("/etl/run-job/{job_id}")
async def run_etl_job(job_id: str) -> Dict[str, Any]:
    """Execute ETL job."""
    job = await etl_pipeline.run_etl_job(job_id)
    return {
        'job_id': job.job_id,
        'status': job.status,
        'records_processed': job.records_processed,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        'error_message': job.error_message
    }

@router.get("/etl/job-status/{job_id}")
async def get_etl_job_status(job_id: str) -> Dict[str, Any]:
    """Get ETL job status and lineage."""
    return await etl_pipeline.get_job_status(job_id)

@router.get("/etl/jobs")
async def list_etl_jobs(status: Optional[str] = None) -> List[Dict]:
    """List ETL jobs with optional filtering."""
    return await etl_pipeline.list_jobs(status)


# ========== FEATURE STORE ENDPOINTS ==========

@router.post("/features/register")
async def register_feature(feature_name: str,
                          feature_type: str,
                          description: str,
                          ttl_seconds: int = 3600) -> Dict[str, Any]:
    """Register a new feature in the feature store."""
    await feature_store.register_feature(feature_name, feature_type, description, ttl_seconds)
    return {
        'feature_name': feature_name,
        'type': feature_type,
        'status': 'registered'
    }

@router.post("/features/compute-technical/{symbol}")
async def compute_technical_features(symbol: str,
                                    price_data: List[Dict]) -> Dict[str, Any]:
    """Compute technical analysis features for a symbol."""
    return await feature_store.compute_technical_features(symbol, price_data)

@router.post("/features/store-online/{entity_id}")
async def store_online_features(entity_id: str,
                               features: Dict[str, Any]) -> Dict[str, str]:
    """Store features in online store for real-time serving."""
    await feature_store.store_online_features(entity_id, features)
    return {'status': 'stored', 'entity_id': entity_id}

@router.get("/features/get-online/{entity_id}")
async def get_online_features(entity_id: str,
                              feature_names: List[str]) -> Dict[str, Any]:
    """Retrieve features from online store."""
    return await feature_store.get_online_features(entity_id, feature_names)

@router.post("/features/drift-detection")
async def detect_feature_drift(feature_name: str,
                              current_values: List[float],
                              reference_values: List[float]) -> Dict[str, Any]:
    """Detect feature drift from reference distribution."""
    return await feature_store.detect_feature_drift(feature_name, current_values, reference_values)


# ========== PAPER TRADING ENDPOINTS ==========

@router.post("/paper/account/create")
async def create_paper_account(user_id: str,
                             initial_balance: float = 100000.0) -> Dict[str, Any]:
    """Create paper trading account."""
    return await paper_trading.create_account(user_id, initial_balance)

@router.post("/paper/order/submit")
async def submit_paper_order(user_id: str,
                            symbol: str,
                            side: str,
                            quantity: float,
                            order_type: str = "market",
                            price: Optional[float] = None) -> Dict[str, Any]:
    """Submit paper trading order."""
    order = await paper_trading.submit_order(user_id, symbol, side, quantity, order_type, price)
    return {
        'order_id': order.order_id,
        'status': order.status.value,
        'symbol': order.symbol,
        'side': order.side,
        'quantity': order.quantity,
        'filled_quantity': order.filled_quantity,
        'avg_fill_price': order.avg_fill_price,
        'commission': order.commission
    }

@router.post("/paper/prices/update")
async def update_paper_prices(prices: Dict[str, float]) -> Dict[str, Any]:
    """Update market prices for paper trading simulation."""
    await paper_trading.update_market_prices(prices)
    return {'updated_symbols': len(prices)}

@router.get("/paper/portfolio/{user_id}")
async def get_paper_portfolio(user_id: str) -> Dict[str, Any]:
    """Get paper trading portfolio."""
    return await paper_trading.get_portfolio(user_id)

@router.post("/paper/order/cancel/{order_id}")
async def cancel_paper_order(order_id: str) -> Dict[str, Any]:
    """Cancel pending paper trading order."""
    success = await paper_trading.cancel_order(order_id)
    return {'order_id': order_id, 'cancelled': success}
