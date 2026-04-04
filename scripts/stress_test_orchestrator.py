#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-PERFECTION: Stress Test Orchestrator
Phase 1.2 - Comprehensive system stress testing

Tests system resilience, performance, security, and reliability under load.
"""

import os
import json
import asyncio
import time
import psutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import concurrent.futures
import sys

class StressTestOrchestrator:
    """Orchestrates comprehensive stress testing"""
    
    def __init__(self):
        self.data_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory/data")
        self.monitoring_dir = self.data_dir / "monitoring"
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_suites": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "system_metrics": {}
        }
    
    def capture_system_metrics(self) -> Dict:
        """Capture current system metrics"""
        try:
            metrics = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Network IO if available
            try:
                net_io = psutil.net_io_counters()
                metrics["network_sent_mb"] = net_io.bytes_sent / (1024 * 1024)
                metrics["network_recv_mb"] = net_io.bytes_recv / (1024 * 1024)
            except:
                pass
            
            return metrics
        except Exception as e:
            return {"error": str(e)}
    
    def test_script_load(self, script_path: Path, iterations: int = 10) -> Dict:
        """Load test a Python script"""
        test_result = {
            "test_name": f"Load Test: {script_path.name}",
            "script": str(script_path),
            "iterations": iterations,
            "status": "pending",
            "metrics": {
                "total_time": 0,
                "avg_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
                "success_count": 0,
                "failure_count": 0
            },
            "errors": []
        }
        
        start_time = time.time()
        execution_times = []
        
        print(f"  🔄 Running {iterations} iterations of {script_path.name}...")
        
        for i in range(iterations):
            iter_start = time.time()
            try:
                # Run script with timeout
                result = subprocess.run(
                    [sys.executable, str(script_path), "--help"],
                    capture_output=True,
                    timeout=10
                )
                iter_time = time.time() - iter_start
                execution_times.append(iter_time)
                
                if result.returncode == 0:
                    test_result["metrics"]["success_count"] += 1
                else:
                    test_result["metrics"]["failure_count"] += 1
                    if len(test_result["errors"]) < 3:  # Limit error storage
                        test_result["errors"].append(f"Iteration {i+1}: Exit code {result.returncode}")
            
            except subprocess.TimeoutExpired:
                test_result["metrics"]["failure_count"] += 1
                test_result["errors"].append(f"Iteration {i+1}: Timeout")
            except Exception as e:
                test_result["metrics"]["failure_count"] += 1
                test_result["errors"].append(f"Iteration {i+1}: {str(e)}")
        
        # Calculate metrics
        test_result["metrics"]["total_time"] = time.time() - start_time
        if execution_times:
            test_result["metrics"]["avg_time"] = sum(execution_times) / len(execution_times)
            test_result["metrics"]["min_time"] = min(execution_times)
            test_result["metrics"]["max_time"] = max(execution_times)
        
        # Determine status
        success_rate = test_result["metrics"]["success_count"] / iterations
        if success_rate >= 0.9:
            test_result["status"] = "passed"
        elif success_rate >= 0.7:
            test_result["status"] = "warning"
        else:
            test_result["status"] = "failed"
        
        return test_result
    
    def test_parallel_execution(self, scripts: List[Path], max_workers: int = 5) -> Dict:
        """Test parallel script execution"""
        test_result = {
            "test_name": "Parallel Execution Stress Test",
            "script_count": len(scripts),
            "max_workers": max_workers,
            "status": "pending",
            "metrics": {
                "total_time": 0,
                "scripts_completed": 0,
                "scripts_failed": 0
            },
            "errors": []
        }
        
        print(f"  ⚡ Testing parallel execution of {len(scripts)} scripts...")
        
        start_time = time.time()
        
        def run_script(script_path):
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path), "--help"],
                    capture_output=True,
                    timeout=15
                )
                return (script_path.name, result.returncode == 0)
            except Exception as e:
                return (script_path.name, False)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(run_script, script) for script in scripts[:20]]  # Limit to 20
            
            for future in concurrent.futures.as_completed(futures):
                script_name, success = future.result()
                if success:
                    test_result["metrics"]["scripts_completed"] += 1
                else:
                    test_result["metrics"]["scripts_failed"] += 1
                    test_result["errors"].append(f"Failed: {script_name}")
        
        test_result["metrics"]["total_time"] = time.time() - start_time
        
        # Determine status
        if test_result["metrics"]["scripts_failed"] == 0:
            test_result["status"] = "passed"
        elif test_result["metrics"]["scripts_failed"] < len(scripts) * 0.2:
            test_result["status"] = "warning"
        else:
            test_result["status"] = "failed"
        
        return test_result
    
    def test_memory_stress(self, target_mb: int = 100) -> Dict:
        """Test memory allocation and cleanup"""
        test_result = {
            "test_name": "Memory Stress Test",
            "target_mb": target_mb,
            "status": "pending",
            "metrics": {
                "initial_memory_mb": 0,
                "peak_memory_mb": 0,
                "final_memory_mb": 0,
                "memory_leaked_mb": 0
            },
            "errors": []
        }
        
        print(f"  🧠 Testing memory allocation ({target_mb}MB)...")
        
        try:
            import gc
            
            # Get initial memory
            gc.collect()
            initial_mem = psutil.Process().memory_info().rss / (1024 * 1024)
            test_result["metrics"]["initial_memory_mb"] = round(initial_mem, 2)
            
            # Allocate memory
            data = []
            chunk_size = 1024 * 1024  # 1MB chunks
            for i in range(target_mb):
                data.append(bytearray(chunk_size))
            
            # Measure peak
            peak_mem = psutil.Process().memory_info().rss / (1024 * 1024)
            test_result["metrics"]["peak_memory_mb"] = round(peak_mem, 2)
            
            # Cleanup
            data.clear()
            gc.collect()
            
            # Measure final
            final_mem = psutil.Process().memory_info().rss / (1024 * 1024)
            test_result["metrics"]["final_memory_mb"] = round(final_mem, 2)
            test_result["metrics"]["memory_leaked_mb"] = round(final_mem - initial_mem, 2)
            
            # Determine status
            if test_result["metrics"]["memory_leaked_mb"] < 10:
                test_result["status"] = "passed"
            elif test_result["metrics"]["memory_leaked_mb"] < 50:
                test_result["status"] = "warning"
            else:
                test_result["status"] = "failed"
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(str(e))
        
        return test_result
    
    def test_file_io_stress(self, file_count: int = 100) -> Dict:
        """Test file I/O operations"""
        test_result = {
            "test_name": "File I/O Stress Test",
            "file_count": file_count,
            "status": "pending",
            "metrics": {
                "write_time": 0,
                "read_time": 0,
                "delete_time": 0,
                "total_time": 0
            },
            "errors": []
        }
        
        print(f"  📁 Testing file I/O ({file_count} files)...")
        
        import tempfile
        
        temp_dir = Path(tempfile.mkdtemp(prefix="citadel_io_test_"))
        
        try:
            # Write test
            write_start = time.time()
            for i in range(file_count):
                test_file = temp_dir / f"test_{i}.txt"
                test_file.write_text(f"Test data {i}" * 100)
            test_result["metrics"]["write_time"] = round(time.time() - write_start, 3)
            
            # Read test
            read_start = time.time()
            for i in range(file_count):
                test_file = temp_dir / f"test_{i}.txt"
                _ = test_file.read_text()
            test_result["metrics"]["read_time"] = round(time.time() - read_start, 3)
            
            # Delete test
            delete_start = time.time()
            for i in range(file_count):
                test_file = temp_dir / f"test_{i}.txt"
                test_file.unlink()
            test_result["metrics"]["delete_time"] = round(time.time() - delete_start, 3)
            
            test_result["metrics"]["total_time"] = round(
                test_result["metrics"]["write_time"] +
                test_result["metrics"]["read_time"] +
                test_result["metrics"]["delete_time"], 3
            )
            
            test_result["status"] = "passed"
        
        except Exception as e:
            test_result["status"] = "failed"
            test_result["errors"].append(str(e))
        
        finally:
            # Cleanup temp directory
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
        
        return test_result
    
    def run_stress_tests(self) -> None:
        """Run all stress tests"""
        print("🏛️ CITADEL STRESS TEST ORCHESTRATOR")
        print("=" * 60)
        
        # Capture initial system metrics
        self.test_results["system_metrics"]["initial"] = self.capture_system_metrics()
        print(f"📊 Initial System State:")
        print(f"   CPU: {self.test_results['system_metrics']['initial']['cpu_percent']}%")
        print(f"   Memory: {self.test_results['system_metrics']['initial']['memory_percent']}%")
        print(f"   Disk: {self.test_results['system_metrics']['initial']['disk_percent']}%\n")
        
        # Test 1: Memory Stress
        print("🧪 Test Suite 1: Memory Stress")
        result = self.test_memory_stress(100)
        self.test_results["test_suites"].append(result)
        self._update_summary(result)
        print(f"   Status: {result['status'].upper()}")
        
        # Test 2: File I/O Stress
        print("\n🧪 Test Suite 2: File I/O Stress")
        result = self.test_file_io_stress(100)
        self.test_results["test_suites"].append(result)
        self._update_summary(result)
        print(f"   Status: {result['status'].upper()}")
        
        # Test 3: Script Load Testing
        scripts_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory/scripts")
        test_scripts = list(scripts_dir.glob("*.py"))[:5]  # Test first 5 scripts
        
        if test_scripts:
            print("\n🧪 Test Suite 3: Script Load Testing")
            for script in test_scripts:
                result = self.test_script_load(script, iterations=5)
                self.test_results["test_suites"].append(result)
                self._update_summary(result)
                print(f"   {script.name}: {result['status'].upper()}")
        
        # Test 4: Parallel Execution
        if test_scripts:
            print("\n🧪 Test Suite 4: Parallel Execution")
            result = self.test_parallel_execution(test_scripts, max_workers=3)
            self.test_results["test_suites"].append(result)
            self._update_summary(result)
            print(f"   Status: {result['status'].upper()}")
        
        # Capture final system metrics
        self.test_results["system_metrics"]["final"] = self.capture_system_metrics()
        
        # Save results
        results_file = self.monitoring_dir / "stress_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 STRESS TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.test_results['summary']['total_tests']}")
        print(f"✅ Passed: {self.test_results['summary']['passed']}")
        print(f"❌ Failed: {self.test_results['summary']['failed']}")
        print(f"⚠️  Warnings: {self.test_results['summary']['warnings']}")
        print(f"\n💾 Results saved: {results_file}")
    
    def _update_summary(self, result: Dict) -> None:
        """Update summary statistics"""
        self.test_results["summary"]["total_tests"] += 1
        
        if result["status"] == "passed":
            self.test_results["summary"]["passed"] += 1
        elif result["status"] == "failed":
            self.test_results["summary"]["failed"] += 1
        elif result["status"] == "warning":
            self.test_results["summary"]["warnings"] += 1

def main():
    """Main execution"""
    orchestrator = StressTestOrchestrator()
    orchestrator.run_stress_tests()

if __name__ == "__main__":
    main()
