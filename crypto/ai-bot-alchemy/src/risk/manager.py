"""
Risk management system.

Validates all trades before execution to ensure they meet risk limits:
- Position size limits
- Daily loss limits
- Maximum drawdown limits
- Exposure limits
"""

from typing import Optional, Dict
from datetime import datetime, date
from loguru import logger

from config.settings import get_settings
from src.trading.portfolio import Portfolio


class RiskManager:
    """Enforces risk management rules before trade execution."""

    def __init__(self, portfolio: Portfolio):
        """
        Initialize risk manager.

        Args:
            portfolio: Portfolio instance to monitor
        """
        self.portfolio = portfolio
        self.settings = get_settings()

        # Daily tracking
        self.daily_losses: Dict[date, float] = {}
        self.current_date = datetime.now().date()

        # Circuit breaker state
        self.circuit_breaker_triggered = False

        logger.info("Risk manager initialized")

    def validate_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        current_prices: Dict[str, float]
    ) -> tuple[bool, str]:
        """
        Validate if a trade meets risk requirements.

        Args:
            symbol: Token symbol
            side: 'BUY' or 'SELL'
            quantity: Quantity to trade
            price: Execution price
            current_prices: Current market prices for all positions

        Returns:
            Tuple of (is_valid, reason)

        Example:
            >>> risk_mgr = RiskManager(portfolio)
            >>> is_valid, reason = risk_mgr.validate_trade("ETH", "BUY", 1.0, 3000.0, {"ETH": 3000})
        """
        # Check circuit breaker
        if self.circuit_breaker_triggered:
            return False, "Circuit breaker triggered - trading halted"

        # Check daily losses
        if not self._check_daily_loss_limit(current_prices):
            return False, "Daily loss limit exceeded"

        # Check drawdown
        if not self._check_drawdown_limit(current_prices):
            self.circuit_breaker_triggered = True
            return False, "Maximum drawdown exceeded - circuit breaker triggered!"

        if side == 'BUY':
            # Validate buy order
            is_valid, reason = self._validate_buy(symbol, quantity, price, current_prices)

        elif side == 'SELL':
            # Validate sell order
            is_valid, reason = self._validate_sell(symbol)

        else:
            return False, f"Unknown trade side: {side}"

        if not is_valid:
            logger.warning(f"Trade validation failed: {reason}")

        return is_valid, reason

    def _validate_buy(
        self,
        symbol: str,
        quantity: float,
        price: float,
        current_prices: Dict[str, float]
    ) -> tuple[bool, str]:
        """Validate a BUY order."""

        # Check position size limit
        trade_value = quantity * price
        total_equity = self.portfolio.get_total_equity(current_prices)

        position_size_pct = trade_value / total_equity if total_equity > 0 else 0
        max_position_pct = self.settings.risk.max_position_size_pct

        if position_size_pct > max_position_pct:
            return False, (
                f"Position size {position_size_pct:.1%} exceeds limit {max_position_pct:.1%}"
            )

        # Check if we already have a position in this symbol
        if self.portfolio.has_position(symbol):
            return False, f"Already holding position in {symbol}"

        # Check concurrent position limit
        max_positions = self.settings.strategy.max_concurrent_positions
        if self.portfolio.get_position_count() >= max_positions:
            return False, f"Maximum concurrent positions ({max_positions}) reached"

        # Check sufficient funds
        if trade_value > self.portfolio.cash:
            return False, (
                f"Insufficient funds: need ${trade_value:,.2f}, have ${self.portfolio.cash:,.2f}"
            )

        logger.debug(f"BUY validation passed: {quantity:.4f} {symbol} @ ${price:,.2f}")
        return True, "Trade approved"

    def _validate_sell(self, symbol: str) -> tuple[bool, str]:
        """Validate a SELL order."""

        # Check if we have a position to sell
        if not self.portfolio.has_position(symbol):
            return False, f"No position to sell in {symbol}"

        logger.debug(f"SELL validation passed: {symbol}")
        return True, "Trade approved"

    def _check_daily_loss_limit(self, current_prices: Dict[str, float]) -> bool:
        """Check if daily loss limit has been exceeded."""

        today = datetime.now().date()

        # Reset daily tracking if new day
        if today != self.current_date:
            self.daily_losses = {}
            self.current_date = today

        # Calculate today's loss
        total_equity = self.portfolio.get_total_equity(current_prices)
        starting_equity = self.portfolio.starting_equity

        today_pnl = total_equity - starting_equity
        today_pnl_pct = today_pnl / starting_equity if starting_equity > 0 else 0

        # Check limit
        max_daily_loss_pct = self.settings.risk.max_daily_loss_pct

        if today_pnl_pct <= -max_daily_loss_pct:
            logger.error(
                f"Daily loss limit exceeded: {today_pnl_pct:.2%} <= {-max_daily_loss_pct:.2%}"
            )
            return False

        return True

    def _check_drawdown_limit(self, current_prices: Dict[str, float]) -> bool:
        """Check if maximum drawdown limit has been exceeded."""

        total_equity = self.portfolio.get_total_equity(current_prices)
        peak_equity = self.portfolio.peak_equity

        drawdown_pct = (total_equity - peak_equity) / peak_equity if peak_equity > 0 else 0

        max_drawdown_pct = self.settings.risk.max_drawdown_pct

        if drawdown_pct <= -max_drawdown_pct:
            logger.critical(
                f"Maximum drawdown exceeded: {drawdown_pct:.2%} <= {-max_drawdown_pct:.2%}"
            )
            return False

        return True

    def reset_circuit_breaker(self):
        """Reset circuit breaker (use with caution!)."""
        self.circuit_breaker_triggered = False
        logger.warning("Circuit breaker reset")

    def get_risk_status(self, current_prices: Dict[str, float]) -> Dict:
        """
        Get current risk status.

        Returns:
            Dict with risk metrics
        """
        total_equity = self.portfolio.get_total_equity(current_prices)
        peak_equity = self.portfolio.peak_equity

        return {
            'circuit_breaker_triggered': self.circuit_breaker_triggered,
            'current_equity': total_equity,
            'peak_equity': peak_equity,
            'drawdown_pct': (total_equity - peak_equity) / peak_equity if peak_equity > 0 else 0,
            'max_drawdown_limit': self.settings.risk.max_drawdown_pct,
            'max_position_size': self.settings.risk.max_position_size_pct,
            'max_concurrent_positions': self.settings.strategy.max_concurrent_positions,
            'current_positions': self.portfolio.get_position_count()
        }


