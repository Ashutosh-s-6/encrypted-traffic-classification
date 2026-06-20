import pandas as pd
import os

files = [
    "../../data/raw/TimeBasedFeatures-Dataset-15s-AllInOne.arff",
    "../../data/raw/TimeBasedFeatures-Dataset-30s-AllInOne.arff",
    "../../data/raw/TimeBasedFeatures-Dataset-60s-AllInOne.arff",
    "../../data/raw/TimeBasedFeatures-Dataset-120s-AllInOne.arff"
]

dfs = []

for file in files:
    print(f"Processing {file}...")

    with open(file, "r") as f:
        lines = f.readlines()

    # find where actual data starts
    data_start = False
    data_lines = []
    columns = []

    for line in lines:

        # collect column names
        if line.lower().startswith("@attribute"):
            parts = line.split()
            columns.append(parts[1])

        if line.lower().startswith("@data"):
            data_start = True
            continue

        if data_start:
            row = line.strip()

            if row == "":
                continue

            # skip rows with empty values
            if ",," in row:
                continue

            data_lines.append(row.split(","))

    df = pd.DataFrame(data_lines, columns=columns)

    dfs.append(df)

dataset = pd.concat(dfs, ignore_index=True)

print("Final dataset shape:", dataset.shape)

os.makedirs("../../data/processed", exist_ok=True)

dataset.to_csv("../../data/processed/traffic_dataset.csv", index=False)

print("Dataset saved successfully.")