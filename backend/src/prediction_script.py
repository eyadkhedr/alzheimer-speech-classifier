"""
prediction_script.py
Runs the full dementia prediction pipeline:
1. Segments input audio
2. Extracts acoustic + linguistic features
3. Runs the trained ML model
4. Applies weighted majority voting to determine AD/HC classification
"""

import os
import shutil
import pandas as pd
import logging
import torch

# Import project modules
from backend.src.segmentation import process_single_audio_file
from backend.src.acoustic_extraction import extract_all_features
from backend.src.linguistic_extraction import extract_linguistic_features
from backend.src.transcription import transcribe_audio, load_language_model, language_models
from backend.api.prediction import (
    load_model_and_scaler,
    predict,
    save_predictions,
    weighted_majority_voting,
)

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(BASE_DIR, "..")
MODEL_DIR = os.path.join(ROOT_DIR, "models")
UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads")
PROCESSED_DIR = os.path.join(ROOT_DIR, "processed_audio")
LOG_DIR = os.path.join(ROOT_DIR, "logs")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "prediction_pipeline.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ----------------------------------------------------
# Load Model + Scaler
# ----------------------------------------------------
MODEL_PATH = os.path.join(MODEL_DIR, "random_forest_model.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")

model, scaler = load_model_and_scaler(MODEL_PATH, SCALER_PATH)
logging.info("✅ Model and scaler loaded successfully.")


# ----------------------------------------------------
# Utilities
# ----------------------------------------------------
def delete_directory(directory_path: str):
    """Delete a directory and its contents."""
    if os.path.exists(directory_path):
        try:
            shutil.rmtree(directory_path)
            logging.info(f"Deleted directory: {directory_path}")
        except Exception as e:
            logging.error(f"Error deleting directory {directory_path}: {e}")


def safe_delete_file(file_path: str):
    """Delete file if it exists."""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {e}")


# ----------------------------------------------------
# Main Prediction Function
# ----------------------------------------------------
def predict_final_classification(audio_file_path: str, lang: str) -> str:
    """
    Full pipeline for audio-based dementia classification.
    Returns 'AD' or 'HC'.
    """

    classification_label = "Unknown"

    try:
        logging.info(f"🚀 Starting prediction pipeline for file: {audio_file_path}")

        # 1. Segment Audio
        process_single_audio_file(audio_file_path, output_folder=PROCESSED_DIR)

        # 2. Collect Segment Paths
        segment_files = sorted(
            [os.path.join(PROCESSED_DIR, f) for f in os.listdir(PROCESSED_DIR) if f.endswith(".wav")]
        )
        if not segment_files:
            raise FileNotFoundError("No audio segments found after segmentation.")

        logging.info(f"🧩 Found {len(segment_files)} audio segments for processing.")

        # 3. Load Language Model
        load_language_model(lang)
        tokenizer = language_models[lang]["tokenizer"]
        asr_model = language_models[lang]["model"]

        results = []

        for segment_path in segment_files:
            logging.info(f"Processing segment: {segment_path}")

            # --- Extract Acoustic Features ---
            acoustic_features = extract_all_features(segment_path)
            acoustic_df = pd.DataFrame([acoustic_features])

            # --- Transcribe Segment ---
            transcription = transcribe_audio(segment_path, tokenizer, asr_model, device="cpu")

            # --- Extract Linguistic Features ---
            linguistic_df = extract_linguistic_features(transcription, lang)

            # --- Combine Features ---
            combined_features = pd.concat([acoustic_df, linguistic_df], axis=1)

            # --- Predict Probability ---
            preds, probs = predict(model, scaler, combined_features)
            positive_prob = probs[0]
            threshold = 0.28
            predicted_label = 1 if positive_prob >= threshold else 0

            acoustic_df["Prediction"] = predicted_label
            acoustic_df["Probability"] = positive_prob
            acoustic_df["file_name"] = os.path.basename(segment_path)

            results.append(acoustic_df)

        # 4. Combine and Save All Results
        all_results_df = pd.concat(results, ignore_index=True)
        save_predictions(all_results_df, all_results_df["Prediction"], all_results_df["Probability"])

        # 5. Weighted Majority Voting
        classification_result = weighted_majority_voting(all_results_df)
        classification_label = "HC" if classification_result == 0 else "AD"

        logging.info(f"✅ Final classification result: {classification_label}")
        return classification_label

    except Exception as e:
        logging.error(f"Error during classification: {e}")
        return "Error: Could not classify audio."

    finally:
        # Clean up after prediction
        delete_directory(PROCESSED_DIR)
        safe_delete_file(os.path.join(UPLOAD_DIR, "recording.wav"))
        safe_delete_file(os.path.join(UPLOAD_DIR, "test_connection.wav"))
