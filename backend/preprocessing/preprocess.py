# Preprocessing functions for handling and cleaning the data
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder

def preprocess_data(df, training=True):

    # Replace invalid values
    df.replace(-1, pd.NA, inplace=True)

    # Drop missing rows
    df.dropna(inplace=True)

    # Rename label column
    df.rename(columns={"class1": "label"}, inplace=True)

    if training:
        # Encode labels
        le = LabelEncoder()
        df["label"] = le.fit_transform(df["label"])

        # Save encoder
        pickle.dump(le, open("../saved_models/label_encoder.pkl", "wb"))

    else:
        # Load encoder
        le = pickle.load(open("backend/saved_models/label_encoder.pkl", "rb"))

    return df