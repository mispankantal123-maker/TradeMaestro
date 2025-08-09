"""
News Filter Module
Filters high-impact news events to avoid trading during volatile periods.
"""

import datetime
from typing import List, Dict, Any, Optional, Tuple
import requests
import time

from config import *


class NewsFilter:
    """Filters high-impact news events for trading decisions."""
    
    def __init__(self, logger):
        """Initialize news filter."""
        self.logger = logger
        self.news_cache = {}
        self.cache_duration = 3600  # Cache for 1 hour
        self.last_api_call = 0
        self.api_rate_limit = 60  # Minimum seconds between API calls
        
    def is_high_impact_news_time(self) -> bool:
        """
        Check if current time is during high-impact news.
        
        Returns:
            bool: True if high-impact news time
        """
        try:
            utc_now = datetime.datetime.utcnow()
            
            # Check time-based news schedule
            if self._is_scheduled_news_time(utc_now):
                return True
            
            # Check API-based news if available
            if self._is_api_news_time(utc_now):
                return True
            
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error checking news time: {str(e)}")
            return False  # Default to allow trading if check fails
    
    def _is_scheduled_news_time(self, utc_time: datetime.datetime) -> bool:
        """
        Check against pre-configured news schedule.
        
        Args:
            utc_time: Current UTC time
            
        Returns:
            bool: True if scheduled news time
        """
        try:
            current_hour = utc_time.hour
            current_minute = utc_time.minute
            current_time_minutes = current_hour * 60 + current_minute
            day_of_week = utc_time.weekday()  # 0=Monday, 6=Sunday
            
            # Check daily critical times
            for start_h, start_m, end_h, end_m in HIGH_IMPACT_NEWS_TIMES:
                start_minutes = start_h * 60 + start_m
                end_minutes = end_h * 60 + end_m
                
                if start_minutes <= current_time_minutes <= end_minutes:
                    self.logger.log(f"⚠️ High-impact news time detected: {current_hour:02d}:{current_minute:02d} UTC")
                    return True
            
            # Check weekly specific times
            weekly_times = WEEKLY_NEWS_TIMES.get(day_of_week, [])
            for start_h, start_m, end_h, end_m in weekly_times:
                start_minutes = start_h * 60 + start_m
                end_minutes = end_h * 60 + end_m
                
                if start_minutes <= current_time_minutes <= end_minutes:
                    self.logger.log(f"⚠️ Weekly high-impact news time detected: {current_hour:02d}:{current_minute:02d} UTC")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error checking scheduled news: {str(e)}")
            return False
    
    def _is_api_news_time(self, utc_time: datetime.datetime) -> bool:
        """
        Check high-impact news via API (if configured).
        
        Args:
            utc_time: Current UTC time
            
        Returns:
            bool: True if API indicates news time
        """
        try:
            # Rate limiting for API calls
            current_time = time.time()
            if current_time - self.last_api_call < self.api_rate_limit:
                return False
            
            # For now, return False as we don't have a specific news API configured
            # This can be extended with actual news API integration
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error checking API news: {str(e)}")
            return False
    
    def get_upcoming_news_events(self, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """
        Get upcoming high-impact news events.
        
        Args:
            hours_ahead: Hours to look ahead
            
        Returns:
            List of news event dictionaries
        """
        try:
            events = []
            utc_now = datetime.datetime.utcnow()
            
            # Generate schedule-based events for the next period
            for day_offset in range(hours_ahead // 24 + 1):
                check_date = utc_now + datetime.timedelta(days=day_offset)
                
                # Daily events
                for start_h, start_m, end_h, end_m in HIGH_IMPACT_NEWS_TIMES:
                    event_time = datetime.datetime(
                        check_date.year, check_date.month, check_date.day,
                        start_h, start_m, 0
                    )
                    
                    if utc_now <= event_time <= utc_now + datetime.timedelta(hours=hours_ahead):
                        events.append({
                            'time': event_time,
                            'title': 'High-Impact News Period',
                            'impact': 'HIGH',
                            'currency': 'Multiple',
                            'type': 'Scheduled'
                        })
                
                # Weekly events
                day_of_week = check_date.weekday()
                weekly_times = WEEKLY_NEWS_TIMES.get(day_of_week, [])
                for start_h, start_m, end_h, end_m in weekly_times:
                    event_time = datetime.datetime(
                        check_date.year, check_date.month, check_date.day,
                        start_h, start_m, 0
                    )
                    
                    if utc_now <= event_time <= utc_now + datetime.timedelta(hours=hours_ahead):
                        event_name = self._get_weekly_event_name(day_of_week, start_h)
                        events.append({
                            'time': event_time,
                            'title': event_name,
                            'impact': 'HIGH',
                            'currency': 'USD',
                            'type': 'Weekly'
                        })
            
            # Sort by time
            events.sort(key=lambda x: x['time'])
            
            return events
            
        except Exception as e:
            self.logger.log(f"❌ Error getting upcoming news: {str(e)}")
            return []
    
    def _get_weekly_event_name(self, day_of_week: int, hour: int) -> str:
        """Get descriptive name for weekly events."""
        if day_of_week == 2 and hour == 13:  # Wednesday
            return "FOMC Minutes Release"
        elif day_of_week == 4 and hour == 12:  # Friday
            return "Non-Farm Payrolls & Major Economic Data"
        else:
            return "Weekly High-Impact Event"
    
    def should_avoid_trading(self, symbol: str = None, strategy: str = None) -> Tuple[bool, str]:
        """
        Comprehensive check if trading should be avoided.
        
        Args:
            symbol: Trading symbol (optional)
            strategy: Trading strategy (optional)
            
        Returns:
            Tuple of (should_avoid, reason)
        """
        try:
            # Check high-impact news
            if self.is_high_impact_news_time():
                return True, "High-impact news period"
            
            # Strategy-specific checks
            if strategy == "HFT":
                # HFT is more sensitive to news
                upcoming_events = self.get_upcoming_news_events(hours_ahead=2)
                if upcoming_events:
                    return True, "Upcoming high-impact news (HFT sensitivity)"
            
            # Symbol-specific checks
            if symbol:
                if any(currency in symbol.upper() for currency in ["USD", "EUR", "GBP"]):
                    # Major currencies are more affected by news
                    upcoming_events = self.get_upcoming_news_events(hours_ahead=1)
                    major_events = [e for e in upcoming_events if e['impact'] == 'HIGH']
                    if major_events:
                        return True, f"Upcoming major currency news in 1 hour"
            
            return False, "No news conflicts detected"
            
        except Exception as e:
            self.logger.log(f"❌ Error in news avoidance check: {str(e)}")
            return False, "News check failed - allowing trading"
    
    def get_news_summary(self) -> Dict[str, Any]:
        """
        Get current news filter status summary.
        
        Returns:
            Dict with news filter status
        """
        try:
            utc_now = datetime.datetime.utcnow()
            
            # Current status
            is_news_time = self.is_high_impact_news_time()
            
            # Upcoming events
            upcoming_events = self.get_upcoming_news_events(hours_ahead=24)
            next_event = upcoming_events[0] if upcoming_events else None
            
            # Time until next event
            time_to_next = None
            if next_event:
                time_diff = next_event['time'] - utc_now
                hours = time_diff.total_seconds() / 3600
                time_to_next = f"{hours:.1f} hours"
            
            return {
                'current_time_utc': utc_now.strftime('%Y-%m-%d %H:%M:%S'),
                'is_news_time': is_news_time,
                'upcoming_events_24h': len(upcoming_events),
                'next_event': next_event,
                'time_to_next_event': time_to_next,
                'cache_size': len(self.news_cache)
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error getting news summary: {str(e)}")
            return {}
    
    def add_custom_news_event(self, event_time: datetime.datetime, title: str, 
                             impact: str = "HIGH", currency: str = "Multiple") -> bool:
        """
        Add custom news event to filter.
        
        Args:
            event_time: Event datetime (UTC)
            title: Event title
            impact: Impact level
            currency: Affected currency
            
        Returns:
            bool: True if added successfully
        """
        try:
            event_key = f"custom_{int(event_time.timestamp())}"
            
            self.news_cache[event_key] = {
                'time': event_time,
                'title': title,
                'impact': impact,
                'currency': currency,
                'type': 'Custom',
                'added_at': datetime.datetime.utcnow()
            }
            
            self.logger.log(f"📰 Custom news event added: {title} at {event_time}")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error adding custom news event: {str(e)}")
            return False
    
    def clear_expired_events(self) -> None:
        """Clear expired news events from cache."""
        try:
            current_time = datetime.datetime.utcnow()
            expired_keys = []
            
            for key, event in self.news_cache.items():
                if 'time' in event and event['time'] < current_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.news_cache[key]
            
            if expired_keys:
                self.logger.log(f"🧹 Cleared {len(expired_keys)} expired news events")
                
        except Exception as e:
            self.logger.log(f"❌ Error clearing expired events: {str(e)}")
    
    def get_market_hours_status(self) -> Dict[str, Any]:
        """
        Get current market hours status for major sessions.
        
        Returns:
            Dict with market hours information
        """
        try:
            utc_now = datetime.datetime.utcnow()
            current_hour = utc_now.hour
            current_minute = utc_now.minute
            current_time_minutes = current_hour * 60 + current_minute
            
            sessions_status = {}
            
            for session_name, session_config in TRADING_SESSIONS.items():
                is_active = self._is_time_in_session_hours(current_time_minutes, session_config)
                sessions_status[session_name] = {
                    'active': is_active,
                    'start': session_config['start'],
                    'end': session_config['end'],
                    'volatility': session_config['volatility']
                }
            
            return {
                'current_time_utc': utc_now.strftime('%H:%M'),
                'sessions': sessions_status
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error getting market hours: {str(e)}")
            return {}
    
    def _is_time_in_session_hours(self, current_time_minutes: int, session_config: Dict[str, Any]) -> bool:
        """Check if time is within session hours."""
        try:
            start_time = session_config["start"]
            end_time = session_config["end"]
            
            start_hour, start_minute = map(int, start_time.split(":"))
            end_hour, end_minute = map(int, end_time.split(":"))
            
            start_minutes = start_hour * 60 + start_minute
            end_minutes = end_hour * 60 + end_minute
            
            if start_minutes > end_minutes:
                return current_time_minutes >= start_minutes or current_time_minutes <= end_minutes
            else:
                return start_minutes <= current_time_minutes <= end_minutes
                
        except Exception as e:
            return False
