"""Tests for risk manager."""

import pytest
from src.risk.manager import RiskManager
from src.trading.portfolio import Portfolio


@pytest.fixture
def portfolio():
    """Create a test portfolio."""
    return Portfolio(initial_balance=10000.0)


@pytest.fixture
def risk_manager(portfolio):
    """Create a test risk manager."""
    return RiskManager(portfolio)


def test_risk_manager_initialization(risk_manager):
    """Test risk manager initializes correctly."""
    assert risk_manager.portfolio is not None
    assert risk_manager.circuit_breaker_triggered is False


def test_validate_valid_buy(risk_manager):
    """Test validating a valid buy order."""
    current_prices = {"ETH": 3000.0}

    is_valid, reason = risk_manager.validate_trade(
        symbol="ETH",
        side="BUY",
        quantity=0.5,
        price=3000.0,
        current_prices=current_prices
    )

    assert is_valid is True
    assert "approved" in reason.lower()


def test_validate_oversized_position(risk_manager):
    """Test rejecting oversized position."""
    current_prices = {"ETH": 3000.0}

    # Try to buy $30,000 worth (300% of equity)
    is_valid, reason = risk_manager.validate_trade(
        symbol="ETH",
        side="BUY",
        quantity=10.0,
        price=3000.0,
        current_prices=current_prices
    )

    assert is_valid is False
    assert "position size" in reason.lower()


def test_validate_duplicate_position(risk_manager, portfolio):
    """Test rejecting duplicate position."""
    current_prices = {"ETH": 3000.0}

    # Open initial position
    portfolio.open_position("ETH", 0.5, 3000.0)

    # Try to open another
    is_valid, reason = risk_manager.validate_trade(
        symbol="ETH",
        side="BUY",
        quantity=0.5,
        price=3000.0,
        current_prices=current_prices
    )

    assert is_valid is False
    assert "already holding" in reason.lower()


def test_validate_insufficient_funds(risk_manager):
    """Test rejecting trade with insufficient funds or oversized position."""
    current_prices = {"ETH": 3000.0}

    # Try to buy more than we have cash for
    # (Will be rejected for position size OR insufficient funds)
    is_valid, reason = risk_manager.validate_trade(
        symbol="ETH",
        side="BUY",
        quantity=5.0,  # $15,000 worth, but only have $10k
        price=3000.0,
        current_prices=current_prices
    )

    assert is_valid is False
    # Can fail for either position size or insufficient funds
    assert ("insufficient funds" in reason.lower() or "position size" in reason.lower())


def test_circuit_breaker_trigger(risk_manager, portfolio):
    """Test circuit breaker triggers on max drawdown or daily loss."""
    # Open a position
    portfolio.open_position("ETH", 1.0, 3000.0)

    # Simulate huge loss (price drops 80%)
    current_prices = {"ETH": 600.0}

    is_valid, reason = risk_manager.validate_trade(
        symbol="BTC",
        side="BUY",
        quantity=0.1,
        price=50000.0,
        current_prices=current_prices
    )

    assert is_valid is False
    # Will trigger either circuit breaker or daily loss limit
    assert ("circuit breaker" in reason.lower() or "daily loss" in reason.lower() or "drawdown" in reason.lower())


def test_calculate_position_size(risk_manager):
    """Test position size calculation with confidence adjustment."""
    current_prices = {"ETH": 3000.0}

    # High confidence
    size_high = risk_manager.calculate_position_size(
        symbol="ETH",
        entry_price=3000.0,
        confidence=0.9,
        current_prices=current_prices
    )

    # Low confidence
    size_low = risk_manager.calculate_position_size(
        symbol="ETH",
        entry_price=3000.0,
        confidence=0.5,
        current_prices=current_prices
    )

    # High confidence should result in larger position
    assert size_high > size_low


def test_get_risk_status(risk_manager, portfolio):
    """Test getting risk status."""
    current_prices = {"ETH": 3000.0}

    portfolio.open_position("ETH", 0.5, 3000.0)

    status = risk_manager.get_risk_status(current_prices)

    assert 'circuit_breaker_triggered' in status
    assert 'current_equity' in status
    assert 'drawdown_pct' in status
    assert 'current_positions' in status
    assert status['current_positions'] == 1


def test_check_position_risk(risk_manager, portfolio):
    """Test checking position risk metrics."""
    # No position initially
    risk = risk_manager.check_position_risk("ETH", 3000.0)
    assert risk['has_position'] is False

    # Open position
    portfolio.open_position("ETH", 1.0, 3000.0)

    # Check risk when profitable
    risk = risk_manager.check_position_risk("ETH", 3500.0)
    assert risk['has_position'] is True
    assert risk['pnl'] > 0
    assert risk['should_close'] is False

    # Check risk when hitting stop loss
    risk = risk_manager.check_position_risk("ETH", 2700.0)  # -10% loss
    assert risk['should_close'] is True
