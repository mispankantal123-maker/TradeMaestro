"""
Freeze Prevention Module
Provides utilities to prevent GUI and system freezes on Windows.
"""

import time
import threading
import psutil
import os
from typing import Callable, Any


class FreezePreventionManager:
    """Manages freeze prevention mechanisms."""
    
    def __init__(self, logger):
        self.logger = logger
        self.monitoring_active = False
        self.performance_data = {
            'cpu_usage': [],
            'memory_usage': [],
            'thread_count': [],
            'gui_response_times': []
        }
        
    def start_monitoring(self):
        """Start performance monitoring to detect potential freezes."""
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._performance_monitor, daemon=True)
        monitor_thread.start()
        self.logger.log("✅ Freeze prevention monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        self.logger.log("🛑 Freeze prevention monitoring stopped")
    
    def _performance_monitor(self):
        """Monitor system performance for freeze indicators."""
        while self.monitoring_active:
            try:
                # Monitor CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.performance_data['cpu_usage'].append(cpu_percent)
                
                # Monitor memory usage
                memory = psutil.virtual_memory()
                self.performance_data['memory_usage'].append(memory.percent)
                
                # Monitor thread count
                process = psutil.Process(os.getpid())
                thread_count = process.num_threads()
                self.performance_data['thread_count'].append(thread_count)
                
                # Keep only last 60 data points (1 minute)
                for key in self.performance_data:
                    if len(self.performance_data[key]) > 60:
                        self.performance_data[key] = self.performance_data[key][-60:]
                
                # Check for freeze indicators
                self._check_freeze_indicators()
                
                time.sleep(1)  # Monitor every second
                
            except Exception as e:
                self.logger.log(f"❌ Performance monitor error: {str(e)}")
                time.sleep(5)
    
    def _check_freeze_indicators(self):
        """Check for potential freeze indicators."""
        try:
            # Check CPU usage spike
            if len(self.performance_data['cpu_usage']) >= 10:
                recent_cpu = self.performance_data['cpu_usage'][-10:]
                avg_cpu = sum(recent_cpu) / len(recent_cpu)
                
                if avg_cpu > 90:
                    self.logger.log(f"⚠️ High CPU usage detected: {avg_cpu:.1f}%")
            
            # Check memory usage
            if len(self.performance_data['memory_usage']) >= 10:
                recent_memory = self.performance_data['memory_usage'][-10:]
                avg_memory = sum(recent_memory) / len(recent_memory)
                
                if avg_memory > 85:
                    self.logger.log(f"⚠️ High memory usage detected: {avg_memory:.1f}%")
            
            # Check thread count growth
            if len(self.performance_data['thread_count']) >= 30:
                recent_threads = self.performance_data['thread_count'][-30:]
                thread_growth = recent_threads[-1] - recent_threads[0]
                
                if thread_growth > 10:
                    self.logger.log(f"⚠️ Thread count growing: +{thread_growth} threads")
                    
        except Exception as e:
            pass  # Silent fail for monitoring
    
    def execute_with_timeout(self, func: Callable, timeout: float, *args, **kwargs) -> Any:
        """Execute function with timeout to prevent hanging."""
        import concurrent.futures
        
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(func, *args, **kwargs)
                result = future.result(timeout=timeout)
                return result
                
        except concurrent.futures.TimeoutError:
            self.logger.log(f"⚠️ Function timeout after {timeout}s: {func.__name__}")
            return None
        except Exception as e:
            self.logger.log(f"❌ Function error: {func.__name__}: {str(e)}")
            return None
    
    def get_performance_report(self) -> dict:
        """Get current performance report."""
        try:
            current_cpu = psutil.cpu_percent()
            current_memory = psutil.virtual_memory().percent
            process = psutil.Process(os.getpid())
            current_threads = process.num_threads()
            
            return {
                'cpu_usage': current_cpu,
                'memory_usage': current_memory,
                'thread_count': current_threads,
                'status': 'HEALTHY' if current_cpu < 80 and current_memory < 80 else 'WARNING'
            }
            
        except Exception as e:
            return {'error': str(e)}