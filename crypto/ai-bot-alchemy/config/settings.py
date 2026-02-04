"""
Central configuration management using Pydantic.

All settings are loaded from:
1. Environment variables (.env.local)
2. YAML configuration files (trading_params.yaml, risk_params.yaml)
3. Default values

This ensures type safety, validation, and clear configuration management.
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class AlchemySettings(BaseSettings):
    """Alchemy API configuration."""

    api_key: str = Field(..., description="Alchemy API key")
    network: str = Field(default="eth-mainnet", description="Blockchain network")

    model_config = SettingsConfigDict(
        env_prefix="ALCHEMY_",
        env_file=".env.local",
        case_sensitive=False
    )


class StrategyConfig:
    """Trading strategy configuration from YAML."""

    def __init__(self, config_dict: dict):
        self.timeframe: str = config_dict.get("timeframe", "1h")
        self.signal_threshold: float = config_dict.get("signal_threshold", 0.65)
        self.check_interval_seconds: int = config_dict.get("check_interval_seconds", 300)

        # Position management
        pos_mgmt = config_dict.get("position_management", {})
        self.base_position_size_pct: float = pos_mgmt.get("base_position_size_pct", 0.10)
        self.max_concurrent_positions: int = pos_mgmt.get("max_concurrent_positions", 3)


class RiskConfig:
    """Risk management configuration from YAML."""

    def __init__(self, config_dict: dict):
        # Position limits
        pos_limits = config_dict.get("position_limits", {})
        self.max_position_size_pct: float = pos_limits.get("max_position_size_pct", 0.25)

        # Loss limits
        loss_limits = config_dict.get("loss_limits", {})
        self.stop_loss_pct: float = loss_limits.get("stop_loss_pct", 0.05)
        self.max_daily_loss_pct: float = loss_limits.get("max_daily_loss_pct", 0.10)
        self.max_drawdown_pct: float = loss_limits.get("max_drawdown_pct", 0.20)


class DataSettings:
    """Data collection and storage settings."""

    def __init__(self):
        self.default_lookback_hours: int = 168  # 1 week
        self.blocks_per_hour: int = 300  # Ethereum block rate
        self.whale_threshold_usd: float = 1_000_000  # $1M for whale transactions
        self.data_dir: Path = Path("data")
        self.raw_data_dir: Path = self.data_dir / "raw"
        self.processed_data_dir: Path = self.data_dir / "processed"
        self.models_dir: Path = self.data_dir / "models"
        self.backtest_dir: Path = self.data_dir / "backtest_results"


class LoggingSettings:
    """Logging configuration."""

    def __init__(self):
        self.log_dir: Path = Path("logs")
        self.trading_log_dir: Path = self.log_dir / "trading"
        self.error_log_dir: Path = self.log_dir / "errors"
        self.performance_log_dir: Path = self.log_dir / "performance"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")


class Settings:
    """Main application settings aggregator."""

    def __init__(self):
        # Load environment-based settings
        self.alchemy = AlchemySettings()

        # Load YAML configurations
        self.strategy = self._load_strategy_config()
        self.risk = self._load_risk_config()

        # Initialize other settings
        self.data = DataSettings()
        self.logging = LoggingSettings()

        # Ensure directories exist
        self._ensure_directories()

    def _load_strategy_config(self) -> StrategyConfig:
        """Load trading strategy configuration from YAML."""
        config_path = Path("config/trading_params.yaml")
        if config_path.exists():
            with open(config_path, "r") as f:
                config_dict = yaml.safe_load(f) or {}
        else:
            config_dict = {}
        return StrategyConfig(config_dict)

    def _load_risk_config(self) -> RiskConfig:
        """Load risk management configuration from YAML."""
        config_path = Path("config/risk_params.yaml")
        if config_path.exists():
            with open(config_path, "r") as f:
                config_dict = yaml.safe_load(f) or {}
        else:
            config_dict = {}
        return RiskConfig(config_dict)

    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.data.raw_data_dir,
            self.data.processed_data_dir,
            self.data.models_dir,
            self.data.backtest_dir,
            self.logging.trading_log_dir,
            self.logging.error_log_dir,
            self.logging.performance_log_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def validate(self) -> bool:
        """Validate all configuration settings."""
        try:
            # Validate Alchemy API key exists
            if not self.alchemy.api_key:
                raise ValueError("ALCHEMY_API_KEY not set in environment")

            # Validate strategy parameters
            if not (0 < self.strategy.signal_threshold <= 1):
                raise ValueError(f"signal_threshold must be between 0 and 1, got {self.strategy.signal_threshold}")

            if not (0 < self.strategy.base_position_size_pct <= 1):
                raise ValueError(f"base_position_size_pct must be between 0 and 1")

            # Validate risk parameters
            if not (0 < self.risk.stop_loss_pct <= 1):
                raise ValueError(f"stop_loss_pct must be between 0 and 1")

            if not (0 < self.risk.max_daily_loss_pct <= 1):
                raise ValueError(f"max_daily_loss_pct must be between 0 and 1")

            if self.risk.max_position_size_pct < self.strategy.base_position_size_pct:
                raise ValueError("max_position_size_pct must be >= base_position_size_pct")

            return True

        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
        if not _settings.validate():
            raise RuntimeError("Configuration validation failed")
    return _settings


def reload_settings():
    """Reload settings from files (useful for testing or hot-reloading)."""
    global _settings
    _settings = None
    return get_settings()
