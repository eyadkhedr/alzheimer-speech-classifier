"""
acoustic_extraction.py
Extracts acoustic features from audio files for dementia classification.

This module combines Librosa, PyAudioAnalysis, and OpenSMILE feature extraction
into a single callable function for use in model inference or dataset creation.
"""

import os
import librosa
import numpy as np
import pandas as pd
import opensmile
from tqdm import tqdm
from pyAudioAnalysis import ShortTermFeatures, audioBasicIO
import warnings
import logging

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------
warnings.filterwarnings('ignore')

# Define directories dynamically (relative to repo)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "feature_extraction.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# ----------------------------------------------------
# Librosa Feature Extraction
# ----------------------------------------------------
def extract_librosa_features(file_path, sr=22050):
    """Extract Librosa-based features such as MFCC, chroma, spectral features."""
    try:
        y, sr = librosa.load(file_path, sr=sr, duration=5.0)
    except Exception as e:
        logging.error(f"librosa.load error for {file_path}: {e}")
        return {}

    features = {}
    try:
        features["duration"] = librosa.get_duration(y=y, sr=sr)
        features["zero_crossing_rate"] = np.mean(librosa.feature.zero_crossing_rate(y))
        features["spectral_centroid"] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        features["spectral_bandwidth"] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        features["spectral_rolloff"] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))

        # MFCC
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        for i in range(40):
            features[f"mfcc_{i+1}_mean"] = np.mean(mfccs[i])
            features[f"mfcc_{i+1}_std"] = np.std(mfccs[i])

        # Chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        for i in range(chroma.shape[0]):
            features[f"chroma_{i+1}_mean"] = np.mean(chroma[i])
            features[f"chroma_{i+1}_std"] = np.std(chroma[i])

        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        for i in range(contrast.shape[0]):
            features[f"spectral_contrast_{i+1}_mean"] = np.mean(contrast[i])
            features[f"spectral_contrast_{i+1}_std"] = np.std(contrast[i])

        # Tonnetz
        tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
        for i in range(tonnetz.shape[0]):
            features[f"tonnetz_{i+1}_mean"] = np.mean(tonnetz[i])
            features[f"tonnetz_{i+1}_std"] = np.std(tonnetz[i])

    except Exception as e:
        logging.error(f"Librosa feature extraction error for {file_path}: {e}")
        return {}

    return features


# ----------------------------------------------------
# PyAudioAnalysis Feature Extraction
# ----------------------------------------------------
def extract_pyaudio_features(file_path):
    """Extract short-term statistical features using PyAudioAnalysis."""
    try:
        [Fs, x] = audioBasicIO.read_audio_file(file_path)
        x = audioBasicIO.stereo_to_mono(x)
    except Exception as e:
        logging.error(f"audioBasicIO.read_audio_file error for {file_path}: {e}")
        return {}

    try:
        feats, names = ShortTermFeatures.feature_extraction(x, Fs, 0.050 * Fs, 0.025 * Fs)
        f_mean, f_std = np.mean(feats, axis=1), np.std(feats, axis=1)
        return {f"pyaudio_{name}_mean": f_mean[i] for i, name in enumerate(names)} | \
               {f"pyaudio_{name}_std": f_std[i] for i, name in enumerate(names)}
    except Exception as e:
        logging.error(f"ShortTermFeatures.feature_extraction error for {file_path}: {e}")
        return {}


# ----------------------------------------------------
# OpenSMILE Feature Extraction
# ----------------------------------------------------
def extract_opensmile_features(file_path):
    """Extract ComParE_2016-level functionals using OpenSMILE."""
    try:
        smile = opensmile.Smile(
            feature_set=opensmile.FeatureSet.ComParE_2016,
            feature_level=opensmile.FeatureLevel.Functionals,
        )
        result = smile.process_file(file_path)
        features = result.to_dict(orient="records")[0]
        return {f"opensmile_{k}": v for k, v in features.items()}
    except Exception as e:
        logging.error(f"OpenSMILE feature extraction error for {file_path}: {e}")
        return {}


# ----------------------------------------------------
# Combined Feature Extraction
# ----------------------------------------------------
def extract_acoustic_features(file_path):
    """Unified entry point for extracting all acoustic features."""
    all_features = {}
    all_features.update(extract_librosa_features(file_path))
    all_features.update(extract_pyaudio_features(file_path))
    all_features.update(extract_opensmile_features(file_path))

    if not all_features:
        logging.warning(f"No features extracted for {file_path}.")
    else:
        logging.info(f"Extracted {len(all_features)} acoustic features from {file_path}.")
        print("🎧 Extracted Acoustic Features")

    return pd.DataFrame([all_features])


# ----------------------------------------------------
# Batch Processing (Optional)
# ----------------------------------------------------
def process_audio_directory(directory_path):
    """Process all WAV files in a directory and return a DataFrame."""
    features_list = []
    audio_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".wav")]

    if not audio_files:
        logging.warning(f"No audio files found in {directory_path}.")
        return pd.DataFrame()

    for f in tqdm(audio_files, desc="Extracting Features"):
        feats = extract_acoustic_features(f)
        feats["label"] = "Unknown"
        feats["file_name"] = os.path.basename(f)
        features_list.append(feats)

    return pd.concat(features_list, ignore_index=True) if features_list else pd.DataFrame()
