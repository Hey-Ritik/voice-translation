"""
Language code mappings for Whisper, NLLB, and display names.
Indian languages focus with full multilingual support.
"""
from typing import Optional

# Whisper language codes (ISO 639-1)
WHISPER_LANG_CODES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "ur": "Urdu",
    "pa": "Punjabi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "or": "Odia",
    "as": "Assamese",
    "zh": "Chinese",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ar": "Arabic",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "pt": "Portuguese",
    "it": "Italian",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "tr": "Turkish",
}

# NLLB-200 Flores language codes (script suffix)
# Format: lang_Script - see https://github.com/facebookresearch/flores/blob/main/flores200/README.md
NLLB_LANG_CODES = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "bn": "ben_Beng",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "mr": "mar_Deva",
    "ur": "urd_Arab",
    "pa": "pan_Guru",
    "gu": "guj_Gujr",
    "kn": "kan_Knda",
    "ml": "mal_Mlym",
    "or": "ory_Orya",
    "as": "asm_Beng",
    "zh": "zho_Hans",
    "fr": "fra_Latn",
    "de": "deu_Latn",
    "es": "spa_Latn",
    "ar": "arb_Arab",
    "ja": "jpn_Jpan",
    "ko": "kor_Hang",
    "ru": "rus_Cyrl",
    "pt": "por_Latn",
    "it": "ita_Latn",
    "th": "tha_Thai",
    "vi": "vie_Latn",
    "id": "ind_Latn",
    "tr": "tur_Latn",
}

# Target languages for dropdown (Indian first, then others)
TARGET_LANGUAGES = [
    ("hi", "Hindi"),
    ("bn", "Bengali"),
    ("ta", "Tamil"),
    ("te", "Telugu"),
    ("mr", "Marathi"),
    ("ur", "Urdu"),
    ("pa", "Punjabi"),
    ("gu", "Gujarati"),
    ("kn", "Kannada"),
    ("ml", "Malayalam"),
    ("en", "English"),
    ("zh", "Chinese"),
    ("fr", "French"),
    ("de", "German"),
    ("es", "Spanish"),
    ("ar", "Arabic"),
    ("ja", "Japanese"),
    ("ko", "Korean"),
    ("ru", "Russian"),
    ("pt", "Portuguese"),
    ("it", "Italian"),
    ("th", "Thai"),
    ("vi", "Vietnamese"),
    ("id", "Indonesian"),
    ("tr", "Turkish"),
]


def whisper_to_display(lang_code: Optional[str]) -> str:
    """Convert Whisper language code to display name."""
    if not lang_code:
        return "Unknown"
    return WHISPER_LANG_CODES.get(lang_code, lang_code)


def to_nllb_code(lang_code: str) -> Optional[str]:
    """Convert ISO 639-1 to NLLB Flores code."""
    return NLLB_LANG_CODES.get(lang_code)
