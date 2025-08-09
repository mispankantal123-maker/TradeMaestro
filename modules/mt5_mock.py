"""
Mock MT5 Module for Testing and Development
This module provides a mock implementation of the MetaTrader5 API for testing purposes
when the actual MT5 terminal is not available.
"""

import time
import random
import datetime
from typing import Optional, List, Dict, Any, NamedTuple


class MockAccountInfo(NamedTuple):
    """Mock account information structure."""
    login: int = 12345678
    trade_mode: int = 0
    leverage: int = 100
    limit_orders: int = 200
    margin_so_mode: int = 0
    trade_allowed: bool = True
    trade_expert: bool = True
    margin_mode: int = 0
    currency_digits: int = 2
    fifo_close: bool = False
    balance: float = 10000.0
    credit: float = 0.0
    profit: float = 0.0
    equity: float = 10000.0
    margin: float = 0.0
    margin_free: float = 10000.0
    margin_level: float = 0.0
    margin_so_call: float = 50.0
    margin_so_so: float = 30.0
    margin_initial: float = 0.0
    margin_maintenance: float = 0.0
    assets: float = 0.0
    liabilities: float = 0.0
    commission_blocked: float = 0.0
    name: str = "Demo Account"
    server: str = "MockServer-Demo"
    currency: str = "USD"
    company: str = "Mock Broker Ltd"


class MockSymbolInfo(NamedTuple):
    """Mock symbol information structure."""
    custom: bool = False
    chart_mode: int = 0
    select: bool = True
    visible: bool = True
    session_deals: int = 0
    session_buy_orders: int = 0
    session_sell_orders: int = 0
    volume: int = 0
    volumehigh: int = 0
    volumelow: int = 0
    time: int = int(time.time())
    digits: int = 5
    spread: int = 20
    spread_float: bool = True
    ticks_bookdepth: int = 10
    trade_calc_mode: int = 0
    trade_mode: int = 0
    start_time: int = 0
    expiration_time: int = 0
    trade_stops_level: int = 0
    trade_freeze_level: int = 0
    trade_exemode: int = 0
    swap_mode: int = 0
    swap_rollover3days: int = 3
    margin_hedged_use_leg: bool = False
    expiration_mode: int = 0
    filling_mode: int = 0
    order_mode: int = 0
    order_gtc_mode: int = 0
    option_mode: int = 0
    option_right: int = 0
    bid: float = 1.08500
    bidhigh: float = 1.08600
    bidlow: float = 1.08400
    ask: float = 1.08520
    askhigh: float = 1.08620
    asklow: float = 1.08420
    last: float = 1.08510
    lasthigh: float = 1.08610
    lastlow: float = 1.08410
    volume_real: float = 0.0
    volumehigh_real: float = 0.0
    volumelow_real: float = 0.0
    option_strike: float = 0.0
    point: float = 0.00001
    trade_tick_value: float = 1.0
    trade_tick_value_profit: float = 1.0
    trade_tick_value_loss: float = 1.0
    trade_tick_size: float = 0.00001
    trade_contract_size: float = 100000.0
    trade_accrued_interest: float = 0.0
    trade_face_value: float = 0.0
    trade_liquidity_rate: float = 0.0
    volume_min: float = 0.01
    volume_max: float = 500.0
    volume_step: float = 0.01
    volume_limit: float = 0.0
    swap_long: float = -0.76
    swap_short: float = 0.24
    margin_initial: float = 0.0
    margin_maintenance: float = 0.0
    session_volume: float = 0.0
    session_turnover: float = 0.0
    session_interest: float = 0.0
    session_buy_orders_volume: float = 0.0
    session_sell_orders_volume: float = 0.0
    session_open: float = 1.08500
    session_close: float = 1.08510
    session_aw: float = 0.0
    session_price_settlement: float = 0.0
    session_price_limit_min: float = 0.0
    session_price_limit_max: float = 0.0
    margin_hedged: float = 50000.0
    price_change: float = 0.0001
    price_volatility: float = 0.0
    price_theoretical: float = 0.0
    price_greeks_delta: float = 0.0
    price_greeks_theta: float = 0.0
    price_greeks_gamma: float = 0.0
    price_greeks_vega: float = 0.0
    price_greeks_rho: float = 0.0
    price_greeks_omega: float = 0.0
    price_sensitivity: float = 0.0
    basis: str = ""
    category: str = ""
    currency_base: str = "EUR"
    currency_profit: str = "USD"
    currency_margin: str = "EUR"
    bank: str = ""
    description: str = "Euro vs US Dollar"
    exchange: str = ""
    formula: str = ""
    isin: str = ""
    name: str = "EURUSD"
    page: str = ""
    path: str = ""


class MockTick(NamedTuple):
    """Mock tick data structure."""
    time: int
    bid: float
    ask: float
    last: float
    volume: int
    time_msc: int
    flags: int = 0
    volume_real: float = 100.0


class MockTradeResult(NamedTuple):
    """Mock trade result structure."""
    retcode: int = 10009  # TRADE_RETCODE_DONE
    deal: Optional[int] = None
    order: Optional[int] = None
    volume: float = 0.0
    price: float = 0.0
    bid: float = 0.0
    ask: float = 0.0
    comment: str = ""
    request_id: int = 0
    retcode_external: int = 0


class MockPosition(NamedTuple):
    """Mock position structure."""
    ticket: int
    time: int
    time_msc: int
    time_update: int
    time_update_msc: int
    type: int = 0  # POSITION_TYPE_BUY
    magic: int = 0
    identifier: int = 0
    reason: int = 0
    volume: float = 0.01
    price_open: float = 1.08500
    sl: float = 0.0
    tp: float = 0.0
    price_current: float = 1.08520
    swap: float = 0.0
    profit: float = 2.0
    symbol: str = "EURUSD"
    comment: str = "AutoBotCuan"
    external_id: str = ""


class MockDeal(NamedTuple):
    """Mock deal structure."""
    ticket: int
    order: int
    time: int
    time_msc: int
    type: int = 0  # DEAL_TYPE_BUY
    entry: int = 0  # DEAL_ENTRY_IN
    magic: int = 0
    position_id: int = 0
    reason: int = 0
    volume: float = 0.01
    price: float = 1.08500
    commission: float = 0.0
    swap: float = 0.0
    profit: float = 0.0
    fee: float = 0.0
    symbol: str = "EURUSD"
    comment: str = "AutoBotCuan"
    external_id: str = ""


class MockMT5:
    """Mock MetaTrader 5 API implementation for testing."""
    
    # Constants
    TRADE_RETCODE_DONE = 10009
    TRADE_RETCODE_ERROR = 10013
    TRADE_RETCODE_TIMEOUT = 10012
    TRADE_RETCODE_INVALID = 10014
    TRADE_RETCODE_INVALID_VOLUME = 10015
    TRADE_RETCODE_INVALID_PRICE = 10016
    TRADE_RETCODE_INVALID_STOPS = 10017
    TRADE_RETCODE_TRADE_DISABLED = 10018
    TRADE_RETCODE_MARKET_CLOSED = 10019
    TRADE_RETCODE_NO_MONEY = 10020
    TRADE_RETCODE_PRICE_CHANGED = 10021
    TRADE_RETCODE_PRICE_OFF = 10022
    TRADE_RETCODE_INVALID_EXPIRATION = 10023
    TRADE_RETCODE_ORDER_CHANGED = 10024
    TRADE_RETCODE_TOO_MANY_REQUESTS = 10025
    TRADE_RETCODE_NO_CHANGES = 10026
    TRADE_RETCODE_SERVER_DISABLES_AT = 10027
    TRADE_RETCODE_CLIENT_DISABLES_AT = 10028
    TRADE_RETCODE_LOCKED = 10029
    TRADE_RETCODE_FROZEN = 10030
    TRADE_RETCODE_INVALID_FILL = 10031
    TRADE_RETCODE_CONNECTION = 10032
    TRADE_RETCODE_ONLY_REAL = 10033
    TRADE_RETCODE_LIMIT_ORDERS = 10034
    TRADE_RETCODE_LIMIT_VOLUME = 10035
    TRADE_RETCODE_INVALID_ORDER = 10036
    TRADE_RETCODE_POSITION_CLOSED = 10037
    TRADE_RETCODE_INVALID_CLOSE_VOLUME = 10038
    TRADE_RETCODE_CLOSE_ORDER_EXIST = 10039
    TRADE_RETCODE_LIMIT_POSITIONS = 10040
    TRADE_RETCODE_REJECT_CANCEL = 10041
    TRADE_RETCODE_LONG_ONLY = 10042
    TRADE_RETCODE_SHORT_ONLY = 10043
    TRADE_RETCODE_CLOSE_ONLY = 10044
    TRADE_RETCODE_FIFO_CLOSE = 10045
    
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    ORDER_TYPE_BUY_LIMIT = 2
    ORDER_TYPE_SELL_LIMIT = 3
    ORDER_TYPE_BUY_STOP = 4
    ORDER_TYPE_SELL_STOP = 5
    ORDER_TYPE_BUY_STOP_LIMIT = 6
    ORDER_TYPE_SELL_STOP_LIMIT = 7
    ORDER_TYPE_CLOSE_BY = 8
    
    TRADE_ACTION_DEAL = 1
    TRADE_ACTION_PENDING = 5
    TRADE_ACTION_SLTP = 2
    TRADE_ACTION_MODIFY = 3
    TRADE_ACTION_REMOVE = 4
    TRADE_ACTION_CLOSE_BY = 10
    
    POSITION_TYPE_BUY = 0
    POSITION_TYPE_SELL = 1
    
    ORDER_TIME_GTC = 0
    ORDER_TIME_DAY = 1
    ORDER_TIME_SPECIFIED = 2
    ORDER_TIME_SPECIFIED_DAY = 3
    
    ORDER_FILLING_FOK = 0
    ORDER_FILLING_IOC = 1
    ORDER_FILLING_RETURN = 2
    
    def __init__(self):
        self.initialized = False
        self.connected = False
        self.account_info_data = MockAccountInfo()
        self.symbols = {
            'EURUSD': MockSymbolInfo(name='EURUSD', digits=5, point=0.00001, 
                                   currency_base='EUR', currency_profit='USD', 
                                   description='Euro vs US Dollar'),
            'GBPUSD': MockSymbolInfo(name='GBPUSD', digits=5, point=0.00001,
                                   currency_base='GBP', currency_profit='USD',
                                   description='British Pound vs US Dollar'),
            'USDJPY': MockSymbolInfo(name='USDJPY', digits=3, point=0.001,
                                   currency_base='USD', currency_profit='JPY',
                                   description='US Dollar vs Japanese Yen'),
            'XAUUSD': MockSymbolInfo(name='XAUUSD', digits=2, point=0.01,
                                   currency_base='XAU', currency_profit='USD',
                                   description='Gold vs US Dollar',
                                   bid=2650.00, ask=2651.00),
            'BTCUSD': MockSymbolInfo(name='BTCUSD', digits=2, point=0.01,
                                   currency_base='BTC', currency_profit='USD',
                                   description='Bitcoin vs US Dollar',
                                   bid=98000.00, ask=98050.00),
            'SPX500': MockSymbolInfo(name='SPX500', digits=2, point=0.01,
                                   currency_base='SPX', currency_profit='USD',
                                   description='S&P 500 Index',
                                   bid=5900.00, ask=5901.00),
        }
        self.positions = {}
        self.orders = {}
        self.deals = []
        self.next_ticket = 100000
        self._last_error_code = 0
    
    def initialize(self, path: str = "", login: Optional[int] = None, password: str = "", 
                  server: str = "", timeout: int = 60000, portable: bool = False) -> bool:
        """Mock MT5 initialization."""
        print("🔄 Mock MT5: Initializing connection...")
        time.sleep(0.5)  # Simulate connection time
        self.initialized = True
        self.connected = True
        print("✅ Mock MT5: Connected successfully!")
        return True
    
    def shutdown(self) -> None:
        """Mock MT5 shutdown."""
        print("🔄 Mock MT5: Shutting down...")
        self.initialized = False
        self.connected = False
        print("✅ Mock MT5: Disconnected successfully!")
    
    def version(self) -> tuple:
        """Mock version information."""
        return (500, 4815, "08 Aug 2025")
    
    def account_info(self) -> Optional[MockAccountInfo]:
        """Mock account information."""
        if not self.connected:
            return None
        
        # Simulate balance changes from open positions
        total_profit = sum(pos.profit for pos in self.positions.values())
        balance = self.account_info_data.balance
        equity = balance + total_profit
        
        return self.account_info_data._replace(
            equity=equity,
            profit=total_profit,
            margin_free=equity
        )
    
    def terminal_info(self) -> dict:
        """Mock terminal information."""
        return {
            'community_account': False,
            'community_connection': False,
            'connected': self.connected,
            'dlls_allowed': True,
            'trade_allowed': True,
            'tradeapi_disabled': False,
            'email_enabled': False,
            'ftp_enabled': False,
            'notifications_enabled': False,
            'mqid': False,
            'build': 4815,
            'maxbars': 100000,
            'codepage': 1252,
            'ping_last': 15,
            'community_balance': 0.0,
            'retransmission': 0.0,
            'company': "Mock Broker Ltd",
            'name': "MetaTrader 5 Mock",
            'language': 1033,
            'path': "/mock/mt5/path"
        }
    
    def symbols_total(self) -> int:
        """Mock total symbols count."""
        return len(self.symbols)
    
    def symbols_get(self, group: str = "*") -> Optional[List[MockSymbolInfo]]:
        """Mock symbols list."""
        if not self.connected:
            return None
        
        # Filter symbols based on group pattern
        if group == "*":
            return list(self.symbols.values())
        else:
            # Simple pattern matching
            filtered = []
            for symbol in self.symbols.values():
                if group.upper() in symbol.name.upper():
                    filtered.append(symbol)
            return filtered
    
    def symbol_info(self, symbol: str) -> Optional[MockSymbolInfo]:
        """Mock symbol information."""
        if not self.connected:
            return None
        
        return self.symbols.get(symbol.upper())
    
    def symbol_info_tick(self, symbol: str) -> Optional[MockTick]:
        """Mock tick information."""
        if not self.connected:
            return None
        
        symbol_info = self.symbols.get(symbol.upper())
        if not symbol_info:
            return None
        
        # Simulate price movement
        base_bid = symbol_info.bid
        base_ask = symbol_info.ask
        
        # Add small random movement
        price_change = random.uniform(-0.0001, 0.0001)
        if symbol == 'XAUUSD':
            price_change *= 100  # Gold moves more
        elif symbol == 'BTCUSD':
            price_change *= 1000  # Bitcoin moves much more
        elif symbol == 'SPX500':
            price_change *= 10  # Index moves more
        
        new_bid = base_bid + price_change
        new_ask = base_ask + price_change
        
        current_time = int(time.time())
        return MockTick(
            time=current_time,
            bid=new_bid,
            ask=new_ask,
            last=(new_bid + new_ask) / 2,
            volume=random.randint(10, 1000),
            time_msc=current_time * 1000
        )
    
    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        """Mock symbol selection."""
        if not self.connected:
            return False
        
        if symbol.upper() in self.symbols:
            return True
        return False
    
    def order_send(self, request: dict) -> MockTradeResult:
        """Mock order sending."""
        if not self.connected:
            return MockTradeResult(retcode=self.TRADE_RETCODE_CONNECTION)
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Basic validation
        if not request.get('symbol') or request.get('volume', 0) <= 0:
            return MockTradeResult(retcode=self.TRADE_RETCODE_INVALID)
        
        symbol = request['symbol']
        if symbol not in self.symbols:
            return MockTradeResult(retcode=self.TRADE_RETCODE_INVALID)
        
        action = request.get('action')
        
        if action == self.TRADE_ACTION_DEAL:
            # Market order
            ticket = self.next_ticket
            self.next_ticket += 1
            
            order_type = request.get('type')
            volume = request['volume']
            
            # Get current price
            tick = self.symbol_info_tick(symbol)
            if not tick:
                return MockTradeResult(retcode=self.TRADE_RETCODE_INVALID)
            
            price = tick.ask if order_type == self.ORDER_TYPE_BUY else tick.bid
            
            # Create position
            current_time = int(time.time())
            position = MockPosition(
                ticket=ticket,
                time=current_time,
                time_msc=current_time * 1000,
                time_update=current_time,
                time_update_msc=current_time * 1000,
                type=self.POSITION_TYPE_BUY if order_type == self.ORDER_TYPE_BUY else self.POSITION_TYPE_SELL,
                volume=volume,
                price_open=price,
                symbol=symbol,
                sl=request.get('sl', 0.0),
                tp=request.get('tp', 0.0),
                profit=0.0
            )
            
            self.positions[ticket] = position
            
            # Create deal
            deal = MockDeal(
                ticket=self.next_ticket,
                order=ticket,
                time=current_time,
                time_msc=current_time * 1000,
                position_id=ticket,
                volume=volume,
                price=price,
                symbol=symbol
            )
            self.next_ticket += 1
            self.deals.append(deal)
            
            return MockTradeResult(
                retcode=self.TRADE_RETCODE_DONE,
                order=ticket,
                deal=deal.ticket,
                volume=volume,
                price=price,
                bid=tick.bid,
                ask=tick.ask
            )
        
        elif action == self.TRADE_ACTION_SLTP:
            # Modify position TP/SL
            position_ticket = request.get('position')
            if position_ticket and position_ticket in self.positions:
                position = self.positions[position_ticket]
                new_sl = request.get('sl', position.sl)
                new_tp = request.get('tp', position.tp)
                
                self.positions[position_ticket] = position._replace(sl=new_sl, tp=new_tp)
                
                return MockTradeResult(retcode=self.TRADE_RETCODE_DONE)
        
        return MockTradeResult(retcode=self.TRADE_RETCODE_ERROR)
    
    def positions_total(self) -> int:
        """Mock total positions count."""
        return len(self.positions)
    
    def positions_get(self, symbol: Optional[str] = None, ticket: Optional[int] = None) -> Optional[List[MockPosition]]:
        """Mock positions retrieval."""
        if not self.connected:
            return None
        
        positions = list(self.positions.values())
        
        if ticket is not None:
            positions = [pos for pos in positions if pos.ticket == ticket]
        elif symbol is not None:
            positions = [pos for pos in positions if pos.symbol == symbol]
        
        # Update position profits
        updated_positions = []
        for pos in positions:
            tick = self.symbol_info_tick(pos.symbol)
            if tick:
                # Calculate profit
                current_price = tick.bid if pos.type == self.POSITION_TYPE_BUY else tick.ask
                price_diff = current_price - pos.price_open if pos.type == self.POSITION_TYPE_BUY else pos.price_open - current_price
                
                symbol_info = self.symbols.get(pos.symbol)
                if symbol_info:
                    profit = price_diff * pos.volume * symbol_info.trade_contract_size / symbol_info.point
                    updated_pos = pos._replace(price_current=current_price, profit=profit)
                    self.positions[pos.ticket] = updated_pos
                    updated_positions.append(updated_pos)
                else:
                    updated_positions.append(pos)
            else:
                updated_positions.append(pos)
        
        return updated_positions
    
    def history_deals_get(self, date_from: datetime.datetime, date_to: datetime.datetime,
                         group: str = "*") -> Optional[List[MockDeal]]:
        """Mock deals history."""
        if not self.connected:
            return None
        
        # Filter deals by date range
        from_timestamp = date_from.timestamp() if date_from else 0
        to_timestamp = date_to.timestamp() if date_to else time.time()
        
        filtered_deals = []
        for deal in self.deals:
            if from_timestamp <= deal.time <= to_timestamp:
                if group == "*" or group.upper() in deal.symbol.upper():
                    filtered_deals.append(deal)
        
        return filtered_deals
    
    def last_error(self) -> int:
        """Mock last error."""
        return self._last_error_code
    
    def copy_rates_from(self, symbol: str, timeframe: int, date_from: datetime.datetime, count: int):
        """Mock rates data."""
        if not self.connected:
            return None
        
        # Generate mock OHLCV data
        rates = []
        current_time = int(date_from.timestamp())
        
        symbol_info = self.symbols.get(symbol.upper())
        if not symbol_info:
            return None
        
        base_price = symbol_info.bid
        
        for i in range(count):
            # Generate realistic OHLCV data
            open_price = base_price + random.uniform(-0.001, 0.001)
            high_price = open_price + random.uniform(0, 0.002)
            low_price = open_price - random.uniform(0, 0.002)
            close_price = open_price + random.uniform(-0.0015, 0.0015)
            
            rates.append({
                'time': current_time,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'tick_volume': random.randint(100, 1000),
                'spread': random.randint(10, 30),
                'real_volume': 0
            })
            
            current_time += 60 * timeframe  # Add minutes based on timeframe
            base_price = close_price  # Use previous close as base for next candle
        
        return rates


# Global mock instance
mock_mt5 = MockMT5()

# Mock all the functions that would normally be imported from MetaTrader5
def initialize(*args, **kwargs):
    return mock_mt5.initialize(*args, **kwargs)

def shutdown():
    return mock_mt5.shutdown()

def version():
    return mock_mt5.version()

def account_info():
    return mock_mt5.account_info()

def terminal_info():
    return mock_mt5.terminal_info()

def symbols_total():
    return mock_mt5.symbols_total()

def symbols_get(group="*"):
    return mock_mt5.symbols_get(group)

def symbol_info(symbol):
    return mock_mt5.symbol_info(symbol)

def symbol_info_tick(symbol):
    return mock_mt5.symbol_info_tick(symbol)

def symbol_select(symbol, enable=True):
    return mock_mt5.symbol_select(symbol, enable)

def order_send(request):
    return mock_mt5.order_send(request)

def positions_total():
    return mock_mt5.positions_total()

def positions_get(symbol=None, ticket=None):
    return mock_mt5.positions_get(symbol, ticket)

def history_deals_get(date_from, date_to, group="*"):
    return mock_mt5.history_deals_get(date_from, date_to, group)

def last_error():
    return mock_mt5.last_error()

def copy_rates_from(symbol, timeframe, date_from, count):
    return mock_mt5.copy_rates_from(symbol, timeframe, date_from, count)

# Constants
TRADE_RETCODE_DONE = mock_mt5.TRADE_RETCODE_DONE
TRADE_RETCODE_ERROR = mock_mt5.TRADE_RETCODE_ERROR
TRADE_RETCODE_TIMEOUT = mock_mt5.TRADE_RETCODE_TIMEOUT
TRADE_RETCODE_INVALID = mock_mt5.TRADE_RETCODE_INVALID
TRADE_RETCODE_INVALID_VOLUME = mock_mt5.TRADE_RETCODE_INVALID_VOLUME
TRADE_RETCODE_INVALID_PRICE = mock_mt5.TRADE_RETCODE_INVALID_PRICE
TRADE_RETCODE_INVALID_STOPS = mock_mt5.TRADE_RETCODE_INVALID_STOPS
TRADE_RETCODE_TRADE_DISABLED = mock_mt5.TRADE_RETCODE_TRADE_DISABLED
TRADE_RETCODE_MARKET_CLOSED = mock_mt5.TRADE_RETCODE_MARKET_CLOSED
TRADE_RETCODE_NO_MONEY = mock_mt5.TRADE_RETCODE_NO_MONEY
TRADE_RETCODE_PRICE_CHANGED = mock_mt5.TRADE_RETCODE_PRICE_CHANGED
TRADE_RETCODE_PRICE_OFF = mock_mt5.TRADE_RETCODE_PRICE_OFF
TRADE_RETCODE_INVALID_EXPIRATION = mock_mt5.TRADE_RETCODE_INVALID_EXPIRATION
TRADE_RETCODE_ORDER_CHANGED = mock_mt5.TRADE_RETCODE_ORDER_CHANGED
TRADE_RETCODE_TOO_MANY_REQUESTS = mock_mt5.TRADE_RETCODE_TOO_MANY_REQUESTS
TRADE_RETCODE_NO_CHANGES = mock_mt5.TRADE_RETCODE_NO_CHANGES
TRADE_RETCODE_SERVER_DISABLES_AT = mock_mt5.TRADE_RETCODE_SERVER_DISABLES_AT
TRADE_RETCODE_CLIENT_DISABLES_AT = mock_mt5.TRADE_RETCODE_CLIENT_DISABLES_AT
TRADE_RETCODE_LOCKED = mock_mt5.TRADE_RETCODE_LOCKED
TRADE_RETCODE_FROZEN = mock_mt5.TRADE_RETCODE_FROZEN
TRADE_RETCODE_INVALID_FILL = mock_mt5.TRADE_RETCODE_INVALID_FILL
TRADE_RETCODE_CONNECTION = mock_mt5.TRADE_RETCODE_CONNECTION
TRADE_RETCODE_ONLY_REAL = mock_mt5.TRADE_RETCODE_ONLY_REAL
TRADE_RETCODE_LIMIT_ORDERS = mock_mt5.TRADE_RETCODE_LIMIT_ORDERS
TRADE_RETCODE_LIMIT_VOLUME = mock_mt5.TRADE_RETCODE_LIMIT_VOLUME
TRADE_RETCODE_INVALID_ORDER = mock_mt5.TRADE_RETCODE_INVALID_ORDER
TRADE_RETCODE_POSITION_CLOSED = mock_mt5.TRADE_RETCODE_POSITION_CLOSED
TRADE_RETCODE_INVALID_CLOSE_VOLUME = mock_mt5.TRADE_RETCODE_INVALID_CLOSE_VOLUME
TRADE_RETCODE_CLOSE_ORDER_EXIST = mock_mt5.TRADE_RETCODE_CLOSE_ORDER_EXIST
TRADE_RETCODE_LIMIT_POSITIONS = mock_mt5.TRADE_RETCODE_LIMIT_POSITIONS
TRADE_RETCODE_REJECT_CANCEL = mock_mt5.TRADE_RETCODE_REJECT_CANCEL
TRADE_RETCODE_LONG_ONLY = mock_mt5.TRADE_RETCODE_LONG_ONLY
TRADE_RETCODE_SHORT_ONLY = mock_mt5.TRADE_RETCODE_SHORT_ONLY
TRADE_RETCODE_CLOSE_ONLY = mock_mt5.TRADE_RETCODE_CLOSE_ONLY
TRADE_RETCODE_FIFO_CLOSE = mock_mt5.TRADE_RETCODE_FIFO_CLOSE

ORDER_TYPE_BUY = mock_mt5.ORDER_TYPE_BUY
ORDER_TYPE_SELL = mock_mt5.ORDER_TYPE_SELL
ORDER_TYPE_BUY_LIMIT = mock_mt5.ORDER_TYPE_BUY_LIMIT
ORDER_TYPE_SELL_LIMIT = mock_mt5.ORDER_TYPE_SELL_LIMIT
ORDER_TYPE_BUY_STOP = mock_mt5.ORDER_TYPE_BUY_STOP
ORDER_TYPE_SELL_STOP = mock_mt5.ORDER_TYPE_SELL_STOP
ORDER_TYPE_BUY_STOP_LIMIT = mock_mt5.ORDER_TYPE_BUY_STOP_LIMIT
ORDER_TYPE_SELL_STOP_LIMIT = mock_mt5.ORDER_TYPE_SELL_STOP_LIMIT
ORDER_TYPE_CLOSE_BY = mock_mt5.ORDER_TYPE_CLOSE_BY

TRADE_ACTION_DEAL = mock_mt5.TRADE_ACTION_DEAL
TRADE_ACTION_PENDING = mock_mt5.TRADE_ACTION_PENDING
TRADE_ACTION_SLTP = mock_mt5.TRADE_ACTION_SLTP
TRADE_ACTION_MODIFY = mock_mt5.TRADE_ACTION_MODIFY
TRADE_ACTION_REMOVE = mock_mt5.TRADE_ACTION_REMOVE
TRADE_ACTION_CLOSE_BY = mock_mt5.TRADE_ACTION_CLOSE_BY

POSITION_TYPE_BUY = mock_mt5.POSITION_TYPE_BUY
POSITION_TYPE_SELL = mock_mt5.POSITION_TYPE_SELL

ORDER_TIME_GTC = mock_mt5.ORDER_TIME_GTC
ORDER_TIME_DAY = mock_mt5.ORDER_TIME_DAY
ORDER_TIME_SPECIFIED = mock_mt5.ORDER_TIME_SPECIFIED
ORDER_TIME_SPECIFIED_DAY = mock_mt5.ORDER_TIME_SPECIFIED_DAY

ORDER_FILLING_FOK = mock_mt5.ORDER_FILLING_FOK
ORDER_FILLING_IOC = mock_mt5.ORDER_FILLING_IOC
ORDER_FILLING_RETURN = mock_mt5.ORDER_FILLING_RETURN

# Timeframes
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 60
TIMEFRAME_H4 = 240
TIMEFRAME_D1 = 1440
TIMEFRAME_W1 = 10080
TIMEFRAME_MN1 = 43200