# acoustic_extraction.py
import os
import librosa
import numpy as np
import pandas as pd
import opensmile
from tqdm import tqdm
from pyAudioAnalysis import ShortTermFeatures, audioBasicIO
import warnings
import logging

warnings.filterwarnings('ignore')

# Configure logging
log_path = os.path.join(os.path.dirname(__file__), 'feature_extraction.log')
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


def extract_librosa_features(file_path, sr=22050):
    try:
        y, sr = librosa.load(file_path, sr=sr, duration=5.0)
    except Exception as e:
        logging.error(f"librosa.load error for {file_path}: {e}")
        return {}
    
    features = {}
    try:
        features['duration'] = librosa.get_duration(y=y, sr=sr)
        features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y))
        features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        mfccs_mean = np.mean(mfccs, axis=1)
        mfccs_std = np.std(mfccs, axis=1)
        for i in range(len(mfccs_mean)):
            features[f'mfcc_{i+1}_mean'] = mfccs_mean[i]
            features[f'mfcc_{i+1}_std'] = mfccs_std[i]
        
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        chroma_std = np.std(chroma, axis=1)
        for i in range(len(chroma_mean)):
            features[f'chroma_{i+1}_mean'] = chroma_mean[i]
            features[f'chroma_{i+1}_std'] = chroma_std[i]
        
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        contrast_mean = np.mean(contrast, axis=1)
        contrast_std = np.std(contrast, axis=1)
        for i in range(len(contrast_mean)):
            features[f'spectral_contrast_{i+1}_mean'] = contrast_mean[i]
            features[f'spectral_contrast_{i+1}_std'] = contrast_std[i]
        
        tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
        tonnetz_mean = np.mean(tonnetz, axis=1)
        tonnetz_std = np.std(tonnetz, axis=1)
        for i in range(len(tonnetz_mean)):
            features[f'tonnetz_{i+1}_mean'] = tonnetz_mean[i]
            features[f'tonnetz_{i+1}_std'] = tonnetz_std[i]
        
    except Exception as e:
        logging.error(f"Librosa feature extraction error for {file_path}: {e}")
        return {}
    
    return features

def extract_pyaudio_features(file_path):
    try:
        [Fs, x] = audioBasicIO.read_audio_file(file_path)
        x = audioBasicIO.stereo_to_mono(x)
    except Exception as e:
        logging.error(f"audioBasicIO.read_audio_file error for {file_path}: {e}")
        return {}
    
    features = {}
    try:
        features_short, feature_names = ShortTermFeatures.feature_extraction(x, Fs, 0.050*Fs, 0.025*Fs)
        features_mean = np.mean(features_short, axis=1)
        features_std = np.std(features_short, axis=1)
        
        for i, fname in enumerate(feature_names):
            features[f'pyaudio_{fname}_mean'] = features_mean[i]
            features[f'pyaudio_{fname}_std'] = features_std[i]
        
    except Exception as e:
        logging.error(f"ShortTermFeatures.feature_extraction error for {file_path}: {e}")
        return {}
    
    return features

def extract_opensmile_features(file_path):
    try:
        smile = opensmile.Smile(
            feature_set=opensmile.FeatureSet.ComParE_2016,
            feature_level=opensmile.FeatureLevel.Functionals
        )
        result = smile.process_file(file_path)
        features = result.to_dict(orient='records')[0]
        features = {f'opensmile_{k}': v for k, v in features.items()}
        
    except Exception as e:
        logging.error(f"OpenSMILE feature extraction error for {file_path}: {e}")
        return {}
    
    return features

def extract_all_features(file_path):
    features = {}
    
    librosa_feats = extract_librosa_features(file_path)
    if librosa_feats:
        features.update(librosa_feats)
    
    pyaudio_feats = extract_pyaudio_features(file_path)
    if pyaudio_feats:
        features.update(pyaudio_feats)
    
    opensmile_feats = extract_opensmile_features(file_path)
    if opensmile_feats:
        features.update(opensmile_feats)
    print('Extracted Acoustic Features')
    
    return features

def process_audio_files_in_directory(directory_path):
    features_list = []
    try:
        audio_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.wav')]
        if not audio_files:
            logging.warning(f"No audio files found in {directory_path}.")
            return features_list
    except Exception as e:
        logging.error(f"Error accessing path {directory_path}: {e}")
        return features_list

    for file_path in tqdm(audio_files, desc="Processing Audio Files"):
        try:
            features = extract_all_features(file_path)
            if not features:
                logging.warning(f"No features extracted for {file_path}. Skipping.")
                continue
            features['label'] = 'Unknown'
            features['file_name'] = os.path.basename(file_path)
            features_list.append(features)
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
    
    return features_list

def save_features_to_csv(features_list, output_filename='Acoustic.csv'):
    if features_list:
        df = pd.DataFrame(features_list)
        try:
            df.to_csv(output_filename, index=False)
            logging.info(f"Saved {output_filename} with shape {df.shape}")
        except Exception as e:
            logging.error(f"Error saving {output_filename}: {e}")

def verify_saved_csv(csv_file):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        logging.info(f"{csv_file} - Shape: {df.shape}")
        print(df.head())
    else:
        logging.warning(f"{csv_file} not found.")
