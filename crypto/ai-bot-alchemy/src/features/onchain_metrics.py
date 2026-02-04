"""
On-chain metrics for blockchain-based features.

These metrics capture blockchain activity that can signal
market sentiment before it appears in price data.

Metrics:
- Gas pressure (network congestion)
- Transaction velocity (activity trends)
- Network congestion score
"""

import pandas as pd
import numpy as np
from loguru import logger


class OnChainMetrics:
    """Calculator for on-chain blockchain metrics."""

    def add_all_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all on-chain metrics to DataFrame.

        Args:
            df: DataFrame with 'gas_used' and 'transaction_count' columns

        Returns:
            DataFrame with on-chain metrics added
        """
        df = self.add_gas_metrics(df)
        df = self.add_transaction_metrics(df)
        df = self.add_network_congestion(df)

        return df

    def add_gas_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add gas-related metrics.

        Gas usage indicates network demand and user willingness to pay
        for transaction priority. Spikes in gas often precede price movements.

        Features:
        - gas_trend: Percentage change in gas usage
        - gas_pressure: Normalized gas usage relative to recent average
        """
        if 'gas_used' not in df.columns:
            logger.warning("gas_used column not found, skipping gas metrics")
            df['gas_trend'] = 0.0
            df['gas_pressure'] = 0.0
            return df

        # Gas trend (percentage change)
        df['gas_trend'] = df['gas_used'].pct_change()

        # Gas pressure: current vs moving average
        gas_ma = df['gas_used'].rolling(window=24).mean()
        df['gas_pressure'] = (df['gas_used'] - gas_ma) / gas_ma

        # Fill NaN values
        df['gas_trend'] = df['gas_trend'].fillna(0)
        df['gas_pressure'] = df['gas_pressure'].fillna(0)

        return df

    def add_transaction_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add transaction-related metrics.

        Transaction count reflects network activity and market interest.
        Rising transactions often indicate increasing market participation.

        Features:
        - tx_trend: Percentage change in transaction count
        """
        if 'transaction_count' not in df.columns:
            logger.warning("transaction_count column not found, skipping transaction metrics")
            df['tx_trend'] = 0.0
            return df

        # Transaction trend (percentage change)
        df['tx_trend'] = df['transaction_count'].pct_change()

        # Fill NaN values
        df['tx_trend'] = df['tx_trend'].fillna(0)

        return df

    def add_network_congestion(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add network congestion score.

        Combines gas usage and transaction count to create a composite
        congestion indicator. High congestion can signal:
        - High demand (bullish for price)
        - Network stress (bearish for user experience)

        Features:
        - network_congestion: Composite score (0-1)
        """
        if 'gas_used' not in df.columns or 'transaction_count' not in df.columns:
            logger.warning("Required columns not found, skipping congestion score")
            df['network_congestion'] = 0.0
            return df

        # Normalize gas and transactions to 0-1 range
        gas_normalized = self._normalize(df['gas_used'])
        tx_normalized = self._normalize(df['transaction_count'])

        # Combine into congestion score
        # Higher weight on gas (more direct indicator of demand)
        df['network_congestion'] = (gas_normalized * 0.7) + (tx_normalized * 0.3)

        return df

    def _normalize(self, series: pd.Series, window: int = 100) -> pd.Series:
        """
        Normalize a series to 0-1 range using rolling min-max.

        Args:
            series: Series to normalize
            window: Rolling window for min-max calculation

        Returns:
            Normalized series (0-1)
        """
        rolling_min = series.rolling(window=window, min_periods=1).min()
        rolling_max = series.rolling(window=window, min_periods=1).max()

        # Avoid division by zero
        denominator = rolling_max - rolling_min
        denominator = denominator.replace(0, 1)

        normalized = (series - rolling_min) / denominator

        # Clip to 0-1 range
        normalized = normalized.clip(0, 1)

        return normalized.fillna(0.5)  # Fill NaN with neutral value


if __name__ == "__main__":
    # Test on-chain metrics
    import sys
    from datetime import datetime, timedelta

    logger.remove()
    logger.add(sys.stdout, level="DEBUG")

    # Create synthetic blockchain data
    np.random.seed(42)
    n_samples = 150

    # Simulate gas usage with some spikes
    base_gas = 15_000_000
    gas_noise = np.random.randint(-1_000_000, 1_000_000, n_samples)
    gas_spikes = np.zeros(n_samples)
    gas_spikes[[30, 60, 90, 120]] = 5_000_000  # Add some congestion spikes
    gas_used = base_gas + gas_noise + gas_spikes

    # Simulate transaction counts
    base_tx = 150
    tx_noise = np.random.randint(-20, 20, n_samples)
    tx_count = base_tx + tx_noise

    test_df = pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(hours=i) for i in range(n_samples-1, -1, -1)],
        'gas_used': gas_used,
        'transaction_count': tx_count
    })

    print("Raw blockchain data:")
    print(test_df.head(10))

    # Add on-chain metrics
    calculator = OnChainMetrics()
    metrics_df = calculator.add_all_metrics(test_df)

    print(f"\n" + "="*60)
    print("On-chain metrics added:")
    print("="*60)

    print(f"\nDataFrame shape: {metrics_df.shape}")
    print(f"Columns: {metrics_df.columns.tolist()}")

    print(f"\nSample with metrics:")
    print(metrics_df[['gas_used', 'gas_trend', 'gas_pressure', 'network_congestion']].tail(10))

    print(f"\nMetric statistics:")
    metric_cols = ['gas_trend', 'gas_pressure', 'tx_trend', 'network_congestion']
    print(metrics_df[metric_cols].describe())

    # Check for congestion spikes
    high_congestion = metrics_df[metrics_df['network_congestion'] > 0.8]
    print(f"\nHigh congestion periods: {len(high_congestion)}")
    print(high_congestion[['timestamp', 'gas_used', 'network_congestion']].head())

    print("\n✓ On-chain metrics test passed!")
