"""
Prediction Integration Script
- Fetches the latest patient from the API.
- Loads the pre-trained model.
- Makes a prediction.
- Logs the prediction back to the API.
"""
import requests
import joblib
import pandas as pd
import warnings
from sklearn.exceptions import InconsistentVersionWarning

# Suppress warnings from scikit-learn version mismatches
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# API Configuration
BASE_API_URL = "http://127.0.0.1:8000/api/v1"
LATEST_PATIENT_URL = f"{BASE_API_URL}/patients/latest"
LOG_PREDICTION_URL = f"{BASE_API_URL}/predictions"

# Model Configuration
MODEL_PATH = "model.pkl"

def fetch_latest_patient():
    """Fetches the latest patient record from the API."""
    print(f"Fetching latest patient from: {LATEST_PATIENT_URL}")
    try:
        response = requests.get(LATEST_PATIENT_URL)
        response.raise_for_status() # Raises an error for 4xx or 5xx
        patient_data = response.json()
        print(f"✓ Success: Fetched data for patient_id: {patient_data.get('patient_id')}")
        return patient_data
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: Failed to fetch patient data. {e}")
        return None

def load_model(path):
    """Loads the pre-trained model from disk."""
    print(f"Loading model from: {MODEL_PATH}")
    try:
        model = joblib.load(path)
        print(f"✓ Success: Model '{MODEL_PATH}' loaded.")
        return model
    except FileNotFoundError:
        print(f"✗ Error: Model file not found at '{path}'.")
        print("  Please ensure 'model.pkl' is in the same directory.")
        return None
    except Exception as e:
        print(f"✗ Error: Failed to load model. {e}")
        return None

def preprocess_data(patient_data):
    """
    Prepares the single patient JSON data into a DataFrame
    ready for the model.
    
    *** IMPORTANT ***: This MUST match the preprocessing
    steps used to train your model.
    """
    print("Preprocessing data for model...")
    try:
        # Convert the single patient dict to a pandas DataFrame
        # The model expects a 2D array or DataFrame
        data_df = pd.DataFrame([patient_data])
        
        # --- Feature Engineering Example ---
        # Re-create any features your model expects
        # Example: 'age_years' and 'bmi'
        if 'age_days' in data_df.columns:
            data_df['age_years'] = data_df['age_days'] / 365.25
        
        if 'height' in data_df.columns and 'weight' in data_df.columns:
            # Ensure height is in meters for BMI calculation
            data_df['bmi'] = data_df['weight'] / ((data_df['height'] / 100) ** 2)

        # --- Column Selection ---
        # Select *only* the columns the model was trained on
        # and in the *exact* same order.
        
        # Define the list of features your model was trained on.
        # ** YOU MUST UPDATE THIS LIST **
        model_features = [
            'age_years',
            'gender',
            'height',
            'weight',
            'bmi',
            'ap_hi',
            'ap_lo',
            'cholesterol',
            'glucose',
            'smoke',
            'alcohol',
            'physical_activity'
        ]
        
        # Filter the DataFrame to only these features
        # and fill any missing columns (if any) with 0 or appropriate default
        data_df = data_df.reindex(columns=model_features, fill_value=0)
        
        print(f"✓ Success: Data preprocessed. Features: {list(data_df.columns)}")
        return data_df
        
    except Exception as e:
        print(f"✗ Error: Failed during data preprocessing. {e}")
        return None

def make_prediction(model, data):
    """Makes a prediction using the loaded model."""
    print("Making prediction...")
    try:
        # Predict probability (for a score)
        # model.predict_proba() returns [[prob_0, prob_1]]
        # We want the probability for class 1
        prediction_score = model.predict_proba(data)[0][1]
        
        # Predict the class (0 or 1)
        predicted_class = model.predict(data)[0]
        
        print(f"✓ Success: Prediction made.")
        print(f"  - Score (Prob of Disease): {prediction_score:.4f}")
        print(f"  - Class (0=No, 1=Yes):     {predicted_class}")
        
        return float(prediction_score), int(predicted_class)
        
    except Exception as e:
        print(f"✗ Error: Failed to make prediction. {e}")
        return None, None

def log_prediction(patient_id, score, class_):
    """Logs the prediction result back to the API."""
    print(f"Logging prediction for patient_id: {patient_id}...")
    
    payload = {
        "patient_id": patient_id,
        "prediction_score": score,
        "predicted_class": class_
    }
    
    try:
        response = requests.post(LOG_PREDICTION_URL, json=payload)
        response.raise_for_status()
        print("✓ Success: Prediction logged to database.")
        print(f"  - Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: Failed to log prediction. {e}")
        if e.response:
            print(f"  - API Response: {e.response.text}")

def main():
    print("\n--- Starting Prediction Pipeline ---")
    
    patient = fetch_latest_patient()
    if not patient:
        return

    model = load_model(MODEL_PATH)
    if not model:
        return

    # To preprocess, we need the full patient record
    # Let's get the other records
    try:
        patient_id = patient['patient_id']
        measurements = requests.get(f"{BASE_API_URL}/medical-measurements/patient/{patient_id}").json()[0]
        lifestyle = requests.get(f"{BASE_API_URL}/lifestyle-factors/patient/{patient_id}").json()[0]
        
        # Combine all data into one flat dictionary
        full_patient_record = {**patient, **measurements, **lifestyle}
    except Exception as e:
        print(f"✗ Error: Failed to get full patient record (measurements, lifestyle). {e}")
        return
        
    processed_data = preprocess_data(full_patient_record)
    if processed_data is None:
        return
        
    score, p_class = make_prediction(model, processed_data)
    if score is None:
        return
        
    log_prediction(patient['patient_id'], score, p_class)
    
    print("--- Pipeline Finished ---")

if __name__ == "__main__":
    main()
