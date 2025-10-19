"""
segmentation.py
----------------
Splits an input audio file into 20-second segments (or pads shorter clips).
Handles re-encoding using FFmpeg when format compatibility issues arise.
"""

import os
import shutil
import logging
import subprocess
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


# ----------------------------------------------------
# Configuration
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(BASE_DIR, "..")
PROCESSED_DIR = os.path.join(ROOT_DIR, "processed_audio")
LOG_DIR = os.path.join(ROOT_DIR, "logs")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "segmentation.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# ----------------------------------------------------
# Core Function
# ----------------------------------------------------
def process_single_audio_file(file_path: str, output_folder: str = PROCESSED_DIR):
    """
    Splits the given audio file into 20-second segments.
    Pads short files to reach 20 seconds.
    Automatically handles re-encoding with FFmpeg if Pydub can't decode the file.
    """
    if not os.path.isfile(file_path):
        logging.error(f"Invalid file path: {file_path}")
        print("❌ Invalid file path or file does not exist.")
        return

    # Clean output folder
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    try:
        audio = AudioSegment.from_file(file_path)
    except CouldntDecodeError as e:
        logging.warning(f"Decode error for {file_path}: {e}")
        print(f"⚠️ Error decoding {file_path}, attempting to re-encode...")
        reencoded_path = reencode_audio(file_path)
        if reencoded_path:
            try:
                audio = AudioSegment.from_file(reencoded_path)
                logging.info(f"Successfully re-encoded {reencoded_path}")
            except CouldntDecodeError as e2:
                logging.error(f"Re-encoding failed for {file_path}: {e2}")
                print("❌ Failed to re-encode audio.")
                return
        else:
            return

    duration_ms = len(audio)
    twenty_sec_ms = 20 * 1000

    if duration_ms < twenty_sec_ms:
        process_short_audio(audio, os.path.basename(file_path), duration_ms, twenty_sec_ms, output_folder)
    else:
        process_long_audio(audio, os.path.basename(file_path), duration_ms, twenty_sec_ms, output_folder)

    print(f"✅ Processed audio files are saved in: {output_folder}")
    logging.info(f"Audio segmentation completed for {file_path}")


# ----------------------------------------------------
# Helper: Re-encode with FFmpeg
# ----------------------------------------------------
def reencode_audio(file_path: str):
    """Re-encode audio to WAV (PCM 16-bit, 16kHz) for universal compatibility."""
    base, _ = os.path.splitext(file_path)
    reencoded_path = f"{base}_reencoded.wav"
    command = [
        "ffmpeg", "-y",
        "-i", file_path,
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        reencoded_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return reencoded_path
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg re-encoding failed: {e.stderr.decode(errors='ignore')}")
        print("❌ FFmpeg re-encoding failed.")
        return None


# ----------------------------------------------------
# Helper: Handle Short Audio
# ----------------------------------------------------
def process_short_audio(audio, filename, duration_ms, target_ms, output_folder):
    """Pads short audio by looping it until it reaches 20 seconds."""
    repeats = (target_ms // duration_ms) + 1
    new_audio = (audio * repeats)[:target_ms]
    output_filename = os.path.splitext(filename)[0] + ".wav"
    output_path = os.path.join(output_folder, output_filename)
    new_audio.export(output_path, format="wav")
    logging.info(f"Padded short audio: {filename} → {output_filename}")
    print(f"🟢 Processed short audio: {filename} → {output_filename}")


# ----------------------------------------------------
# Helper: Handle Long Audio
# ----------------------------------------------------
def process_long_audio(audio, filename, duration_ms, segment_ms, output_folder):
    """Splits long audio into 20-second segments, padding the last one if needed."""
    num_segments = duration_ms // segment_ms

    for i in range(int(num_segments)):
        start_ms = i * segment_ms
        end_ms = start_ms + segment_ms
        segment = audio[start_ms:end_ms]
        output_filename = f"{os.path.splitext(filename)[0]}_segment{i+1}.wav"
        output_path = os.path.join(output_folder, output_filename)
        segment.export(output_path, format="wav")
        logging.info(f"Segment {i+1} exported: {output_filename}")

    remainder_ms = duration_ms % segment_ms
    if remainder_ms > 0:
        last_segment = audio[-remainder_ms:]
        repeats = (segment_ms // remainder_ms) + 1
        last_segment = (last_segment * repeats)[:segment_ms]
        output_filename = f"{os.path.splitext(filename)[0]}_segment{int(num_segments)+1}.wav"
        output_path = os.path.join(output_folder, output_filename)
        last_segment.export(output_path, format="wav")
        logging.info(f"Last segment padded: {output_filename}")
        print(f"🟢 Processed final padded segment: {output_filename}")
