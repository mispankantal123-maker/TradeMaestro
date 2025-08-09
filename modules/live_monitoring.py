"""
Live Monitoring & Alerting Module
Real-time dashboard and Telegram notifications for live trading
"""

import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import requests


class LiveMonitoringDashboard:
    """Real-time monitoring dashboard for live trading metrics."""
    
    def __init__(self, logger, performance_monitor):
        """Initialize live monitoring dashboard."""
        self.logger = logger
        self.performance_monitor = performance_monitor
        
        # Metrics storage
        self.trading_metrics = {
            'total_signals': 0,
            'executed_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_pnl': 0.0,
            'daily_pnl': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0
        }
        
        # Strategy-specific metrics
        self.strategy_metrics = defaultdict(lambda: {
            'signals': 0,
            'executed': 0,
            'winrate': 0.0,
            'avg_latency': 0.0,
            'pnl': 0.0
        })
        
        # Real-time tracking
        self.signal_latencies = deque(maxlen=100)
        self.execution_times = deque(maxlen=100)
        self.error_log = deque(maxlen=50)
        
        # Dashboard state
        self.last_update = time.time()
        self.dashboard_active = True
        
        # Update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        self.logger.log("✅ Live Monitoring Dashboard initialized")
    
    def record_signal(self, strategy: str, symbol: str, action: str, quality_score: float):
        """Record new signal detection."""
        try:
            self.trading_metrics['total_signals'] += 1
            self.strategy_metrics[strategy]['signals'] += 1
            
            self.logger.log(f"📊 Signal recorded: {strategy} {symbol} {action} (quality: {quality_score})")
            
        except Exception as e:
            self.logger.log(f"❌ Error recording signal: {str(e)}")
    
    def record_trade_execution(self, strategy: str, symbol: str, action: str, 
                             lot_size: float, execution_time: float):
        """Record trade execution."""
        try:
            self.trading_metrics['executed_trades'] += 1
            self.strategy_metrics[strategy]['executed'] += 1
            self.execution_times.append(execution_time)
            
            # Update winrate
            if self.strategy_metrics[strategy]['signals'] > 0:
                self.strategy_metrics[strategy]['winrate'] = (
                    self.strategy_metrics[strategy]['executed'] / 
                    self.strategy_metrics[strategy]['signals'] * 100
                )
            
            self.logger.log(f"✅ Trade executed: {strategy} {symbol} {action} {lot_size} lots in {execution_time*1000:.1f}ms")
            
        except Exception as e:
            self.logger.log(f"❌ Error recording trade execution: {str(e)}")
    
    def record_trade_result(self, strategy: str, pnl: float, successful: bool):
        """Record trade result."""
        try:
            if successful:
                self.trading_metrics['successful_trades'] += 1
            else:
                self.trading_metrics['failed_trades'] += 1
            
            # Update PnL
            self.trading_metrics['total_pnl'] += pnl
            self.trading_metrics['daily_pnl'] += pnl
            self.strategy_metrics[strategy]['pnl'] += pnl
            
            # Update drawdown
            if pnl < 0:
                self.trading_metrics['current_drawdown'] += abs(pnl)
                self.trading_metrics['max_drawdown'] = max(
                    self.trading_metrics['max_drawdown'],
                    self.trading_metrics['current_drawdown']
                )
            else:
                self.trading_metrics['current_drawdown'] = max(0, self.trading_metrics['current_drawdown'] - pnl)
            
            self.logger.log(f"💰 Trade result: {strategy} PnL: {pnl:.2f} ({'✅' if successful else '❌'})")
            
        except Exception as e:
            self.logger.log(f"❌ Error recording trade result: {str(e)}")
    
    def record_error(self, error_type: str, error_message: str, strategy: str = None):
        """Record error occurrence."""
        try:
            error_entry = {
                'timestamp': datetime.now(),
                'type': error_type,
                'message': error_message,
                'strategy': strategy
            }
            
            self.error_log.append(error_entry)
            self.logger.log(f"❌ Error recorded: {error_type} - {error_message}")
            
        except Exception as e:
            self.logger.log(f"❌ Error recording error: {str(e)}")
    
    def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data."""
        try:
            # Get performance data
            perf_summary = self.performance_monitor.get_performance_summary()
            
            # Calculate averages
            avg_signal_latency = sum(self.signal_latencies) / len(self.signal_latencies) if self.signal_latencies else 0
            avg_execution_time = sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
            
            # Calculate overall winrate
            total_executed = self.trading_metrics['executed_trades']
            total_successful = self.trading_metrics['successful_trades']
            overall_winrate = (total_successful / total_executed * 100) if total_executed > 0 else 0
            
            # Recent errors
            recent_errors = [
                {
                    'timestamp': err['timestamp'].strftime('%H:%M:%S'),
                    'type': err['type'],
                    'message': err['message'][:50] + '...' if len(err['message']) > 50 else err['message']
                }
                for err in list(self.error_log)[-5:]
            ]
            
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'trading_summary': {
                    'total_signals': self.trading_metrics['total_signals'],
                    'executed_trades': self.trading_metrics['executed_trades'],
                    'overall_winrate': f"{overall_winrate:.1f}%",
                    'total_pnl': f"{self.trading_metrics['total_pnl']:.2f}",
                    'daily_pnl': f"{self.trading_metrics['daily_pnl']:.2f}",
                    'current_drawdown': f"{self.trading_metrics['current_drawdown']:.2f}",
                    'max_drawdown': f"{self.trading_metrics['max_drawdown']:.2f}"
                },
                'performance_metrics': {
                    'avg_signal_latency': f"{avg_signal_latency*1000:.1f}ms",
                    'avg_execution_time': f"{avg_execution_time*1000:.1f}ms",
                    'memory_usage': perf_summary['memory']['current'],
                    'cpu_usage': perf_summary['cpu']['current'],
                    'uptime': perf_summary['uptime']
                },
                'strategy_performance': dict(self.strategy_metrics),
                'recent_errors': recent_errors,
                'health_status': perf_summary['health_status']
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error getting dashboard data: {str(e)}")
            return {'error': str(e)}
    
    def print_dashboard(self):
        """Print dashboard to console."""
        try:
            data = self.get_dashboard_data()
            
            print("\n" + "="*60)
            print("🚀 MT5 TRADING BOT - LIVE DASHBOARD")
            print("="*60)
            print(f"📅 {data['timestamp']}")
            print(f"🏥 Health: {data['health_status']}")
            
            # Trading summary
            trading = data['trading_summary']
            print(f"\n📊 TRADING SUMMARY:")
            print(f"   Signals: {trading['total_signals']} | Executed: {trading['executed_trades']} | Winrate: {trading['overall_winrate']}")
            print(f"   Total PnL: {trading['total_pnl']} | Daily: {trading['daily_pnl']} | Drawdown: {trading['current_drawdown']}")
            
            # Performance metrics
            perf = data['performance_metrics']
            print(f"\n⚡ PERFORMANCE:")
            print(f"   Signal Latency: {perf['avg_signal_latency']} | Execution: {perf['avg_execution_time']}")
            print(f"   Memory: {perf['memory_usage']} | CPU: {perf['cpu_usage']} | Uptime: {perf['uptime']}")
            
            # Strategy performance
            print(f"\n🎯 STRATEGY PERFORMANCE:")
            for strategy, metrics in data['strategy_performance'].items():
                winrate = metrics['winrate']
                pnl = metrics['pnl']
                signals = metrics['signals']
                executed = metrics['executed']
                print(f"   {strategy}: {signals} signals, {executed} executed, {winrate:.1f}% winrate, PnL: {pnl:.2f}")
            
            # Recent errors
            if data['recent_errors']:
                print(f"\n❌ RECENT ERRORS:")
                for error in data['recent_errors']:
                    print(f"   {error['timestamp']} - {error['type']}: {error['message']}")
            
            print("="*60 + "\n")
            
        except Exception as e:
            self.logger.log(f"❌ Error printing dashboard: {str(e)}")
    
    def export_dashboard_data(self, filepath: str) -> bool:
        """Export dashboard data to JSON file."""
        try:
            data = self.get_dashboard_data()
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.log(f"✅ Dashboard data exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Failed to export dashboard data: {str(e)}")
            return False
    
    def _update_loop(self):
        """Background update loop for dashboard."""
        while self.dashboard_active:
            try:
                # Print dashboard every 60 seconds
                if time.time() - self.last_update > 60:
                    self.print_dashboard()
                    self.last_update = time.time()
                
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                self.logger.log(f"❌ Dashboard update error: {str(e)}")
                time.sleep(30)
    
    def stop_monitoring(self):
        """Stop monitoring dashboard."""
        self.dashboard_active = False
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=5)


class TelegramAlerting:
    """Telegram notifications for critical trading events."""
    
    def __init__(self, logger, bot_token: str = None, chat_id: str = None):
        """Initialize Telegram alerting."""
        self.logger = logger
        self.bot_token = bot_token
        self.chat_id = chat_id
        
        # Alert thresholds
        self.LATENCY_THRESHOLD = 500  # 500ms
        self.DRAWDOWN_THRESHOLD = 100  # $100
        self.ERROR_COUNT_THRESHOLD = 5  # 5 errors in 10 minutes
        
        # Rate limiting
        self.last_alert_times = defaultdict(float)
        self.ALERT_COOLDOWN = 300  # 5 minutes between similar alerts
        
        # Error tracking for alerting
        self.recent_errors = deque(maxlen=20)
        
        self.enabled = bool(bot_token and chat_id)
        
        if self.enabled:
            self.logger.log("✅ Telegram Alerting initialized")
        else:
            self.logger.log("⚠️ Telegram Alerting disabled (no token/chat_id)")
    
    def send_alert(self, message: str, alert_type: str = "INFO") -> bool:
        """Send Telegram alert message."""
        if not self.enabled:
            return False
        
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_alert_times[alert_type] < self.ALERT_COOLDOWN:
                return False
            
            # Format message
            emoji_map = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "CRITICAL": "🚨",
                "SUCCESS": "✅"
            }
            
            emoji = emoji_map.get(alert_type, "📢")
            formatted_message = f"{emoji} MT5 Bot Alert\n\n{message}\n\nTime: {datetime.now().strftime('%H:%M:%S')}"
            
            # Send via Telegram API
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': formatted_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.last_alert_times[alert_type] = current_time
                self.logger.log(f"✅ Telegram alert sent: {alert_type}")
                return True
            else:
                self.logger.log(f"❌ Telegram alert failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.log(f"❌ Error sending Telegram alert: {str(e)}")
            return False
    
    def alert_high_latency(self, strategy: str, latency_ms: float):
        """Alert for high latency detection."""
        if latency_ms > self.LATENCY_THRESHOLD:
            message = f"🐌 High Latency Alert\n\nStrategy: {strategy}\nLatency: {latency_ms:.1f}ms\nThreshold: {self.LATENCY_THRESHOLD}ms"
            self.send_alert(message, "WARNING")
    
    def alert_repeated_errors(self, error_type: str, count: int):
        """Alert for repeated errors."""
        message = f"🔄 Repeated Error Alert\n\nError Type: {error_type}\nOccurrences: {count}\nTime Window: 10 minutes"
        self.send_alert(message, "ERROR")
    
    def alert_high_drawdown(self, current_drawdown: float, max_drawdown: float):
        """Alert for high drawdown."""
        if current_drawdown > self.DRAWDOWN_THRESHOLD:
            message = f"📉 High Drawdown Alert\n\nCurrent: ${current_drawdown:.2f}\nMax: ${max_drawdown:.2f}\nThreshold: ${self.DRAWDOWN_THRESHOLD}"
            self.send_alert(message, "CRITICAL")
    
    def alert_trading_stopped(self, reason: str):
        """Alert when trading is stopped."""
        message = f"⏹️ Trading Stopped\n\nReason: {reason}\nTime: {datetime.now().strftime('%H:%M:%S')}"
        self.send_alert(message, "CRITICAL")
    
    def alert_connection_lost(self, duration_minutes: float):
        """Alert for MT5 connection loss."""
        message = f"🔌 Connection Lost\n\nMT5 connection down for {duration_minutes:.1f} minutes\nAttempting reconnection..."
        self.send_alert(message, "ERROR")
    
    def alert_daily_summary(self, dashboard_data: Dict):
        """Send daily trading summary."""
        try:
            trading = dashboard_data['trading_summary']
            perf = dashboard_data['performance_metrics']
            
            message = f"""📊 Daily Trading Summary
            
Signals: {trading['total_signals']}
Executed: {trading['executed_trades']}
Winrate: {trading['overall_winrate']}
Daily PnL: {trading['daily_pnl']}

Performance:
Memory: {perf['memory_usage']}
CPU: {perf['cpu_usage']}
Uptime: {perf['uptime']}

Health: {dashboard_data['health_status']}"""
            
            self.send_alert(message, "INFO")
            
        except Exception as e:
            self.logger.log(f"❌ Error sending daily summary: {str(e)}")
    
    def record_error_for_alerting(self, error_type: str, error_message: str):
        """Record error for potential alerting."""
        try:
            self.recent_errors.append({
                'timestamp': datetime.now(),
                'type': error_type,
                'message': error_message
            })
            
            # Check for repeated errors
            recent_count = sum(1 for err in self.recent_errors 
                             if err['type'] == error_type and 
                             datetime.now() - err['timestamp'] < timedelta(minutes=10))
            
            if recent_count >= self.ERROR_COUNT_THRESHOLD:
                self.alert_repeated_errors(error_type, recent_count)
                
        except Exception as e:
            self.logger.log(f"❌ Error recording error for alerting: {str(e)}")