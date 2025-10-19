# transcription.py
import os
import torch
import librosa
import pandas as pd
from tqdm import tqdm
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import warnings

warnings.filterwarnings("ignore")

language_models = {
    'es': {
        'model_name': 'jonatasgrosman/wav2vec2-large-xlsr-53-spanish'
    },
    'zh': {
        'model_name': 'jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn'
    },
    'de': {
        'model_name': 'jonatasgrosman/wav2vec2-large-xlsr-53-german'
    },
    'en': {
        'model_name': 'facebook/wav2vec2-large-960h'
    },
    'el': {
        'model_name': 'facebook/wav2vec2-large-xlsr-53-greek'
    },
    'ar': {
        'model_name': 'jonatasgrosman/wav2vec2-large-xlsr-53-arabic'
    }
}

def load_language_model(language_code):
    if language_code not in language_models:
        raise ValueError(f"Language '{language_code}' is not supported. Please choose from {list(language_models.keys())}.")

    model_name = language_models[language_code]['model_name']
    print(f"Loading ASR model for language '{language_code}': {model_name}")
    try:
        tokenizer = Wav2Vec2Tokenizer.from_pretrained(model_name)
        model = Wav2Vec2ForCTC.from_pretrained(model_name).to('cpu')  # Change to 'cuda' if GPU is available
        language_models[language_code]['tokenizer'] = tokenizer
        language_models[language_code]['model'] = model
        print(f"Successfully loaded model for '{language_code}'.\n")
    except Exception as e:
        print(f"Failed to load model for '{language_code}': {e}\n")
        language_models[language_code]['tokenizer'] = None
        language_models[language_code]['model'] = None

def transcribe_audio(file_path, tokenizer, model, device='cpu'):
    try:
        audio, rate = librosa.load(file_path, sr=16000)
        input_values = tokenizer(audio, return_tensors="pt", padding="longest").input_values.to(device)
        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = tokenizer.decode(predicted_ids[0])
        print('Transcribed Audio File')
        return transcription.lower().strip()
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def transcribe_dataset(dataset_path, language_code, device='cpu'):
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"The specified dataset path '{dataset_path}' does not exist.")
    
    load_language_model(language_code)
    tokenizer = language_models[language_code]['tokenizer']
    model = language_models[language_code]['model']
    
    transcriptions = []
    audio_files = [f for f in os.listdir(dataset_path) if f.lower().endswith('.wav')]
    total_files = len(audio_files)

    print(f"\nTranscribing dataset for language: {language_code}")
    print(f"  Found {total_files} audio files in the dataset.")
    
    for audio_file in tqdm(audio_files, desc="Processing files", unit="file"):
        file_path = os.path.join(dataset_path, audio_file)
        transcription = transcribe_audio(file_path, tokenizer, model, device=device)
        transcriptions.append({
            'file_name': audio_file,
            'transcription': transcription,
            'label': 'Unknown'
        })

    return transcriptions

def save_transcriptions_to_csv(transcriptions, output_csv='transcriptions.csv'):
    transcriptions_df = pd.DataFrame(transcriptions)
    transcriptions_df.to_csv(output_csv, index=False)
    print(f"\nTranscriptions saved to '{output_csv}'.")