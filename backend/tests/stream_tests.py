from backend.speech.recorder_stream import AudioStreamRecorder
from backend.speech.transcriber_stream import StreamingTranscriber
import time

rec = AudioStreamRecorder()
tr = StreamingTranscriber(language="en")

rec.start()
print("🎙️ Listening... Ctrl+C to stop")

try:
    while True:
        chunk = rec.read_chunk()
        tr.add_chunk(chunk)

        text = tr.transcribe()
        if text:
            print("🧠", text)

        time.sleep(0.1)

except KeyboardInterrupt:
    rec.stop()
    print("🛑 Stopped")
