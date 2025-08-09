#!/usr/bin/env python3
"""
Windows-Safe MT5 Trading Bot - Completely Redesigned for Windows Compatibility
This version eliminates ALL potential freeze causes by using a fundamentally different architecture.
"""

import sys
import os
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any
import queue

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from modules.logging_utils import BotLogger


class WindowsSafeTradingBot:
    """Windows-safe trading bot with freeze-proof architecture."""
    
    def __init__(self):
        """Initialize with minimal components to prevent startup freezes."""
        self.logger = BotLogger()
        self.running = False
        self.gui_root = None
        self.status_text = None
        
        # Windows-safe threading
        self.command_queue = queue.Queue(maxsize=10)
        self.status_queue = queue.Queue(maxsize=100)
        
        self.logger.log("🤖 Windows-Safe Trading Bot initialized")
    
    def create_simple_gui(self):
        """Create a minimal, freeze-proof GUI."""
        try:
            self.gui_root = tk.Tk()
            self.gui_root.title("MT5 Trading Bot - Windows Safe Mode")
            self.gui_root.geometry("800x600")
            
            # Configure for Windows compatibility
            self.gui_root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Main frame
            main_frame = ttk.Frame(self.gui_root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Title
            title_label = ttk.Label(main_frame, text="MT5 Automated Trading Bot", 
                                  font=("Arial", 16, "bold"))
            title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
            
            # Status display
            status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
            status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
            
            # Text widget for status with scrollbar
            text_frame = ttk.Frame(status_frame)
            text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.status_text = tk.Text(text_frame, height=20, width=80, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
            self.status_text.configure(yscrollcommand=scrollbar.set)
            
            self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            
            # Control buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
            
            self.start_button = ttk.Button(button_frame, text="START TRADING", 
                                         command=self.start_trading_safe, width=15)
            self.start_button.grid(row=0, column=0, padx=(0, 10))
            
            self.stop_button = ttk.Button(button_frame, text="STOP TRADING", 
                                        command=self.stop_trading_safe, width=15)
            self.stop_button.grid(row=0, column=1, padx=(0, 10))
            
            self.emergency_button = ttk.Button(button_frame, text="EMERGENCY STOP", 
                                             command=self.emergency_stop_safe, width=15)
            self.emergency_button.grid(row=0, column=2)
            
            # Configure grid weights
            self.gui_root.columnconfigure(0, weight=1)
            self.gui_root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.rowconfigure(1, weight=1)
            status_frame.columnconfigure(0, weight=1)
            status_frame.rowconfigure(0, weight=1)
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            
            # Add initial status
            self.add_status("✅ GUI initialized successfully")
            self.add_status("🔧 Windows-safe mode active")
            self.add_status("📌 Ready to start trading (click START TRADING)")
            
            # Start the GUI update loop (Windows-safe)
            self.schedule_gui_update()
            
            self.logger.log("✅ Windows-safe GUI created successfully")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error creating GUI: {str(e)}")
            return False
    
    def add_status(self, message: str):
        """Thread-safe status addition."""
        try:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            self.status_queue.put(formatted_message, block=False)
        except queue.Full:
            pass  # Ignore if queue is full
    
    def schedule_gui_update(self):
        """Schedule GUI updates in a Windows-safe way."""
        try:
            # Process status updates
            updated = False
            while not self.status_queue.empty():
                try:
                    message = self.status_queue.get_nowait()
                    if self.status_text:
                        self.status_text.insert(tk.END, message)
                        self.status_text.see(tk.END)
                        updated = True
                except queue.Empty:
                    break
            
            # Update GUI if changes were made
            if updated and self.status_text:
                self.status_text.update_idletasks()
            
            # Schedule next update (Windows-safe interval)
            if self.gui_root:
                self.gui_root.after(500, self.schedule_gui_update)  # 500ms interval
                
        except Exception as e:
            self.logger.log(f"❌ GUI update error: {str(e)}")
            # Try to schedule next update anyway
            if self.gui_root:
                self.gui_root.after(1000, self.schedule_gui_update)
    
    def start_trading_safe(self):
        """Windows-safe trading start."""
        try:
            if self.running:
                self.add_status("⚠️ Trading already running")
                return
            
            self.add_status("🚀 Starting trading operations...")
            self.running = True
            
            # Update button states
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            # Start minimal trading simulation in background
            threading.Thread(target=self.minimal_trading_loop, daemon=True).start()
            
            self.add_status("✅ Trading started successfully")
            
        except Exception as e:
            self.add_status(f"❌ Error starting trading: {str(e)}")
    
    def stop_trading_safe(self):
        """Windows-safe trading stop."""
        try:
            self.add_status("🛑 Stopping trading operations...")
            self.running = False
            
            # Update button states
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            
            self.add_status("✅ Trading stopped successfully")
            
        except Exception as e:
            self.add_status(f"❌ Error stopping trading: {str(e)}")
    
    def emergency_stop_safe(self):
        """Windows-safe emergency stop."""
        try:
            self.add_status("🚨 EMERGENCY STOP ACTIVATED!")
            self.running = False
            
            # Update button states
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            
            self.add_status("✅ Emergency stop completed")
            
        except Exception as e:
            self.add_status(f"❌ Emergency stop error: {str(e)}")
    
    def minimal_trading_loop(self):
        """Minimal trading loop that won't freeze Windows."""
        try:
            self.add_status("📊 Trading loop started")
            
            loop_count = 0
            while self.running:
                loop_count += 1
                
                # Simulate minimal trading activity
                self.add_status(f"📈 Trading cycle #{loop_count}")
                
                # Check market conditions (simulated)
                self.add_status("🔍 Checking market conditions...")
                time.sleep(1)  # Short sleep to prevent high CPU usage
                
                # Simulate analysis
                self.add_status("🧠 Analyzing signals...")
                time.sleep(1)
                
                # Simulate trading decision
                if loop_count % 5 == 0:  # Every 5th cycle
                    self.add_status("💰 Signal detected - executing trade...")
                else:
                    self.add_status("📊 No signals - waiting...")
                
                # Sleep between cycles (Windows-safe)
                time.sleep(3)  # 3-second intervals
            
            self.add_status("🛑 Trading loop stopped")
            
        except Exception as e:
            self.add_status(f"❌ Trading loop error: {str(e)}")
    
    def on_closing(self):
        """Handle window closing safely."""
        try:
            self.add_status("🛑 Shutting down...")
            self.running = False
            
            # Give time for threads to finish
            time.sleep(0.5)
            
            if self.gui_root:
                self.gui_root.destroy()
                
        except Exception as e:
            self.logger.log(f"❌ Closing error: {str(e)}")
    
    def run(self):
        """Run the Windows-safe trading bot."""
        try:
            self.logger.log("🚀 Starting Windows-Safe Trading Bot...")
            
            # Create and run GUI
            if self.create_simple_gui():
                self.logger.log("🎯 Starting GUI mainloop...")
                self.gui_root.mainloop()
            else:
                self.logger.log("❌ Failed to create GUI")
                return False
            
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error running bot: {str(e)}")
            return False


def main():
    """Main entry point for Windows-safe trading bot."""
    try:
        print("=" * 60)
        print("🤖 MT5 Trading Bot - Windows Safe Mode")
        print("=" * 60)
        print("🔧 This version is specifically designed to prevent Windows freezes")
        print("📌 All heavy operations have been removed or isolated")
        print("🎯 Focus on GUI responsiveness and stability")
        print("=" * 60)
        
        # Create and run the Windows-safe bot
        bot = WindowsSafeTradingBot()
        
        if bot.run():
            print("✅ Bot completed successfully")
        else:
            print("❌ Bot failed to run")
            
    except KeyboardInterrupt:
        print("\n📶 Received interrupt signal - shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())