"""
Translation service: NLLB-200 for multilingual (Indian languages) with optional OpenAI fallback.
Uses model + tokenizer directly (no pipeline) for dynamic language pairs.
"""
import logging
from typing import Optional

from app.config import get_settings
from app.services.language_codes import to_nllb_code

logger = logging.getLogger(__name__)


class TranslationService:
    """Translate text using NLLB or OpenAI."""

    _instance: Optional["TranslationService"] = None

    def __init__(self) -> None:
        self._settings = get_settings()
        self._model = None
        self._tokenizer = None
        self._device = None
        self._openai_available = bool(self._settings.openai_api_key)

    def _load_nllb(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        try:
            import torch
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            self._device = 0 if torch.cuda.is_available() else -1
            model_name = self._settings.nllb_model
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            if self._device >= 0:
                self._model = self._model.to(self._device)
            logger.info("Loaded NLLB translation model (model + tokenizer)")
        except Exception as e:
            logger.exception("Failed to load NLLB: %s", e)
            raise

    def translate_nllb(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using NLLB-200 (model + tokenizer, dynamic language pair)."""
        self._load_nllb()
        src_code = to_nllb_code(source_lang)
        tgt_code = to_nllb_code(target_lang)
        if not src_code or not tgt_code:
            logger.warning("Unsupported language pair for NLLB: %s -> %s", source_lang, target_lang)
            return text
        if source_lang == target_lang:
            return text
        try:
            self._tokenizer.src_lang = src_code
            forced_bos_id = self._tokenizer.convert_tokens_to_ids(tgt_code)
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
            )
            if self._device >= 0:
                inputs = {k: v.to(self._model.device) for k, v in inputs.items()}
            out_ids = self._model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_id,
                max_length=512,
            )
            decoded = self._tokenizer.batch_decode(out_ids, skip_special_tokens=True)
            return (decoded[0].strip() if decoded else text)
        except Exception as e:
            logger.warning("NLLB translate failed: %s", e)
            return text

    def translate_openai(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using OpenAI API (if key is set)."""
        if not self._settings.openai_api_key:
            return text
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self._settings.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"Translate the following text from {source_lang} to {target_lang}. "
                        "Reply with only the translation, no explanation.",
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=500,
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning("OpenAI translation failed: %s", e)
        return text

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        use_openai: bool = False,
    ) -> str:
        """
        Translate text from source to target language.
        Uses OpenAI if use_openai and API key set, else NLLB.
        """
        if not text or not text.strip():
            return ""
        if source_lang == target_lang:
            return text
        if use_openai and self._openai_available:
            return self.translate_openai(text, source_lang, target_lang)
        return self.translate_nllb(text, source_lang, target_lang)


def get_translation_service() -> TranslationService:
    """Singleton translation service."""
    if TranslationService._instance is None:
        TranslationService._instance = TranslationService()
    return TranslationService._instance
