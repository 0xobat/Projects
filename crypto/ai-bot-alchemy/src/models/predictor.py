"""
Real-time prediction service.

Loads trained models and makes predictions on new data.
"""

import json
import pickle
from typing import Tuple, Optional
import pandas as pd
import numpy as np
from loguru import logger

from config.settings import get_settings


class Predictor:
    """Real-time prediction service for trained models."""

    def __init__(self, model_version: Optional[str] = "latest"):
        """
        Initialize predictor with a trained model.

        Args:
            model_version: Version to load (default: "latest")
        """
        self.settings = get_settings()
        self.model = None
        self.feature_columns = None
        self.model_version = model_version

        self._load_model(model_version)

    def _load_model(self, version: str):
        """Load model from disk."""
        models_dir = self.settings.data.models_dir

        # Handle "latest" version
        if version == "latest":
            # Find most recent model directory
            model_dirs = [d for d in models_dir.iterdir() if d.is_dir()]
            if not model_dirs:
                raise ValueError("No trained models found")

            latest_dir = max(model_dirs, key=lambda d: d.stat().st_mtime)
            version = latest_dir.name

        load_dir = models_dir / version

        if not load_dir.exists():
            raise ValueError(f"Model version {version} not found")

        # Load model
        model_path = load_dir / "model.pkl"
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        # Load feature columns
        features_path = load_dir / "features.json"
        with open(features_path, 'r') as f:
            self.feature_columns = json.load(f)

        logger.info(f"Loaded model version: {version}")
        self.model_version = version

    def predict(self, features_df: pd.DataFrame) -> Tuple[int, float]:
        """
        Make prediction on new data.

        Args:
            features_df: DataFrame with engineered features

        Returns:
            Tuple of (prediction, confidence)
            - prediction: 0 (down) or 1 (up)
            - confidence: Probability between 0 and 1

        Example:
            >>> predictor = Predictor()
            >>> prediction, confidence = predictor.predict(latest_features)
            >>> print(f"Prediction: {prediction}, Confidence: {confidence:.2%}")
        """
        if self.model is None:
            raise ValueError("No model loaded")

        # Select and order features
        X = features_df[self.feature_columns]

        # Make prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]

        # Confidence is the probability of the predicted class
        confidence = probabilities[prediction]

        logger.debug(f"Prediction: {prediction}, Confidence: {confidence:.2%}")

        return int(prediction), float(confidence)

    def predict_batch(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Make predictions on multiple samples.

        Args:
            features_df: DataFrame with multiple rows of features

        Returns:
            DataFrame with predictions and confidences
        """
        if self.model is None:
            raise ValueError("No model loaded")

        # Select and order features
        X = features_df[self.feature_columns]

        # Make predictions
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)

        # Get confidence (probability of predicted class)
        confidences = probabilities[np.arange(len(predictions)), predictions]

        result_df = pd.DataFrame({
            'prediction': predictions,
            'confidence': confidences,
            'prob_down': probabilities[:, 0],
            'prob_up': probabilities[:, 1]
        })

        return result_df


if __name__ == "__main__":
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    print("Predictor module ready!")
    print("To test, first train a model using trainer.py")
