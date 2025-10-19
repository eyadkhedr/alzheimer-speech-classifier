# 📱 Mobile App (Flutter Client)

The **Universal Dementia Detector** mobile app records a short voice sample, sends it to the backend, and displays the dementia prediction.

---

## 🌍 Features
- Record and upload voice samples  
- Choose your language  
- Receive AI-based dementia prediction  
- Simple, multilingual UI (40+ languages supported)

---

## 📂 Structure
````

mobile_app/
├── lib/
│   ├── l10n/               # Language localization (.arb files)
│   ├── screens/            # App screens
│   │   ├── recording_page.dart
│   │   ├── analysis_page.dart
│   │   ├── result_page.dart
│   ├── main.dart           # Entry point
│   └── theme.dart          # Theme settings
└── pubspec.yaml

````

---

## ▶️ Run the App
1. Open `mobile_app/` in VS Code or Android Studio.  
2. Update API URL in `api_service.dart` with your Flask endpoint.  
3. Run:
```bash
flutter pub get
flutter run
````

---

## ⚠️ Note

* `lib/l10n/build/` is **auto-generated** — ignored in `.gitignore`.
* `.arb` files define all UI translations.
* The app is for **research & educational purposes only**.
