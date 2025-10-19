# segmentation.py
import os
import shutil
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import subprocess

def process_single_audio_file(file_path, output_folder=r'D:\ISEF Application\dementia_detector\server\server\processed_audio'):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    if not os.path.isfile(file_path):
        print("Invalid file path or the file does not exist.")
        return

    try:
        audio = AudioSegment.from_file(file_path)
    except CouldntDecodeError as e:
        print(f"Error processing {file_path}: {e}")
        print("Attempting to re-encode the file to a universally supported format...")
        reencoded_path = reencode_audio(file_path)
        if reencoded_path:
            try:
                audio = AudioSegment.from_file(reencoded_path)
                print(f"Successfully re-encoded and loaded {reencoded_path}")
            except CouldntDecodeError as e2:
                print(f"Re-encoding failed for {file_path}: {e2}")
                return
        else:
            return

    duration_ms = len(audio)
    twenty_sec_ms = 20 * 1000

    if duration_ms < twenty_sec_ms:
        process_short_audio(audio, os.path.basename(file_path), duration_ms, twenty_sec_ms, output_folder)
    else:
        process_long_audio(audio, os.path.basename(file_path), duration_ms, twenty_sec_ms, output_folder)

    print(f"\nProcessed audio files are available in {output_folder}")

def reencode_audio(file_path):
    base, _ = os.path.splitext(file_path)
    reencoded_path = f"{base}_reencoded.wav"

    command = [
        'ffmpeg',
        '-y',
        '-i', file_path,
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        reencoded_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return reencoded_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg re-encoding failed for {file_path}: {e.stderr.decode(errors='ignore')}")
        return None

def process_short_audio(audio, filename, duration_ms, twenty_sec_ms, output_folder):
    repeats = (twenty_sec_ms // duration_ms) + 1
    new_audio = audio * repeats
    new_audio = new_audio[:twenty_sec_ms]
    output_filename = os.path.splitext(filename)[0] + '.wav'
    output_path = os.path.join(output_folder, output_filename)
    new_audio.export(output_path, format='wav')
    print(f"Processed short audio: {filename} -> {output_filename}")

def process_long_audio(audio, filename, duration_ms, twenty_sec_ms, output_folder):
    num_segments = duration_ms // twenty_sec_ms
    for i in range(int(num_segments)):
        start_ms = i * twenty_sec_ms
        end_ms = start_ms + twenty_sec_ms
        segment = audio[start_ms:end_ms]
        output_filename = f"{os.path.splitext(filename)[0]}_segment{i+1}.wav"
        output_path = os.path.join(output_folder, output_filename)
        segment.export(output_path, format='wav')
        print(f"Processed segment {i+1} of {filename} -> {output_filename}")

    remainder_ms = duration_ms % twenty_sec_ms
    if remainder_ms > 0:
        last_segment = audio[-remainder_ms:]
        repeats = (twenty_sec_ms // remainder_ms) + 1
        last_segment = last_segment * repeats
        last_segment = last_segment[:twenty_sec_ms]
        output_filename = f"{os.path.splitext(filename)[0]}_segment{int(num_segments)+1}.wav"
        output_path = os.path.join(output_folder, output_filename)
        last_segment.export(output_path, format='wav')
        print(f"Processed last segment of {filename} -> {output_filename}")
