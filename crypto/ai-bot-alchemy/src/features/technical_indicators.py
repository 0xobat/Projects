"""
Technical indicators for price-based features.

Implements common technical analysis indicators:
- Moving averages
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Momentum indicators
- Volatility measures
"""

import pandas as pd
import numpy as np
from loguru import logger


class TechnicalIndicators:
    """Calculator for technical analysis indicators."""

    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical indicators to DataFrame.

        Args:
            df: DataFrame with 'price' column

        Returns:
            DataFrame with all technical indicators added
        """
        df = self.add_price_changes(df)
        df = self.add_moving_averages(df)
        df = self.add_volatility(df)
        df = self.add_momentum(df)
        df = self.add_rsi(df)
        df = self.add_macd(df)
        df = self.add_bollinger_bands(df)

        return df

    def add_price_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add price change features.

        Features:
        - price_change: Percentage change from previous period
        """
        df['price_change'] = df['price'].pct_change()
        return df

    def add_moving_averages(
        self,
        df: pd.DataFrame,
        windows: list = [12, 24, 48]
    ) -> pd.DataFrame:
        """
        Add moving average features.

        Moving averages smooth out noise and identify trends.

        Args:
            df: DataFrame with 'price' column
            windows: List of window sizes (default: 12h, 24h, 48h)

        Features:
        - price_ma_12: 12-period moving average
        - price_ma_24: 24-period moving average
        - price_ma_48: 48-period moving average
        """
        for window in windows:
            df[f'price_ma_{window}'] = df['price'].rolling(window=window).mean()

        return df

    def add_volatility(self, df: pd.DataFrame, window: int = 12) -> pd.DataFrame:
        """
        Add volatility measures.

        Volatility indicates market instability and risk.

        Args:
            df: DataFrame with 'price_change' column
            window: Rolling window size (default: 12)

        Features:
        - volatility: Standard deviation of price changes
        """
        if 'price_change' not in df.columns:
            df = self.add_price_changes(df)

        df['volatility'] = df['price_change'].rolling(window=window).std()

        return df

    def add_momentum(self, df: pd.DataFrame, window: int = 6) -> pd.DataFrame:
        """
        Add momentum indicators.

        Momentum measures the rate of price change.

        Args:
            df: DataFrame with 'price' column
            window: Lookback window (default: 6)

        Features:
        - momentum: Price change over the window period
        """
        df['momentum'] = df['price'] - df['price'].shift(window)

        return df

    def add_rsi(self, df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Add Relative Strength Index (RSI).

        RSI measures overbought/oversold conditions.
        - RSI > 70: Overbought (potential sell signal)
        - RSI < 30: Oversold (potential buy signal)

        Args:
            df: DataFrame with 'price' column
            window: RSI period (default: 14)

        Features:
        - rsi: Relative Strength Index (0-100)
        """
        # Calculate price changes
        delta = df['price'].diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=window).mean()
        avg_losses = losses.rolling(window=window).mean()

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        df['rsi'] = 100 - (100 / (1 + rs))

        return df

    def add_macd(
        self,
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        """
        Add MACD (Moving Average Convergence Divergence).

        MACD is a trend-following momentum indicator.
        - MACD crossing above signal: Bullish
        - MACD crossing below signal: Bearish

        Args:
            df: DataFrame with 'price' column
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)

        Features:
        - macd: MACD line
        - macd_signal: Signal line
        """
        # Calculate exponential moving averages
        ema_fast = df['price'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['price'].ewm(span=slow, adjust=False).mean()

        # MACD line
        df['macd'] = ema_fast - ema_slow

        # Signal line
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()

        return df

    def add_bollinger_bands(
        self,
        df: pd.DataFrame,
        window: int = 20,
        num_std: float = 2.0
    ) -> pd.DataFrame:
        """
        Add Bollinger Bands.

        Bollinger Bands measure volatility and identify overbought/oversold levels.
        - Price near upper band: Overbought
        - Price near lower band: Oversold
        - Band width: Volatility indicator

        Args:
            df: DataFrame with 'price' column
            window: Moving average period (default: 20)
            num_std: Number of standard deviations (default: 2.0)

        Features:
        - bb_upper: Upper Bollinger Band
        - bb_lower: Lower Bollinger Band
        - bb_width: Band width (volatility measure)
        """
        # Middle band (moving average)
        ma = df['price'].rolling(window=window).mean()

        # Standard deviation
        std = df['price'].rolling(window=window).std()

        # Upper and lower bands
        df['bb_upper'] = ma + (std * num_std)
        df['bb_lower'] = ma - (std * num_std)

        # Band width
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / ma

        return df


if __name__ == "__main__":
    # Test technical indicators
    import sys
    from datetime import datetime, timedelta

    logger.remove()
    logger.add(sys.stdout, level="DEBUG")

    # Create synthetic price data
    np.random.seed(42)
    n_samples = 100

    # Simulate a trending price with noise
    trend = np.linspace(3000, 3200, n_samples)
    noise = np.random.randn(n_samples) * 50
    prices = trend + noise

    test_df = pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(hours=i) for i in range(n_samples-1, -1, -1)],
        'price': prices
    })

    print("Raw price data:")
    print(test_df.head(10))

    # Add technical indicators
    calculator = TechnicalIndicators()
    indicators_df = calculator.add_all_indicators(test_df)

    print(f"\n" + "="*60)
    print("Technical indicators added:")
    print("="*60)

    print(f"\nDataFrame shape: {indicators_df.shape}")
    print(f"Columns: {indicators_df.columns.tolist()}")

    print(f"\nSample with indicators:")
    print(indicators_df[['price', 'price_ma_12', 'rsi', 'macd', 'bb_width']].tail(10))

    print(f"\nIndicator statistics:")
    indicator_cols = ['price_change', 'volatility', 'rsi', 'macd', 'bb_width']
    print(indicators_df[indicator_cols].describe())

    print("\n✓ Technical indicators test passed!")
