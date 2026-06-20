# new xgboost training script

import pandas as pd
import pickle
import json

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# Load data
df = pd.read_csv("../../data/processed/traffic_dataset.csv")

df.rename(columns={"class1": "label"}, inplace=True)

labels = df["label"]

X = df.drop("label", axis=1)

# Clean
X.replace(-1, 0, inplace=True)
X = X.apply(pd.to_numeric, errors="coerce")
X.fillna(0, inplace=True)

# Save feature structure
feature_names = X.columns.tolist()

with open("../saved_models/general_features.json", "w") as f:
    json.dump(feature_names, f)

# Encode labels
le = LabelEncoder()
y = le.fit_transform(labels)

with open("../saved_models/general_label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Model
model = XGBClassifier(
    n_estimators=150,
    max_depth=6,
    eval_metric="mlogloss"
)

print("Training XGB General model...")
model.fit(X_train, y_train)

# Accuracy
pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, pred))

# Save
with open("../saved_models/xgb_general.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ XGB General model saved")
