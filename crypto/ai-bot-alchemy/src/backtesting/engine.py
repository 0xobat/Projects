"""
Backtesting engine for strategy validation.

Simulates trading strategies on historical data to evaluate performance
before deploying capital in live markets.
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
import pandas as pd
from loguru import logger

from src.trading.portfolio import Portfolio
from src.risk.manager import RiskManager


@dataclass
class BacktestConfig:
    """Backtesting configuration."""

    initial_balance: float = 10000.0
    commission_pct: float = 0.001  # 0.1% per trade
    slippage_pct: float = 0.0005   # 0.05% slippage

    # Risk parameters (override defaults)
    max_position_size_pct: Optional[float] = None
    max_daily_loss_pct: Optional[float] = None
    max_drawdown_pct: Optional[float] = None


@dataclass
class Trade:
    """Record of a single trade."""

    timestamp: datetime
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: float
    price: float
    commission: float
    pnl: float = 0.0
    pnl_pct: float = 0.0


@dataclass
class BacktestResult:
    """Complete backtesting results."""

    # Performance metrics
    total_return: float = 0.0
    total_return_pct: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0

    # Trade statistics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0

    # Equity curve
    equity_curve: List[Dict] = field(default_factory=list)

    # Trade log
    trades: List[Trade] = field(default_factory=list)

    # Timing
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_days: float = 0.0


class BacktestEngine:
    """
    Backtesting engine for strategy evaluation.

    Usage:
        >>> engine = BacktestEngine(config)
        >>> result = engine.run(historical_data, strategy_func)
        >>> print(f"Total return: {result.total_return_pct:.2%}")
    """

    def __init__(self, config: BacktestConfig):
        """
        Initialize backtesting engine.

        Args:
            config: Backtesting configuration
        """
        self.config = config
        self.portfolio = Portfolio(initial_balance=config.initial_balance)
        self.risk_manager = RiskManager(self.portfolio)

        # Override risk parameters if specified
        if config.max_position_size_pct:
            self.risk_manager.settings.risk.max_position_size_pct = config.max_position_size_pct
        if config.max_daily_loss_pct:
            self.risk_manager.settings.risk.max_daily_loss_pct = config.max_daily_loss_pct
        if config.max_drawdown_pct:
            self.risk_manager.settings.risk.max_drawdown_pct = config.max_drawdown_pct

        self.trades: List[Trade] = []
        self.equity_curve: List[Dict] = []

        logger.info(f"Backtest engine initialized with ${config.initial_balance:,.2f}")

    def run(
        self,
        data: pd.DataFrame,
        strategy: Callable[[pd.DataFrame, int], tuple[str, float]]
    ) -> BacktestResult:
        """
        Run backtest on historical data.

        Args:
            data: Historical OHLCV data with features
                  Required columns: timestamp, open, high, low, close, volume
            strategy: Strategy function that returns (signal, confidence)
                     Takes (data, current_index) and returns ('BUY'/'SELL'/'HOLD', confidence)

        Returns:
            BacktestResult with performance metrics

        Example:
            >>> def my_strategy(data, idx):
            ...     if data.loc[idx, 'rsi'] < 30:
            ...         return 'BUY', 0.8
            ...     elif data.loc[idx, 'rsi'] > 70:
            ...         return 'SELL', 0.8
            ...     return 'HOLD', 0.0
            >>>
            >>> result = engine.run(historical_data, my_strategy)
        """
        logger.info("="*60)
        logger.info("Starting backtest")
        logger.info("="*60)

        # Validate data
        required_cols = ['timestamp', 'close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Reset state
        self.portfolio = Portfolio(initial_balance=self.config.initial_balance)
        self.risk_manager = RiskManager(self.portfolio)
        self.trades = []
        self.equity_curve = []

        start_date = data['timestamp'].iloc[0]
        end_date = data['timestamp'].iloc[-1]

        logger.info(f"Period: {start_date} to {end_date}")
        logger.info(f"Data points: {len(data)}")

        # Main backtest loop
        for idx in range(len(data)):
            row = data.iloc[idx]
            timestamp = row['timestamp']
            price = row['close']

            # Track equity
            current_prices = {"ETH": price}  # Hardcoded for now
            equity = self.portfolio.get_total_equity(current_prices)

            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': equity,
                'cash': self.portfolio.cash,
                'positions_value': equity - self.portfolio.cash
            })

            # Get signal from strategy
            signal, confidence = strategy(data, idx)

            # Execute trades based on signal
            if signal == 'BUY' and not self.portfolio.has_position("ETH"):
                self._execute_buy("ETH", price, confidence, timestamp, current_prices)

            elif signal == 'SELL' and self.portfolio.has_position("ETH"):
                self._execute_sell("ETH", price, timestamp)

        # Close any remaining positions at end
        if self.portfolio.has_position("ETH"):
            final_price = data['close'].iloc[-1]
            self._execute_sell("ETH", final_price, data['timestamp'].iloc[-1])

        # Calculate results
        result = self._calculate_results(start_date, end_date)

        logger.info("="*60)
        logger.info("Backtest complete")
        logger.info("="*60)
        self._log_results(result)

        return result

    def _execute_buy(
        self,
        symbol: str,
        price: float,
        confidence: float,
        timestamp: datetime,
        current_prices: Dict[str, float]
    ):
        """Execute a BUY order in backtest."""

        # Calculate position size (fixed percentage for now)
        total_equity = self.portfolio.get_total_equity(current_prices)
        position_pct = 0.10  # 10% of equity per trade
        trade_value = total_equity * position_pct
        quantity = trade_value / price

        # Apply slippage
        execution_price = price * (1 + self.config.slippage_pct)

        # Validate trade
        is_valid, reason = self.risk_manager.validate_trade(
            symbol, "BUY", quantity, execution_price, current_prices
        )

        if not is_valid:
            logger.debug(f"Trade rejected: {reason}")
            return

        # Execute
        success = self.portfolio.open_position(symbol, quantity, execution_price)

        if success:
            # Calculate commission
            commission = trade_value * self.config.commission_pct
            self.portfolio.cash -= commission

            # Record trade
            trade = Trade(
                timestamp=timestamp,
                symbol=symbol,
                side='BUY',
                quantity=quantity,
                price=execution_price,
                commission=commission
            )
            self.trades.append(trade)

            logger.debug(
                f"BUY: {quantity:.4f} {symbol} @ ${execution_price:,.2f} "
                f"(commission: ${commission:.2f})"
            )

    def _execute_sell(self, symbol: str, price: float, timestamp: datetime):
        """Execute a SELL order in backtest."""

        # Apply slippage
        execution_price = price * (1 - self.config.slippage_pct)

        # Get position details before closing
        position = self.portfolio.get_position(symbol)
        if not position:
            return

        quantity = position.quantity
        trade_value = quantity * execution_price

        # Close position
        result = self.portfolio.close_position(symbol, execution_price)

        if result:
            # Calculate commission
            commission = trade_value * self.config.commission_pct
            self.portfolio.cash -= commission

            # Record trade
            trade = Trade(
                timestamp=timestamp,
                symbol=symbol,
                side='SELL',
                quantity=quantity,
                price=execution_price,
                commission=commission,
                pnl=result['pnl'] - commission,
                pnl_pct=result['pnl_pct']
            )
            self.trades.append(trade)

            logger.debug(
                f"SELL: {quantity:.4f} {symbol} @ ${execution_price:,.2f} "
                f"(P&L: ${trade.pnl:+,.2f} / {trade.pnl_pct:+.2%}, commission: ${commission:.2f})"
            )

    def _calculate_results(self, start_date: datetime, end_date: datetime) -> BacktestResult:
        """Calculate comprehensive backtest results."""

        result = BacktestResult()

        # Basic info
        result.start_date = start_date
        result.end_date = end_date
        result.duration_days = (end_date - start_date).total_seconds() / 86400

        # Equity curve
        result.equity_curve = self.equity_curve

        # Trade log
        result.trades = self.trades

        # Performance metrics
        initial_balance = self.config.initial_balance
        final_equity = self.equity_curve[-1]['equity'] if self.equity_curve else initial_balance

        result.total_return = final_equity - initial_balance
        result.total_return_pct = result.total_return / initial_balance if initial_balance > 0 else 0

        # Drawdown
        peak_equity = initial_balance
        max_dd = 0.0

        for point in self.equity_curve:
            equity = point['equity']
            if equity > peak_equity:
                peak_equity = equity

            drawdown = peak_equity - equity
            if drawdown > max_dd:
                max_dd = drawdown

        result.max_drawdown = max_dd
        result.max_drawdown_pct = max_dd / peak_equity if peak_equity > 0 else 0

        # Sharpe ratio (simplified - using trade returns)
        if len(self.trades) > 1:
            returns = [t.pnl_pct for t in self.trades if t.side == 'SELL']
            if returns:
                import numpy as np
                mean_return = np.mean(returns)
                std_return = np.std(returns)
                result.sharpe_ratio = mean_return / std_return if std_return > 0 else 0

        # Trade statistics
        sell_trades = [t for t in self.trades if t.side == 'SELL']
        result.total_trades = len(sell_trades)

        if sell_trades:
            winning = [t for t in sell_trades if t.pnl > 0]
            losing = [t for t in sell_trades if t.pnl <= 0]

            result.winning_trades = len(winning)
            result.losing_trades = len(losing)
            result.win_rate = result.winning_trades / result.total_trades

            result.avg_win = sum(t.pnl for t in winning) / len(winning) if winning else 0
            result.avg_loss = sum(t.pnl for t in losing) / len(losing) if losing else 0

            total_wins = sum(t.pnl for t in winning)
            total_losses = abs(sum(t.pnl for t in losing))
            result.profit_factor = total_wins / total_losses if total_losses > 0 else 0

        return result

    def _log_results(self, result: BacktestResult):
        """Log backtest results."""

        logger.info(f"Total Return: ${result.total_return:+,.2f} ({result.total_return_pct:+.2%})")
        logger.info(f"Max Drawdown: ${result.max_drawdown:,.2f} ({result.max_drawdown_pct:.2%})")
        logger.info(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        logger.info(f"")
        logger.info(f"Total Trades: {result.total_trades}")
        logger.info(f"Win Rate: {result.win_rate:.1%} ({result.winning_trades}W / {result.losing_trades}L)")
        logger.info(f"Avg Win: ${result.avg_win:,.2f}")
        logger.info(f"Avg Loss: ${result.avg_loss:,.2f}")
        logger.info(f"Profit Factor: {result.profit_factor:.2f}")
        logger.info(f"Duration: {result.duration_days:.1f} days")
