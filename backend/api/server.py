"""
server.py
Flask backend for the Universal Dementia Detector mobile app.

- Handles audio file uploads and language selection.
- Connects to the ML inference pipeline (prediction.py) for classification.
- Provides endpoints for checking upload status and canceling processing.

Endpoints:
  POST /upload               → Uploads audio file for analysis
  POST /selected-language    → Sets current language code
  GET  /get_classification   → Returns predicted dementia classification
  GET  /upload-status        → Checks upload completion
  POST /cancel               → Cancels active process and clears directories
"""

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import shutil
import signal
from datetime import datetime
from backend.src.prediction_script import predict_final_classification
# =========================
# Flask Configuration
# =========================
app = Flask(__name__)

# Define project directories (relative paths)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed_audio")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Global runtime variables
UPLOAD_STATUS = {"complete": False}
selected_language_code = None
current_process_pid = None


# =========================
# Utility Functions
# =========================
def reset_upload_status():
    """Resets upload completion flag."""
    UPLOAD_STATUS["complete"] = False


def clear_processed_audio():
    """Clears processed audio folder."""
    if os.path.exists(PROCESSED_FOLDER):
        shutil.rmtree(PROCESSED_FOLDER)
        os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# =========================
# Routes
# =========================
@app.route('/selected-language', methods=['POST'])
def selected_language():
    global selected_language_code
    try:
        data = request.get_json()
        if not data or 'languageCode' not in data:
            return jsonify({"status": "error", "message": "Missing 'languageCode' in request body"}), 400

        selected_language_code = data['languageCode']
        reset_upload_status()

        return jsonify({
            "status": "success",
            "message": f"Language '{selected_language_code}' set successfully"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/upload', methods=['POST'])
def upload_audio():
    try:
        global UPLOAD_STATUS

        if selected_language_code is None:
            return jsonify({"status": "error", "message": "Language code not set"}), 400

        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part in request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400

        # Use secure filename and timestamp
        filename = secure_filename(f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        UPLOAD_STATUS["complete"] = True

        return jsonify({"status": "success", "message": "File uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/upload-status', methods=['GET'])
def upload_status():
    return jsonify({"complete": UPLOAD_STATUS.get("complete", False)}), 200


@app.route('/get_classification', methods=['GET'])
def get_classification():
    try:
        if selected_language_code is None:
            return jsonify({"status": "error", "message": "Language not set"}), 400

        if not UPLOAD_STATUS.get("complete", False):
            return jsonify({"status": "error", "message": "No file uploaded yet"}), 400

        # Get latest uploaded file
        uploaded_files = sorted(
            [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.wav')],
            key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)),
            reverse=True
        )
        if not uploaded_files:
            return jsonify({"status": "error", "message": "No audio file found"}), 404

        latest_file = os.path.join(UPLOAD_FOLDER, uploaded_files[0])

        # Run prediction
        classification_label = predict_final_classification(latest_file, selected_language_code)

        reset_upload_status()  # reset after prediction
        return jsonify({"status": "success", "classification": classification_label}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/cancel', methods=['POST'])
def cancel_process():
    global current_process_pid
    try:
        if current_process_pid:
            os.kill(current_process_pid, signal.SIGTERM)
            current_process_pid = None

        clear_processed_audio()
        reset_upload_status()

        return jsonify({"status": "success", "message": "Process canceled and cleaned up"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/test-connection', methods=['POST'])
def test_connection():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part in request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400

        test_path = os.path.join(UPLOAD_FOLDER, "test_connection.wav")
        file.save(test_path)
        return jsonify({"status": "success", "message": "Test connection successful"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# =========================
# Entry Point
# =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
