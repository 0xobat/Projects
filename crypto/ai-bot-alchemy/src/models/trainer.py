"""
Model training pipeline.

Handles:
- Training ML models with cross-validation
- Hyperparameter tuning
- Feature importance analysis
- Model versioning and persistence
"""

import os
import pickle
import json
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from loguru import logger

from config.settings import get_settings


class ModelTrainer:
    """Trains and evaluates ML models for price prediction."""

    def __init__(self):
        """Initialize trainer with settings."""
        self.settings = get_settings()
        self.model = None
        self.feature_columns = None
        self.model_metadata = {}

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        cv_folds: int = 5,
        tune_hyperparameters: bool = False
    ) -> Dict:
        """
        Train a Random Forest classifier.

        Args:
            X: Features DataFrame
            y: Target series
            test_size: Fraction of data for testing (default: 0.2)
            cv_folds: Number of cross-validation folds (default: 5)
            tune_hyperparameters: Whether to tune hyperparameters (default: False)

        Returns:
            Dictionary with training metrics

        Example:
            >>> trainer = ModelTrainer()
            >>> metrics = trainer.train(X_features, y_target)
        """
        logger.info(f"Training model on {len(X)} samples with {len(X.columns)} features")

        # Store feature columns
        self.feature_columns = list(X.columns)

        # Split data (time series: no shuffling!)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            shuffle=False  # CRITICAL: preserve temporal order
        )

        logger.info(f"Train: {len(X_train)} | Test: {len(X_test)}")

        # Initialize model
        if tune_hyperparameters:
            logger.info("Tuning hyperparameters with GridSearch...")
            self.model = self._tune_hyperparameters(X_train, y_train)
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced',
                n_jobs=-1
            )

        # Train model
        logger.info("Training model...")
        self.model.fit(X_train, y_train)
        logger.info("✓ Model trained")

        # Evaluate on test set
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        test_metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0)
        }

        logger.info(f"Test Accuracy: {test_metrics['accuracy']:.2%}")
        logger.info(f"Test Precision: {test_metrics['precision']:.2%}")
        logger.info(f"Test Recall: {test_metrics['recall']:.2%}")
        logger.info(f"Test F1: {test_metrics['f1']:.2%}")

        # Cross-validation on training data
        logger.info(f"Running {cv_folds}-fold cross-validation...")
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=cv_folds)

        cv_metrics = {
            'cv_scores': cv_scores.tolist(),
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }

        logger.info(f"CV Mean: {cv_metrics['cv_mean']:.2%} (+/- {cv_metrics['cv_std']:.2%})")

        # Feature importance
        feature_importance = self._get_feature_importance()

        # Classification report
        report = classification_report(y_test, y_pred, output_dict=True)

        # Store metadata
        self.model_metadata = {
            'training_date': datetime.now().isoformat(),
            'n_samples_train': len(X_train),
            'n_samples_test': len(X_test),
            'n_features': len(self.feature_columns),
            'feature_columns': self.feature_columns,
            'test_metrics': test_metrics,
            'cv_metrics': cv_metrics,
            'feature_importance': feature_importance,
            'classification_report': report,
            'hyperparameters': self.model.get_params()
        }

        logger.info("Training complete!")

        return self.model_metadata

    def _tune_hyperparameters(self, X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
        """
        Tune hyperparameters using GridSearchCV.

        Args:
            X_train: Training features
            y_train: Training target

        Returns:
            Best estimator
        """
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }

        grid_search = GridSearchCV(
            RandomForestClassifier(random_state=42, class_weight='balanced', n_jobs=-1),
            param_grid,
            cv=3,
            scoring='f1',
            n_jobs=-1,
            verbose=1
        )

        grid_search.fit(X_train, y_train)

        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best CV score: {grid_search.best_score_:.2%}")

        return grid_search.best_estimator_

    def _get_feature_importance(self) -> Dict:
        """
        Get feature importance from trained model.

        Returns:
            Dictionary mapping feature -> importance score
        """
        if self.model is None or self.feature_columns is None:
            return {}

        importances = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_columns, importances.tolist()))

        # Sort by importance
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )

        logger.debug("Top 5 features:")
        for i, (feature, importance) in enumerate(list(feature_importance.items())[:5]):
            logger.debug(f"  {i+1}. {feature}: {importance:.4f}")

        return feature_importance

    def save_model(self, version: Optional[str] = None) -> str:
        """
        Save trained model to disk.

        Args:
            version: Optional version string (default: timestamp)

        Returns:
            Path to saved model

        Example:
            >>> trainer.save_model(version="v1.0")
        """
        if self.model is None:
            raise ValueError("No model to save. Train a model first.")

        # Generate version
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create save directory
        save_dir = self.settings.data.models_dir / version
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save model
        model_path = save_dir / "model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)

        logger.info(f"Model saved to: {model_path}")

        # Save metadata
        metadata_path = save_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.model_metadata, f, indent=2)

        logger.info(f"Metadata saved to: {metadata_path}")

        # Save feature columns
        features_path = save_dir / "features.json"
        with open(features_path, 'w') as f:
            json.dump(self.feature_columns, f, indent=2)

        logger.info(f"Features saved to: {features_path}")

        return str(model_path)

    def load_model(self, version: str) -> None:
        """
        Load a saved model.

        Args:
            version: Model version to load

        Example:
            >>> trainer.load_model(version="v1.0")
        """
        load_dir = self.settings.data.models_dir / version

        if not load_dir.exists():
            raise ValueError(f"Model version {version} not found")

        # Load model
        model_path = load_dir / "model.pkl"
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        logger.info(f"Model loaded from: {model_path}")

        # Load metadata
        metadata_path = load_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                self.model_metadata = json.load(f)

        # Load feature columns
        features_path = load_dir / "features.json"
        if features_path.exists():
            with open(features_path, 'r') as f:
                self.feature_columns = json.load(f)

        logger.info(f"Loaded model version: {version}")


if __name__ == "__main__":
    # Test trainer
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    # Create synthetic training data
    np.random.seed(42)
    n_samples = 1000

    X = pd.DataFrame({
        'price_change': np.random.randn(n_samples) * 0.02,
        'volatility': np.abs(np.random.randn(n_samples)) * 0.01,
        'rsi': np.random.rand(n_samples) * 100,
        'momentum': np.random.randn(n_samples) * 50,
        'gas_trend': np.random.randn(n_samples) * 0.05
    })

    # Create somewhat realistic target
    y = ((X['price_change'] > 0) & (X['rsi'] < 60)).astype(int)

    print(f"Training data: {X.shape}")
    print(f"Target distribution: {y.value_counts().to_dict()}")

    # Train model
    trainer = ModelTrainer()
    metrics = trainer.train(X, y)

    print("\n" + "="*60)
    print("Training Metrics")
    print("="*60)
    print(f"Accuracy: {metrics['test_metrics']['accuracy']:.2%}")
    print(f"F1 Score: {metrics['test_metrics']['f1']:.2%}")
    print(f"CV Mean: {metrics['cv_metrics']['cv_mean']:.2%}")

    # Save model
    model_path = trainer.save_model(version="test")
    print(f"\nModel saved to: {model_path}")

    print("\n✓ Model training test passed!")
