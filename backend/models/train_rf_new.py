import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# =====================================================
# LOAD DATA
# =====================================================

DATA_PATH = os.path.join("..", "..", "data", "processed", "final_dataset.csv")

df = pd.read_csv(DATA_PATH)

print("✅ Dataset loaded:", df.shape)

# =====================================================
# CLEAN DATA
# =====================================================

# Separate label
y = df["class1"]
X = df.drop(columns=["class1"])

# Convert to numeric
X = X.apply(pd.to_numeric, errors="coerce")

# Replace -1
X = X.replace(-1, 0)

# Fill NaN
X = X.fillna(0)


# =====================================================
# FEATURES & TARGET
# =====================================================

if "label" in df.columns:
    target_col = "label"
elif "class1" in df.columns:
    target_col = "class1"
else:
    raise ValueError("❌ No target column found (label/class1)")

X = df.drop(target_col, axis=1)
y = df[target_col]

# 🔥 SAVE FEATURE STRUCTURE (IMPORTANT)
import json
with open("../saved_models/features_new.json", "w") as f:
    json.dump(list(X.columns), f)

print("✅ Features saved")

# =====================================================
# SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training samples:", X_train.shape)
print("Testing samples:", X_test.shape)

# =====================================================
# MODEL
# =====================================================

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    n_jobs=-1,
    random_state=42
)

print("🚀 Training Random Forest...")

model.fit(X_train, y_train)

print("✅ Training completed")

# =====================================================
# EVALUATION
# =====================================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n🎯 Accuracy:", accuracy)

print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# =====================================================
# SAVE MODEL
# =====================================================

SAVE_PATH = os.path.join("..", "saved_models", "rf1_new.pkl")

joblib.dump(model, SAVE_PATH)

print(f"\n✅ RF model saved at: {SAVE_PATH}")