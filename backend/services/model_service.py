import pandas as pd
import joblib
import os
import pickle

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# ================= PATHS =================
RF_MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "rf1_new.pkl")
XGB_MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "xgb1_new.pkl")
LGBM_MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "lgbm_model.pkl")

LABEL_ENCODER_PATH = os.path.join(BASE_DIR, "saved_models", "label_encoder_new.pkl")

MALICIOUS_MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "malicious_model.pkl")
MALICIOUS_ENCODER_PATH = os.path.join(BASE_DIR, "saved_models", "malicious_encoder.pkl")


# ================= LOAD MODELS =================
def load_model(model_name):

    if model_name == "rf":
        print("🔵 Loading RF model...")
        return joblib.load(RF_MODEL_PATH)

    elif model_name == "xgb":
        print("🟢 Loading XGB model...")
        return joblib.load(XGB_MODEL_PATH)

    elif model_name == "lgbm":
        print("🌿 Loading LGBM model...")
        return joblib.load(LGBM_MODEL_PATH)

    else:
        raise ValueError(f"Invalid model selected: {model_name}")


def load_malicious_model():
    print("🔴 Loading Malicious model...")
    return joblib.load(MALICIOUS_MODEL_PATH)


# ================= FEATURE ALIGN =================
def align_features(df, expected_features):

    for col in expected_features:
        if col not in df.columns:
            print(f"⚠️ Adding missing column: {col}")
            df[col] = 0

    df = df[expected_features]

    return df


# ================= MAIN =================
def predict_traffic(file_path, model_name="rf"):

    print("\n📁 File received:", file_path)

    df = pd.read_csv(file_path)

    y_true = None

    # ================= HANDLE LABEL =================
    if "class1" in df.columns:
        y_true = df["class1"]
        df = df.drop(columns=["class1"])

    elif "label" in df.columns:
        y_true = df["label"]
        df = df.drop(columns=["label"])

    # ================= CLEAN =================
    df.replace(-1, 0, inplace=True)
    df = df.apply(pd.to_numeric, errors="coerce")
    df.fillna(0, inplace=True)

    # 🔥 QUICK FIX
    if "std_fiat" not in df.columns:
        print("⚠️ Adding std_fiat (quick fix)")
        df["std_fiat"] = 0

    if "std_biat" not in df.columns:
        print("⚠️ Adding std_biat (quick fix)")
        df["std_biat"] = 0

    # ================= LOAD TRAFFIC MODEL =================
    traffic_model = load_model(model_name)

    # ================= TRAFFIC ALIGN =================
    traffic_features = list(traffic_model.feature_names_in_)

    print("\n🧠 Traffic expects:", traffic_features)
    print("📊 Before alignment:", df.columns.tolist())

    df_traffic = align_features(df.copy(), traffic_features)

    print("📊 Traffic aligned:", df_traffic.columns.tolist())

    # ================= TRAFFIC PREDICTION =================
    traffic_pred = traffic_model.predict(df_traffic)

    # Decode for XGB
    if model_name in ["xgb", "lgbm"] and os.path.exists(LABEL_ENCODER_PATH):
        try:
            le = pickle.load(open(LABEL_ENCODER_PATH, "rb"))
            traffic_pred = le.inverse_transform(traffic_pred.astype(int))
        except Exception as e:
            print("⚠️ Traffic decode error:", e)

    # ================= LOAD MALICIOUS MODEL =================
    malicious_model = load_malicious_model()

    # ================= MALICIOUS ALIGN (🔥 FINAL FIX) =================
    mal_features = list(malicious_model.feature_names_in_)

    print("\n🧠 Malicious expects:", mal_features)

    df_mal = df.copy()

    for col in mal_features:
        if col not in df_mal.columns:
            print(f"⚠️ Adding missing for malicious: {col}")
            df_mal[col] = 0

    df_mal = df_mal[mal_features]

    print("📊 Malicious aligned:", df_mal.columns.tolist())

    # ================= MALICIOUS PREDICTION =================
    mal_encoded = malicious_model.predict(df_mal)
    mal_proba = malicious_model.predict_proba(df_mal)

    # Decode malicious
    try:
        le_mal = pickle.load(open(MALICIOUS_ENCODER_PATH, "rb"))
        mal_pred = le_mal.inverse_transform(mal_encoded)
    except Exception as e:
        print("⚠️ Malicious decode error:", e)
        mal_pred = mal_encoded

    # ================= DISTRIBUTION =================
    distribution = {str(k): int(v) for k, v in pd.Series(traffic_pred).value_counts().to_dict().items()}

    # ================= METRICS =================
    if y_true is not None:
        metrics = {
            "accuracy": accuracy_score(y_true, traffic_pred),
            "precision": precision_score(y_true, traffic_pred, average="macro", zero_division=0),
            "recall": recall_score(y_true, traffic_pred, average="macro", zero_division=0),
            "f1": f1_score(y_true, traffic_pred, average="macro", zero_division=0)
        }
    else:
        metrics = {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0}

    # ================= RISK ENGINE =================
    risk_labels = []
    risk_distribution = {"High": 0, "Medium": 0, "Low": 0}

    for i in range(len(df_traffic)):
        score = mal_proba[i][1]

        if score > 0.8:
            risk = "High"
        elif score > 0.4:
            risk = "Medium"
        else:
            risk = "Low"

        risk_labels.append(risk)
        risk_distribution[risk] += 1

    overall_risk = (
        "High" if risk_distribution["High"] > 0 else
        "Medium" if risk_distribution["Medium"] > 0 else
        "Low"
    )

    # ================= ENTITY =================
    ip_analysis = {}

    for i in range(len(df_traffic)):
        ip_analysis[f"Flow-{i+1}"] = {
            "traffic": str(traffic_pred[i]),
            "malicious": str(mal_pred[i]),
            "risk": risk_labels[i],
            "confidence": float(round(float(mal_proba[i][1]) * 100, 2))
        }

    suspicious = [k for k, v in ip_analysis.items() if v["risk"] == "High"][:20]

    print("✅ Prediction complete\n")

    return distribution, metrics, {
        "risk_distribution": risk_distribution,
        "overall_risk": overall_risk,
        "suspicious_entities": suspicious,
        "ip_analysis": ip_analysis
    }