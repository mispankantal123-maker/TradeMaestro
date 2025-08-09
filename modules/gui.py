"""
GUI Module
Tkinter-based graphical user interface for the trading bot.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import threading
import datetime
from typing import Optional, Dict, Any, Callable

from config import *


class TradingBotGUI:
    """Main GUI class for the trading bot."""
    
    def __init__(self, bot_instance, logger):
        """Initialize the GUI."""
        self.bot = bot_instance
        self.logger = logger
        self.root = None
        self.widgets = {}
        self.is_running = False
        
        # Set logger GUI callback
        self.logger.set_gui_callback(self.log_to_gui)
        
    def create_main_window(self) -> None:
        """Create the main GUI window."""
        try:
            self.root = tk.Tk()
            self.root.title("MT5 Automated Trading Bot")
            self.root.geometry("1200x800")
            self.root.minsize(800, 600)
            
            # Configure style
            style = ttk.Style()
            style.theme_use('clam')
            
            # Create main frames
            self._create_menu_bar()
            self._create_main_frames()
            self._create_connection_frame()
            self._create_control_frame()
            self._create_strategy_frame()
            self._create_risk_frame()
            self._create_live_stats_frame()
            self._create_symbol_frame()
            self._create_calculator_frame()
            self._create_log_frame()
            self._create_status_frame()
            
            # Bind close event
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # Start update timer
            self._schedule_updates()
            
        except Exception as e:
            self.logger.log(f"❌ Error creating main window: {str(e)}")
    
    def _create_menu_bar(self) -> None:
        """Create menu bar."""
        try:
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)
            
            # File menu
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Export Logs (CSV)", command=self._export_logs_csv)
            file_menu.add_command(label="Export Logs (TXT)", command=self._export_logs_txt)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self._on_closing)
            
            # Tools menu
            tools_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Tools", menu=tools_menu)
            tools_menu.add_command(label="TP/SL Calculator", command=self._show_calculator)
            tools_menu.add_command(label="Performance Report", command=self._show_performance_report)
            tools_menu.add_command(label="Test Telegram", command=self._test_telegram)
            
            # Help menu
            help_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Help", menu=help_menu)
            help_menu.add_command(label="About", command=self._show_about)
            
        except Exception as e:
            self.logger.log(f"❌ Error creating menu bar: {str(e)}")
    
    def _create_main_frames(self) -> None:
        """Create main layout frames."""
        try:
            # Create notebook for tabbed interface
            self.widgets['notebook'] = ttk.Notebook(self.root)
            self.widgets['notebook'].pack(fill='both', expand=True, padx=5, pady=5)
            
            # Main control tab
            self.widgets['main_frame'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['main_frame'], text="Main Control")
            
            # Monitoring tab
            self.widgets['monitor_frame'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['monitor_frame'], text="Monitoring")
            
            # Settings tab
            self.widgets['settings_frame'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['settings_frame'], text="Settings")
            
        except Exception as e:
            self.logger.log(f"❌ Error creating main frames: {str(e)}")
    
    def _create_connection_frame(self) -> None:
        """Create MT5 connection frame."""
        try:
            frame = ttk.LabelFrame(self.widgets['main_frame'], text="MT5 Connection", padding=10)
            frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
            
            # Connection status
            ttk.Label(frame, text="Status:").grid(row=0, column=0, sticky='w')
            self.widgets['connection_status'] = ttk.Label(frame, text="Disconnected", foreground='red')
            self.widgets['connection_status'].grid(row=0, column=1, sticky='w', padx=(5, 0))
            
            # Connect button
            self.widgets['connect_btn'] = ttk.Button(frame, text="Connect", command=self._connect_mt5)
            self.widgets['connect_btn'].grid(row=0, column=2, padx=(10, 0))
            
            # Disconnect button
            self.widgets['disconnect_btn'] = ttk.Button(frame, text="Disconnect", command=self._disconnect_mt5)
            self.widgets['disconnect_btn'].grid(row=0, column=3, padx=(5, 0))
            
            # Account info
            self.widgets['account_info'] = ttk.Label(frame, text="Account: Not connected")
            self.widgets['account_info'].grid(row=1, column=0, columnspan=4, sticky='w', pady=(5, 0))
            
        except Exception as e:
            self.logger.log(f"❌ Error creating connection frame: {str(e)}")
    
    def _create_control_frame(self) -> None:
        """Create bot control frame."""
        try:
            frame = ttk.LabelFrame(self.widgets['main_frame'], text="Bot Control", padding=10)
            frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
            
            # Start/Stop buttons
            self.widgets['start_btn'] = ttk.Button(frame, text="Start Bot", command=self._start_bot)
            self.widgets['start_btn'].grid(row=0, column=0, padx=(0, 5))
            
            self.widgets['stop_btn'] = ttk.Button(frame, text="Stop Bot", command=self._stop_bot)
            self.widgets['stop_btn'].grid(row=0, column=1, padx=5)
            
            self.widgets['emergency_btn'] = ttk.Button(frame, text="EMERGENCY STOP", command=self._emergency_stop)
            self.widgets['emergency_btn'].grid(row=0, column=2, padx=5)
            self.widgets['emergency_btn'].configure(style='Emergency.TButton')
            
            # Bot status
            self.widgets['bot_status'] = ttk.Label(frame, text="Bot Status: Stopped")
            self.widgets['bot_status'].grid(row=1, column=0, columnspan=3, sticky='w', pady=(10, 0))
            
        except Exception as e:
            self.logger.log(f"❌ Error creating control frame: {str(e)}")
    
    def _create_strategy_frame(self) -> None:
        """Create strategy selection frame."""
        try:
            frame = ttk.LabelFrame(self.widgets['main_frame'], text="Strategy Settings", padding=10)
            frame.grid(row=2, column=0, sticky='new', padx=5, pady=5)
            
            # Strategy selection
            ttk.Label(frame, text="Strategy:").grid(row=0, column=0, sticky='w')
            self.widgets['strategy_var'] = tk.StringVar(value="Scalping")
            strategy_combo = ttk.Combobox(frame, textvariable=self.widgets['strategy_var'], 
                                        values=list(STRATEGY_DEFAULTS.keys()), state='readonly')
            strategy_combo.grid(row=0, column=1, sticky='ew', padx=(5, 0))
            strategy_combo.bind('<<ComboboxSelected>>', self._on_strategy_changed)
            
            # Strategy info
            self.widgets['strategy_info'] = ttk.Label(frame, text="TP: 8 pips, SL: 5 pips, Lot: 0.05")
            self.widgets['strategy_info'].grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 0))
            
            frame.columnconfigure(1, weight=1)
            
        except Exception as e:
            self.logger.log(f"❌ Error creating strategy frame: {str(e)}")
    
    def _create_risk_frame(self) -> None:
        """Create risk management frame."""
        try:
            frame = ttk.LabelFrame(self.widgets['main_frame'], text="Risk Management", padding=10)
            frame.grid(row=2, column=1, sticky='new', padx=5, pady=5)
            
            # Auto lot toggle
            self.widgets['auto_lot_var'] = tk.BooleanVar(value=True)
            auto_lot_check = ttk.Checkbutton(frame, text="Auto Lot Sizing", variable=self.widgets['auto_lot_var'])
            auto_lot_check.grid(row=0, column=0, columnspan=2, sticky='w')
            
            # Risk percentage
            ttk.Label(frame, text="Risk %:").grid(row=1, column=0, sticky='w', pady=(5, 0))
            self.widgets['risk_var'] = tk.StringVar(value="1.0")
            risk_entry = ttk.Entry(frame, textvariable=self.widgets['risk_var'], width=10)
            risk_entry.grid(row=1, column=1, sticky='ew', padx=(5, 0), pady=(5, 0))
            
            # Max positions
            ttk.Label(frame, text="Max Positions:").grid(row=2, column=0, sticky='w', pady=(5, 0))
            self.widgets['max_pos_var'] = tk.StringVar(value=str(MAX_POSITIONS))
            pos_entry = ttk.Entry(frame, textvariable=self.widgets['max_pos_var'], width=10)
            pos_entry.grid(row=2, column=1, sticky='ew', padx=(5, 0), pady=(5, 0))
            
            frame.columnconfigure(1, weight=1)
            
        except Exception as e:
            self.logger.log(f"❌ Error creating risk frame: {str(e)}")
    
    def _create_live_stats_frame(self) -> None:
        """Create live statistics frame."""
        try:
            frame = ttk.LabelFrame(self.widgets['monitor_frame'], text="Live Statistics", padding=10)
            frame.pack(fill='x', padx=5, pady=5)
            
            # Balance info
            balance_frame = ttk.Frame(frame)
            balance_frame.pack(fill='x', pady=(0, 5))
            
            ttk.Label(balance_frame, text="Balance:").pack(side='left')
            self.widgets['balance_label'] = ttk.Label(balance_frame, text="$0.00", font=('Arial', 12, 'bold'))
            self.widgets['balance_label'].pack(side='right')
            
            # Equity info
            equity_frame = ttk.Frame(frame)
            equity_frame.pack(fill='x', pady=2)
            
            ttk.Label(equity_frame, text="Equity:").pack(side='left')
            self.widgets['equity_label'] = ttk.Label(equity_frame, text="$0.00")
            self.widgets['equity_label'].pack(side='right')
            
            # Profit info
            profit_frame = ttk.Frame(frame)
            profit_frame.pack(fill='x', pady=2)
            
            ttk.Label(profit_frame, text="Today's P&L:").pack(side='left')
            self.widgets['profit_label'] = ttk.Label(profit_frame, text="$0.00")
            self.widgets['profit_label'].pack(side='right')
            
            # Positions count
            positions_frame = ttk.Frame(frame)
            positions_frame.pack(fill='x', pady=2)
            
            ttk.Label(positions_frame, text="Open Positions:").pack(side='left')
            self.widgets['positions_label'] = ttk.Label(positions_frame, text="0")
            self.widgets['positions_label'].pack(side='right')
            
        except Exception as e:
            self.logger.log(f"❌ Error creating live stats frame: {str(e)}")
    
    def _create_symbol_frame(self) -> None:
        """Create symbol management frame."""
        try:
            frame = ttk.LabelFrame(self.widgets['settings_frame'], text="Symbol Management", padding=10)
            frame.pack(fill='x', padx=5, pady=5)
            
            # Symbol input
            ttk.Label(frame, text="Test Symbol:").grid(row=0, column=0, sticky='w')
            self.widgets['symbol_var'] = tk.StringVar(value="EURUSD")
            symbol_entry = ttk.Entry(frame, textvariable=self.widgets['symbol_var'], width=15)
            symbol_entry.grid(row=0, column=1, padx=(5, 0))
            
            # Validate button
            validate_btn = ttk.Button(frame, text="Validate", command=self._validate_symbol)
            validate_btn.grid(row=0, column=2, padx=(5, 0))
            
            # Symbol info
            self.widgets['symbol_info'] = ttk.Label(frame, text="Symbol info will appear here")
            self.widgets['symbol_info'].grid(row=1, column=0, columnspan=3, sticky='w', pady=(10, 0))
            
        except Exception as e:
            self.logger.log(f"❌ Error creating symbol frame: {str(e)}")
    
    def _create_calculator_frame(self) -> None:
        """Create TP/SL calculator frame."""
        try:
            frame = ttk.LabelFrame(self.widgets['settings_frame'], text="TP/SL Calculator", padding=10)
            frame.pack(fill='x', padx=5, pady=5)
            
            # Input fields
            fields = [
                ("Symbol:", "calc_symbol"),
                ("Lot Size:", "calc_lot"),
                ("Current Price:", "calc_price"),
                ("TP (pips):", "calc_tp"),
                ("SL (pips):", "calc_sl")
            ]
            
            for i, (label, var_name) in enumerate(fields):
                ttk.Label(frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
                self.widgets[f'{var_name}_var'] = tk.StringVar()
                entry = ttk.Entry(frame, textvariable=self.widgets[f'{var_name}_var'], width=15)
                entry.grid(row=i, column=1, padx=(5, 0), pady=2)
            
            # Calculate button
            calc_btn = ttk.Button(frame, text="Calculate", command=self._calculate_tp_sl)
            calc_btn.grid(row=len(fields), column=0, columnspan=2, pady=(10, 0))
            
            # Results
            self.widgets['calc_results'] = ttk.Label(frame, text="Calculation results will appear here")
            self.widgets['calc_results'].grid(row=len(fields)+1, column=0, columnspan=2, sticky='w', pady=(10, 0))
            
        except Exception as e:
            self.logger.log(f"❌ Error creating calculator frame: {str(e)}")
    
    def _create_log_frame(self) -> None:
        """Create log display frame."""
        try:
            frame = ttk.LabelFrame(self.widgets['monitor_frame'], text="Live Logs", padding=10)
            frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Log text widget with scrollbar
            self.widgets['log_text'] = ScrolledText(frame, height=20, state='disabled')
            self.widgets['log_text'].pack(fill='both', expand=True)
            
            # Log control buttons
            button_frame = ttk.Frame(frame)
            button_frame.pack(fill='x', pady=(5, 0))
            
            ttk.Button(button_frame, text="Clear Logs", command=self._clear_logs).pack(side='left')
            ttk.Button(button_frame, text="Export CSV", command=self._export_logs_csv).pack(side='left', padx=(5, 0))
            ttk.Button(button_frame, text="Export TXT", command=self._export_logs_txt).pack(side='left', padx=(5, 0))
            
        except Exception as e:
            self.logger.log(f"❌ Error creating log frame: {str(e)}")
    
    def _create_status_frame(self) -> None:
        """Create status display frame."""
        try:
            frame = ttk.LabelFrame(self.root, text="Status", padding=5)
            frame.pack(fill='x', padx=5, pady=(0, 5))
            
            # Status labels
            self.widgets['status_time'] = ttk.Label(frame, text="Time: --")
            self.widgets['status_time'].pack(side='left')
            
            self.widgets['status_session'] = ttk.Label(frame, text="Session: --")
            self.widgets['status_session'].pack(side='left', padx=(20, 0))
            
            self.widgets['status_positions'] = ttk.Label(frame, text="Positions: 0")
            self.widgets['status_positions'].pack(side='left', padx=(20, 0))
            
            self.widgets['status_balance'] = ttk.Label(frame, text="Balance: --")
            self.widgets['status_balance'].pack(side='right')
            
        except Exception as e:
            self.logger.log(f"❌ Error creating status frame: {str(e)}")
    
    def _schedule_updates(self) -> None:
        """Schedule periodic GUI updates."""
        try:
            self._update_status()
            self.root.after(GUI_UPDATE_INTERVAL, self._schedule_updates)
        except Exception as e:
            self.logger.log(f"❌ Error scheduling updates: {str(e)}")
    
    def _update_status(self) -> None:
        """Update status displays."""
        try:
            # Update time
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.widgets['status_time'].config(text=f"Time: {current_time}")
            
            # Update connection status
            if hasattr(self.bot, 'connection') and self.bot.connection.connected:
                self.widgets['connection_status'].config(text="Connected", foreground='green')
                
                # Update account info if available
                if hasattr(self.bot, 'account_manager') and self.bot.account_manager.account_info:
                    account_info = self.bot.account_manager.account_info
                    account_text = f"Account: {account_info.get('login', 'N/A')} | Balance: {account_info.get('balance', 0):.2f}"
                    self.widgets['account_info'].config(text=account_text)
                    
                    balance_text = f"Balance: {account_info.get('balance', 0):.2f} {account_info.get('currency', '')}"
                    self.widgets['status_balance'].config(text=balance_text)
                    
                    # Update positions
                    if hasattr(self.bot.account_manager, 'get_position_count'):
                        pos_count = self.bot.account_manager.get_position_count()
                        self.widgets['status_positions'].config(text=f"Positions: {pos_count}")
            else:
                self.widgets['connection_status'].config(text="Disconnected", foreground='red')
                self.widgets['account_info'].config(text="Account: Not connected")
            
            # Update bot status
            if hasattr(self.bot, 'running') and self.bot.running:
                self.widgets['bot_status'].config(text="Bot Status: Running", foreground='green')
            else:
                self.widgets['bot_status'].config(text="Bot Status: Stopped", foreground='red')
            
            # Update session info
            if hasattr(self.bot, 'session_manager'):
                try:
                    current_session = self.bot.session_manager.get_current_session()
                    session_name = current_session.get('name', 'Unknown')
                    self.widgets['status_session'].config(text=f"Session: {session_name}")
                except:
                    self.widgets['status_session'].config(text="Session: --")
            
        except Exception as e:
            pass  # Silently handle update errors to avoid spam
    
    def log_to_gui(self, message: str) -> None:
        """Add message to GUI log display."""
        try:
            if 'log_text' in self.widgets:
                self.widgets['log_text'].config(state='normal')
                self.widgets['log_text'].insert('end', message + '\n')
                self.widgets['log_text'].see('end')
                self.widgets['log_text'].config(state='disabled')
                
                # Limit log size
                lines = self.widgets['log_text'].get('1.0', 'end').split('\n')
                if len(lines) > 1000:
                    self.widgets['log_text'].config(state='normal')
                    self.widgets['log_text'].delete('1.0', '100.0')
                    self.widgets['log_text'].config(state='disabled')
        except Exception as e:
            pass  # Silently handle GUI logging errors
    
    def _connect_mt5(self) -> None:
        """Connect to MT5."""
        try:
            if hasattr(self.bot, 'connection'):
                threading.Thread(target=self.bot.connection.connect, daemon=True).start()
        except Exception as e:
            self.logger.log(f"❌ Error connecting MT5: {str(e)}")
    
    def _disconnect_mt5(self) -> None:
        """Disconnect from MT5."""
        try:
            if hasattr(self.bot, 'connection'):
                self.bot.connection.disconnect()
        except Exception as e:
            self.logger.log(f"❌ Error disconnecting MT5: {str(e)}")
    
    def _start_bot(self) -> None:
        """Start the trading bot."""
        try:
            threading.Thread(target=self.bot.start, daemon=True).start()
        except Exception as e:
            self.logger.log(f"❌ Error starting bot: {str(e)}")
    
    def _stop_bot(self) -> None:
        """Stop the trading bot."""
        try:
            self.bot.stop()
        except Exception as e:
            self.logger.log(f"❌ Error stopping bot: {str(e)}")
    
    def _emergency_stop(self) -> None:
        """Emergency stop with confirmation."""
        try:
            result = messagebox.askyesno("Emergency Stop", 
                                       "Are you sure you want to emergency stop?\n"
                                       "This will close all positions and stop the bot.")
            if result:
                self.bot.emergency_stop()
        except Exception as e:
            self.logger.log(f"❌ Error in emergency stop: {str(e)}")
    
    def _on_strategy_changed(self, event=None) -> None:
        """Handle strategy selection change."""
        try:
            strategy = self.widgets['strategy_var'].get()
            if hasattr(self.bot, 'strategy_manager'):
                self.bot.strategy_manager.set_strategy(strategy)
            
            # Update strategy info
            config = STRATEGY_DEFAULTS.get(strategy, {})
            info_text = f"TP: {config.get('tp_pips', 0)} pips, SL: {config.get('sl_pips', 0)} pips, Lot: {config.get('lot_size', 0)}"
            self.widgets['strategy_info'].config(text=info_text)
            
        except Exception as e:
            self.logger.log(f"❌ Error changing strategy: {str(e)}")
    
    def _validate_symbol(self) -> None:
        """Validate entered symbol."""
        try:
            symbol = self.widgets['symbol_var'].get().strip().upper()
            if not symbol:
                return
            
            if hasattr(self.bot, 'connection') and hasattr(self.bot, 'symbol_manager'):
                # Run validation in background
                def validate():
                    try:
                        if self.bot.symbol_manager.validate_and_activate_symbol(symbol):
                            symbol_info = self.bot.symbol_manager.get_symbol_info(symbol)
                            if symbol_info:
                                info_text = (f"✅ {symbol}: Digits: {symbol_info.get('digits', 'N/A')}, "
                                           f"Spread: {symbol_info.get('spread', 'N/A'):.1f} pips, "
                                           f"Point: {symbol_info.get('point', 'N/A')}")
                                self.widgets['symbol_info'].config(text=info_text, foreground='green')
                            else:
                                self.widgets['symbol_info'].config(text=f"✅ {symbol} validated but no detailed info", 
                                                                 foreground='orange')
                        else:
                            self.widgets['symbol_info'].config(text=f"❌ {symbol} validation failed", 
                                                             foreground='red')
                    except Exception as e:
                        self.widgets['symbol_info'].config(text=f"❌ Error validating {symbol}: {str(e)}", 
                                                         foreground='red')
                
                threading.Thread(target=validate, daemon=True).start()
            else:
                self.widgets['symbol_info'].config(text="❌ Not connected to MT5", foreground='red')
                
        except Exception as e:
            self.logger.log(f"❌ Error validating symbol: {str(e)}")
    
    def _calculate_tp_sl(self) -> None:
        """Calculate TP/SL values."""
        try:
            # Get input values
            symbol = self.widgets['calc_symbol_var'].get().strip().upper()
            lot_str = self.widgets['calc_lot_var'].get().strip()
            price_str = self.widgets['calc_price_var'].get().strip()
            tp_str = self.widgets['calc_tp_var'].get().strip()
            sl_str = self.widgets['calc_sl_var'].get().strip()
            
            if not all([symbol, lot_str, tp_str, sl_str]):
                self.widgets['calc_results'].config(text="❌ Please fill all fields", foreground='red')
                return
            
            try:
                lot_size = float(lot_str)
                tp_pips = float(tp_str)
                sl_pips = float(sl_str)
                current_price = float(price_str) if price_str else 0
            except ValueError:
                self.widgets['calc_results'].config(text="❌ Invalid numeric values", foreground='red')
                return
            
            # Calculate if we have risk manager
            if hasattr(self.bot, 'risk_manager'):
                pip_value = self.bot.risk_manager.calculate_pip_value(symbol, lot_size)
                
                tp_profit = tp_pips * pip_value
                sl_loss = sl_pips * pip_value
                risk_reward = tp_pips / sl_pips if sl_pips > 0 else 0
                
                result_text = (f"Pip Value: {pip_value:.2f} | "
                             f"TP Profit: {tp_profit:.2f} | "
                             f"SL Loss: {sl_loss:.2f} | "
                             f"R:R = 1:{risk_reward:.2f}")
                
                self.widgets['calc_results'].config(text=result_text, foreground='green')
            else:
                self.widgets['calc_results'].config(text="❌ Risk manager not available", foreground='red')
                
        except Exception as e:
            self.widgets['calc_results'].config(text=f"❌ Calculation error: {str(e)}", foreground='red')
    
    def _clear_logs(self) -> None:
        """Clear log display."""
        try:
            self.widgets['log_text'].config(state='normal')
            self.widgets['log_text'].delete('1.0', 'end')
            self.widgets['log_text'].config(state='disabled')
            self.logger.clear_logs()
        except Exception as e:
            self.logger.log(f"❌ Error clearing logs: {str(e)}")
    
    def _export_logs_csv(self) -> None:
        """Export logs to CSV file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Logs to CSV"
            )
            if filename:
                result = self.logger.export_logs_csv(filename)
                if result:
                    messagebox.showinfo("Export Complete", f"Logs exported to:\n{result}")
        except Exception as e:
            self.logger.log(f"❌ Error exporting logs to CSV: {str(e)}")
    
    def _export_logs_txt(self) -> None:
        """Export logs to text file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Logs to Text"
            )
            if filename:
                result = self.logger.export_logs_txt(filename)
                if result:
                    messagebox.showinfo("Export Complete", f"Logs exported to:\n{result}")
        except Exception as e:
            self.logger.log(f"❌ Error exporting logs to TXT: {str(e)}")
    
    def _show_calculator(self) -> None:
        """Show TP/SL calculator window."""
        try:
            # Switch to settings tab
            self.widgets['notebook'].select(2)
        except Exception as e:
            self.logger.log(f"❌ Error showing calculator: {str(e)}")
    
    def _show_performance_report(self) -> None:
        """Show performance report."""
        try:
            session_data = {}
            if hasattr(self.bot, 'session_manager'):
                session_data = self.bot.session_manager.get_session_summary()
            
            report = self.logger.generate_performance_report(session_data)
            
            # Show in new window
            report_window = tk.Toplevel(self.root)
            report_window.title("Performance Report")
            report_window.geometry("600x400")
            
            text_widget = ScrolledText(report_window, state='disabled')
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            
            text_widget.config(state='normal')
            text_widget.insert('1.0', report)
            text_widget.config(state='disabled')
            
        except Exception as e:
            self.logger.log(f"❌ Error showing performance report: {str(e)}")
    
    def _test_telegram(self) -> None:
        """Test Telegram notification."""
        try:
            success = self.logger.send_test_notification()
            if success:
                messagebox.showinfo("Telegram Test", "Test notification sent successfully!")
            else:
                messagebox.showerror("Telegram Test", "Failed to send test notification. Check configuration.")
        except Exception as e:
            self.logger.log(f"❌ Error testing Telegram: {str(e)}")
    
    def _show_about(self) -> None:
        """Show about dialog."""
        try:
            about_text = """MT5 Automated Trading Bot
            
Version: 1.0.0
A comprehensive automated trading bot for MetaTrader 5
with modular architecture and advanced risk management.

Features:
• Multiple trading strategies
• Session-aware trading
• Risk management
• News filtering
• Telegram notifications
• Comprehensive logging

Created with ❤️ for professional traders"""
            
            messagebox.showinfo("About", about_text)
        except Exception as e:
            self.logger.log(f"❌ Error showing about: {str(e)}")
    
    def _on_closing(self) -> None:
        """Handle window closing."""
        try:
            if hasattr(self.bot, 'running') and self.bot.running:
                result = messagebox.askyesno("Quit", "Bot is still running. Stop bot and quit?")
                if result:
                    self.bot.stop()
                    self.root.destroy()
            else:
                self.root.destroy()
        except Exception as e:
            self.logger.log(f"❌ Error closing window: {str(e)}")
            self.root.destroy()
    
    def run(self) -> None:
        """Run the GUI main loop."""
        try:
            self.create_main_window()
            if self.root:
                self.root.mainloop()
        except Exception as e:
            self.logger.log(f"❌ Error running GUI: {str(e)}")
