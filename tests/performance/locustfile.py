"""
Locust Performance Test Suite
Simulates 10,000+ concurrent users
Tests API endpoints, WebSocket, and trading operations
"""

from locust import HttpUser, WebSocketUser, task, between, events
from locust.exception import StopUser
import random
import json
import time
from typing import Optional


class APIUser(HttpUser):
    """Simulates API users"""
    wait_time = between(1, 5)
    weight = 3  # 75% of users
    
    def on_start(self):
        """Login on start"""
        self.client.post("/api/v1/auth/login", json={
            "username": f"user_{self.user_id}",
            "password": "test_password_123"
        })
        self.token = "mock_jwt_token"
    
    @task(5)
    def get_portfolio(self):
        """Get portfolio data"""
        self.client.get(
            "/api/v1/portfolio",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(10)
    def get_market_data(self):
        """Get market prices"""
        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "BTC", "ETH"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/v1/market/price/{symbol}")
    
    @task(3)
    def get_ai_prediction(self):
        """Get AI prediction (heavier endpoint)"""
        self.client.post(
            "/api/v1/ai/predict",
            json={"symbol": "AAPL", "timeframe": "1d"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def execute_trade(self):
        """Simulate trade execution"""
        self.client.post(
            "/api/v1/trade/order",
            json={
                "symbol": random.choice(["AAPL", "MSFT", "TSLA"]),
                "side": random.choice(["buy", "sell"]),
                "quantity": random.randint(1, 100),
                "order_type": "market"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def get_vision_analysis(self):
        """Oracle Vision chart analysis (compute intensive)"""
        self.client.post(
            "/api/v1/vision/analyze",
            json={
                "symbol": "BTC",
                "chart_data": {"timeframe": "1h", "bars": 100}
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )


class WebSocketUser(WebSocketUser):
    """Simulates WebSocket connections"""
    wait_time = between(0.5, 2)
    weight = 2  # Simulates real-time traders
    
    def on_start(self):
        """Connect to WebSocket"""
        self.client.connect("/ws")
        self.client.send(json.dumps({
            "type": "subscribe",
            "symbols": ["AAPL", "BTC", "ETH"]
        }))
    
    @task(1)
    def subscribe_to_symbols(self):
        """Subscribe to price updates"""
        symbols = ["MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]
        subset = random.sample(symbols, k=random.randint(1, 3))
        self.client.send(json.dumps({
            "type": "subscribe",
            "symbols": subset
        }))
    
    @task(10)
    def heartbeat(self):
        """Send heartbeat to keep connection alive"""
        self.client.send(json.dumps({"type": "ping", "timestamp": time.time()}))
    
    def on_message(self, message):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            if data.get("type") == "price_update":
                # Simulate processing delay
                time.sleep(0.01)
        except:
            pass


class PowerUser(HttpUser):
    """Simulates power users (heavy API usage)"""
    wait_time = between(0.1, 1)
    weight = 1
    
    def on_start(self):
        """Login and setup"""
        self.client.post("/api/v1/auth/login", json={
            "username": f"power_user_{self.user_id}",
            "password": "test_password_123"
        })
        self.token = "mock_jwt_token"
    
    @task(20)
    def rapid_price_check(self):
        """Rapid price checks"""
        symbols = ["BTC", "ETH", "AAPL", "TSLA"]
        symbol = random.choice(symbols)
        self.client.get(
            f"/api/v1/market/price/{symbol}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(5)
    def batch_operations(self):
        """Batch API calls"""
        # Multiple rapid requests
        for _ in range(5):
            self.client.get(
                "/api/v1/portfolio/summary",
                headers={"Authorization": f"Bearer {self.token}"}
            )
    
    @task(2)
    def heavy_ml_request(self):
        """ML prediction requests"""
        self.client.post(
            "/api/v1/ai/ensemble-predict",
            json={
                "symbols": ["AAPL", "MSFT", "GOOGL"],
                "models": ["lstm", "xgboost", "random_forest"]
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )


class MobileUser(HttpUser):
    """Simulates mobile app users"""
    wait_time = between(5, 15)
    weight = 4
    
    def on_start(self):
        self.token = "mock_mobile_token"
    
    @task(10)
    def mobile_dashboard(self):
        """Mobile dashboard load"""
        self.client.get(
            "/api/v1/mobile/dashboard",
            headers={
                "Authorization": f"Bearer {self.token}",
                "X-Client-Version": "1.0.0"
            }
        )
    
    @task(5)
    def mobile_portfolio(self):
        """Mobile portfolio view"""
        self.client.get(
            "/api/v1/portfolio/mobile",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def biometric_auth(self):
        """Simulate biometric authentication"""
        self.client.post(
            "/api/v1/auth/biometric",
            json={"type": "fingerprint", "verified": True},
            headers={"Authorization": f"Bearer {self.token}"}
        )


# Event hooks for custom metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, 
               response, context, exception, **kwargs):
    """Log slow requests"""
    if response_time > 1000:  # 1 second
        print(f"SLOW REQUEST: {name} took {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Setup before test"""
    print("="*60)
    print("PERFORMANCE TEST STARTING")
    print("Target: 10,000+ concurrent users")
    print("="*60)


@events.test_stop.add_listener  
def on_test_stop(environment, **kwargs):
    """Cleanup after test"""
    print("="*60)
    print("PERFORMANCE TEST COMPLETED")
    print("="*60)


# Custom load shape for gradual ramp-up
class GradualRampUp:
    """Gradually ramp up to 10,000 users"""
    
    def __init__(self):
        self.target_users = 10000
        self.ramp_duration = 600  # 10 minutes to ramp
        self.steady_duration = 1800  # 30 minutes steady
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time < self.ramp_duration:
            # Ramp up phase
            progress = run_time / self.ramp_duration
            user_count = int(self.target_users * progress)
            spawn_rate = user_count / 60  # Users per second
            return user_count, spawn_rate
        elif run_time < self.ramp_duration + self.steady_duration:
            # Steady state
            return self.target_users, 100
        else:
            # Ramp down
            return 0, 100
    
    def get_run_time(self):
        return time.time() - self.start_time if hasattr(self, 'start_time') else 0


# Test configuration
TEST_CONFIG = {
    "target_users": 10000,
    "spawn_rate": 100,  # users per second
    "test_duration": 2400,  # 40 minutes
    "host": "https://staging-api.financialmaster.com",
    "headless": False,
    "autostart": True
}
