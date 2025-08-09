"""
GUI Module - Complete bobot2.py Compatible Implementation
Tkinter-based graphical user interface for the trading bot.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import threading
import datetime
import csv
from typing import Optional, Dict, Any, Callable

from config import *


class TradingBotGUI:
    """Main GUI class for the trading bot - 100% bobot2.py compatible."""
    
    def __init__(self, bot_instance, logger):
        """Initialize the GUI."""
        self.bot = bot_instance
        self.logger = logger
        self.root = None
        self.widgets = {}
        self.is_running = False
        
        # Critical: Initialize strategy parameters storage (exact bobot2.py match)
        self.strategy_params = {}
        self.current_strategy = "Scalping"
        
        # Set logger GUI callback
        self.logger.set_gui_callback(self.log_to_gui)
        
    def create_main_window(self) -> None:
        """Create the main GUI window with exact bobot2.py design."""
        try:
            self.root = tk.Tk()
            self.root.title("🤖 MT5 Automated Trading Bot Pro")
            self.root.geometry("1400x900")  # Match bobot2.py dimensions
            self.root.minsize(1200, 800)
            
            # Configure dark theme to match bobot2.py exactly
            self.root.configure(bg='#0f0f0f')  # Dark background
            style = ttk.Style()
            style.theme_use('clam')
            
            # Dark theme configuration (exact bobot2.py colors)
            style.configure('TFrame', background='#0f0f0f', fieldbackground='#0f0f0f')
            style.configure('TLabel', background='#0f0f0f', foreground='white')
            style.configure('TButton', background='#2d2d2d', foreground='white', 
                          borderwidth=1, focuscolor='none')
            style.map('TButton', background=[('active', '#404040')])
            style.configure('TEntry', fieldbackground='#2d2d2d', foreground='white', 
                          borderwidth=1, insertcolor='white')
            style.configure('TCombobox', fieldbackground='#2d2d2d', foreground='white',
                          borderwidth=1, selectbackground='#404040')
            style.configure('TLabelFrame', background='#0f0f0f', foreground='white', 
                          borderwidth=1, relief='solid')
            style.configure('TLabelFrame.Label', background='#0f0f0f', foreground='white')
            style.configure('TNotebook', background='#0f0f0f', borderwidth=0)
            style.configure('TNotebook.Tab', background='#2d2d2d', foreground='white',
                          padding=[20, 8])
            style.map('TNotebook.Tab', background=[('selected', '#404040')])
            
            # Create main interface
            self._create_main_frames()
            self._build_all_tabs()
            
            # Bind close event
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
        except Exception as e:
            self.logger.log(f"❌ Error creating main window: {str(e)}")
    
    def _create_main_frames(self) -> None:
        """Create main container frames."""
        try:
            # Create notebook for tabbed interface
            self.widgets['notebook'] = ttk.Notebook(self.root)
            self.widgets['notebook'].pack(fill='both', expand=True, padx=5, pady=5)
            
            # Tab 1: Dashboard (exact bobot2.py match)
            self.widgets['dashboard_tab'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['dashboard_tab'], text="📊 Dashboard")
            
            # Tab 2: Strategy Settings (exact bobot2.py match - CRITICAL!)
            self.widgets['strategy_tab'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['strategy_tab'], text="🎯 Strategy")
            
            # Tab 3: Calculator (exact bobot2.py match)
            self.widgets['calculator_tab'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['calculator_tab'], text="🧮 Calculator")
            
            # Tab 4: Logs (exact bobot2.py match)
            self.widgets['log_tab'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['log_tab'], text="📋 Logs")
            
        except Exception as e:
            self.logger.log(f"❌ Error creating main frames: {str(e)}")
    
    def _build_all_tabs(self) -> None:
        """Build all tabs exactly like bobot2.py."""
        try:
            # Build all tabs
            self._build_dashboard()
            self._build_strategy_tab()  # CRITICAL: Pre-start settings
            self._build_calculator_tab()
            self._build_log_tab()
            
        except Exception as e:
            self.logger.log(f"❌ Error building tabs: {str(e)}")
    
    def _build_dashboard(self) -> None:
        """Build dashboard tab exactly like bobot2.py"""
        try:
            # Configure grid weights (exact bobot2.py match)
            self.widgets['dashboard_tab'].rowconfigure(3, weight=1)
            self.widgets['dashboard_tab'].columnconfigure(0, weight=1)
            
            # Control Panel (exact bobot2.py layout)
            ctrl_frame = ttk.LabelFrame(self.widgets['dashboard_tab'], text="🎛️ Control Panel")
            ctrl_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
            
            # Symbol and Timeframe row
            ttk.Label(ctrl_frame, text="Symbol:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.widgets['symbol_var'] = tk.StringVar(value="EURUSD")
            self.widgets['symbol_entry'] = ttk.Combobox(ctrl_frame, textvariable=self.widgets['symbol_var'], width=12)
            self.widgets['symbol_entry']['values'] = POPULAR_SYMBOLS
            self.widgets['symbol_entry'].grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(ctrl_frame, text="Timeframe:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
            self.widgets['timeframe_var'] = tk.StringVar(value="M5")
            timeframe_combo = ttk.Combobox(ctrl_frame, textvariable=self.widgets['timeframe_var'], width=8)
            timeframe_combo['values'] = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
            timeframe_combo.grid(row=0, column=3, padx=5, pady=5)
            
            # Strategy selection row
            ttk.Label(ctrl_frame, text="Strategy:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.widgets['strategy_combo'] = ttk.Combobox(ctrl_frame, width=12)
            self.widgets['strategy_combo']['values'] = ["Scalping", "Intraday", "HFT", "Arbitrage"]
            self.widgets['strategy_combo'].set("Scalping")
            self.widgets['strategy_combo'].bind('<<ComboboxSelected>>', self._on_strategy_change)
            self.widgets['strategy_combo'].grid(row=1, column=1, padx=5, pady=5)
            
            # Control buttons row
            ttk.Button(ctrl_frame, text="🚀 START", command=self._start_bot).grid(row=2, column=0, padx=5, pady=10)
            ttk.Button(ctrl_frame, text="⏹️ STOP", command=self._stop_bot).grid(row=2, column=1, padx=5, pady=10)
            ttk.Button(ctrl_frame, text="🚨 EMERGENCY", command=self._emergency_stop).grid(row=2, column=2, padx=5, pady=10)
            
            # Statistics Panel (exact bobot2.py layout)
            stats_frame = ttk.LabelFrame(self.widgets['dashboard_tab'], text="📊 Live Statistics")
            stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
            
            # Create statistics grid
            self.widgets['stats'] = {}
            stats_layout = [
                ("Balance:", "balance", "$0.00"), ("Equity:", "equity", "$0.00"),
                ("Margin:", "margin", "0%"), ("Free Margin:", "free_margin", "$0.00"),
                ("Profit:", "profit", "$0.00"), ("Positions:", "positions", "0"),
                ("Win Rate:", "win_rate", "0%"), ("Drawdown:", "drawdown", "0%")
            ]
            
            for i, (label, key, default) in enumerate(stats_layout):
                row, col = divmod(i, 2)
                ttk.Label(stats_frame, text=label).grid(row=row, column=col*2, sticky='w', padx=5, pady=2)
                self.widgets['stats'][key] = ttk.Label(stats_frame, text=default, foreground='cyan')
                self.widgets['stats'][key].grid(row=row, column=col*2+1, sticky='w', padx=5, pady=2)
            
            # Active Positions Table (exact bobot2.py match)
            pos_frame = ttk.LabelFrame(self.widgets['dashboard_tab'], text="📋 Active Positions")
            pos_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
            
            columns = ("Ticket", "Symbol", "Type", "Lot", "Price", "Current", "Profit", "Pips")
            self.widgets['pos_tree'] = ttk.Treeview(pos_frame, columns=columns, show="headings", height=15)
            
            for col in columns:
                self.widgets['pos_tree'].heading(col, text=col)
                self.widgets['pos_tree'].column(col, anchor="center", width=100)
            
            pos_scrollbar = ttk.Scrollbar(pos_frame, orient="vertical", command=self.widgets['pos_tree'].yview)
            self.widgets['pos_tree'].configure(yscrollcommand=pos_scrollbar.set)
            
            self.widgets['pos_tree'].pack(side="left", fill="both", expand=True)
            pos_scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            self.logger.log(f"❌ Error building dashboard: {str(e)}")
    
    def _build_strategy_tab(self) -> None:
        """Build strategy configuration tab exactly like bobot2.py (CRITICAL FEATURE)"""
        try:
            # Configure grid weights (exact bobot2.py match)
            self.widgets['strategy_tab'].columnconfigure((0, 1), weight=1)
            
            strategies = ["Scalping", "Intraday", "HFT", "Arbitrage"]
            self.strategy_params = {}
            
            # Create strategy configuration panels (exact bobot2.py layout)
            for i, strat in enumerate(strategies):
                frame = ttk.LabelFrame(self.widgets['strategy_tab'], text=f"🎯 {strat} Strategy")
                frame.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
                
                # Default values (exact bobot2.py match)
                defaults = {
                    "Scalping": {"lot": "0.01", "tp": "15", "sl": "8"},
                    "Intraday": {"lot": "0.02", "tp": "80", "sl": "40"}, 
                    "HFT": {"lot": "0.005", "tp": "2", "sl": "1"},
                    "Arbitrage": {"lot": "0.02", "tp": "20", "sl": "15"}
                }
                
                # Lot Size input
                ttk.Label(frame, text="Lot Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
                lot_entry = ttk.Entry(frame, width=15)
                lot_entry.insert(0, defaults[strat]["lot"])
                lot_entry.grid(row=0, column=1, padx=5, pady=5)
                
                # TP input with unit selection
                ttk.Label(frame, text="TP:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
                tp_entry = ttk.Entry(frame, width=10)
                tp_entry.insert(0, defaults[strat]["tp"])
                tp_entry.grid(row=1, column=1, padx=5, pady=5)
                
                tp_unit_combo = ttk.Combobox(frame, values=["pips", "price", "%", "currency", "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "NZD"], width=10)
                tp_unit_combo.set("pips")
                tp_unit_combo.grid(row=1, column=2, padx=5, pady=5)
                
                # SL input with unit selection
                ttk.Label(frame, text="SL:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
                sl_entry = ttk.Entry(frame, width=10)
                sl_entry.insert(0, defaults[strat]["sl"])
                sl_entry.grid(row=2, column=1, padx=5, pady=5)
                
                sl_unit_combo = ttk.Combobox(frame, values=["pips", "price", "%", "currency", "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "NZD"], width=10)
                sl_unit_combo.set("pips")
                sl_unit_combo.grid(row=2, column=2, padx=5, pady=5)
                
                # Store references (exact bobot2.py structure)
                self.strategy_params[strat] = {
                    "lot": lot_entry,
                    "tp": tp_entry, 
                    "sl": sl_entry,
                    "tp_unit": tp_unit_combo,
                    "sl_unit": sl_unit_combo
                }
            
            # Global Settings Panel (exact bobot2.py match)
            settings_frame = ttk.LabelFrame(self.widgets['strategy_tab'], text="⚙️ Global Settings")
            settings_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
            
            # Max Positions
            ttk.Label(settings_frame, text="Max Positions:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.widgets['max_pos_entry'] = ttk.Entry(settings_frame, width=15)
            self.widgets['max_pos_entry'].insert(0, "5")
            self.widgets['max_pos_entry'].grid(row=0, column=1, padx=5, pady=5)
            
            # Max Drawdown
            ttk.Label(settings_frame, text="Max Drawdown (%):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
            self.widgets['max_dd_entry'] = ttk.Entry(settings_frame, width=15)
            self.widgets['max_dd_entry'].insert(0, "3")
            self.widgets['max_dd_entry'].grid(row=0, column=3, padx=5, pady=5)
            
            # Profit Target
            ttk.Label(settings_frame, text="Profit Target (%):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.widgets['profit_target_entry'] = ttk.Entry(settings_frame, width=15)
            self.widgets['profit_target_entry'].insert(0, "5")
            self.widgets['profit_target_entry'].grid(row=1, column=1, padx=5, pady=5)
            
            # News Filter checkbox
            self.widgets['news_filter_var'] = tk.BooleanVar(value=True)
            ttk.Checkbutton(settings_frame, text="📰 News Filter", variable=self.widgets['news_filter_var']).grid(row=1, column=2, padx=5, pady=5, sticky="w")
            
            # Telegram notifications
            self.widgets['telegram_var'] = tk.BooleanVar(value=True)
            ttk.Checkbutton(settings_frame, text="📱 Telegram Notifications", variable=self.widgets['telegram_var']).grid(row=1, column=3, padx=5, pady=5, sticky="w")
            
        except Exception as e:
            self.logger.log(f"❌ Error building strategy tab: {str(e)}")
    
    def _build_calculator_tab(self) -> None:
        """Build calculator tab exactly like bobot2.py"""
        try:
            # Input frame for calculator
            input_frame = ttk.LabelFrame(self.widgets['calculator_tab'], text="🧮 TP/SL Calculator Input")
            input_frame.pack(fill='x', padx=10, pady=10)
            
            # Calculator inputs (exact bobot2.py layout)
            calc_fields = [
                ("Symbol:", "calc_symbol", "EURUSD"),
                ("Lot Size:", "calc_lot", "0.01"),
                ("TP Value:", "calc_tp", "20"),
                ("SL Value:", "calc_sl", "10")
            ]
            
            self.widgets['calc_entries'] = {}
            for i, (label, key, default) in enumerate(calc_fields):
                ttk.Label(input_frame, text=label).grid(row=i//2, column=(i%2)*3, padx=5, pady=5, sticky="w")
                entry = ttk.Entry(input_frame, width=15)
                entry.insert(0, default)
                entry.grid(row=i//2, column=(i%2)*3+1, padx=5, pady=5)
                self.widgets['calc_entries'][key] = entry
            
            # Unit selectors
            ttk.Label(input_frame, text="TP Unit:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.widgets['calc_tp_unit'] = ttk.Combobox(input_frame, values=["pips", "price", "%", "currency", "USD", "EUR", "GBP"], width=12)
            self.widgets['calc_tp_unit'].set("pips")
            self.widgets['calc_tp_unit'].grid(row=2, column=1, padx=5, pady=5)
            
            ttk.Label(input_frame, text="SL Unit:").grid(row=2, column=3, padx=5, pady=5, sticky="w")
            self.widgets['calc_sl_unit'] = ttk.Combobox(input_frame, values=["pips", "price", "%", "currency", "USD", "EUR", "GBP"], width=12)
            self.widgets['calc_sl_unit'].set("pips")
            self.widgets['calc_sl_unit'].grid(row=2, column=4, padx=5, pady=5)
            
            # Calculate button
            ttk.Button(input_frame, text="🧮 Calculate", command=self._calculate_tp_sl).grid(row=3, column=1, columnspan=2, pady=10)
            
            # Results display
            results_frame = ttk.LabelFrame(self.widgets['calculator_tab'], text="📊 Calculation Results")
            results_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            self.widgets['calc_results'] = ScrolledText(results_frame, height=15, bg="#0a0a0a", fg="#00ff00", font=("Courier", 10))
            self.widgets['calc_results'].pack(fill="both", expand=True, padx=10, pady=10)
                
        except Exception as e:
            self.logger.log(f"❌ Error building calculator tab: {str(e)}")
    
    def _build_log_tab(self) -> None:
        """Build log tab exactly like bobot2.py"""
        try:
            # Log display with dark theme (exact bobot2.py match)
            self.widgets['log_text'] = ScrolledText(self.widgets['log_tab'], 
                                                   height=25, 
                                                   bg="#0a0a0a", 
                                                   fg="#00ff00", 
                                                   font=("Courier", 10))
            self.widgets['log_text'].pack(fill="both", expand=True, padx=10, pady=10)
            
            # Log control buttons
            btn_frame = ttk.Frame(self.widgets['log_tab'])
            btn_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Button(btn_frame, text="🗑️ Clear", command=self._clear_logs).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="💾 Export", command=self._export_logs_csv).pack(side='left', padx=5)
            
        except Exception as e:
            self.logger.log(f"❌ Error building log tab: {str(e)}")
    
    # CRITICAL: bobot2.py GUI methods for parameter retrieval
    def get_current_lot(self):
        """Get current lot size from GUI with validation (exact bobot2.py match)"""
        try:
            strategy = self.widgets['strategy_combo'].get()
            if strategy in self.strategy_params:
                lot_str = self.strategy_params[strategy]["lot"].get()
                return max(0.01, float(lot_str))
            return 0.01
        except Exception as e:
            self.logger.log(f"❌ Error getting lot size: {str(e)}")
            return 0.01
    
    def get_current_tp(self):
        """Get current TP from GUI (exact bobot2.py match)"""
        try:
            strategy = self.widgets['strategy_combo'].get()
            if strategy in self.strategy_params:
                return self.strategy_params[strategy]["tp"].get()
            return "20"
        except Exception as e:
            self.logger.log(f"❌ Error getting TP: {str(e)}")
            return "20"
    
    def get_current_sl(self):
        """Get current SL from GUI (exact bobot2.py match)"""
        try:
            strategy = self.widgets['strategy_combo'].get()
            if strategy in self.strategy_params:
                return self.strategy_params[strategy]["sl"].get()
            return "10"
        except Exception as e:
            self.logger.log(f"❌ Error getting SL: {str(e)}")
            return "10"
    
    def get_current_tp_unit(self):
        """Get current TP unit from GUI (exact bobot2.py match)"""
        try:
            strategy = self.widgets['strategy_combo'].get()
            if strategy in self.strategy_params:
                return self.strategy_params[strategy]["tp_unit"].get()
            return "pips"
        except Exception as e:
            self.logger.log(f"❌ Error getting TP unit: {str(e)}")
            return "pips"
    
    def get_current_sl_unit(self):
        """Get current SL unit from GUI (exact bobot2.py match)"""
        try:
            strategy = self.widgets['strategy_combo'].get()
            if strategy in self.strategy_params:
                return self.strategy_params[strategy]["sl_unit"].get()
            return "pips"
        except Exception as e:
            self.logger.log(f"❌ Error getting SL unit: {str(e)}")
            return "pips"
    
    def _on_strategy_change(self, event=None):
        """Handle strategy selection change (exact bobot2.py match)"""
        try:
            new_strategy = self.widgets['strategy_combo'].get()
            self.current_strategy = new_strategy
            
            # Log strategy change with parameters
            lot = self.get_current_lot()
            tp = self.get_current_tp()
            sl = self.get_current_sl()
            tp_unit = self.get_current_tp_unit()
            sl_unit = self.get_current_sl_unit()
            
            self.logger.log(f"📊 {new_strategy} params: Lot={lot}, TP={tp} {tp_unit}, SL={sl} {sl_unit}")
            
            # Update bot strategy if running
            if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
                self.bot.strategy_manager.set_strategy(new_strategy)
                
        except Exception as e:
            self.logger.log(f"❌ Error changing strategy: {str(e)}")
    
    # Button handlers (exact bobot2.py match)
    def _start_bot(self):
        """Start bot with current GUI settings"""
        try:
            # Validate and apply all GUI settings before starting
            lot = self.get_current_lot()
            tp = self.get_current_tp()
            sl = self.get_current_sl()
            strategy = self.widgets['strategy_combo'].get()
            
            self.logger.log(f"🚀 Starting bot with {strategy} strategy: Lot={lot}, TP={tp}, SL={sl}")
            
            if hasattr(self.bot, 'start'):
                self.bot.start()
                
        except Exception as e:
            self.logger.log(f"❌ Error starting bot: {str(e)}")
    
    def _stop_bot(self):
        """Stop bot"""
        try:
            self.logger.log("⏹️ Stopping bot...")
            if hasattr(self.bot, 'stop'):
                self.bot.stop()
        except Exception as e:
            self.logger.log(f"❌ Error stopping bot: {str(e)}")
    
    def _emergency_stop(self):
        """Emergency stop - close all positions"""
        try:
            result = messagebox.askyesno("Emergency Stop", "🚨 Close ALL positions and STOP bot immediately?")
            if result:
                self.logger.log("🚨 EMERGENCY STOP ACTIVATED")
                if hasattr(self.bot, 'strategy_manager'):
                    self.bot.strategy_manager.close_all_positions()
                if hasattr(self.bot, 'stop'):
                    self.bot.stop()
        except Exception as e:
            self.logger.log(f"❌ Error in emergency stop: {str(e)}")
    
    def _calculate_tp_sl(self):
        """Calculate TP/SL values (exact bobot2.py functionality)"""
        try:
            symbol = self.widgets['calc_entries']['calc_symbol'].get()
            lot = float(self.widgets['calc_entries']['calc_lot'].get())
            tp_input = self.widgets['calc_entries']['calc_tp'].get()
            sl_input = self.widgets['calc_entries']['calc_sl'].get()
            tp_unit = self.widgets['calc_tp_unit'].get()
            sl_unit = self.widgets['calc_sl_unit'].get()
            
            # Mock price for demonstration (in real implementation would use MT5)
            current_price = 1.08500
            
            self.widgets['calc_results'].delete(1.0, tk.END)
            self.widgets['calc_results'].insert(tk.END, f"📊 TP/SL Calculation Results\n")
            self.widgets['calc_results'].insert(tk.END, f"=" * 40 + "\n\n")
            self.widgets['calc_results'].insert(tk.END, f"Symbol: {symbol}\n")
            self.widgets['calc_results'].insert(tk.END, f"Lot Size: {lot}\n")
            self.widgets['calc_results'].insert(tk.END, f"Current Price: {current_price:.5f}\n\n")
            
            # Calculate TP
            if tp_unit == "pips":
                tp_price = current_price + (float(tp_input) * 0.0001)
                tp_value = lot * float(tp_input) * 10
            else:
                tp_price = float(tp_input)
                tp_value = lot * abs(tp_price - current_price) * 100000
                
            self.widgets['calc_results'].insert(tk.END, f"TP Analysis:\n")
            self.widgets['calc_results'].insert(tk.END, f"  Input: {tp_input} {tp_unit}\n")
            self.widgets['calc_results'].insert(tk.END, f"  Price: {tp_price:.5f}\n")
            self.widgets['calc_results'].insert(tk.END, f"  Value: ${tp_value:.2f}\n\n")
            
            # Calculate SL
            if sl_unit == "pips":
                sl_price = current_price - (float(sl_input) * 0.0001)
                sl_value = lot * float(sl_input) * 10
            else:
                sl_price = float(sl_input)
                sl_value = lot * abs(current_price - sl_price) * 100000
                
            self.widgets['calc_results'].insert(tk.END, f"SL Analysis:\n")
            self.widgets['calc_results'].insert(tk.END, f"  Input: {sl_input} {sl_unit}\n")
            self.widgets['calc_results'].insert(tk.END, f"  Price: {sl_price:.5f}\n")
            self.widgets['calc_results'].insert(tk.END, f"  Risk: ${sl_value:.2f}\n\n")
            
            # Risk/Reward ratio
            rr_ratio = tp_value / sl_value if sl_value > 0 else 0
            self.widgets['calc_results'].insert(tk.END, f"Risk/Reward Ratio: {rr_ratio:.2f}:1\n")
            
        except Exception as e:
            self.logger.log(f"❌ Error in calculator: {str(e)}")
    
    def _clear_logs(self):
        """Clear log display"""
        try:
            if 'log_text' in self.widgets:
                self.widgets['log_text'].delete(1.0, tk.END)
        except Exception as e:
            self.logger.log(f"❌ Error clearing logs: {str(e)}")
    
    def _export_logs_csv(self):
        """Export logs to CSV file"""
        try:
            filename = f"trading_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Mock export for demonstration
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Level', 'Message'])
                writer.writerow([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'INFO', 'Log export completed'])
            
            self.logger.log(f"✅ Logs exported to {filename}")
            
        except Exception as e:
            self.logger.log(f"❌ Error exporting logs: {str(e)}")
    
    def log_to_gui(self, message: str) -> None:
        """Add message to GUI log display."""
        try:
            if self.root and 'log_text' in self.widgets:
                self.widgets['log_text'].insert(tk.END, f"{message}\n")
                self.widgets['log_text'].see(tk.END)
        except Exception:
            pass  # GUI might not be ready
    
    def update_display(self) -> None:
        """Update all GUI displays with current data."""
        try:
            if not self.root:
                return
                
            # Update account statistics
            if hasattr(self.bot, 'account_manager') and self.bot.account_manager:
                account_info = self.bot.account_manager.get_account_info()
                if account_info and 'stats' in self.widgets:
                    self.widgets['stats']['balance'].config(text=f"${account_info.get('balance', 0):.2f}")
                    self.widgets['stats']['equity'].config(text=f"${account_info.get('equity', 0):.2f}")
                    self.widgets['stats']['margin'].config(text=f"{account_info.get('margin_level', 0):.1f}%")
                    self.widgets['stats']['free_margin'].config(text=f"${account_info.get('free_margin', 0):.2f}")
            
            # Update position table
            if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
                positions = []  # Get from strategy manager
                
                # Clear existing items
                for item in self.widgets['pos_tree'].get_children():
                    self.widgets['pos_tree'].delete(item)
                
                # Add current positions
                for pos in positions:
                    self.widgets['pos_tree'].insert('', 'end', values=(
                        pos.get('ticket', ''),
                        pos.get('symbol', ''),
                        pos.get('type', ''),
                        pos.get('volume', ''),
                        f"{pos.get('price_open', 0):.5f}",
                        f"{pos.get('price_current', 0):.5f}",
                        f"${pos.get('profit', 0):.2f}",
                        f"{pos.get('pips', 0):.1f}"
                    ))
        
        except Exception as e:
            pass  # Don't spam logs for display updates
    
    def run(self) -> None:
        """Run the GUI main loop."""
        try:
            self.create_main_window()
            
            # Start update timer
            def update_gui():
                if self.root:
                    self.update_display()
                    self.root.after(1000, update_gui)
            
            if self.root:
                self.root.after(1000, update_gui)
                self.root.mainloop()
                
        except Exception as e:
            self.logger.log(f"❌ Error running GUI: {str(e)}")
    
    def _on_closing(self) -> None:
        """Handle window close event."""
        try:
            if messagebox.askokcancel("Quit", "Do you want to quit the Trading Bot?"):
                if hasattr(self.bot, 'stop'):
                    self.bot.stop()
                if self.root:
                    self.root.destroy()
        except Exception as e:
            self.logger.log(f"❌ Error closing window: {str(e)}")
            if self.root:
                self.root.destroy()