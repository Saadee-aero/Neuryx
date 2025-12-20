import sounddevice as sd
import numpy as np
import queue
import threading

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"
CHUNK_DURATION = 2.0  # seconds
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)


class AudioStreamRecorder:
    def __init__(self):
        self.q = queue.Queue()
        self.stream = None
        self.running = False

    def _callback(self, indata, frames, time, status):
        if status:
            print("Stream status:", status)

        # copy to avoid memory overwrite
        self.q.put(indata.copy())

    def start(self):
        if self.running:
            return

        self.running = True
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._callback,
            blocksize=CHUNK_SAMPLES,
        )
        self.stream.start()
        print("🎙️ Streaming started")

    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("🛑 Streaming stopped")

    def read_chunk(self):
        """
        Blocking read — returns one chunk (numpy array)
        """
        return self.q.get()
