import os
import pandas as pd
import torch
from segmentation import process_single_audio_file
from acoustic_extraction import extract_all_features
from linguistic_extraction import extract_linguistic_features
from transcription import transcribe_audio, load_language_model, language_models
from prediction import load_model_and_scaler, predict, save_predictions, final_classification, weighted_majority_voting
import shutil

# Paths to model and scaler
MODEL_PATH = r"D:\ISEF Application\dementia_detector\server\model\random_forest_model.joblib"  # Update with the actual path
SCALER_PATH = r"D:\ISEF Application\dementia_detector\server\model\scaler.joblib"  # Update with the actual path

# Load model and scaler
model, scaler = load_model_and_scaler(MODEL_PATH, SCALER_PATH)

def delete_directory(directory_path):
    if os.path.exists(directory_path):
        try:
            shutil.rmtree(directory_path)
            print(f"Directory '{directory_path}' and all its contents have been deleted.")
        except Exception as e:
            print(f"Error deleting directory: {e}")
    else:
        print(f"Directory '{directory_path}' does not exist.")

def predict_final_classification(audio_file_path, lang):
    processed_folder = r'D:\ISEF Application\dementia_detector\server\server\processed_audio'
    classification_label = "Unknown"  # Default classification in case of failure
    try:
        # Create output folder for processed audio
        os.makedirs(processed_folder, exist_ok=True)

        # Process segmentation
        process_single_audio_file(audio_file_path, output_folder=processed_folder)

        # Get all audio segment paths
        segment_files = [
            os.path.join(processed_folder, file) 
            for file in sorted(os.listdir(processed_folder)) 
            if file.endswith('.wav')
        ]

        if not segment_files:
            raise FileNotFoundError("No audio segments found after processing.")

        # Load language model
        load_language_model(lang)
        tokenizer = language_models[lang]['tokenizer']
        asr_model = language_models[lang]['model']

        # Accumulate predictions and probabilities
        results = []

        for segment_path in segment_files:
            # Extract acoustic features
            acoustic_features = extract_all_features(segment_path)
            acoustic_features_df = pd.DataFrame([acoustic_features])

            # Transcribe the audio segment
            transcription = transcribe_audio(segment_path, tokenizer, asr_model, device='cpu')

            # Extract linguistic features
            linguistic_features = extract_linguistic_features(transcription, lang)
            linguistic_features_df = pd.DataFrame([linguistic_features])

            # Combine features for prediction
            combined_features = pd.concat([acoustic_features_df, linguistic_features_df], axis=1)

            # Get the probability of the positive class (AD)
            positive_prob = predict(model, scaler, combined_features)[1][0]  # assuming binary classification and [0] for the single row

            # Set custom threshold
            threshold = 0.28  # Example: change as needed

            # Classify based on threshold
            predicted_label = 1 if positive_prob >= threshold else 0

            # Store results
            acoustic_features_df['Prediction'] = [predicted_label]
            acoustic_features_df['Probability'] = [positive_prob]
            acoustic_features_df['file_name'] = os.path.basename(segment_path)


            results.append(acoustic_features_df)

        # Combine all results into a single DataFrame
        all_results_df = pd.concat(results, ignore_index=True)

        # Save predictions to a CSV
        save_predictions(all_results_df, all_results_df['Prediction'], all_results_df['Probability'])

        # Final classification
        classification_result = weighted_majority_voting(all_results_df)

        classification_label = "HC" if classification_result == 0 else "AD"

        return classification_label

    except Exception as e:
        print(f"Error: {e}")
        return "Error: Could not classify audio."
    finally:
        # Delete the processed audio directory after all operations
        delete_directory(processed_folder)
        os.remove(r"D:\ISEF Application\dementia_detector\server\server\uploads\recording.wav")
        os.remove(r"D:\ISEF Application\dementia_detector\server\server\uploads\test_connection.wav")