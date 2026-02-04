import requests
from datetime import datetime, timedelta
import pandas as pd

def fetch_eth_prices_alchemy(hours=168):
    """
    Fetch historical ETH prices using Alchemy's Token Prices API.
    
    This gives us reliable, exchange-aggregated pricing that reflects
    actual market conditions across major venues.
    """
    # Alchemy's prices endpoint
    url = f"https://eth-mainnet.g.alchemy.com/prices/v1/{os.getenv('ALCHEMY_API_KEY')}/tokens/by-symbol"
    
    # Calculate our time window
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    params = {
        'symbols': 'ETH',
        'startTime': int(start_time.timestamp()),
        'endTime': int(end_time.timestamp()),
        'interval': '1h'  # Hourly price points
    }
    
    headers = {
        'Accept': 'application/json'
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        prices = data['data'][0]['prices']
        
        # Convert to DataFrame format
        price_data = []
        for price_point in prices:
            price_data.append({
                'timestamp': datetime.fromtimestamp(price_point['timestamp']),
                'price': price_point['value']
            })
        
        return pd.DataFrame(price_data)
    else:
        raise Exception(f"Failed to fetch prices: {response.status_code} - {response.text}")

# Fetch prices
print("Fetching ETH price data from Alchemy...")
price_df = fetch_eth_prices_alchemy(hours=168)

# Ensure timestamps are datetime objects for merging
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Merge blockchain data with price data# merge_asof handles slight timestamp mismatches by finding nearest match
df = pd.merge_asof(
    df.sort_values('timestamp'),
    price_df.sort_values('timestamp'),
    on='timestamp',
    direction='nearest'
)

print(f"Merged data shape: {df.shape}")
print(df.head())


def engineer_features(df):
    """
    Transform raw data into predictive features.
    
    We're creating two types of features:
    1. Price-based technical indicators (moving averages, volatility)
    2. On-chain sentiment proxies (gas and transaction trends)
    
    The goal is to give the model multiple perspectives on market conditions.
    """
    
    # ============================================# PRICE-BASED FEATURES# ============================================
    
    # Percentage change from previous hour# Captures momentum - is price accelerating up or down?
    df['price_change'] = df['price'].pct_change()
    
    # Moving averages - smooth out noise, identify trends
    df['price_ma_12'] = df['price'].rolling(window=12).mean()  # 12-hour
    df['price_ma_24'] = df['price'].rolling(window=24).mean()  # 24-hour
    
    # When short-term MA crosses above long-term MA = bullish signal# When it crosses below = bearish signal
    
    # Volatility - standard deviation of recent price changes# High volatility = risky/unstable market
    df['volatility'] = df['price_change'].rolling(window=12).std()
    
    # ============================================# ON-CHAIN SENTIMENT FEATURES# ============================================
    
    # Gas usage trend - are people paying more to transact?# Spikes often precede price movements
    df['gas_trend'] = df['gas_used'].pct_change()
    
    # Transaction count trend - is activity increasing?# More transactions = more interest = potential price catalyst
    df['tx_trend'] = df['transaction_count'].pct_change()
    
    # ============================================# MOMENTUM INDICATORS# ============================================
    
    # Price change over last 6 hours# Positive momentum = upward trajectory
    df['momentum'] = df['price'] - df['price'].shift(6)
    
    # ============================================# TARGET VARIABLE# ============================================
    
    # What we're trying to predict: will price go up in the next hour?# 1 = yes (buy signal), 0 = no (sell/hold signal)
    df['target'] = (df['price'].shift(-1) > df['price']).astype(int)
    
    # Drop rows with NaN values (from rolling windows and shifts)
    df = df.dropna()
    
    return df

df = engineer_features(df)
print(f"\nEngineered features: {df.columns.tolist()}")
print(f"Data shape: {df.shape}")
print(f"\nSample of engineered data:")
print(df[['price', 'price_change', 'volatility', 'momentum', 'target']].head())