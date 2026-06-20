import pandas as pd

df = pd.read_csv("../../data/processed/traffic_dataset.csv")

print("Dataset shape:", df.shape)

print("\nColumns:\n", df.columns)

print("\nSample rows:")
print(df.head())

print("\nClass distribution:")
print(df["class1"].value_counts())