# AI Trading Bot - Alchemy Edition

An AI-powered cryptocurrency trading bot that uses machine learning to predict price movements and execute trades with comprehensive risk management.

## 🚀 Features

- **ML-Powered Predictions**: Random Forest classifier trained on technical and on-chain features
- **Multi-Source Data Pipeline**: Combines price data, blockchain metrics, and whale activity
- **Comprehensive Risk Management**: Position limits, stop losses, daily loss limits, and circuit breakers
- **Paper Trading**: Test strategies without risking real money
- **Real-time Monitoring**: Track performance, P&L, and trading metrics
- **Modular Architecture**: Clean separation of concerns for easy extension
- **Fast Setup with uv**: Lightning-fast dependency installation and management

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Main Application (main.py)                  │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
┌──────────▼──────┐ ┌─────▼──────┐ ┌─────▼──────────┐
│   Data Layer    │ │  ML Layer   │ │ Trading Layer  │
│  - Fetchers     │ │  - Features │ │  - Strategy    │
│  - WebSocket    │ │  - Training │ │  - Risk Mgmt   │
│  - Storage      │ │  - Registry │ │  - Execution   │
└─────────────────┘ └─────────────┘ └────────────────┘
```

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Alchemy API key ([Get one here](https://dashboard.alchemy.com/))

### Setup

1. **Install uv (if not already installed)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone and navigate to the repository**
   ```bash
   cd ai-bot-alchemy
   ```

3. **Sync dependencies with uv**
   ```bash
   uv sync
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` and add your Alchemy API key:
   ```
   ALCHEMY_API_KEY=your_api_key_here
   ```

5. **Verify configuration**
   ```bash
   uv run python main.py status
   ```

### Quick Setup Script

For a guided setup experience, use the provided script:

```bash
./quickstart.sh
```

This script will:
- Check if uv is installed
- Create `.env.local` from template
- Install all dependencies
- Display next steps

## 🎯 Quick Start

### 1. Train a Model

Train an ML model on historical data:

```bash
uv run python main.py train --hours 168
```

Options:
- `--hours`: Hours of historical data (default: 168 = 1 week)
- `--version`: Model version name (default: timestamp)
- `--tune`: Enable hyperparameter tuning (slower but better results)

Example:
```bash
uv run python main.py train --hours 336 --version v1.0 --tune
```

### 2. Run Paper Trading

Test your strategy with simulated trading:

```bash
uv run python main.py paper-trade --duration 3600
```

Options:
- `--duration`: Duration in seconds (default: 3600 = 1 hour)
- `--model-version`: Model to use (default: latest)
- `--initial-balance`: Starting capital (default: $10,000)
- `--check-interval`: Check interval in seconds (default: 300 = 5 min)

Example:
```bash
uv run python main.py paper-trade --duration 7200 --initial-balance 50000 --check-interval 180
```

### 3. Check Status

View bot status and trading history:

```bash
uv run python main.py status
```

## 📊 Features Explained

### Data Sources

1. **Price Data** (`src/data/price_fetcher.py`)
   - Hourly ETH prices from Alchemy
   - Supports multiple tokens
   - Automatic retry logic

2. **Blockchain Data** (`src/data/blockchain_fetcher.py`)
   - Gas usage (network congestion)
   - Transaction counts (market activity)
   - Block-level metrics

3. **Whale Monitoring** (`src/data/whale_monitor.py`)
   - WebSocket tracking of large transactions (>$1M)
   - Whale activity scoring
   - Accumulation/distribution signals

### Feature Engineering

**Technical Indicators** (`src/features/technical_indicators.py`):
- Moving averages (12h, 24h, 48h)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volatility measures
- Momentum indicators

**On-Chain Metrics** (`src/features/onchain_metrics.py`):
- Gas pressure index
- Transaction velocity
- Network congestion score

### Machine Learning

**Model** (`src/models/trainer.py`):
- Random Forest classifier
- Cross-validation
- Feature importance analysis
- Hyperparameter tuning (optional)

**Prediction** (`src/models/predictor.py`):
- Real-time predictions
- Confidence scores
- Model versioning

### Risk Management

**Risk Manager** (`src/risk/manager.py`):
- ✅ Position size limits (max 25% of capital)
- ✅ Daily loss limits (max 10% daily loss)
- ✅ Maximum drawdown protection (20% circuit breaker)
- ✅ Concurrent position limits (max 3 positions)
- ✅ Stop loss (5% per position)

### Trading Strategy

**Signal Generation** (`src/trading/signal_generator.py`):
- Converts ML predictions to BUY/SELL/HOLD signals
- Confidence threshold filtering (default: 65%)
- Context-aware decision making

**Portfolio Management** (`src/trading/portfolio.py`):
- Position tracking
- P&L calculation
- Performance metrics
- Trade history

## ⚙️ Configuration

### Trading Parameters

Edit `config/trading_params.yaml`:

```yaml
strategy:
  timeframe: "1h"
  signal_threshold: 0.65  # Min confidence for signals
  check_interval_seconds: 300

