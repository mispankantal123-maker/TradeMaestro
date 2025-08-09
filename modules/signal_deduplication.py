"""
Signal Deduplication Module
Prevents duplicate signals and ensures consistent signal quality
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
import hashlib


class SignalDeduplicator:
    """Manages signal deduplication and consistency checking."""
    
    def __init__(self, logger):
        """Initialize signal deduplicator."""
        self.logger = logger
        
        # Signal tracking
        self.recent_signals = defaultdict(list)  # symbol -> list of signal hashes
        self.signal_timestamps = {}  # signal_hash -> timestamp
        self.executed_signals = set()  # Set of executed signal hashes
        
        # Deduplication parameters
        self.SIGNAL_TIMEOUT = 300  # 5 minutes
        self.MIN_SIGNAL_INTERVAL = 30  # 30 seconds between similar signals
        self.MAX_SIGNALS_PER_MINUTE = 5  # Maximum signals per symbol per minute
        
        # Signal similarity thresholds
        self.SIMILARITY_THRESHOLD = 0.8  # 80% similarity threshold
        
        self.logger.log("✅ Signal Deduplicator initialized")
    
    def generate_signal_hash(self, symbol: str, strategy: str, signals: List[str], action: str) -> str:
        """Generate unique hash for signal combination."""
        try:
            # Create content string for hashing
            content = f"{symbol}_{strategy}_{action}_{'_'.join(sorted(signals))}"
            
            # Generate hash
            signal_hash = hashlib.md5(content.encode()).hexdigest()[:12]
            
            return signal_hash
            
        except Exception as e:
            self.logger.log(f"❌ Error generating signal hash: {str(e)}")
            return f"error_{int(time.time())}"
    
    def is_duplicate_signal(self, symbol: str, strategy: str, signals: List[str], action: str) -> Tuple[bool, str]:
        """Check if signal is a duplicate of recent signals."""
        try:
            current_time = time.time()
            signal_hash = self.generate_signal_hash(symbol, strategy, signals, action)
            
            # Clean old signals
            self._clean_old_signals(current_time)
            
            # Check if exact signal already exists
            if signal_hash in self.signal_timestamps:
                last_time = self.signal_timestamps[signal_hash]
                if current_time - last_time < self.MIN_SIGNAL_INTERVAL:
                    return True, f"Duplicate signal within {self.MIN_SIGNAL_INTERVAL}s"
            
            # Check signal rate limiting
            recent_count = self._count_recent_signals(symbol, current_time, 60)  # Last minute
            if recent_count >= self.MAX_SIGNALS_PER_MINUTE:
                return True, f"Rate limit exceeded: {recent_count} signals in last minute"
            
            # Check for similar signals
            similarity_check = self._check_signal_similarity(symbol, strategy, signals, action, current_time)
            if similarity_check[0]:
                return True, similarity_check[1]
            
            # Record this signal
            self.signal_timestamps[signal_hash] = current_time
            self.recent_signals[symbol].append({
                'hash': signal_hash,
                'timestamp': current_time,
                'strategy': strategy,
                'signals': signals,
                'action': action
            })
            
            return False, "Signal is unique"
            
        except Exception as e:
            self.logger.log(f"❌ Error checking duplicate signal: {str(e)}")
            return False, f"Check error: {str(e)}"
    
    def mark_signal_executed(self, symbol: str, strategy: str, signals: List[str], action: str):
        """Mark signal as executed to prevent re-execution."""
        try:
            signal_hash = self.generate_signal_hash(symbol, strategy, signals, action)
            self.executed_signals.add(signal_hash)
            
            self.logger.log(f"✅ Signal marked as executed: {signal_hash[:8]}")
            
        except Exception as e:
            self.logger.log(f"❌ Error marking signal as executed: {str(e)}")
    
    def was_signal_executed(self, symbol: str, strategy: str, signals: List[str], action: str) -> bool:
        """Check if signal was already executed."""
        try:
            signal_hash = self.generate_signal_hash(symbol, strategy, signals, action)
            return signal_hash in self.executed_signals
            
        except Exception as e:
            self.logger.log(f"❌ Error checking signal execution: {str(e)}")
            return False
    
    def _clean_old_signals(self, current_time: float):
        """Clean old signals from memory."""
        try:
            # Clean timestamps
            expired_hashes = []
            for signal_hash, timestamp in self.signal_timestamps.items():
                if current_time - timestamp > self.SIGNAL_TIMEOUT:
                    expired_hashes.append(signal_hash)
            
            for hash_to_remove in expired_hashes:
                del self.signal_timestamps[hash_to_remove]
                self.executed_signals.discard(hash_to_remove)
            
            # Clean symbol signals
            for symbol in self.recent_signals:
                self.recent_signals[symbol] = [
                    signal for signal in self.recent_signals[symbol]
                    if current_time - signal['timestamp'] <= self.SIGNAL_TIMEOUT
                ]
            
        except Exception as e:
            self.logger.log(f"❌ Error cleaning old signals: {str(e)}")
    
    def _count_recent_signals(self, symbol: str, current_time: float, window_seconds: int) -> int:
        """Count recent signals for a symbol within time window."""
        try:
            if symbol not in self.recent_signals:
                return 0
            
            count = 0
            for signal in self.recent_signals[symbol]:
                if current_time - signal['timestamp'] <= window_seconds:
                    count += 1
            
            return count
            
        except Exception as e:
            self.logger.log(f"❌ Error counting recent signals: {str(e)}")
            return 0
    
    def _check_signal_similarity(self, symbol: str, strategy: str, signals: List[str], 
                                action: str, current_time: float) -> Tuple[bool, str]:
        """Check for similar signals in recent history."""
        try:
            if symbol not in self.recent_signals:
                return False, "No recent signals"
            
            for recent_signal in self.recent_signals[symbol]:
                # Only check signals from last 2 minutes
                if current_time - recent_signal['timestamp'] > 120:
                    continue
                
                # Check strategy and action match
                if recent_signal['strategy'] == strategy and recent_signal['action'] == action:
                    # Calculate signal similarity
                    similarity = self._calculate_signal_similarity(signals, recent_signal['signals'])
                    
                    if similarity >= self.SIMILARITY_THRESHOLD:
                        time_diff = current_time - recent_signal['timestamp']
                        return True, f"Similar signal detected (similarity: {similarity:.2f}, {time_diff:.0f}s ago)"
            
            return False, "No similar signals found"
            
        except Exception as e:
            self.logger.log(f"❌ Error checking signal similarity: {str(e)}")
            return False, f"Similarity check error: {str(e)}"
    
    def _calculate_signal_similarity(self, signals1: List[str], signals2: List[str]) -> float:
        """Calculate similarity between two signal lists."""
        try:
            if not signals1 or not signals2:
                return 0.0
            
            # Convert to sets of words for comparison
            words1 = set()
            for signal in signals1:
                words1.update(signal.lower().split())
            
            words2 = set()
            for signal in signals2:
                words2.update(signal.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating signal similarity: {str(e)}")
            return 0.0
    
    def get_deduplication_stats(self) -> Dict:
        """Get deduplication statistics."""
        try:
            current_time = time.time()
            
            # Count signals by symbol
            symbol_counts = {}
            total_signals = 0
            
            for symbol, signal_list in self.recent_signals.items():
                active_signals = [s for s in signal_list if current_time - s['timestamp'] <= 300]
                symbol_counts[symbol] = len(active_signals)
                total_signals += len(active_signals)
            
            # Count executed signals
            executed_count = len(self.executed_signals)
            
            return {
                'total_tracked_signals': total_signals,
                'executed_signals': executed_count,
                'signals_by_symbol': symbol_counts,
                'deduplication_timeout': f"{self.SIGNAL_TIMEOUT}s",
                'min_signal_interval': f"{self.MIN_SIGNAL_INTERVAL}s",
                'max_signals_per_minute': self.MAX_SIGNALS_PER_MINUTE
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error getting deduplication stats: {str(e)}")
            return {'error': str(e)}


class OutlierDetector:
    """Detects and filters outlier signals that may be anomalous."""
    
    def __init__(self, logger):
        """Initialize outlier detector."""
        self.logger = logger
        
        # Signal quality tracking
        self.signal_quality_history = defaultdict(list)  # strategy -> quality scores
        self.signal_success_rates = defaultdict(lambda: {'total': 0, 'successful': 0})
        
        # Outlier detection parameters
        self.MIN_HISTORY_LENGTH = 20  # Minimum signals needed for outlier detection
        self.OUTLIER_THRESHOLD = 2.5  # Standard deviations for outlier detection
        self.SUCCESS_RATE_THRESHOLD = 0.3  # Minimum 30% success rate
        
        self.logger.log("✅ Outlier Detector initialized")
    
    def record_signal_quality(self, strategy: str, quality_score: float):
        """Record signal quality for outlier analysis."""
        try:
            self.signal_quality_history[strategy].append(quality_score)
            
            # Keep last 100 scores
            if len(self.signal_quality_history[strategy]) > 100:
                self.signal_quality_history[strategy] = self.signal_quality_history[strategy][-100:]
            
        except Exception as e:
            self.logger.log(f"❌ Error recording signal quality: {str(e)}")
    
    def record_signal_outcome(self, strategy: str, successful: bool):
        """Record signal outcome for success rate tracking."""
        try:
            self.signal_success_rates[strategy]['total'] += 1
            if successful:
                self.signal_success_rates[strategy]['successful'] += 1
            
        except Exception as e:
            self.logger.log(f"❌ Error recording signal outcome: {str(e)}")
    
    def is_outlier_signal(self, strategy: str, quality_score: float) -> Tuple[bool, str]:
        """Detect if signal is an outlier based on historical quality."""
        try:
            history = self.signal_quality_history.get(strategy, [])
            
            if len(history) < self.MIN_HISTORY_LENGTH:
                return False, "Insufficient history for outlier detection"
            
            # Calculate statistics
            import numpy as np
            mean_quality = np.mean(history)
            std_quality = np.std(history)
            
            # Z-score calculation
            if std_quality == 0:
                return False, "No variation in signal quality"
            
            z_score = abs(quality_score - mean_quality) / std_quality
            
            # Check if outlier
            if z_score > self.OUTLIER_THRESHOLD:
                if quality_score < mean_quality:
                    return True, f"Low quality outlier (z-score: {z_score:.2f})"
                else:
                    return False, f"High quality outlier (z-score: {z_score:.2f}) - allowed"
            
            return False, f"Normal signal quality (z-score: {z_score:.2f})"
            
        except Exception as e:
            self.logger.log(f"❌ Error detecting outlier signal: {str(e)}")
            return False, f"Outlier detection error: {str(e)}"
    
    def should_filter_strategy(self, strategy: str) -> Tuple[bool, str]:
        """Check if strategy should be filtered due to poor performance."""
        try:
            stats = self.signal_success_rates.get(strategy, {'total': 0, 'successful': 0})
            
            if stats['total'] < 10:  # Need at least 10 signals
                return False, "Insufficient data for strategy filtering"
            
            success_rate = stats['successful'] / stats['total']
            
            if success_rate < self.SUCCESS_RATE_THRESHOLD:
                return True, f"Poor success rate: {success_rate:.2f} < {self.SUCCESS_RATE_THRESHOLD}"
            
            return False, f"Acceptable success rate: {success_rate:.2f}"
            
        except Exception as e:
            self.logger.log(f"❌ Error checking strategy filter: {str(e)}")
            return False, f"Strategy filter error: {str(e)}"
    
    def get_outlier_stats(self) -> Dict:
        """Get outlier detection statistics."""
        try:
            stats = {}
            
            for strategy in self.signal_quality_history:
                history = self.signal_quality_history[strategy]
                success_data = self.signal_success_rates[strategy]
                
                if len(history) > 0:
                    import numpy as np
                    stats[strategy] = {
                        'quality_samples': len(history),
                        'avg_quality': f"{np.mean(history):.2f}",
                        'quality_std': f"{np.std(history):.2f}",
                        'total_signals': success_data['total'],
                        'successful_signals': success_data['successful'],
                        'success_rate': f"{(success_data['successful'] / max(1, success_data['total'])):.2f}"
                    }
            
            return stats
            
        except Exception as e:
            self.logger.log(f"❌ Error getting outlier stats: {str(e)}")
            return {'error': str(e)}