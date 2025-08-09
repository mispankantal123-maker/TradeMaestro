"""
MT5 Connection Module
Handles all MT5 connection, initialization, and health monitoring.
"""

import platform
import sys
import time
from typing import Optional, Dict, Any, List
import threading

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    print("🔌 Using real MetaTrader5 connection")
except ImportError:
    print("⚠️ MetaTrader5 not available - using mock implementation")
    from modules import mt5_mock as mt5
    MT5_AVAILABLE = False

from config import *


class MT5Connection:
    """Manages MT5 connection with comprehensive error handling and diagnostics."""
    
    def __init__(self, logger):
        """Initialize MT5 connection manager."""
        self.logger = logger
        self.mt5 = mt5
        self.connected = False
        self.connection_lock = threading.Lock()
        self.last_connection_attempt = 0
        self.connection_attempts = 0
        
    def connect(self) -> bool:
        """
        Enhanced MT5 connection with comprehensive debugging and error handling.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        with self.connection_lock:
            try:
                # Check if MT5 module is available
                if not MT5_AVAILABLE:
                    self.logger.log("⚠️ Using mock MT5 implementation for testing")
                elif self.mt5 is None:
                    self.logger.log("❌ MetaTrader5 module not available")
                    self._install_mt5_module()
                    return False
                
                # Shutdown any existing connection
                try:
                    self.mt5.shutdown()
                    time.sleep(1)
                except:
                    pass
                
                self._log_diagnostic_info()
                
                # Attempt connection with multiple methods
                if self._attempt_connection():
                    self._validate_connection()
                    self.connected = True
                    self.connection_attempts = 0
                    self.logger.log("✅ MT5 connection established successfully")
                    return True
                else:
                    self.connected = False
                    self._log_troubleshooting_hints()
                    return False
                    
            except Exception as e:
                self.logger.log(f"❌ Connection error: {str(e)}")
                self.connected = False
                return False
    
    def _install_mt5_module(self) -> bool:
        """Attempt to install MetaTrader5 module."""
        try:
            import subprocess
            self.logger.log("📦 Attempting to install MetaTrader5 module...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "MetaTrader5", "--upgrade"
            ], check=True)
            
            # Try to import again
            import MetaTrader5 as mt5
            self.mt5 = mt5
            self.logger.log("✅ MetaTrader5 module installed successfully")
            return True
        except Exception as e:
            self.logger.log(f"❌ Failed to install MetaTrader5: {str(e)}")
            return False
    
    def _log_diagnostic_info(self) -> None:
        """Log comprehensive diagnostic information."""
        self.logger.log("🔍 === MT5 CONNECTION DIAGNOSTIC ===")
        self.logger.log(f"🔍 Python Version: {sys.version}")
        self.logger.log(f"🔍 Python Architecture: {platform.architecture()[0]}")
        self.logger.log(f"🔍 Platform: {platform.system()} {platform.release()}")
        
        try:
            version_attr = getattr(self.mt5, '__version__', 'Unknown')
            self.logger.log(f"🔍 MT5 Module Version: {version_attr}")
        except:
            self.logger.log("🔍 MT5 Module Version: Unknown")
    
    def _attempt_connection(self) -> bool:
        """Attempt connection using multiple initialization methods."""
        init_methods = [
            ("Default", lambda: self.mt5.initialize()),
            ("Path 64-bit", lambda: self.mt5.initialize(
                path="C:\\Program Files\\MetaTrader 5\\terminal64.exe")),
            ("Path 32-bit", lambda: self.mt5.initialize(
                path="C:\\Program Files (x86)\\MetaTrader 5\\terminal.exe")),
            ("Auto-login", lambda: self.mt5.initialize(login=0)),
        ]
        
        for attempt in range(MAX_CONNECTION_ATTEMPTS):
            self.logger.log(f"🔄 Connection attempt {attempt + 1}/{MAX_CONNECTION_ATTEMPTS}")
            
            for method_name, init_method in init_methods:
                try:
                    self.logger.log(f"🔄 Trying {method_name} initialization...")
                    result = init_method()
                    
                    if result:
                        self.logger.log(f"✅ Connected using {method_name} method")
                        return True
                    else:
                        error = self.mt5.last_error()
                        self.logger.log(f"⚠️ {method_name} failed: {error}")
                        
                except Exception as e:
                    self.logger.log(f"⚠️ {method_name} exception: {str(e)}")
                    continue
            
            if attempt < MAX_CONNECTION_ATTEMPTS - 1:
                self.logger.log(f"⏳ Waiting {CONNECTION_RETRY_DELAY}s before retry...")
                time.sleep(CONNECTION_RETRY_DELAY)
        
        return False
    
    def _validate_connection(self) -> bool:
        """Validate the established connection."""
        try:
            # Get MT5 version info
            version_info = self.mt5.version()
            if version_info:
                self.logger.log(f"🔍 MT5 Version: {version_info}")
            
            # Get account info
            account_info = self.mt5.account_info()
            if account_info:
                self.logger.log(f"👤 Account: {account_info.login}")
                self.logger.log(f"💰 Balance: {account_info.balance}")
                self.logger.log(f"🏢 Company: {account_info.company}")
            else:
                self.logger.log("⚠️ Cannot get account info")
                return False
            
            # Test symbol access
            symbols = self.mt5.symbols_get()
            if symbols and len(symbols) > 0:
                self.logger.log(f"📊 Available symbols: {len(symbols)}")
            else:
                self.logger.log("⚠️ No symbols available")
                return False
            
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Connection validation failed: {str(e)}")
            return False
    
    def _log_troubleshooting_hints(self) -> None:
        """Log troubleshooting hints for connection failures."""
        self.logger.log("💡 TROUBLESHOOTING SUGGESTIONS:")
        self.logger.log("   1. ⚠️ CRITICAL: Run MT5 as Administrator")
        self.logger.log("   2. ⚠️ CRITICAL: Ensure MT5 is logged into trading account")
        self.logger.log("   3. ⚠️ Verify Python and MT5 are both 64-bit")
        self.logger.log("   4. ⚠️ Close other MT5 instances")
        self.logger.log("   5. ⚠️ Restart MT5 terminal")
        self.logger.log("   6. ⚠️ Check firewall/antivirus settings")
        self.logger.log("   7. ⚠️ Verify broker allows algorithmic trading")
    
    def check_connection(self) -> bool:
        """
        Check if MT5 connection is still active.
        
        Returns:
            bool: True if connected and functional
        """
        try:
            if not self.connected or self.mt5 is None:
                return False
            
            # Quick connection test
            account_info = self.mt5.account_info()
            if account_info is None:
                self.connected = False
                return False
            
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Connection check failed: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MT5."""
        try:
            if self.mt5 is not None:
                self.mt5.shutdown()
                self.logger.log("🔌 Disconnected from MT5")
            self.connected = False
        except Exception as e:
            self.logger.log(f"❌ Error during disconnect: {str(e)}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get current connection information.
        
        Returns:
            Dict containing connection details
        """
        info = {
            "connected": self.connected,
            "connection_attempts": self.connection_attempts,
            "last_attempt": self.last_connection_attempt
        }
        
        if self.connected and self.mt5:
            try:
                account_info = self.mt5.account_info()
                if account_info:
                    info.update({
                        "login": account_info.login,
                        "company": account_info.company,
                        "server": account_info.server,
                        "currency": account_info.currency,
                        "leverage": account_info.leverage,
                        "trade_allowed": account_info.trade_allowed
                    })
                
                version_info = self.mt5.version()
                if version_info:
                    info["mt5_version"] = str(version_info)
                    
            except Exception as e:
                self.logger.log(f"❌ Error getting connection info: {str(e)}")
        
        return info
    
    def auto_reconnect(self) -> bool:
        """
        Attempt automatic reconnection if connection is lost.
        
        Returns:
            bool: True if reconnection successful
        """
        if self.check_connection():
            return True
        
        self.logger.log("🔄 Connection lost, attempting auto-reconnect...")
        return self.connect()
