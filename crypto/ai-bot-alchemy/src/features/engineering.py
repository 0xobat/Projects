"""
Feature engineering coordinator.

Orchestrates the creation of all features from raw data:
- Technical indicators (price-based)
- On-chain metrics (blockchain-based)
- Whale activity signals

This module extracts and refactors feature engineering logic from the
original model.py file.
"""

import pandas as pd
from loguru import logger

from src.features.technical_indicators import TechnicalIndicators
from src.features.onchain_metrics import OnChainMetrics


class FeatureEngineer:
    """
    Coordinates feature engineering from multiple sources.

    This class brings together technical analysis, on-chain metrics,
    and whale activity to create a comprehensive feature set.
    """

    def __init__(self):
        """Initialize feature calculators."""
        self.technical = TechnicalIndicators()
        self.onchain = OnChainMetrics()

    def engineer_all_features(self, df: pd.DataFrame, include_target: bool = True) -> pd.DataFrame:
        """
        Transform raw data into ML-ready features.

        Args:
            df: DataFrame with raw data (price, gas_used, transaction_count, whale_score)
            include_target: Whether to create target variable (for training)

        Returns:
            DataFrame with engineered features

        Example:
            >>> engineer = FeatureEngineer()
            >>> features_df = engineer.engineer_all_features(raw_df)
        """
        logger.info("Engineering features from raw data")

        try:
            # Make a copy to avoid modifying original
            df = df.copy()

            # 1. Technical indicators (price-based features)
            logger.debug("Computing technical indicators...")
            df = self.technical.add_all_indicators(df)

            # 2. On-chain metrics
            logger.debug("Computing on-chain metrics...")
            df = self.onchain.add_all_metrics(df)

            # 3. Whale activity features (already in df if from aggregator)
            if 'whale_score' not in df.columns:
                df['whale_score'] = 0.0

            # 4. Create target variable (for training only)
            if include_target:
                logger.debug("Creating target variable...")
                df = self._create_target(df)

            # 5. Clean data
            df = self._clean_features(df)

            logger.info(f"Feature engineering complete: {len(df)} samples, {len(df.columns)} features")

            return df

        except Exception as e:
            logger.error(f"Feature engineering failed: {e}")
            raise

    def _create_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create target variable for supervised learning.

        Target: Will price go up in the next period?
        1 = yes (BUY signal)
        0 = no (SELL/HOLD signal)

        Args:
            df: DataFrame with price column

        Returns:
            DataFrame with 'target' column added
        """
        # Shift price backwards to look into the future
        df['target'] = (df['price'].shift(-1) > df['price']).astype(int)
        return df

    def _clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean engineered features.

        - Drop rows with NaN values (from rolling windows)
        - Remove infinite values
        - Reset index

        Args:
            df: DataFrame with features

        Returns:
            Cleaned DataFrame
        """
        initial_len = len(df)

        # Replace infinite values with NaN
        df = df.replace([float('inf'), float('-inf')], float('nan'))

        # Drop rows with NaN
        df = df.dropna()

        # Reset index
        df = df.reset_index(drop=True)

        dropped = initial_len - len(df)
        if dropped > 0:
            logger.warning(f"Dropped {dropped} rows during feature cleaning")

        return df

    def get_feature_columns(self, include_whale: bool = True) -> list:
        """
        Get list of feature column names (excluding target and metadata).

        Args:
            include_whale: Whether to include whale_score

        Returns:
            List of feature column names
        """
        features = [
            # Technical indicators
            'price_change',
            'price_ma_12',
            'price_ma_24',
            'price_ma_48',
            'volatility',
            'momentum',
            'rsi',
            'macd',
            'macd_signal',
            'bb_upper',
            'bb_lower',
            'bb_width',

            # On-chain metrics
            'gas_trend',
            'tx_trend',
            'gas_pressure',
            'network_congestion',
        ]

        if include_whale:
            features.append('whale_score')

        return features

    def validate_features(self, df: pd.DataFrame) -> bool:
        """
        Validate that all required features are present.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, raises exception otherwise
        """
        required_features = self.get_feature_columns()
        missing = [f for f in required_features if f not in df.columns]

        if missing:
            raise ValueError(f"Missing required features: {missing}")

        logger.debug("Feature validation passed")
        return True


if __name__ == "__main__":
    # Test feature engineering
    from loguru import logger
    import sys
    import numpy as np
    from datetime import datetime, timedelta

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    # Create synthetic test data
    np.random.seed(42)
    n_samples = 200

    test_df = pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(hours=i) for i in range(n_samples-1, -1, -1)],
        'price': 3000 + np.cumsum(np.random.randn(n_samples) * 50),
        'gas_used': 15000000 + np.random.randint(-1000000, 1000000, n_samples),
        'transaction_count': 150 + np.random.randint(-20, 20, n_samples),
        'whale_score': np.random.rand(n_samples) * 0.3
    })

    print(f"Raw data shape: {test_df.shape}")
    print(f"\nRaw data sample:")
    print(test_df.head())

    # Engineer features
    engineer = FeatureEngineer()
    features_df = engineer.engineer_all_features(test_df)

    print(f"\n" + "="*60)
    print(f"Engineered features shape: {features_df.shape}")
    print(f"\nFeature columns:")
    print(engineer.get_feature_columns())

    print(f"\nFeatures sample:")
    print(features_df[['price', 'price_change', 'rsi', 'momentum', 'target']].head(10))

    print(f"\nFeature statistics:")
    print(features_df[engineer.get_feature_columns()].describe())

    # Validate
    engineer.validate_features(features_df)
    print("\n✓ Feature validation passed!")
