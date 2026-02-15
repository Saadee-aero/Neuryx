from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
from backend.speech.audio_manager import AudioManager
from backend.speech.transcriber import transcribe_audio
# from backend.speech.transcriber_stream import StreamingTranscriber # REMOVED
from backend.routers import models
from backend.core.logger import get_logger
from backend.core.system_monitor import get_memory_usage_mb
import numpy as np
import asyncio
import time

logger = get_logger("backend.main")

app = FastAPI(title="NEURYX")
app.include_router(models.router)

# Serve built frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audio_manager = AudioManager()

@app.on_event("startup")
async def startup_event():
    logger.info("Neuryx Backend Starting...")
    logger.info(f"Initial Memory Usage: {get_memory_usage_mb():.2f} MB")
    # Pre-load model so first connection is fast
    from backend.speech.model_loader import ModelLoader
    ModelLoader.get_model("small")
    logger.info(f"Model pre-loaded. Memory: {get_memory_usage_mb():.2f} MB")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Neuryx Backend Shutting Down...")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.post("/record/start")
def start_recording():
    """Start recording on the server's default microphone."""
    try:
        logger.info("Starting batch recording...")
        return audio_manager.start_recording()
    except Exception as e:
        logger.error(f"Failed to start recording: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/record/stop")
def stop_recording():
    """Stop recording, save file, and transcribe."""
    try:
        logger.info("Stopping batch recording...")
        result = audio_manager.stop_recording()
        if result.get("status") == "stopped":
            # Transcribe the saved file
            logger.info(f"Transcribing file: {result['file']}")
            transcript = transcribe_audio(result["file"])
            logger.info("Batch transcription complete")
            return {
                "status": "success", 
                "file": result["file"], 
                "transcript": transcript
            }
        return result
    except Exception as e:
        logger.error(f"Failed to stop/transcribe: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/transcribe")
async def transcribe_file(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Batch transcription endpoint.
    Accepts an audio file, saves it, and runs full-accuracy transcription.
    """
    try:
        # 1. Save File
        upload_dir = os.path.join(os.path.dirname(__file__), "recordings")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create unique filename
        filename = f"{int(time.time())}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        logger.info(f"Received file for transcription: {filename} | Lang: {language}")
        
        with open(file_path, "wb") as buffer:
            # Write in chunks to handle large files
            while content := await file.read(1024 * 1024): # 1MB chunks
                buffer.write(content)
                
        # 2. Load Model
        from backend.speech.model_loader import ModelLoader
        # Use 'small' model by default
        model = ModelLoader.get_model("small")
        
        # 3. Transcribe (Accuracy Profile)
        # BATCH MODE SETTINGS
        # beam_size=5, best_of=3, temperature=0.0
        start_time = time.time()
        
        segments, info = model.transcribe(
            file_path,
            language=None if language == "auto" else language,
            beam_size=5,
            best_of=3,
            temperature=0.0,
            condition_on_previous_text=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # 4. Format Response
        result_segments = []
        full_text_parts = []
        
        for seg in segments:
            text = seg.text.strip()
            full_text_parts.append(text)
            result_segments.append({
                "text": text,
                "start": seg.start,
                "end": seg.end
            })
            
        full_text = " ".join(full_text_parts)
        duration = time.time() - start_time
        
        logger.info(f"Transcription complete in {duration:.2f}s")
        
        return JSONResponse({
            "status": "success",
            "language": info.language,
            "duration": info.duration,
            "processing_time": duration,
            "full_text": full_text,
            "segments": result_segments
        })

    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Mount static assets AFTER all API/WS routes (so routes take priority)
if os.path.isdir(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="static-assets")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="static-root")

