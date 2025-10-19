"""
prediction.py
Handles model loading, feature extraction, scaling, and final dementia classification.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import NotFittedError

# Import your feature extraction scripts
from backend.src.acoustic_extraction import extract_acoustic_features
from backend.src.linguistic_extraction import extract_linguistic_features


# ==========================================
# PATH CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "random_forest_model.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.joblib")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUTS_DIR, exist_ok=True)


# ==========================================
# LOAD MODEL AND SCALER
# ==========================================
def load_model_and_scaler():
    """Load trained model and scaler from the models directory."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"❌ Model file not found at {MODEL_PATH}")
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"❌ Scaler file not found at {SCALER_PATH}")

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    print("✅ Model and Scaler loaded successfully.")
    return model, scaler


# ==========================================
# FEATURE EXTRACTION
# ==========================================
def prepare_features(audio_path, language_code):
    """
    Extract and combine acoustic + linguistic features from an audio file.
    Returns a pandas DataFrame ready for scaling.
    """
    print(f"🎧 Extracting features for file: {audio_path}")

    # Extract acoustic and linguistic features using your existing functions
    acoustic_df = extract_acoustic_features(audio_path)
    linguistic_df = extract_linguistic_features(audio_path, language_code)

    # Combine the two feature sets
    combined_df = pd.concat([acoustic_df, linguistic_df], axis=1)
    combined_df.fillna(combined_df.median(), inplace=True)

    print(f"✅ Combined feature vector: {combined_df.shape[1]} features.")
    return combined_df


# ==========================================
# PREDICTION
# ==========================================
def predict_final_classification(audio_path, language_code):
    """
    Main callable function for the Flask API.
    Takes an audio file path and language code, returns classification result.
    """
    try:
        model, scaler = load_model_and_scaler()
        combined_features = prepare_features(audio_path, language_code)

        # Ensure correct feature scaling
        try:
            scaled_features = scaler.transform(combined_features)
        except NotFittedError:
            print("⚠️ Scaler not fitted. Fitting a new one temporarily.")
            scaled_features = scaler.fit_transform(combined_features)

        # Predict probability and class
        probabilities = model.predict_proba(scaled_features)[:, 1]
        prediction = int(np.round(probabilities.mean()))

        # Convert to readable label
        label = "Alzheimer's Detected" if prediction == 1 else "Healthy Control"

        # Log and return
        print(f"🧠 Prediction: {label} (Probability: {probabilities.mean():.2f})")
        return label

    except Exception as e:
        print(f"❌ Error during prediction: {str(e)}")
        return "Error: Prediction failed."


# ==========================================
# LOCAL TEST (Optional)
# ==========================================
if __name__ == "__main__":
    # Example local test — change to your WAV file path
    test_audio = os.path.join(BASE_DIR, "uploads", "recording.wav")
    test_lang = "en"  # example language code
    result = predict_final_classification(test_audio, test_lang)
    print(f"\nFinal Classification Result: {result}")
