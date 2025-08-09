"""
Fail-Safe & Recovery Module
Comprehensive safety mechanisms and recovery procedures for live trading
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import json
import os


class FailSafeManager:
    """Manages fail-safe mechanisms and emergency procedures."""
    
    def __init__(self, logger, connection_manager, order_manager):
        """Initialize fail-safe manager."""
        self.logger = logger
        self.connection_manager = connection_manager
        self.order_manager = order_manager
        
        # Safety parameters
        self.max_drawdown_percent = 10.0  # 10% max drawdown
        self.max_daily_loss = 500.0  # $500 max daily loss
        self.max_open_positions = 10  # Maximum open positions
        self.emergency_stop_triggered = False
        
        # Monitoring state
        self.account_balance = 0.0
        self.daily_pnl = 0.0
        self.current_drawdown = 0.0
        self.open_positions_count = 0
        
        # Recovery mechanisms
        self.auto_pause_active = False
        self.pause_reason = ""
        self.pause_start_time = None
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        
        # Monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._safety_monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.log("✅ Fail-Safe Manager initialized")
    
    def update_account_status(self, balance: float, equity: float, positions: List[Dict]):
        """Update account status for monitoring."""
        try:
            self.account_balance = balance
            self.open_positions_count = len(positions)
            
            # Calculate current P&L from positions
            current_pnl = sum(pos.get('profit', 0) for pos in positions)
            
            # Update drawdown
            if current_pnl < 0:
                self.current_drawdown = abs(current_pnl)
            
            # Calculate daily P&L (simplified - would need actual daily tracking)
            self.daily_pnl = current_pnl
            
        except Exception as e:
            self.logger.log(f"❌ Error updating account status: {str(e)}")
    
    def check_safety_conditions(self) -> Tuple[bool, str]:
        """Check all safety conditions and return status."""
        try:
            # Check drawdown percentage
            if self.account_balance > 0:
                drawdown_percent = (self.current_drawdown / self.account_balance) * 100
                if drawdown_percent > self.max_drawdown_percent:
                    return False, f"Drawdown limit exceeded: {drawdown_percent:.1f}% > {self.max_drawdown_percent}%"
            
            # Check daily loss limit
            if self.daily_pnl < -self.max_daily_loss:
                return False, f"Daily loss limit exceeded: ${abs(self.daily_pnl):.2f} > ${self.max_daily_loss}"
            
            # Check position count
            if self.open_positions_count > self.max_open_positions:
                return False, f"Too many open positions: {self.open_positions_count} > {self.max_open_positions}"
            
            # Check if emergency stop is active
            if self.emergency_stop_triggered:
                return False, "Emergency stop is active"
            
            return True, "All safety conditions met"
            
        except Exception as e:
            self.logger.log(f"❌ Error checking safety conditions: {str(e)}")
            return False, f"Safety check error: {str(e)}"
    
    def trigger_emergency_stop(self, reason: str = "Manual trigger") -> bool:
        """Trigger emergency stop procedure."""
        try:
            self.emergency_stop_triggered = True
            self.logger.log(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")
            
            # Close all open positions
            success = self._close_all_positions()
            
            # Pause trading
            self._pause_trading(f"Emergency stop: {reason}")
            
            return success
            
        except Exception as e:
            self.logger.log(f"❌ Error triggering emergency stop: {str(e)}")
            return False
    
    def auto_pause_trading(self, reason: str) -> bool:
        """Automatically pause trading with reason."""
        try:
            if self.auto_pause_active:
                return True  # Already paused
            
            self.auto_pause_active = True
            self.pause_reason = reason
            self.pause_start_time = datetime.now()
            
            self.logger.log(f"⏸️ Auto-pause activated: {reason}")
            
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error auto-pausing trading: {str(e)}")
            return False
    
    def resume_trading(self, force: bool = False) -> bool:
        """Resume trading after pause."""
        try:
            if not self.auto_pause_active and not force:
                return True  # Not paused
            
            # Check safety conditions before resuming
            safe, reason = self.check_safety_conditions()
            if not safe and not force:
                self.logger.log(f"⚠️ Cannot resume trading: {reason}")
                return False
            
            self.auto_pause_active = False
            self.pause_reason = ""
            self.pause_start_time = None
            
            # Reset emergency stop if forced
            if force:
                self.emergency_stop_triggered = False
            
            self.logger.log("▶️ Trading resumed")
            
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error resuming trading: {str(e)}")
            return False
    
    def _close_all_positions(self) -> bool:
        """Close all open positions immediately."""
        try:
            if not hasattr(self.order_manager, 'close_all_positions'):
                self.logger.log("⚠️ Order manager doesn't support close_all_positions")
                return False
            
            success = self.order_manager.close_all_positions()
            
            if success:
                self.logger.log("✅ All positions closed successfully")
            else:
                self.logger.log("❌ Failed to close some positions")
            
            return success
            
        except Exception as e:
            self.logger.log(f"❌ Error closing all positions: {str(e)}")
            return False
    
    def _pause_trading(self, reason: str):
        """Internal pause trading mechanism."""
        try:
            self.auto_pause_active = True
            self.pause_reason = reason
            self.pause_start_time = datetime.now()
            
            self.logger.log(f"⏸️ Trading paused: {reason}")
            
        except Exception as e:
            self.logger.log(f"❌ Error pausing trading: {str(e)}")
    
    def _safety_monitor_loop(self):
        """Background safety monitoring loop."""
        while self.monitoring_active:
            try:
                # Check safety conditions every 30 seconds
                safe, reason = self.check_safety_conditions()
                
                if not safe and not self.auto_pause_active and not self.emergency_stop_triggered:
                    # Trigger automatic safety measures
                    if "drawdown" in reason.lower() or "loss" in reason.lower():
                        self.trigger_emergency_stop(reason)
                    else:
                        self.auto_pause_trading(reason)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.log(f"❌ Safety monitor error: {str(e)}")
                time.sleep(60)
    
    def get_safety_status(self) -> Dict:
        """Get comprehensive safety status."""
        try:
            safe, reason = self.check_safety_conditions()
            
            pause_duration = None
            if self.pause_start_time:
                pause_duration = datetime.now() - self.pause_start_time
            
            return {
                'safety_status': 'SAFE' if safe else 'UNSAFE',
                'safety_reason': reason,
                'emergency_stop_active': self.emergency_stop_triggered,
                'auto_pause_active': self.auto_pause_active,
                'pause_reason': self.pause_reason,
                'pause_duration': str(pause_duration) if pause_duration else None,
                'account_balance': self.account_balance,
                'current_drawdown': self.current_drawdown,
                'daily_pnl': self.daily_pnl,
                'open_positions': self.open_positions_count,
                'max_drawdown_percent': self.max_drawdown_percent,
                'max_daily_loss': self.max_daily_loss,
                'max_open_positions': self.max_open_positions
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error getting safety status: {str(e)}")
            return {'error': str(e)}
    
    def stop_monitoring(self):
        """Stop safety monitoring."""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)


class ConfigurationReloader:
    """Handles dynamic configuration reloading without restart."""
    
    def __init__(self, logger, config_manager):
        """Initialize configuration reloader."""
        self.logger = logger
        self.config_manager = config_manager
        
        # Configuration state
        self.last_config_hash = None
        self.reload_callbacks = []
        
        # File watching
        self.config_file_path = getattr(config_manager, 'config_file', 'config/bot_settings.json')
        self.last_modified = 0
        
        self.logger.log("✅ Configuration Reloader initialized")
    
    def register_reload_callback(self, callback_func):
        """Register callback function for configuration reload."""
        self.reload_callbacks.append(callback_func)
        self.logger.log(f"✅ Reload callback registered: {callback_func.__name__}")
    
    def check_config_changes(self) -> bool:
        """Check if configuration file has been modified."""
        try:
            if not os.path.exists(self.config_file_path):
                return False
            
            current_modified = os.path.getmtime(self.config_file_path)
            
            if current_modified > self.last_modified:
                self.last_modified = current_modified
                return True
            
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error checking config changes: {str(e)}")
            return False
    
    def reload_configuration(self) -> bool:
        """Reload configuration and notify components."""
        try:
            # Load new configuration
            new_config = self.config_manager.load_config()
            
            if not new_config:
                self.logger.log("❌ Failed to load new configuration")
                return False
            
            # Calculate configuration hash for change detection
            config_str = json.dumps(new_config, sort_keys=True)
            import hashlib
            new_hash = hashlib.md5(config_str.encode()).hexdigest()
            
            if new_hash == self.last_config_hash:
                return True  # No changes
            
            self.last_config_hash = new_hash
            
            # Notify all registered callbacks
            for callback in self.reload_callbacks:
                try:
                    callback(new_config)
                    self.logger.log(f"✅ Configuration reloaded for: {callback.__name__}")
                except Exception as e:
                    self.logger.log(f"❌ Error in reload callback {callback.__name__}: {str(e)}")
            
            self.logger.log("✅ Configuration successfully reloaded")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error reloading configuration: {str(e)}")
            return False
    
    def force_reload(self) -> bool:
        """Force configuration reload regardless of file changes."""
        try:
            self.last_config_hash = None  # Force reload
            return self.reload_configuration()
            
        except Exception as e:
            self.logger.log(f"❌ Error forcing config reload: {str(e)}")
            return False


class SelfHealingSystem:
    """Self-healing mechanisms for automatic recovery."""
    
    def __init__(self, logger, connection_manager, fail_safe_manager):
        """Initialize self-healing system."""
        self.logger = logger
        self.connection_manager = connection_manager
        self.fail_safe = fail_safe_manager
        
        # Healing parameters
        self.connection_check_interval = 60  # 1 minute
        self.max_reconnection_attempts = 5
        self.reconnection_delay = 30  # 30 seconds
        
        # State tracking
        self.last_connection_check = time.time()
        self.connection_failures = 0
        self.healing_active = True
        
        # Healing thread
        self.healing_thread = threading.Thread(target=self._healing_loop, daemon=True)
        self.healing_thread.start()
        
        self.logger.log("✅ Self-Healing System initialized")
    
    def check_connection_health(self) -> Tuple[bool, str]:
        """Check MT5 connection health."""
        try:
            if not hasattr(self.connection_manager, 'check_connection'):
                return True, "Connection check not available"
            
            is_connected = self.connection_manager.check_connection()
            
            if is_connected:
                self.connection_failures = 0
                return True, "Connection healthy"
            else:
                self.connection_failures += 1
                return False, f"Connection down (failure #{self.connection_failures})"
                
        except Exception as e:
            self.connection_failures += 1
            return False, f"Connection check error: {str(e)}"
    
    def attempt_connection_recovery(self) -> bool:
        """Attempt to recover MT5 connection."""
        try:
            if self.connection_failures > self.max_reconnection_attempts:
                self.logger.log(f"🚨 Max reconnection attempts exceeded ({self.max_reconnection_attempts})")
                return False
            
            self.logger.log(f"🔄 Attempting connection recovery (attempt {self.connection_failures})")
            
            # Attempt reconnection
            if hasattr(self.connection_manager, 'connect'):
                success = self.connection_manager.connect()
                
                if success:
                    self.logger.log("✅ Connection recovery successful")
                    self.connection_failures = 0
                    return True
                else:
                    self.logger.log("❌ Connection recovery failed")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error during connection recovery: {str(e)}")
            return False
    
    def perform_system_health_check(self) -> Dict:
        """Perform comprehensive system health check."""
        try:
            health_report = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'overall_status': 'HEALTHY',
                'issues': [],
                'recommendations': []
            }
            
            # Check connection
            conn_healthy, conn_reason = self.check_connection_health()
            if not conn_healthy:
                health_report['issues'].append(f"Connection: {conn_reason}")
                health_report['overall_status'] = 'DEGRADED'
            
            # Check safety status
            safety_status = self.fail_safe.get_safety_status()
            if safety_status.get('safety_status') != 'SAFE':
                health_report['issues'].append(f"Safety: {safety_status.get('safety_reason')}")
                health_report['overall_status'] = 'CRITICAL'
            
            # Generate recommendations
            if health_report['issues']:
                if any('connection' in issue.lower() for issue in health_report['issues']):
                    health_report['recommendations'].append("Check MT5 platform and internet connection")
                
                if any('safety' in issue.lower() for issue in health_report['issues']):
                    health_report['recommendations'].append("Review risk management settings")
            
            return health_report
            
        except Exception as e:
            self.logger.log(f"❌ Error performing health check: {str(e)}")
            return {'error': str(e)}
    
    def _healing_loop(self):
        """Background self-healing loop."""
        while self.healing_active:
            try:
                current_time = time.time()
                
                # Check connection health periodically
                if current_time - self.last_connection_check > self.connection_check_interval:
                    conn_healthy, reason = self.check_connection_health()
                    
                    if not conn_healthy:
                        # Attempt recovery
                        time.sleep(self.reconnection_delay)
                        self.attempt_connection_recovery()
                    
                    self.last_connection_check = current_time
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.log(f"❌ Self-healing loop error: {str(e)}")
                time.sleep(60)
    
    def stop_healing(self):
        """Stop self-healing system."""
        self.healing_active = False
        if self.healing_thread.is_alive():
            self.healing_thread.join(timeout=5)