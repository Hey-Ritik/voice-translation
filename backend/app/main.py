"""
FastAPI application: REST + WebSocket for real-time speech translation.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.services.language_codes import TARGET_LANGUAGES
from app.websocket.audio_handler import process_audio_chunk

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown: optional preload of models can go here."""
    yield
    # Shutdown cleanup if needed


app = FastAPI(
    title="Voice Translation API",
    description="Real-time speech-to-text and translation over WebSocket",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "voice-translation",
        "docs": "/docs",
        "websocket": "/ws/audio",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/languages")
async def languages():
    """Return list of target languages for the dropdown."""
    return {"languages": [{"code": c, "name": n} for c, n in TARGET_LANGUAGES]}


@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):
    """Real-time audio: client sends JSON { audio (base64), target_lang, sample_rate? }."""
    await websocket.accept()
    target_lang = "en"
    sample_rate = settings.sample_rate
    try:
        await websocket.send_json({
            "type": "ready",
            "message": "Send audio chunks as JSON: { \"audio\": \"<base64>\", \"target_lang\": \"hi\" }",
        })
        while True:
            try:
                data = await websocket.receive_json()
            except Exception as e:
                await websocket.send_json({"type": "error", "error": str(e)})
                continue

            target_lang = data.get("target_lang") or target_lang
            sample_rate = data.get("sample_rate") or sample_rate
            audio_b64 = data.get("audio")
            if not audio_b64:
                await websocket.send_json({"type": "error", "error": "Missing 'audio' field"})
                continue

            result = await process_audio_chunk(audio_b64, target_lang, sample_rate)
            result["type"] = "caption"
            await websocket.send_json(result)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.exception("WebSocket error: %s", e)
        try:
            await websocket.send_json({"type": "error", "error": str(e)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
