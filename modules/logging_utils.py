"""
Logging Utilities Module
Centralized logging with file output, GUI integration, and Telegram notifications.
"""

import os
import datetime
import csv
import threading
import requests
from typing import Optional, List, Dict, Any
import time

from config import *


class BotLogger:
    """Centralized logger with multiple output channels."""
    
    def __init__(self):
        """Initialize the bot logger."""
        self.log_lock = threading.Lock()
        self.gui_callback = None
        self.log_buffer = []
        self.max_buffer_size = 1000
        self.telegram_rate_limit = {}
        
        # Ensure log directory exists
        self._ensure_log_directory()
        
        # Initialize log file
        self.log_file_path = self._get_log_file_path()
        
    def _ensure_log_directory(self) -> bool:
        """Ensure log directory exists."""
        try:
            if not os.path.exists(LOG_DIR):
                os.makedirs(LOG_DIR, exist_ok=True)
                print(f"📁 Created log directory: {LOG_DIR}")
            return True
        except PermissionError as pe:
            print(f"❌ Permission denied creating log directory: {str(pe)}")
            return False
        except Exception as e:
            print(f"❌ Failed to create log directory: {str(e)}")
            return False
    
    def _get_log_file_path(self) -> str:
        """Get current log file path with date."""
        today = datetime.datetime.now().strftime("%Y%m%d")
        return os.path.join(LOG_DIR, f"{LOG_FILE_PREFIX}_{today}.log")
    
    def set_gui_callback(self, callback) -> None:
        """
        Set GUI callback for log display.
        
        Args:
            callback: Function to call for GUI log updates
        """
        self.gui_callback = callback
    
    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log message to all configured outputs.
        
        Args:
            message: Message to log
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        with self.log_lock:
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                formatted_message = f"[{timestamp}] {level}: {message}"
                
                # Console output
                print(formatted_message)
                
                # File output
                self._write_to_file(formatted_message)
                
                # Buffer for GUI
                self._add_to_buffer(formatted_message)
                
                # GUI callback
                if self.gui_callback:
                    try:
                        self.gui_callback(formatted_message)
                    except Exception as e:
                        print(f"GUI logging failed: {str(e)}")
                
                # Telegram notification for important messages
                if level in ["ERROR", "CRITICAL"] or "✅" in message or "❌" in message:
                    self._send_telegram_notification(message)
                    
            except Exception as e:
                print(f"Logging error: {str(e)}")
    
    def _write_to_file(self, message: str) -> None:
        """Write message to log file."""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        except Exception as e:
            print(f"File logging error: {str(e)}")
    
    def _add_to_buffer(self, message: str) -> None:
        """Add message to internal buffer."""
        try:
            self.log_buffer.append(message)
            
            # Maintain buffer size
            if len(self.log_buffer) > self.max_buffer_size:
                self.log_buffer = self.log_buffer[-self.max_buffer_size:]
                
        except Exception as e:
            print(f"Buffer logging error: {str(e)}")
    
    def _send_telegram_notification(self, message: str) -> None:
        """
        Send notification to Telegram with rate limiting.
        
        Args:
            message: Message to send
        """
        try:
            # Skip if no token configured
            if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your_telegram_bot_token":
                return
            
            # Rate limiting - max 1 message per 10 seconds
            current_time = time.time()
            if current_time - self.telegram_rate_limit.get('last_send', 0) < 10:
                return
            
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            
            # Truncate long messages
            if len(message) > 4000:
                message = message[:4000] + "... (truncated)"
            
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': f"🤖 Trading Bot: {message}",
                'parse_mode': 'HTML'
            }
            
            # Send in background to avoid blocking
            threading.Thread(
                target=self._send_telegram_request,
                args=(url, payload),
                daemon=True
            ).start()
            
            self.telegram_rate_limit['last_send'] = current_time
            
        except Exception as e:
            print(f"Telegram notification error: {str(e)}")
    
    def _send_telegram_request(self, url: str, payload: Dict[str, Any]) -> None:
        """Send Telegram request in background thread."""
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                print(f"Telegram API error: {response.status_code}")
        except Exception as e:
            print(f"Telegram request error: {str(e)}")
    
    def get_log_buffer(self) -> List[str]:
        """
        Get current log buffer contents.
        
        Returns:
            List of log messages
        """
        with self.log_lock:
            return self.log_buffer.copy()
    
    def export_logs_csv(self, filename: str = None) -> str:
        """
        Export logs to CSV file.
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            str: Path to exported file
        """
        try:
            if filename is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"exported_logs_{timestamp}.csv"
            
            filepath = os.path.join(LOG_DIR, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Level', 'Message'])
                
                for log_entry in self.log_buffer:
                    try:
                        # Parse log entry
                        parts = log_entry.split('] ', 1)
                        if len(parts) == 2:
                            timestamp_part = parts[0].replace('[', '')
                            rest = parts[1]
                            
                            level_parts = rest.split(': ', 1)
                            if len(level_parts) == 2:
                                level = level_parts[0]
                                message = level_parts[1]
                            else:
                                level = "INFO"
                                message = rest
                        else:
                            timestamp_part = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            level = "INFO"
                            message = log_entry
                        
                        writer.writerow([timestamp_part, level, message])
                        
                    except Exception as e:
                        print(f"Error parsing log entry: {str(e)}")
                        continue
            
            self.log(f"📊 Logs exported to: {filepath}")
            return filepath
            
        except Exception as e:
            self.log(f"❌ Error exporting logs: {str(e)}", "ERROR")
            return ""
    
    def export_logs_txt(self, filename: str = None) -> str:
        """
        Export logs to text file.
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            str: Path to exported file
        """
        try:
            if filename is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"exported_logs_{timestamp}.txt"
            
            filepath = os.path.join(LOG_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("MT5 Trading Bot - Log Export\n")
                f.write("=" * 50 + "\n")
                f.write(f"Export Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Entries: {len(self.log_buffer)}\n")
                f.write("=" * 50 + "\n\n")
                
                for log_entry in self.log_buffer:
                    f.write(log_entry + '\n')
            
            self.log(f"📊 Logs exported to: {filepath}")
            return filepath
            
        except Exception as e:
            self.log(f"❌ Error exporting logs: {str(e)}", "ERROR")
            return ""
    
    def clear_logs(self) -> None:
        """Clear log buffer."""
        with self.log_lock:
            self.log_buffer.clear()
            self.log("🧹 Log buffer cleared")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Dict with log statistics
        """
        try:
            with self.log_lock:
                total_logs = len(self.log_buffer)
                error_count = sum(1 for log in self.log_buffer if "ERROR" in log)
                warning_count = sum(1 for log in self.log_buffer if "WARNING" in log)
                
                return {
                    "total_logs": total_logs,
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "buffer_size": self.max_buffer_size,
                    "log_file": self.log_file_path
                }
                
        except Exception as e:
            self.log(f"❌ Error getting log stats: {str(e)}", "ERROR")
            return {}
    
    def send_test_notification(self) -> bool:
        """
        Send test Telegram notification.
        
        Returns:
            bool: True if notification sent successfully
        """
        try:
            test_message = "🧪 Test notification from MT5 Trading Bot"
            self._send_telegram_notification(test_message)
            self.log("📱 Test notification sent to Telegram")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to send test notification: {str(e)}", "ERROR")
            return False
    
    def generate_performance_report(self, session_data: Dict[str, Any] = None) -> str:
        """
        Generate performance report.
        
        Args:
            session_data: Session performance data
            
        Returns:
            str: Formatted performance report
        """
        try:
            report_lines = []
            report_lines.append("📊 TRADING BOT PERFORMANCE REPORT")
            report_lines.append("=" * 50)
            report_lines.append(f"Report Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            if session_data:
                report_lines.append("💰 SESSION STATISTICS:")
                report_lines.append(f"  Total Trades: {session_data.get('total_trades', 0)}")
                report_lines.append(f"  Winning Trades: {session_data.get('winning_trades', 0)}")
                report_lines.append(f"  Losing Trades: {session_data.get('losing_trades', 0)}")
                
                total_trades = session_data.get('total_trades', 0)
                if total_trades > 0:
                    win_rate = (session_data.get('winning_trades', 0) / total_trades) * 100
                    report_lines.append(f"  Win Rate: {win_rate:.1f}%")
                
                report_lines.append(f"  Total Profit: {session_data.get('total_profit', 0):.2f}")
                report_lines.append("")
            
            # Log statistics
            log_stats = self.get_log_stats()
            report_lines.append("📋 LOG STATISTICS:")
            report_lines.append(f"  Total Log Entries: {log_stats.get('total_logs', 0)}")
            report_lines.append(f"  Error Count: {log_stats.get('error_count', 0)}")
            report_lines.append(f"  Warning Count: {log_stats.get('warning_count', 0)}")
            report_lines.append("")
            
            report_lines.append("=" * 50)
            
            report = "\n".join(report_lines)
            self.log("📊 Performance report generated")
            
            return report
            
        except Exception as e:
            self.log(f"❌ Error generating performance report: {str(e)}", "ERROR")
            return ""
