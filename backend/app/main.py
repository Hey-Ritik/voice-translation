"""
FastAPI application: REST + WebSocket for real-time speech translation.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.services.language_codes import TARGET_LANGUAGES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown: preload models."""
    from app.services.model_loader import ModelLoader
    try:
        ModelLoader.get_instance().start_loading()
    except Exception as e:
        logger.error(f"Error triggering background model loading: {e}")
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
    """Real-time audio: delegate to handler."""
    await websocket.accept()
    from app.websocket.audio_handler import handle_audio_websocket
    await handle_audio_websocket(websocket)