position_management:
  base_position_size_pct: 0.10  # 10% of capital per trade
  max_concurrent_positions: 3
```

### Risk Parameters

Edit `config/risk_params.yaml`:

```yaml
position_limits:
  max_position_size_pct: 0.25  # Max 25% per position

loss_limits:
  stop_loss_pct: 0.05  # Exit if position loses 5%
  max_daily_loss_pct: 0.10  # Stop trading if daily loss > 10%
  max_drawdown_pct: 0.20  # Circuit breaker at 20% drawdown
```

## 📁 Project Structure

```
ai-bot-alchemy/
├── config/                     # Configuration files
│   ├── settings.py            # Central configuration
│   ├── trading_params.yaml    # Trading parameters
│   └── risk_params.yaml       # Risk limits
│
├── src/
│   ├── data/                  # Data fetching & aggregation
│   │   ├── blockchain_fetcher.py
│   │   ├── price_fetcher.py
│   │   ├── whale_monitor.py
│   │   ├── data_aggregator.py
│   │   └── storage.py
│   │
│   ├── features/              # Feature engineering
│   │   ├── engineering.py
│   │   ├── technical_indicators.py
│   │   └── onchain_metrics.py
│   │
│   ├── models/                # Machine learning
│   │   ├── trainer.py
│   │   └── predictor.py
│   │
│   ├── trading/               # Trading logic
│   │   ├── signal_generator.py
│   │   └── portfolio.py
│   │
│   └── risk/                  # Risk management
│       └── manager.py
│
├── data/                      # Data storage (gitignored)
│   ├── raw/
│   ├── processed/
│   ├── models/
│   └── backtest_results/
│
├── logs/                      # Application logs (gitignored)
│   ├── trading/
│   ├── errors/
│   └── performance/
│
├── main.py                    # Entry point
├── pyproject.toml            # Dependencies
└── README.md                 # This file
```

## 🔒 Safety Features

1. **Paper Trading First**: Always test strategies before live trading
2. **Multiple Risk Layers**: Position limits, stop losses, circuit breakers
3. **Comprehensive Logging**: Full audit trail of all decisions
4. **Configuration Validation**: Settings validated at startup
5. **Error Recovery**: Automatic retry logic and graceful degradation

## 📈 Performance Metrics

The bot tracks:
- Total return ($ and %)
- Win rate
- Total trades
- Average trade size
- Maximum drawdown
- Sharpe ratio (TODO)

## 🚧 Roadmap

### Completed ✅
- [x] Data pipeline (blockchain + price + whale)
- [x] Feature engineering (technical + on-chain)
- [x] ML model training
- [x] Risk management system
- [x] Paper trading
- [x] Performance tracking

### Planned 📋
- [ ] Backtesting framework
- [ ] Advanced position sizing (Kelly criterion)
- [ ] Multi-token support
- [ ] Live trading execution
- [ ] Web dashboard
- [ ] Telegram notifications
- [ ] More ML models (LSTM, XGBoost)
- [ ] Sentiment analysis integration

## ⚠️ Disclaimer

**This bot is for educational purposes only.**

- Cryptocurrency trading involves significant risk
- Past performance does not guarantee future results
- Always start with paper trading
- Never invest more than you can afford to lose
- The authors are not responsible for any financial losses

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Alchemy](https://www.alchemy.com/) for blockchain data APIs
- scikit-learn for ML framework
- The crypto trading community for inspiration

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues first
- Provide detailed reproduction steps

---

**Happy Trading! 🚀📈**

*Remember: Start with paper trading and always manage your risk!*
