"""
TradeMaestro Core - Rebuilt Architecture
Producer-Consumer pattern with safe MT5 operations and timeout protection.
"""

import threading
import time
from collections import deque
from queue import Queue, Full, Empty
from typing import Optional, Any, Callable
import concurrent.futures


class TradeMaestroCore:
    """Core trading engine with rebuilt architecture for freeze prevention."""
    
    def __init__(self, logger, mt5_interface):
        self.logger = logger
        self.mt5 = mt5_interface
        
        # Configuration
        self.CANDLE_CACHE_SIZE = 1000
        self.FETCH_INTERVAL = 0.5  # seconds
        self.PROCESS_TIMEOUT = 2.0
        self.EXECUTE_TIMEOUT = 5.0
        self.QUEUE_MAXSIZE = 200
        
        # Shared resources
        self.stop_event = threading.Event()
        self.candle_cache = deque(maxlen=self.CANDLE_CACHE_SIZE)
        self.fetch_queue = Queue(maxsize=self.QUEUE_MAXSIZE)
        self.exec_queue = Queue(maxsize=self.QUEUE_MAXSIZE)
        
        # Worker threads
        self.threads = []
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="TradeMaestro")
        
        # Monitoring
        self.health_metrics = {
            'fetch_queue_size': 0,
            'exec_queue_size': 0,
            'cache_size': 0,
            'workers_active': 0,
            'last_fetch_time': 0,
            'last_process_time': 0,
            'last_execute_time': 0
        }
        
    def safe_mt5_call(self, func: Callable, *args, retries: int = 3, timeout: float = 2.0, backoff: float = 0.5) -> Optional[Any]:
        """Safe MT5 call with timeout and retries."""
        for i in range(retries):
            start = time.time()
            try:
                # Use thread pool for timeout protection
                future = self.thread_pool.submit(func, *args)
                result = future.result(timeout=timeout)
                return result
            except concurrent.futures.TimeoutError:
                self.logger.log(f"⚠️ MT5 call timeout: {func.__name__}")
                time.sleep(backoff * (i + 1))
            except Exception as e:
                self.logger.log(f"❌ MT5 call error: {func.__name__}: {str(e)}")
                time.sleep(backoff * (i + 1))
        
        return None
    
    def fetcher_loop(self):
        """Data fetcher worker - gets market data from MT5."""
        self.logger.log("🔄 Fetcher worker started")
        
        while not self.stop_event.is_set():
            try:
                # Fetch latest candle data with timeout protection
                data = self.safe_mt5_call(
                    getattr(self.mt5, 'copy_rates_from_pos', lambda *args: None),
                    "EURUSD", 0, 1000  # symbol, timeframe, start_pos, count
                )
                
                if data is not None and len(data) > 0:
                    # Update cache (thread-safe deque)
                    self.candle_cache.extend(data)
                    self.health_metrics['last_fetch_time'] = time.time()
                    
                    # Push to processing queue (non-blocking)
                    try:
                        self.fetch_queue.put_nowait({
                            'type': 'candle_data',
                            'data': data,
                            'timestamp': time.time()
                        })
                    except Full:
                        # Queue full, drop oldest data
                        try:
                            self.fetch_queue.get_nowait()  # Remove oldest
                            self.fetch_queue.put_nowait({
                                'type': 'candle_data',
                                'data': data,
                                'timestamp': time.time()
                            })
                        except Empty:
                            pass
                
                # Update metrics
                self.health_metrics['fetch_queue_size'] = self.fetch_queue.qsize()
                self.health_metrics['cache_size'] = len(self.candle_cache)
                
                # Prevent busy loop
                time.sleep(self.FETCH_INTERVAL)
                
            except Exception as e:
                self.logger.log(f"❌ Fetcher error: {str(e)}")
                time.sleep(1.0)  # Error recovery delay
        
        self.logger.log("🛑 Fetcher worker stopped")
    
    def processor_loop(self, worker_id: int):
        """Signal processor worker - calculates indicators and generates signals."""
        self.logger.log(f"🔄 Processor worker {worker_id} started")
        
        while not self.stop_event.is_set():
            try:
                # Get data from fetch queue with timeout
                try:
                    data_item = self.fetch_queue.get(timeout=1.0)
                except Empty:
                    continue
                
                # Process data with timeout protection
                start_time = time.time()
                
                if data_item['type'] == 'candle_data':
                    # Calculate indicators (mock implementation)
                    signal = self._calculate_trading_signal(data_item['data'])
                    
                    if signal:
                        # Push trading signal to execution queue
                        try:
                            self.exec_queue.put_nowait({
                                'type': 'trading_signal',
                                'signal': signal,
                                'timestamp': time.time(),
                                'worker_id': worker_id
                            })
                        except Full:
                            self.logger.log("⚠️ Execution queue full, dropping signal")
                
                # Mark task as done
                self.fetch_queue.task_done()
                
                # Update metrics
                self.health_metrics['last_process_time'] = time.time()
                process_time = time.time() - start_time
                
                # Log slow processing
                if process_time > self.PROCESS_TIMEOUT:
                    self.logger.log(f"⚠️ Slow processing: {process_time:.3f}s")
                
            except Exception as e:
                self.logger.log(f"❌ Processor {worker_id} error: {str(e)}")
                time.sleep(0.5)
        
        self.logger.log(f"🛑 Processor worker {worker_id} stopped")
    
    def executor_loop(self):
        """Order executor worker - sends orders to MT5."""
        self.logger.log("🔄 Executor worker started")
        
        while not self.stop_event.is_set():
            try:
                # Get order from execution queue with timeout
                try:
                    order_item = self.exec_queue.get(timeout=1.0)
                except Empty:
                    continue
                
                if order_item['type'] == 'trading_signal':
                    signal = order_item['signal']
                    
                    # Execute order with timeout protection
                    result = self.safe_mt5_call(
                        getattr(self.mt5, 'order_send', lambda x: {'retcode': 10009}),
                        signal,
                        retries=3,
                        timeout=self.EXECUTE_TIMEOUT
                    )
                    
                    if result:
                        self.logger.log(f"✅ Order executed: {signal['action']} {signal['symbol']}")
                    else:
                        self.logger.log(f"❌ Order failed: {signal['action']} {signal['symbol']}")
                    
                    # Update metrics
                    self.health_metrics['last_execute_time'] = time.time()
                
                # Mark task as done
                self.exec_queue.task_done()
                
            except Exception as e:
                self.logger.log(f"❌ Executor error: {str(e)}")
                time.sleep(0.5)
        
        self.logger.log("🛑 Executor worker stopped")
    
    def _calculate_trading_signal(self, candle_data) -> Optional[dict]:
        """Calculate trading signal from candle data (mock implementation)."""
        try:
            # Mock signal generation
            if len(candle_data) > 0:
                # Simple mock signal
                return {
                    'action': 'BUY',
                    'symbol': 'EURUSD',
                    'volume': 0.01,
                    'price': 1.0000,
                    'sl': 0.9950,
                    'tp': 1.0050
                }
            return None
        except Exception as e:
            self.logger.log(f"❌ Signal calculation error: {str(e)}")
            return None
    
    def monitor_loop(self):
        """Health monitoring worker."""
        self.logger.log("🔄 Monitor worker started")
        
        while not self.stop_event.is_set():
            try:
                # Update queue metrics
                self.health_metrics['fetch_queue_size'] = self.fetch_queue.qsize()
                self.health_metrics['exec_queue_size'] = self.exec_queue.qsize()
                self.health_metrics['cache_size'] = len(self.candle_cache)
                self.health_metrics['workers_active'] = len([t for t in self.threads if t.is_alive()])
                
                # Log health status every 30 seconds
                current_time = time.time()
                if int(current_time) % 30 == 0:
                    self.logger.log(f"📊 Health: Q:{self.health_metrics['fetch_queue_size']}/{self.health_metrics['exec_queue_size']} Cache:{self.health_metrics['cache_size']} Workers:{self.health_metrics['workers_active']}")
                
                # Check for stale workers
                if self.health_metrics['last_fetch_time'] > 0 and current_time - self.health_metrics['last_fetch_time'] > 60:
                    self.logger.log("⚠️ Fetcher appears stale")
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                self.logger.log(f"❌ Monitor error: {str(e)}")
                time.sleep(10)
        
        self.logger.log("🛑 Monitor worker stopped")
    
    def start(self):
        """Start all workers with rebuilt architecture."""
        try:
            self.logger.log("🚀 Starting TradeMaestro Core with rebuilt architecture...")
            
            # Create and start worker threads
            self.threads = [
                threading.Thread(target=self.fetcher_loop, daemon=True, name="Fetcher"),
                threading.Thread(target=self.processor_loop, args=(1,), daemon=True, name="Processor-1"),
                threading.Thread(target=self.processor_loop, args=(2,), daemon=True, name="Processor-2"),
                threading.Thread(target=self.executor_loop, daemon=True, name="Executor"),
                threading.Thread(target=self.monitor_loop, daemon=True, name="Monitor")
            ]
            
            # Start all threads
            for thread in self.threads:
                thread.start()
                self.logger.log(f"✅ Started {thread.name}")
            
            self.logger.log("✅ TradeMaestro Core started successfully")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Failed to start TradeMaestro Core: {str(e)}")
            return False
    
    def stop(self):
        """Stop all workers gracefully."""
        try:
            self.logger.log("🛑 Stopping TradeMaestro Core...")
            
            # Signal all workers to stop
            self.stop_event.set()
            
            # Wait for threads to finish with timeout
            for thread in self.threads:
                thread.join(timeout=5.0)
                if thread.is_alive():
                    self.logger.log(f"⚠️ {thread.name} did not stop gracefully")
                else:
                    self.logger.log(f"✅ {thread.name} stopped")
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True, timeout=5.0)
            
            self.logger.log("✅ TradeMaestro Core stopped successfully")
            
        except Exception as e:
            self.logger.log(f"❌ Error stopping TradeMaestro Core: {str(e)}")
    
    def get_health_metrics(self) -> dict:
        """Get current health metrics."""
        return self.health_metrics.copy()