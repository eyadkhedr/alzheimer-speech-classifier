# ⚙️ Backend (AI Inference Engine)

This directory contains the backend for the Universal Dementia Detector.  
It handles **audio uploads**, **feature extraction**, and **AI prediction** using a trained Random Forest model.

---

## 📂 Structure
````

backend/
├── api/
│   ├── server.py        # Flask REST API
│   └── prediction.py    # Model loading & response formatting
├── src/
│   ├── acoustic_extraction.py
│   ├── linguistic_extraction.py
│   ├── segmentation.py
│   ├── transcription.py
│   └── prediction_script.py
├── models/              # random_forest_model.joblib, scaler.joblib
├── uploads/             # Temporary user uploads
└── processed_audio/     # Segmented clips during prediction

````

---

## 🧠 How it Works
1. **Upload:** User audio is uploaded through the Flutter app.  
2. **Segmentation:** The file is split into 20s segments.  
3. **Transcription:** Wav2Vec2 transcribes each segment.  
4. **Feature Extraction:** Acoustic + linguistic features generated.  
5. **Prediction:** Random Forest outputs HC / AD.  
6. **Cleanup:** Temporary files deleted after analysis.

---

## ▶️ Run
```bash
cd backend
python -m backend.api.server
````

Runs a Flask server at `http://0.0.0.0:8000`.

---

## 🧩 Notes

* Model files (`.joblib`) must exist in `backend/models/`.
* Compatible with ngrok for external mobile connections.
* `.gitignore` ensures no sensitive or build files are uploaded.
