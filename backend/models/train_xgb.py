import pandas as pd
import pickle
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv("../../data/processed/traffic_dataset.csv")

print("✅ Dataset loaded:", df.shape)

# =====================================================
# HANDLE LABEL FIRST (IMPORTANT FIX)
# =====================================================

df.rename(columns={"class1": "label"}, inplace=True)

# Save original labels BEFORE numeric conversion
labels = df["label"]

# =====================================================
# CLEAN FEATURES ONLY
# =====================================================

X = df.drop("label", axis=1)

# Replace -1 values
X.replace(-1, 0, inplace=True)

# Convert features to numeric ONLY
X = X.apply(pd.to_numeric, errors="coerce")

# Fill NaN
X.fillna(0, inplace=True)

# =====================================================
# ENCODE LABEL
# =====================================================

le = LabelEncoder()
y = le.fit_transform(labels)

# Debug check
print("\n🔍 Class Distribution:")
print(pd.Series(y).value_counts())

# Save encoder
with open("../saved_models/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print("✅ Labels encoded")

# =====================================================
# TRAIN TEST SPLIT
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
# XGBOOST MODEL
# =====================================================

model = XGBClassifier(
    n_estimators=150,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='mlogloss'
)

print("🚀 Training XGBoost model...")

model.fit(X_train, y_train)

print("✅ Training completed")

# =====================================================
# EVALUATION
# =====================================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n🎯 XGBoost Accuracy:", accuracy)

# =====================================================
# SAVE MODEL
# =====================================================

with open("../saved_models/xgb_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\n✅ XGBoost model saved successfully!")

