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
