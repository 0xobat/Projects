# Setup Guide

## Installation Steps

### 1. Install uv

If you don't have `uv` installed:

```bash
# On Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:
```bash
uv --version
```

### 2. Sync Dependencies

Navigate to the project directory and sync all dependencies:

```bash
cd ai-bot-alchemy
uv sync
```

This will:
- Create a virtual environment automatically (`.venv/`)
- Install all required packages listed in `pyproject.toml`
- Lock dependencies for reproducible builds
- alchemy-sdk-py (blockchain data)
- web3, websockets (Web3 and WebSocket support)
- pandas, numpy (data processing)
- scikit-learn (machine learning)
- pydantic, python-dotenv, pyyaml (configuration)
- requests, aiohttp (HTTP requests)
- sqlalchemy (database)
- matplotlib, plotly (visualization)
- click (CLI)
- loguru (logging)
- tenacity (retry logic)
- pytest (testing)

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env.local
```

Edit `.env.local` and add your Alchemy API key:
```
ALCHEMY_API_KEY=your_actual_api_key_here
ALCHEMY_NETWORK=eth-mainnet
LOG_LEVEL=INFO
```

### 4. Verify Installation

```bash
uv run python main.py status
```

You should see:
```
============================================================
AI TRADING BOT STATUS
============================================================

Available Models: 0

No trading history yet

✓ Status check complete
```

## First Run

### Train Your First Model

Train on 24 hours of data (faster for testing):
```bash
uv run python main.py train --hours 24
```

Or train on a full week (better accuracy):
```bash
uv run python main.py train --hours 168
```

Expected output:
- Data fetching progress
- Feature engineering stats
- Model training progress
- Cross-validation scores
- Test set performance
- Feature importance ranking

### Run Paper Trading

Start a 30-minute paper trading session:
```bash
uv run python main.py paper-trade --duration 1800
```

Watch the bot:
1. Fetch market data
2. Generate predictions
3. Create trading signals
4. Execute simulated trades
5. Track portfolio performance

## Troubleshooting

### Issue: "ALCHEMY_API_KEY not set"
**Solution**: Make sure `.env.local` exists and contains your API key.

### Issue: "No trained models found"
**Solution**: Run `uv run python main.py train` first to train a model.

### Issue: "Module not found"
**Solution**:
1. Run `uv sync` again to ensure all dependencies are installed
2. Check you're in the correct directory
3. Verify `uv` is properly installed: `uv --version`

### Issue: API rate limits
**Solution**:
1. Reduce check interval: `--check-interval 600` (10 minutes)
2. Use shorter training periods: `--hours 48`
3. Upgrade your Alchemy plan

## Configuration Tuning

### Adjust Risk Parameters

Edit `config/risk_params.yaml`:
```yaml
position_limits:
  max_position_size_pct: 0.15  # Reduce from 0.25 to 0.15 (15%)

loss_limits:
  stop_loss_pct: 0.03  # Tighter stop loss (3% instead of 5%)
  max_daily_loss_pct: 0.05  # More conservative (5% instead of 10%)
```

### Adjust Trading Strategy

Edit `config/trading_params.yaml`:
```yaml
strategy:
  signal_threshold: 0.75  # Higher threshold = fewer trades but higher confidence
  check_interval_seconds: 600  # Less frequent checks

position_management:
  base_position_size_pct: 0.05  # Smaller position sizes
  max_concurrent_positions: 1  # Only one position at a time
```

## Next Steps

1. ✅ Train a model with 1 week of data
2. ✅ Run paper trading for a few hours
3. ✅ Review logs in `logs/trading/`
4. ✅ Adjust configuration based on results
5. ✅ Repeat until satisfied with performance

## Production Checklist

Before considering live trading (NOT IMPLEMENTED YET):

- [ ] Extensive paper trading (at least 2 weeks)
- [ ] Win rate > 55%
- [ ] Positive total return over multiple sessions
- [ ] Risk limits properly configured and tested
- [ ] Circuit breaker tested
- [ ] Comprehensive logging enabled
- [ ] Monitoring and alerting set up
- [ ] Start with minimal capital
- [ ] Have a manual stop-loss plan

## Support

If you encounter issues:
1. Check logs in `logs/errors/`
2. Review configuration in `config/`
3. Test individual components (see test code at bottom of each module)
4. Open an issue with detailed error messages

---

**Good luck with your trading bot! Remember: Paper trade first!**
