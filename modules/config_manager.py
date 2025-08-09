"""
Configuration Management Module
Handles saving/loading of strategy parameters and user preferences
Implements persistent configuration system for bobot2.py compatibility
"""

import json
import os
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime


class ConfigManager:
    """Manages configuration persistence for the trading bot."""
    
    def __init__(self, logger):
        """Initialize configuration manager."""
        self.logger = logger
        self.config_dir = "config"
        self.config_file = os.path.join(self.config_dir, "bot_settings.json")
        self.backup_dir = os.path.join(self.config_dir, "backups")
        
        # Create directories if they don't exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Default configuration
        self.default_config = {
            "strategy_settings": {
                "HFT": {
                    "lot_size": "0.01",
                    "tp_value": "10",
                    "sl_value": "8",
                    "tp_unit": "pips",
                    "sl_unit": "pips",
                    "enabled": True
                },
                "Scalping": {
                    "lot_size": "0.02",
                    "tp_value": "15",
                    "sl_value": "10",
                    "tp_unit": "pips",
                    "sl_unit": "pips",
                    "enabled": True
                },
                "Intraday": {
                    "lot_size": "0.05",
                    "tp_value": "30",
                    "sl_value": "20",
                    "tp_unit": "pips",
                    "sl_unit": "pips",
                    "enabled": True
                },
                "Arbitrage": {
                    "lot_size": "0.03",
                    "tp_value": "12",
                    "sl_value": "15",
                    "tp_unit": "pips",
                    "sl_unit": "pips",
                    "enabled": True
                }
            },
            "gui_settings": {
                "current_strategy": "Scalping",
                "auto_trading": False,
                "show_debug": True,
                "theme": "dark",
                "last_symbols": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
            },
            "risk_settings": {
                "max_daily_risk": "2.0",
                "max_positions": "5",
                "max_drawdown": "10.0",
                "risk_per_trade": "1.0"
            },
            "ai_settings": {
                "enable_ai_analysis": True,
                "min_quality_score": 60,
                "enable_signal_enhancement": True,
                "enable_volume_confirmation": True
            },
            "session_settings": {
                "preferred_sessions": ["london", "new_york"],
                "avoid_news_times": True,
                "min_spread_threshold": 3.0
            },
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "created": datetime.now().isoformat()
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict with configuration data
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Validate and merge with defaults
                merged_config = self._merge_with_defaults(config)
                self.logger.log("✅ Configuration loaded successfully")
                return merged_config
            else:
                self.logger.log("⚠️ No config file found, using defaults")
                return self.default_config.copy()
                
        except Exception as e:
            self.logger.log(f"❌ Error loading config: {str(e)}")
            self.logger.log("⚠️ Using default configuration")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            bool: True if successful
        """
        try:
            # Create backup first
            self._create_backup()
            
            # Update timestamp
            config["last_updated"] = datetime.now().isoformat()
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.log("✅ Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error saving config: {str(e)}")
            return False
    
    def get_strategy_settings(self, strategy: str) -> Dict[str, Any]:
        """Get settings for specific strategy."""
        try:
            config = self.load_config()
            strategy_settings = config.get("strategy_settings", {})
            return strategy_settings.get(strategy, self.default_config["strategy_settings"][strategy])
        except Exception as e:
            self.logger.log(f"❌ Error getting strategy settings: {str(e)}")
            return self.default_config["strategy_settings"].get(strategy, {})
    
    def save_strategy_settings(self, strategy: str, settings: Dict[str, Any]) -> bool:
        """Save settings for specific strategy."""
        try:
            config = self.load_config()
            if "strategy_settings" not in config:
                config["strategy_settings"] = {}
            
            config["strategy_settings"][strategy] = settings
            return self.save_config(config)
            
        except Exception as e:
            self.logger.log(f"❌ Error saving strategy settings: {str(e)}")
            return False
    
    def get_gui_settings(self) -> Dict[str, Any]:
        """Get GUI settings."""
        try:
            config = self.load_config()
            return config.get("gui_settings", self.default_config["gui_settings"])
        except Exception as e:
            self.logger.log(f"❌ Error getting GUI settings: {str(e)}")
            return self.default_config["gui_settings"]
    
    def save_gui_settings(self, settings: Dict[str, Any]) -> bool:
        """Save GUI settings."""
        try:
            config = self.load_config()
            config["gui_settings"] = settings
            return self.save_config(config)
            
        except Exception as e:
            self.logger.log(f"❌ Error saving GUI settings: {str(e)}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """Export configuration to specified path."""
        try:
            config = self.load_config()
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.log(f"✅ Configuration exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error exporting config: {str(e)}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Import configuration from specified path."""
        try:
            if not os.path.exists(import_path):
                self.logger.log(f"❌ Import file not found: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validate imported config
            validated_config = self._merge_with_defaults(imported_config)
            
            # Save imported config
            if self.save_config(validated_config):
                self.logger.log(f"✅ Configuration imported from: {import_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error importing config: {str(e)}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        try:
            # Create backup first
            self._create_backup()
            
            # Reset to defaults
            default_config = self.default_config.copy()
            default_config["created"] = datetime.now().isoformat()
            
            if self.save_config(default_config):
                self.logger.log("✅ Configuration reset to defaults")
                return True
            
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error resetting config: {str(e)}")
            return False
    
    def _create_backup(self) -> bool:
        """Create backup of current configuration."""
        try:
            if os.path.exists(self.config_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(self.backup_dir, f"bot_settings_backup_{timestamp}.json")
                
                with open(self.config_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                
                # Keep only last 10 backups
                self._cleanup_old_backups()
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error creating backup: {str(e)}")
            return False
    
    def _cleanup_old_backups(self, max_backups: int = 10):
        """Clean up old backup files."""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith("bot_settings_backup_") and file.endswith(".json"):
                    backup_files.append(os.path.join(self.backup_dir, file))
            
            # Sort by modification time
            backup_files.sort(key=os.path.getmtime, reverse=True)
            
            # Remove old backups
            for old_backup in backup_files[max_backups:]:
                os.remove(old_backup)
                
        except Exception as e:
            self.logger.log(f"❌ Error cleaning up backups: {str(e)}")
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults to handle missing keys."""
        try:
            merged = self.default_config.copy()
            
            # Deep merge strategy settings
            if "strategy_settings" in config:
                for strategy, settings in config["strategy_settings"].items():
                    if strategy in merged["strategy_settings"]:
                        merged["strategy_settings"][strategy].update(settings)
                    else:
                        merged["strategy_settings"][strategy] = settings
            
            # Merge other sections
            for section in ["gui_settings", "risk_settings", "ai_settings", "session_settings"]:
                if section in config:
                    merged[section].update(config[section])
            
            # Preserve metadata
            if "version" in config:
                merged["version"] = config["version"]
            if "created" in config:
                merged["created"] = config["created"]
            
            return merged
            
        except Exception as e:
            self.logger.log(f"❌ Error merging config: {str(e)}")
            return self.default_config.copy()
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration structure and values.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Check required sections
            required_sections = ["strategy_settings", "gui_settings", "risk_settings"]
            for section in required_sections:
                if section not in config:
                    errors.append(f"Missing required section: {section}")
            
            # Validate strategy settings
            if "strategy_settings" in config:
                for strategy, settings in config["strategy_settings"].items():
                    if not isinstance(settings, dict):
                        errors.append(f"Invalid strategy settings for {strategy}")
                        continue
                    
                    # Check required fields
                    required_fields = ["lot_size", "tp_value", "sl_value", "tp_unit", "sl_unit"]
                    for field in required_fields:
                        if field not in settings:
                            errors.append(f"Missing {field} in {strategy} settings")
            
            # Validate numeric values
            if "risk_settings" in config:
                risk_settings = config["risk_settings"]
                for key, value in risk_settings.items():
                    if isinstance(value, str):
                        try:
                            float(value)
                        except ValueError:
                            errors.append(f"Invalid numeric value for {key}: {value}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors