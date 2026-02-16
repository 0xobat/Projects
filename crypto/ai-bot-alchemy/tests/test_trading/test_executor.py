"""Tests for live trading executor."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.trading.executor import (
    ExchangeExecutor,
    Order,
    OrderSide,
    OrderType,
    OrderStatus,
    CCXT_AVAILABLE
)


@pytest.fixture
def mock_exchange():
    """Create a mock CCXT exchange."""
    exchange = Mock()
    exchange.load_markets = Mock(return_value=None)
    exchange.markets = {
        'ETH/USDT': {'id': 'ETHUSDT'},
        'BTC/USDT': {'id': 'BTCUSDT'}
    }
    return exchange


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_executor_initialization():
    """Test executor initializes correctly."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)

        assert executor.exchange_name == 'binance'
        assert executor.testnet is True
        assert len(executor.orders) == 0


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_market_buy_order():
    """Test placing a market buy order."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_exchange.create_market_order = Mock(return_value={
            'id': 'EXCH-123',
            'status': 'closed',
            'filled': 0.1,
            'average': 3000.0,
            'fee': {'cost': 0.3}
        })
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)
        order = executor.market_buy('ETH/USDT', 0.1)

        assert order.symbol == 'ETH/USDT'
        assert order.side == OrderSide.BUY
        assert order.type == OrderType.MARKET
        assert order.quantity == 0.1
        assert order.status == OrderStatus.FILLED
        assert order.exchange_order_id == 'EXCH-123'


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_market_sell_order():
    """Test placing a market sell order."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_exchange.create_market_order = Mock(return_value={
            'id': 'EXCH-456',
            'status': 'closed',
            'filled': 0.1,
            'average': 3100.0,
            'fee': {'cost': 0.31}
        })
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)
        order = executor.market_sell('ETH/USDT', 0.1)

        assert order.side == OrderSide.SELL
        assert order.status == OrderStatus.FILLED


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_limit_buy_order():
    """Test placing a limit buy order."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_exchange.create_limit_order = Mock(return_value={
            'id': 'EXCH-789',
            'status': 'open',
            'filled': 0.0,
            'average': 0.0,
        })
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)
        order = executor.limit_buy('ETH/USDT', 0.1, 2900.0)

        assert order.type == OrderType.LIMIT
        assert order.price == 2900.0
        assert order.status == OrderStatus.OPEN


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_cancel_order():
    """Test cancelling an order."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_exchange.create_limit_order = Mock(return_value={
            'id': 'EXCH-999',
            'status': 'open',
        })
        mock_exchange.cancel_order = Mock()
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)

        # Place order
        order = executor.limit_buy('ETH/USDT', 0.1, 2900.0)
        order_id = order.id

        # Cancel it
        success = executor.cancel_order(order_id)

        assert success is True
        assert executor.orders[order_id].status == OrderStatus.CANCELLED


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_get_order_status():
    """Test fetching order status."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_exchange.create_limit_order = Mock(return_value={
            'id': 'EXCH-111',
            'status': 'open',
            'filled': 0.0,
        })
        mock_exchange.fetch_order = Mock(return_value={
            'id': 'EXCH-111',
            'status': 'closed',
            'filled': 0.1,
            'average': 2900.0,
        })
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)

        # Place order
        order = executor.limit_buy('ETH/USDT', 0.1, 2900.0)
        order_id = order.id

        # Get updated status
        updated_order = executor.get_order_status(order_id)

        assert updated_order.status == OrderStatus.FILLED
        assert updated_order.filled_quantity == 0.1


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_get_balance():
    """Test fetching account balance."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_exchange.fetch_balance = Mock(return_value={
            'USDT': {'free': 10000.0, 'used': 1000.0}
        })
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)
        balance = executor.get_balance('USDT')

        assert balance == 10000.0


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_get_ticker():
    """Test fetching ticker data."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_exchange.fetch_ticker = Mock(return_value={
            'last': 3000.0,
            'bid': 2999.5,
            'ask': 3000.5,
            'baseVolume': 12345.6,
            'timestamp': 1640000000000
        })
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)
        ticker = executor.get_ticker('ETH/USDT')

        assert ticker['last'] == 3000.0
        assert ticker['bid'] == 2999.5
        assert ticker['ask'] == 3000.5


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_get_open_orders():
    """Test fetching open orders."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_exchange.create_limit_order = Mock(side_effect=[
            {'id': 'EXCH-1', 'status': 'open'},
            {'id': 'EXCH-2', 'status': 'open'},
            {'id': 'EXCH-3', 'status': 'closed'},
        ])
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)

        # Place multiple orders
        executor.limit_buy('ETH/USDT', 0.1, 2900.0)
        executor.limit_buy('BTC/USDT', 0.01, 45000.0)
        order3 = executor.limit_buy('ETH/USDT', 0.05, 2950.0)
        order3.status = OrderStatus.FILLED  # Simulate fill

        # Get open orders
        open_orders = executor.get_open_orders()

        assert len(open_orders) == 2  # Only the open ones

        # Filter by symbol
        eth_orders = executor.get_open_orders(symbol='ETH/USDT')
        assert len(eth_orders) == 1


@pytest.mark.skipif(not CCXT_AVAILABLE, reason="ccxt not installed")
def test_failed_order():
    """Test handling failed order execution."""
    with patch('src.trading.executor.ccxt') as mock_ccxt:
        mock_exchange = Mock()
        mock_exchange.load_markets = Mock()
        mock_exchange.create_market_order = Mock(side_effect=Exception("Insufficient balance"))
        mock_ccxt.binance = Mock(return_value=mock_exchange)
        mock_ccxt.exchanges = ['binance']

        executor = ExchangeExecutor(exchange='binance', testnet=True)
        order = executor.market_buy('ETH/USDT', 100.0)

        assert order.status == OrderStatus.FAILED


def test_order_creation():
    """Test Order dataclass creation."""
    order = Order(
        id="TEST-001",
        symbol="ETH/USDT",
        side=OrderSide.BUY,
        type=OrderType.MARKET,
        quantity=0.1
    )

    assert order.id == "TEST-001"
    assert order.symbol == "ETH/USDT"
    assert order.side == OrderSide.BUY
    assert order.type == OrderType.MARKET
    assert order.quantity == 0.1
    assert order.status == OrderStatus.PENDING
    assert order.timestamp is not None
