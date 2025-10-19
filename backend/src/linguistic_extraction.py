"""
linguistic_extraction.py
Extracts linguistic features from text transcriptions using SpaCy and LFTK.

Supports multilingual processing (40+ languages) using appropriate SpaCy pipelines.
Used for dementia-related language pattern analysis in multilingual datasets.
"""

import os
import pandas as pd
import spacy
import lftk
import logging

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "linguistic_extraction.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ----------------------------------------------------
# Language to SpaCy Model Mapping
# ----------------------------------------------------
SPACY_PIPELINES = {
    "de": "de_core_news_sm", "en": "en_core_web_sm", "es": "es_core_news_sm",
    "fr": "fr_core_news_sm", "it": "it_core_news_sm", "nl": "nl_core_news_sm",
    "pl": "pl_core_news_sm", "pt": "pt_core_news_sm", "ru": "ru_core_news_sm",
    "zh": "zh_core_web_sm", "ja": "ja_core_news_sm", "ko": "ko_core_news_sm",
    # fallback multilingual pipeline for unsupported languages
    "default": "xx_sent_ud_sm"
}

_loaded_pipelines = {}

# ----------------------------------------------------
# SpaCy Pipeline Management
# ----------------------------------------------------
def get_spacy_pipeline(lang_code: str):
    """Load and cache the SpaCy pipeline for a given language."""
    model_name = SPACY_PIPELINES.get(lang_code, SPACY_PIPELINES["default"])

    if lang_code not in _loaded_pipelines:
        try:
            _loaded_pipelines[lang_code] = spacy.load(model_name)
            logging.info(f"Loaded SpaCy model: {model_name} for language {lang_code}")
        except Exception as e:
            logging.error(f"Error loading SpaCy model for {lang_code}: {e}")
            raise RuntimeError(f"Failed to load SpaCy model for {lang_code}: {e}")
    
    return _loaded_pipelines[lang_code]

# ----------------------------------------------------
# Feature Extraction Core
# ----------------------------------------------------
# Filter out problematic LFTK features
_all_features = [
    f for f in lftk.search_features(return_format="list_key")
    if f not in ["bilog_ttr", "bilog_ttr_no_lem"]
]

def extract_linguistic_features(transcription: str, lang_code: str) -> pd.DataFrame:
    """
    Extract linguistic features from a single transcription.
    Returns a DataFrame with one row of feature values.
    """
    if not transcription.strip():
        logging.warning("Empty transcription received for linguistic feature extraction.")
        return pd.DataFrame([{f: float("nan") for f in _all_features}])

    try:
        nlp = get_spacy_pipeline(lang_code)
        doc = nlp(transcription)
        extractor = lftk.Extractor(docs=doc)
        features = extractor.extract(features=_all_features)
        logging.info(f"Extracted linguistic features for language: {lang_code}")
        print("🗣️ Extracted Linguistic Features")
        return pd.DataFrame([features])
    except Exception as e:
        logging.error(f"Error extracting linguistic features: {e}")
        return pd.DataFrame([{f: float('nan') for f in _all_features}])

# ----------------------------------------------------
# Batch CSV Processing
# ----------------------------------------------------
def process_transcriptions_csv(input_csv: str, output_csv: str, lang_code: str):
    """
    Process a CSV file containing transcriptions and save linguistic features to output_csv.
    Expected column: 'transcription'
    """
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    df = pd.read_csv(input_csv)
    if "transcription" not in df.columns:
        raise ValueError("Input CSV must contain a 'transcription' column.")

    nlp = get_spacy_pipeline(lang_code)
    results = []

    for _, row in df.iterrows():
        text = str(row["transcription"]).strip()
        try:
            doc = nlp(text)
            extractor = lftk.Extractor(docs=doc)
            feats = extractor.extract(features=_all_features)
        except Exception as e:
            logging.error(f"Error extracting features for row: {e}")
            feats = {f: float("nan") for f in _all_features}

        feats["label"] = "Unknown"
        if "id" in row:
            feats["id"] = row["id"]
        results.append(feats)

    features_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    features_df.to_csv(output_csv, index=False)
    logging.info(f"Linguistic features saved to {output_csv}")
    print(f"✅ Linguistic features saved to {output_csv}")
    return output_csv
