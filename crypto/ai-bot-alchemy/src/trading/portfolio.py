"""
Portfolio management - track positions, cash, and P&L.
"""

from typing import Dict, Optional
from datetime import datetime
from loguru import logger


class Position:
    """Represents a single trading position."""

    def __init__(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        entry_time: datetime
    ):
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.entry_value = quantity * entry_price

    def get_pnl(self, current_price: float) -> Dict:
        """
        Calculate current P&L for this position.

        Args:
            current_price: Current market price

        Returns:
            Dict with P&L metrics
        """
        current_value = self.quantity * current_price
        pnl = current_value - self.entry_value
        pnl_pct = (pnl / self.entry_value) if self.entry_value > 0 else 0

        return {
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'entry_value': self.entry_value,
            'current_value': current_value,
            'entry_price': self.entry_price,
            'current_price': current_price
        }


class Portfolio:
    """Manages portfolio state: cash, positions, and performance."""

    def __init__(self, initial_balance: float = 10000.0):
        """
        Initialize portfolio.

        Args:
            initial_balance: Starting cash balance (default: $10,000)
        """
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.positions: Dict[str, Position] = {}

        self.starting_equity = initial_balance
        self.peak_equity = initial_balance

        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0

        logger.info(f"Portfolio initialized with ${initial_balance:,.2f}")

    def get_available_capital(self) -> float:
        """Get available cash for trading."""
        return self.cash

    def get_total_equity(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio equity.

        Args:
            current_prices: Dict mapping symbol -> current price

        Returns:
            Total equity (cash + position values)
        """
        position_value = sum(
            pos.quantity * current_prices.get(pos.symbol, pos.entry_price)
            for pos in self.positions.values()
        )

        return self.cash + position_value

    def open_position(
        self,
        symbol: str,
        quantity: float,
        price: float
    ) -> bool:
        """
        Open a new position.

        Args:
            symbol: Token symbol
            quantity: Quantity to buy
            price: Entry price

        Returns:
            True if successful, False if insufficient funds
        """
        cost = quantity * price

        if cost > self.cash:
            logger.warning(f"Insufficient funds: need ${cost:,.2f}, have ${self.cash:,.2f}")
            return False

        # Check if position already exists
        if symbol in self.positions:
            logger.warning(f"Position in {symbol} already exists")
            return False

        # Create position
        position = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=price,
            entry_time=datetime.now()
        )

        self.positions[symbol] = position
        self.cash -= cost
        self.total_trades += 1

        logger.info(
            f"Opened position: {quantity:.4f} {symbol} @ ${price:,.2f} "
            f"(cost: ${cost:,.2f}, remaining cash: ${self.cash:,.2f})"
        )

        return True

    def close_position(
        self,
        symbol: str,
        price: float
    ) -> Optional[Dict]:
        """
        Close an existing position.

        Args:
            symbol: Token symbol
            price: Exit price

        Returns:
            Dict with trade results, or None if position doesn't exist
        """
        if symbol not in self.positions:
            logger.warning(f"No position found for {symbol}")
            return None

        position = self.positions[symbol]

        # Calculate proceeds
        proceeds = position.quantity * price
        pnl_metrics = position.get_pnl(price)

        # Update cash
        self.cash += proceeds

        # Update performance stats
        self.total_pnl += pnl_metrics['pnl']

        if pnl_metrics['pnl'] > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        # Remove position
        del self.positions[symbol]

        logger.info(
            f"Closed position: {position.quantity:.4f} {symbol} @ ${price:,.2f} "
            f"(P&L: ${pnl_metrics['pnl']:+,.2f} / {pnl_metrics['pnl_pct']:+.2%})"
        )

        return {
            'symbol': symbol,
            'quantity': position.quantity,
            'entry_price': position.entry_price,
            'exit_price': price,
            'pnl': pnl_metrics['pnl'],
            'pnl_pct': pnl_metrics['pnl_pct'],
            'hold_time': (datetime.now() - position.entry_time).total_seconds() / 3600
        }

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get a position by symbol."""
        return self.positions.get(symbol)

    def has_position(self, symbol: str) -> bool:
        """Check if portfolio has a position in a symbol."""
        return symbol in self.positions

    def get_position_count(self) -> int:
        """Get number of open positions."""
        return len(self.positions)

    def get_performance_summary(self, current_prices: Dict[str, float]) -> Dict:
        """
        Get comprehensive performance summary.

        Args:
            current_prices: Current market prices

        Returns:
            Dict with performance metrics
        """
        total_equity = self.get_total_equity(current_prices)
        total_return = total_equity - self.initial_balance
        total_return_pct = (total_return / self.initial_balance) if self.initial_balance > 0 else 0

        # Update peak equity
        if total_equity > self.peak_equity:
            self.peak_equity = total_equity

        # Calculate drawdown
        drawdown = (total_equity - self.peak_equity) / self.peak_equity if self.peak_equity > 0 else 0

        # Win rate
        win_rate = (self.winning_trades / self.total_trades) if self.total_trades > 0 else 0

        return {
            'initial_balance': self.initial_balance,
            'current_cash': self.cash,
            'total_equity': total_equity,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'peak_equity': self.peak_equity,
            'drawdown': drawdown,
            'drawdown_pct': drawdown,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'open_positions': self.get_position_count()
        }


if __name__ == "__main__":
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    # Test portfolio
    portfolio = Portfolio(initial_balance=10000.0)

    print("\n" + "="*60)
    print("Testing Portfolio Management")
    print("="*60)

    # Open position
    portfolio.open_position("ETH", quantity=1.0, price=3000.0)

    # Check portfolio state
    print(f"\nAvailable capital: ${portfolio.get_available_capital():,.2f}")
    print(f"Open positions: {portfolio.get_position_count()}")

    # Simulate price change
    current_prices = {"ETH": 3150.0}  # 5% gain

    # Check P&L
    position = portfolio.get_position("ETH")
    pnl = position.get_pnl(current_prices["ETH"])
    print(f"\nCurrent P&L: ${pnl['pnl']:+,.2f} ({pnl['pnl_pct']:+.2%})")

    # Close position
    trade_result = portfolio.close_position("ETH", price=3150.0)
    print(f"\nTrade result: ${trade_result['pnl']:+,.2f}")

    # Performance summary
    summary = portfolio.get_performance_summary(current_prices)
    print(f"\n" + "="*60)
    print("Performance Summary")
    print("="*60)
    print(f"Total Return: ${summary['total_return']:+,.2f} ({summary['total_return_pct']:+.2%})")
    print(f"Win Rate: {summary['win_rate']:.1%}")
    print(f"Total Trades: {summary['total_trades']}")

    print("\n✓ Portfolio test passed!")
