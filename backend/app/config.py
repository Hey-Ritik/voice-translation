"""
Application configuration with environment variable handling.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Whisper STT
    whisper_model_size: str = "base"  # tiny, base, small, medium, large-v2, large-v3
    whisper_device: str = "cpu"  # cpu or cuda
    whisper_compute_type: str = "int8"  # int8, float16, float32
    whisper_chunk_length_s: int = 10  # max segment length for chunked transcribe

    # Translation
    translation_engine: str = "nllb"  # nllb or openai
    nllb_model: str = "facebook/nllb-200-distilled-600M"
    openai_api_key: Optional[str] = None

    # Audio processing
    sample_rate: int = 16000
    chunk_duration_ms: int = 2000  # process every N ms of audio
    min_audio_length_s: float = 0.5  # skip chunks shorter than this

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://*.onrender.com",
        "https://*.vercel.app", # Allow Vercel deployments
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
