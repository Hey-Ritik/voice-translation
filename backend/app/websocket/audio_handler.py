"""
WebSocket audio handler: receive audio chunks, buffer them until silence, run STT + translation.
Optimized for "Sentence-level" translation to improve accuracy and reduce load.
"""
import asyncio
import base64
import json
import logging
import time
import numpy as np
from typing import Optional
from fastapi import WebSocketDisconnect

from app.config import get_settings
from app.services.language_codes import whisper_to_display
from app.services.stt_service import get_stt_service
from app.services.translation_service import get_translation_service

logger = logging.getLogger(__name__)

# VAD / Buffering Constants
SILENCE_THRESHOLD = 0.01      # <--- RMS amplitude threshold for silence. Tune this!
SILENCE_DURATION_MS = 600     # <--- How much silence triggers a "sentence end"
MAX_BUFFER_DURATION_S = 6.0   # <--- Force translate after this many seconds
MIN_BUFFER_DURATION_S = 1.0   # <--- Don't translate tiny snippets (noise)

async def process_audio_buffer(
    audio_bytes: bytes,
    target_lang: str,
    sample_rate: int,
) -> dict:
    """
    Process a gathered audio buffer: transcribe -> translate.
    """
    settings = get_settings()
    loop = asyncio.get_running_loop()

    def _run() -> dict:
        try:
            stt = get_stt_service()
            result = stt.transcribe(audio_bytes, sample_rate=sample_rate, language=None)
            original = (result.text or "").strip()
            
            # If Whisper returns empty or very short garbage
            if not original or len(original) < 2:
                return {
                    "original": "",
                    "translated": "",
                    "detected_lang": result.detected_language,
                    "error": None,
                }

            detected = result.detected_language or "en"
            trans = get_translation_service()
            use_openai = settings.translation_engine == "openai" and settings.openai_api_key
            translated = trans.translate(original, detected, target_lang, use_openai=use_openai)

            return {
                "original": original,
                "translated": translated or original,
                "detected_lang": result.detected_language,
                "detected_lang_display": whisper_to_display(result.detected_language),
                "error": None,
            }
        except Exception as e:
            logger.exception("Buffer processing failed: %s", e)
            return {
                "original": "",
                "translated": "",
                "detected_lang": None,
                "error": str(e),
            }

    return await loop.run_in_executor(None, _run)


def is_silence(audio_chunk: bytes, threshold: float) -> bool:
    """Simple RMS-based silence detection."""
    try:
        data = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32)
        if len(data) == 0:
            return True
        # Normalize 16-bit to -1..1
        data = data / 32768.0
        rms = np.sqrt(np.mean(data**2))
        return rms < threshold
    except Exception:
        return False


async def handle_audio_websocket(websocket, path: Optional[str] = None):
    """
    WebSocket handler:
    1. Buffers audio chunks.
    2. Checks for silence.
    3. Triggers translation.
    """
    target_lang = "en"
    settings = get_settings()
    sample_rate = settings.sample_rate
    
    # Session State
    audio_buffer = bytearray()
    silence_start_time = None
    last_process_time = time.time()
    
    try:
        await websocket.send_json({
            "type": "ready",
            "message": "Connected. Send audio chunks.",
            "config": {
                "sample_rate": sample_rate, 
                "chunk_size_ms": 250
            }
        })
        
        while True:
            try:
                # 1. Receive & Parse Message
                try:
                    data = await websocket.receive_json()
                except WebSocketDisconnect:
                    break
                except Exception:
                    # If receive_json fails (e.g. text/bytes mismatch), try text
                    # or just stop. simpler to rely on disconnect.
                    break
                
                # data is already a dict from receive_json()
                
                target_lang = data.get("target_lang") or target_lang
                audio_b64 = data.get("audio")
                
                if not audio_b64:
                    continue
                
                # 2. Decode & Buffer
                chunk_bytes = base64.b64decode(audio_b64)
                audio_buffer.extend(chunk_bytes)
                
                # 3. VAD Logic
                # Calculate duration of current buffer
                # 16-bit mono = 2 bytes per sample
                current_duration_s = len(audio_buffer) / (2 * sample_rate)
                
                chunk_is_silent = is_silence(chunk_bytes, SILENCE_THRESHOLD)
                
                now = time.time()
                should_process = False
                
                if chunk_is_silent:
                    if silence_start_time is None:
                        silence_start_time = now
                    elif (now - silence_start_time) * 1000 >= SILENCE_DURATION_MS:
                        # Enough silence detected -> End of sentence?
                        if current_duration_s >= MIN_BUFFER_DURATION_S:
                            should_process = True
                else:
                    silence_start_time = None
                    
                # Force process if buffer too long
                if current_duration_s >= MAX_BUFFER_DURATION_S:
                    should_process = True
                
                # 4. Process if needed
                if should_process:
                    logger.info(f"Processing buffer: {current_duration_s:.2f}s")
                    
                    # Offload to thread to not block WS ping/pong
                    process_task = asyncio.create_task(
                        process_audio_buffer(bytes(audio_buffer), target_lang, sample_rate)
                    )
                    
                    # We await it here for simplicity, but in a real streaming system 
                    # we might want to just fire & forget or use a queue. 
                    # For now, awaiting ensures we don't overlap two translations of same context logic 
                    # (though we cleared buffer, so overlap isn't an issue execution-wise, but ordering is).
                    # 'await' causes a small pause in receiving, which is actually fine 
                    # because we act on silence.
                    result = await process_task
                    
                    if result["original"]:
                        result["type"] = "caption"
                        await websocket.send_json(result)
                    
                    # Reset
                    audio_buffer = bytearray()
                    silence_start_time = None
                    last_process_time = now
                    
            except Exception as e:
                logger.error(f"WS Loop Error: {e}")
                
    except Exception as e:
        logger.exception("WebSocket handler critical error: %s", e)
    finally:
        try:
            await websocket.close()
        except:
            pass
