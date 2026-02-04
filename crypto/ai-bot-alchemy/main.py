"""
AI Trading Bot - Main Application Entry Point

Modes:
- train: Train a new ML model
- paper-trade: Run paper trading simulation
- backtest: Historical strategy testing (TODO)
"""

import sys
import time
from datetime import datetime
from pathlib import Path
import click
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_settings
from src.data.data_aggregator import DataAggregator
from src.features.engineering import FeatureEngineer
from src.models.trainer import ModelTrainer
from src.models.predictor import Predictor
from src.trading.signal_generator import SignalGenerator, Signal
from src.trading.portfolio import Portfolio
from src.risk.manager import RiskManager
from src.data.storage import DataStorage


def setup_logging(log_level: str = "INFO"):
    """Configure logging."""
    logger.remove()

    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level
    )

    # File output
    settings = get_settings()
    log_dir = settings.logging.trading_log_dir

    logger.add(
        log_dir / "trading_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG"
    )

    logger.add(
        settings.logging.error_log_dir / "errors_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="90 days",
        level="ERROR"
    )


@click.group()
@click.option('--log-level', default='INFO', help='Logging level')
def cli(log_level):
    """AI Trading Bot - ML-powered cryptocurrency trading."""
    setup_logging(log_level)


@cli.command()
@click.option('--hours', default=168, help='Hours of historical data to fetch (default: 168 = 1 week)')
@click.option('--version', default=None, help='Model version name (default: timestamp)')
@click.option('--tune', is_flag=True, help='Tune hyperparameters (slower)')
def train(hours, version, tune):
    """Train a new ML model on historical data."""

    logger.info("="*60)
    logger.info("TRAINING MODE")
    logger.info("="*60)

    try:
        # 1. Fetch data
        logger.info(f"Fetching {hours} hours of historical data...")
        aggregator = DataAggregator()
        raw_df = aggregator.fetch_training_dataset(hours=hours)

        logger.info(f"Fetched {len(raw_df)} data points")

        # 2. Engineer features
        logger.info("Engineering features...")
        engineer = FeatureEngineer()
        features_df = engineer.engineer_all_features(raw_df, include_target=True)

        logger.info(f"Engineered {len(features_df)} samples with {len(features_df.columns)} features")

        # 3. Prepare training data
        feature_cols = engineer.get_feature_columns()
        X = features_df[feature_cols]
        y = features_df['target']

        logger.info(f"Training with {len(X)} samples, {len(feature_cols)} features")
        logger.info(f"Target distribution: {y.value_counts().to_dict()}")

        # 4. Train model
        logger.info("Training model...")
        trainer = ModelTrainer()
        metrics = trainer.train(X, y, tune_hyperparameters=tune)

        # 5. Display results
        logger.info("="*60)
        logger.info("TRAINING RESULTS")
        logger.info("="*60)
        logger.info(f"Test Accuracy: {metrics['test_metrics']['accuracy']:.2%}")
        logger.info(f"Test Precision: {metrics['test_metrics']['precision']:.2%}")
        logger.info(f"Test Recall: {metrics['test_metrics']['recall']:.2%}")
        logger.info(f"Test F1: {metrics['test_metrics']['f1']:.2%}")
        logger.info(f"CV Mean: {metrics['cv_metrics']['cv_mean']:.2%} (+/- {metrics['cv_metrics']['cv_std']:.2%})")

        logger.info("\nTop 5 Features:")
        for i, (feat, importance) in enumerate(list(metrics['feature_importance'].items())[:5]):
            logger.info(f"  {i+1}. {feat}: {importance:.4f}")

        # 6. Save model
        model_path = trainer.save_model(version=version)
        logger.success(f"\n✓ Model saved to: {model_path}")

        logger.info("\nTo run paper trading with this model:")
        logger.info(f"  python main.py paper-trade")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


