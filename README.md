# Voice Translation — Real-time Speech Captions & Translation

Full-stack real-time speech-to-text and translation web app. Speak in any language; see live original captions and translated captions. Optimized for **Indian languages** (Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Urdu, Punjabi, etc.).

## Features

- **Real-time streaming**: Microphone → WebSocket → STT → Translation → Live captions
- **Automatic language detection**: No need to select source language
- **Dual captions**: Separate panels for live speech (original) and translation
- **Text-to-speech (TTS)**: Translated text is spoken in the target language (Web Speech API), with mute toggle and speaking indicator
- **Caption management**: Auto-clear after 10s or 3s silence; manual Clear button; buffer limited to last 3 lines
- **Session handling**: Captions reset when mic stops or target language changes
- **Target language dropdown**: Indian languages first, then others
- **Clean UI**: Two-panel layout, mic start/stop, Clear, mute toggle, detected language
- **Error handling**: Mic permission, silence, network, and server errors surfaced in UI

## Architecture

```
[Browser]  Mic → Web Audio (chunks) → WebSocket (base64)
                ↑
[Backend]  WebSocket → decode → Whisper STT → NLLB/OpenAI translate → JSON
                ↓
[Browser]  Caption display (original + translated) + detected language label
```

- **Frontend**: React (Vite), Web Audio API (ScriptProcessorNode for chunked capture), WebSocket client
- **Backend**: FastAPI, WebSocket endpoint, chunk-based processing
- **STT**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (language detection + transcription)
- **Translation**: [NLLB-200](https://huggingface.co/facebook/nllb-200-distilled-600M) (default) or OpenAI API (optional)

## Project structure

```
voice-translation/
├── backend/
│   ├── app/
│   │   ├── config.py           # Settings (env)
│   │   ├── main.py             # FastAPI app + WebSocket
│   │   ├── services/
│   │   │   ├── language_codes.py
│   │   │   ├── stt_service.py  # Whisper STT
│   │   │   └── translation_service.py  # NLLB / OpenAI
│   │   └── websocket/
│   │       └── audio_handler.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/         # MicButton, LanguageSelector, CaptionDisplay, etc.
│   │   └── hooks/              # useAudioStream, useTranslationSocket
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
└── README.md
```

## Setup

### Prerequisites

- **Python 3.10+** (backend)
- **Node.js 18+** (frontend)
- **FFmpeg** (for faster-whisper; install on system path)

### Backend

1. Create a virtual environment and install dependencies:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy env example and optionally edit:

   ```bash
   cp .env.example .env
   ```

3. Run the server:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   First run will download the Whisper model (e.g. `base`) and, on first translation, the NLLB model. Ensure enough disk space and a stable connection.

### Frontend

1. Install and run:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. Open [http://localhost:5173](http://localhost:5173). The dev server proxies `/ws/*` and `/languages` to the backend (port 8000).

### Environment variables

**Backend (`.env`)**

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST`, `PORT` | Server bind | `0.0.0.0`, `8000` |
| `WHISPER_MODEL_SIZE` | Whisper model | `base` |
| `WHISPER_DEVICE` | `cpu` or `cuda` | `cpu` |
| `WHISPER_COMPUTE_TYPE` | `int8`, `float16`, `float32` | `int8` |
| `TRANSLATION_ENGINE` | `nllb` or `openai` | `nllb` |
| `NLLB_MODEL` | HuggingFace model id | `facebook/nllb-200-distilled-600M` |
| `OPENAI_API_KEY` | Optional; used if `TRANSLATION_ENGINE=openai` | — |
| `SAMPLE_RATE` | Audio sample rate | `16000` |
| `MIN_AUDIO_LENGTH_S` | Skip chunks shorter than this | `0.5` |

**Frontend (`.env`)**

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base (optional in dev) |
| `VITE_WS_URL` | WebSocket URL (optional; default same host + `/ws/audio`) |

## Usage

1. Open the app and choose a **target language** (e.g. Hindi).
2. Click the **microphone** button. Allow mic access if prompted.
3. Speak. **Original** and **translated** captions appear in real time; **Detected** shows the source language.
4. Click the mic again to stop.

## API

- **GET /** — Service info and links
- **GET /health** — Health check
- **GET /languages** — List of target languages for the dropdown
- **WebSocket /ws/audio** — Real-time pipeline  
  - Send JSON: `{ "audio": "<base64 PCM>", "target_lang": "hi", "sample_rate": 16000 }`  
  - Receive: `{ "type": "caption", "original", "translated", "detected_lang", "detected_lang_display" }` or `{ "type": "error", "error": "..." }`

## Notes

- **Latency**: Chunks are ~2 s; processing depends on CPU/GPU. Use smaller Whisper model (e.g. `tiny`) or GPU for lower latency.
- **Indian languages**: NLLB and Whisper support Hindi, Bengali, Tamil, Telugu, Marathi, Urdu, Punjabi, Gujarati, Kannada, Malayalam, etc.
- **Silence**: Very short or silent chunks are skipped; no caption is emitted.
- **Modularity**: STT and translation are in separate services; you can swap Whisper for another engine or NLLB for OpenAI/IndicTrans by changing config and service code.

## License

Use and modify as needed for your project.
## 🛠️ Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# If on Windows/No-GPU, install CPU torch separately if needed:
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Run Server
uvicorn app.main:app --reload
```
Server runs at `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
App runs at `http://localhost:5173`.

## 🚀 Deployment (Render)

This project is configured for [Render](https://render.com).

1. **New Web Service**: Connect your repo.
2. **Build Command**: `./backend/build.sh` (installs CPU-optimized Torch).
3. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. **Environment Variables**:
   - `PYTHON_VERSION`: `3.10.12`
   - `WHISPER_MODEL_SIZE`: `tiny` (Recommended for free tier)
   - `TRANSLATION_ENGINE`: `nllb`

> **Note**: The first deployment might take a few minutes to build the dependencies.
Use and modify as needed for your project.
