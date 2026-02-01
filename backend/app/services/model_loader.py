import logging
import threading
from typing import Optional, Any

from app.config import get_settings

logger = logging.getLogger(__name__)


class ModelLoader:
    _instance: Optional["ModelLoader"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._settings = get_settings()
        self._whisper_model = None
        self._nllb_model = None
        self._nllb_tokenizer = None
        self._nllb_device = None

    @classmethod
    def get_instance(cls) -> "ModelLoader":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def start_loading(self):
        """Start loading models in a background thread."""
        thread = threading.Thread(target=self._load_all, daemon=True)
        thread.start()

    def _load_all(self):
        logger.info("Starting background model loading...")
        try:
            self._load_whisper()
            self._load_nllb()
            logger.info("Background model loading complete.")
        except Exception as e:
            logger.error(f"Background loading failed: {e}")

    def load_models(self):
        """Load all models synchronously (blocking)."""
        self._load_all()


    def _load_whisper(self):
        with self._lock:
            if self._whisper_model:
                return
            try:
                logger.info("Loading Whisper model...")
                from faster_whisper import WhisperModel
                self._whisper_model = WhisperModel(
                    self._settings.whisper_model_size,
                    device=self._settings.whisper_device,
                    compute_type=self._settings.whisper_compute_type,
                )
                logger.info("Whisper model loaded.")
            except Exception as e:
                logger.error(f"Failed to load Whisper: {e}")

    def _load_nllb(self):
        with self._lock:
            if self._nllb_model:
                return
            try:
                logger.info("Loading NLLB model...")
                import torch
                from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

                self._nllb_device = 0 if torch.cuda.is_available() else -1
                model_name = self._settings.nllb_model
                
                self._nllb_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self._nllb_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                
                if self._nllb_device >= 0:
                    self._nllb_model = self._nllb_model.to(self._nllb_device)
                    
                logger.info("NLLB model loaded.")
            except Exception as e:
                logger.error(f"Failed to load NLLB: {e}")

    @property
    def whisper_model(self) -> Any:
        if not self._whisper_model:
            self._load_whisper()
        return self._whisper_model

    @property
    def nllb_components(self) -> tuple[Any, Any, int]:
        """Returns (model, tokenizer, device)."""
        if not self._nllb_model:
            self._load_nllb()
        return self._nllb_model, self._nllb_tokenizer, self._nllb_device
