from flask import Blueprint, request, jsonify
import os

from services.model_service import predict_traffic

routes = Blueprint("routes", __name__)


# =====================================================
# PREDICT ROUTE
# =====================================================

@routes.route("/predict", methods=["POST"])
def predict():

    try:
        file = request.files["file"]
        model_name = request.form.get("model", "rf")  # rf / xgb

        # Save uploaded file
        upload_dir = os.path.join("data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        upload_path = os.path.join(upload_dir, file.filename)
        file.save(upload_path)

        print(f"📁 File received: {file.filename}")
        print(f"🤖 Model selected: {model_name}")

        # =====================================================
        # 🔥 CALL UPDATED FUNCTION (3 RETURNS NOW)
        # =====================================================

        distribution, metrics, security = predict_traffic(upload_path, model_name)

        # =====================================================
        # RESPONSE
        # =====================================================

        return jsonify({
            "distribution": distribution,
            "metrics": metrics,
            "security": security
        })

    except Exception as e:
        print("❌ Error in /predict:", e)

        return jsonify({
            "error": "Failed to process file",
            "details": str(e)
        }), 500