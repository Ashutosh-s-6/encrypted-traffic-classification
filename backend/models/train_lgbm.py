import pandas as pd
import numpy as np
import joblib
import os

from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# ================= PATH SETUP =================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "traffic_dataset_updated.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "saved_models",
    "lgbm_model.pkl"
)

print("📂 Loading dataset...")

# ================= LOAD =================

df = pd.read_csv(DATA_PATH)

print("✅ Dataset loaded")

# ================= TARGET =================

y = df["class1"]

# Keep malicious if useful
X = df.drop(columns=["class1", "malicious"], errors="ignore")

# ================= CLEAN DATA =================

X.replace([np.inf, -np.inf], np.nan, inplace=True)

X.fillna(0, inplace=True)

# ================= SPLIT =================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ================= MODEL =================

model = LGBMClassifier(
    n_estimators=300,
    learning_rate=0.05,
    num_leaves=31,
    max_depth=10,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

# ================= TRAIN =================

model.fit(X_train, y_train)

print("✅ Model trained")

# ================= PREDICT =================

y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# ================= SAVE =================

joblib.dump(model, MODEL_PATH)

print("✅ LightGBM model saved!")