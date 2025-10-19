from flask import Flask, request, jsonify
import os
import shutil
import signal
from prediction_script import predict_final_classification  # Import the prediction logic from the script

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = r"D:\ISEF Application\dementia_detector\server\server\uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PROCESSED_FOLDER = r"D:\ISEF Application\dementia_detector\server\server\processed_audio"
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Directory to store processed audio files

# Variable to store selected language
selected_language_code = None

# Variable to track the running process ID
current_process_pid = None

@app.route('/selected-language', methods=['POST'])
def selected_language():
    global selected_language_code
    try:
        data = request.get_json()
        if not data or 'languageCode' not in data:
            return jsonify({"status": "error", "message": "Missing 'languageCode' in request body"}), 400
        
        selected_language_code = data['languageCode']
        return jsonify({"status": "success", "message": f"Language '{selected_language_code}' saved successfully"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get_classification', methods=['GET'])
def get_classification():
    global selected_language_code, UPLOAD_STATUS
    try:
        if selected_language_code is None:
            return jsonify({
                "status": "error",
                "message": "Language code is not set. Use /selected-language to set it."
            }), 400

        # Check if the upload is complete
        if not UPLOAD_STATUS.get("complete", False):
            return jsonify({
                "status": "error",
                "message": "File upload not complete. Please try again later."
            }), 400

        # Perform classification
        file_path = os.path.join(UPLOAD_FOLDER, 'recording.wav')
        classification_label = predict_final_classification(file_path, selected_language_code)
        return jsonify({"status": "success", "classification": classification_label}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


UPLOAD_STATUS = {"complete": False}  # Global flag for upload status

@app.route('/upload', methods=['POST'])
def upload_audio():
    global selected_language_code, UPLOAD_STATUS
    try:
        if selected_language_code is None:
            return jsonify({"status": "error", "message": "Language code not set"}), 400

        # Check if a file is included in the request
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part in the request"}), 400
        
        file = request.files['file']
        
        # Check if the file has a valid name
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
        
        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, 'recording.wav')
        file.save(file_path)
        
        # Update the upload status
        UPLOAD_STATUS["complete"] = True
        
        return jsonify({"status": "success", "message": "File uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/upload-status', methods=['GET'])
def upload_status():
    try:
        return jsonify({"complete": UPLOAD_STATUS.get("complete", False)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/cancel', methods=['POST'])
def cancel_process():
    global current_process_pid
    try:
        # Stop the running process (if any)
        if current_process_pid:
            os.kill(current_process_pid, signal.SIGTERM)
            current_process_pid = None

        # Delete the processed_audio directory
        if os.path.exists(PROCESSED_FOLDER):
            shutil.rmtree(PROCESSED_FOLDER)

        return jsonify({"status": "success", "message": "Process canceled and directory deleted"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/test-connection', methods=['POST'])
def test_connection():
    try:
        # Check if a file is included in the request
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part in the request"}), 400
        
        file = request.files['file']
        
        # Check if the file has a valid name
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
        
        # Save the test file to a temporary location
        test_file_path = os.path.join(UPLOAD_FOLDER, 'test_connection.wav')
        file.save(test_file_path)
        
        return jsonify({"status": "success", "message": "Test connection successful"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
