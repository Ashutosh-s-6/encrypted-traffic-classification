import pandas as pd
import pickle
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv("../../data/processed/traffic_dataset_updated.csv")

print("✅ Dataset loaded")

# =====================================================
# FEATURES & TARGET
# =====================================================

X = df.drop(["class1", "malicious"], axis=1)
y = df["malicious"]

# =====================================================
# ENCODE LABELS
# =====================================================

le = LabelEncoder()
y = le.fit_transform(y)

# Save encoder
pickle.dump(le, open("../saved_models/malicious_encoder.pkl", "wb"))

print("✅ Label encoding done")

# =====================================================
# TRAIN TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =====================================================
# MODEL
# =====================================================

model = XGBClassifier(
    n_estimators=150,
    max_depth=6,
    learning_rate=0.1,
    eval_metric="logloss"
)

# Train
model.fit(X_train, y_train)

print("✅ Model trained")

# =====================================================
# EVALUATE
# =====================================================

preds = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, preds))
print("\nClassification Report:\n", classification_report(y_test, preds))

# =====================================================
# SAVE MODEL
# =====================================================

pickle.dump(model, open("../saved_models/malicious_model.pkl", "wb"))

print("\n✅ Malicious model saved successfully!")