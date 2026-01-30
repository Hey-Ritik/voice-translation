"""
WebSocket audio handler: receive audio chunks, run STT + translation, stream results.
"""
import asyncio
import base64
import json
import logging
from typing import Optional

from app.config import get_settings
from app.services.language_codes import whisper_to_display
from app.services.stt_service import get_stt_service
from app.services.translation_service import get_translation_service

logger = logging.getLogger(__name__)


async def process_audio_chunk(
    audio_b64: str,
    target_lang: str,
    sample_rate: int,
) -> dict:
    """
    Process a single audio chunk: decode -> transcribe -> translate.
    Runs in thread pool to avoid blocking the event loop.
    """
    settings = get_settings()
    loop = asyncio.get_running_loop()

    def _run() -> dict:
        try:
            audio_bytes = base64.b64decode(audio_b64)
            if len(audio_bytes) < 500:
                return {"original": "", "translated": "", "detected_lang": None, "error": None}

            # Minimum duration check
            duration_s = len(audio_bytes) / (2 * sample_rate)
            if duration_s < settings.min_audio_length_s:
                return {"original": "", "translated": "", "detected_lang": None, "error": None}

            stt = get_stt_service()
            result = stt.transcribe(audio_bytes, sample_rate=sample_rate, language=None)
            original = (result.text or "").strip()
            if not original:
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
            logger.exception("Chunk processing failed: %s", e)
            return {
                "original": "",
                "translated": "",
                "detected_lang": None,
                "error": str(e),
            }

    return await loop.run_in_executor(None, _run)


async def handle_audio_websocket(websocket, path: Optional[str] = None):
    """
    WebSocket handler: receive JSON messages with base64 audio and target_lang,
    respond with transcription + translation.
    """
    target_lang = "en"
    sample_rate = get_settings().sample_rate
    try:
        await websocket.send_json({
            "type": "ready",
            "message": "Send audio chunks as JSON: { \"audio\": \"<base64>\", \"target_lang\": \"hi\" }",
        })
        async for message in websocket:
            try:
                if isinstance(message, bytes):
                    try:
                        data = json.loads(message.decode("utf-8"))
                    except Exception:
                        await websocket.send_json({"type": "error", "error": "Invalid JSON"})
                        continue
                else:
                    data = message if isinstance(message, dict) else json.loads(message)

                target_lang = data.get("target_lang") or target_lang
                sample_rate = data.get("sample_rate") or sample_rate
                audio_b64 = data.get("audio")
                if not audio_b64:
                    await websocket.send_json({"type": "error", "error": "Missing 'audio' field"})
                    continue

                result = await process_audio_chunk(audio_b64, target_lang, sample_rate)
                result["type"] = "caption"
                await websocket.send_json(result)
            except json.JSONDecodeError as e:
                await websocket.send_json({"type": "error", "error": f"Invalid JSON: {e}"})
            except Exception as e:
                logger.exception("Message handling failed: %s", e)
                await websocket.send_json({"type": "error", "error": str(e)})
    except Exception as e:
        logger.exception("WebSocket handler error: %s", e)
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
