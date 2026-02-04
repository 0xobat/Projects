"""
Whale transaction monitor using WebSocket.

Monitors large Ethereum transactions in real-time to detect whale activity.
Whale movements often precede significant price movements and can be used
as a sentiment indicator.
"""

import asyncio
import json
from datetime import datetime
from typing import Callable, Optional, Dict, List
from collections import deque
import websockets
from web3 import Web3
from loguru import logger

from config.settings import get_settings


class WhaleMonitor:
    """
    Monitor large ETH transactions via WebSocket.

    Tracks transactions above a threshold (default: $1M USD) and
    classifies them as accumulation (bullish) or distribution (bearish).
    """

    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize whale monitor.

        Args:
            callback: Optional function to call when whale transaction detected
                     Signature: callback(transaction_data: dict) -> None
        """
        settings = get_settings()
        self.api_key = settings.alchemy.api_key
        self.threshold_usd = settings.data.whale_threshold_usd
        self.callback = callback

        # WebSocket endpoint
        self.ws_url = f"wss://eth-mainnet.g.alchemy.com/v2/{self.api_key}"

        # Recent whale transactions (for calculating activity score)
        self.recent_whales: deque = deque(maxlen=100)  # Keep last 100

        # Whale activity score (rolling calculation)
        self.whale_score: float = 0.0

        # Connection state
        self.is_running: bool = False
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None

    async def connect(self):
        """Establish WebSocket connection to Alchemy."""
        try:
            logger.info(f"Connecting to Alchemy WebSocket...")
            self.websocket = await websockets.connect(
                self.ws_url,
                ping_interval=20,
                ping_timeout=10
            )
            logger.info("WebSocket connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            raise

    async def subscribe_to_pending_transactions(self):
        """Subscribe to pending transactions feed."""
        try:
            # Subscribe to new pending transactions
            subscription_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_subscribe",
                "params": ["alchemy_pendingTransactions"]
            }

            await self.websocket.send(json.dumps(subscription_request))
            response = await self.websocket.recv()
            response_data = json.loads(response)

            if 'result' in response_data:
                logger.info(f"Subscribed to pending transactions: {response_data['result']}")
            else:
                logger.error(f"Subscription failed: {response_data}")

        except Exception as e:
            logger.error(f"Failed to subscribe: {e}")
            raise

    def _classify_transaction(self, tx_data: dict, eth_price: float) -> Optional[Dict]:
        """
        Classify a transaction as whale activity if above threshold.

        Args:
            tx_data: Transaction data from WebSocket
            eth_price: Current ETH price in USD

        Returns:
            Classification dict if whale transaction, None otherwise
        """
        try:
            # Extract transaction details
            tx_hash = tx_data.get('hash')
            from_addr = tx_data.get('from')
            to_addr = tx_data.get('to')
            value_wei = tx_data.get('value', '0x0')

            # Convert value to ETH
            if isinstance(value_wei, str):
                value_wei = int(value_wei, 16)
            value_eth = Web3.from_wei(value_wei, 'ether')

            # Convert to USD
            value_usd = float(value_eth) * eth_price

            # Check if whale transaction
            if value_usd >= self.threshold_usd:
                # Classify as accumulation or distribution
                # Simple heuristic: transactions to exchanges = bearish (distribution)
                # transactions from exchanges = bullish (accumulation)
                # For MVP, we'll use a simple classification

                classification = {
                    'timestamp': datetime.now(),
                    'tx_hash': tx_hash,
                    'from': from_addr,
                    'to': to_addr,
                    'value_eth': float(value_eth),
                    'value_usd': value_usd,
                    'type': 'transfer',  # Simplified for MVP
                    'signal': 'neutral'  # Simplified for MVP
                }

                logger.info(
                    f"🐋 Whale detected: {value_eth:.2f} ETH (${value_usd:,.0f}) "
                    f"| TX: {tx_hash[:10]}..."
                )

                return classification

            return None

        except Exception as e:
            logger.debug(f"Error classifying transaction: {e}")
            return None

    def _update_whale_score(self, whale_tx: dict):
        """
        Update whale activity score based on recent transactions.

        Score calculation:
        - Each whale transaction adds to the score
        - Score decays over time
        - Positive = accumulation (bullish)
        - Negative = distribution (bearish)
        """
        self.recent_whales.append(whale_tx)

        # Calculate score from recent transactions
        # For MVP: simple count-based score
        # In production: weight by size, direction, time decay
        self.whale_score = len(self.recent_whales) / 100.0  # Normalize to 0-1

        logger.debug(f"Whale activity score updated: {self.whale_score:.3f}")

    async def monitor(self, eth_price: float, duration_seconds: Optional[int] = None):
        """
        Monitor whale transactions.

        Args:
            eth_price: Current ETH price in USD (for threshold calculation)
            duration_seconds: Optional duration to monitor (None = indefinite)
        """
        try:
            await self.connect()
            await self.subscribe_to_pending_transactions()

            self.is_running = True
            start_time = datetime.now()

            logger.info(f"Monitoring whale transactions (threshold: ${self.threshold_usd:,.0f})")

            while self.is_running:
                # Check duration limit
                if duration_seconds:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration_seconds:
                        logger.info(f"Duration limit reached ({duration_seconds}s)")
                        break

                # Receive message
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=60.0
                    )
                    data = json.loads(message)

                    # Check if it's a transaction notification
                    if 'params' in data and 'result' in data['params']:
                        tx_data = data['params']['result']

                        # Classify transaction
                        whale_tx = self._classify_transaction(tx_data, eth_price)

                        if whale_tx:
                            # Update score
                            self._update_whale_score(whale_tx)

                            # Call callback if provided
                            if self.callback:
                                self.callback(whale_tx)

                except asyncio.TimeoutError:
                    logger.debug("WebSocket timeout, continuing...")
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed, reconnecting...")
                    await self.connect()
                    await self.subscribe_to_pending_transactions()
                    continue

        except Exception as e:
            logger.error(f"Error in whale monitoring: {e}")
            raise
        finally:
            await self.stop()

    async def stop(self):
        """Stop monitoring and close WebSocket connection."""
        self.is_running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Whale monitor stopped")

    def get_whale_score(self) -> float:
        """
        Get current whale activity score.

        Returns:
            Score between 0 and 1 (higher = more whale activity)
        """
        return self.whale_score

    def get_recent_whales(self, limit: int = 10) -> List[Dict]:
        """
        Get recent whale transactions.

        Args:
            limit: Maximum number of transactions to return

        Returns:
            List of recent whale transaction dictionaries
        """
        return list(self.recent_whales)[-limit:]


def example_callback(whale_tx: dict):
    """Example callback function for whale transactions."""
    print(f"\n🚨 WHALE ALERT 🚨")
    print(f"Value: {whale_tx['value_eth']:.2f} ETH (${whale_tx['value_usd']:,.0f})")
    print(f"Hash: {whale_tx['tx_hash']}")


async def main():
    """Test the whale monitor."""
    # Example: Monitor for 60 seconds
    monitor = WhaleMonitor(callback=example_callback)

    # Use a sample ETH price for testing
    eth_price = 3000.0

    try:
        await monitor.monitor(eth_price, duration_seconds=60)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        await monitor.stop()


if __name__ == "__main__":
    # Test the monitor
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    asyncio.run(main())
