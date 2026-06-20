import pandas as pd

# =====================================================
# LOAD DATASET
# =====================================================

df = pd.read_csv("../../data/processed/traffic_dataset.csv")

print("✅ Dataset loaded")
print("Columns:", df.columns)

# =====================================================
# CREATE MALICIOUS COLUMN
# =====================================================

def map_malicious(label):
    label = str(label).strip().upper()

    if label in ["P2P", "FT"]:
        return "Malicious"
    else:
        return "Benign"

# Apply function
df["malicious"] = df["class1"].apply(map_malicious)

print("✅ Malicious column created")

# =====================================================
# SAVE NEW DATASET
# =====================================================

output_path = "../../data/processed/traffic_dataset_updated.csv"

df.to_csv(output_path, index=False)

print(f"✅ Saved at: {output_path}")