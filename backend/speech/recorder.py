import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
from pathlib import Path

SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 5  # seconds

RECORDINGS_DIR = Path("recordings")
RECORDINGS_DIR.mkdir(exist_ok=True)

def record_audio(duration=DURATION, output_path=None):
    print("Recording started...")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32"
    )
    sd.wait()

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = RECORDINGS_DIR / f"recording_{timestamp}.wav"
    else:
        output_path = Path(output_path)

    write(output_path, SAMPLE_RATE, audio)
    print(f"Recording saved to {output_path}")

    return str(output_path)
