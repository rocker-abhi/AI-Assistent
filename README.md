# 🚀 Friday AI Assistant

A modern, real-time voice and chat AI coding companion powered by **FastAPI**, **PostgreSQL**, **WebSockets**, **Edge-TTS**, **Whisper STT**, and dynamic LLM providers (**Groq Cloud** & **Local Ollama**).

---

## 🏗️ Architecture Diagrams

### 1. System Architecture

```mermaid
flowchart TB
    subgraph Frontend["🖥️ Frontend (Friday-UI)"]
        UI["Three.js 3D Particle Visualizer"]
        VAD["Voice Activity Detection (VAD)"]
        WS_Client["WebSocket Client"]
        Audio_Out["Web Audio Player"]
    end

    subgraph Backend["⚡ Backend (FastAPI Server)"]
        WS_Endpoint["WebSocket Route (/ws/{client_id})"]
        Manager["Connection Manager"]
        
        subgraph Handlers["Message Handlers"]
            AudioHandler["Audio Handler (STT Dispatch)"]
            TextHandler["Text Handler (Conversation Flow)"]
        end
        
        subgraph Speech["Speech & Audio Engine"]
            Whisper["Whisper STT Engine"]
            EdgeTTS["Edge-TTS Voice Streamer"]
        end
        
        subgraph LLM_Engine["Unified Assistant Engine"]
            ProviderRouter{"LLM Provider Router (.env)"}
            GroqClient["Groq Cloud Client (ChatGroq)"]
            OllamaClient["Local Ollama Client (ChatOllama)"]
        end
    end

    subgraph External_AI["🤖 AI Backends"]
        GroqCloud["Groq Cloud API (Llama 3.3 / GPT-OSS / Qwen)"]
        OllamaLocal["Ollama Instance (DeepSeek-R1 / Llama 3)"]
    end

    subgraph Storage["🗄️ PostgreSQL Database"]
        Schema["Schema: chat_schema"]
        ConversationsTable["Table: conversations"]
        MessagesTable["Table: messages"]
    end

    %% Frontend to Backend Connections
    VAD -->|Raw PCM Audio Stream| WS_Client
    WS_Client <-->|Bi-directional WebSocket| WS_Endpoint
    WS_Endpoint --> Manager
    Manager --> AudioHandler
    Manager --> TextHandler
    
    %% Audio & STT
    AudioHandler --> Whisper
    Whisper -->|Transcribed Text| TextHandler

    %% LLM Processing
    TextHandler --> ProviderRouter
    ProviderRouter -->|LLM_PROVIDER=groq| GroqClient
    ProviderRouter -->|LLM_PROVIDER=ollama| OllamaClient
    GroqClient <-->|API Request / Stream| GroqCloud
    OllamaClient <-->|Local Stream| OllamaLocal

    %% TTS & Streaming
    GroqClient -->|Text Tokens Stream| EdgeTTS
    OllamaClient -->|Text Tokens Stream| EdgeTTS
    EdgeTTS -->|MP3 Chunks| Manager
    Manager -->|Stream Audio & Text| WS_Client
    WS_Client --> Audio_Out
    WS_Client --> UI

    %% Database Persistence
    TextHandler <-->|ORM / SQLAlchemy| Storage
```

---

### 2. Real-time Interaction Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as Friday-UI (Browser)
    participant WS as WebSocket Route
    participant Handler as Text/Audio Handler
    participant Whisper as Whisper STT
    participant Assistant as Unified Assistant
    participant LLM as Groq / Ollama
    participant TTS as Edge-TTS
    participant DB as PostgreSQL (chat_schema)

    User->>Frontend: Speaks / Types "Hello Friday"
    alt Voice Input
        Frontend->>WS: Send Base64 Audio (Float32 PCM)
        WS->>Handler: Dispatch to AudioHandler
        Handler->>Whisper: Transcribe audio samples
        Whisper-->>Handler: Transcribed text
        Handler->>Frontend: Send user_transcription event
    else Text Input
        Frontend->>WS: Send JSON Text message
        WS->>Handler: Dispatch to TextHandler
    end

    Handler->>DB: Save user message in chat_schema.messages
    Handler->>Assistant: chat_stream(prompt, history)
    Assistant->>LLM: Stream prompt with Friday persona
    
    loop Real-Time Token & Audio Generation
        LLM-->>Assistant: Stream text chunk
        Assistant-->>Frontend: Send {"type": "text", "data": token}
        Assistant->>TTS: Sentence buffer ready -> Synthesize speech
        TTS-->>Assistant: Audio MP3 chunk
        Assistant-->>Frontend: Send {"type": "audio", "data": base64_mp3}
        Frontend->>Frontend: Play audio chunk & Animate 3D sphere
    end

    Assistant-->>Handler: Completion done
    Handler->>DB: Save assistant response in chat_schema.messages
    Handler-->>Frontend: Send {"type": "done"}