@cli.command()
@click.option('--duration', default=3600, help='Duration in seconds (default: 3600 = 1 hour)')
@click.option('--model-version', default='latest', help='Model version to use (default: latest)')
@click.option('--initial-balance', default=10000.0, help='Initial capital (default: $10,000)')
@click.option('--check-interval', default=300, help='Check interval in seconds (default: 300 = 5 min)')
def paper_trade(duration, model_version, initial_balance, check_interval):
    """Run paper trading simulation."""

    logger.info("="*60)
    logger.info("PAPER TRADING MODE")
    logger.info("="*60)
    logger.info(f"Duration: {duration}s | Initial Balance: ${initial_balance:,.2f}")
    logger.info(f"Model: {model_version} | Check Interval: {check_interval}s")
    logger.info("="*60)

    try:
        # Initialize components
        logger.info("Initializing components...")

        aggregator = DataAggregator()
        engineer = FeatureEngineer()
        predictor = Predictor(model_version=model_version)
        signal_generator = SignalGenerator()
        portfolio = Portfolio(initial_balance=initial_balance)
        risk_manager = RiskManager(portfolio)
        storage = DataStorage()

        logger.success("✓ All components initialized")

        # Trading loop
        start_time = datetime.now()
        iteration = 0

        logger.info("\nStarting paper trading loop...")
        logger.info("Press Ctrl+C to stop\n")

        while True:
            iteration += 1
            elapsed = (datetime.now() - start_time).total_seconds()

            if elapsed >= duration:
                logger.info(f"Duration limit reached ({duration}s)")
                break

            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {iteration} | Elapsed: {elapsed:.0f}s / {duration}s")
            logger.info(f"{'='*60}")

            try:
                # 1. Fetch latest data
                logger.info("Fetching latest market data...")
                latest_raw = aggregator.fetch_latest_features()

                current_price = latest_raw['price'].values[0]
                logger.info(f"Current ETH price: ${current_price:,.2f}")

                # 2. Engineer features
                latest_features = engineer.engineer_all_features(latest_raw, include_target=False)

                # 3. Get prediction
                prediction, confidence = predictor.predict(latest_features)

                logger.info(f"Prediction: {prediction} ({'UP' if prediction == 1 else 'DOWN'})")
                logger.info(f"Confidence: {confidence:.2%}")

                # Store prediction
                storage.store_prediction(
                    prediction=prediction,
                    confidence=confidence,
                    model_version=model_version
                )

                # 4. Generate signal
                signal, reasoning = signal_generator.generate_signal(prediction, confidence)

                logger.info(f"Signal: {signal.value}")

                # 5. Current prices for portfolio calculation
                current_prices = {"ETH": current_price}

                # 6. Execute trades based on signal
                if signal == Signal.BUY and not portfolio.has_position("ETH"):
                    # Calculate position size
                    position_size_pct = get_settings().strategy.base_position_size_pct
                    total_equity = portfolio.get_total_equity(current_prices)
                    trade_value = total_equity * position_size_pct
                    quantity = trade_value / current_price

                    # Validate trade
                    is_valid, reason = risk_manager.validate_trade(
                        "ETH", "BUY", quantity, current_price, current_prices
                    )

                    if is_valid:
                        success = portfolio.open_position("ETH", quantity, current_price)

                        if success:
                            logger.success(f"✓ BUY executed: {quantity:.4f} ETH @ ${current_price:,.2f}")

                            storage.store_trade(
                                side="BUY",
                                quantity=quantity,
                                price=current_price,
                                signal_confidence=confidence
                            )
                    else:
                        logger.warning(f"✗ Trade rejected: {reason}")

                elif signal == Signal.SELL and portfolio.has_position("ETH"):
                    # Close position
                    trade_result = portfolio.close_position("ETH", current_price)

                    if trade_result:
                        logger.success(
                            f"✓ SELL executed: {trade_result['quantity']:.4f} ETH @ ${current_price:,.2f} "
                            f"(P&L: ${trade_result['pnl']:+,.2f} / {trade_result['pnl_pct']:+.2%})"
                        )

                        storage.store_trade(
                            side="SELL",
                            quantity=trade_result['quantity'],
                            price=current_price,
                            signal_confidence=confidence,
                            notes=f"P&L: ${trade_result['pnl']:+,.2f}"
                        )

                # 7. Check stop loss on open positions
                if portfolio.has_position("ETH"):
                    position = portfolio.get_position("ETH")
                    pnl = position.get_pnl(current_price)

                    logger.info(f"Open position P&L: ${pnl['pnl']:+,.2f} ({pnl['pnl_pct']:+.2%})")

                    should_close = signal_generator.should_close_position(pnl['pnl_pct'], confidence)

                    if should_close:
                        logger.warning("Stop loss or confidence threshold triggered!")
                        trade_result = portfolio.close_position("ETH", current_price)

                        if trade_result:
                            logger.info(f"Position closed: P&L ${trade_result['pnl']:+,.2f}")

                # 8. Display portfolio status
                summary = portfolio.get_performance_summary(current_prices)

                logger.info(f"\n{'─'*60}")
                logger.info("PORTFOLIO STATUS")
                logger.info(f"{'─'*60}")
                logger.info(f"Total Equity: ${summary['total_equity']:,.2f}")
                logger.info(f"Cash: ${summary['current_cash']:,.2f}")
                logger.info(f"Total Return: ${summary['total_return']:+,.2f} ({summary['total_return_pct']:+.2%})")
                logger.info(f"Open Positions: {summary['open_positions']}")
                logger.info(f"Total Trades: {summary['total_trades']} (W: {summary['winning_trades']}, L: {summary['losing_trades']})")
                logger.info(f"Win Rate: {summary['win_rate']:.1%}")

                # 9. Wait for next check
                logger.info(f"\nWaiting {check_interval}s until next check...")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("\nInterrupted by user")
                break

            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                logger.error(f"Waiting {check_interval}s before retry...")
                time.sleep(check_interval)
                continue

        # Final summary
        logger.info("\n" + "="*60)
        logger.info("PAPER TRADING COMPLETE")
        logger.info("="*60)

        final_summary = portfolio.get_performance_summary({"ETH": current_price})

        logger.info(f"Initial Balance: ${final_summary['initial_balance']:,.2f}")
        logger.info(f"Final Equity: ${final_summary['total_equity']:,.2f}")
        logger.info(f"Total Return: ${final_summary['total_return']:+,.2f} ({final_summary['total_return_pct']:+.2%})")
        logger.info(f"Total Trades: {final_summary['total_trades']}")
        logger.info(f"Win Rate: {final_summary['win_rate']:.1%}")
        logger.info(f"Max Drawdown: {final_summary['drawdown_pct']:.2%}")

        logger.success("\n✓ Paper trading session complete!")

    except Exception as e:
        logger.error(f"Paper trading failed: {e}")
        raise


@cli.command()
def status():
    """Show bot status and available models."""

    logger.info("="*60)
    logger.info("AI TRADING BOT STATUS")
    logger.info("="*60)

    try:
        settings = get_settings()

        # Check models
        models_dir = settings.data.models_dir
        model_dirs = [d for d in models_dir.iterdir() if d.is_dir()]

        logger.info(f"\nAvailable Models: {len(model_dirs)}")
        for model_dir in sorted(model_dirs, key=lambda d: d.stat().st_mtime, reverse=True)[:5]:
            logger.info(f"  - {model_dir.name}")

        # Check storage
        storage = DataStorage()
        perf_summary = storage.get_performance_summary()

        if 'total_trades' in perf_summary:
            logger.info(f"\nTrading History:")
            logger.info(f"  Total Trades: {perf_summary['total_trades']}")
            logger.info(f"  Total Volume: ${perf_summary['total_volume']:,.2f}")
            logger.info(f"  First Trade: {perf_summary['first_trade']}")
            logger.info(f"  Last Trade: {perf_summary['last_trade']}")
        else:
            logger.info(f"\nNo trading history yet")

        logger.info("\n✓ Status check complete")

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise


if __name__ == '__main__':
    cli()
