# prediction.py
import joblib
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_model_and_scaler(model_path, scaler_path):
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print("\nModel and Scaler loaded successfully from disk.")
        return model, scaler
    else:
        raise FileNotFoundError("Model or Scaler file does not exist. Please train and save before loading.")

def preprocess_data(acoustic_file, linguistic_file):
    acoustic_df = pd.read_csv(acoustic_file)
    linguistic_df = pd.read_csv(linguistic_file)

    print(f"\nAcoustic data loaded: {acoustic_df.shape[0]} samples, {acoustic_df.shape[1]} features.")
    print(f"Linguistic data loaded: {linguistic_df.shape[0]} samples, {linguistic_df.shape[1]} features.")

    acoustic_df = acoustic_df[acoustic_df['label'] == 'Unknown']
    linguistic_df = linguistic_df[linguistic_df['label'] == 'Unknown']

    acoustic_df.reset_index(drop=True, inplace=True)
    linguistic_df.reset_index(drop=True, inplace=True)

    min_samples = min(acoustic_df.shape[0], linguistic_df.shape[0])
    acoustic_df = acoustic_df.sample(n=min_samples, random_state=42).reset_index(drop=True)
    linguistic_df = linguistic_df.sample(n=min_samples, random_state=42).reset_index(drop=True)

    acoustic_features = acoustic_df.drop(columns=['label', 'file_name'], errors='ignore')
    linguistic_features = linguistic_df.drop(columns=['label'], errors='ignore')

    acoustic_features.fillna(acoustic_features.median(), inplace=True)
    linguistic_features.fillna(linguistic_features.median(), inplace=True)

    combined_features = pd.concat([acoustic_features, linguistic_features], axis=1)
    return combined_features, acoustic_df

def predict(model, scaler, combined_features):
    scaled_features = scaler.transform(combined_features)

    significant_features = model.feature_names_in_
    features_df = pd.DataFrame(scaled_features, columns=combined_features.columns)
    selected_features = features_df[significant_features]

    predictions = model.predict(selected_features)
    probabilities = model.predict_proba(selected_features)[:, 1]
    return predictions, probabilities

def save_predictions(acoustic_df, predictions, probabilities, output_file='predictions.csv'):
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, output_file)

    acoustic_df['Prediction'] = predictions
    acoustic_df['Probability'] = probabilities
    acoustic_df[['file_name', 'Prediction', 'Probability']].to_csv(output_path, index=False)
    print(f"\nPredictions saved to {output_path}")
    return output_path


def weighted_majority_voting(df):
    weighted_sum_1 = df[df['Prediction'] == 1]['Probability'].sum()
    weighted_sum_0 = (1 - df[df['Prediction'] == 0]['Probability']).sum()
    return 1 if weighted_sum_1 > weighted_sum_0 else 0

def final_classification(input_csv):
    df = pd.read_csv(input_csv)
    print("\nFinal Classification:")
    wmv_result = weighted_majority_voting(df)
    print(f"Weighted Majority Voting: {wmv_result}")