```

---

## 🌟 Features

- **⚡ Dual LLM Provider Support**: Seamlessly switch between **Groq Cloud** (e.g., `openai/gpt-oss-120b`, `llama-3.3-70b-versatile`, `qwen/qwen3.6-27b`) and **Local Ollama** (e.g., `deepseek-r1:1.5b`, `llama3`) directly via configuration.
- **🎙️ Real-time Voice & Audio Streaming**:
  - **Speech-to-Text (STT)**: Transcribes incoming microphone audio with OpenAI Whisper.
  - **Text-to-Speech (TTS)**: Streams natural voice audio back in real time using Microsoft Edge-TTS.
- **💬 Persistent Chat History**: Stores conversations and messages in PostgreSQL using SQLAlchemy and custom schemas (`chat_schema`).
- **🛡️ Startup Health Check**: Validates database connectivity on startup and gracefully stops the backend server if PostgreSQL is unreachable.
- **🌐 3D Interactive UI**: Frontend with 3D particle sphere visualizer (Three.js), voice activity detection (VAD), and WebSocket real-time audio playback.

---

## 📸 Screenshots & UI Preview

| 3D Sphere Interactive Voice Mode | Real-Time Voice & Chat Interface |
| :---: | :---: |
| ![Friday 3D Sphere Visualizer](./screenshot/Screenshot%20From%202026-08-18%2019-47-45.png) | ![Friday Real-Time Chat](./screenshot/Screenshot%20From%202026-08-18%2019-48-41.png) |

---

## 📁 Project Structure

```text
├── app/
│   ├── core/
│   │   ├── config.py         # Application settings loaded from .env
│   │   ├── database.py       # SQLAlchemy database session & engine manager
│   │   └── logger.py         # Configured application logger
│   ├── LLM/
│   │   ├── assistant.py      # Unified LLM engine (Groq & Ollama switching + TTS)
│   │   ├── groq_llms.py      # Groq LLM interface
│   │   ├── ollama_llms.py    # Ollama LLM interface
│   │   └── personality/      # Friday persona & prompt engineering
│   ├── models/
│   │   ├── base.py           # SQLAlchemy declarative base
│   │   └── chat_schema/      # Conversation and Message database models
│   └── websockets/
│       ├── handler/          # Audio & Text WebSocket message handlers
│       ├── manager.py        # WebSocket connection manager
│       └── route.py          # WebSocket API endpoint (/ws/{client_id})
├── alembic/                  # Database migration scripts
├── scripts/
│   └── setup_db.py           # Automated database connectivity & schema setup script
├── setup_db.py               # Root runner for setup_db
├── main.py                   # FastAPI application & Uvicorn entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Local environment configuration
└── Friday-UI/                # Frontend application (Vite, React/Three.js)
```

---

## ⚙️ Prerequisites

- **Python**: `3.10` or newer
- **Node.js**: `v18+` and `npm`
- **PostgreSQL**: Running instance with a database created (default: `assistant_db`)
- **Ollama** (optional): If using local models (`ollama serve`)
- **Groq API Key** (optional): If using Groq cloud models ([console.groq.com](https://console.groq.com))

---

## 🚀 Quickstart Guide

### 1. Clone & Set Up Python Virtual Environment

```bash
# Navigate to the backend directory
cd /path/to/AI-Assistent

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 2. Configure Environment Variables (`.env`)

Copy `.env.example` to `.env` and adjust the values:

```bash
cp .env.example .env
```

#### Key `.env` Configuration Options:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `PRIMARY_DB` | PostgreSQL connection string (`postgresql+psycopg://user:pass@host:port/dbname`) | `postgresql+psycopg://abhishek:postgres@localhost:5432/assistant_db` |
| `LLM_PROVIDER` | Active LLM backend: **`groq`** or **`ollama`** | `groq` |
| `GROQ_API_KEY` | Groq Cloud API key | `gsk_...` |
| `GROQ_MODEL` | Groq model identifier | `openai/gpt-oss-120b` |
| `GROQ_TEMPERATURE` | Groq sampling temperature | `0.2` |
| `OLLAMA_BASE_URL`| Ollama service URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `deepseek-r1:1.5b` |
| `OLLAMA_TEMPERATURE` | Ollama sampling temperature | `0.5` |
| `TTS_VOICE` | Microsoft Edge-TTS voice model | `en-US-JennyNeural` |
| `TTS_RATE` | Speech rate modifier | `+17%` |
| `WISPER_MODEL` | Whisper STT model size (`base`, `small`, `medium`) | `base` |

---

### 3. Switching LLM Providers (Groq vs Ollama)

You can switch the LLM provider at any time by updating `LLM_PROVIDER` in your `.env` file:

#### Option A: Use Groq Cloud
```env
LLM_PROVIDER="groq"
GROQ_API_KEY="your-groq-api-key"
GROQ_MODEL="openai/gpt-oss-120b"
```

#### Option B: Use Local Ollama
```env
LLM_PROVIDER="ollama"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="deepseek-r1:1.5b"
```

The unified `Assistant` engine automatically routes requests to the configured provider upon server startup or reloads.

---

### 4. Database Setup

Run the automated database setup script. This script:
1. **Tests connectivity** to your PostgreSQL database.
2. **Creates the schema** (`chat_schema`) if it does not exist.
3. **Generates all tables and indexes** (`conversations`, `messages`).

```bash
python setup_db.py
```

*Alternatively, you can apply Alembic migrations:*
```bash
alembic upgrade head
```

---

### 5. Running the Backend Server

Start the FastAPI application with Uvicorn:

```bash
source venv/bin/activate
python main.py
```

> **Note:** If the backend cannot establish a connection to PostgreSQL during startup, it will log the error and immediately stop the server to prevent running in a broken state.

- **API Base URL**: `http://127.0.0.1:8000`
- **Health Check**: `GET http://127.0.0.1:8000/`
- **WebSocket Endpoint**: `ws://127.0.0.1:8000/ws/{client_id}`

---

### 6. Running the Frontend (Friday-UI)

In a separate terminal:

```bash
cd Friday-UI
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser to interact with Friday!

---

## 📡 Communication Protocol & API Specification

The application uses **WebSockets (`ws://`)** for real-time, bi-directional, low-latency communication between the frontend client and the backend server.

### 🔗 Endpoint
```text
ws://127.0.0.1:8000/ws/{client_id}
```
- **`client_id`**: A unique identifier for the connected frontend session (e.g., `friday-frontend`).
- **Connection Lifecycle**: 
  - Upon connection, the server sends previous chat history.
  - If a client disconnects or issues a cancel event, any in-flight streaming LLM/TTS tasks are cleanly cancelled.

---

### 📤 Client-to-Server Messages (JSON)

Incoming messages must conform to `InputMessageSchema`:

```json
{
  "type": "message",
  "message_type": "<text | audio | cancel>",
  "message_id": "msg_1787061958952",
  "content": {
    "text": "<payload_content>"
  },
  "timestamp": "2026-08-18T14:05:58.952Z"
}
```

#### 1. Text Message (`message_type: "text"`)
Sent when the user submits a text prompt in the chat input.
```json
{
  "type": "message",
  "message_type": "text",
  "message_id": "msg_1787061958952",
  "content": {
    "text": "How do I optimize a PostgreSQL query?"
  },
  "timestamp": "2026-08-18T14:05:58.952Z"
}
```

#### 2. Audio Message (`message_type: "audio"`)
Sent when the Voice Activity Detection (VAD) detects speech.
- **Audio Format**: Base64-encoded raw **Float32 PCM** audio sampled at **16,000 Hz (16 kHz)**.
```json
{
  "type": "message",
  "message_type": "audio",
  "message_id": "msg_1787061958953",
  "content": {
    "text": "<base64_encoded_float32_pcm_audio>"
  },
  "timestamp": "2026-08-18T14:05:58.953Z"
}
```

#### 3. Cancel / Interrupt Message (`message_type: "cancel"`)
Sent when the user interrupts or clicks cancel while the assistant is speaking/streaming.
```json
{
  "type": "message",
  "message_type": "cancel",
  "message_id": "msg_1787061958954",
  "content": {
    "text": ""
  },
  "timestamp": "2026-08-18T14:05:58.954Z"
}
```

---

### 📥 Server-to-Client Events (JSON)

The backend sends JSON events over the WebSocket connection during processing:

| Event `type` | Payload Format | Description |
| :--- | :--- | :--- |
| **`history`** | `{"type": "history", "data": [{"role": "user", "content": "..."}, ...]}` | Initial chat history sent immediately after connection. |
| **`received`** | `{"status": "received", "message": {...}}` | Immediate acknowledgement of received message. |
| **`user_transcription`**| `{"type": "user_transcription", "message": "transcribed text"}` | Whisper transcription result of the user's voice input. |
| **`text`** | `{"type": "text", "data": "word "}` | Incremental LLM text token chunk streamed in real time. |
| **`audio`** | `{"type": "audio", "data": "<base64_encoded_mp3_chunk>"}` | Synthesized voice audio chunk (Edge-TTS MP3) for instant playback. |
| **`done`** | `{"type": "done"}` | Signals that LLM generation, audio streaming, and database persistence are complete. |
| **`error`** | `{"type": "error", "message": "error description"}` | Notifies the client of any processing or API errors. |
| **`cancelled`** | `{"status": "cancelled", "message": "Processing interrupted."}` | Confirms that ongoing generation has been aborted. |

---

## 📜 License

MIT License.

