"""
Price data fetcher for cryptocurrency market data.

Fetches historical and real-time price data from Alchemy's Price API.
Supports multiple tokens and OHLCV (Open, High, Low, Close, Volume) data.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from config.settings import get_settings


class PriceFetcher:
    """Fetches cryptocurrency price data from Alchemy Price API."""

    def __init__(self):
        """Initialize with Alchemy API key."""
        settings = get_settings()
        self.api_key = settings.alchemy.api_key
        self.base_url = "https://eth-mainnet.g.alchemy.com/prices/v1"

    def _build_url(self, endpoint: str) -> str:
        """Build complete API URL."""
        return f"{self.base_url}/{self.api_key}/{endpoint}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _make_request(self, url: str, params: dict) -> dict:
        """
        Make HTTP request with retry logic.

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            Exception if request fails after retries
        """
        try:
            response = requests.get(
                url,
                params=params,
                headers={'Accept': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def fetch_historical_prices(
        self,
        symbol: str = "ETH",
        hours: int = 168,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """
        Fetch historical price data for a token.

        Args:
            symbol: Token symbol (e.g., "ETH", "BTC")
            hours: Number of hours of historical data
            interval: Time interval ("1h", "1d", etc.)

        Returns:
            DataFrame with columns: timestamp, price

        Example:
            >>> fetcher = PriceFetcher()
            >>> df = fetcher.fetch_historical_prices("ETH", hours=24)
        """
        logger.info(f"Fetching {hours}h of {symbol} price data (interval: {interval})")

        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)

            url = self._build_url("tokens/by-symbol")
            params = {
                'symbols': symbol,
                'startTime': int(start_time.timestamp()),
                'endTime': int(end_time.timestamp()),
                'interval': interval
            }

            data = self._make_request(url, params)

            # Parse response
            if 'data' not in data or len(data['data']) == 0:
                raise ValueError(f"No price data returned for {symbol}")

            prices = data['data'][0].get('prices', [])

            if not prices:
                raise ValueError(f"No price points returned for {symbol}")

            # Convert to DataFrame
            price_data = []
            for price_point in prices:
                price_data.append({
                    'timestamp': datetime.fromtimestamp(price_point['timestamp']),
                    'price': float(price_point['value'])
                })

            df = pd.DataFrame(price_data)
            logger.info(f"Successfully fetched {len(df)} price points for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch price data for {symbol}: {e}")
            raise

    def fetch_latest_price(self, symbol: str = "ETH") -> float:
        """
        Fetch the latest spot price for a token.

        Args:
            symbol: Token symbol (e.g., "ETH")

        Returns:
            Latest price as float

        Example:
            >>> fetcher = PriceFetcher()
            >>> eth_price = fetcher.fetch_latest_price("ETH")
        """
        try:
            url = self._build_url("tokens/by-symbol")
            params = {'symbols': symbol}

            data = self._make_request(url, params)

            if 'data' not in data or len(data['data']) == 0:
                raise ValueError(f"No price data returned for {symbol}")

            # Get the latest price
            latest_price = float(data['data'][0]['prices'][-1]['value'])
            logger.debug(f"Latest {symbol} price: ${latest_price:,.2f}")
            return latest_price

        except Exception as e:
            logger.error(f"Failed to fetch latest price for {symbol}: {e}")
            raise

    def fetch_multiple_tokens(
        self,
        symbols: List[str],
        hours: int = 24
    ) -> dict:
        """
        Fetch price data for multiple tokens.

        Args:
            symbols: List of token symbols
            hours: Number of hours of historical data

        Returns:
            Dictionary mapping symbol -> DataFrame

        Example:
            >>> fetcher = PriceFetcher()
            >>> prices = fetcher.fetch_multiple_tokens(["ETH", "BTC"], hours=24)
        """
        logger.info(f"Fetching prices for {len(symbols)} tokens: {symbols}")

        prices_dict = {}
        for symbol in symbols:
            try:
                df = self.fetch_historical_prices(symbol, hours=hours)
                prices_dict[symbol] = df
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol}: {e}")
                continue

        logger.info(f"Successfully fetched data for {len(prices_dict)}/{len(symbols)} tokens")
        return prices_dict

    def fetch_ohlcv_data(
        self,
        symbol: str = "ETH",
        hours: int = 168,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data.

        Note: Alchemy's current API may not support full OHLCV.
        This method provides a basic implementation that can be extended.

        Args:
            symbol: Token symbol
            hours: Number of hours of historical data
            interval: Time interval

        Returns:
            DataFrame with OHLCV data
        """
        # For now, we fetch price data and simulate OHLCV structure
        # In production, this should be replaced with actual OHLCV data source
        logger.warning("OHLCV data is simulated from price data. Consider using a dedicated OHLCV source.")

        df = self.fetch_historical_prices(symbol, hours, interval)

        # Simulate OHLCV (in production, get actual OHLCV data)
        df['open'] = df['price']
        df['high'] = df['price'] * 1.001  # Placeholder
        df['low'] = df['price'] * 0.999   # Placeholder
        df['close'] = df['price']
        df['volume'] = 0  # Not available from current API

        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]


if __name__ == "__main__":
    # Test the fetcher
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    fetcher = PriceFetcher()

    # Fetch ETH prices
    df = fetcher.fetch_historical_prices("ETH", hours=24)
    print(f"\nFetched {len(df)} ETH price points")
    print(df.head())
    print(f"Price range: ${df['price'].min():,.2f} - ${df['price'].max():,.2f}")

    # Fetch latest price
    latest_price = fetcher.fetch_latest_price("ETH")
    print(f"\nLatest ETH price: ${latest_price:,.2f}")

    # Fetch multiple tokens
    prices = fetcher.fetch_multiple_tokens(["ETH"], hours=24)
    print(f"\nFetched data for {len(prices)} tokens")
