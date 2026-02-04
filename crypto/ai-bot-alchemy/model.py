from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report

# Select the features we engineered
feature_columns = [
    'price_change', 'price_ma_12', 'price_ma_24', 'volatility',
    'gas_trend', 'tx_trend', 'momentum'
]

X = df[feature_columns]
y = df['target']

# Split data: 80% for training, 20% for testing# CRITICAL: shuffle=False to avoid look-ahead bias# In time series, future data can't inform past predictions
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

# Initialize Random Forest classifier
model = RandomForestClassifier(
    n_estimators=100,      # 100 decision trees in the forest
    max_depth=10,          # Prevent trees from growing too deep (overfitting)
    random_state=42,       # For reproducibility
    class_weight='balanced' # Handle imbalanced classes (more ups than downs or vice versa)
)

print("\nTraining model...")
model.fit(X_train, y_train)
print("✓ Model trained")

# ============================================# EVALUATE ON TEST SET# ============================================

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"TEST SET PERFORMANCE")
print(f"{'='*50}")
print(f"Accuracy: {accuracy:.2%}")
print(f"\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Down', 'Up']))

# ============================================# CROSS-VALIDATION# ============================================# Cross-validation gives us more robust performance estimates# by training/testing on multiple data splits
cv_scores = cross_val_score(model, X_train, y_train, cv=5)
print(f"\nCross-validation scores: {cv_scores}")
print(f"Average CV score: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

# ============================================# FEATURE IMPORTANCE# ============================================# Random Forests tell us which features mattered most
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n{'='*50}")
print("FEATURE IMPORTANCE")
print(f"{'='*50}")
print(feature_importance)
