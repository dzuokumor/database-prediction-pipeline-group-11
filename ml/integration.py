"""
Responsibilities:
- Fetch the latest patient data entry via API.
- Preprocess data (handle missing values, scale features, etc.).
"""

import requests
import pandas as pd
from sklearn.preprocessing import StandardScaler


# API endpoint
API_URL = "http://127.0.0.1:8000/api/v1/patients/latest"


def fetch_latest_data(api_url: str):
    """
    Fetch the latest patient data entry from the API.
    """
    print("Fetching latest patient data from API...")

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        print("Latest data entry fetched successfully.")
        return data
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"API request failed: {e}")


def preprocess_data(data: dict) -> pd.DataFrame:
    """
    Preprocess data for ML model use.

    Steps:
    - Convert JSON to DataFrame
    - Handle missing values
    - Drop irrelevant columns
    - Scale numeric features
    """
    print("Starting data preprocessing...")

    # Convert JSON data to DataFrame
    df = pd.DataFrame([data])
    print(f"Data received with shape: {df.shape}")

    # Handle missing numeric values
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    if not numeric_cols.empty:
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        print(f"Filled missing numeric values with median: {list(numeric_cols)}")

    # Handle missing categorical values
    categorical_cols = df.select_dtypes(include=["object"]).columns
    if not categorical_cols.empty:
        df[categorical_cols] = df[categorical_cols].fillna("Unknown")
        print(f"Filled missing categorical values with 'Unknown': {list(categorical_cols)}")

    # Drop irrelevant columns
    drop_cols = ["id", "created_at", "updated_at"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
    print(f"Dropped irrelevant columns if present: {drop_cols}")

    # Scale numeric features
    if not numeric_cols.empty:
        scaler = StandardScaler()
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
        print(f"Scaled numeric columns: {list(numeric_cols)}")
    else:
        print("No numeric columns found to scale.")

    print("Preprocessing complete.")
    return df


def main():
    """
    Fetch, preprocess, and save the latest data entry for ML prediction.
    """
    latest_entry = fetch_latest_data(API_URL)
    processed_df = preprocess_data(latest_entry)

    # Save processed data
    output_path = "ml/processed_latest_entry.csv"
    processed_df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}\n")

    # Display preview
    print("Preprocessed data (ready for ML prediction):")
    print(processed_df.head())


if __name__ == "__main__":
    main()
