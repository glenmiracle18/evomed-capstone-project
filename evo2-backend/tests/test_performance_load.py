"""
Performance and Load Testing for African Population-Aware Variant Analysis System

This test suite validates system performance under various load conditions
and measures key performance metrics including response times, throughput,
and resource utilization.
"""

import asyncio
import aiohttp
import time
import json
import statistics
import threading
import psutil
import concurrent.futures
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class PerformanceResult:
    """Data class for storing performance test results"""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float]
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput_rps: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: str


class PerformanceMonitor:
    """Monitor system resources during testing"""
    
    def __init__(self):
        self.monitoring = False
        self.cpu_readings = []
        self.memory_readings = []
    
    def start_monitoring(self):
        """Start monitoring system resources"""
        self.monitoring = True
        self.cpu_readings = []
        self.memory_readings = []
        
        def monitor():
            while self.monitoring:
                self.cpu_readings.append(psutil.cpu_percent())
                self.memory_readings.append(psutil.virtual_memory().used / 1024 / 1024)  # MB
                time.sleep(0.5)
        
        self.monitor_thread = threading.Thread(target=monitor)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring and return average readings"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        
        avg_cpu = statistics.mean(self.cpu_readings) if self.cpu_readings else 0
        avg_memory = statistics.mean(self.memory_readings) if self.memory_readings else 0
        
        return avg_cpu, avg_memory


class LoadTester:
    """Load testing framework for the variant analysis API"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.monitor = PerformanceMonitor()
        
        # Test variant data sets
        self.test_variants = [
            {
                "variant_position": 5227002,
                "alternative": "A",
                "genome": "hg38",
                "chromosome": "chr11",
                "use_african_adjustment": True
            },
            {
                "variant_position": 43057063,
                "alternative": "G",
                "genome": "hg38",
                "chromosome": "chr17",
                "use_african_adjustment": True
            },
            {
                "variant_position": 158481978,
                "alternative": "C",
                "genome": "hg38",
                "chromosome": "chr2",
                "use_african_adjustment": True
            },
            {
                "variant_position": 176206982,
                "alternative": "T",
                "genome": "hg38",
                "chromosome": "chr3",
                "use_african_adjustment": True
            }
        ]
    
    async def single_request(self, session: aiohttp.ClientSession, variant_data: dict) -> Dict[str, Any]:
        """Make a single API request and measure response time"""
        start_time = time.time()
        try:
            async with session.post(
                f"{self.api_url}/analyze_variant",
                json=variant_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response_time": response_time,
                        "result": result
                    }
                else:
                    return {
                        "success": False,
                        "response_time": response_time,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def run_load_test(self, concurrent_users: int, requests_per_user: int) -> PerformanceResult:
        """Run load test with specified concurrency and request count"""
        print(f"Starting load test: {concurrent_users} concurrent users, {requests_per_user} requests each")
        
        total_requests = concurrent_users * requests_per_user
        self.monitor.start_monitoring()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Create tasks for concurrent execution
            for user in range(concurrent_users):
                for request in range(requests_per_user):
                    variant_data = self.test_variants[request % len(self.test_variants)]
                    tasks.append(self.single_request(session, variant_data))
            
            # Execute all requests concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
        
        avg_cpu, avg_memory = self.monitor.stop_monitoring()
        
        # Analyze results
        successful_requests = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_requests = [r for r in results if not isinstance(r, dict) or not r.get("success")]
        
        response_times = [r["response_time"] for r in successful_requests]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = np.percentile(response_times, 95)
            p99_response_time = np.percentile(response_times, 99)
        else:
            avg_response_time = median_response_time = p95_response_time = p99_response_time = 0
        
        throughput = len(successful_requests) / total_time if total_time > 0 else 0
        error_rate = len(failed_requests) / total_requests * 100
        
        return PerformanceResult(
            test_name=f"Load Test ({concurrent_users} users, {requests_per_user} req/user)",
            total_requests=total_requests,
            successful_requests=len(successful_requests),
            failed_requests=len(failed_requests),
            response_times=response_times,
            avg_response_time=avg_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            throughput_rps=throughput,
            error_rate=error_rate,
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu,
            timestamp=datetime.now().isoformat()
        )
    
    def run_stress_test(self) -> List[PerformanceResult]:
        """Run stress test with increasing load"""
        print("Starting stress test with increasing load...")
        
        stress_scenarios = [
            (1, 10),   # 1 user, 10 requests
            (5, 10),   # 5 users, 10 requests each
            (10, 10),  # 10 users, 10 requests each
            (20, 5),   # 20 users, 5 requests each
            (50, 2),   # 50 users, 2 requests each
        ]
        
        results = []
        for concurrent_users, requests_per_user in stress_scenarios:
            try:
                result = asyncio.run(self.run_load_test(concurrent_users, requests_per_user))
                results.append(result)
                print(f"✓ Completed: {result.test_name}")
                print(f"  Success rate: {(result.successful_requests/result.total_requests)*100:.1f}%")
                print(f"  Avg response: {result.avg_response_time:.2f}s")
                print(f"  Throughput: {result.throughput_rps:.1f} req/s")
                print()
                
                # Brief pause between tests
                time.sleep(2)
                
            except Exception as e:
                print(f"✗ Failed: {concurrent_users} users, {requests_per_user} req/user - {e}")
        
        return results
    
    def run_endurance_test(self, duration_minutes: int = 5) -> PerformanceResult:
        """Run endurance test for specified duration"""
        print(f"Starting endurance test for {duration_minutes} minutes...")
        
        duration_seconds = duration_minutes * 60
        end_time = time.time() + duration_seconds
        
        self.monitor.start_monitoring()
        
        all_results = []
        request_count = 0
        
        async def endurance_loop():
            nonlocal all_results, request_count
            
            async with aiohttp.ClientSession() as session:
                while time.time() < end_time:
                    variant_data = self.test_variants[request_count % len(self.test_variants)]
                    result = await self.single_request(session, variant_data)
                    all_results.append(result)
                    request_count += 1
                    
                    # Small delay to simulate realistic usage
                    await asyncio.sleep(0.1)
        
        start_time = time.time()
        asyncio.run(endurance_loop())
        total_time = time.time() - start_time
        
        avg_cpu, avg_memory = self.monitor.stop_monitoring()
        
        # Analyze endurance results
        successful_requests = [r for r in all_results if r.get("success")]
        failed_requests = [r for r in all_results if not r.get("success")]
        
        response_times = [r["response_time"] for r in successful_requests]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = np.percentile(response_times, 95)
            p99_response_time = np.percentile(response_times, 99)
        else:
            avg_response_time = median_response_time = p95_response_time = p99_response_time = 0
        
        throughput = len(successful_requests) / total_time if total_time > 0 else 0
        error_rate = len(failed_requests) / len(all_results) * 100 if all_results else 0
        
        return PerformanceResult(
            test_name=f"Endurance Test ({duration_minutes} minutes)",
            total_requests=len(all_results),
            successful_requests=len(successful_requests),
            failed_requests=len(failed_requests),
            response_times=response_times,
            avg_response_time=avg_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            throughput_rps=throughput,
            error_rate=error_rate,
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu,
            timestamp=datetime.now().isoformat()
        )


def generate_performance_report(results: List[PerformanceResult], output_file: str = "performance_report.json"):
    """Generate comprehensive performance report"""
    
    report = {
        "test_suite": "African Population-Aware Variant Analysis - Performance Testing",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": len(results),
            "total_requests": sum(r.total_requests for r in results),
            "total_successful": sum(r.successful_requests for r in results),
            "overall_success_rate": sum(r.successful_requests for r in results) / sum(r.total_requests for r in results) * 100 if results else 0,
            "avg_response_time": statistics.mean([r.avg_response_time for r in results]) if results else 0,
            "max_throughput": max([r.throughput_rps for r in results]) if results else 0
        },
        "detailed_results": []
    }
    
    for result in results:
        report["detailed_results"].append({
            "test_name": result.test_name,
            "metrics": {
                "total_requests": result.total_requests,
                "successful_requests": result.successful_requests,
                "failed_requests": result.failed_requests,
                "success_rate_percent": (result.successful_requests / result.total_requests * 100) if result.total_requests > 0 else 0,
                "avg_response_time_seconds": result.avg_response_time,
                "median_response_time_seconds": result.median_response_time,
                "p95_response_time_seconds": result.p95_response_time,
                "p99_response_time_seconds": result.p99_response_time,
                "throughput_requests_per_second": result.throughput_rps,
                "error_rate_percent": result.error_rate,
                "avg_memory_usage_mb": result.memory_usage_mb,
                "avg_cpu_usage_percent": result.cpu_usage_percent
            },
            "meets_requirements": {
                "response_time_under_5s": result.avg_response_time < 5.0,
                "success_rate_above_95": (result.successful_requests / result.total_requests * 100) > 95 if result.total_requests > 0 else False,
                "error_rate_below_1": result.error_rate < 1.0
            },
            "timestamp": result.timestamp
        })
    
    # Save report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report


def create_performance_visualizations(results: List[PerformanceResult]):
    """Create performance visualization charts"""
    
    if not results:
        return
    
    # Response time comparison
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Response time comparison
    test_names = [r.test_name for r in results]
    avg_times = [r.avg_response_time for r in results]
    p95_times = [r.p95_response_time for r in results]
    
    x = np.arange(len(test_names))
    width = 0.35
    
    ax1.bar(x - width/2, avg_times, width, label='Average', alpha=0.8)
    ax1.bar(x + width/2, p95_times, width, label='95th Percentile', alpha=0.8)
    ax1.set_xlabel('Test Scenarios')
    ax1.set_ylabel('Response Time (seconds)')
    ax1.set_title('Response Time Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(test_names, rotation=45, ha='right')
    ax1.legend()
    ax1.axhline(y=5, color='r', linestyle='--', label='5s Requirement')
    
    # 2. Throughput comparison
    throughputs = [r.throughput_rps for r in results]
    ax2.bar(test_names, throughputs, alpha=0.8, color='green')
    ax2.set_xlabel('Test Scenarios')
    ax2.set_ylabel('Throughput (requests/second)')
    ax2.set_title('Throughput Comparison')
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Success rate comparison
    success_rates = [(r.successful_requests / r.total_requests * 100) if r.total_requests > 0 else 0 for r in results]
    ax3.bar(test_names, success_rates, alpha=0.8, color='blue')
    ax3.set_xlabel('Test Scenarios')
    ax3.set_ylabel('Success Rate (%)')
    ax3.set_title('Success Rate Comparison')
    ax3.set_ylim(0, 105)
    ax3.axhline(y=95, color='r', linestyle='--', label='95% Target')
    ax3.tick_params(axis='x', rotation=45)
    ax3.legend()
    
    # 4. Resource usage
    memory_usage = [r.memory_usage_mb for r in results]
    cpu_usage = [r.cpu_usage_percent for r in results]
    
    ax4_twin = ax4.twinx()
    ax4.bar([i - 0.2 for i in range(len(test_names))], memory_usage, width=0.4, alpha=0.8, color='orange', label='Memory (MB)')
    ax4_twin.bar([i + 0.2 for i in range(len(test_names))], cpu_usage, width=0.4, alpha=0.8, color='purple', label='CPU (%)')
    
    ax4.set_xlabel('Test Scenarios')
    ax4.set_ylabel('Memory Usage (MB)', color='orange')
    ax4_twin.set_ylabel('CPU Usage (%)', color='purple')
    ax4.set_title('Resource Usage Comparison')
    ax4.set_xticks(range(len(test_names)))
    ax4.set_xticklabels(test_names, rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('performance_results.png', dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    # Configuration
    API_URL = "https://your-endpoint.modal.run"  # Update with actual endpoint
    
    print("🚀 Starting Performance and Load Testing")
    print("="*60)
    
    # Initialize load tester
    tester = LoadTester(API_URL)
    
    all_results = []
    
    try:
        # 1. Basic performance test
        print("1. Running basic performance test...")
        basic_result = asyncio.run(tester.run_load_test(1, 5))
        all_results.append(basic_result)
        
        # 2. Stress testing
        print("\n2. Running stress tests...")
        stress_results = tester.run_stress_test()
        all_results.extend(stress_results)
        
        # 3. Endurance testing
        print("\n3. Running endurance test...")
        endurance_result = tester.run_endurance_test(3)  # 3 minutes
        all_results.append(endurance_result)
        
        # 4. Generate report
        print("\n4. Generating performance report...")
        report = generate_performance_report(all_results)
        
        # 5. Create visualizations
        print("5. Creating performance visualizations...")
        create_performance_visualizations(all_results)
        
        # 6. Print summary
        print(f"\n{'='*60}")
        print("PERFORMANCE TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests completed: {len(all_results)}")
        print(f"Total requests processed: {sum(r.total_requests for r in all_results)}")
        print(f"Overall success rate: {report['summary']['overall_success_rate']:.1f}%")
        print(f"Average response time: {report['summary']['avg_response_time']:.2f}s")
        print(f"Maximum throughput: {report['summary']['max_throughput']:.1f} req/s")
        
        # Check if requirements are met
        requirements_met = all(
            result.avg_response_time < 5.0 and 
            (result.successful_requests / result.total_requests * 100) > 95
            for result in all_results if result.total_requests > 0
        )
        
        if requirements_met:
            print("\n✅ All performance requirements met!")
        else:
            print("\n⚠️  Some performance requirements not met. Review detailed results.")
        
        print(f"\nDetailed results saved to: performance_report.json")
        print(f"Visualizations saved to: performance_results.png")
        
    except Exception as e:
        print(f"\n❌ Performance testing failed: {e}")
        import traceback
        traceback.print_exc()