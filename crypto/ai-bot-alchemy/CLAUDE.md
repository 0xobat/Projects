# ai-bot-alchemy — AI Crypto Trading Bot

AI-powered cryptocurrency trading bot with ML predictions and risk management.

## Tech Stack

- **Language:** Python 3.10+
- **Package Manager:** UV
- **ML:** scikit-learn
- **Blockchain:** web3, alchemy-sdk-py
- **API:** FastAPI (planned)
- **Testing:** pytest

## Running

```bash
uv sync              # Install dependencies
uv run python main.py  # Run the bot
```

## Source Layout

- `src/` — Main source modules
  - `backtesting/` — Backtesting framework
  - `data/` — Data handling
  - `features/` — Feature engineering
  - `models/` — ML models
  - `risk/` — Risk management
  - `trading/` — Trading logic
- `config/` — Configuration files (settings, params)
- `main.py` — Entry point

## Agent Harness

This project uses the harness convention. See `harness/` directory:

- `harness/init.sh` — Install deps with UV
- `harness/verify.sh` — Run pytest and syntax checks
- `harness/features.json` — Feature inventory with pass/fail status
- `harness/progress.txt` — Read this first to see what previous sessions did
