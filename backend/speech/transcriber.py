from faster_whisper import WhisperModel

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

def transcribe_audio(audio_path: str) -> str:
    segments, info = model.transcribe(audio_path)

    text = []
    for segment in segments:
        text.append(segment.text)

    return " ".join(text)
