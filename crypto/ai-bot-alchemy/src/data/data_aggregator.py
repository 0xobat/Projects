"""
Data aggregator - unified pipeline combining all data sources.

This module coordinates data fetching from multiple sources and provides
clean, merged datasets for both training and real-time trading.
"""

from datetime import datetime
from typing import Optional, Dict
import pandas as pd
from loguru import logger

from src.data.blockchain_fetcher import BlockchainFetcher
from src.data.price_fetcher import PriceFetcher
from src.data.whale_monitor import WhaleMonitor
from config.settings import get_settings


class DataAggregator:
    """
    Aggregates data from multiple sources into unified datasets.

    Handles:
    - Blockchain on-chain metrics
    - Price data
    - Whale activity scores
    - Timestamp alignment and merging
    """

    def __init__(self):
        """Initialize data fetchers."""
        self.blockchain_fetcher = BlockchainFetcher()
        self.price_fetcher = PriceFetcher()
        self.whale_monitor = WhaleMonitor()
        self.settings = get_settings()

        # Cache for real-time data
        self._cache: Dict = {}
        self._cache_timestamp: Optional[datetime] = None

    def fetch_training_dataset(
        self,
        hours: int = 168,
        symbol: str = "ETH"
    ) -> pd.DataFrame:
        """
        Fetch complete dataset for model training.

        This fetches historical data from all sources and merges them
        into a single DataFrame suitable for feature engineering and training.

        Args:
            hours: Number of hours of historical data (default: 168 = 1 week)
            symbol: Token symbol (default: "ETH")

        Returns:
            Merged DataFrame with all features

        Example:
            >>> aggregator = DataAggregator()
            >>> df = aggregator.fetch_training_dataset(hours=168)
            >>> # df now contains: price, gas_used, tx_count, whale_score, etc.
        """
        logger.info(f"Fetching training dataset: {hours}h of {symbol} data")

        try:
            # 1. Fetch blockchain data
            logger.info("Fetching blockchain data...")
            blockchain_df = self.blockchain_fetcher.fetch_historical_data(
                hours=hours,
                sample_rate=1  # Hourly samples
            )

            # 2. Fetch price data
            logger.info("Fetching price data...")
            price_df = self.price_fetcher.fetch_historical_prices(
                symbol=symbol,
                hours=hours,
                interval="1h"
            )

            # 3. Merge data sources
            logger.info("Merging data sources...")
            df = self._merge_data(blockchain_df, price_df)

            # 4. Add whale activity placeholder
            # Note: For historical data, we don't have real-time whale data
            # In production, you might store historical whale activity
            df['whale_score'] = 0.0  # Placeholder

            # 5. Validate merged data
            logger.info(f"Training dataset ready: {len(df)} samples, {len(df.columns)} features")
            logger.debug(f"Columns: {df.columns.tolist()}")

            return df

        except Exception as e:
            logger.error(f"Failed to fetch training dataset: {e}")
            raise

    def fetch_latest_features(self, symbol: str = "ETH") -> pd.DataFrame:
        """
        Fetch the latest data point for real-time trading.

        This is optimized for speed and only fetches current data.

        Args:
            symbol: Token symbol (default: "ETH")

        Returns:
            DataFrame with single row of latest features

        Example:
            >>> aggregator = DataAggregator()
            >>> latest = aggregator.fetch_latest_features()
            >>> # Use for real-time prediction
        """
        logger.debug("Fetching latest features for real-time trading")

        try:
            # 1. Fetch latest blockchain data
            blockchain_df = self.blockchain_fetcher.fetch_latest_block()

            # 2. Fetch latest price
            latest_price = self.price_fetcher.fetch_latest_price(symbol)
            price_df = pd.DataFrame([{
                'timestamp': datetime.now(),
                'price': latest_price
            }])

            # 3. Merge
            df = self._merge_data(blockchain_df, price_df)

            # 4. Add whale score (from monitor)
            df['whale_score'] = self.whale_monitor.get_whale_score()

            logger.debug(f"Latest features: price=${latest_price:,.2f}, whale_score={df['whale_score'].values[0]:.3f}")

            return df

        except Exception as e:
            logger.error(f"Failed to fetch latest features: {e}")
            raise

    def _merge_data(
        self,
        blockchain_df: pd.DataFrame,
        price_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge blockchain and price data on timestamps.

        Uses merge_asof to handle slight timestamp mismatches.

        Args:
            blockchain_df: Blockchain data with timestamps
            price_df: Price data with timestamps

        Returns:
            Merged DataFrame
        """
        try:
            # Ensure timestamp columns are datetime
            blockchain_df['timestamp'] = pd.to_datetime(
                blockchain_df['timestamp'],
                unit='s',
                errors='coerce'
            )
            price_df['timestamp'] = pd.to_datetime(
                price_df['timestamp'],
                errors='coerce'
            )

            # Sort by timestamp
            blockchain_df = blockchain_df.sort_values('timestamp')
            price_df = price_df.sort_values('timestamp')

            # Merge using nearest timestamp
            merged_df = pd.merge_asof(
                blockchain_df,
                price_df,
                on='timestamp',
                direction='nearest',
                tolerance=pd.Timedelta('5min')  # Allow 5-minute tolerance
            )

            # Drop rows with missing values
            initial_len = len(merged_df)
            merged_df = merged_df.dropna()
            dropped = initial_len - len(merged_df)

            if dropped > 0:
                logger.warning(f"Dropped {dropped} rows with missing values after merge")

            return merged_df

        except Exception as e:
            logger.error(f"Failed to merge data: {e}")
            raise

    def update_realtime_data(self, symbol: str = "ETH", use_cache: bool = True) -> pd.DataFrame:
        """
        Update and return real-time data with caching.

        This method caches data for a short period to avoid excessive API calls
        during real-time trading loops.

        Args:
            symbol: Token symbol
            use_cache: Whether to use cached data if available (default: True)

        Returns:
            Latest features DataFrame
        """
        # Check cache validity (cache for 1 minute)
        if use_cache and self._cache_timestamp:
            elapsed = (datetime.now() - self._cache_timestamp).total_seconds()
            if elapsed < 60:  # Cache valid for 60 seconds
                logger.debug("Using cached real-time data")
                return self._cache.get('latest_features')

        # Fetch fresh data
        latest_features = self.fetch_latest_features(symbol)

        # Update cache
        self._cache['latest_features'] = latest_features
        self._cache_timestamp = datetime.now()

        return latest_features

    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of a dataset.

        Args:
            df: DataFrame to summarize

        Returns:
            Dictionary with summary statistics
        """
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'time_range': {
                'start': df['timestamp'].min(),
                'end': df['timestamp'].max(),
                'duration_hours': (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
            },
            'price_stats': {
                'min': df['price'].min(),
                'max': df['price'].max(),
                'mean': df['price'].mean(),
                'std': df['price'].std()
            } if 'price' in df.columns else None,
            'missing_values': df.isnull().sum().to_dict()
        }


if __name__ == "__main__":
    # Test the aggregator
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    aggregator = DataAggregator()

    # Test training dataset
    print("\n" + "="*60)
    print("Testing training dataset fetch...")
    print("="*60)

    df_train = aggregator.fetch_training_dataset(hours=24)
    print(f"\nTraining dataset shape: {df_train.shape}")
    print(f"\nColumns: {df_train.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df_train.head())

    # Test latest features
    print("\n" + "="*60)
    print("Testing latest features fetch...")
    print("="*60)

    df_latest = aggregator.fetch_latest_features()
    print(f"\nLatest features:")
    print(df_latest)

    # Get summary
    summary = aggregator.get_data_summary(df_train)
    print(f"\n" + "="*60)
    print("Dataset Summary")
    print("="*60)
    print(f"Rows: {summary['rows']}")
    print(f"Columns: {summary['columns']}")
    print(f"Time range: {summary['time_range']['duration_hours']:.1f} hours")
    if summary['price_stats']:
        print(f"Price range: ${summary['price_stats']['min']:,.2f} - ${summary['price_stats']['max']:,.2f}")