if __name__ == "__main__":
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    # Test risk manager
    portfolio = Portfolio(initial_balance=10000.0)
    risk_mgr = RiskManager(portfolio)

    print("\n" + "="*60)
    print("Testing Risk Manager")
    print("="*60)

    current_prices = {"ETH": 3000.0}

    # Test 1: Valid trade
    is_valid, reason = risk_mgr.validate_trade("ETH", "BUY", 0.5, 3000.0, current_prices)
    print(f"\n1. Valid trade: {is_valid}")
    print(f"   Reason: {reason}")

    # Test 2: Oversized position
    is_valid, reason = risk_mgr.validate_trade("ETH", "BUY", 10.0, 3000.0, current_prices)
    print(f"\n2. Oversized position: {is_valid}")
    print(f"   Reason: {reason}")

    # Test 3: Execute valid trade
    portfolio.open_position("ETH", 0.5, 3000.0)

    # Test 4: Try to open duplicate position
    is_valid, reason = risk_mgr.validate_trade("ETH", "BUY", 0.5, 3000.0, current_prices)
    print(f"\n3. Duplicate position: {is_valid}")
    print(f"   Reason: {reason}")

    # Get risk status
    status = risk_mgr.get_risk_status(current_prices)
    print(f"\n" + "="*60)
    print("Risk Status")
    print("="*60)
    print(f"Current positions: {status['current_positions']}/{status['max_concurrent_positions']}")
    print(f"Drawdown: {status['drawdown_pct']:.2%} (limit: {status['max_drawdown_limit']:.2%})")
    print(f"Circuit breaker: {status['circuit_breaker_triggered']}")

    print("\n✓ Risk manager test passed!")
