"""
Trading Sessions Module
Manages trading sessions and session-aware adjustments.
"""

import datetime
from typing import Dict, Any, Optional
import threading

from config import *


class SessionManager:
    """Manages trading sessions and session-based adjustments."""
    
    def __init__(self, logger):
        """Initialize session manager."""
        self.logger = logger
        self.current_session = None
        self.session_lock = threading.Lock()
        self.session_data = {
            "start_time": None,
            "start_balance": 0.0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_profit": 0.0,
            "daily_orders": 0,
            "daily_profit": 0.0,
            "last_balance": 0.0,
            "session_equity": 0.0,
            "max_equity": 0.0
        }
        
    def initialize(self) -> None:
        """Initialize session manager."""
        try:
            self.session_data["start_time"] = datetime.datetime.now()
            self.logger.log("✅ Session Manager initialized")
        except Exception as e:
            self.logger.log(f"❌ Session Manager initialization failed: {str(e)}")
    
    def get_current_session(self) -> Dict[str, Any]:
        """
        Get current trading session based on UTC time.
        
        Returns:
            Dict with current session information
        """
        with self.session_lock:
            try:
                utc_now = datetime.datetime.utcnow()
                current_time = utc_now.strftime("%H:%M")
                current_hour = utc_now.hour
                current_minute = utc_now.minute
                current_time_minutes = current_hour * 60 + current_minute
                
                # Check each session
                for session_name, session_config in TRADING_SESSIONS.items():
                    if self._is_time_in_session(current_time_minutes, session_config):
                        session_info = session_config.copy()
                        session_info["name"] = session_name
                        session_info["settings"] = SESSION_SETTINGS.get(session_name, {})
                        
                        if self.current_session != session_name:
                            self.current_session = session_name
                            self.logger.log(f"📅 Session changed to: {session_name}")
                        
                        return session_info
                
                # Default session if none match
                default_session = TRADING_SESSIONS["London"].copy()
                default_session["name"] = "London"
                default_session["settings"] = SESSION_SETTINGS["London"]
                return default_session
                
            except Exception as e:
                self.logger.log(f"❌ Error getting current session: {str(e)}")
                # Return default session on error
                default_session = TRADING_SESSIONS["London"].copy()
                default_session["name"] = "London"
                default_session["settings"] = SESSION_SETTINGS["London"]
                return default_session
    
    def _is_time_in_session(self, current_time_minutes: int, session_config: Dict[str, Any]) -> bool:
        """
        Check if current time is within session hours.
        
        Args:
            current_time_minutes: Current time in minutes from midnight
            session_config: Session configuration
            
        Returns:
            bool: True if time is in session
        """
        try:
            start_time = session_config["start"]
            end_time = session_config["end"]
            
            # Parse start and end times
            start_hour, start_minute = map(int, start_time.split(":"))
            end_hour, end_minute = map(int, end_time.split(":"))
            
            start_minutes = start_hour * 60 + start_minute
            end_minutes = end_hour * 60 + end_minute
            
            # Handle overnight sessions (e.g., Asia session 21:00 - 06:00)
            if start_minutes > end_minutes:
                # Session crosses midnight
                return current_time_minutes >= start_minutes or current_time_minutes <= end_minutes
            else:
                # Normal session within same day
                return start_minutes <= current_time_minutes <= end_minutes
                
        except Exception as e:
            self.logger.log(f"❌ Error checking session time: {str(e)}")
            return False
    
    def adjust_strategy_for_session(self, base_lot: float, base_tp: float, base_sl: float, 
                                   session_info: Dict[str, Any]) -> tuple:
        """
        Adjust trading parameters based on current session.
        
        Args:
            base_lot: Base lot size
            base_tp: Base take profit
            base_sl: Base stop loss
            session_info: Current session information
            
        Returns:
            Tuple of (adjusted_lot, adjusted_tp, adjusted_sl)
        """
        try:
            settings = session_info.get("settings", {})
            
            # Apply session multipliers
            lot_multiplier = settings.get("lot_multiplier", 1.0)
            tp_multiplier = settings.get("tp_multiplier", 1.0)
            sl_multiplier = settings.get("sl_multiplier", 1.0)
            
            adjusted_lot = base_lot * lot_multiplier
            adjusted_tp = base_tp * tp_multiplier
            adjusted_sl = base_sl * sl_multiplier
            
            # Apply volatility-based adjustments
            volatility = session_info.get("volatility", "medium")
            if volatility == "very_high":
                adjusted_sl *= 1.2  # Wider stops for high volatility
                adjusted_tp *= 1.3  # Higher targets
            elif volatility == "high":
                adjusted_sl *= 1.1
                adjusted_tp *= 1.2
            elif volatility == "low":
                adjusted_sl *= 0.9
                adjusted_tp *= 0.8
            
            self.logger.log(f"📊 Session adjustments applied: " +
                          f"Lot {base_lot:.3f} -> {adjusted_lot:.3f}, " +
                          f"TP {base_tp:.1f} -> {adjusted_tp:.1f}, " +
                          f"SL {base_sl:.1f} -> {adjusted_sl:.1f}")
            
            return adjusted_lot, adjusted_tp, adjusted_sl
            
        except Exception as e:
            self.logger.log(f"❌ Error adjusting strategy for session: {str(e)}")
            return base_lot, base_tp, base_sl
    
    def update_session_data(self) -> None:
        """Update session performance data."""
        try:
            # This would typically update performance metrics
            # For now, just log that we're updating
            pass
        except Exception as e:
            self.logger.log(f"❌ Error updating session data: {str(e)}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get current session performance summary.
        
        Returns:
            Dict with session performance data
        """
        try:
            current_time = datetime.datetime.now()
            session_duration = None
            
            if self.session_data["start_time"]:
                duration = current_time - self.session_data["start_time"]
                session_duration = str(duration).split('.')[0]  # Remove microseconds
            
            return {
                "session_name": self.current_session,
                "start_time": self.session_data["start_time"],
                "duration": session_duration,
                "total_trades": self.session_data["total_trades"],
                "winning_trades": self.session_data["winning_trades"],
                "losing_trades": self.session_data["losing_trades"],
                "win_rate": (self.session_data["winning_trades"] / max(self.session_data["total_trades"], 1)) * 100,
                "total_profit": self.session_data["total_profit"],
                "daily_profit": self.session_data["daily_profit"]
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error getting session summary: {str(e)}")
            return {}
    
    def reset_session_data(self) -> None:
        """Reset session data for new session."""
        try:
            with self.session_lock:
                self.session_data.update({
                    "start_time": datetime.datetime.now(),
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "total_profit": 0.0,
                    "daily_orders": 0,
                    "daily_profit": 0.0
                })
                self.logger.log("🔄 Session data reset")
        except Exception as e:
            self.logger.log(f"❌ Error resetting session data: {str(e)}")
    
    def is_session_active(self, session_name: str) -> bool:
        """
        Check if a specific session is currently active.
        
        Args:
            session_name: Name of session to check
            
        Returns:
            bool: True if session is active
        """
        try:
            current_session = self.get_current_session()
            return current_session.get("name") == session_name
        except Exception as e:
            self.logger.log(f"❌ Error checking session activity: {str(e)}")
            return False
    
    def get_preferred_pairs_for_session(self, session_name: str = None) -> list:
        """
        Get preferred trading pairs for current or specified session.
        
        Args:
            session_name: Session name (optional, uses current if not specified)
            
        Returns:
            List of preferred symbol names
        """
        try:
            if session_name is None:
                session_info = self.get_current_session()
                session_name = session_info.get("name", "London")
            
            session_config = TRADING_SESSIONS.get(session_name)
            if session_config:
                return session_config.get("preferred_pairs", POPULAR_SYMBOLS[:5])
            else:
                return POPULAR_SYMBOLS[:5]
                
        except Exception as e:
            self.logger.log(f"❌ Error getting preferred pairs: {str(e)}")
            return POPULAR_SYMBOLS[:5]
