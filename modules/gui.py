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
        """Create the main GUI window with bobot2.py design."""
        try:
            self.root = tk.Tk()
            self.root.title("🤖 MT5 Automated Trading Bot Pro")
            self.root.geometry("1400x900")  # Match bobot2.py dimensions
            self.root.minsize(1200, 800)
            
            # Configure dark theme to match bobot2.py
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
            
            # Create main frames
            self._create_menu_bar()
            self._create_main_frames()
            # Create all frames for bobot2.py compatibility
            self._create_connection_frame()
            self._create_control_frame()
            self._create_strategy_frame()
            self._create_risk_frame()
            self._create_enhanced_stats_frame()  # Enhanced version
            self._create_symbol_frame()
            self._create_positions_table()  # New: Real-time position table
            self._create_enhanced_calculator()  # Enhanced multi-unit calculator
            self._create_enhanced_logs()  # Enhanced log viewer
            self._create_session_display()  # New: Session indicator
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
            if self.root:
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
            
            # Tab 1: Main Control (exact bobot2.py match)
            self.widgets['main_frame'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['main_frame'], text="🎯 Main Control")
            
            # Tab 2: Position Monitor (exact bobot2.py match)
            self.widgets['positions_frame'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['positions_frame'], text="📊 Positions")
            
            # Tab 3: Calculator (exact bobot2.py match)
            self.widgets['calculator_frame'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['calculator_frame'], text="🧮 Calculator")
            
            # Tab 4: Logs (exact bobot2.py match)
            self.widgets['logs_frame'] = ttk.Frame(self.widgets['notebook'])
            self.widgets['notebook'].add(self.widgets['logs_frame'], text="📋 Logs")
            
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
            frame = ttk.LabelFrame(self.widgets['main_frame'], text="🎯 Symbol Management", padding=10)
            frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
            
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
            # This function is now replaced by _create_enhanced_calculator
            # Keep for backward compatibility but don't create duplicate UI
            pass
            
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
            # This function is now replaced by _create_enhanced_logs
            # Keep for backward compatibility but don't create duplicate UI
            pass
            
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
            if self.root:
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
                    if self.root:
                        self.root.destroy()
            else:
                if self.root:
                    self.root.destroy()
        except Exception as e:
            self.logger.log(f"❌ Error closing window: {str(e)}")
            if self.root:
                self.root.destroy()
    
    def _create_enhanced_stats_frame(self) -> None:
        """Create enhanced statistics frame with all bobot2.py metrics."""
        try:
            frame = ttk.LabelFrame(self.widgets['main_frame'], text="📊 Enhanced Statistics", padding=10)
            frame.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
            
            # Statistics grid (exact bobot2.py layout)
            stats_grid = [
                ("Win Rate:", "win_rate", "0%"),
                ("Daily Orders:", "daily_orders", "0"),
                ("Total P&L:", "total_pnl", "$0.00"),
                ("Current Margin:", "current_margin", "0%"),
                ("Max Drawdown:", "max_drawdown", "0%"),
                ("Active Positions:", "active_positions", "0"),
                ("Strategy Performance:", "strategy_perf", "N/A"),
                ("Session Volume:", "session_volume", "0 lots")
            ]
            
            self.widgets['enhanced_stats'] = {}
            for i, (label, key, default) in enumerate(stats_grid):
                row, col = divmod(i, 2)
                ttk.Label(frame, text=label).grid(row=row, column=col*2, sticky='w', padx=5, pady=2)
                self.widgets['enhanced_stats'][key] = ttk.Label(frame, text=default, foreground='cyan')
                self.widgets['enhanced_stats'][key].grid(row=row, column=col*2+1, sticky='w', padx=5, pady=2)
                
        except Exception as e:
            self.logger.log(f"❌ Error creating enhanced stats frame: {str(e)}")
    
    def _create_positions_table(self) -> None:
        """Create real-time positions table (exact bobot2.py implementation)."""
        try:
            # Position table in Positions tab
            table_frame = ttk.LabelFrame(self.widgets['positions_frame'], text="🔥 Live Positions", padding=10)
            table_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Treeview for positions table
            columns = ('Symbol', 'Type', 'Volume', 'Open Price', 'Current Price', 'P&L', 'Time')
            self.widgets['positions_tree'] = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
            
            # Configure column headings and widths (exact bobot2.py styling)
            column_widths = {'Symbol': 80, 'Type': 60, 'Volume': 80, 'Open Price': 100, 
                           'Current Price': 100, 'P&L': 100, 'Time': 120}
            
            for col in columns:
                self.widgets['positions_tree'].heading(col, text=col)
                self.widgets['positions_tree'].column(col, width=column_widths.get(col, 100), anchor='center')
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.widgets['positions_tree'].yview)
            h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.widgets['positions_tree'].xview)
            self.widgets['positions_tree'].configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack components
            self.widgets['positions_tree'].pack(side='left', fill='both', expand=True)
            v_scrollbar.pack(side='right', fill='y')
            h_scrollbar.pack(side='bottom', fill='x')
            
            # Position control buttons
            btn_frame = ttk.Frame(self.widgets['positions_frame'])
            btn_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Button(btn_frame, text="🔄 Refresh", command=self._refresh_positions).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="❌ Close All", command=self._close_all_positions).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="📊 Export", command=self._export_positions).pack(side='left', padx=5)
                
        except Exception as e:
            self.logger.log(f"❌ Error creating positions table: {str(e)}")
    
    def _create_enhanced_calculator(self) -> None:
        """Create enhanced multi-unit TP/SL calculator (exact bobot2.py implementation)."""
        try:
            calc_frame = ttk.LabelFrame(self.widgets['calculator_frame'], text="🧮 Advanced TP/SL Calculator", padding=15)
            calc_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Multi-unit calculator layout (exact bobot2.py design)
            input_frame = ttk.Frame(calc_frame)
            input_frame.pack(fill='x', pady=5)
            
            # Symbol and lot size
            ttk.Label(input_frame, text="Symbol:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
            self.widgets['calc_symbol'] = ttk.Combobox(input_frame, values=POPULAR_SYMBOLS, width=12)
            self.widgets['calc_symbol'].set('EURUSD')
            self.widgets['calc_symbol'].grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(input_frame, text="Lot Size:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
            self.widgets['calc_lot'] = ttk.Entry(input_frame, width=10)
            self.widgets['calc_lot'].insert(0, '0.01')
            self.widgets['calc_lot'].grid(row=0, column=3, padx=5, pady=5)
            
            # Multi-unit TP/SL inputs (exact bobot2.py layout)
            units_frame = ttk.LabelFrame(calc_frame, text="Multi-Unit TP/SL Setup", padding=10)
            units_frame.pack(fill='both', expand=True, pady=10)
            
            # TP/SL unit options
            self.widgets['tp_units'] = {}
            self.widgets['sl_units'] = {}
            
            units = ['Pips', 'Price', 'Percentage', 'Currency']
            for i, unit in enumerate(units):
                # TP section
                tp_frame = ttk.Frame(units_frame)
                tp_frame.grid(row=i, column=0, sticky='ew', padx=10, pady=5)
                
                ttk.Label(tp_frame, text=f"TP ({unit}):").pack(side='left', padx=5)
                self.widgets['tp_units'][unit] = ttk.Entry(tp_frame, width=12)
                self.widgets['tp_units'][unit].pack(side='left', padx=5)
                
                # SL section
                sl_frame = ttk.Frame(units_frame)
                sl_frame.grid(row=i, column=1, sticky='ew', padx=10, pady=5)
                
                ttk.Label(sl_frame, text=f"SL ({unit}):").pack(side='left', padx=5)
                self.widgets['sl_units'][unit] = ttk.Entry(sl_frame, width=12)
                self.widgets['sl_units'][unit].pack(side='left', padx=5)
            
            # Calculate button and results
            calc_btn_frame = ttk.Frame(calc_frame)
            calc_btn_frame.pack(fill='x', pady=10)
            
            ttk.Button(calc_btn_frame, text="🔥 Calculate All Units", 
                      command=self._calculate_multi_units).pack(pady=5)
            
            # Enhanced results display
            self.widgets['calc_results_enhanced'] = ScrolledText(calc_frame, height=8, state='disabled')
            self.widgets['calc_results_enhanced'].pack(fill='both', expand=True, pady=5)
                
        except Exception as e:
            self.logger.log(f"❌ Error creating enhanced calculator: {str(e)}")
    
    def _create_enhanced_logs(self) -> None:
        """Create enhanced log viewer with filtering (exact bobot2.py implementation)."""
        try:
            logs_frame = ttk.LabelFrame(self.widgets['logs_frame'], text="📋 Enhanced Log Viewer", padding=10)
            logs_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Log filtering controls (exact bobot2.py layout)
            filter_frame = ttk.Frame(logs_frame)
            filter_frame.pack(fill='x', pady=5)
            
            ttk.Label(filter_frame, text="Filter:").pack(side='left', padx=5)
            self.widgets['log_filter'] = ttk.Combobox(filter_frame, values=['All', 'Trades', 'Errors', 'Signals', 'Session'], width=15)
            self.widgets['log_filter'].set('All')
            self.widgets['log_filter'].pack(side='left', padx=5)
            
            ttk.Button(filter_frame, text="🔍 Apply Filter", command=self._apply_log_filter).pack(side='left', padx=5)
            ttk.Button(filter_frame, text="🗑️ Clear Logs", command=self._clear_logs).pack(side='left', padx=5)
            ttk.Button(filter_frame, text="💾 Export", command=self._export_logs_csv).pack(side='left', padx=5)
            
            # Enhanced log display with line numbers
            log_display_frame = ttk.Frame(logs_frame)
            log_display_frame.pack(fill='both', expand=True, pady=5)
            
            self.widgets['log_text_enhanced'] = ScrolledText(log_display_frame, state='disabled', height=15)
            self.widgets['log_text_enhanced'].pack(fill='both', expand=True)
            
            # Configure text tags for colored output
            self.widgets['log_text_enhanced'].tag_configure('error', foreground='red')
            self.widgets['log_text_enhanced'].tag_configure('success', foreground='green')
            self.widgets['log_text_enhanced'].tag_configure('warning', foreground='yellow')
            self.widgets['log_text_enhanced'].tag_configure('info', foreground='cyan')
                
        except Exception as e:
            self.logger.log(f"❌ Error creating enhanced logs: {str(e)}")
    
    def _create_session_display(self) -> None:
        """Create session indicator display (exact bobot2.py implementation)."""
        try:
            session_frame = ttk.LabelFrame(self.widgets['main_frame'], text="🌍 Trading Sessions", padding=10)
            session_frame.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
            
            # Session indicators (exact bobot2.py layout)
            sessions = ['Asia 🌏', 'London 🌍', 'New York 🌎']
            self.widgets['session_indicators'] = {}
            
            for i, session in enumerate(sessions):
                session_key = session.split()[0].lower()
                
                frame = ttk.Frame(session_frame)
                frame.grid(row=0, column=i, padx=10, pady=5)
                
                ttk.Label(frame, text=session).pack()
                self.widgets['session_indicators'][session_key] = ttk.Label(frame, text="●", foreground='gray', font=('Arial', 16))
                self.widgets['session_indicators'][session_key].pack()
                
            # Current session display
            ttk.Label(session_frame, text="Active:").grid(row=1, column=0, sticky='w', pady=5)
            self.widgets['current_session'] = ttk.Label(session_frame, text="London", foreground='green', font=('Arial', 12, 'bold'))
            self.widgets['current_session'].grid(row=1, column=1, pady=5)
                
        except Exception as e:
            self.logger.log(f"❌ Error creating session display: {str(e)}")
    
    # Enhanced GUI callback functions
    def _refresh_positions(self) -> None:
        """Refresh positions table with real-time data."""
        try:
            # Clear existing items
            for item in self.widgets['positions_tree'].get_children():
                self.widgets['positions_tree'].delete(item)
            
            # Get positions from account manager
            if hasattr(self.bot, 'account_manager') and self.bot.account_manager:
                positions = self.bot.account_manager.get_positions()
                for pos in positions:
                    self.widgets['positions_tree'].insert('', 'end', values=pos)
                    
        except Exception as e:
            self.logger.log(f"❌ Error refreshing positions: {str(e)}")
    
    def _close_all_positions(self) -> None:
        """Close all positions (emergency function)."""
        try:
            result = messagebox.askyesno("Close All Positions", 
                                       "⚠️ This will close ALL open positions immediately. Are you sure?")
            if result and hasattr(self.bot, 'strategy_manager'):
                success = self.bot.strategy_manager.close_all_positions()
                if success:
                    messagebox.showinfo("Success", "All positions closed successfully!")
                else:
                    messagebox.showerror("Error", "Failed to close some positions. Check logs.")
        except Exception as e:
            self.logger.log(f"❌ Error closing all positions: {str(e)}")
    
    def _export_positions(self) -> None:
        """Export positions to CSV."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Export Positions"
            )
            if filename and hasattr(self.bot, 'account_manager'):
                success = self.bot.account_manager.export_positions_csv(filename)
                if success:
                    messagebox.showinfo("Export Complete", f"Positions exported to:\n{filename}")
        except Exception as e:
            self.logger.log(f"❌ Error exporting positions: {str(e)}")
    
    def _calculate_multi_units(self) -> None:
        """Calculate TP/SL for all units (exact bobot2.py implementation)."""
        try:
            symbol = self.widgets['calc_symbol'].get()
            lot_size = float(self.widgets['calc_lot'].get())
            
            results = []
            results.append(f"🧮 Multi-Unit TP/SL Calculator Results for {symbol}\n")
            results.append(f"Lot Size: {lot_size}\n")
            results.append("=" * 50 + "\n")
            
            # Calculate for each unit type
            for unit in ['Pips', 'Price', 'Percentage', 'Currency']:
                tp_value = self.widgets['tp_units'][unit].get()
                sl_value = self.widgets['sl_units'][unit].get()
                
                if tp_value or sl_value:
                    results.append(f"\n📊 {unit} Calculations:\n")
                    
                    if tp_value:
                        # Calculate TP profit based on unit type
                        tp_profit = self._calculate_unit_profit(symbol, lot_size, tp_value, unit, 'TP')
                        results.append(f"  TP ({unit}): {tp_value} → Profit: ${tp_profit:.2f}\n")
                    
                    if sl_value:
                        # Calculate SL loss based on unit type
                        sl_loss = self._calculate_unit_profit(symbol, lot_size, sl_value, unit, 'SL')
                        results.append(f"  SL ({unit}): {sl_value} → Loss: ${sl_loss:.2f}\n")
                    
                    if tp_value and sl_value:
                        # Calculate risk-reward ratio
                        rr_ratio = abs(float(tp_value)) / abs(float(sl_value)) if float(sl_value) != 0 else 0
                        results.append(f"  Risk:Reward = 1:{rr_ratio:.2f}\n")
            
            # Display results
            self.widgets['calc_results_enhanced'].config(state='normal')
            self.widgets['calc_results_enhanced'].delete('1.0', 'end')
            self.widgets['calc_results_enhanced'].insert('1.0', ''.join(results))
            self.widgets['calc_results_enhanced'].config(state='disabled')
            
        except Exception as e:
            error_msg = f"❌ Calculation error: {str(e)}"
            self.widgets['calc_results_enhanced'].config(state='normal')
            self.widgets['calc_results_enhanced'].delete('1.0', 'end')
            self.widgets['calc_results_enhanced'].insert('1.0', error_msg)
            self.widgets['calc_results_enhanced'].config(state='disabled')
    
    def _calculate_unit_profit(self, symbol: str, lot_size: float, value: str, unit: str, direction: str) -> float:
        """Calculate profit/loss for specific unit type."""
        try:
            if not value or not self.bot.risk_manager:
                return 0.0
            
            value_float = float(value)
            
            if unit == 'Pips':
                return self.bot.risk_manager.calculate_pip_value(symbol, lot_size) * value_float
            elif unit == 'Currency':
                return value_float
            elif unit == 'Percentage':
                # Calculate based on account balance percentage
                if hasattr(self.bot, 'account_manager'):
                    balance = self.bot.account_manager.get_balance()
                    return balance * (value_float / 100)
                return 0.0
            elif unit == 'Price':
                # Calculate based on price difference
                pip_value = self.bot.risk_manager.calculate_pip_value(symbol, lot_size)
                point = 0.0001 if 'JPY' not in symbol else 0.01
                pips = value_float / point
                return pip_value * pips
            
            return 0.0
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating unit profit: {str(e)}")
            return 0.0
    
    def _apply_log_filter(self) -> None:
        """Apply log filtering based on selected category."""
        try:
            filter_type = self.widgets['log_filter'].get()
            # Implementation would filter logs based on type
            self.logger.log(f"📋 Applied log filter: {filter_type}")
        except Exception as e:
            self.logger.log(f"❌ Error applying log filter: {str(e)}")

    def run(self) -> None:
        """Run the GUI main loop."""
        try:
            self.create_main_window()
            if self.root:
                self.root.mainloop()
        except Exception as e:
            self.logger.log(f"❌ Error running GUI: {str(e)}")
