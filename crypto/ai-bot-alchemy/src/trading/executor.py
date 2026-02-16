"""
Live trading executor for real exchange integration.

Connects to cryptocurrency exchanges via CCXT library for live order execution.
Supports multiple exchanges with unified interface.
"""

from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from loguru import logger

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    logger.warning("ccxt not installed - live trading disabled. Install with: uv add ccxt")


class OrderSide(Enum):
    """Order side enum."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enum."""
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(Enum):
    """Order status enum."""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Order:
    """Order details."""

    id: str
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: float
    price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    commission: float = 0.0
    timestamp: datetime = None
    exchange_order_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ExchangeExecutor:
    """
    Live trading executor using CCXT.

    Supports multiple exchanges with API key authentication.
    Handles order placement, status tracking, and fill monitoring.

    Usage:
        >>> executor = ExchangeExecutor(exchange='binance', testnet=True)
        >>> order = executor.market_buy('ETH/USDT', 0.1)
        >>> status = executor.get_order_status(order.id)
    """

    def __init__(
        self,
        exchange: str = 'binance',
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = True
    ):
        """
        Initialize exchange executor.

        Args:
            exchange: Exchange name (binance, coinbase, kraken, etc.)
            api_key: Exchange API key (if None, read-only mode)
            api_secret: Exchange API secret
            testnet: Use testnet/sandbox mode if available

        Raises:
            ImportError: If ccxt is not installed
            ValueError: If exchange is not supported
        """
        if not CCXT_AVAILABLE:
            raise ImportError(
                "ccxt library required for live trading. Install with: uv add ccxt"
            )

        self.exchange_name = exchange
        self.testnet = testnet
        self.orders: Dict[str, Order] = {}
        self._order_counter = 0

        # Initialize exchange
        try:
            exchange_class = getattr(ccxt, exchange)
        except AttributeError:
            raise ValueError(
                f"Exchange '{exchange}' not supported. "
                f"Available: {', '.join(ccxt.exchanges)}"
            )

        config = {
            'enableRateLimit': True,
        }

        if api_key and api_secret:
            config['apiKey'] = api_key
            config['secret'] = api_secret

        # Enable testnet if supported
        if testnet:
            if hasattr(exchange_class, 'set_sandbox_mode'):
                config['sandbox'] = True
                logger.info(f"Using {exchange} testnet/sandbox mode")
            else:
                logger.warning(f"{exchange} does not support testnet mode")

        self.exchange = exchange_class(config)

        # Validate connection
        try:
            self.exchange.load_markets()
            logger.success(
                f"Connected to {exchange} "
                f"({'testnet' if testnet else 'mainnet'}) - "
                f"{len(self.exchange.markets)} markets loaded"
            )
        except Exception as e:
            logger.error(f"Failed to connect to {exchange}: {e}")
            raise

    def market_buy(self, symbol: str, quantity: float) -> Order:
        """
        Execute a market buy order.

        Args:
            symbol: Trading pair (e.g. 'ETH/USDT')
            quantity: Quantity in base currency

        Returns:
            Order object with execution details

        Example:
            >>> order = executor.market_buy('ETH/USDT', 0.1)
            >>> print(f"Bought {order.filled_quantity} ETH @ ${order.average_fill_price}")
        """
        return self._execute_order(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=quantity
        )

    def market_sell(self, symbol: str, quantity: float) -> Order:
        """
        Execute a market sell order.

        Args:
            symbol: Trading pair (e.g. 'ETH/USDT')
            quantity: Quantity in base currency

        Returns:
            Order object with execution details
        """
        return self._execute_order(
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=quantity
        )

    def limit_buy(self, symbol: str, quantity: float, price: float) -> Order:
        """
        Place a limit buy order.

        Args:
            symbol: Trading pair (e.g. 'ETH/USDT')
            quantity: Quantity in base currency
            price: Limit price

        Returns:
            Order object
        """
        return self._execute_order(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price
        )

    def limit_sell(self, symbol: str, quantity: float, price: float) -> Order:
        """
        Place a limit sell order.

        Args:
            symbol: Trading pair (e.g. 'ETH/USDT')
            quantity: Quantity in base currency
            price: Limit price

        Returns:
            Order object
        """
        return self._execute_order(
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price
        )

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an open order.

        Args:
            order_id: Internal order ID

        Returns:
            True if cancelled successfully
        """
        if order_id not in self.orders:
            logger.error(f"Order {order_id} not found")
            return False

        order = self.orders[order_id]

        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            logger.warning(f"Order {order_id} already {order.status.value}")
            return False

        try:
            if order.exchange_order_id:
                self.exchange.cancel_order(order.exchange_order_id, order.symbol)

            order.status = OrderStatus.CANCELLED
            logger.info(f"Order {order_id} cancelled")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False

    def get_order_status(self, order_id: str) -> Optional[Order]:
        """
        Get current order status.

        Args:
            order_id: Internal order ID

        Returns:
            Order object with updated status, or None if not found
        """
        if order_id not in self.orders:
            return None

        order = self.orders[order_id]

        # Update status from exchange
        if order.exchange_order_id and order.status not in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            try:
                exchange_order = self.exchange.fetch_order(order.exchange_order_id, order.symbol)
                order = self._update_order_from_exchange(order, exchange_order)
            except Exception as e:
                logger.error(f"Failed to fetch order status: {e}")

        return order

    def get_balance(self, currency: str = 'USDT') -> float:
        """
        Get account balance for a currency.

        Args:
            currency: Currency symbol (USDT, USD, BTC, ETH, etc.)

        Returns:
            Available balance
        """
        try:
            balance = self.exchange.fetch_balance()
            return balance.get(currency, {}).get('free', 0.0)
        except Exception as e:
            logger.error(f"Failed to fetch balance: {e}")
            return 0.0

    def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker data for a symbol.

        Args:
            symbol: Trading pair (e.g. 'ETH/USDT')

        Returns:
            Dict with ticker data (last, bid, ask, volume, etc.)
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'last': ticker.get('last'),
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'volume': ticker.get('baseVolume'),
                'timestamp': ticker.get('timestamp')
            }
        except Exception as e:
            logger.error(f"Failed to fetch ticker for {symbol}: {e}")
            return {}

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Get all open orders.

        Args:
            symbol: Trading pair filter (optional)

        Returns:
            List of open Order objects
        """
        open_orders = [
            order for order in self.orders.values()
            if order.status == OrderStatus.OPEN
        ]

        if symbol:
            open_orders = [o for o in open_orders if o.symbol == symbol]

        return open_orders

    def _execute_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None
    ) -> Order:
        """Internal method to execute an order."""

        # Create order object
        self._order_counter += 1
        order_id = f"ORD-{self._order_counter:06d}"

        order = Order(
            id=order_id,
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            price=price,
            status=OrderStatus.PENDING
        )

        self.orders[order_id] = order

        logger.info(
            f"Executing {order_type.value.upper()} {side.value.upper()}: "
            f"{quantity} {symbol}" +
            (f" @ ${price}" if price else "")
        )

        try:
            # Execute on exchange
            if order_type == OrderType.MARKET:
                exchange_order = self.exchange.create_market_order(
                    symbol=symbol,
                    side=side.value,
                    amount=quantity
                )
            else:  # LIMIT
                exchange_order = self.exchange.create_limit_order(
                    symbol=symbol,
                    side=side.value,
                    amount=quantity,
                    price=price
                )

            # Update order with exchange response
            order = self._update_order_from_exchange(order, exchange_order)

            logger.success(
                f"Order {order_id} executed: {order.status.value} - "
                f"Filled: {order.filled_quantity}/{order.quantity}"
            )

        except Exception as e:
            order.status = OrderStatus.FAILED
            logger.error(f"Order {order_id} failed: {e}")

        return order

    def _update_order_from_exchange(self, order: Order, exchange_order: Dict) -> Order:
        """Update internal order with exchange data."""

        order.exchange_order_id = exchange_order.get('id')

        # Map exchange status to internal status
        status_map = {
            'open': OrderStatus.OPEN,
            'closed': OrderStatus.FILLED,
            'canceled': OrderStatus.CANCELLED,
            'cancelled': OrderStatus.CANCELLED,
        }

        exchange_status = exchange_order.get('status', '').lower()
        order.status = status_map.get(exchange_status, OrderStatus.OPEN)

        # Update fill info
        order.filled_quantity = exchange_order.get('filled', 0.0)
        order.average_fill_price = exchange_order.get('average', 0.0)

        # Update commission
        if 'fee' in exchange_order:
            order.commission = exchange_order['fee'].get('cost', 0.0)

        # Check for partial fills
        if 0 < order.filled_quantity < order.quantity:
            order.status = OrderStatus.PARTIALLY_FILLED

        return order


if __name__ == "__main__":
    """
    Demo/test mode - run this file directly to test exchange connection.
    """
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    print("\n" + "="*60)
    print("Exchange Executor Demo")
    print("="*60)

    if not CCXT_AVAILABLE:
        print("\nError: ccxt not installed")
        print("Install with: uv add ccxt")
        sys.exit(1)

    print(f"\nAvailable exchanges: {len(ccxt.exchanges)}")
    print(f"Popular: binance, coinbase, kraken, bitfinex, etc.")

    # Demo with read-only connection (no API keys)
    try:
        print("\nConnecting to Binance testnet (read-only)...")
        executor = ExchangeExecutor(exchange='binance', testnet=True)

        print("\nFetching ETH/USDT ticker...")
        ticker = executor.get_ticker('ETH/USDT')
        if ticker:
            print(f"Last price: ${ticker['last']:,.2f}")
            print(f"Bid: ${ticker['bid']:,.2f}")
            print(f"Ask: ${ticker['ask']:,.2f}")

        print("\n✓ Demo complete!")
        print("\nTo enable live trading:")
        print("1. Add your exchange API credentials to .env.local")
        print("2. Initialize with: ExchangeExecutor(api_key='...', api_secret='...')")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
