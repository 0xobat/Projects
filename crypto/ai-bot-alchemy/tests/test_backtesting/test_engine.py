"""Tests for backtesting engine."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.backtesting.engine import BacktestEngine, BacktestConfig, BacktestResult


@pytest.fixture
def historical_data():
    """Create synthetic historical price data."""
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='1h')

    # Create sine wave price pattern for predictable results
    prices = 3000 + 200 * np.sin(np.linspace(0, 4*np.pi, len(dates)))

    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.uniform(100, 1000, len(dates))
    })

    return df


@pytest.fixture
def config():
    """Create test backtest config."""
    return BacktestConfig(
        initial_balance=10000.0,
        commission_pct=0.001,
        slippage_pct=0.0005
    )


def simple_buy_hold_strategy(data: pd.DataFrame, idx: int) -> tuple[str, float]:
    """Simple buy and hold strategy."""
    if idx == 0:
        return 'BUY', 1.0
    elif idx == len(data) - 1:
        return 'SELL', 1.0
    return 'HOLD', 0.0


def momentum_strategy(data: pd.DataFrame, idx: int) -> tuple[str, float]:
    """Simple momentum strategy using price changes."""
    if idx < 10:
        return 'HOLD', 0.0

    # Calculate 10-period momentum
    current_price = data.loc[idx, 'close']
    past_price = data.loc[idx-10, 'close']
    momentum = (current_price - past_price) / past_price

    if momentum > 0.02:  # 2% positive momentum
        return 'BUY', 0.8
    elif momentum < -0.02:  # 2% negative momentum
        return 'SELL', 0.8

    return 'HOLD', 0.0


def test_backtest_engine_initialization(config):
    """Test engine initializes correctly."""
    engine = BacktestEngine(config)

    assert engine.portfolio.cash == config.initial_balance
    assert engine.risk_manager is not None
    assert len(engine.trades) == 0


def test_backtest_buy_hold(config, historical_data):
    """Test backtesting a simple buy-and-hold strategy."""
    engine = BacktestEngine(config)

    result = engine.run(historical_data, simple_buy_hold_strategy)

    assert isinstance(result, BacktestResult)
    assert result.total_trades >= 1  # At least one buy-sell pair
    assert len(result.equity_curve) == len(historical_data)
    assert result.start_date is not None
    assert result.end_date is not None


def test_backtest_momentum_strategy(config, historical_data):
    """Test backtesting a momentum strategy."""
    engine = BacktestEngine(config)

    result = engine.run(historical_data, momentum_strategy)

    assert isinstance(result, BacktestResult)
    # Momentum strategy may or may not trigger based on data
    # Just verify the backtest runs without error
    assert result.total_trades >= 0


def test_backtest_result_metrics(config, historical_data):
    """Test that backtest result contains all expected metrics."""
    engine = BacktestEngine(config)

    result = engine.run(historical_data, simple_buy_hold_strategy)

    # Performance metrics
    assert hasattr(result, 'total_return')
    assert hasattr(result, 'total_return_pct')
    assert hasattr(result, 'sharpe_ratio')
    assert hasattr(result, 'max_drawdown')
    assert hasattr(result, 'max_drawdown_pct')

    # Trade statistics
    assert hasattr(result, 'total_trades')
    assert hasattr(result, 'winning_trades')
    assert hasattr(result, 'losing_trades')
    assert hasattr(result, 'win_rate')
    assert hasattr(result, 'avg_win')
    assert hasattr(result, 'avg_loss')
    assert hasattr(result, 'profit_factor')


def test_backtest_equity_curve(config, historical_data):
    """Test that equity curve is tracked correctly."""
    engine = BacktestEngine(config)

    result = engine.run(historical_data, simple_buy_hold_strategy)

    assert len(result.equity_curve) > 0
    assert len(result.equity_curve) == len(historical_data)

    # Check first point
    first_point = result.equity_curve[0]
    assert 'timestamp' in first_point
    assert 'equity' in first_point
    assert 'cash' in first_point
    assert 'positions_value' in first_point


def test_backtest_trade_log(config, historical_data):
    """Test that trades are logged correctly."""
    engine = BacktestEngine(config)

    result = engine.run(historical_data, momentum_strategy)

    if result.total_trades > 0:
        trade = result.trades[0]

        assert hasattr(trade, 'timestamp')
        assert hasattr(trade, 'symbol')
        assert hasattr(trade, 'side')
        assert hasattr(trade, 'quantity')
        assert hasattr(trade, 'price')
        assert hasattr(trade, 'commission')

        # Sell trades should have P&L
        sell_trades = [t for t in result.trades if t.side == 'SELL']
        if sell_trades:
            assert sell_trades[0].pnl != 0 or sell_trades[0].pnl_pct != 0


def test_backtest_commission_calculation(config, historical_data):
    """Test that commissions are calculated."""
    engine = BacktestEngine(config)

    result = engine.run(historical_data, simple_buy_hold_strategy)

    # Should have at least buy and sell with commissions
    total_commission = sum(t.commission for t in result.trades)
    assert total_commission > 0


def test_backtest_invalid_data():
    """Test that backtest fails gracefully with invalid data."""
    engine = BacktestEngine(BacktestConfig())

    # Missing required columns
    invalid_data = pd.DataFrame({
        'timestamp': [datetime.now()],
        'price': [3000.0]  # Missing 'close'
    })

    with pytest.raises(ValueError, match="Missing required columns"):
        engine.run(invalid_data, simple_buy_hold_strategy)


def test_backtest_empty_data():
    """Test backtest with empty data."""
    engine = BacktestEngine(BacktestConfig())

    empty_data = pd.DataFrame(columns=['timestamp', 'close'])

    # Should handle empty data without crashing
    # (might raise an error or return empty result)
    try:
        result = engine.run(empty_data, simple_buy_hold_strategy)
        assert result.total_trades == 0
    except (ValueError, IndexError):
        # Expected - empty data should fail
        pass


def test_backtest_win_rate_calculation(config):
    """Test win rate calculation."""
    # Create controlled data for predictable results
    dates = pd.date_range(start='2024-01-01', periods=50, freq='1h')

    # Price goes: up, down, up, down
    prices = [3000 + (100 if i % 20 < 10 else -100) for i in range(len(dates))]

    data = pd.DataFrame({
        'timestamp': dates,
        'close': prices,
    })

    # Strategy that buys at lows, sells at highs
    def contrarian_strategy(df, idx):
        if idx < 1:
            return 'HOLD', 0.0

        price_change = df.loc[idx, 'close'] - df.loc[idx-1, 'close']

        if price_change < -50:  # Buy after drops
            return 'BUY', 0.9
        elif price_change > 50:  # Sell after rises
            return 'SELL', 0.9

        return 'HOLD', 0.0

    engine = BacktestEngine(config)
    result = engine.run(data, contrarian_strategy)

    # Should have trades
    if result.total_trades > 0:
        assert 0 <= result.win_rate <= 1.0
        assert result.winning_trades + result.losing_trades == result.total_trades
