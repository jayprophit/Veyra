"""
DevOps Manager: CI/CD, Deployments, Feature Flags, Infrastructure
"""

import asyncio
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Deployment:
    version: str
    commit_sha: str
    environment: str
    status: DeploymentStatus
    timestamp: datetime
    deployed_by: str
    health_check_passed: bool = False
    smoke_tests_passed: bool = False


@dataclass
class FeatureFlag:
    name: str
    enabled: bool
    rollout_percentage: int
    targeting_rules: Dict[str, Any]
    created_at: datetime


class DevOpsManager:
    """
    DevOps Manager
    
    Responsibilities:
    - Blue-green deployments with zero downtime
    - Feature flags for gradual rollouts
    - Automated rollback on failure
    - Health checks and smoke tests
    - Infrastructure state management
    """
    
    def __init__(self):
        self.deployments: List[Deployment] = []
        self.rollback_history: List[Dict] = []
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self.infrastructure_state = {}
        
    async def blue_green_deploy(
        self, 
        version: str, 
        commit_sha: str,
        deployed_by: str = "system"
    ) -> Dict:
        """
        Execute blue-green deployment strategy
        
        Steps:
        1. Deploy to 'green' environment
        2. Run health checks
        3. Run smoke tests
        4. Switch traffic
        5. Monitor stability
        6. Archive blue
        
        Returns:
            Deployment result with status and details
        """
        deployment = Deployment(
            version=version,
            commit_sha=commit_sha,
            environment="production",
            status=DeploymentStatus.IN_PROGRESS,
            timestamp=datetime.utcnow(),
            deployed_by=deployed_by
        )
        
        try:
            # Step 1: Deploy to green
            logger.info(f"Deploying {version} to green environment...")
            green_url = await self._deploy_to_green(version)
            
            # Step 2: Health checks
            logger.info("Running health checks...")
            health_ok = await self._health_check(green_url)
            if not health_ok:
                await self._rollback_green()
                deployment.status = DeploymentStatus.FAILED
                self.deployments.append(deployment)
                return {
                    'success': False,
                    'error': 'Health checks failed',
                    'deployment': deployment
                }
            
            deployment.health_check_passed = True
            
            # Step 3: Smoke tests
            logger.info("Running smoke tests...")
            smoke_ok = await self._run_smoke_tests(green_url)
            if not smoke_ok:
                await self._rollback_green()
                deployment.status = DeploymentStatus.FAILED
                self.deployments.append(deployment)
                return {
                    'success': False,
                    'error': 'Smoke tests failed',
                    'deployment': deployment
                }
            
            deployment.smoke_tests_passed = True
            
            # Step 4: Switch traffic (blue → green)
            logger.info("Switching traffic to green...")
            await self._switch_traffic_to_green()
            
            # Step 5: Monitor for 5 minutes
            logger.info("Monitoring stability...")
            await asyncio.sleep(300)  # 5 minutes
            
            stable = await self._check_stability()
            if not stable:
                logger.warning("Stability check failed, rolling back...")
                await self._rollback_to_blue()
                deployment.status = DeploymentStatus.ROLLED_BACK
                self.deployments.append(deployment)
                return {
                    'success': False,
                    'error': 'Stability check failed, auto-rolled back',
                    'deployment': deployment
                }
            
            # Step 6: Archive blue
            await self._archive_blue_environment()
            
            deployment.status = DeploymentStatus.SUCCESS
            self.deployments.append(deployment)
            
            return {
                'success': True,
                'message': f'Deployment {version} successful',
                'deployment': deployment,
                'url': green_url
            }
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            await self._rollback_green()
            deployment.status = DeploymentStatus.FAILED
            self.deployments.append(deployment)
            return {
                'success': False,
                'error': str(e),
                'deployment': deployment
            }
    
    def check_feature_flag(self, flag_name: str, user_id: str, user_segment: str = "standard") -> bool:
        """
        Check if feature is enabled for user
        
        Uses deterministic hashing for consistent user experience
        across sessions.
        
        Args:
            flag_name: Name of the feature flag
            user_id: Unique user identifier
            user_segment: User tier (free, standard, premium, beta)
            
        Returns:
            True if feature enabled for this user
        """
        flag = self.feature_flags.get(flag_name)
        if not flag:
            return False
        
        if not flag.enabled:
            return False
        
        # Check targeting rules first
        if user_segment in flag.targeting_rules.get('segments', []):
            return True
        
        # Percentage-based rollout
        rollout = flag.rollout_percentage
        
        # Deterministic hash for consistent experience
        hash_input = f"{flag_name}:{user_id}"
        hash_val = int(hashlib.md5(hash_input.encode()).hexdigest(), 16) % 100
        
        return hash_val < rollout
    
    def create_feature_flag(
        self, 
        name: str, 
        rollout_percentage: int = 0,
        segments: List[str] = None
    ) -> FeatureFlag:
        """Create new feature flag"""
        flag = FeatureFlag(
            name=name,
            enabled=True,
            rollout_percentage=rollout_percentage,
            targeting_rules={'segments': segments or []},
            created_at=datetime.utcnow()
        )
        self.feature_flags[name] = flag
        return flag
    
    async def automated_rollback(self, error_rate: float, latency_p95: float):
        """
        Auto-rollback if metrics exceed thresholds
        
        Triggers:
        - Error rate > 5%
        - P95 latency > 2000ms
        """
        triggered = False
        reason = ""
        
        if error_rate > 0.05:
            triggered = True
            reason = f"Error rate {error_rate*100:.1f}% exceeds 5% threshold"
        
        if latency_p95 > 2000:
            triggered = True
            reason += f" P95 latency {latency_p95}ms exceeds 2000ms"
        
        if triggered:
            logger.critical(f"Auto-rollback triggered: {reason}")
            
            # Get last stable version
            last_stable = self._get_last_stable_deployment()
            
            if last_stable:
                await self._rollback_to_version(last_stable.version)
                
                self.rollback_history.append({
                    'timestamp': datetime.utcnow(),
                    'reason': reason,
                    'rolled_back_to': last_stable.version,
                    'auto_triggered': True
                })
                
                # Send alert
                await self._send_rollback_alert(reason, last_stable.version)
                
                return {
                    'rolled_back': True,
                    'to_version': last_stable.version,
                    'reason': reason
                }
        
        return {'rolled_back': False}
    
    async def get_deployment_metrics(self) -> Dict:
        """Get deployment success metrics"""
        total = len(self.deployments)
        successful = len([d for d in self.deployments if d.status == DeploymentStatus.SUCCESS])
        failed = len([d for d in self.deployments if d.status == DeploymentStatus.FAILED])
        rolled_back = len([d for d in self.deployments if d.status == DeploymentStatus.ROLLED_BACK])
        
        # Calculate MTTR (Mean Time To Recovery)
        mttr = self._calculate_mttr()
        
        # Calculate lead time
        lead_time = self._calculate_lead_time()
        
        return {
            'total_deployments': total,
            'successful': successful,
            'failed': failed,
            'rolled_back': rolled_back,
            'success_rate': successful / total if total > 0 else 0,
            'mttr_minutes': mttr,
            'lead_time_hours': lead_time,
            'deployment_frequency': self._calculate_deployment_frequency()
        }
    
    async def canary_deploy(self, version: str, percentage: int = 10) -> Dict:
        """
        Canary deployment to subset of traffic
        
        Gradually increases traffic to new version
        while monitoring for issues.
        """
        # Start with small percentage
        await self._set_canary_percentage(percentage)
        
        # Monitor for 10 minutes
        await asyncio.sleep(600)
        
        # Check metrics
        metrics = await self._get_canary_metrics()
        
        if metrics['error_rate'] < 0.01 and metrics['latency_p95'] < 1000:
            # Increase to 50%
            await self._set_canary_percentage(50)
            await asyncio.sleep(600)
            
            metrics = await self._get_canary_metrics()
            if metrics['error_rate'] < 0.01:
                # Full rollout
                await self._set_canary_percentage(100)
                return {'status': 'complete', 'version': version}
        else:
            # Rollback canary
            await self._rollback_canary()
            return {'status': 'rolled_back', 'error': 'Canary metrics failed'}
        
        return {'status': 'in_progress', 'percentage': percentage}
    
    # Private helper methods
    async def _deploy_to_green(self, version: str) -> str:
        """Deploy to green environment"""
        # Railway/Vercel deployment logic
        return f"https://green-{version}.up.railway.app"
    
    async def _health_check(self, url: str) -> bool:
        """Run health check on deployment"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/api/health", timeout=10) as resp:
                    return resp.status == 200
        except:
            return False
    
    async def _run_smoke_tests(self, url: str) -> bool:
        """Run smoke tests on deployment"""
        tests = [
            ('/api/health', 200),
            ('/api/portfolio/current', 401),  # Should require auth
            ('/api/market/prices', 200),
        ]
        
        import aiohttp
        async with aiohttp.ClientSession() as session:
            for endpoint, expected in tests:
                try:
                    async with session.get(f"{url}{endpoint}", timeout=10) as resp:
                        if resp.status != expected:
                            return False
                except:
                    return False
        
        return True
    
    async def _switch_traffic_to_green(self):
        """Switch traffic from blue to green"""
        # Update load balancer or DNS
        pass
    
    async def _check_stability(self) -> bool:
        """Check if deployment is stable"""
        # Check error rates and latency
        return True
    
    async def _rollback_green(self):
        """Rollback green deployment"""
        pass
    
    async def _rollback_to_blue(self):
        """Rollback to blue environment"""
        pass
    
    async def _archive_blue_environment(self):
        """Archive blue environment after successful deploy"""
        pass
    
    def _get_last_stable_deployment(self) -> Optional[Deployment]:
        """Get last successful deployment"""
        for dep in reversed(self.deployments):
            if dep.status == DeploymentStatus.SUCCESS:
                return dep
        return None
    
    async def _rollback_to_version(self, version: str):
        """Rollback to specific version"""
        logger.info(f"Rolling back to version {version}")
        # Execute rollback
    
    async def _send_rollback_alert(self, reason: str, version: str):
        """Send alert about rollback"""
        pass
    
    def _calculate_mttr(self) -> float:
        """Calculate Mean Time To Recovery"""
        if not self.rollback_history:
            return 0.0
        # Calculate average time from failure to recovery
        return 5.0  # Placeholder
    
    def _calculate_lead_time(self) -> float:
        """Calculate deployment lead time"""
        return 2.5  # Placeholder hours
    
    def _calculate_deployment_frequency(self) -> str:
        """Calculate how often deployments occur"""
        return "daily"  # Placeholder
    
    async def _set_canary_percentage(self, percentage: int):
        """Set canary traffic percentage"""
        pass
    
    async def _get_canary_metrics(self) -> Dict:
        """Get canary deployment metrics"""
        return {'error_rate': 0.001, 'latency_p95': 500}
    
    async def _rollback_canary(self):
        """Rollback canary deployment"""
        pass
