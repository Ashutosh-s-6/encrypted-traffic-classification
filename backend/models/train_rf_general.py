# new random forest training script

import pandas as pd
import joblib
import json
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# Load data
df = pd.read_csv("../../data/processed/traffic_dataset.csv")

print("Dataset loaded:", df.shape)

# Label
df.rename(columns={"class1": "label"}, inplace=True)

labels = df["label"]

# Features
X = df.drop("label", axis=1)

# Clean
X.replace(-1, 0, inplace=True)
X = X.apply(pd.to_numeric, errors="coerce")
X.fillna(0, inplace=True)

# Save feature names
feature_names = X.columns.tolist()

with open("../saved_models/general_features.json", "w") as f:
    json.dump(feature_names, f)

print("Saved feature structure")

# Encode labels
le = LabelEncoder()
y = le.fit_transform(labels)

joblib.dump(le, "../saved_models/general_label_encoder.pkl")

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Model
model = RandomForestClassifier(n_estimators=200, n_jobs=-1)

print("Training RF General model...")
model.fit(X_train, y_train)

# Accuracy
pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, pred))

# Save
joblib.dump(model, "../saved_models/rf_general.pkl")

print("✅ RF General model saved")
