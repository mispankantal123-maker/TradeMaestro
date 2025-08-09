#!/usr/bin/env python3
"""
MT5 Automated Trading Bot - Main Entry Point
A comprehensive automated trading bot for MetaTrader 5 with modular architecture.
"""

import sys
import os
import threading
import time
import signal
from typing import Optional

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


class TradingBot:
    """Main Trading Bot class that orchestrates all components."""
    
    def __init__(self):
        """Initialize the trading bot with all necessary components."""
        self.logger = BotLogger()
        self.connection = MT5Connection(self.logger)
        self.session_manager = SessionManager(self.logger)
        self.strategy_manager = StrategyManager(self.logger)
        self.account_manager = AccountManager(self.logger)
        self.gui: Optional[TradingBotGUI] = None
        
        self.running = False
        self.main_thread: Optional[threading.Thread] = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.log("🤖 Trading Bot initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.log(f"📶 Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def start(self) -> bool:
        """Start the trading bot."""
        try:
            self.logger.log("🚀 Starting Trading Bot...")
            
            # Initialize MT5 connection
            if not self.connection.connect():
                self.logger.log("❌ Failed to connect to MT5. Cannot start bot.")
                return False
            
            # Initialize account manager
            if not self.account_manager.initialize(self.connection.mt5):
                self.logger.log("❌ Failed to initialize account manager.")
                return False
            
            # Initialize session manager
            self.session_manager.initialize()
            
            # Initialize strategy manager
            self.strategy_manager.initialize(self.connection.mt5, self.account_manager)
            
            self.running = True
            
            # Start main trading loop in separate thread
            self.main_thread = threading.Thread(target=self._main_loop, daemon=True)
            self.main_thread.start()
            
            self.logger.log("✅ Trading Bot started successfully")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error starting bot: {str(e)}")
            return False
    
    def stop(self) -> None:
        """Stop the trading bot gracefully."""
        try:
            self.logger.log("🛑 Stopping Trading Bot...")
            self.running = False
            
            # Wait for main thread to finish
            if self.main_thread and self.main_thread.is_alive():
                self.main_thread.join(timeout=5.0)
            
            # Cleanup resources
            cleanup_resources()
            
            # Disconnect from MT5
            self.connection.disconnect()
            
            self.logger.log("✅ Trading Bot stopped successfully")
            
        except Exception as e:
            self.logger.log(f"❌ Error stopping bot: {str(e)}")
    
    def _main_loop(self) -> None:
        """Main trading loop that runs continuously."""
        try:
            while self.running:
                try:
                    # Check MT5 connection health
                    if not self.connection.check_connection():
                        self.logger.log("⚠️ MT5 connection lost, attempting to reconnect...")
                        if not self.connection.connect():
                            self.logger.log("❌ Failed to reconnect to MT5")
                            time.sleep(CONNECTION_RETRY_DELAY)
                            continue
                    
                    # Get current session
                    current_session = self.session_manager.get_current_session()
                    
                    # Execute trading strategy
                    self.strategy_manager.execute_strategy(current_session)
                    
                    # Update session data
                    self.session_manager.update_session_data()
                    
                    # Sleep based on current strategy interval
                    strategy_name = self.strategy_manager.get_current_strategy()
                    interval = BOT_LOOP_INTERVALS.get(strategy_name, 1.0)
                    time.sleep(interval)
                    
                except Exception as e:
                    self.logger.log(f"❌ Error in main loop: {str(e)}")
                    time.sleep(1.0)  # Short delay before retrying
                    
        except Exception as e:
            self.logger.log(f"❌ Fatal error in main loop: {str(e)}")
    
    def start_gui(self) -> None:
        """Start the GUI interface."""
        try:
            self.gui = TradingBotGUI(self, self.logger)
            self.gui.run()
        except Exception as e:
            self.logger.log(f"❌ Error starting GUI: {str(e)}")
    
    def emergency_stop(self) -> None:
        """Emergency stop - close all positions and stop bot."""
        try:
            self.logger.log("🚨 EMERGENCY STOP TRIGGERED!")
            
            # Close all open positions
            if hasattr(self.strategy_manager, 'close_all_positions'):
                self.strategy_manager.close_all_positions()
            
            # Stop the bot
            self.stop()
            
        except Exception as e:
            self.logger.log(f"❌ Error during emergency stop: {str(e)}")


def main():
    """Main entry point for the trading bot."""
    try:
        print("=" * 60)
        print("🤖 MT5 Automated Trading Bot")
        print("=" * 60)
        
        # Create bot instance
        bot = TradingBot()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--no-gui":
                # Run in headless mode
                bot.logger.log("🖥️ Running in headless mode (no GUI)")
                if bot.start():
                    try:
                        # Keep the main thread alive
                        while bot.running:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        bot.logger.log("📶 Keyboard interrupt received")
                    finally:
                        bot.stop()
                else:
                    bot.logger.log("❌ Failed to start bot")
                    sys.exit(1)
            else:
                print(f"Unknown argument: {sys.argv[1]}")
                print("Usage: python main.py [--no-gui]")
                sys.exit(1)
        else:
            # Run with GUI (default)
            bot.start_gui()
    
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
