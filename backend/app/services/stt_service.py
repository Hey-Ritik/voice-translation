"""
Speech-to-Text service using faster-whisper.
Processes audio chunks with automatic language detection.
"""
import logging
from dataclasses import dataclass
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Result of a single transcription."""

    text: str
    detected_language: Optional[str]
    language_probability: Optional[float]


class STTService:
    """Whisper-based speech-to-text with language detection."""

    _instance: Optional["STTService"] = None

    def __init__(self) -> None:
        self._model = None
        self._settings = get_settings()

    def _load_model(self) -> None:
        if self._model is not None:
            return
        
        from app.services.model_loader import ModelLoader
        self._model = ModelLoader.get_instance().whisper_model


    def transcribe(
        self,
        audio_bytes: bytes,
        sample_rate: int = 16000,
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio bytes. Auto-detect language if language is None.
        """
        self._load_model()
        if not audio_bytes or len(audio_bytes) < 1000:
            return TranscriptionResult(
                text="",
                detected_language=language,
                language_probability=None,
            )

        import numpy as np

        # Convert bytes to float32 mono
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        audio_float = audio_array.astype(np.float32) / 32768.0

        try:
            segments, info = self._model.transcribe(
                audio_float,
                language=language,
                task="transcribe",
                beam_size=1,
                best_of=1,
                vad_filter=False,
                # vad_parameters=dict(min_silence_duration_ms=300, speech_pad_ms=100, threshold=0.5),
                condition_on_previous_text=False,
            )
            detected_lang = info.language
            lang_prob = info.language_probability
            text_parts = [s.text.strip() for s in segments if s.text.strip()]
            text = " ".join(text_parts).strip()
            return TranscriptionResult(
                text=text,
                detected_language=detected_lang,
                language_probability=lang_prob,
            )
        except Exception as e:
            logger.exception("Transcription failed: %s", e)
            return TranscriptionResult(
                text="",
                detected_language=language,
                language_probability=None,
            )


def get_stt_service() -> STTService:
    """Singleton STT service."""
    if STTService._instance is None:
        STTService._instance = STTService()
    return STTService._instance  # type: ignore
