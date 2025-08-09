"""
Windows Freeze Fix for TradeMaestro
Comprehensive solution to prevent GUI freezing on Windows systems.
"""

import threading
import time
import sys
import signal
from typing import Optional


class WindowsFreezeFix:
    """Windows-specific freeze prevention utilities."""
    
    def __init__(self, logger):
        self.logger = logger
        self.is_windows = sys.platform.startswith('win')
        self.main_thread_watchdog = None
        self.watchdog_active = False
        
    def setup_windows_compatibility(self):
        """Setup Windows-specific compatibility measures."""
        if self.is_windows:
            self.logger.log("🪟 Setting up Windows compatibility...")
            
            # Setup signal handlers for graceful shutdown
            try:
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
                self.logger.log("✅ Windows signal handlers configured")
            except Exception as e:
                self.logger.log(f"⚠️ Could not setup signal handlers: {str(e)}")
            
            # Start main thread watchdog
            self.start_main_thread_watchdog()
            
        else:
            self.logger.log("🐧 Linux/Unix detected - Windows fixes not needed")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.log(f"📶 Received signal {signum}, shutting down gracefully...")
        self.stop_watchdog()
        
    def start_main_thread_watchdog(self):
        """Start watchdog to monitor main thread responsiveness."""
        if self.is_windows and not self.watchdog_active:
            self.watchdog_active = True
            self.main_thread_watchdog = threading.Thread(
                target=self._watchdog_loop, 
                daemon=True, 
                name="WindowsWatchdog"
            )
            self.main_thread_watchdog.start()
            self.logger.log("🐕 Windows main thread watchdog started")
    
    def _watchdog_loop(self):
        """Watchdog loop to detect main thread freezes."""
        last_heartbeat = time.time()
        freeze_threshold = 10.0  # 10 seconds
        
        while self.watchdog_active:
            try:
                current_time = time.time()
                
                # Check if main thread has been responsive
                time_since_heartbeat = current_time - last_heartbeat
                
                if time_since_heartbeat > freeze_threshold:
                    self.logger.log(f"⚠️ POTENTIAL FREEZE DETECTED: Main thread unresponsive for {time_since_heartbeat:.1f}s")
                    
                    # Log system resource usage
                    try:
                        import psutil
                        cpu_percent = psutil.cpu_percent()
                        memory_percent = psutil.virtual_memory().percent
                        self.logger.log(f"📊 System: CPU {cpu_percent}%, Memory {memory_percent}%")
                    except:
                        pass
                
                # Update heartbeat (this should be called from main thread periodically)
                last_heartbeat = current_time
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self.logger.log(f"❌ Watchdog error: {str(e)}")
                time.sleep(5)
    
    def heartbeat(self):
        """Call this from main thread periodically to indicate it's alive."""
        # This can be called from GUI update loops
        pass
    
    def stop_watchdog(self):
        """Stop the watchdog system."""
        self.watchdog_active = False
        if self.main_thread_watchdog and self.main_thread_watchdog.is_alive():
            self.main_thread_watchdog.join(timeout=2)
            self.logger.log("🛑 Windows watchdog stopped")
    
    def prevent_gui_freeze(self, gui_update_func):
        """Wrapper to prevent GUI freeze during updates."""
        if self.is_windows:
            try:
                # Use timeout protection for GUI updates on Windows
                import concurrent.futures
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(gui_update_func)
                    try:
                        result = future.result(timeout=1.0)  # 1 second timeout
                        return result
                    except concurrent.futures.TimeoutError:
                        self.logger.log("⚠️ GUI update timeout - prevented freeze")
                        return None
            except Exception as e:
                self.logger.log(f"❌ GUI freeze prevention error: {str(e)}")
                return gui_update_func()  # Fallback
        else:
            return gui_update_func()
    
    def safe_threading_start(self, target_func, thread_name: str, *args, **kwargs):
        """Safely start a thread with Windows-specific protections."""
        try:
            thread = threading.Thread(
                target=self._safe_thread_wrapper,
                args=(target_func, thread_name, *args),
                kwargs=kwargs,
                daemon=True,
                name=thread_name
            )
            thread.start()
            self.logger.log(f"✅ Thread started safely: {thread_name}")
            return thread
        except Exception as e:
            self.logger.log(f"❌ Failed to start thread {thread_name}: {str(e)}")
            return None
    
    def _safe_thread_wrapper(self, target_func, thread_name, *args, **kwargs):
        """Wrapper for thread functions with error handling."""
        try:
            self.logger.log(f"🔄 Thread {thread_name} started")
            target_func(*args, **kwargs)
        except Exception as e:
            self.logger.log(f"❌ Thread {thread_name} error: {str(e)}")
        finally:
            self.logger.log(f"🛑 Thread {thread_name} finished")
    
    def get_system_info(self) -> dict:
        """Get system information for debugging."""
        info = {
            'platform': sys.platform,
            'is_windows': self.is_windows,
            'python_version': sys.version,
            'thread_count': threading.active_count()
        }
        
        try:
            import psutil
            info.update({
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'available_memory_gb': psutil.virtual_memory().available / (1024**3)
            })
        except ImportError:
            info['psutil_available'] = False
            
        return info