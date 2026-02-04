"""
Data storage module using SQLite.

Stores:
- Historical market data
- Model predictions
- Trade executions
- Performance metrics

This provides a lightweight database for tracking bot activity and
analyzing performance over time.
"""

from datetime import datetime
from typing import Optional, List, Dict
import pandas as pd
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Boolean,
    Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from config.settings import get_settings


Base = declarative_base()


class MarketData(Base):
    """Market data time series."""
    __tablename__ = 'market_data'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(10), nullable=False, default='ETH')
    price = Column(Float, nullable=False)
    gas_used = Column(Integer)
    transaction_count = Column(Integer)
    whale_score = Column(Float, default=0.0)


class Prediction(Base):
    """Model predictions."""
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(10), nullable=False, default='ETH')
    prediction = Column(Integer, nullable=False)  # 0 or 1
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    model_version = Column(String(50))
    features_json = Column(Text)  # JSON string of input features


class Trade(Base):
    """Trade executions."""
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(10), nullable=False, default='ETH')
    side = Column(String(4), nullable=False)  # 'BUY' or 'SELL'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    is_paper = Column(Boolean, default=True)
    signal_confidence = Column(Float)
    notes = Column(Text)


class Performance(Base):
    """Daily performance metrics."""
    __tablename__ = 'performance'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    starting_balance = Column(Float, nullable=False)
    ending_balance = Column(Float, nullable=False)
    pnl = Column(Float, nullable=False)
    pnl_pct = Column(Float, nullable=False)
    num_trades = Column(Integer, default=0)
    num_wins = Column(Integer, default=0)
    num_losses = Column(Integer, default=0)
    max_drawdown_pct = Column(Float)


class DataStorage:
    """Database storage manager."""

    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize database connection.

        Args:
            db_url: SQLAlchemy database URL (default: SQLite in data/ directory)
        """
        settings = get_settings()

        if db_url is None:
            db_path = settings.data.data_dir / "trading.db"
            db_url = f"sqlite:///{db_path}"

        logger.info(f"Initializing database: {db_url}")

        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)

        logger.info("Database initialized successfully")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def store_market_data(self, df: pd.DataFrame):
        """
        Store market data from DataFrame.

        Args:
            df: DataFrame with columns: timestamp, price, gas_used, transaction_count, whale_score

        Example:
            >>> storage = DataStorage()
            >>> storage.store_market_data(market_df)
        """
        try:
            with self.get_session() as session:
                for _, row in df.iterrows():
                    market_data = MarketData(
                        timestamp=row['timestamp'],
                        price=row['price'],
                        gas_used=row.get('gas_used'),
                        transaction_count=row.get('transaction_count'),
                        whale_score=row.get('whale_score', 0.0)
                    )
                    session.add(market_data)

                session.commit()
                logger.debug(f"Stored {len(df)} market data points")

        except Exception as e:
            logger.error(f"Failed to store market data: {e}")
            raise

    def store_prediction(
        self,
        prediction: int,
        confidence: float,
        model_version: str,
        features: Optional[Dict] = None
    ):
        """
        Store a model prediction.

        Args:
            prediction: Predicted class (0 or 1)
            confidence: Prediction confidence (0.0 to 1.0)
            model_version: Model identifier
            features: Optional dictionary of input features
        """
        try:
            import json

            with self.get_session() as session:
                pred = Prediction(
                    timestamp=datetime.now(),
                    prediction=prediction,
                    confidence=confidence,
                    model_version=model_version,
                    features_json=json.dumps(features) if features else None
                )
                session.add(pred)
                session.commit()

                logger.debug(f"Stored prediction: {prediction} (confidence: {confidence:.2%})")

        except Exception as e:
            logger.error(f"Failed to store prediction: {e}")
            raise

    def store_trade(
        self,
        side: str,
        quantity: float,
        price: float,
        is_paper: bool = True,
        signal_confidence: Optional[float] = None,
        notes: Optional[str] = None
    ):
        """
        Store a trade execution.

        Args:
            side: 'BUY' or 'SELL'
            quantity: Quantity traded
            price: Execution price
            is_paper: Whether this is paper trading (default: True)
            signal_confidence: Optional signal confidence
            notes: Optional notes
        """
        try:
            with self.get_session() as session:
                trade = Trade(
                    timestamp=datetime.now(),
                    side=side.upper(),
                    quantity=quantity,
                    price=price,
                    total_value=quantity * price,
                    is_paper=is_paper,
                    signal_confidence=signal_confidence,
                    notes=notes
                )
                session.add(trade)
                session.commit()

                logger.info(
                    f"Stored trade: {side} {quantity:.4f} @ ${price:,.2f} "
                    f"({'PAPER' if is_paper else 'LIVE'})"
                )

        except Exception as e:
            logger.error(f"Failed to store trade: {e}")
            raise

    def get_recent_trades(self, limit: int = 10) -> List[Trade]:
        """Get recent trades."""
        with self.get_session() as session:
            return session.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()

    def get_market_data(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Retrieve market data as DataFrame.

        Args:
            start_time: Optional start timestamp
            end_time: Optional end timestamp

        Returns:
            DataFrame with market data
        """
        with self.get_session() as session:
            query = session.query(MarketData)

            if start_time:
                query = query.filter(MarketData.timestamp >= start_time)
            if end_time:
                query = query.filter(MarketData.timestamp <= end_time)

            query = query.order_by(MarketData.timestamp)

            # Convert to DataFrame
            data = query.all()
            if not data:
                return pd.DataFrame()

            df = pd.DataFrame([{
                'timestamp': d.timestamp,
                'price': d.price,
                'gas_used': d.gas_used,
                'transaction_count': d.transaction_count,
                'whale_score': d.whale_score
            } for d in data])

            return df

    def get_performance_summary(self) -> Dict:
        """
        Get overall performance summary.

        Returns:
            Dictionary with performance statistics
        """
        with self.get_session() as session:
            trades = session.query(Trade).all()

            if not trades:
                return {'message': 'No trades yet'}

            total_trades = len(trades)
            buy_trades = [t for t in trades if t.side == 'BUY']
            sell_trades = [t for t in trades if t.side == 'SELL']

            return {
                'total_trades': total_trades,
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades),
                'total_volume': sum(t.total_value for t in trades),
                'avg_trade_size': sum(t.total_value for t in trades) / total_trades,
                'first_trade': min(t.timestamp for t in trades),
                'last_trade': max(t.timestamp for t in trades)
            }


if __name__ == "__main__":
    # Test storage
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    # Initialize storage
    storage = DataStorage()

    # Test storing market data
    test_df = pd.DataFrame([{
        'timestamp': datetime.now(),
        'price': 3000.0,
        'gas_used': 15000000,
        'transaction_count': 150,
        'whale_score': 0.5
    }])

    storage.store_market_data(test_df)

    # Test storing prediction
    storage.store_prediction(
        prediction=1,
        confidence=0.75,
        model_version="rf_v1"
    )

    # Test storing trade
    storage.store_trade(
        side='BUY',
        quantity=0.5,
        price=3000.0,
        signal_confidence=0.75
    )

    # Get performance summary
    summary = storage.get_performance_summary()
    print(f"\nPerformance Summary:")
    print(summary)

    print("\nStorage test completed successfully!")
