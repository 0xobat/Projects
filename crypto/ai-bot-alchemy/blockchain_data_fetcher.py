import os
from dotenv import load_dotenv
from alchemy import Alchemy, Network
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Load environment variables from .env file
load_dotenv()

# Initialize Alchemy SDK
alchemy = Alchemy(
    api_key=os.getenv('ALCHEMY_API_KEY'),
    network=Network.ETH_MAINNET
)

def fetch_historical_data(hours=168):  # Default: last week (168 hours)
    """
    Fetch historical blockchain data that we'll use as features.
    
    We're collecting:
    - Block numbers and timestamps (for temporal ordering)
    - Gas used per block (proxy for network activity)
    - Transaction counts (proxy for market interest)
    
    These on-chain metrics can signal market conditions before they
    appear in price data.
    """
    current_block = alchemy.core.get_block_number()
    
    # Ethereum produces ~1 block every 12 seconds# So roughly 300 blocks per hour
    blocks_per_hour = 300
    blocks_to_fetch = hours * blocks_per_hour
    
    # We'll sample every N blocks to avoid excessive API calls# Sampling hourly (every 300 blocks) gives us manageable data
    data = []
    for i in range(current_block - blocks_to_fetch, current_block, blocks_per_hour):
        try:
            block = alchemy.core.get_block(i)
            data.append({
                'block_number': i,
                'timestamp': block.timestamp,
                'gas_used': block.gas_used,
                'transaction_count': len(block.transactions)
            })
        except Exception as e:
            print(f"Error fetching block {i}: {e}")
            continue
    
    return pd.DataFrame(data)

# Fetch a week of data
print("Fetching historical blockchain data...")
df = fetch_historical_data(hours=168)
print(f"Retrieved {len(df)} data points")
print(df.head())