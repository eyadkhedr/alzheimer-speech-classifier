# 🧠 Universal Dementia Detector

A **language-independent AI system** that detects early Alzheimer’s from short speech samples.  
It combines **acoustic** (Librosa, OpenSMILE) and **linguistic** (LFTK, SpaCy) features to classify speech as *Healthy Control (HC)* or *Alzheimer’s Disease (AD)*.

- **F1-score:** 84.77% (13.37% improvement over multilingual baselines)  
- **Languages:** English, German, Mandarin (scalable to others)  
- **Tools:** Python, scikit-learn, XGBoost, Whisper, Flutter, Firebase, Flask

---

## 📂 Project Structure
```

alzheimer-speech-classifier/
├── backend/          # AI model & Flask API
├── mobile_app/       # Flutter application
├── training/         # Model training scripts & notebooks
├── sample_data/      # Example data for testing
└── requirements.txt  # Python dependencies

````

---

## 🚀 Quick Start
```bash
git clone https://github.com/eyadkhedr/alzheimer-speech-classifier.git
cd alzheimer-speech-classifier
pip install -r requirements.txt
cd backend
python -m backend.api.server
````

Then open `mobile_app/` in Flutter and update the server URL (use ngrok if needed).

---

## 🧩 Model Summary

* **Features:** 6,000+ acoustic + linguistic features
* **Classifier:** Random Forest
* **Inference:** Flask backend with auto-cleaning after prediction

---

## ⚙️ Tech Stack

**Backend:** Python, Flask, scikit-learn
**App:** Flutter, Dart, Firebase
**Feature Extraction:** Librosa, OpenSMILE, LFTK, Whisper

---

## ⚠️ Ethics & Privacy

* No real patient data is included.
* Uploaded recordings are deleted after analysis.
* The model is for **research and educational** use, not medical diagnosis.

---

## 👤 Author

**Eyad Khedr** — Obour STEM School, Egypt
Email: [eyada0103@gmail.com](mailto:eyada0103@gmail.com)
