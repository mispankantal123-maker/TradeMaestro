"""
Performance Monitoring Module
Real-time performance tracking and optimization for live trading
"""

import time
import threading
import psutil
import os
from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class PerformanceMonitor:
    """Monitors bot performance metrics for live trading optimization."""
    
    def __init__(self, logger):
        """Initialize performance monitor."""
        self.logger = logger
        self.start_time = time.time()
        self.process = psutil.Process(os.getpid())
        
        # Performance metrics storage
        self.execution_times = deque(maxlen=1000)  # Last 1000 executions
        self.memory_usage = deque(maxlen=100)      # Last 100 memory checks
        self.cpu_usage = deque(maxlen=100)         # Last 100 CPU checks
        
        # Signal performance tracking
        self.signal_latencies = defaultdict(lambda: deque(maxlen=100))
        self.execution_latencies = deque(maxlen=100)
        self.strategy_performance = defaultdict(lambda: {
            'signals': 0, 'executed': 0, 'winrate': 0.0, 'avg_latency': 0.0
        })
        
        # Error tracking
        self.error_counts = defaultdict(int)
        self.error_history = deque(maxlen=50)
        
        # Monitoring flags
        self.monitoring_active = True
        self.last_memory_check = time.time()
        self.baseline_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Performance thresholds
        self.LATENCY_THRESHOLD_HFT = 0.150  # 150ms for HFT
        self.LATENCY_THRESHOLD_NORMAL = 0.500  # 500ms for other strategies
        self.MEMORY_GROWTH_THRESHOLD = 0.10  # 10% growth limit
        self.CPU_THRESHOLD = 80.0  # 80% CPU usage limit
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.log("✅ Performance Monitor initialized")
    
    def record_signal_detection(self, strategy: str, timestamp: float = None) -> str:
        """Record signal detection time and return unique ID."""
        if timestamp is None:
            timestamp = time.time()
        
        signal_id = f"{strategy}_{int(timestamp * 1000)}"
        self.signal_start_times = getattr(self, 'signal_start_times', {})
        self.signal_start_times[signal_id] = timestamp
        
        return signal_id
    
    def record_signal_completion(self, signal_id: str, strategy: str, executed: bool = False):
        """Record signal processing completion."""
        if not hasattr(self, 'signal_start_times') or signal_id not in self.signal_start_times:
            return
        
        start_time = self.signal_start_times[signal_id]
        completion_time = time.time()
        latency = completion_time - start_time
        
        # Record latency
        self.signal_latencies[strategy].append(latency)
        self.execution_times.append(latency)
        
        # Update strategy performance
        self.strategy_performance[strategy]['signals'] += 1
        if executed:
            self.strategy_performance[strategy]['executed'] += 1
        
        # Calculate average latency
        if self.signal_latencies[strategy]:
            self.strategy_performance[strategy]['avg_latency'] = sum(self.signal_latencies[strategy]) / len(self.signal_latencies[strategy])
        
        # Check latency threshold
        threshold = self.LATENCY_THRESHOLD_HFT if strategy == "HFT" else self.LATENCY_THRESHOLD_NORMAL
        if latency > threshold:
            self.logger.log(f"⚠️ High latency detected: {strategy} {latency*1000:.1f}ms (threshold: {threshold*1000:.1f}ms)")
        
        # Cleanup
        del self.signal_start_times[signal_id]
    
    def record_execution_time(self, operation: str, duration: float):
        """Record execution time for specific operation."""
        self.execution_times.append(duration)
        
        # Log slow operations
        if duration > 0.1:  # 100ms
            self.logger.log(f"⚠️ Slow operation: {operation} took {duration*1000:.1f}ms")
    
    def record_error(self, error_type: str, error_message: str):
        """Record error occurrence."""
        self.error_counts[error_type] += 1
        self.error_history.append({
            'timestamp': datetime.now(),
            'type': error_type,
            'message': error_message
        })
        
        # Alert on repeated errors
        if self.error_counts[error_type] >= 5:
            self.logger.log(f"🚨 Repeated error: {error_type} occurred {self.error_counts[error_type]} times")
    
    def check_memory_usage(self) -> Tuple[float, float]:
        """Check current memory usage and growth."""
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        growth_percentage = ((current_memory - self.baseline_memory) / self.baseline_memory) * 100
        
        self.memory_usage.append(current_memory)
        
        # Alert on excessive memory growth
        if growth_percentage > self.MEMORY_GROWTH_THRESHOLD * 100:
            self.logger.log(f"🚨 High memory usage: {current_memory:.1f}MB (+{growth_percentage:.1f}%)")
        
        return current_memory, growth_percentage
    
    def check_cpu_usage(self) -> float:
        """Check current CPU usage."""
        cpu_percent = self.process.cpu_percent(interval=None)
        self.cpu_usage.append(cpu_percent)
        
        # Alert on high CPU usage
        if cpu_percent > self.CPU_THRESHOLD:
            self.logger.log(f"🚨 High CPU usage: {cpu_percent:.1f}%")
        
        return cpu_percent
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary."""
        current_memory, memory_growth = self.check_memory_usage()
        cpu_percent = self.check_cpu_usage()
        uptime = time.time() - self.start_time
        
        # Calculate averages
        avg_execution_time = sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
        avg_memory = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else current_memory
        avg_cpu = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else cpu_percent
        
        # Strategy performance
        strategy_stats = {}
        for strategy, stats in self.strategy_performance.items():
            winrate = (stats['executed'] / stats['signals'] * 100) if stats['signals'] > 0 else 0
            strategy_stats[strategy] = {
                'signals': stats['signals'],
                'executed': stats['executed'],
                'winrate': f"{winrate:.1f}%",
                'avg_latency': f"{stats['avg_latency']*1000:.1f}ms"
            }
        
        return {
            'uptime': f"{uptime/3600:.1f} hours",
            'memory': {
                'current': f"{current_memory:.1f}MB",
                'growth': f"{memory_growth:.1f}%",
                'average': f"{avg_memory:.1f}MB"
            },
            'cpu': {
                'current': f"{cpu_percent:.1f}%",
                'average': f"{avg_cpu:.1f}%"
            },
            'execution': {
                'avg_time': f"{avg_execution_time*1000:.1f}ms",
                'total_operations': len(self.execution_times)
            },
            'strategies': strategy_stats,
            'errors': dict(self.error_counts),
            'health_status': self._get_health_status()
        }
    
    def _get_health_status(self) -> str:
        """Determine overall health status."""
        current_memory, memory_growth = self.check_memory_usage()
        cpu_percent = self.check_cpu_usage()
        
        # Check for critical issues
        if memory_growth > self.MEMORY_GROWTH_THRESHOLD * 100:
            return "CRITICAL - High Memory Usage"
        
        if cpu_percent > self.CPU_THRESHOLD:
            return "WARNING - High CPU Usage"
        
        # Check error rates
        recent_errors = len([e for e in self.error_history if e['timestamp'] > datetime.now() - timedelta(minutes=10)])
        if recent_errors > 10:
            return "WARNING - High Error Rate"
        
        # Check latency
        if self.execution_times:
            avg_latency = sum(self.execution_times) / len(self.execution_times)
            if avg_latency > self.LATENCY_THRESHOLD_NORMAL:
                return "WARNING - High Latency"
        
        return "HEALTHY"
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Check memory every 30 seconds
                if time.time() - self.last_memory_check > 30:
                    self.check_memory_usage()
                    self.check_cpu_usage()
                    self.last_memory_check = time.time()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.log(f"❌ Monitor loop error: {str(e)}")
                time.sleep(10)
    
    def stop_monitoring(self):
        """Stop monitoring thread."""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
    
    def export_metrics(self, filepath: str) -> bool:
        """Export performance metrics to file."""
        try:
            metrics = self.get_performance_summary()
            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            self.logger.log(f"✅ Metrics exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Failed to export metrics: {str(e)}")
            return False


class LatencyOptimizer:
    """Optimizes execution latency for live trading."""
    
    def __init__(self, logger):
        """Initialize latency optimizer."""
        self.logger = logger
        self.symbol_cache = {}
        self.price_cache = {}
        self.cache_timestamps = {}
        self.CACHE_TIMEOUT = 1.0  # 1 second cache timeout
        
        self.logger.log("✅ Latency Optimizer initialized")
    
    def get_cached_symbol_info(self, symbol: str, symbol_manager) -> Optional[Dict]:
        """Get symbol info with caching."""
        current_time = time.time()
        
        # Check cache
        if (symbol in self.symbol_cache and 
            symbol in self.cache_timestamps and 
            current_time - self.cache_timestamps[symbol] < self.CACHE_TIMEOUT):
            return self.symbol_cache[symbol]
        
        # Fetch fresh data
        start_time = time.time()
        symbol_info = symbol_manager.get_symbol_info(symbol)
        fetch_time = time.time() - start_time
        
        if symbol_info:
            self.symbol_cache[symbol] = symbol_info
            self.cache_timestamps[symbol] = current_time
            
            if fetch_time > 0.050:  # 50ms
                self.logger.log(f"⚠️ Slow symbol info fetch: {symbol} took {fetch_time*1000:.1f}ms")
        
        return symbol_info
    
    def get_cached_price(self, symbol: str, mt5_instance) -> Optional[float]:
        """Get current price with caching."""
        current_time = time.time()
        cache_key = f"{symbol}_price"
        
        # Check cache (shorter timeout for prices)
        if (cache_key in self.price_cache and 
            cache_key in self.cache_timestamps and 
            current_time - self.cache_timestamps[cache_key] < 0.5):  # 500ms timeout
            return self.price_cache[cache_key]
        
        # Fetch fresh price
        start_time = time.time()
        try:
            tick = mt5_instance.symbol_info_tick(symbol)
            if tick:
                price = (tick.bid + tick.ask) / 2
                self.price_cache[cache_key] = price
                self.cache_timestamps[cache_key] = current_time
                
                fetch_time = time.time() - start_time
                if fetch_time > 0.020:  # 20ms
                    self.logger.log(f"⚠️ Slow price fetch: {symbol} took {fetch_time*1000:.1f}ms")
                
                return price
        except Exception as e:
            self.logger.log(f"❌ Price fetch error: {symbol} - {str(e)}")
        
        return None
    
    def prefetch_symbol_data(self, symbols: List[str], symbol_manager, mt5_instance):
        """Prefetch symbol data for multiple symbols."""
        start_time = time.time()
        
        for symbol in symbols:
            self.get_cached_symbol_info(symbol, symbol_manager)
            self.get_cached_price(symbol, mt5_instance)
        
        total_time = time.time() - start_time
        self.logger.log(f"✅ Prefetched data for {len(symbols)} symbols in {total_time*1000:.1f}ms")
    
    def clear_cache(self):
        """Clear all cached data."""
        self.symbol_cache.clear()
        self.price_cache.clear()
        self.cache_timestamps.clear()
        self.logger.log("✅ Cache cleared")