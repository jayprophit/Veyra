"""
FinOps Manager: Financial Operations for Cloud & Trading Cost Optimization
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CloudSpend:
    provider: str
    amount: float
    currency: str
    service_breakdown: Dict[str, float]
    timestamp: datetime


@dataclass
class CostRecommendation:
    category: str
    current_cost: float
    potential_savings: float
    confidence: float
    action: str
    automated: bool


class FinOpsManager:
    """
    Financial Operations Manager
    
    Responsibilities:
    - Cloud spend monitoring and optimization
    - Trading cost analysis across brokers
    - Budget alerting and forecasting
    - Resource auto-scaling based on market conditions
    """
    
    def __init__(self):
        self.budget_thresholds = [0.7, 0.9, 1.0]
        self.providers = {
            'railway': self.get_railway_spend,
            'vercel': self.get_vercel_spend,
            'supabase': self.get_supabase_spend,
            'upstash': self.get_upstash_spend,
            'openai': self.get_openai_spend
        }
        self.monthly_budget = float(self._load_budget_config())
        
    def _load_budget_config(self) -> str:
        """Load budget from config or env"""
        import os
        return os.getenv('MONTHLY_CLOUD_BUDGET', '100')
    
    async def get_cloud_spend_report(self) -> Dict:
        """
        Aggregate spend across all cloud providers
        
        Returns:
            Dict with total spend, breakdown by provider,
            budget utilization, and forecast
        """
        spend_data = {}
        
        # Parallel fetch from all providers
        tasks = [
            (name, func())
            for name, func in self.providers.items()
        ]
        
        for name, task in tasks:
            try:
                spend_data[name] = await task
            except Exception as e:
                logger.error(f"Failed to fetch {name} spend: {e}")
                spend_data[name] = 0.0
        
        total = sum(spend_data.values())
        utilization = total / self.monthly_budget
        
        # Check thresholds and alert
        await self._check_budget_thresholds(total, utilization)
        
        # Generate forecast
        forecast = self._forecast_month_end(total)
        
        return {
            'total_spend': total,
            'currency': 'GBP',
            'breakdown': spend_data,
            'budget_utilization': utilization,
            'forecast_end_of_month': forecast,
            'alerts': self._generate_alerts(utilization),
            'recommendations': await self._generate_recommendations(spend_data)
        }
    
    async def get_railway_spend(self) -> float:
        """Fetch Railway.app spend via API"""
        token = self._get_railway_token()
        if not token:
            return 0.0
            
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {token}'}
            async with session.get(
                'https://backboard.railway.app/graphql',
                headers=headers
            ) as resp:
                # Parse GraphQL response for usage
                data = await resp.json()
                return self._parse_railway_usage(data)
    
    async def get_vercel_spend(self) -> float:
        """Fetch Vercel spend"""
        token = self._get_vercel_token()
        if not token:
            return 0.0
            
        # Vercel API integration
        return 0.0  # Placeholder
    
    async def get_supabase_spend(self) -> float:
        """Fetch Supabase spend"""
        # Supabase usage API
        return 0.0  # Placeholder
    
    async def get_upstash_spend(self) -> float:
        """Fetch Upstash Redis spend"""
        return 0.0  # Placeholder
    
    async def get_openai_spend(self) -> float:
        """Fetch OpenAI API usage costs"""
        # OpenAI usage API
        return 0.0  # Placeholder
    
    async def analyze_trading_costs(self) -> List[CostRecommendation]:
        """
        Analyze trading fees across all connected brokers
        and recommend cost optimizations
        """
        recommendations = []
        
        # Get fee structures from all brokers
        broker_fees = await self._fetch_broker_fee_schedules()
        
        # Analyze by asset class
        for asset_class in ['crypto', 'stocks', 'forex', 'commodities']:
            current_broker = self._get_current_broker_for(asset_class)
            current_fees = broker_fees.get(current_broker, {})
            
            # Find cheaper alternatives
            alternatives = [
                (name, fees)
                for name, fees in broker_fees.items()
                if fees.get(asset_class, float('inf')) < current_fees.get(asset_class, 0)
            ]
            
            if alternatives:
                best_alternative = min(alternatives, key=lambda x: x[1][asset_class])
                
                # Calculate potential savings
                monthly_volume = self._estimate_monthly_volume(asset_class)
                current_cost = monthly_volume * current_fees.get(asset_class, 0)
                new_cost = monthly_volume * best_alternative[1][asset_class]
                savings = current_cost - new_cost
                
                if savings > 10:  # Only recommend if > £10 savings
                    recommendations.append(CostRecommendation(
                        category=f'{asset_class}_trading_fees',
                        current_cost=current_cost,
                        potential_savings=savings,
                        confidence=0.85,
                        action=f'Switch from {current_broker} to {best_alternative[0]}',
                        automated=False  # Requires manual broker setup
                    ))
        
        return recommendations
    
    async def auto_scale_resources(self):
        """
        Auto-scale infrastructure based on market volatility
        and system load predictions
        """
        # Get current metrics
        market_volatility = await self._get_market_volatility()
        current_load = await self._get_system_load()
        predicted_load = await self._predict_load_next_hour()
        
        # Scaling logic
        if market_volatility > 0.7 or predicted_load > 0.8:
            # Scale up for high activity
            await self._scale_railway(3)
            await self._enable_redis_cluster()
            logger.info("Scaled up: high volatility/load detected")
            
        elif market_volatility < 0.2 and predicted_load < 0.3:
            # Scale down for low activity
            await self._scale_railway(1)
            await self._disable_redis_cluster()
            logger.info("Scaled down: low activity period")
    
    async def _check_budget_thresholds(self, total: float, utilization: float):
        """Send alerts when budget thresholds are crossed"""
        for threshold in self.budget_thresholds:
            if utilization >= threshold:
                await self._send_budget_alert(threshold, total, self.monthly_budget)
    
    async def _send_budget_alert(self, threshold: float, current: float, budget: float):
        """Send budget alert via configured channels"""
        severity = 'warning' if threshold < 1.0 else 'critical'
        
        alert = {
            'type': 'budget_alert',
            'severity': severity,
            'threshold_percent': threshold * 100,
            'current_spend': current,
            'budget': budget,
            'timestamp': datetime.utcnow().isoformat(),
            'message': f'Budget {threshold*100:.0f}% reached: £{current:.2f} / £{budget:.2f}'
        }
        
        # Send to notification system
        # await notification_manager.send_alert(alert)
        logger.warning(alert['message'])
    
    def _forecast_month_end(self, current_spend: float) -> float:
        """Linear forecast to end of month"""
        today = datetime.now()
        days_in_month = (today.replace(day=28) + timedelta(days=4)).day
        days_elapsed = today.day
        
        if days_elapsed == 0:
            return current_spend
            
        daily_rate = current_spend / days_elapsed
        forecast = daily_rate * days_in_month
        
        return round(forecast, 2)
    
    async def _generate_recommendations(self, spend_data: Dict) -> List[Dict]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        # Check for idle resources
        if spend_data.get('railway', 0) > 50:
            recommendations.append({
                'type': 'resource_optimization',
                'provider': 'railway',
                'savings_estimate': 15.0,
                'action': 'Review idle services and downsize non-production instances'
            })
        
        return recommendations
    
    # Helper methods (placeholders)
    def _get_railway_token(self) -> Optional[str]:
        import os
        return os.getenv('RAILWAY_TOKEN')
    
    def _get_vercel_token(self) -> Optional[str]:
        import os
        return os.getenv('VERCEL_TOKEN')
    
    def _parse_railway_usage(self, data: Dict) -> float:
        return 0.0
    
    def _get_current_broker_for(self, asset_class: str) -> str:
        return 'binance'
    
    async def _fetch_broker_fee_schedules(self) -> Dict:
        return {}
    
    def _estimate_monthly_volume(self, asset_class: str) -> float:
        return 1000.0
    
    async def _get_market_volatility(self) -> float:
        return 0.5
    
    async def _get_system_load(self) -> float:
        return 0.5
    
    async def _predict_load_next_hour(self) -> float:
        return 0.5
    
    async def _scale_railway(self, instances: int):
        pass
    
    async def _enable_redis_cluster(self):
        pass
    
    async def _disable_redis_cluster(self):
        pass
    
    def _generate_alerts(self, utilization: float) -> List[str]:
        alerts = []
        if utilization > 0.9:
            alerts.append('CRITICAL: Budget 90% exceeded')
        elif utilization > 0.7:
            alerts.append('WARNING: Budget 70% reached')
        return alerts
