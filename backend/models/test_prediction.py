import sys
import os

# add backend folder to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.model_service import predict_traffic

file_path = "../data/processed/traffic_dataset.csv"

result = predict_traffic(file_path)

print("Prediction distribution:\n")
print(result)