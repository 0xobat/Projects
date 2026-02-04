"""
Blockchain data fetcher for on-chain metrics.

Fetches Ethereum blockchain data that provides market sentiment signals:
- Block gas usage (network congestion)
- Transaction counts (market activity)
- Block timestamps (for temporal alignment)

Enhanced with error handling, retry logic, and async support.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pandas as pd
from alchemy import Alchemy, Network
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from config.settings import get_settings


class BlockchainFetcher:
    """Fetches on-chain data from Ethereum using Alchemy SDK."""

    def __init__(self):
        """Initialize with Alchemy SDK."""
        settings = get_settings()
        self.alchemy = Alchemy(
            api_key=settings.alchemy.api_key,
            network=Network.ETH_MAINNET
        )
        self.blocks_per_hour = settings.data.blocks_per_hour

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _fetch_block_with_retry(self, block_number: int) -> Dict:
        """
        Fetch a single block with retry logic.

        Args:
            block_number: Block number to fetch

        Returns:
            Dictionary with block data

        Raises:
            Exception if all retries fail
        """
        try:
            block = self.alchemy.core.get_block(block_number)
            return {
                'block_number': block_number,
                'timestamp': block.timestamp,
                'gas_used': block.gas_used,
                'transaction_count': len(block.transactions)
            }
        except Exception as e:
            logger.error(f"Error fetching block {block_number}: {e}")
            raise

    def fetch_historical_data(
        self,
        hours: int = 168,
        sample_rate: int = 1
    ) -> pd.DataFrame:
        """
        Fetch historical blockchain data.

        Args:
            hours: Number of hours of historical data to fetch (default: 168 = 1 week)
            sample_rate: Sample every N hours (default: 1 = every hour)

        Returns:
            DataFrame with columns: block_number, timestamp, gas_used, transaction_count

        Example:
            >>> fetcher = BlockchainFetcher()
            >>> df = fetcher.fetch_historical_data(hours=24)  # Last 24 hours
        """
        logger.info(f"Fetching {hours} hours of blockchain data (sampling every {sample_rate}h)")

        try:
            current_block = self.alchemy.core.get_block_number()
            logger.debug(f"Current block: {current_block}")

            # Calculate blocks to fetch
            blocks_to_fetch = hours * self.blocks_per_hour
            sample_interval = sample_rate * self.blocks_per_hour

            data = []
            failed_blocks = 0

            # Sample blocks at specified interval
            for block_num in range(
                current_block - blocks_to_fetch,
                current_block,
                sample_interval
            ):
                try:
                    block_data = self._fetch_block_with_retry(block_num)
                    data.append(block_data)
                except Exception as e:
                    failed_blocks += 1
                    logger.warning(f"Failed to fetch block {block_num} after retries: {e}")
                    continue

            df = pd.DataFrame(data)

            if failed_blocks > 0:
                logger.warning(f"Failed to fetch {failed_blocks} blocks out of {len(data) + failed_blocks}")

            logger.info(f"Successfully fetched {len(df)} blockchain data points")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch blockchain data: {e}")
            raise

    def fetch_latest_block(self) -> pd.DataFrame:
        """
        Fetch just the latest block data.

        Returns:
            DataFrame with single row of latest block data
        """
        try:
            current_block = self.alchemy.core.get_block_number()
            block_data = self._fetch_block_with_retry(current_block)
            return pd.DataFrame([block_data])
        except Exception as e:
            logger.error(f"Failed to fetch latest block: {e}")
            raise

    def get_current_gas_price(self) -> int:
        """
        Get current gas price in Wei.

        Returns:
            Current gas price

        Example:
            >>> fetcher = BlockchainFetcher()
            >>> gas_price = fetcher.get_current_gas_price()
            >>> gas_price_gwei = gas_price / 1e9  # Convert to Gwei
        """
        try:
            gas_price = self.alchemy.core.get_gas_price()
            logger.debug(f"Current gas price: {gas_price / 1e9:.2f} Gwei")
            return gas_price
        except Exception as e:
            logger.error(f"Failed to fetch gas price: {e}")
            raise

    async def fetch_multiple_blocks(self, block_numbers: List[int]) -> pd.DataFrame:
        """
        Fetch multiple blocks concurrently (async).

        Args:
            block_numbers: List of block numbers to fetch

        Returns:
            DataFrame with all fetched blocks
        """
        # Note: Current Alchemy SDK doesn't support async natively
        # This is a placeholder for future async implementation
        logger.warning("Async fetching not yet implemented, falling back to sequential")
        data = []
        for block_num in block_numbers:
            try:
                block_data = self._fetch_block_with_retry(block_num)
                data.append(block_data)
            except Exception:
                continue
        return pd.DataFrame(data)


if __name__ == "__main__":
    # Test the fetcher
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    fetcher = BlockchainFetcher()

    # Fetch last 24 hours
    df = fetcher.fetch_historical_data(hours=24)
    print(f"\nFetched {len(df)} data points")
    print(df.head())

    # Fetch latest block
    latest = fetcher.fetch_latest_block()
    print(f"\nLatest block:")
    print(latest)

    # Get gas price
    gas_price = fetcher.get_current_gas_price()
    print(f"\nCurrent gas price: {gas_price / 1e9:.2f} Gwei")
