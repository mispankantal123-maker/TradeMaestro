# MT5 Automated Trading Bot

## Overview

This is a comprehensive automated trading bot for MetaTrader 5 (MT5) platform built in Python with a modular architecture. The bot features multiple trading strategies (HFT, Scalping, Intraday, Arbitrage), session-aware behavior, comprehensive risk management, and a Tkinter-based GUI for real-time monitoring and control. The system is designed with safety-first principles, extensive diagnostics, and robust error handling for professional trading applications.

**Status: ✅ FULLY OPERATIONAL** - Successfully migrated from Replit Agent to Replit environment. Running with mock MT5 implementation for testing and development purposes.

**Migration Status: ✅ COMPLETED** - Project successfully migrated from Replit Agent with comprehensive GUI audit completed (45% compatibility with bobot2.py reference).

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Design Pattern
The application follows a modular architecture with clear separation of concerns. Each component is encapsulated in its own module with well-defined interfaces and dependencies injected through initialization.

### Main Components Architecture

**Entry Point**: `main.py` serves as the orchestrator, initializing all components and managing the main trading loop with proper signal handling for graceful shutdown.

**Configuration Management**: Centralized configuration in `config.py` contains all constants, trading parameters, risk limits, and environment-based security settings.

**Connection Layer**: `modules/connection.py` handles MT5 platform connectivity with multi-attempt initialization, comprehensive diagnostics, and automatic reconnection capabilities.

**GUI Framework**: Tkinter-based interface in `modules/gui.py` provides real-time monitoring, manual controls, emergency stops, and TP/SL calculators with live updates.

**Trading Engine**: Core trading logic split across multiple specialized modules:
- `modules/orders.py` - Order execution with rate limiting and validation
- `modules/strategy.py` - Multiple strategy implementations with signal generation
- `modules/risk.py` - Position sizing, TP/SL calculations, and risk controls
- `modules/symbols.py` - Symbol validation, activation, and market data management

**Session Management**: `modules/sessions.py` implements time-aware trading with session-specific adjustments for Asia/London/New York markets and overlap periods.

**Market Analysis**: `modules/indicators.py` provides technical analysis with EMA, RSI, MACD, ATR, Bollinger Bands, and Stochastic calculations.

### Data Flow Architecture

The system follows a event-driven pattern where the main loop continuously monitors market conditions, generates signals through the strategy manager, validates trades through risk management, and executes orders through the order manager. All operations are logged through the centralized logging system with multiple output channels.

### Error Handling Strategy

Comprehensive error handling with fallback mechanisms at every level. Connection failures trigger automatic reconnection attempts, trading errors are logged with detailed diagnostics, and critical failures initiate safe shutdown procedures.

### Threading Model

The application uses thread-safe operations with locks for shared resources. The GUI runs on the main thread while trading operations use background threads with proper synchronization.

### Risk Management Framework

Multi-layered risk controls including position sizing based on account balance percentage, maximum loss streaks, daily loss limits, drawdown protection, and session-aware adjustments. All risk parameters are configurable and enforced before order execution.

## External Dependencies

**MetaTrader 5 Platform**: Primary dependency for market data and order execution. Requires MT5 terminal installation and proper broker configuration.

**Python Packages**:
- MetaTrader5 - Official MT5 Python API
- pandas - Data manipulation and analysis
- numpy - Numerical computations for indicators
- tkinter - GUI framework (built-in with Python)
- requests - HTTP client for news API integration

**News Data Services**: Optional integration with financial news APIs for high-impact event filtering. Configurable endpoints for economic calendar data.

**Telegram Integration**: Bot notifications and logging through Telegram Bot API. Requires bot token and chat ID configuration through environment variables.

**File System Dependencies**: Local logging to dated files, CSV export functionality, and configuration persistence.

**Network Requirements**: Stable internet connection for MT5 platform communication, news API calls, and Telegram notifications.

**Testing Framework**: unittest module for comprehensive test coverage of critical components including risk calculations, order management, and symbol validation.