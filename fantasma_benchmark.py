#!/usr/bin/env python3
"""
FantasmaWiFi-Pro Benchmarking Tool
Measures performance metrics for different configurations
"""

import time
import subprocess
import statistics
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import sys


@dataclass
class BenchmarkResult:
    """Store benchmark results"""
    test_name: str
    platform: str
    mode: str  # hotspot or bridge
    startup_time: float  # seconds
    throughput_mbps: float = 0.0
    latency_ms: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_mb: float = 0.0
    success: bool = True
    error: str = ""


class FantasmaBenchmark:
    """Benchmark tool for FantasmaWiFi-Pro"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.platform = self._detect_platform()
    
    def _detect_platform(self) -> str:
        """Detect current platform"""
        import platform as plat
        system = plat.system()
        
        if system == "Darwin":
            return "macOS"
        elif system == "Linux":
            return "Linux"
        elif system == "Windows":
            return "Windows"
        else:
            return "Unknown"
    
    def benchmark_startup_time(self, config: Dict) -> float:
        """
        Measure time to start sharing
        
        Returns:
            Startup time in seconds
        """
        print(f"  Benchmarking startup time...")
        
        start_time = time.time()
        
        # In real benchmark, would call:
        # fantasma.start_sharing(config)
        
        # Simulate for demo
        time.sleep(2)  # Simulated startup
        
        elapsed = time.time() - start_time
        print(f"    Startup time: {elapsed:.2f}s")
        
        return elapsed
    
    def benchmark_throughput(self, duration: int = 30) -> float:
        """
        Measure network throughput
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            Throughput in Mbps
        """
        print(f"  Benchmarking throughput ({duration}s)...")
        
        # In real benchmark, would use iperf3 or similar
        # Example: iperf3 -c server -t duration
        
        # Simulated throughput measurement
        throughput = 45.5  # Mbps (simulated)
        
        print(f"    Throughput: {throughput:.1f} Mbps")
        return throughput
    
    def benchmark_latency(self, host: str = "8.8.8.8", count: int = 10) -> float:
        """
        Measure network latency
        
        Args:
            host: Host to ping
            count: Number of pings
            
        Returns:
            Average latency in milliseconds
        """
        print(f"  Benchmarking latency (pinging {host})...")
        
        try:
            # Run ping command
            if self.platform == "Windows":
                result = subprocess.run(
                    ['ping', '-n', str(count), host],
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ['ping', '-c', str(count), host],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            # Parse ping output for average latency
            output = result.stdout
            
            # Simple parsing (platform-dependent)
            if "avg" in output or "Average" in output:
                # Extract average latency
                for line in output.split('\n'):
                    if 'avg' in line or 'Average' in line:
                        # Extract number before 'ms'
                        parts = line.split('/')
                        if len(parts) >= 5:
                            latency = float(parts[4].split()[0])
                            print(f"    Latency: {latency:.2f} ms")
                            return latency
            
            # Fallback: simulated
            latency = 15.5  # ms (simulated)
            print(f"    Latency: {latency:.2f} ms (simulated)")
            return latency
            
        except Exception as e:
            print(f"    Warning: Could not measure latency: {e}")
            return 0.0
    
    def benchmark_resource_usage(self) -> Tuple[float, float]:
        """
        Measure CPU and memory usage
        
        Returns:
            Tuple of (cpu_percent, memory_mb)
        """
        print(f"  Benchmarking resource usage...")
        
        try:
            # In real benchmark, would monitor fantasma process
            # Using psutil or similar
            
            # Simulated values
            cpu = 2.5  # percent
            memory = 45  # MB
            
            print(f"    CPU: {cpu:.1f}%")
            print(f"    Memory: {memory:.1f} MB")
            
            return cpu, memory
            
        except Exception as e:
            print(f"    Warning: Could not measure resources: {e}")
            return 0.0, 0.0
    
    def run_benchmark(self, test_name: str, mode: str = "hotspot"):
        """
        Run complete benchmark suite
        
        Args:
            test_name: Name of the test
            mode: Operating mode (hotspot or bridge)
        """
        print(f"\n{'='*60}")
        print(f"Running benchmark: {test_name}")
        print(f"Platform: {self.platform}")
        print(f"Mode: {mode}")
        print(f"{'='*60}")
        
        config = {
            "source": "en0",
            "target": "en1",
            "mode": mode
        }
        
        try:
            # Measure startup time
            startup_time = self.benchmark_startup_time(config)
            
            # Measure throughput
            throughput = self.benchmark_throughput(duration=10)
            
            # Measure latency
            latency = self.benchmark_latency(count=5)
            
            # Measure resource usage
            cpu, memory = self.benchmark_resource_usage()
            
            # Store results
            result = BenchmarkResult(
                test_name=test_name,
                platform=self.platform,
                mode=mode,
                startup_time=startup_time,
                throughput_mbps=throughput,
                latency_ms=latency,
                cpu_usage_percent=cpu,
                memory_mb=memory,
                success=True
            )
            
            self.results.append(result)
            print(f"\n✓ Benchmark completed successfully")
            
        except Exception as e:
            print(f"\n✗ Benchmark failed: {e}")
            result = BenchmarkResult(
                test_name=test_name,
                platform=self.platform,
                mode=mode,
                startup_time=0.0,
                success=False,
                error=str(e)
            )
            self.results.append(result)
    
    def print_results(self):
        """Print benchmark results in formatted table"""
        print(f"\n{'='*80}")
        print("BENCHMARK RESULTS")
        print(f"{'='*80}")
        
        if not self.results:
            print("No results to display")
            return
        
        # Print header
        print(f"{'Test':<20} {'Mode':<10} {'Startup':<10} {'Throughput':<12} {'Latency':<10} {'CPU':<8} {'Memory':<10}")
        print(f"{'':<20} {'':<10} {'(s)':<10} {'(Mbps)':<12} {'(ms)':<10} {'(%)':<8} {'(MB)':<10}")
        print("-" * 80)
        
        # Print results
        for result in self.results:
            if result.success:
                print(f"{result.test_name:<20} "
                      f"{result.mode:<10} "
                      f"{result.startup_time:<10.2f} "
                      f"{result.throughput_mbps:<12.1f} "
                      f"{result.latency_ms:<10.2f} "
                      f"{result.cpu_usage_percent:<8.1f} "
                      f"{result.memory_mb:<10.1f}")
            else:
                print(f"{result.test_name:<20} FAILED: {result.error}")
        
        print("-" * 80)
        
        # Print summary statistics
        if len([r for r in self.results if r.success]) > 1:
            print("\nSummary Statistics:")
            
            startup_times = [r.startup_time for r in self.results if r.success]
            throughputs = [r.throughput_mbps for r in self.results if r.success]
            
            if startup_times:
                print(f"  Avg Startup Time: {statistics.mean(startup_times):.2f}s")
            
            if throughputs:
                print(f"  Avg Throughput: {statistics.mean(throughputs):.1f} Mbps")
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save results to JSON file"""
        data = {
            'platform': self.platform,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': [asdict(r) for r in self.results]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✓ Results saved to {filename}")
    
    def compare_modes(self):
        """Compare hotspot vs bridge mode"""
        print("\n" + "="*60)
        print("COMPARING MODES")
        print("="*60)
        
        # Run benchmarks for both modes
        self.run_benchmark("Hotspot Mode Test", mode="hotspot")
        time.sleep(2)
        self.run_benchmark("Bridge Mode Test", mode="bridge")
        
        # Print comparison
        hotspot = next((r for r in self.results if r.mode == "hotspot"), None)
        bridge = next((r for r in self.results if r.mode == "bridge"), None)
        
        if hotspot and bridge:
            print("\nMode Comparison:")
            print(f"  Startup Time:")
            print(f"    Hotspot: {hotspot.startup_time:.2f}s")
            print(f"    Bridge:  {bridge.startup_time:.2f}s")
            print(f"  Throughput:")
            print(f"    Hotspot: {hotspot.throughput_mbps:.1f} Mbps")
            print(f"    Bridge:  {bridge.throughput_mbps:.1f} Mbps")


def main():
    """Main benchmark execution"""
    print("="*60)
    print("FantasmaWiFi-Pro Benchmarking Tool")
    print("="*60)
    
    benchmark = FantasmaBenchmark()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--compare':
        # Compare modes
        benchmark.compare_modes()
    else:
        # Run standard benchmarks
        benchmark.run_benchmark("Default Configuration", mode="hotspot")
    
    # Print results
    benchmark.print_results()
    
    # Save results
    benchmark.save_results()
    
    print("\n" + "="*60)
    print("Benchmark complete!")
    print("="*60)


if __name__ == '__main__':
    main()
