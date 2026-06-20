import pandas as pd
import os

DATA_DIR = os.path.join("..", "data", "uploads")
OUTPUT_PATH = os.path.join("..", "data", "processed", "final_dataset.csv")

all_dfs = []

print("🚀 Starting dataset preparation...\n")

for file in os.listdir(DATA_DIR):

    if file.endswith(".csv"):

        path = os.path.join(DATA_DIR, file)

        print(f"Processing: {file}")

        df = pd.read_csv(path)

        df.columns = df.columns.str.strip()

        if "class1" not in df.columns:
            continue

        # ✅ SAVE LABEL FIRST
        label_col = df["class1"]

        # Remove label
        df = df.drop(columns=["class1"])

        # Convert only features
        df = df.apply(pd.to_numeric, errors="coerce")

        # Clean data
        df.replace(-1, 0, inplace=True)
        df.fillna(0, inplace=True)

        # Add label back
        df["class1"] = label_col

        all_dfs.append(df)

print("\n📊 Merging datasets...")

final_df = pd.concat(all_dfs, ignore_index=True)

print("Final shape:", final_df.shape)

print("\n🔍 Class Distribution:")
print(final_df["class1"].value_counts())

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
final_df.to_csv(OUTPUT_PATH, index=False)

print(f"\n✅ Final dataset saved at: {OUTPUT_PATH}")