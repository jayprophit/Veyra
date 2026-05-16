"""
WebSocket Load Testing
Tests WebSocket scalability with thousands of concurrent connections
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp
import websockets
import statistics


@dataclass
class LoadTestResult:
    """WebSocket load test results"""
    test_id: str
    concurrent_connections: int
    duration_seconds: int
    
    # Metrics
    connections_established: int = 0
    connections_failed: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    messages_failed: int = 0
    
    # Latency
    latency_min_ms: float = 0
    latency_max_ms: float = 0
    latency_avg_ms: float = 0
    latency_p95_ms: float = 0
    latency_p99_ms: float = 0
    
    # Errors
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    started_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.utcnow()
    
    @property
    def success_rate(self) -> float:
        total = self.connections_established + self.connections_failed
        if total == 0:
            return 0
        return (self.connections_established / total) * 100
    
    @property
    def throughput_per_second(self) -> float:
        if not self.completed_at:
            return 0
        duration = (self.completed_at - self.started_at).total_seconds()
        if duration == 0:
            return 0
        return self.messages_received / duration


class WebSocketLoadTester:
    """
    WebSocket Load Testing Tool
    
    Simulates thousands of concurrent WebSocket connections
    Measures latency, throughput, and connection stability
    
    Usage:
        tester = WebSocketLoadTester("ws://localhost:8000/ws")
        results = await tester.run_load_test(
            concurrent_connections=10000,
            duration_seconds=300,
            messages_per_connection=100
        )
    """
    
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.results: List[LoadTestResult] = []
        self.latencies: List[float] = []
    
    async def run_load_test(
        self,
        concurrent_connections: int = 1000,
        duration_seconds: int = 60,
        messages_per_connection: int = 50,
        connection_delay_ms: int = 10
    ) -> LoadTestResult:
        """
        Run WebSocket load test
        
        Args:
            concurrent_connections: Number of simultaneous connections
            duration_seconds: How long to run the test
            messages_per_connection: Messages to send per connection
            connection_delay_ms: Delay between connection attempts
        """
        test_id = f"load_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        result = LoadTestResult(
            test_id=test_id,
            concurrent_connections=concurrent_connections,
            duration_seconds=duration_seconds
        )
        
        print(f"Starting WebSocket load test: {concurrent_connections} connections for {duration_seconds}s")
        
        # Create connections gradually
        tasks = []
        for i in range(concurrent_connections):
            task = asyncio.create_task(
                self._simulate_client(
                    client_id=i,
                    duration=duration_seconds,
                    messages=messages_per_connection,
                    result=result
                )
            )
            tasks.append(task)
            
            # Small delay between connections to prevent thundering herd
            if connection_delay_ms > 0:
                await asyncio.sleep(connection_delay_ms / 1000)
        
        # Wait for all connections to complete or timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=duration_seconds + 30  # Extra buffer
            )
        except asyncio.TimeoutError:
            print("Test timed out")
        
        # Calculate statistics
        result.completed_at = datetime.utcnow()
        
        if self.latencies:
            result.latency_min_ms = min(self.latencies)
            result.latency_max_ms = max(self.latencies)
            result.latency_avg_ms = statistics.mean(self.latencies)
            result.latency_p95_ms = self._percentile(self.latencies, 95)
            result.latency_p99_ms = self._percentile(self.latencies, 99)
        
        self.results.append(result)
        
        self._print_results(result)
        
        return result
    
    async def _simulate_client(
        self,
        client_id: int,
        duration: int,
        messages: int,
        result: LoadTestResult
    ):
        """Simulate a single WebSocket client"""
        start_time = time.time()
        
        try:
            async with websockets.connect(self.ws_url) as ws:
                result.connections_established += 1
                
                # Subscribe to symbols
                subscribe_msg = {
                    "type": "subscribe",
                    "symbols": ["AAPL", "MSFT", "TSLA"]
                }
                await ws.send(json.dumps(subscribe_msg))
                
                # Send ping messages periodically
                messages_sent = 0
                while messages_sent < messages and (time.time() - start_time) < duration:
                    ping_start = time.time()
                    
                    ping_msg = {"type": "ping", "timestamp": ping_start}
                    await ws.send(json.dumps(ping_msg))
                    result.messages_sent += 1
                    messages_sent += 1
                    
                    # Wait for pong
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=5)
                        result.messages_received += 1
                        
                        # Calculate latency
                        latency_ms = (time.time() - ping_start) * 1000
                        self.latencies.append(latency_ms)
                        
                    except asyncio.TimeoutError:
                        result.messages_failed += 1
                        result.errors.append({
                            "client_id": client_id,
                            "error": "Timeout waiting for response",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    
                    # Wait before next message
                    await asyncio.sleep(0.5)
                    
        except Exception as e:
            result.connections_failed += 1
            result.errors.append({
                "client_id": client_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _print_results(self, result: LoadTestResult):
        """Print test results"""
        print("\n" + "="*60)
        print("WEBSOCKET LOAD TEST RESULTS")
        print("="*60)
        print(f"Test ID: {result.test_id}")
        print(f"Duration: {result.duration_seconds}s")
        print(f"Target Connections: {result.concurrent_connections}")
        print()
        print("CONNECTION METRICS:")
        print(f"  Established: {result.connections_established}")
        print(f"  Failed: {result.connections_failed}")
        print(f"  Success Rate: {result.success_rate:.2f}%")
        print()
        print("MESSAGE METRICS:")
        print(f"  Sent: {result.messages_sent}")
        print(f"  Received: {result.messages_received}")
        print(f"  Failed: {result.messages_failed}")
        print(f"  Throughput: {result.throughput_per_second:.2f} msg/s")
        print()
        print("LATENCY (ms):")
        print(f"  Min: {result.latency_min_ms:.2f}")
        print(f"  Avg: {result.latency_avg_ms:.2f}")
        print(f"  Max: {result.latency_max_ms:.2f}")
        print(f"  P95: {result.latency_p95_ms:.2f}")
        print(f"  P99: {result.latency_p99_ms:.2f}")
        print()
        print("ERRORS:")
        print(f"  Total: {len(result.errors)}")
        if result.errors:
            print(f"  First 3: {[e['error'] for e in result.errors[:3]]}")
        print("="*60)
    
    async def stress_test(
        self,
        max_connections: int = 50000,
        ramp_up_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Gradually ramp up connections until failure
        
        Finds maximum sustainable connections
        """
        print(f"Starting stress test: ramping to {max_connections} connections over {ramp_up_seconds}s")
        
        step_size = 1000
        current_connections = 0
        sustainable_limit = 0
        
        while current_connections < max_connections:
            current_connections += step_size
            
            print(f"Testing {current_connections} connections...")
            
            result = await self.run_load_test(
                concurrent_connections=current_connections,
                duration_seconds=30,  # Short test per step
                messages_per_connection=10
            )
            
            if result.success_rate >= 95 and result.latency_p95_ms < 1000:
                sustainable_limit = current_connections
                print(f"  ✓ Success: {result.success_rate:.1f}% @ {result.latency_p95_ms:.0f}ms P95")
            else:
                print(f"  ✗ Failed: {result.success_rate:.1f}% @ {result.latency_p95_ms:.0f}ms P95")
                break
        
        return {
            "max_sustainable_connections": sustainable_limit,
            "failure_point": current_connections,
            "recommended_limit": int(sustainable_limit * 0.8),  # 80% for safety
            "test_timestamp": datetime.utcnow().isoformat()
        }
    
    async def generate_report(self, output_file: str = "websocket_load_test_report.json"):
        """Generate comprehensive test report"""
        if not self.results:
            return
        
        report = {
            "test_summary": {
                "total_tests": len(self.results),
                "max_connections_tested": max(r.concurrent_connections for r in self.results),
                "best_success_rate": max(r.success_rate for r in self.results),
                "lowest_latency_p95": min(r.latency_p95_ms for r in self.results if r.latency_p95_ms > 0),
            },
            "tests": [
                {
                    "test_id": r.test_id,
                    "concurrent_connections": r.concurrent_connections,
                    "duration": r.duration_seconds,
                    "success_rate": r.success_rate,
                    "latency_p95_ms": r.latency_p95_ms,
                    "throughput": r.throughput_per_second,
                    "errors_count": len(r.errors)
                }
                for r in self.results
            ],
            "recommendations": self._generate_recommendations()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {output_file}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate scaling recommendations"""
        recommendations = []
        
        if not self.results:
            return recommendations
        
        # Find best performing test
        best = max(self.results, key=lambda r: r.success_rate)
        
        if best.success_rate < 99:
            recommendations.append(
                f"Consider connection pooling - only {best.success_rate:.1f}% connection success rate"
            )
        
        if best.latency_p95_ms > 500:
            recommendations.append(
                f"High latency detected: P95 = {best.latency_p95_ms:.0f}ms. "
                "Consider WebSocket connection multiplexing or regional load balancing"
            )
        
        if best.concurrent_connections < 10000:
            recommendations.append(
                f"Current limit: {best.concurrent_connections} connections. "
                "Consider horizontal scaling with multiple WebSocket servers"
            )
        
        recommendations.append(
            f"Recommended production limit: {int(best.concurrent_connections * 0.7)} connections "
            "(70% of tested max for safety margin)"
        )
        
        return recommendations


# Quick test runner
async def quick_test():
    """Run quick WebSocket load test"""
    tester = WebSocketLoadTester("ws://localhost:8000/ws")
    
    # Test 1000 concurrent connections for 30 seconds
    result = await tester.run_load_test(
        concurrent_connections=1000,
        duration_seconds=30,
        messages_per_connection=20
    )
    
    return result


if __name__ == "__main__":
    # Run test
    asyncio.run(quick_test())
