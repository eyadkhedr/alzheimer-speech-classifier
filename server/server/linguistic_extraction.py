# linguistic_extraction.py
import os
import pandas as pd
import spacy
import lftk

spacy_pipelines = {
    "af": "xx_sent_ud_sm",  # Afrikaans
    "ar": "xx_sent_ud_sm",  # Arabic
    "bg": "xx_sent_ud_sm",  # Bulgarian
    "bn": "xx_sent_ud_sm",  # Bengali
    "ca": "xx_sent_ud_sm",  # Catalan
    "cs": "xx_sent_ud_sm",  # Czech
    "da": "xx_sent_ud_sm",  # Danish
    "de": "de_core_news_sm", # German
    "el": "xx_sent_ud_sm",  # Greek
    "en": "en_core_web_sm",  # English
    "es": "es_core_news_sm", # Spanish
    "et": "xx_sent_ud_sm",  # Estonian
    "fa": "xx_sent_ud_sm",  # Persian
    "fi": "xx_sent_ud_sm",  # Finnish
    "fr": "fr_core_news_sm", # French
    "gu": "xx_sent_ud_sm",  # Gujarati
    "he": "xx_sent_ud_sm",  # Hebrew
    "hi": "xx_sent_ud_sm",  # Hindi
    "hr": "xx_sent_ud_sm",  # Croatian
    "hu": "xx_sent_ud_sm",  # Hungarian
    "id": "xx_sent_ud_sm",  # Indonesian
    "it": "it_core_news_sm", # Italian
    "ja": "ja_core_news_sm", # Japanese
    "kn": "xx_sent_ud_sm",  # Kannada
    "ko": "ko_core_news_sm", # Korean
    "lt": "xx_sent_ud_sm",  # Lithuanian
    "lv": "xx_sent_ud_sm",  # Latvian
    "ml": "xx_sent_ud_sm",  # Malayalam
    "mr": "xx_sent_ud_sm",  # Marathi
    "nb": "xx_sent_ud_sm",  # Norwegian Bokmål
    "nl": "nl_core_news_sm", # Dutch
    "pl": "pl_core_news_sm", # Polish
    "pt": "pt_core_news_sm", # Portuguese
    "ro": "xx_sent_ud_sm",  # Romanian
    "ru": "ru_core_news_sm", # Russian
    "si": "xx_sent_ud_sm",  # Sinhala
    "sk": "xx_sent_ud_sm",  # Slovak
    "sl": "xx_sent_ud_sm",  # Slovenian
    "sq": "xx_sent_ud_sm",  # Albanian
    "sv": "xx_sent_ud_sm",  # Swedish
    "ta": "xx_sent_ud_sm",  # Tamil
    "te": "xx_sent_ud_sm",  # Telugu
    "th": "xx_sent_ud_sm",  # Thai
    "tl": "xx_sent_ud_sm",  # Tagalog
    "tr": "xx_sent_ud_sm",  # Turkish
    "uk": "xx_sent_ud_sm",  # Ukrainian
    "ur": "xx_sent_ud_sm",  # Urdu
    "vi": "xx_sent_ud_sm",  # Vietnamese
    "zh": "zh_core_web_sm"   # Chinese (Mandarin)
}

loaded_pipelines = {}

def get_spacy_pipeline(lang_code):
    if lang_code not in spacy_pipelines:
        raise ValueError(f"Unsupported language: {lang_code}")
    if lang_code not in loaded_pipelines:
        loaded_pipelines[lang_code] = spacy.load(spacy_pipelines[lang_code])
    return loaded_pipelines[lang_code]

all_features = lftk.search_features(return_format="list_key")
problematic_features = ["bilog_ttr", "bilog_ttr_no_lem"]
all_features = [f for f in all_features if f not in problematic_features]

def extract_linguistic_features(transcription, lang_code):
    nlp = get_spacy_pipeline(lang_code)
    doc = nlp(transcription)
    extractor = lftk.Extractor(docs=doc)
    try:
        feats = extractor.extract(features=all_features)
    except ValueError:
        feats = {f: float('nan') for f in all_features}
    print('Extracted Linguistic Features')
    print('---------------------------------')
    return feats

def process_csv(input_file, output_file, lang_code):
    df = pd.read_csv(input_file)
    if 'transcription' not in df.columns:
        raise ValueError("No 'transcription' column found in the input CSV.")
    df['transcription'] = df['transcription'].fillna("").astype(str)
    
    nlp = get_spacy_pipeline(lang_code)
    feature_rows = []
    
    for _, row in df.iterrows():
        text = row['transcription']
        doc = nlp(text)
        extractor = lftk.Extractor(docs=doc)
        try:
            feats = extractor.extract(features=all_features)
        except ValueError:
            feats = {f: float('nan') for f in all_features}
        
        if 'id' in row:
            feats['id'] = row['id']
        
        feature_rows.append(feats)
    
    features_df = pd.DataFrame(feature_rows)
    features_df['label'] = "Unknown"
    features_df.to_csv(output_file, index=False)
    print(f"Features saved to {output_file}")
