import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("../../data/processed/traffic_dataset.csv")

print("Dataset loaded:", df.shape)

# Target column
target = "class1"

# Features
X = df.drop(columns=[target])
y = df[target]

# Convert to numeric
X = X.apply(pd.to_numeric, errors="coerce")

# Fill missing values
X = X.fillna(0)

# Train / Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training samples:", X_train.shape)
print("Testing samples:", X_test.shape)

# Train model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    n_jobs=-1,
    random_state=42
)

print("Training model...")

model.fit(X_train, y_train)

print("Model training completed")

# Predictions
pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, pred)

print("\nModel Accuracy:", accuracy)

print("\nClassification Report:\n")
print(classification_report(y_test, pred))

# Save model
joblib.dump(model, "../saved_models/traffic_classifier.pkl")

print("\nModel saved to backend/saved_models/")