"""
transcription.py
----------------
Handles automatic speech recognition (ASR) for multilingual audio input.
Uses Hugging Face Wav2Vec2 models for transcription.
"""

import os
import torch
import librosa
import pandas as pd
from tqdm import tqdm
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import logging
import warnings

warnings.filterwarnings("ignore")


# ----------------------------------------------------
# Directory setup
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(BASE_DIR, "..")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "transcription.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# ----------------------------------------------------
# Supported Languages
# ----------------------------------------------------
language_models = {
    "en": {"model_name": "facebook/wav2vec2-large-960h"},
    "de": {"model_name": "jonatasgrosman/wav2vec2-large-xlsr-53-german"},
    "es": {"model_name": "jonatasgrosman/wav2vec2-large-xlsr-53-spanish"},
    "zh": {"model_name": "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn"},
    "el": {"model_name": "facebook/wav2vec2-large-xlsr-53-greek"},
    "ar": {"model_name": "jonatasgrosman/wav2vec2-large-xlsr-53-arabic"},
}


# ----------------------------------------------------
# Model Loading
# ----------------------------------------------------
def load_language_model(language_code: str):
    """
    Loads the tokenizer and model for the given language.
    """
    if language_code not in language_models:
        raise ValueError(
            f"Unsupported language '{language_code}'. Supported: {list(language_models.keys())}"
        )

    model_name = language_models[language_code]["model_name"]
    logging.info(f"Loading ASR model for '{language_code}' ({model_name})")
    print(f"🎧 Loading ASR model for '{language_code}' ...")

    try:
        tokenizer = Wav2Vec2Tokenizer.from_pretrained(model_name)
        model = Wav2Vec2ForCTC.from_pretrained(model_name).to("cpu")  # use 'cuda' if available

        language_models[language_code]["tokenizer"] = tokenizer
        language_models[language_code]["model"] = model

        print(f"✅ Model loaded successfully for '{language_code}'\n")
        logging.info(f"Model loaded successfully for {language_code}")
    except Exception as e:
        print(f"❌ Failed to load model for '{language_code}': {e}")
        logging.error(f"Model load error for {language_code}: {e}")
        language_models[language_code]["tokenizer"] = None
        language_models[language_code]["model"] = None


# ----------------------------------------------------
# Transcribe a Single File
# ----------------------------------------------------
def transcribe_audio(file_path: str, tokenizer, model, device="cpu"):
    """
    Transcribes a single WAV file using the provided model and tokenizer.
    """
    try:
        audio, rate = librosa.load(file_path, sr=16000)
        input_values = tokenizer(audio, return_tensors="pt", padding="longest").input_values.to(device)
        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = tokenizer.decode(predicted_ids[0])

        transcription = transcription.lower().strip()
        logging.info(f"Transcribed: {os.path.basename(file_path)}")
        print(f"🗣️ Transcribed {os.path.basename(file_path)}")
        return transcription
    except Exception as e:
        print(f"❌ Error transcribing {file_path}: {e}")
        logging.error(f"Transcription error for {file_path}: {e}")
        return None


# ----------------------------------------------------
# Transcribe a Dataset
# ----------------------------------------------------
def transcribe_dataset(dataset_path: str, language_code: str, device="cpu"):
    """
    Transcribes all .wav files in a directory and returns results as a list of dicts.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset path '{dataset_path}' not found.")

    load_language_model(language_code)
    tokenizer = language_models[language_code]["tokenizer"]
    model = language_models[language_code]["model"]

    if not tokenizer or not model:
        raise RuntimeError(f"Failed to initialize ASR model for {language_code}")

    audio_files = [f for f in os.listdir(dataset_path) if f.lower().endswith(".wav")]
    total_files = len(audio_files)

    print(f"\n🔊 Transcribing {total_files} audio files ({language_code})...")
    transcriptions = []

    for audio_file in tqdm(audio_files, desc="Transcribing", unit="file"):
        file_path = os.path.join(dataset_path, audio_file)
        text = transcribe_audio(file_path, tokenizer, model, device)
        transcriptions.append({
            "file_name": audio_file,
            "transcription": text,
            "label": "Unknown"
        })

    return transcriptions


# ----------------------------------------------------
# Save Transcriptions
# ----------------------------------------------------
def save_transcriptions_to_csv(transcriptions, output_csv="transcriptions.csv"):
    """
    Saves transcription results to a CSV file in the project outputs directory.
    """
    output_dir = os.path.join(ROOT_DIR, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, output_csv)
    pd.DataFrame(transcriptions).to_csv(output_path, index=False)

    print(f"\n💾 Transcriptions saved to: {output_path}")
    logging.info(f"Transcriptions saved: {output_path}")
    return output_path
