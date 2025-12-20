from backend.speech.recorder import record_audio
from backend.speech.transcriber import transcribe_audio
from datetime import datetime
import os

def record_and_transcribe(duration=5):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    audio_path = f"recordings/recording_{timestamp}.wav"
    text_path  = f"transcripts/transcript_{timestamp}.txt"

    print("[1/3] Recording audio...")
    record_audio(duration, output_path=audio_path)

    print("[2/3] Transcribing...")
    text = transcribe_audio(audio_path)

    print("[3/3] Saving transcript...")
    os.makedirs("transcripts", exist_ok=True)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)

    return {
        "audio": audio_path,
        "transcript": text_path,
        "text": text
    }
