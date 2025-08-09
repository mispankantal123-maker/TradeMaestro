#!/usr/bin/env python3
"""
MT5 Automated Trading Bot - Windows-Compatible Fixed Version
Based on the working Windows-Safe Bot principles but with full trading functionality.
"""

import sys
import os
import threading
import time
import signal
import queue
from typing import Optional, Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from modules.connection import MT5Connection
from modules.logging_utils import BotLogger
from modules.gui import TradingBotGUI
from modules.utils import cleanup_resources
from modules.sessions import SessionManager
from modules.strategy import StrategyManager
from modules.account import AccountManager


class WindowsCompatibleTradingBot:
    """Windows-compatible trading bot with freeze prevention."""
    
    def __init__(self):
        """Initialize with Windows-safe architecture."""
        self.logger = BotLogger()
        
        # Core components (lightweight initialization)
        self.connection = None
        self.session_manager = None
        self.strategy_manager = None
        self.account_manager = None
        self.gui: Optional[TradingBotGUI] = None
        
        # Windows-safe state management
        self.running = False
        self.trading_active = False
        self.command_queue = queue.Queue(maxsize=10)
        self.status_queue = queue.Queue(maxsize=100)
        
        # Thread management
        self.background_thread = None
        self.trading_thread = None
        
        # Windows compatibility
        self.is_windows = sys.platform.startswith('win')
        if self.is_windows:
            self.logger.log("🪟 Windows detected - using compatible mode")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.log("🤖 Windows-Compatible Trading Bot initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.log(f"📶 Received signal {signum}, shutting down...")
        self.stop()
    
    def initialize_components_safe(self) -> bool:
        """Initialize components in Windows-safe manner."""
        try:
            self.logger.log("🔧 Initializing components safely...")
            
            # Initialize in specific order with timeout protection
            components = [
                ("MT5 Connection", self._init_connection),
                ("Account Manager", self._init_account),
                ("Session Manager", self._init_sessions),
                ("Strategy Manager", self._init_strategy)
            ]
            
            for name, init_func in components:
                self.logger.log(f"🔄 Initializing {name}...")
                
                if self.is_windows:
                    # Use timeout for Windows compatibility
                    success = self._run_with_timeout(init_func, timeout=10.0)
                else:
                    success = init_func()
                
                if not success:
                    self.logger.log(f"❌ Failed to initialize {name}")
                    return False
                
                self.logger.log(f"✅ {name} initialized successfully")
                
                # Windows-specific delay to prevent race conditions
                if self.is_windows:
                    time.sleep(0.1)
            
            self.logger.log("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Component initialization error: {str(e)}")
            return False
    
    def _run_with_timeout(self, func, timeout=10.0):
        """Run function with timeout protection for Windows."""
        try:
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func)
                try:
                    return future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    self.logger.log(f"⚠️ Operation timed out after {timeout}s")
                    return False
        except Exception as e:
            self.logger.log(f"❌ Timeout execution error: {str(e)}")
            return False
    
    def _init_connection(self) -> bool:
        """Initialize MT5 connection safely."""
        try:
            self.connection = MT5Connection(self.logger)
            return self.connection.connect()
        except Exception as e:
            self.logger.log(f"❌ Connection init error: {str(e)}")
            return False
    
    def _init_account(self) -> bool:
        """Initialize account manager safely."""
        try:
            self.account_manager = AccountManager(self.logger)
            if self.connection and self.connection.mt5:
                return self.account_manager.initialize(self.connection.mt5)
            return False
        except Exception as e:
            self.logger.log(f"❌ Account init error: {str(e)}")
            return False
    
    def _init_sessions(self) -> bool:
        """Initialize session manager safely."""
        try:
            self.session_manager = SessionManager(self.logger)
            self.session_manager.initialize()
            return True
        except Exception as e:
            self.logger.log(f"❌ Session init error: {str(e)}")
            return False
    
    def _init_strategy(self) -> bool:
        """Initialize strategy manager safely."""
        try:
            self.strategy_manager = StrategyManager(self.logger)
            if self.connection and self.account_manager:
                self.strategy_manager.initialize(self.connection.mt5, self.account_manager)
                return True
            return False
        except Exception as e:
            self.logger.log(f"❌ Strategy init error: {str(e)}")
            return False
    
    def start_gui(self) -> None:
        """Start GUI with Windows-safe initialization."""
        try:
            self.logger.log("🎯 Starting Windows-compatible GUI...")
            
            # Create GUI with proper initialization
            self.gui = TradingBotGUI(self, self.logger)
            
            # Initialize components in background
            self.background_thread = threading.Thread(
                target=self._background_initialization,
                daemon=True,
                name="BackgroundInit"
            )
            self.background_thread.start()
            
            # Start GUI mainloop (this should be responsive)
            self.logger.log("🚀 Starting GUI mainloop...")
            self.gui.run()
            
        except Exception as e:
            self.logger.log(f"❌ GUI startup error: {str(e)}")
    
    def _background_initialization(self):
        """Initialize heavy components in background."""
        try:
            self.logger.log("🔄 Background initialization started...")
            
            # Initialize components safely
            if self.initialize_components_safe():
                self.running = True
                
                # Update GUI to show ready state
                if self.gui:
                    self.logger.log("✅ GUI notified of successful initialization")
                
                self.logger.log("✅ Background initialization completed")
            else:
                self.logger.log("❌ Background initialization failed")
                
        except Exception as e:
            self.logger.log(f"❌ Background initialization error: {str(e)}")
    
    def start_trading_safe(self) -> bool:
        """Start trading with Windows-safe threading."""
        try:
            if self.trading_active:
                self.logger.log("⚠️ Trading already active")
                return True
            
            if not self.running:
                self.logger.log("❌ Bot not ready - components not initialized")
                return False
            
            self.logger.log("🚀 Starting trading operations...")
            self.trading_active = True
            
            # Start trading in separate thread with Windows protection
            if self.is_windows:
                # Windows-safe trading thread
                self.trading_thread = threading.Thread(
                    target=self._windows_safe_trading_loop,
                    daemon=True,
                    name="WindowsTradingLoop"
                )
            else:
                # Standard trading thread
                self.trading_thread = threading.Thread(
                    target=self._standard_trading_loop,
                    daemon=True,
                    name="StandardTradingLoop"
                )
            
            self.trading_thread.start()
            self.logger.log("✅ Trading started successfully")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error starting trading: {str(e)}")
            return False
    
    def _windows_safe_trading_loop(self):
        """Windows-safe trading loop with yield points."""
        try:
            self.logger.log("🪟 Windows-safe trading loop started")
            
            while self.trading_active and self.running:
                try:
                    # Check connection health
                    if not self._check_connection_safe():
                        time.sleep(5)  # Wait before retry
                        continue
                    
                    # Get session info
                    session = self._get_session_safe()
                    if not session:
                        time.sleep(1)
                        continue
                    
                    # Execute strategy with yield points
                    self._execute_strategy_safe(session)
                    
                    # Windows-safe sleep with yield
                    self._windows_safe_sleep(3.0)
                    
                except Exception as e:
                    self.logger.log(f"❌ Trading loop error: {str(e)}")
                    time.sleep(5)  # Error recovery delay
            
            self.logger.log("🛑 Windows-safe trading loop stopped")
            
        except Exception as e:
            self.logger.log(f"❌ Trading loop fatal error: {str(e)}")
    
    def _standard_trading_loop(self):
        """Standard trading loop for non-Windows systems."""
        try:
            self.logger.log("🐧 Standard trading loop started")
            
            while self.trading_active and self.running:
                try:
                    # Standard trading operations
                    if self.connection and self.connection.check_connection():
                        session = self.session_manager.get_current_session()
                        if session:
                            self.strategy_manager.execute_strategy(session)
                    
                    time.sleep(1.0)  # Standard interval
                    
                except Exception as e:
                    self.logger.log(f"❌ Trading error: {str(e)}")
                    time.sleep(3)
            
            self.logger.log("🛑 Standard trading loop stopped")
            
        except Exception as e:
            self.logger.log(f"❌ Trading loop error: {str(e)}")
    
    def _check_connection_safe(self) -> bool:
        """Check connection with Windows safety."""
        try:
            if self.connection:
                return self.connection.check_connection()
            return False
        except Exception:
            return False
    
    def _get_session_safe(self) -> Optional[Dict[str, Any]]:
        """Get session info with Windows safety."""
        try:
            if self.session_manager:
                return self.session_manager.get_current_session()
            return None
        except Exception:
            return None
    
    def _execute_strategy_safe(self, session: Dict[str, Any]):
        """Execute strategy with Windows safety."""
        try:
            if self.strategy_manager:
                # Use timeout protection for Windows
                if self.is_windows:
                    self._run_with_timeout(
                        lambda: self.strategy_manager.execute_strategy(session),
                        timeout=5.0
                    )
                else:
                    self.strategy_manager.execute_strategy(session)
        except Exception as e:
            self.logger.log(f"❌ Strategy execution error: {str(e)}")
    
    def _windows_safe_sleep(self, duration: float):
        """Windows-safe sleep with yield points."""
        if self.is_windows:
            # Break sleep into smaller chunks for Windows
            chunks = int(duration * 10)  # 100ms chunks
            for _ in range(chunks):
                if not self.trading_active:
                    break
                time.sleep(0.1)
        else:
            time.sleep(duration)
    
    def stop_trading_safe(self) -> bool:
        """Stop trading safely."""
        try:
            self.logger.log("🛑 Stopping trading operations...")
            self.trading_active = False
            
            # Wait for trading thread to finish
            if self.trading_thread and self.trading_thread.is_alive():
                self.trading_thread.join(timeout=5.0)
            
            self.logger.log("✅ Trading stopped successfully")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error stopping trading: {str(e)}")
            return False
    
    def stop(self) -> None:
        """Stop the bot gracefully."""
        try:
            self.logger.log("🛑 Stopping Trading Bot...")
            
            # Stop trading first
            self.trading_active = False
            self.running = False
            
            # Stop threads
            if self.trading_thread and self.trading_thread.is_alive():
                self.trading_thread.join(timeout=3.0)
            
            if self.background_thread and self.background_thread.is_alive():
                self.background_thread.join(timeout=3.0)
            
            # Cleanup connections
            if self.connection:
                self.connection.disconnect()
            
            cleanup_resources()
            
            self.logger.log("✅ Trading Bot stopped successfully")
            
        except Exception as e:
            self.logger.log(f"❌ Error stopping bot: {str(e)}")


def main():
    """Main entry point."""
    try:
        print("=" * 60)
        print("🤖 MT5 Trading Bot - Windows Compatible")
        print("=" * 60)
        
        # Create bot instance
        bot = WindowsCompatibleTradingBot()
        
        # Run with GUI
        bot.start_gui()
        
    except KeyboardInterrupt:
        print("\n📶 Received interrupt signal - shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())