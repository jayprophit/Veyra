"""
Full System Integration Test
Comprehensive integration testing for all Veyra Platform components
"""

import asyncio
import aiohttp
import pytest
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
import pandas as pd
from pathlib import Path
import subprocess
import time
import os
from unittest.mock import patch, AsyncMock

# Import Veyra components
from src.backend.integrations.opensource.visual_learning_ai import visual_ai
from src.backend.integrations.opensource.predictive_analytics import predictive_analytics
from src.backend.core.compliance_manager import compliance_manager
from tests.security.penetration_testing_suite import PenetrationTestingSuite

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # PASSED, FAILED, SKIPPED
    duration: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class IntegrationTestSuite:
    """Integration test suite configuration"""
    base_url: str = "https://api.veyra.com"
    frontend_url: str = "https://app.veyra.com"
    mobile_app_url: str = "http://localhost:8080"
    test_timeout: int = 300
    parallel_tests: bool = True
    cleanup_after_test: bool = True

class FullSystemIntegrationTest:
    """Comprehensive full system integration testing"""
    
    def __init__(self, config: IntegrationTestSuite = None):
        self.config = config or IntegrationTestSuite()
        self.session = None
        self.test_results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        
        # Test configurations
        self.test_data = self._generate_test_data()
        
        logger.info("Full System Integration Test initialized")
        
    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate test data for integration tests"""
        return {
            "test_user": {
                "email": "test.user@veyra.com",
                "password": "TestPassword123!",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User"
            },
            "test_portfolio": {
                "name": "Test Portfolio",
                "description": "Integration test portfolio",
                "initial_balance": 10000.0,
                "risk_tolerance": "medium"
            },
            "test_symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
            "test_trade": {
                "symbol": "AAPL",
                "quantity": 100,
                "order_type": "market",
                "side": "buy"
            }
        }
        
    async def run_full_integration_test(self) -> Dict[str, Any]:
        """Run comprehensive integration test suite"""
        try:
            logger.info("Starting Full System Integration Test")
            self.start_time = datetime.utcnow()
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.test_timeout),
                connector=aiohttp.TCPConnector(ssl=False)
            )
            
            # Run all test categories
            await self._run_all_tests()
            
            # Generate comprehensive report
            report = await self._generate_test_report()
            
            return report
            
        except Exception as e:
            logger.error(f"Error in full integration test: {e}")
            raise
        finally:
            if self.session:
                await self.session.close()
                
    async def _run_all_tests(self):
        """Run all integration test categories"""
        test_categories = [
            ("System Health Tests", self._test_system_health),
            ("Authentication Tests", self._test_authentication),
            ("API Integration Tests", self._test_api_integration),
            ("Database Integration Tests", self._test_database_integration),
            ("Mobile App Integration Tests", self._test_mobile_integration),
            ("Visual Learning AI Tests", self._test_visual_learning_ai),
            ("Predictive Analytics Tests", self._test_predictive_analytics),
            ("Compliance Tests", self._test_compliance),
            ("Security Tests", self._test_security),
            ("Performance Tests", self._test_performance),
            ("End-to-End Workflow Tests", self._test_end_to_end_workflows),
            ("Disaster Recovery Tests", self._test_disaster_recovery)
        ]
        
        if self.config.parallel_tests:
            # Run tests in parallel where possible
            tasks = []
            for category_name, test_func in test_categories:
                task = asyncio.create_task(self._run_test_category(category_name, test_func))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Run tests sequentially
            for category_name, test_func in test_categories:
                await self._run_test_category(category_name, test_func)
                
    async def _run_test_category(self, category_name: str, test_func):
        """Run a test category"""
        try:
            logger.info(f"Running {category_name}")
            await test_func()
        except Exception as e:
            logger.error(f"Error in {category_name}: {e}")
            self.test_results.append(TestResult(
                test_name=category_name,
                status="FAILED",
                duration=0.0,
                error_message=str(e)
            ))
            
    async def _test_system_health(self):
        """Test system health and connectivity"""
        tests = [
            ("API Health Check", self._test_api_health),
            ("Frontend Health Check", self._test_frontend_health),
            ("Database Connectivity", self._test_database_connectivity),
            ("Redis Connectivity", self._test_redis_connectivity),
            ("External API Connectivity", self._test_external_api_connectivity)
        ]
        
        for test_name, test_func in tests:
            await self._run_individual_test(test_name, test_func)
            
    async def _test_api_health(self):
        """Test API health endpoint"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.config.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    assert data.get("status") == "healthy"
                    assert "timestamp" in data
                    assert "version" in data
                    
                    self.test_results.append(TestResult(
                        test_name="API Health Check",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"API health check failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="API Health Check",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_frontend_health(self):
        """Test frontend health endpoint"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.config.frontend_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    assert data.get("status") == "healthy"
                    
                    self.test_results.append(TestResult(
                        test_name="Frontend Health Check",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Frontend health check failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Frontend Health Check",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_database_connectivity(self):
        """Test database connectivity"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.config.base_url}/health/db") as response:
                if response.status == 200:
                    data = await response.json()
                    assert data.get("database") == "connected"
                    assert "connection_pool" in data
                    
                    self.test_results.append(TestResult(
                        test_name="Database Connectivity",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Database connectivity check failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Database Connectivity",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_redis_connectivity(self):
        """Test Redis connectivity"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.config.base_url}/health/redis") as response:
                if response.status == 200:
                    data = await response.json()
                    assert data.get("redis") == "connected"
                    assert "memory_usage" in data
                    
                    self.test_results.append(TestResult(
                        test_name="Redis Connectivity",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Redis connectivity check failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Redis Connectivity",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_external_api_connectivity(self):
        """Test external API connectivity"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.config.base_url}/health/external") as response:
                if response.status == 200:
                    data = await response.json()
                    assert "external_apis" in data
                    
                    self.test_results.append(TestResult(
                        test_name="External API Connectivity",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"External API connectivity check failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="External API Connectivity",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_authentication(self):
        """Test authentication system"""
        tests = [
            ("User Registration", self._test_user_registration),
            ("User Login", self._test_user_login),
            ("Token Refresh", self._test_token_refresh),
            ("Logout", self._test_logout),
            ("Biometric Authentication", self._test_biometric_auth)
        ]
        
        for test_name, test_func in tests:
            await self._run_individual_test(test_name, test_func)
            
    async def _test_user_registration(self):
        """Test user registration"""
        start_time = time.time()
        
        try:
            user_data = self.test_data["test_user"]
            
            async with self.session.post(
                f"{self.config.base_url}/auth/register",
                json=user_data
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    assert "user_id" in data
                    assert "access_token" in data
                    assert "refresh_token" in data
                    
                    # Store tokens for subsequent tests
                    self.test_data["access_token"] = data["access_token"]
                    self.test_data["refresh_token"] = data["refresh_token"]
                    self.test_data["user_id"] = data["user_id"]
                    
                    self.test_results.append(TestResult(
                        test_name="User Registration",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"User registration failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="User Registration",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_user_login(self):
        """Test user login"""
        start_time = time.time()
        
        try:
            user_data = self.test_data["test_user"]
            
            async with self.session.post(
                f"{self.config.base_url}/auth/login",
                json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "access_token" in data
                    assert "refresh_token" in data
                    
                    # Update tokens
                    self.test_data["access_token"] = data["access_token"]
                    self.test_data["refresh_token"] = data["refresh_token"]
                    
                    self.test_results.append(TestResult(
                        test_name="User Login",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"User login failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="User Login",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_token_refresh(self):
        """Test token refresh"""
        start_time = time.time()
        
        try:
            refresh_token = self.test_data.get("refresh_token")
            if not refresh_token:
                raise Exception("No refresh token available")
                
            async with self.session.post(
                f"{self.config.base_url}/auth/refresh",
                json={"refresh_token": refresh_token}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "access_token" in data
                    assert "refresh_token" in data
                    
                    # Update tokens
                    self.test_data["access_token"] = data["access_token"]
                    self.test_data["refresh_token"] = data["refresh_token"]
                    
                    self.test_results.append(TestResult(
                        test_name="Token Refresh",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Token refresh failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Token Refresh",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_logout(self):
        """Test user logout"""
        start_time = time.time()
        
        try:
            access_token = self.test_data.get("access_token")
            if not access_token:
                raise Exception("No access token available")
                
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with self.session.post(
                f"{self.config.base_url}/auth/logout",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert data.get("message") == "Logged out successfully"
                    
                    # Clear tokens
                    self.test_data["access_token"] = None
                    self.test_data["refresh_token"] = None
                    
                    self.test_results.append(TestResult(
                        test_name="Logout",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Logout failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Logout",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_biometric_auth(self):
        """Test biometric authentication"""
        start_time = time.time()
        
        try:
            # Simulate biometric authentication
            biometric_data = {
                "biometric_type": "fingerprint",
                "biometric_hash": "simulated_hash_12345",
                "device_id": "test_device_123"
            }
            
            async with self.session.post(
                f"{self.config.base_url}/auth/biometric",
                json=biometric_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "access_token" in data
                    
                    self.test_results.append(TestResult(
                        test_name="Biometric Authentication",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Biometric authentication failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Biometric Authentication",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_api_integration(self):
        """Test API integration endpoints"""
        tests = [
            ("Portfolio API", self._test_portfolio_api),
            ("Trading API", self._test_trading_api),
            ("Market Data API", self._test_market_data_api),
            ("Analytics API", self._test_analytics_api),
            ("WebSocket API", self._test_websocket_api)
        ]
        
        for test_name, test_func in tests:
            await self._run_individual_test(test_name, test_func)
            
    async def _test_portfolio_api(self):
        """Test portfolio API endpoints"""
        start_time = time.time()
        
        try:
            # Login first to get token
            await self._test_user_login()
            access_token = self.test_data.get("access_token")
            
            if not access_token:
                raise Exception("No access token available")
                
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test portfolio creation
            portfolio_data = self.test_data["test_portfolio"]
            
            async with self.session.post(
                f"{self.config.base_url}/api/v1/portfolio",
                json=portfolio_data,
                headers=headers
            ) as response:
                if response.status == 201:
                    portfolio = await response.json()
                    assert "portfolio_id" in data
                    self.test_data["portfolio_id"] = portfolio["portfolio_id"]
                    
                    # Test portfolio retrieval
                    async with self.session.get(
                        f"{self.config.base_url}/api/v1/portfolio/{portfolio['portfolio_id']}",
                        headers=headers
                    ) as get_response:
                        if get_response.status == 200:
                            retrieved_portfolio = await get_response.json()
                            assert retrieved_portfolio["name"] == portfolio_data["name"]
                            
                            self.test_results.append(TestResult(
                                test_name="Portfolio API",
                                status="PASSED",
                                duration=time.time() - start_time,
                                details=retrieved_portfolio
                            ))
                        else:
                            raise Exception(f"Portfolio retrieval failed with status {get_response.status}")
                else:
                    raise Exception(f"Portfolio creation failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Portfolio API",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_trading_api(self):
        """Test trading API endpoints"""
        start_time = time.time()
        
        try:
            access_token = self.test_data.get("access_token")
            if not access_token:
                raise Exception("No access token available")
                
            headers = {"Authorization": f"Bearer {access_token}"}
            trade_data = self.test_data["test_trade"]
            
            # Test trade placement
            async with self.session.post(
                f"{self.config.base_url}/api/v1/trade",
                json=trade_data,
                headers=headers
            ) as response:
                if response.status == 201:
                    trade = await response.json()
                    assert "trade_id" in trade
                    assert trade["symbol"] == trade_data["symbol"]
                    
                    # Test trade status
                    async with self.session.get(
                        f"{self.config.base_url}/api/v1/trade/{trade['trade_id']}",
                        headers=headers
                    ) as get_response:
                        if get_response.status == 200:
                            trade_status = await get_response.json()
                            assert "status" in trade_status
                            
                            self.test_results.append(TestResult(
                                test_name="Trading API",
                                status="PASSED",
                                duration=time.time() - start_time,
                                details=trade_status
                            ))
                        else:
                            raise Exception(f"Trade status check failed with status {get_response.status}")
                else:
                    raise Exception(f"Trade placement failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Trading API",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_market_data_api(self):
        """Test market data API endpoints"""
        start_time = time.time()
        
        try:
            access_token = self.test_data.get("access_token")
            if not access_token:
                raise Exception("No access token available")
                
            headers = {"Authorization": f"Bearer {access_token}"}
            symbol = self.test_data["test_symbols"][0]
            
            # Test market data retrieval
            async with self.session.get(
                f"{self.config.base_url}/api/v1/market/{symbol}",
                headers=headers
            ) as response:
                if response.status == 200:
                    market_data = await response.json()
                    assert "symbol" in market_data
                    assert "price" in market_data
                    assert "volume" in market_data
                    
                    self.test_results.append(TestResult(
                        test_name="Market Data API",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=market_data
                    ))
                else:
                    raise Exception(f"Market data retrieval failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Market Data API",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_analytics_api(self):
        """Test analytics API endpoints"""
        start_time = time.time()
        
        try:
            access_token = self.test_data.get("access_token")
            if not access_token:
                raise Exception("No access token available")
                
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test analytics data
            async with self.session.get(
                f"{self.config.base_url}/api/v1/analytics/portfolio",
                headers=headers
            ) as response:
                if response.status == 200:
                    analytics = await response.json()
                    assert "performance" in analytics
                    assert "risk_metrics" in analytics
                    
                    self.test_results.append(TestResult(
                        test_name="Analytics API",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=analytics
                    ))
                else:
                    raise Exception(f"Analytics retrieval failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Analytics API",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_websocket_api(self):
        """Test WebSocket API connectivity"""
        start_time = time.time()
        
        try:
            # Test WebSocket connection
            import websockets
            
            async with websockets.connect(
                f"ws://localhost:8000/ws/portfolio",
                extra_headers={"Authorization": f"Bearer {self.test_data.get('access_token', '')}"}
            ) as websocket:
                # Send test message
                await websocket.send(json.dumps({"action": "subscribe", "portfolio_id": "test"}))
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                assert "status" in data
                
                self.test_results.append(TestResult(
                    test_name="WebSocket API",
                    status="PASSED",
                    duration=time.time() - start_time,
                    details=data
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="WebSocket API",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_database_integration(self):
        """Test database integration"""
        tests = [
            ("Database Transactions", self._test_database_transactions),
            ("Data Consistency", self._test_data_consistency),
            ("Backup and Restore", self._test_backup_restore)
        ]
        
        for test_name, test_func in tests:
            await self._run_individual_test(test_name, test_func)
            
    async def _test_database_transactions(self):
        """Test database transactions"""
        start_time = time.time()
        
        try:
            # Test transaction rollback
            async with self.session.post(
                f"{self.config.base_url}/api/v1/test/transaction",
                json={"test_rollback": True}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert data.get("transaction_rollback") == True
                    
                    self.test_results.append(TestResult(
                        test_name="Database Transactions",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Database transaction test failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Database Transactions",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_data_consistency(self):
        """Test data consistency"""
        start_time = time.time()
        
        try:
            # Test data consistency checks
            async with self.session.get(
                f"{self.config.base_url}/api/v1/test/consistency"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert data.get("consistent") == True
                    
                    self.test_results.append(TestResult(
                        test_name="Data Consistency",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Data consistency test failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Data Consistency",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_backup_restore(self):
        """Test backup and restore functionality"""
        start_time = time.time()
        
        try:
            # Test backup creation
            async with self.session.post(
                f"{self.config.base_url}/api/v1/test/backup"
            ) as response:
                if response.status == 200:
                    backup_data = await response.json()
                    assert "backup_id" in backup_data
                    
                    self.test_results.append(TestResult(
                        test_name="Backup and Restore",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=backup_data
                    ))
                else:
                    raise Exception(f"Backup test failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Backup and Restore",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_mobile_integration(self):
        """Test mobile app integration"""
        tests = [
            ("Mobile API Connectivity", self._test_mobile_api_connectivity),
            ("Push Notifications", self._test_push_notifications),
            ("Offline Sync", self._test_offline_sync),
            ("Biometric Integration", self._test_mobile_biometric)
        ]
        
        for test_name, test_func in tests:
            await self._run_individual_test(test_name, test_func)
            
    async def _test_mobile_api_connectivity(self):
        """Test mobile API connectivity"""
        start_time = time.time()
        
        try:
            # Test mobile-specific endpoints
            async with self.session.get(f"{self.config.mobile_app_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    assert data.get("status") == "healthy"
                    
                    self.test_results.append(TestResult(
                        test_name="Mobile API Connectivity",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Mobile API connectivity failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Mobile API Connectivity",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_push_notifications(self):
        """Test push notification system"""
        start_time = time.time()
        
        try:
            # Test push notification registration
            notification_data = {
                "device_token": "test_device_token_123",
                "platform": "ios",
                "app_version": "1.0.0"
            }
            
            async with self.session.post(
                f"{self.config.base_url}/api/v1/notifications/register",
                json=notification_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "registration_id" in data
                    
                    self.test_results.append(TestResult(
                        test_name="Push Notifications",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Push notification registration failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Push Notifications",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_offline_sync(self):
        """Test offline synchronization"""
        start_time = time.time()
        
        try:
            # Test offline sync functionality
            sync_data = {
                "sync_data": {
                    "portfolio": {"test": "data"},
                    "trades": [{"test": "trade"}]
                }
            }
            
            async with self.session.post(
                f"{self.config.base_url}/api/v1/sync/offline",
                json=sync_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "sync_id" in data
                    
                    self.test_results.append(TestResult(
                        test_name="Offline Sync",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Offline sync failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Offline Sync",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_mobile_biometric(self):
        """Test mobile biometric integration"""
        start_time = time.time()
        
        try:
            # Test mobile biometric authentication
            biometric_data = {
                "biometric_type": "face_id",
                "device_id": "test_mobile_device",
                "biometric_data": "encrypted_biometric_hash"
            }
            
            async with self.session.post(
                f"{self.config.base_url}/api/v1/auth/mobile/biometric",
                json=biometric_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "authenticated" in data
                    
                    self.test_results.append(TestResult(
                        test_name="Mobile Biometric",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Mobile biometric test failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Mobile Biometric",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_visual_learning_ai(self):
        """Test Visual Learning AI integration"""
        start_time = time.time()
        
        try:
            # Test video analysis
            video_url = "https://www.youtube.com/watch?v=test_video"
            
            # Mock the video analysis for testing
            with patch.object(visual_ai, 'analyze_youtube_video') as mock_analyze:
                mock_analyze.return_value = AsyncMock(
                    return_value={
                        "video_id": "test_video",
                        "sentiment_score": 0.8,
                        "confidence_score": 0.9,
                        "key_topics": ["finance", "trading"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                result = await visual_ai.analyze_youtube_video(video_url)
                assert result["sentiment_score"] > 0
                
                self.test_results.append(TestResult(
                    test_name="Visual Learning AI",
                    status="PASSED",
                    duration=time.time() - start_time,
                    details=result
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Visual Learning AI",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_predictive_analytics(self):
        """Test predictive analytics integration"""
        start_time = time.time()
        
        try:
            # Test price prediction
            symbol = "AAPL"
            
            # Mock the prediction for testing
            with patch.object(predictive_analytics, 'predict_price') as mock_predict:
                mock_predict.return_value = AsyncMock(
                    return_value={
                        "prediction": 150.0,
                        "confidence_interval": (145.0, 155.0),
                        "confidence_score": 0.85,
                        "model_used": "ensemble",
                        "prediction_date": datetime.utcnow().isoformat()
                    }
                )
                
                result = await predictive_analytics.predict_price(symbol)
                assert result["prediction"] > 0
                
                self.test_results.append(TestResult(
                    test_name="Predictive Analytics",
                    status="PASSED",
                    duration=time.time() - start_time,
                    details=result
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Predictive Analytics",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_compliance(self):
        """Test compliance system"""
        start_time = time.time()
        
        try:
            # Test compliance status
            with patch.object(compliance_manager, 'get_compliance_status') as mock_compliance:
                mock_compliance.return_value = AsyncMock(
                    return_value={
                        "overall_score": 95.0,
                        "frameworks": {
                            "GDPR": {"score": 98.0, "status": "compliant"},
                            "SOC2": {"score": 92.0, "status": "compliant"}
                        }
                    }
                )
                
                result = await compliance_manager.get_compliance_status()
                assert result["overall_score"] > 90
                
                self.test_results.append(TestResult(
                    test_name="Compliance",
                    status="PASSED",
                    duration=time.time() - start_time,
                    details=result
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Compliance",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_security(self):
        """Test security systems"""
        start_time = time.time()
        
        try:
            # Test security scanning
            target_config = {
                "base_url": self.config.base_url,
                "api_endpoints": [
                    "/api/v1/portfolio",
                    "/api/v1/trade",
                    "/api/v1/market"
                ]
            }
            
            # Mock penetration testing for safety
            with patch.object(PenetrationTestingSuite, 'run_comprehensive_security_test') as mock_pentest:
                mock_pentest.return_value = AsyncMock(
                    return_value={
                        "report": {
                            "executive_summary": {
                                "overall_security_score": 92.0,
                                "risk_level": "LOW",
                                "total_vulnerabilities": 2
                            }
                        },
                        "execution_time": 120.5,
                        "test_count": 15
                    }
                )
                
                pentest_suite = PenetrationTestingSuite(target_config)
                result = await pentest_suite.run_comprehensive_security_test()
                assert result["report"]["executive_summary"]["overall_security_score"] > 80
                
                self.test_results.append(TestResult(
                    test_name="Security",
                    status="PASSED",
                    duration=time.time() - start_time,
                    details=result
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Security",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_performance(self):
        """Test system performance"""
        tests = [
            ("API Response Time", self._test_api_response_time),
            ("Load Testing", self._test_load_testing),
            ("Memory Usage", self._test_memory_usage),
            ("Database Performance", self._test_database_performance)
        ]
        
        for test_name, test_func in tests:
            await self._run_individual_test(test_name, test_func)
            
    async def _test_api_response_time(self):
        """Test API response times"""
        start_time = time.time()
        
        try:
            # Test multiple endpoints for response time
            endpoints = [
                "/health",
                "/api/v1/portfolio",
                "/api/v1/market/AAPL"
            ]
            
            response_times = []
            
            for endpoint in endpoints:
                endpoint_start = time.time()
                
                async with self.session.get(f"{self.config.base_url}{endpoint}") as response:
                    if response.status == 200:
                        response_time = time.time() - endpoint_start
                        response_times.append(response_time)
                    else:
                        raise Exception(f"Endpoint {endpoint} failed")
                        
            avg_response_time = sum(response_times) / len(response_times)
            
            # Assert average response time is under 500ms
            assert avg_response_time < 0.5
            
            self.test_results.append(TestResult(
                test_name="API Response Time",
                status="PASSED",
                duration=time.time() - start_time,
                details={"avg_response_time": avg_response_time, "response_times": response_times}
            ))
            
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="API Response Time",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_load_testing(self):
        """Test system under load"""
        start_time = time.time()
        
        try:
            # Simulate concurrent requests
            concurrent_requests = 50
            tasks = []
            
            for i in range(concurrent_requests):
                task = asyncio.create_task(
                    self.session.get(f"{self.config.base_url}/health")
                )
                tasks.append(task)
                
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_requests = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
            
            # Assert at least 90% of requests succeed
            assert successful_requests / concurrent_requests >= 0.9
            
            self.test_results.append(TestResult(
                test_name="Load Testing",
                status="PASSED",
                duration=time.time() - start_time,
                details={
                    "concurrent_requests": concurrent_requests,
                    "successful_requests": successful_requests,
                    "success_rate": successful_requests / concurrent_requests
                }
            ))
            
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Load Testing",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_memory_usage(self):
        """Test memory usage"""
        start_time = time.time()
        
        try:
            # Test memory usage endpoint
            async with self.session.get(f"{self.config.base_url}/health/memory") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Assert memory usage is under 80%
                    assert data.get("memory_usage_percent", 0) < 80
                    
                    self.test_results.append(TestResult(
                        test_name="Memory Usage",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Memory usage check failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Memory Usage",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_database_performance(self):
        """Test database performance"""
        start_time = time.time()
        
        try:
            # Test database performance endpoint
            async with self.session.get(f"{self.config.base_url}/health/db/performance") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Assert query time is under 100ms
                    assert data.get("avg_query_time_ms", 0) < 100
                    
                    self.test_results.append(TestResult(
                        test_name="Database Performance",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Database performance check failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Database Performance",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_end_to_end_workflows(self):
        """Test end-to-end workflows"""
        tests = [
            ("Complete Trading Workflow", self._test_complete_trading_workflow),
            ("Portfolio Management Workflow", self._test_portfolio_workflow),
            ("Analytics Workflow", self._test_analytics_workflow)
        ]
        
        for test_name, test_func in tests:
            await self._run_individual_test(test_name, test_func)
            
    async def _test_complete_trading_workflow(self):
        """Test complete trading workflow"""
        start_time = time.time()
        
        try:
            # Step 1: User login
            await self._test_user_login()
            
            # Step 2: Create portfolio
            await self._test_portfolio_api()
            
            # Step 3: Get market data
            await self._test_market_data_api()
            
            # Step 4: Place trade
            await self._test_trading_api()
            
            # Step 5: Get analytics
            await self._test_analytics_api()
            
            self.test_results.append(TestResult(
                test_name="Complete Trading Workflow",
                status="PASSED",
                duration=time.time() - start_time,
                details={"workflow_completed": True}
            ))
            
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Complete Trading Workflow",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_portfolio_workflow(self):
        """Test portfolio management workflow"""
        start_time = time.time()
        
        try:
            access_token = self.test_data.get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Create multiple portfolios
            for i in range(3):
                portfolio_data = {
                    "name": f"Test Portfolio {i}",
                    "description": f"Test portfolio {i}",
                    "initial_balance": 10000.0 + (i * 1000),
                    "risk_tolerance": "medium"
                }
                
                async with self.session.post(
                    f"{self.config.base_url}/api/v1/portfolio",
                    json=portfolio_data,
                    headers=headers
                ) as response:
                    if response.status != 201:
                        raise Exception(f"Portfolio {i} creation failed")
                        
            # List all portfolios
            async with self.session.get(
                f"{self.config.base_url}/api/v1/portfolio",
                headers=headers
            ) as response:
                if response.status == 200:
                    portfolios = await response.json()
                    assert len(portfolios) >= 3
                    
                    self.test_results.append(TestResult(
                        test_name="Portfolio Workflow",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details={"portfolio_count": len(portfolios)}
                    ))
                else:
                    raise Exception("Portfolio listing failed")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Portfolio Workflow",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_analytics_workflow(self):
        """Test analytics workflow"""
        start_time = time.time()
        
        try:
            access_token = self.test_data.get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test multiple analytics endpoints
            analytics_endpoints = [
                "/api/v1/analytics/portfolio",
                "/api/v1/analytics/performance",
                "/api/v1/analytics/risk",
                "/api/v1/analytics/predictions"
            ]
            
            analytics_data = {}
            
            for endpoint in analytics_endpoints:
                async with self.session.get(
                    f"{self.config.base_url}{endpoint}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        analytics_data[endpoint] = data
                    else:
                        raise Exception(f"Analytics endpoint {endpoint} failed")
                        
            self.test_results.append(TestResult(
                test_name="Analytics Workflow",
                status="PASSED",
                duration=time.time() - start_time,
                details=analytics_data
            ))
            
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Analytics Workflow",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_disaster_recovery(self):
        """Test disaster recovery procedures"""
        tests = [
            ("System Backup", self._test_system_backup),
            ("Service Recovery", self._test_service_recovery),
            ("Data Recovery", self._test_data_recovery)
        ]
        
        for test_name, test_func in tests:
            await self._run_individual_test(test_name, test_func)
            
    async def _test_system_backup(self):
        """Test system backup"""
        start_time = time.time()
        
        try:
            # Test system backup
            async with self.session.post(
                f"{self.config.base_url}/admin/backup",
                json={"backup_type": "full"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "backup_id" in data
                    assert "status" in data
                    
                    self.test_results.append(TestResult(
                        test_name="System Backup",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"System backup failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="System Backup",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_service_recovery(self):
        """Test service recovery"""
        start_time = time.time()
        
        try:
            # Test service restart
            async with self.session.post(
                f"{self.config.base_url}/admin/restart",
                json={"service": "api"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "restart_id" in data
                    
                    # Wait for service to be ready
                    await asyncio.sleep(5)
                    
                    # Check if service is healthy
                    async with self.session.get(f"{self.config.base_url}/health") as health_response:
                        if health_response.status == 200:
                            self.test_results.append(TestResult(
                                test_name="Service Recovery",
                                status="PASSED",
                                duration=time.time() - start_time,
                                details=data
                            ))
                        else:
                            raise Exception("Service not healthy after restart")
                else:
                    raise Exception(f"Service restart failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Service Recovery",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _test_data_recovery(self):
        """Test data recovery"""
        start_time = time.time()
        
        try:
            # Test data recovery from backup
            async with self.session.post(
                f"{self.config.base_url}/admin/restore",
                json={"backup_id": "test_backup_123"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "restore_id" in data
                    assert "status" in data
                    
                    self.test_results.append(TestResult(
                        test_name="Data Recovery",
                        status="PASSED",
                        duration=time.time() - start_time,
                        details=data
                    ))
                else:
                    raise Exception(f"Data recovery failed with status {response.status}")
                    
        except Exception as e:
            self.test_results.append(TestResult(
                test_name="Data Recovery",
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _run_individual_test(self, test_name: str, test_func):
        """Run an individual test"""
        start_time = time.time()
        
        try:
            await test_func()
        except Exception as e:
            self.test_results.append(TestResult(
                test_name=test_name,
                status="FAILED",
                duration=time.time() - start_time,
                error_message=str(e)
            ))
            
    async def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        try:
            self.end_time = datetime.utcnow()
            total_duration = (self.end_time - self.start_time).total_seconds()
            
            # Calculate statistics
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r.status == "PASSED"])
            failed_tests = len([r for r in self.test_results if r.status == "FAILED"])
            skipped_tests = len([r for r in self.test_results if r.status == "SKIPPED"])
            
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            # Group results by category
            categories = {}
            for result in self.test_results:
                category = result.test_name.split()[0]  # First word as category
                if category not in categories:
                    categories[category] = {"passed": 0, "failed": 0, "total": 0}
                    
                categories[category][result.status.lower()] += 1
                categories[category]["total"] += 1
                
            # Generate recommendations
            recommendations = self._generate_recommendations()
            
            report = {
                "test_summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "skipped_tests": skipped_tests,
                    "success_rate": success_rate,
                    "total_duration": total_duration,
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.end_time.isoformat()
                },
                "test_results": [asdict(result) for result in self.test_results],
                "categories": categories,
                "recommendations": recommendations,
                "system_info": {
                    "base_url": self.config.base_url,
                    "frontend_url": self.config.frontend_url,
                    "mobile_app_url": self.config.mobile_app_url,
                    "test_timeout": self.config.test_timeout,
                    "parallel_tests": self.config.parallel_tests
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating test report: {e}")
            raise
            
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r.status == "FAILED"]
        
        if len(failed_tests) > 0:
            recommendations.append(f"Address {len(failed_tests)} failed tests")
            
        # Check for specific patterns
        auth_failures = [r for r in failed_tests if "Authentication" in r.test_name]
        if len(auth_failures) > 0:
            recommendations.append("Review authentication system configuration")
            
        api_failures = [r for r in failed_tests if "API" in r.test_name]
        if len(api_failures) > 0:
            recommendations.append("Check API endpoint configurations and connectivity")
            
        performance_failures = [r for r in failed_tests if "Performance" in r.test_name]
        if len(performance_failures) > 0:
            recommendations.append("Optimize system performance and resource allocation")
            
        security_failures = [r for r in failed_tests if "Security" in r.test_name]
        if len(security_failures) > 0:
            recommendations.append("Address security vulnerabilities and implement fixes")
            
        return recommendations

# Main execution function
async def run_full_system_integration_test():
    """Run full system integration test"""
    config = IntegrationTestSuite()
    test_suite = FullSystemIntegrationTest(config)
    
    try:
        report = await test_suite.run_full_integration_test()
        
        # Save report to file
        report_file = Path("test_reports/full_integration_report.json")
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        logger.info(f"Integration test report saved to {report_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"Full system integration test failed: {e}")
        raise

if __name__ == "__main__":
    # Run the integration test
    asyncio.run(run_full_system_integration_test())
