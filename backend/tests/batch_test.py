import sys
import os
import time
import numpy as np
import psutil
from scipy.io.wavfile import write

# Add project root to path
sys.path.append(os.getcwd())

from backend.speech.model_loader import ModelLoader
from backend.core.system_monitor import get_memory_usage_mb

def run_batch_test():
    print("=== Neuryx Batch Architecture Test ===")
    
    # 1. Generate Dummy Audio
    print("Generating 10s dummy audio (16kHz, float32)...")
    sample_rate = 16000
    duration = 10
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    
    filename = "batch_test_audio.wav"
    # Write as 16-bit PCM for compatibility with standard tools, or float32 if supported
    # faster-whisper supports both. Let's use int16 to match standard WAV.
    # But backend supports float32. Let's write float32 to test that path.
    write(filename, sample_rate, audio_data)
    print(f"Saved: {filename}")
    
    try:
        # 2. Load Model
        print("\nLoading Model ('small')...")
        start_load = time.time()
        model = ModelLoader.get_model("small")
        load_time = time.time() - start_load
        print(f"Model Loaded in {load_time:.2f}s | Mem: {get_memory_usage_mb():.2f} MB")
        
        # 3. Transcribe (ACCURACY_PROFILE)
        print("\nTranscribing (Accuracy Profile)...")
        print("Params: beam_size=5, best_of=3, temp=0.0, condition=True")
        
        start_transcribe = time.time()
        segments, info = model.transcribe(
            filename,
            language="en",
            beam_size=5,
            best_of=3,
            temperature=0.0,
            condition_on_previous_text=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Consume generator
        text = " ".join([seg.text for seg in segments])
        
        transcribe_time = time.time() - start_transcribe
        print(f"Transcription Complete in {transcribe_time:.2f}s")
        print(f"Detected Duration: {info.duration:.2f}s")
        print(f"Text Length: {len(text)} chars")
        
        print("\n=== Result ===")
        print(f"Real-time Factor: {transcribe_time / info.duration:.2f}x (Lower is faster)")
        print("Batch Architecture Verified ✅")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"\nCleaned up {filename}")

if __name__ == "__main__":
    run_batch_test()
