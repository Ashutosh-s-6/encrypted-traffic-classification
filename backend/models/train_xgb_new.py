import pandas as pd
import os
import pickle

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

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
# LABEL ENCODING
# =====================================================

le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Save encoder
encoder_path = os.path.join("..", "saved_models", "label_encoder_new.pkl")

with open(encoder_path, "wb") as f:
    pickle.dump(le, f)

print("✅ Label encoder saved")


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

# 🔥 SAVE FEATURES
import json
with open("../saved_models/features_new.json", "w") as f:
    json.dump(list(X.columns), f)

print("✅ Features saved")

# =====================================================
# SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

print("Training samples:", X_train.shape)
print("Testing samples:", X_test.shape)

# =====================================================
# MODEL
# =====================================================

model = XGBClassifier(
    n_estimators=150,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="mlogloss",
    use_label_encoder=False
)

print("🚀 Training XGBoost...")

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

model_path = os.path.join("..", "saved_models", "xgb1_new.pkl")

with open(model_path, "wb") as f:
    pickle.dump(model, f)

print(f"\n✅ XGB model saved at: {model_path}")