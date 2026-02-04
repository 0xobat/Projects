"""
Signal generator - converts ML predictions to trading signals.

Takes model predictions and applies thresholds and logic to
generate actionable BUY/SELL/HOLD signals.
"""

from enum import Enum
from typing import Tuple, Dict, Optional
from loguru import logger

from config.settings import get_settings


class Signal(Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SignalGenerator:
    """Generates trading signals from ML predictions."""

    def __init__(self):
        """Initialize with configuration."""
        self.settings = get_settings()
        self.confidence_threshold = self.settings.strategy.signal_threshold

    def generate_signal(
        self,
        prediction: int,
        confidence: float,
        additional_context: Optional[Dict] = None
    ) -> Tuple[Signal, Dict]:
        """
        Generate trading signal from ML prediction.

        Args:
            prediction: Model prediction (0 = down, 1 = up)
            confidence: Prediction confidence (0-1)
            additional_context: Optional dict with extra context (e.g., whale_score, rsi)

        Returns:
            Tuple of (Signal, reasoning_dict)

        Example:
            >>> generator = SignalGenerator()
            >>> signal, reasoning = generator.generate_signal(1, 0.75)
            >>> print(f"Signal: {signal.value}, Confidence: {reasoning['confidence']}")
        """
        reasoning = {
            'prediction': prediction,
            'confidence': confidence,
            'threshold': self.confidence_threshold,
            'context': additional_context or {}
        }

        # Check confidence threshold
        if confidence < self.confidence_threshold:
            logger.debug(
                f"Confidence {confidence:.2%} below threshold {self.confidence_threshold:.2%}, "
                "generating HOLD signal"
            )
            reasoning['reason'] = "Confidence below threshold"
            return Signal.HOLD, reasoning

        # Generate signal based on prediction
        if prediction == 1:
            # Prediction: price will go up -> BUY signal
            signal = Signal.BUY
            reasoning['reason'] = f"High confidence ({confidence:.2%}) upward prediction"

            logger.info(f"🟢 BUY signal generated (confidence: {confidence:.2%})")

        elif prediction == 0:
            # Prediction: price will go down -> SELL signal
            signal = Signal.SELL
            reasoning['reason'] = f"High confidence ({confidence:.2%}) downward prediction"

            logger.info(f"🔴 SELL signal generated (confidence: {confidence:.2%})")

        else:
            # Unknown prediction -> HOLD
            signal = Signal.HOLD
            reasoning['reason'] = "Unknown prediction value"

            logger.warning(f"Unknown prediction: {prediction}, generating HOLD signal")

        return signal, reasoning

    def should_close_position(
        self,
        current_pnl_pct: float,
        confidence: float
    ) -> bool:
        """
        Determine if an existing position should be closed.

        Args:
            current_pnl_pct: Current P&L percentage
            confidence: Current prediction confidence

        Returns:
            True if position should be closed
        """
        # Close on stop loss
        stop_loss = self.settings.risk.stop_loss_pct
        if current_pnl_pct <= -stop_loss:
            logger.warning(f"Stop loss triggered: {current_pnl_pct:.2%} <= {-stop_loss:.2%}")
            return True

        # Close if confidence drops significantly
        if confidence < self.confidence_threshold * 0.8:
            logger.info(f"Closing position due to low confidence: {confidence:.2%}")
            return True

        return False


if __name__ == "__main__":
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    generator = SignalGenerator()

    # Test various scenarios
    print("Testing Signal Generator:")
    print("=" * 60)

    # High confidence BUY
    signal, reasoning = generator.generate_signal(1, 0.85)
    print(f"\n1. Prediction=1, Confidence=0.85")
    print(f"   Signal: {signal.value}")
    print(f"   Reason: {reasoning['reason']}")

    # High confidence SELL
    signal, reasoning = generator.generate_signal(0, 0.75)
    print(f"\n2. Prediction=0, Confidence=0.75")
    print(f"   Signal: {signal.value}")
    print(f"   Reason: {reasoning['reason']}")

    # Low confidence -> HOLD
    signal, reasoning = generator.generate_signal(1, 0.55)
    print(f"\n3. Prediction=1, Confidence=0.55")
    print(f"   Signal: {signal.value}")
    print(f"   Reason: {reasoning['reason']}")

    # Test stop loss
    print(f"\n4. Testing stop loss (PnL: -6%)")
    should_close = generator.should_close_position(-0.06, 0.70)
    print(f"   Should close: {should_close}")

    print("\n✓ Signal generator test passed!")
